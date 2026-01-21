---
name: pytest:first
description: Create a test BEFORE implementation (TDD red phase)
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: feature
    description: Description of the functionality to test
    required: true
  - name: path
    description: Path to file/module where implementation will be (to determine where to create the test)
    required: false
---

# Command /test:first — TDD Red Phase

Create a test **BEFORE** writing implementation. This is the key command for TDD workflow.

## TDD Principle

1. **Red** — write a failing test (this command)
2. **Green** — write minimal code to pass the test
3. **Refactor** — improve code while keeping tests green

## Instructions

### Step 1: Determine test structure

Based on the feature description, determine:
- What to test (function, method, endpoint)
- Which scenarios to cover (happy path, edge cases, errors)
- Which dependencies to mock

### Step 2: Determine test location

```
src/modules/users/services.py → tests/modules/users/test_services.py
src/modules/users/routers.py → tests/modules/users/test_routers.py
src/core/security.py → tests/core/test_security.py
```

### Step 3: Create a failing test

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

# Import what does NOT exist yet — test will fail
from src.modules.users.services import UserService


class TestUserService:
    """Tests for UserService — user creation."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Mock repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository: AsyncMock) -> UserService:
        """Service with mocked dependencies."""
        return UserService(repository=mock_repository)

    async def test_create_user_success(
        self,
        service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        """Successful user creation."""
        # Arrange
        user_data = {"email": "test@example.com", "name": "Test User"}
        mock_repository.save.return_value = {"id": 1, **user_data}

        # Act
        result = await service.create(user_data)

        # Assert
        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        mock_repository.save.assert_called_once()

    async def test_create_user_duplicate_email_raises_conflict(
        self,
        service: UserService,
        mock_repository: AsyncMock,
    ) -> None:
        """Creating user with existing email raises ConflictError."""
        # Arrange
        from src.core.exceptions import ConflictError

        user_data = {"email": "exists@example.com", "name": "Test User"}
        mock_repository.get_by_email.return_value = {"id": 1}  # already exists

        # Act & Assert
        with pytest.raises(ConflictError):
            await service.create(user_data)
```

### Step 4: Run the test — it should fail

```bash
pytest tests/modules/users/test_services.py -v
```

Expected result: `ImportError` or `AssertionError` — this is **correct** for red phase.

### Step 5: Inform the user

```
## TDD Red Phase Complete

### Test Created
`tests/modules/users/test_services.py`

### Tested Scenarios
1. ✅ Successful user creation
2. ✅ Error on duplicate email

### Next Step (Green Phase)
Now implement `UserService.create()` to make tests pass:

```python
# src/modules/users/services.py
class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def create(self, data: dict) -> dict:
        # Your implementation here
        ...
```

Run tests: `pytest tests/modules/users/test_services.py -v`
```

## Test Templates

### For a service
```python
class TestServiceName:
    @pytest.fixture
    def mock_dependency(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_dependency: AsyncMock) -> ServiceName:
        return ServiceName(dependency=mock_dependency)

    async def test_method_success(self, service: ServiceName) -> None:
        # Arrange
        # Act
        # Assert
        pass
```

### For a FastAPI endpoint
```python
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


class TestEndpointName:
    @pytest.fixture
    async def client(self) -> AsyncClient:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client

    async def test_endpoint_success(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/resource", json={...})
        assert response.status_code == 201
```

### For a repository (integration)
```python
@pytest.mark.integration
class TestRepositoryName:
    @pytest.fixture
    async def session(self, db_session: AsyncSession) -> AsyncSession:
        yield db_session
        await db_session.rollback()

    async def test_save_and_retrieve(self, session: AsyncSession) -> None:
        repo = Repository(session)
        # ...
```

## Important

- Test MUST fail after creation — this confirms it works
- Do not write implementation in this command — only the test
- Use descriptive test names: `test_what_we_do_when_condition_then_result`
