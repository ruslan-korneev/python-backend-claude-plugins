---
name: pytest:fixture
description: Create a pytest fixture
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: name
    description: Fixture name
    required: true
  - name: type
    description: "Type: session, client, db, mock, sample"
    required: false
  - name: scope
    description: "Scope: function (default), class, module, session"
    required: false
---

# Command /test:fixture

Create a pytest fixture for tests.

## Instructions

### Step 1: Determine fixture type

- **session** — AsyncSession for database operations
- **client** — AsyncClient for API testing
- **db** — full test database setup
- **mock** — mock for a dependency
- **sample** — test data (sample user, sample order, etc.)

### Step 2: Determine scope

- **function** (default) — created for each test
- **class** — created for each test class
- **module** — created for each module
- **session** — created once for the entire test session

### Step 3: Determine location

- Shared fixtures → `tests/conftest.py`
- Module-specific fixtures → `tests/modules/{module}/conftest.py`
- Local fixtures → in the test file itself

## Fixture Templates

### AsyncSession with rollback (recommended)

```python
# tests/conftest.py
import pytest
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.database import Base


@pytest.fixture(scope="session")
def engine():
    """Test engine — created once."""
    return create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False,
    )


@pytest.fixture(scope="session")
async def setup_database(engine):
    """Create tables before tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(
    engine,
    setup_database,
) -> AsyncGenerator[AsyncSession, None]:
    """Session with automatic rollback after each test."""
    async with engine.connect() as connection:
        await connection.begin()
        session_maker = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
        )
        async with session_maker() as session:
            yield session
        await connection.rollback()
```

### AsyncClient for FastAPI

```python
# tests/conftest.py
import pytest
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.dependencies import get_session


@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with overridden session."""

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### FakeSessionMaker for DI (dependency-injector)

```python
# tests/conftest.py
import pytest
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class FakeSessionMaker:
    """Fake session maker for tests with rollback."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, *args) -> None:
        pass  # rollback happens in session fixture


@pytest.fixture
def fake_session_maker(session: AsyncSession) -> FakeSessionMaker:
    """Fake session maker for container injection."""
    return FakeSessionMaker(session)


@pytest.fixture
def container(fake_session_maker: FakeSessionMaker):
    """Container with overridden dependencies."""
    from src.core.container import Container

    container = Container()
    container.session_maker.override(fake_session_maker)
    yield container
    container.reset_override()
```

### Sample data

```python
# tests/conftest.py
import pytest
from src.modules.users.models import User


@pytest.fixture
def sample_user_data() -> dict:
    """Data for user creation."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepassword123",
    }


@pytest.fixture
async def sample_user(session: AsyncSession, sample_user_data: dict) -> User:
    """Created user in database."""
    from src.modules.users.repositories import UserRepository

    repo = UserRepository(session)
    user = await repo.create(sample_user_data)
    return user
```

### Mock dependency

```python
# tests/conftest.py or in test file
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_email_service() -> AsyncMock:
    """Mock email service."""
    mock = AsyncMock()
    mock.send.return_value = True
    return mock


@pytest.fixture
def mock_cache() -> MagicMock:
    """Mock cache."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    return mock
```

### Factory fixture

```python
# tests/conftest.py
import pytest
from collections.abc import Callable


@pytest.fixture
def user_factory(session: AsyncSession) -> Callable:
    """Factory for creating users."""
    created_users = []

    async def create_user(
        email: str = "test@example.com",
        name: str = "Test User",
        **kwargs,
    ) -> User:
        from src.modules.users.repositories import UserRepository

        repo = UserRepository(session)
        user = await repo.create({"email": email, "name": name, **kwargs})
        created_users.append(user)
        return user

    yield create_user

    # Cleanup if needed
    for user in created_users:
        await session.delete(user)
```

## Response Format

```
## Fixture Created: {{ name }}

### Location
`tests/conftest.py` (or specify other)

### Code
```python
[fixture code]
```

### Usage
```python
async def test_something({{ name }}: {{ type }}):
    # Use the fixture
    ...
```
```
