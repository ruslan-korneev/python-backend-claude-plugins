# Pytest Fixtures for FastAPI

## Setting Up Test Database

**Test database is required!** Never mock the database.

### Option 1: Same PostgreSQL, Different Databases (Recommended)

Tests create separate databases in the same PostgreSQL:
- `myapp` — production/development
- `test_myapp` — tests without xdist
- `gw0_test_myapp`, `gw1_test_myapp`... — parallel workers

```bash
# Use existing PostgreSQL (dev or docker)
# Test databases are created automatically by setup_test_database fixture
```

### Option 2: Separate Container for Tests

```bash
docker run -d \
  --name postgres-test \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

### pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

## Parallel Test Execution (pytest-xdist)

When running tests on multiple cores, each worker needs its own database.

### Fixture for Creating DB per Worker

```python
# tests/conftest.py
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.database import Base


def get_test_db_name(worker_id: str, base_name: str = "myapp") -> str:
    """Generate database name for worker."""
    if worker_id == "master":
        # Without xdist or main process
        return f"test_{base_name}"
    # gw0, gw1, gw2... → gw0_test_myapp, gw1_test_myapp...
    return f"{worker_id}_test_{base_name}"


@pytest.fixture(scope="session")
def database_url(worker_id: str) -> str:
    """Test database URL for current worker."""
    db_name = get_test_db_name(worker_id)
    return f"postgresql+asyncpg://test:test@localhost:5432/{db_name}"


@pytest.fixture(scope="session")
async def setup_test_database(worker_id: str, database_url: str):
    """Create database for worker, delete after tests."""
    db_name = get_test_db_name(worker_id)

    # Connect to postgres to create database
    admin_url = "postgresql+asyncpg://test:test@localhost:5432/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")

    async with admin_engine.connect() as conn:
        # Check existence
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )
        exists = result.scalar() is not None

        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    await admin_engine.dispose()

    # Create tables
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield database_url

    # Cleanup: drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def engine(setup_test_database: str):
    """Engine for worker's test database."""
    return create_async_engine(setup_test_database, echo=False)
```

### Running

```bash
# 4 workers (by number of cores)
pytest -n 4

# Automatically by CPU count
pytest -n auto
```

### Database Structure

```
PostgreSQL
├── myapp                    # Production/dev
├── test_myapp               # Without xdist or master
├── gw0_test_myapp           # Worker 0
├── gw1_test_myapp           # Worker 1
├── gw2_test_myapp           # Worker 2
└── gw3_test_myapp           # Worker 3
```

## Basic Database Fixtures

### Engine and Session

```python
# tests/conftest.py
import pytest
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import Base


TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    """Test engine — created once per session."""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )


@pytest.fixture(scope="session")
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Create and drop tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(
    engine: AsyncEngine,
    setup_database: None,
) -> AsyncGenerator[AsyncSession, None]:
    """Session with automatic rollback after each test."""
    async with engine.connect() as connection:
        await connection.begin()

        session_maker = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        async with session_maker() as session:
            yield session

        await connection.rollback()
```

### FakeSessionMaker for DI

```python
# tests/conftest.py
from sqlalchemy.ext.asyncio import AsyncSession


class FakeSessionMaker:
    """Fake session maker for use with dependency-injector."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # Rollback happens in session fixture
        pass


@pytest.fixture
def fake_session_maker(session: AsyncSession) -> FakeSessionMaker:
    """Fake session maker for tests."""
    return FakeSessionMaker(session)
```

## HTTP Client

### AsyncClient

```python
# tests/conftest.py
import pytest
from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.dependencies import get_session


@pytest.fixture
async def client(
    session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with overridden DB session."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### Authenticated Client

```python
# tests/conftest.py
from src.core.security import create_access_token


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    sample_user,
) -> AsyncClient:
    """Client with JWT token in headers."""
    token = create_access_token({"sub": str(sample_user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def auth_headers(sample_user) -> dict:
    """Authorization headers."""
    token = create_access_token({"sub": str(sample_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

## Sample Data Fixtures

### User

```python
# tests/conftest.py
from src.modules.users.models import User
from src.modules.users.repositories import UserRepository


@pytest.fixture
def sample_user_data() -> dict:
    """Data for user creation."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": "hashed_password_here",
    }


