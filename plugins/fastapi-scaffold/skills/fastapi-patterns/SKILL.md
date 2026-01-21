# FastAPI Patterns

Best practices and patterns for FastAPI projects with SQLAlchemy 2.0 and dependency-injector.

## Triggers

Use this skill when the user:
- Creates a new FastAPI project or module
- Asks about FastAPI application structure
- Works with SQLAlchemy models and repositories
- Configures Dependency Injection
- Creates DTOs (Pydantic models)

## Layer Architecture

```
Router → Service → Repository → Database
   ↓        ↓          ↓
  DTO     DTO     Model/DTO
```

- **Router** — HTTP endpoints, request validation
- **Service** — business logic, orchestration
- **Repository** — database operations, CRUD operations

## Modular Structure

```
src/
├── core/
│   ├── config.py         # Settings (pydantic-settings)
│   ├── database.py       # Engine, Base, session
│   ├── container.py      # DI Container
│   ├── dependencies.py   # FastAPI dependencies
│   ├── exceptions.py     # Custom exceptions
│   └── repositories.py   # BaseRepository
├── modules/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── dto.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   └── routers.py
│   └── orders/
│       └── ...
└── main.py
```

## BaseRepository with Generics

More details: `${CLAUDE_PLUGIN_ROOT}/skills/fastapi-patterns/references/repository.md`

```python
from typing import Generic, TypeVar
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")
CreateDTOT = TypeVar("CreateDTOT")
ReadDTOT = TypeVar("ReadDTOT")


class BaseRepository(Generic[ModelT, CreateDTOT, ReadDTOT]):
    """Base repository with generic CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def get_all(self) -> Sequence[ReadDTOT]:
        result = await self._session.execute(select(self._model))
        return result.scalars().all()

    async def save(self, data: ModelT | CreateDTOT) -> ReadDTOT:
        if isinstance(data, self._model):
            entity = data
        else:
            entity = self._model(**data.model_dump())
        self._session.add(entity)
        await self._session.flush()
        return entity
```

## DTOs with Pydantic v2

More details: `${CLAUDE_PLUGIN_ROOT}/skills/fastapi-patterns/references/dto.md`

```python
from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Base DTO with ORM mode."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class UserCreateDTO(BaseDTO):
    email: str
    name: str


class UserReadDTO(BaseDTO):
    id: int
    email: str
    name: str
```

## Dependency Injection

More details: `${CLAUDE_PLUGIN_ROOT}/skills/fastapi-patterns/references/di.md`

```python
# container.py
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session_maker = providers.Singleton(
        async_sessionmaker,
        bind=engine,
    )

    user_repository = providers.Factory(
        UserRepository,
        session=session_maker,
    )

    user_service = providers.Factory(
        UserService,
        repository=user_repository,
    )


# routers.py
from dependency_injector.wiring import inject, Provide


@router.get("/users/{id}")
@inject
async def get_user(
    id: int,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> UserReadDTO:
    return await service.get_by_id(id)
```

## Exception Handling

More details: `${CLAUDE_PLUGIN_ROOT}/skills/fastapi-patterns/references/exceptions.md`

```python
# exceptions.py
class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    detail = "Resource already exists"


# handlers.py
async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# main.py
app.add_exception_handler(AppError, app_exception_handler)
```

## Transaction Management

```python
# Via session_maker context manager
async def create_order(self, data: OrderCreateDTO) -> OrderReadDTO:
    async with self._session_maker() as session:
        order = Order(**data.model_dump())
        session.add(order)
        await session.commit()
        return OrderReadDTO.model_validate(order)

# Or via repository
async def create_with_items(self, data: OrderCreateDTO) -> OrderReadDTO:
    order = await self._order_repo.save(data)
    for item in data.items:
        await self._item_repo.save(OrderItem(order_id=order.id, **item))
    await self._session.commit()
    return order
```

## Plugin Commands

- `/fastapi:module <name>` — create a complete module
- `/fastapi:endpoint <method> <path> <module>` — create an endpoint
- `/fastapi:dto <model>` — create DTOs from model
