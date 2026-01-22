# Architecture Anti-Patterns

Common architectural mistakes and how to avoid them.

## Big Ball of Mud

**Description:** No discernible architecture. Code is tangled, with everything depending on everything.

### Symptoms

- No clear module boundaries
- Any change requires touching many files
- Circular dependencies everywhere
- "Utils" and "helpers" folders growing indefinitely
- Fear of refactoring

### Example

```python
# Bad — everything in one place
src/
├── models.py       # 2000 lines, 50 models
├── views.py        # 3000 lines, all endpoints
├── utils.py        # 1500 lines, random functions
├── helpers.py      # More random functions
└── database.py     # Global session, no abstraction

# models.py
from src.utils import send_email, calculate_tax, format_date
from src.helpers import validate_user, check_permissions
from src.database import session

class User:
    def save(self):
        session.add(self)  # Direct DB access in model
        session.commit()
        send_email(self.email, "Welcome!")  # Side effect!
```

### Solution

```python
# Good — modular architecture
src/
├── core/
│   ├── config.py
│   ├── database.py
│   └── exceptions.py
├── modules/
│   ├── users/
│   │   ├── models.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   └── routers.py
│   ├── orders/
│   │   └── ...
│   └── notifications/
│       └── ...
└── main.py

# Clear separation of concerns
class UserService:
    def __init__(
        self,
        repository: UserRepository,
        email_service: EmailService,
    ):
        self._repository = repository
        self._email_service = email_service

    async def create(self, data: UserCreateDTO) -> User:
        user = await self._repository.save(User(**data.model_dump()))
        await self._email_service.send_welcome(user.email)
        return user
```

## Golden Hammer

**Description:** Using one technology or pattern for everything, regardless of fit.

### Symptoms

- "We use microservices for everything"
- "Everything must be async"
- "All data goes in MongoDB"
- Using ORM for complex analytical queries
- REST API for real-time features

### Example

```python
# Bad — forcing REST for real-time
# Polling every second for chat messages
@router.get("/messages")
async def get_messages(since: datetime):
    return await service.get_messages_since(since)

# Client polls every second — inefficient!
```

### Solution

```python
# Good — right tool for the job
# WebSocket for real-time chat
@router.websocket("/ws/chat/{room_id}")
async def chat_websocket(
    websocket: WebSocket,
    room_id: str,
):
    await websocket.accept()
    async for message in chat_service.subscribe(room_id):
        await websocket.send_json(message)

# REST for CRUD operations
@router.get("/messages/{room_id}")
async def get_message_history(room_id: str) -> list[MessageDTO]:
    return await service.get_history(room_id)
```

### Technology Selection Guide

| Use Case | Technology |
|----------|------------|
| CRUD operations | REST API |
| Real-time updates | WebSocket, SSE |
| Complex queries | SQL, not ORM |
| Document storage | MongoDB, PostgreSQL JSONB |
| Caching | Redis |
| Background tasks | Celery, RQ, Temporal |
| Simple monolith | Modular monolith |
| High load, team scaling | Microservices |

## Tight Coupling

**Description:** Components directly depend on concrete implementations, making changes expensive.

### Symptoms

- Cannot test components in isolation
- Changing one class requires changing many others
- Importing concrete classes everywhere
- Hard to replace implementations

### Example

```python
# Bad — tight coupling
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Concrete!
        self.email = SendGridClient()  # Concrete!
        self.payment = StripeClient()  # Concrete!

    async def create_order(self, data: OrderData) -> Order:
        order = Order(**data)
        self.db.save(order)  # Cannot test without real DB
        self.payment.charge(order.total)  # Cannot test without Stripe
        self.email.send(order.user.email, "Order created")
        return order

# Cannot unit test — requires real services
async def test_create_order():
    service = OrderService()  # Connects to real DB, Stripe, SendGrid!
    await service.create_order(data)
```

### Solution

```python
# Good — loose coupling via interfaces
from typing import Protocol


class DatabaseProtocol(Protocol):
    async def save(self, entity: Any) -> Any: ...


class PaymentProtocol(Protocol):
    async def charge(self, amount: Decimal) -> str: ...


class EmailProtocol(Protocol):
    async def send(self, to: str, body: str) -> None: ...


class OrderService:
    def __init__(
        self,
        db: DatabaseProtocol,
        payment: PaymentProtocol,
        email: EmailProtocol,
    ):
        self._db = db
        self._payment = payment
        self._email = email

    async def create_order(self, data: OrderData) -> Order:
        order = Order(**data)
        await self._db.save(order)
        await self._payment.charge(order.total)
        await self._email.send(order.user.email, "Order created")
        return order


# Easy to test with mocks
async def test_create_order():
    mock_db = Mock(spec=DatabaseProtocol)
    mock_payment = Mock(spec=PaymentProtocol)
    mock_email = Mock(spec=EmailProtocol)

    service = OrderService(mock_db, mock_payment, mock_email)
    await service.create_order(data)

    mock_db.save.assert_called_once()
    mock_payment.charge.assert_called_once()
```

