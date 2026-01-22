# Architecture Patterns

System-level architecture patterns for Python backend projects (FastAPI + SQLAlchemy 2.0).

## Triggers

Use this skill when the user:
- Designs a new system or major feature
- Asks about project structure or module boundaries
- Makes data modeling decisions
- Designs API contracts
- Evaluates architectural trade-offs
- Creates or reviews Architecture Decision Records (ADR)
- Needs to modernize legacy code

## Abstraction Levels

| Plugin | Level | Focus |
|--------|-------|-------|
| **software-architect** | System | Architecture, modules, ADR |
| fastapi-scaffold | Module | Boilerplate generation |
| clean-code | Code | SOLID, code smells |

## 5 Core Principles

### 1. Modularity & Separation of Concerns

```python
# Good — clear module boundaries
src/
├── core/           # Infrastructure (config, db, exceptions)
├── modules/
│   ├── users/      # User domain — fully autonomous
│   ├── orders/     # Order domain — depends on users via interfaces
│   └── payments/   # Payment domain — depends on orders via interfaces
└── main.py

# Bad — tangled dependencies
src/
├── models.py       # All models in one file
├── services.py     # All services mixed
├── routes.py       # All routes together
└── utils.py        # "Utils" — the graveyard of architecture
```

### 2. Scalability (Stateless, Horizontal Scaling)

```python
# Good — stateless service, state in external storage
class OrderService:
    def __init__(self, cache: CacheProtocol, db: AsyncSession):
        self._cache = cache  # Redis
        self._db = db        # PostgreSQL

    async def get_order(self, order_id: int) -> Order:
        # Check cache first
        cached = await self._cache.get(f"order:{order_id}")
        if cached:
            return Order.model_validate_json(cached)
        # Fallback to DB
        return await self._repository.get_by_id(order_id)

# Bad — state in memory
class OrderService:
    _orders_cache: dict[int, Order] = {}  # Lost on restart!
```

### 3. Maintainability (Testability, Clear Organization)

```python
# Good — dependencies via constructor (easy to test)
class UserService:
    def __init__(
        self,
        repository: UserRepositoryProtocol,
        email_sender: EmailSenderProtocol,
    ):
        self._repository = repository
        self._email_sender = email_sender

# Test with mocks
async def test_create_user():
    mock_repo = Mock(spec=UserRepositoryProtocol)
    mock_email = Mock(spec=EmailSenderProtocol)
    service = UserService(mock_repo, mock_email)
    # ...

# Bad — hidden dependencies
class UserService:
    def create_user(self, data: UserCreate) -> User:
        from app.email import send_email  # Hidden import!
        from app.db import get_session    # Hidden dependency!
```

### 4. Security (Defense in Depth, Least Privilege)

```python
# Good — validation at every layer
# Router layer
@router.post("/orders")
async def create_order(
    data: OrderCreateDTO,  # Pydantic validation
    current_user: Annotated[User, Depends(get_current_user)],  # Auth
) -> OrderReadDTO:
    # Authorization check
    if not current_user.can_create_orders:
        raise ForbiddenError("User cannot create orders")
    return await service.create(data, current_user.id)

# Service layer
class OrderService:
    async def create(self, data: OrderCreateDTO, user_id: int) -> Order:
        # Business rules validation
        if data.total > MAX_ORDER_AMOUNT:
            raise ValidationError("Order amount exceeds limit")
        # ...

# Repository layer — parameterized queries only
async def get_by_id(self, order_id: int) -> Order | None:
    stmt = select(Order).where(Order.id == order_id)  # No f-strings!
    result = await self._session.execute(stmt)
    return result.scalar_one_or_none()
```

### 5. Performance (Efficient Algorithms, Caching)

