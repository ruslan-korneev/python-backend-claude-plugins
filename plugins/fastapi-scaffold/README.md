# fastapi-scaffold

Plugin for generating FastAPI boilerplate code with best practices.

## Philosophy

- **Repository Pattern** — BaseRepository with generics for type safety
- **Dependency Injection** — dependency-injector for dependency management
- **DTOs** — Pydantic v2 models with `from_attributes=True`
- **Modular Structure** — `src/modules/{name}/` for each module
- **TDD Ready** — tests are generated together with code

## Features

- `/fastapi:module` — create a complete module (models, dto, repositories, services, routers + tests)
- `/fastapi:endpoint` — add an endpoint with service and test
- `/fastapi:dto` — generate DTOs from SQLAlchemy model

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install fastapi-scaffold@python-backend-plugins
```

## Commands

### `/fastapi:module <name>`

Creates a complete module:

```
/fastapi:module users
/fastapi:module orders
```

Generates:
```
src/modules/users/
├── __init__.py
├── models.py       # SQLAlchemy model
├── dto.py          # Create/Read/Update DTOs
├── repositories.py # Repository with BaseRepository
├── services.py     # Business logic
└── routers.py      # FastAPI endpoints

tests/modules/users/
├── conftest.py
├── test_services.py
└── test_routers.py
```

### `/fastapi:endpoint <method> <path> <module>`

Adds an endpoint to an existing module:

```
/fastapi:endpoint POST /users/{user_id}/orders users
/fastapi:endpoint GET /users/{user_id}/profile users
/fastapi:endpoint DELETE /orders/{order_id}/items/{item_id} orders
```

### `/fastapi:dto <model>`

Generates DTOs from SQLAlchemy model:

```
/fastapi:dto User
/fastapi:dto src/modules/orders/models.py
```

## Architecture

```
Router → Service → Repository → Database
   ↓        ↓          ↓
  DTO     DTO     Model/DTO
```

### BaseRepository

```python
class BaseRepository[ModelT, CreateDTOT, ReadDTOT]:
    async def get_all(self) -> Sequence[ReadDTOT]: ...
    async def get_by_id(self, id: int) -> ModelT | None: ...
    async def save(self, data: ModelT | CreateDTOT) -> ModelT: ...
    async def update(self, id: int, data: BaseModel) -> ModelT | None: ...
    async def delete(self, id: int) -> bool: ...
```

### BaseDTO

```python
class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
```

### Exceptions

```python
class AppError(Exception):
    status_code: int
    detail: str

class NotFoundError(AppError): ...
class ConflictError(AppError): ...
```

### DI Container

```python
class Container(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserRepository, session=session_maker)
    user_service = providers.Factory(UserService, repository=user_repository)
```

## Plugin Structure

```
fastapi-scaffold/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── module.md
│   ├── endpoint.md
│   └── dto.md
├── skills/
│   └── fastapi-patterns/
│       ├── SKILL.md
│       └── references/
│           ├── repository.md
│           ├── di.md
│           ├── exceptions.md
│           └── dto.md
└── README.md
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [dependency-injector](https://python-dependency-injector.ets-labs.org/)