@pytest.fixture
async def sample_user(
    session: AsyncSession,
    sample_user_data: dict,
) -> User:
    """User in database."""
    repo = UserRepository(session)
    user = await repo.create(sample_user_data)
    return user
```

### Factory Fixtures

```python
# tests/conftest.py
from collections.abc import Callable, Awaitable


@pytest.fixture
def user_factory(
    session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Factory for creating users."""

    async def create(
        email: str = "test@example.com",
        name: str = "Test User",
        **kwargs,
    ) -> User:
        from src.modules.users.repositories import UserRepository

        repo = UserRepository(session)
        data = {"email": email, "name": name, **kwargs}
        return await repo.create(data)

    return create


@pytest.fixture
def order_factory(
    session: AsyncSession,
    sample_user,
) -> Callable[..., Awaitable]:
    """Factory for creating orders."""

    async def create(
        user_id: int | None = None,
        status: str = "pending",
        **kwargs,
    ):
        from src.modules.orders.repositories import OrderRepository

        repo = OrderRepository(session)
        data = {
            "user_id": user_id or sample_user.id,
            "status": status,
            **kwargs,
        }
        return await repo.create(data)

    return create
```

## Service Fixtures

```python
# tests/conftest.py
from src.modules.users.services import UserService
from src.modules.users.repositories import UserRepository


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    """User repository."""
    return UserRepository(session)


@pytest.fixture
def user_service(user_repository: UserRepository) -> UserService:
    """User service."""
    return UserService(repository=user_repository)
```

## Container Fixtures (dependency-injector)

```python
# tests/conftest.py
from dependency_injector import providers

from src.core.container import Container


@pytest.fixture
def container(fake_session_maker: FakeSessionMaker) -> Container:
    """Container with overridden dependencies."""
    container = Container()

    # Override session_maker
    container.session_maker.override(providers.Object(fake_session_maker))

    yield container

    container.reset_override()


@pytest.fixture
def user_service_from_container(container: Container) -> UserService:
    """Service from container."""
    return container.user_service()
```

## Special Fixtures

### Frozen Time

```python
# tests/conftest.py
from datetime import datetime
from unittest.mock import patch


@pytest.fixture
def frozen_time():
    """Frozen time for tests."""
    frozen = datetime(2024, 6, 15, 12, 0, 0)

    with patch("src.core.utils.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        mock_dt.utcnow.return_value = frozen
        # Allow creating datetime objects
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield frozen
```

### Temp Files

```python
# tests/conftest.py
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """Temporary file for tests."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("test content")
    return file_path
```

### Environment Variables

```python
# tests/conftest.py
import os


@pytest.fixture
def env_vars(monkeypatch):
    """Override environment variables."""
    def set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return set_env


# Usage
async def test_with_env(env_vars):
    env_vars(DATABASE_URL="postgresql://test", DEBUG="true")
    # ...
```

## Fixture Scopes

```python
# function (default) — for each test
@pytest.fixture
async def session():
    ...

# class — for each test class
@pytest.fixture(scope="class")
def shared_resource():
    ...

# module — for each module
@pytest.fixture(scope="module")
def expensive_resource():
    ...

# session — once for entire test session
@pytest.fixture(scope="session")
def engine():
    ...
```

## Autouse Fixtures

```python
# Automatically applied to all tests
@pytest.fixture(autouse=True)
def reset_caches():
    """Reset caches before each test."""
    cache.clear()
    yield
    cache.clear()


# Only for tests in specific module
# tests/modules/users/conftest.py
@pytest.fixture(autouse=True)
async def clean_users_table(session):
    """Clean users table."""
    yield
    await session.execute(delete(User))
```
