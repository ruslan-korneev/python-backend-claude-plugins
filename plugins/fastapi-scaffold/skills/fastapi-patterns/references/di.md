# Dependency Injection with dependency-injector

## Installation

```bash
uv add dependency-injector
```

## Container

```python
"""DI Container."""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.modules.users.repositories import UserRepository
from src.modules.users.services import UserService
from src.modules.orders.repositories import OrderRepository
from src.modules.orders.services import OrderService


class Container(containers.DeclarativeContainer):
    """Application DI container."""

    # Configuration
    config = providers.Configuration()

    # Database
    engine = providers.Singleton(
        create_async_engine,
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )

    session_maker = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Repositories
    user_repository = providers.Factory(
        UserRepository,
        session=session_maker,
    )

    order_repository = providers.Factory(
        OrderRepository,
        session=session_maker,
    )

    # Services
    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )

    order_service = providers.Factory(
        OrderService,
        repository=order_repository,
        user_service=user_service,
    )
```

## Wiring in main.py

```python
"""Application entry point."""

from fastapi import FastAPI
from dependency_injector.wiring import inject, Provide

from src.core.container import Container
from src.modules.users.routers import router as user_router
from src.modules.orders.routers import router as order_router


def create_app() -> FastAPI:
    """Create FastAPI application."""
    container = Container()

    # Wire container to modules
    container.wire(modules=[
        "src.modules.users.routers",
        "src.modules.orders.routers",
    ])

    app = FastAPI(title="My API")
    app.container = container

    # Include routers
    app.include_router(user_router, prefix="/api/v1")
    app.include_router(order_router, prefix="/api/v1")

    return app


app = create_app()
```

## Usage in Routers

### Basic Pattern

```python
"""User routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from src.core.container import Container
from .dto import UserCreateDTO, UserReadDTO
from .services import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
@inject
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> UserReadDTO:
    """Get user by ID."""
    return await service.get_by_id(user_id)


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: UserCreateDTO,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> UserReadDTO:
    """Create new user."""
    return await service.create(data)
```

### Multiple Services

```python
@router.post("/{user_id}/orders")
@inject
async def create_user_order(
    user_id: int,
    data: OrderCreateDTO,
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
    order_service: Annotated[OrderService, Depends(Provide[Container.order_service])],
) -> OrderReadDTO:
    """Create order for user."""
    # Validate user exists
    await user_service.get_by_id(user_id)

    # Create order
    return await order_service.create_for_user(user_id, data)
```

## Session Management

### Option 1: Session via SessionMaker

```python
class UserRepository:
    """Repository with session maker."""

    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def get_by_id(self, user_id: int) -> User | None:
        async with self._session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
```

### Option 2: Session via Depends

```python
# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    """Get database session."""
    async with session_maker() as session:
        yield session


# container.py
class Container(containers.DeclarativeContainer):
    session = providers.Resource(get_session)

    user_repository = providers.Factory(
        UserRepository,
        session=session,
    )
```

### Option 3: FakeSessionMaker for Tests

```python
# tests/conftest.py
class FakeSessionMaker:
    """Fake session maker for tests."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, *args) -> None:
        pass


@pytest.fixture
def container(fake_session_maker):
    """Container with overridden session."""
    container = Container()
    container.session_maker.override(providers.Object(fake_session_maker))
    yield container
    container.reset_override()
```

## Providers

### Factory vs Singleton

```python
# Factory — creates a new instance on each call
user_service = providers.Factory(UserService)

# Singleton — creates one instance
engine = providers.Singleton(create_async_engine, url)

# Resource — for resources with cleanup
session = providers.Resource(get_session)
```

### Callable

```python
# For functions
hash_password = providers.Callable(
    bcrypt.hashpw,
    password=providers.Dependency(),
    salt=bcrypt.gensalt(),
)
```

### Configuration

```python
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()


container = Container()
container.config.from_dict({
    "database": {"url": "postgresql://..."},
    "redis": {"host": "localhost"},
})
```

## Override in Tests

```python
@pytest.fixture
def container():
    container = Container()

    # Override with mock
    mock_email_service = AsyncMock()
    container.email_service.override(providers.Object(mock_email_service))

    yield container

    container.reset_override()


async def test_user_registration(container):
    user_service = container.user_service()
    # email_service is mocked
    await user_service.register(data)
```

## Async Initialization

```python
class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(
        create_async_engine,
        url=settings.database_url,
    )

    @providers.coroutine
    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# main.py
@app.on_event("startup")
async def startup():
    await app.container.init_db()
```