```python
# Good — selective loading, caching
class OrderRepository:
    async def get_with_items(self, order_id: int) -> Order:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))  # Eager load
            .where(Order.id == order_id)
        )
        return (await self._session.execute(stmt)).scalar_one()

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Order]:
        stmt = select(Order).offset(offset).limit(limit)  # Pagination
        return (await self._session.execute(stmt)).scalars().all()

# Bad — N+1 queries, no pagination
async def get_all_with_items(self) -> list[Order]:
    orders = await self._session.execute(select(Order))
    for order in orders:
        _ = order.items  # N+1 query for each order!
    return orders.scalars().all()
```

## Architectural Patterns

More details: `${CLAUDE_PLUGIN_ROOT}/skills/architecture-patterns/references/layered-architecture.md`

### Layered Architecture

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│        (Routers, DTOs, OpenAPI)         │
├─────────────────────────────────────────┤
│           Application Layer             │
│     (Services, Use Cases, Events)       │
├─────────────────────────────────────────┤
│             Domain Layer                │
│   (Entities, Value Objects, Rules)      │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│   (Repositories, External Services)     │
└─────────────────────────────────────────┘
```

**Dependency Rule:** Dependencies point inward. Inner layers don't know about outer layers.

### Repository Pattern

```python
from abc import abstractmethod
from typing import Protocol, Generic, TypeVar

T = TypeVar("T")


class RepositoryProtocol(Protocol[T]):
    """Abstract repository interface."""

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None: ...

    @abstractmethod
    async def save(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, id: int) -> None: ...


class SQLAlchemyRepository(RepositoryProtocol[T]):
    """Concrete implementation for SQLAlchemy."""

    def __init__(self, session: AsyncSession, model: type[T]):
        self._session = session
        self._model = model

    async def get_by_id(self, id: int) -> T | None:
        return await self._session.get(self._model, id)
```

### Event-Driven Architecture

```python
from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class DomainEvent:
    """Base domain event."""
    pass

@dataclass
class UserCreated(DomainEvent):
    user_id: int
    email: str

class EventBus:
    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[Callable]] = {}

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: Callable[[DomainEvent], Awaitable[None]],
    ) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)

# Usage
event_bus = EventBus()
event_bus.subscribe(UserCreated, send_welcome_email)
event_bus.subscribe(UserCreated, create_default_settings)

# In service
await event_bus.publish(UserCreated(user_id=user.id, email=user.email))
```

### CQRS (Command Query Responsibility Segregation)

```python
# Commands — write operations
class CreateOrderCommand:
    user_id: int
    items: list[OrderItemDTO]

class CommandHandler:
    async def handle(self, command: CreateOrderCommand) -> int:
        # Complex write logic with validation
        order = Order(user_id=command.user_id)
        for item in command.items:
            order.add_item(item)
        await self._repository.save(order)
        return order.id

# Queries — read operations (can use different DB, denormalized views)
class OrderQueryService:
    async def get_order_summary(self, order_id: int) -> OrderSummaryDTO:
        # Optimized read query, possibly from read replica
        return await self._read_repository.get_summary(order_id)
```

## Anti-Patterns

More details: `${CLAUDE_PLUGIN_ROOT}/skills/architecture-patterns/references/anti-patterns.md`

| Anti-Pattern | Description | Solution |
|--------------|-------------|----------|
| Big Ball of Mud | No structure, everything depends on everything | Modular architecture |
| Golden Hammer | Using one technology for everything | Choose right tool for the job |
| Tight Coupling | Direct dependencies between modules | Interfaces, DI |
| God Object | One class knows and does everything | Single Responsibility |
| Circular Dependencies | A → B → C → A | Dependency Inversion |

## Plugin Commands

- `/architect:design <name>` — interactive architecture design for new project/module
- `/architect:modernize [path]` — legacy analysis + phased modernization plan
- `/architect:review [path]` — architecture analysis (structure, dependencies, patterns)
- `/architect:adr <title>` — create Architecture Decision Record
- `/architect:diagram <type>` — generate Mermaid diagram (component, data-flow, sequence, er, deployment)
- `/architect:deps [path]` — dependency analysis, detect circular dependencies