## God Object

**Description:** One class that knows too much and does too much.

### Symptoms

- Class with 50+ methods
- Class with 20+ dependencies
- Class name ends with "Manager", "Handler", "Processor"
- Single file with 1000+ lines

### Example

```python
# Bad — God Object
class UserManager:
    """Does everything related to users... and more."""

    def create_user(self, data): ...
    def update_user(self, id, data): ...
    def delete_user(self, id): ...
    def authenticate(self, email, password): ...
    def generate_token(self, user): ...
    def refresh_token(self, token): ...
    def send_welcome_email(self, user): ...
    def send_password_reset(self, user): ...
    def generate_report(self, user_ids): ...
    def export_to_csv(self, users): ...
    def export_to_pdf(self, users): ...
    def validate_email(self, email): ...
    def validate_password(self, password): ...
    def check_permissions(self, user, resource): ...
    def log_activity(self, user, action): ...
    # ... 30 more methods
```

### Solution

```python
# Good — Single Responsibility
class UserService:
    """Handles user CRUD operations."""
    def create(self, data: UserCreateDTO) -> User: ...
    def update(self, id: int, data: UserUpdateDTO) -> User: ...
    def delete(self, id: int) -> None: ...
    def get_by_id(self, id: int) -> User | None: ...


class AuthService:
    """Handles authentication."""
    def authenticate(self, email: str, password: str) -> User: ...
    def generate_tokens(self, user: User) -> TokenPair: ...
    def refresh_token(self, token: str) -> TokenPair: ...


class EmailService:
    """Handles email sending."""
    def send_welcome(self, email: str) -> None: ...
    def send_password_reset(self, email: str, token: str) -> None: ...


class UserReportService:
    """Handles user reports."""
    def generate(self, user_ids: list[int]) -> Report: ...
    def export_csv(self, report: Report) -> bytes: ...
    def export_pdf(self, report: Report) -> bytes: ...


class PermissionService:
    """Handles authorization."""
    def check(self, user: User, resource: str, action: str) -> bool: ...
```

## Circular Dependencies

**Description:** Module A depends on B, B depends on C, C depends on A.

### Symptoms

- Import errors at runtime
- Imports inside functions to avoid errors
- Difficult to understand data flow
- Cannot test modules in isolation

### Example

```python
# Bad — circular dependency
# users/services.py
from orders.services import OrderService

class UserService:
    def get_user_orders(self, user_id: int):
        return OrderService().get_by_user(user_id)

# orders/services.py
from users.services import UserService  # Circular!

class OrderService:
    def get_order_with_user(self, order_id: int):
        order = self.get_by_id(order_id)
        order.user = UserService().get_by_id(order.user_id)
        return order
```

### Solution

```python
# Good — Dependency Inversion
# shared/protocols.py
from typing import Protocol


class UserServiceProtocol(Protocol):
    async def get_by_id(self, id: int) -> User | None: ...


class OrderServiceProtocol(Protocol):
    async def get_by_user(self, user_id: int) -> list[Order]: ...


# users/services.py
class UserService:
    def __init__(self, order_service: OrderServiceProtocol):
        self._order_service = order_service

    async def get_user_with_orders(self, user_id: int):
        user = await self.get_by_id(user_id)
        user.orders = await self._order_service.get_by_user(user_id)
        return user


# orders/services.py
class OrderService:
    def __init__(self, user_service: UserServiceProtocol):
        self._user_service = user_service

    async def get_order_with_user(self, order_id: int):
        order = await self.get_by_id(order_id)
        order.user = await self._user_service.get_by_id(order.user_id)
        return order


# Wire up in DI container — no circular imports!
```

## Anemic Domain Model

**Description:** Domain objects are just data containers with no behavior.

### Symptoms

- Models only have fields, no methods
- All logic in services
- Services manipulate model internals directly
- Validation scattered across codebase

### Example

```python
# Bad — anemic model
class Order:
    id: int
    status: str
    items: list
    total: Decimal


class OrderService:
    def cancel_order(self, order: Order) -> None:
        # Logic that should be in Order
        if order.status in ("pending", "confirmed"):
            order.status = "cancelled"
            for item in order.items:
                item.restore_stock()
        else:
            raise ValueError("Cannot cancel")

    def calculate_total(self, order: Order) -> Decimal:
        # Logic that should be in Order
        total = sum(item.price * item.quantity for item in order.items)
        if order.discount:
            total -= order.discount
        return total
```

### Solution

