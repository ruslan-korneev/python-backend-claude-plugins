# Testing FastAPI Applications

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   └── modules/
│       └── users/
│           ├── conftest.py
│           ├── test_services.py
│           └── test_repositories.py
├── integration/             # Integration tests
│   └── modules/
│       └── users/
│           └── test_api.py
└── e2e/                     # End-to-end tests
    └── test_user_flow.py
```

## Testing Endpoints

### Basic Example

```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


class TestUserEndpoints:
    @pytest.fixture
    async def client(self) -> AsyncClient:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

    async def test_create_user_success(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/users",
            json={"email": "test@example.com", "name": "Test User"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["email"] == "test@example.com"

    async def test_create_user_invalid_email_returns_422(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/users",
            json={"email": "invalid", "name": "Test User"},
        )

        assert response.status_code == 422
        assert "email" in response.json()["detail"][0]["loc"]

    async def test_get_user_not_found_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/users/999999")

        assert response.status_code == 404
```

### With Dependency Override

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.core.dependencies import get_session


class TestUserEndpointsWithDB:
    @pytest.fixture
    async def client(self, session: AsyncSession) -> AsyncClient:
        """Client with overridden DB session."""

        async def override_get_session():
            yield session

        app.dependency_overrides[get_session] = override_get_session

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

        app.dependency_overrides.clear()

    async def test_create_and_get_user(
        self,
        client: AsyncClient,
    ) -> None:
        # Create
        create_response = await client.post(
            "/api/v1/users",
            json={"email": "test@example.com", "name": "Test User"},
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Get
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["email"] == "test@example.com"
```

## Testing with dependency-injector

```python
import pytest
from httpx import ASGITransport, AsyncClient
from dependency_injector import providers

from src.main import app
from src.core.container import Container


class TestWithContainer:
    @pytest.fixture
    def container(self, fake_session_maker) -> Container:
        """Container with overridden dependencies."""
        container = Container()
        container.session_maker.override(providers.Object(fake_session_maker))
        return container

    @pytest.fixture
    async def client(self, container: Container) -> AsyncClient:
        """Client with overridden container."""
        app.container = container

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

        container.reset_override()
```

## Testing Authentication

```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.core.security import create_access_token


class TestProtectedEndpoints:
    @pytest.fixture
    def auth_headers(self, sample_user) -> dict:
        """Headers with JWT token."""
        token = create_access_token({"sub": str(sample_user.id)})
        return {"Authorization": f"Bearer {token}"}

    async def test_protected_endpoint_without_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_protected_endpoint_with_valid_token(
        self,
        client: AsyncClient,
        auth_headers: dict,
        sample_user,
    ) -> None:
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == sample_user.id

    async def test_protected_endpoint_with_expired_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        # Create token with expired time
        token = create_access_token(
            {"sub": "1"},
            expires_delta=timedelta(seconds=-1),
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 401
```

## Testing WebSocket

```python
import pytest
from httpx import ASGITransport
from starlette.testclient import TestClient

from src.main import app


class TestWebSocket:
    def test_websocket_connection(self) -> None:
        client = TestClient(app)

        with client.websocket_connect("/ws") as websocket:
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_authentication_required(self) -> None:
        client = TestClient(app)

        with pytest.raises(Exception):  # WebSocketDisconnect
            with client.websocket_connect("/ws/protected"):
                pass
```

## Testing Background Tasks

```python
import pytest
from unittest.mock import AsyncMock, patch


class TestBackgroundTasks:
    async def test_endpoint_schedules_background_task(
        self,
        client: AsyncClient,
    ) -> None:
        with patch(
            "src.modules.users.routers.send_welcome_email",
            new_callable=AsyncMock,
        ) as mock_send:
            response = await client.post(
                "/api/v1/users",
                json={"email": "test@example.com", "name": "Test"},
            )

            assert response.status_code == 201
            # Background task should be called
            mock_send.assert_called_once_with("test@example.com")
```

## Testing File Upload

```python
import pytest
from io import BytesIO


class TestFileUpload:
    async def test_upload_file_success(
        self,
        client: AsyncClient,
    ) -> None:
        file_content = b"test file content"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        response = await client.post("/api/v1/files/upload", files=files)

        assert response.status_code == 201
        assert response.json()["filename"] == "test.txt"

    async def test_upload_file_too_large_returns_413(
        self,
        client: AsyncClient,
    ) -> None:
        # File larger than limit (e.g., 10MB)
        large_content = b"x" * (10 * 1024 * 1024 + 1)
        files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}

        response = await client.post("/api/v1/files/upload", files=files)

        assert response.status_code == 413
```

## Testing Pagination

```python
class TestPagination:
    @pytest.fixture
    async def many_users(self, session: AsyncSession, user_factory) -> list:
        """Create 25 users."""
        users = []
        for i in range(25):
            user = await user_factory(email=f"user{i}@example.com")
            users.append(user)
        return users

    async def test_pagination_default_limit(
        self,
        client: AsyncClient,
        many_users,
    ) -> None:
        response = await client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 20  # default limit
        assert data["total"] == 25

    async def test_pagination_with_custom_params(
        self,
        client: AsyncClient,
        many_users,
    ) -> None:
        response = await client.get("/api/v1/users?limit=5&offset=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["offset"] == 10
```

## Testing Error Handling

```python
class TestErrorHandling:
    async def test_validation_error_format(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post("/api/v1/users", json={})

        assert response.status_code == 422
        error = response.json()
        assert "detail" in error
        assert isinstance(error["detail"], list)

    async def test_not_found_error_format(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/users/999999")

        assert response.status_code == 404
        error = response.json()
        assert error["detail"] == "User not found"

    async def test_internal_error_hides_details(
        self,
        client: AsyncClient,
    ) -> None:
        with patch(
            "src.modules.users.services.UserService.get",
            side_effect=RuntimeError("Database connection failed"),
        ):
            response = await client.get("/api/v1/users/1")

            assert response.status_code == 500
            # Internal error is not exposed
            assert "Database" not in response.json()["detail"]
```
