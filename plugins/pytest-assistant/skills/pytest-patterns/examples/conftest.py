"""
Example conftest.py for a FastAPI project.

Copy to tests/conftest.py and adapt to your project.
"""

import pytest
from collections.abc import AsyncGenerator, Callable, Awaitable
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from httpx import ASGITransport, AsyncClient

# Imports from your project (replace with your own)
from src.main import app
from src.core.database import Base
from src.core.dependencies import get_session
from src.core.security import create_access_token
from src.modules.users.models import User
from src.modules.users.repositories import UserRepository


# =============================================================================
# Configuration
# =============================================================================

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    """Test engine — created once per test session."""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )


@pytest.fixture(scope="session")
async def setup_database(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Create tables before tests, drop after."""
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
    """
    Session with automatic rollback after each test.

    This is the key fixture for test isolation — each test
    runs in its own transaction that is rolled back at the end.
    """
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


# =============================================================================
# FakeSessionMaker for dependency-injector
# =============================================================================


class FakeSessionMaker:
    """
    Fake session maker for tests.

    Used to replace real session_maker in DI container.
    Rollback happens in session fixture.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


@pytest.fixture
def fake_session_maker(session: AsyncSession) -> FakeSessionMaker:
    """Fake session maker for container injection."""
    return FakeSessionMaker(session)


# =============================================================================
# HTTP Client Fixtures
# =============================================================================


@pytest.fixture
async def client(
    session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client with overridden DB session.

    All requests through this client will use the test session
    with automatic rollback.
    """

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


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    sample_user: User,
) -> AsyncClient:
    """HTTP client with JWT token."""
    token = create_access_token({"sub": str(sample_user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def auth_headers(sample_user: User) -> dict:
    """Authorization headers for requests."""
    token = create_access_token({"sub": str(sample_user.id)})
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_user_data() -> dict:
    """Data for user creation."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": "hashed_password_placeholder",
    }


@pytest.fixture
async def sample_user(
    session: AsyncSession,
    sample_user_data: dict,
) -> User:
    """Created user in database."""
    repo = UserRepository(session)
    user = await repo.create(sample_user_data)
    return user


# =============================================================================
# Factory Fixtures
# =============================================================================


@pytest.fixture
def user_factory(
    session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """
    Factory for creating users.

    Usage:
        user1 = await user_factory(email="user1@example.com")
        user2 = await user_factory(email="user2@example.com", name="Custom")
    """

    async def create(
        email: str = "test@example.com",
        name: str = "Test User",
        **kwargs,
    ) -> User:
        repo = UserRepository(session)
        data = {
            "email": email,
            "name": name,
            "hashed_password": "hashed",
            **kwargs,
        }
        return await repo.create(data)

    return create


# =============================================================================
# Service Fixtures
# =============================================================================


@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    """User repository."""
    return UserRepository(session)


# Uncomment and adapt to your project:
#
# @pytest.fixture
# def user_service(user_repository: UserRepository) -> UserService:
#     """User service."""
#     return UserService(repository=user_repository)


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    from unittest.mock import AsyncMock

    mock = AsyncMock()
    mock.send_welcome.return_value = True
    mock.send_reset_password.return_value = True
    return mock


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def frozen_time():
    """
    Frozen time for tests.

    Usage:
        async def test_created_at(frozen_time):
            order = await service.create(data)
            assert order.created_at == frozen_time
    """
    from datetime import datetime
    from unittest.mock import patch

    frozen = datetime(2024, 6, 15, 12, 0, 0)

    with patch("src.core.utils.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        mock_dt.utcnow.return_value = frozen
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield frozen
