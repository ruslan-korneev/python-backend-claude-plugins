# Layered Architecture for FastAPI

Layered architecture separates concerns into distinct layers with clear responsibilities and dependency rules.

## Layer Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Presentation Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │ Routers │  │  DTOs   │  │OpenAPI  │  │ Middleware  │    │
│  └────┬────┘  └────┬────┘  └─────────┘  └─────────────┘    │
├───────┼────────────┼────────────────────────────────────────┤
│       │   Application Layer                                 │
│       ▼            ▼                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │Services │  │Use Cases│  │ Events  │  │  Commands   │    │
│  └────┬────┘  └────┬────┘  └─────────┘  └─────────────┘    │
├───────┼────────────┼────────────────────────────────────────┤
│       │      Domain Layer                                   │
│       ▼            ▼                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │Entities │  │  Value  │  │ Domain  │  │  Domain     │    │
│  │         │  │ Objects │  │ Rules   │  │  Events     │    │
│  └────┬────┘  └─────────┘  └─────────┘  └─────────────┘    │
├───────┼─────────────────────────────────────────────────────┤
│       │   Infrastructure Layer                              │
│       ▼                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │  Repos  │  │External │  │  Cache  │  │  Messaging  │    │
│  │         │  │   APIs  │  │         │  │             │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Dependency Rules

**The Dependency Rule:** Source code dependencies must point inward only.

```
Presentation → Application → Domain ← Infrastructure
                    ↓           ↑
                    └───────────┘
```

- **Domain** — no dependencies on other layers
- **Application** — depends on Domain only
- **Infrastructure** — depends on Domain (implements interfaces)
- **Presentation** — depends on Application

## Project Structure

```
src/
├── core/                           # Shared infrastructure
│   ├── __init__.py
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── database.py                 # Engine, session factory
│   ├── container.py                # DI container
│   ├── dependencies.py             # FastAPI dependencies
│   ├── exceptions.py               # Base exceptions
│   └── repositories.py             # Base repository
│
├── modules/                        # Feature modules
│   ├── users/
│   │   ├── __init__.py            # Public API exports
│   │   ├── models.py              # SQLAlchemy models (Domain)
│   │   ├── dto.py                 # Pydantic DTOs (Presentation)
│   │   ├── repositories.py        # Data access (Infrastructure)
│   │   ├── services.py            # Business logic (Application)
│   │   └── routers.py             # HTTP endpoints (Presentation)
│   │
│   └── orders/
│       ├── __init__.py
│       ├── models.py
│       ├── dto.py
│       ├── repositories.py
│       ├── services.py
│       ├── routers.py
│       └── events.py              # Domain events
│
├── shared/                         # Cross-cutting concerns
│   ├── protocols.py               # Shared interfaces
│   ├── value_objects.py           # Shared value objects
│   └── events.py                  # Event bus
│
└── main.py                         # Application entry point
```

## Layer Responsibilities

### Presentation Layer

Handles HTTP concerns: routing, request/response transformation, validation.

```python
# routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from .dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from .services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateDTO,
    service: Annotated[UserService, Depends()],
) -> UserReadDTO:
    """Create a new user."""
    return await service.create(data)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends()],
) -> UserReadDTO:
    """Get user by ID."""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
```

```python
# dto.py
from pydantic import BaseModel, ConfigDict, EmailStr


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class UserCreateDTO(BaseDTO):
    email: EmailStr
    name: str
    password: str


class UserReadDTO(BaseDTO):
    id: int
    email: str
    name: str
    is_active: bool


class UserUpdateDTO(BaseDTO):
    name: str | None = None
    is_active: bool | None = None
```

### Application Layer

Contains business logic and orchestrates domain objects.

```python
# services.py
from typing import Sequence

from .dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from .repositories import UserRepository
from .models import User
from src.shared.events import EventBus
from src.modules.users.events import UserCreated


class UserService:
    def __init__(
        self,
        repository: UserRepository,
        event_bus: EventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def create(self, data: UserCreateDTO) -> UserReadDTO:
        # Business rule: check email uniqueness
        existing = await self._repository.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError(data.email)

        # Create user with hashed password
        user = User(
            email=data.email,
            name=data.name,
            password_hash=hash_password(data.password),
        )
        saved = await self._repository.save(user)

        # Publish domain event
        await self._event_bus.publish(
            UserCreated(user_id=saved.id, email=saved.email)
        )

        return UserReadDTO.model_validate(saved)

    async def get_by_id(self, user_id: int) -> UserReadDTO | None:
        user = await self._repository.get_by_id(user_id)
        if user:
            return UserReadDTO.model_validate(user)
        return None

    async def update(
        self,
        user_id: int,
        data: UserUpdateDTO,
    ) -> UserReadDTO | None:
        user = await self._repository.get_by_id(user_id)
        if not user:
            return None

        # Apply partial updates
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        updated = await self._repository.save(user)
        return UserReadDTO.model_validate(updated)
```