```python
# Good — rich domain model
class Order:
    id: int
    status: OrderStatus
    items: list[OrderItem]
    discount: Decimal | None

    @property
    def total(self) -> Decimal:
        """Calculate order total."""
        subtotal = sum(item.subtotal for item in self.items)
        if self.discount:
            return subtotal - self.discount
        return subtotal

    def can_cancel(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)

    def cancel(self) -> None:
        """Cancel the order."""
        if not self.can_cancel():
            raise OrderCannotBeCancelledError(self.status)
        self.status = OrderStatus.CANCELLED
        for item in self.items:
            item.restore_stock()

    def add_item(self, product: Product, quantity: int) -> None:
        """Add item to order."""
        if self.status != OrderStatus.DRAFT:
            raise OrderNotEditableError()
        existing = next((i for i in self.items if i.product_id == product.id), None)
        if existing:
            existing.quantity += quantity
        else:
            self.items.append(OrderItem(product=product, quantity=quantity))


class OrderService:
    """Thin service — orchestrates, doesn't contain logic."""

    async def cancel(self, order_id: int) -> Order:
        order = await self._repository.get_by_id(order_id)
        order.cancel()  # Domain logic in model
        await self._repository.save(order)
        await self._event_bus.publish(OrderCancelled(order_id))
        return order
```

## Distributed Monolith

**Description:** Microservices that are so tightly coupled they behave like a monolith but with network overhead.

### Symptoms

- Services must be deployed together
- Synchronous calls between services
- Shared database between services
- One service change breaks others
- Complex distributed transactions

### Example

```python
# Bad — distributed monolith
class OrderService:
    async def create_order(self, data: OrderData) -> Order:
        # Synchronous calls to other services
        user = await self.user_service.get_user(data.user_id)  # Sync HTTP
        if not user:
            raise UserNotFoundError()

        for item in data.items:
            # Sync call for each item!
            product = await self.product_service.get_product(item.product_id)
            stock = await self.inventory_service.check_stock(item.product_id)
            if stock < item.quantity:
                raise OutOfStockError()

        # Try to reserve across services
        for item in data.items:
            await self.inventory_service.reserve(item.product_id, item.quantity)

        order = Order(**data)
        await self.repository.save(order)

        # Sync payment
        await self.payment_service.charge(user.id, order.total)

        return order
        # If any service fails — manual rollback nightmare!
```

### Solution

```python
# Good — loosely coupled services with events
class OrderService:
    async def create_order(self, data: OrderData) -> Order:
        # Local validation only
        order = Order(**data, status=OrderStatus.PENDING)
        await self._repository.save(order)

        # Publish event — other services react asynchronously
        await self._event_bus.publish(OrderCreated(
            order_id=order.id,
            user_id=data.user_id,
            items=data.items,
        ))

        return order


# Saga pattern for distributed transactions
class OrderSaga:
    """Orchestrates order creation across services."""

    async def handle_order_created(self, event: OrderCreated) -> None:
        try:
            # Step 1: Reserve inventory
            await self._inventory_client.reserve(event.items)

            # Step 2: Process payment
            await self._payment_client.charge(event.user_id, event.total)

            # Step 3: Confirm order
            await self._order_client.confirm(event.order_id)

        except InventoryError:
            await self._order_client.cancel(event.order_id, "Out of stock")

        except PaymentError:
            # Compensating transaction
            await self._inventory_client.release(event.items)
            await self._order_client.cancel(event.order_id, "Payment failed")
```

## Premature Optimization

**Description:** Optimizing before measuring, adding complexity for hypothetical performance gains.

### Symptoms

- Caching everything without profiling
- Microservices for <1000 users
- Complex async where sync is fine
- Denormalization without measured need

### Example

```python
# Bad — premature complexity
class UserService:
    def __init__(
        self,
        redis: Redis,
        read_replica: AsyncSession,
        write_db: AsyncSession,
        search_engine: Elasticsearch,
    ):
        self._cache = redis
        self._read_db = read_replica
        self._write_db = write_db
        self._search = search_engine

    async def get_user(self, id: int) -> User:
        # L1 cache
        cached = await self._cache.get(f"user:{id}")
        if cached:
            return User.model_validate_json(cached)

        # Read from replica
        user = await self._read_db.get(User, id)
        if user:
            # Update cache
            await self._cache.setex(f"user:{id}", 3600, user.model_dump_json())

        return user
    # All this for 100 users/day?
```

### Solution

```python
# Good — start simple, optimize when needed
class UserService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, id: int) -> User | None:
        return await self._session.get(User, id)

# Add caching ONLY when metrics show it's needed
# Add read replicas ONLY when write load is proven bottleneck
# Add search engine ONLY when LIKE queries are too slow
```

## Detection Checklist

| Anti-Pattern | Warning Signs |
|--------------|---------------|
| Big Ball of Mud | utils.py > 500 lines, no module structure |
| Golden Hammer | Same pattern for all problems |
| Tight Coupling | Cannot test without real dependencies |
| God Object | Class with 20+ methods |
| Circular Deps | Import inside function |
| Anemic Model | All logic in services, models are DTOs |
| Distributed Monolith | Services share DB, sync HTTP calls |
| Premature Optimization | Caching without metrics |