### Domain Layer

Contains business entities, value objects, and domain rules.

```python
# models.py
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Domain methods
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False

    def can_perform_action(self, action: str) -> bool:
        """Check if user can perform an action."""
        if not self.is_active:
            return False
        # Additional business rules...
        return True
```

```python
# events.py
from dataclasses import dataclass
from src.shared.events import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    user_id: int
    email: str


@dataclass
class UserDeactivated(DomainEvent):
    user_id: int
    reason: str
```

### Infrastructure Layer

Implements interfaces defined in domain, handles external concerns.

```python
# repositories.py
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[User]:
        stmt = select(User).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def save(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self._session.delete(user)
        await self._session.flush()
```

## Cross-Layer Communication

### Using Protocols for Loose Coupling

```python
# src/shared/protocols.py
from typing import Protocol, TypeVar, Sequence

T = TypeVar("T")


class RepositoryProtocol(Protocol[T]):
    async def get_by_id(self, id: int) -> T | None: ...
    async def save(self, entity: T) -> T: ...
    async def delete(self, entity: T) -> None: ...


class EmailSenderProtocol(Protocol):
    async def send(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> None: ...


class CacheProtocol(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int = 3600) -> None: ...
    async def delete(self, key: str) -> None: ...
```

### Dependency Injection

```python
# src/core/container.py
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from .database import engine
from src.modules.users.repositories import UserRepository
from src.modules.users.services import UserService
from src.shared.events import EventBus


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.modules.users.routers",
            "src.modules.orders.routers",
        ]
    )

    # Infrastructure
    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        expire_on_commit=False,
    )

    event_bus = providers.Singleton(EventBus)

    # User module
    user_repository = providers.Factory(
        UserRepository,
        session=providers.Dependency(),
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
        event_bus=event_bus,
    )
```

## Testing by Layer

```python
# Unit test — Service layer (mock repository)
async def test_user_service_create():
    mock_repo = Mock(spec=UserRepository)
    mock_repo.get_by_email.return_value = None
    mock_repo.save.return_value = User(id=1, email="test@example.com", ...)

    mock_event_bus = Mock(spec=EventBus)

    service = UserService(mock_repo, mock_event_bus)
    result = await service.create(UserCreateDTO(
        email="test@example.com",
        name="Test",
        password="secret",
    ))

    assert result.email == "test@example.com"
    mock_event_bus.publish.assert_called_once()


# Integration test — Repository layer (real database)
async def test_user_repository_save(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = User(email="test@example.com", name="Test", password_hash="hash")

    saved = await repo.save(user)
    await db_session.commit()

    assert saved.id is not None
    assert saved.email == "test@example.com"


# E2E test — Full stack
async def test_create_user_endpoint(client: AsyncClient):
    response = await client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "secret123",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
```

## Common Mistakes

### 1. Leaking Domain to Presentation

```python
# Bad — returning SQLAlchemy model directly
@router.get("/{user_id}")
async def get_user(user_id: int) -> User:  # Leaks domain!
    return await service.get_by_id(user_id)

# Good — return DTO
@router.get("/{user_id}")
async def get_user(user_id: int) -> UserReadDTO:
    return await service.get_by_id(user_id)
```

### 2. Business Logic in Router

```python
# Bad — business logic in router
@router.post("/")
async def create_user(data: UserCreateDTO):
    # Validation should be in service!
    if await repo.get_by_email(data.email):
        raise HTTPException(400, "Email exists")
    user = User(**data.model_dump())
    await repo.save(user)
    send_email(user.email, "Welcome!")  # Side effect in router!
    return user

# Good — router is thin
@router.post("/")
async def create_user(data: UserCreateDTO) -> UserReadDTO:
    return await service.create(data)  # All logic in service
```

### 3. Repository Returning DTOs

```python
# Bad — repository knows about DTOs
class UserRepository:
    async def get_by_id(self, user_id: int) -> UserReadDTO | None:
        user = await self._session.get(User, user_id)
        return UserReadDTO.model_validate(user) if user else None

# Good — repository returns domain entities
class UserRepository:
    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)
```
