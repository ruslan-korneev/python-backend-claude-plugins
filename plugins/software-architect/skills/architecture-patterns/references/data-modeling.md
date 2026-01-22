# Data Modeling with SQLAlchemy 2.0

Best practices for designing database schemas with SQLAlchemy 2.0 and PostgreSQL.

## Model Fundamentals

### Base Model Setup

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class BaseModel(Base, TimestampMixin):
    """Base model with timestamps."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
```

### Using Mapped Columns (SQLAlchemy 2.0 style)

```python
from sqlalchemy import String, Text, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column


class Product(BaseModel):
    __tablename__ = "products"

    # Required fields
    name: Mapped[str] = mapped_column(String(255))
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Optional fields (nullable)
    description: Mapped[str | None] = mapped_column(Text)

    # With defaults
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    # Decimal for money
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
```

## Relationships

### One-to-Many

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)

    # One user has many orders
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Order(BaseModel):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Many orders belong to one user
    user: Mapped["User"] = relationship(back_populates="orders")
```

### Many-to-Many

```python
from sqlalchemy import Table, Column, ForeignKey, Integer


# Association table
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Product(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255))

    tags: Mapped[list["Tag"]] = relationship(
        secondary=product_tags,
        back_populates="products",
    )


class Tag(BaseModel):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_tags,
        back_populates="tags",
    )
```

### Many-to-Many with Extra Data

```python
class OrderItem(BaseModel):
    """Association object with extra data."""
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        primary_key=True,
    )

    # Extra fields
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


class Order(BaseModel):
    __tablename__ = "orders"

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
```

### Self-Referential (Tree Structure)

```python
class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
    )

    # Self-referential relationships
    parent: Mapped["Category | None"] = relationship(
        back_populates="children",
        remote_side="Category.id",
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
    )
```

## Indexing Strategy

### Basic Indexes

```python
from sqlalchemy import Index


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# Composite index for common queries
Index("ix_users_active_created", User.is_active, User.created_at)
```

### Partial Index

```python
from sqlalchemy import Index


class Order(BaseModel):
    __tablename__ = "orders"

    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        # Index only pending orders (PostgreSQL)
        Index(
            "ix_orders_pending",
            "created_at",
            postgresql_where=(status == "pending"),
        ),
    )
```

### Index for JSON Fields

```python
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB


class Product(BaseModel):
    __tablename__ = "products"

    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    __table_args__ = (
        # GIN index for JSONB
        Index(
            "ix_products_metadata",
            metadata_,
            postgresql_using="gin",
        ),
    )
```

## Soft Delete Pattern

```python
from datetime import datetime
from sqlalchemy import DateTime, event
from sqlalchemy.orm import Mapped, mapped_column, Query


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        self.deleted_at = None


class User(BaseModel, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True)


# Repository with soft delete support
class UserRepository:
    async def get_active(self) -> Sequence[User]:
        stmt = select(User).where(User.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_deleted(self) -> Sequence[User]:
        stmt = select(User).where(User.deleted_at.is_not(None))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def soft_delete(self, user: User) -> None:
        user.soft_delete()
        await self._session.flush()
```

## Audit Trail Pattern

```python
from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(Base):
    """Audit trail for tracking changes."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    table_name: Mapped[str] = mapped_column(String(100), index=True)
    record_id: Mapped[int] = mapped_column(index=True)
    action: Mapped[AuditAction] = mapped_column(String(20))
    old_values: Mapped[dict | None] = mapped_column(JSONB)
    new_values: Mapped[dict | None] = mapped_column(JSONB)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )


# Service for audit logging
class AuditService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def log_create(
        self,
        entity: Base,
        user_id: int | None = None,
    ) -> None:
        log = AuditLog(
            table_name=entity.__tablename__,
            record_id=entity.id,
            action=AuditAction.CREATE,
            new_values=self._serialize(entity),
            user_id=user_id,
        )
        self._session.add(log)

    async def log_update(
        self,
        entity: Base,
        old_values: dict,
        user_id: int | None = None,
    ) -> None:
        log = AuditLog(
            table_name=entity.__tablename__,
            record_id=entity.id,
            action=AuditAction.UPDATE,
            old_values=old_values,
            new_values=self._serialize(entity),
            user_id=user_id,
        )
        self._session.add(log)

    def _serialize(self, entity: Base) -> dict:
        return {
            c.name: getattr(entity, c.name)
            for c in entity.__table__.columns
            if not c.name.startswith("_")
        }
```

## Versioning Pattern (Optimistic Locking)

```python
from sqlalchemy import Integer, event
from sqlalchemy.orm import Mapped, mapped_column


class VersionedMixin:
    """Mixin for optimistic locking."""

    version: Mapped[int] = mapped_column(Integer, default=1)


class Product(BaseModel, VersionedMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255))
    stock: Mapped[int] = mapped_column(Integer, default=0)

    __mapper_args__ = {"version_id_col": version}


# Repository with optimistic locking
class ProductRepository:
    async def update_stock(
        self,
        product_id: int,
        quantity: int,
        expected_version: int,
    ) -> Product:
        product = await self._session.get(Product, product_id)
        if not product:
            raise NotFoundError("Product not found")

        if product.version != expected_version:
            raise ConflictError(
                f"Product was modified. Expected version {expected_version}, "
                f"got {product.version}"
            )

        product.stock += quantity
        await self._session.flush()
        return product
```

## Enum Handling

```python
from enum import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(BaseModel):
    __tablename__ = "orders"

    # Store as string (recommended for migrations)
    status: Mapped[OrderStatus] = mapped_column(
        String(20),
        default=OrderStatus.PENDING,
    )

    # Domain methods
    def can_cancel(self) -> bool:
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED)

    def cancel(self) -> None:
        if not self.can_cancel():
            raise InvalidStateError(
                f"Cannot cancel order in {self.status} status"
            )
        self.status = OrderStatus.CANCELLED
```

## Normalization Guidelines

### First Normal Form (1NF)

```python
# Bad — repeating groups
class Order(BaseModel):
    item1_name: Mapped[str]
    item1_qty: Mapped[int]
    item2_name: Mapped[str | None]
    item2_qty: Mapped[int | None]

# Good — separate table
class Order(BaseModel):
    items: Mapped[list["OrderItem"]] = relationship()

class OrderItem(BaseModel):
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    name: Mapped[str]
    quantity: Mapped[int]
```

### Second Normal Form (2NF)

```python
# Bad — partial dependency on composite key
class OrderItem(BaseModel):
    order_id: Mapped[int]
    product_id: Mapped[int]
    product_name: Mapped[str]  # Depends only on product_id!
    quantity: Mapped[int]

# Good — reference product table
class OrderItem(BaseModel):
    order_id: Mapped[int]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]

    product: Mapped["Product"] = relationship()
```

### Third Normal Form (3NF)

```python
# Bad — transitive dependency
class Order(BaseModel):
    user_id: Mapped[int]
    user_email: Mapped[str]  # Depends on user_id, not on order!
    user_name: Mapped[str]   # Same issue

# Good — normalize
class Order(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship()
```

### When to Denormalize

```python
# Acceptable denormalization for read performance
class OrderItem(BaseModel):
    order_id: Mapped[int]
    product_id: Mapped[int]

    # Snapshot at order time (prices change!)
    unit_price: Mapped[Decimal]
    product_name: Mapped[str]

    # Calculated field for fast queries
    total: Mapped[Decimal]  # unit_price * quantity


# Materialized view for complex aggregations
# (handled via Alembic migration)
"""
CREATE MATERIALIZED VIEW order_summary AS
SELECT
    user_id,
    COUNT(*) as order_count,
    SUM(total) as total_spent
FROM orders
GROUP BY user_id;
"""
```

## Query Optimization

### Avoiding N+1 Queries

```python
from sqlalchemy.orm import selectinload, joinedload


class OrderRepository:
    # Bad — N+1 queries
    async def get_orders_bad(self) -> Sequence[Order]:
        result = await self._session.execute(select(Order))
        orders = result.scalars().all()
        for order in orders:
            _ = order.items  # Extra query for each order!
        return orders

    # Good — eager loading
    async def get_orders_with_items(self) -> Sequence[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))  # Single additional query
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    # For single relationship — joinedload
    async def get_orders_with_user(self) -> Sequence[Order]:
        stmt = (
            select(Order)
            .options(joinedload(Order.user))  # JOIN in same query
        )
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()
```

### Selecting Specific Columns

```python
from sqlalchemy import select


class UserRepository:
    # Only fetch needed columns
    async def get_emails(self) -> Sequence[str]:
        stmt = select(User.email).where(User.is_active.is_(True))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    # Return as DTO directly
    async def get_user_summaries(self) -> Sequence[UserSummaryDTO]:
        stmt = select(User.id, User.email, User.name)
        result = await self._session.execute(stmt)
        return [
            UserSummaryDTO(id=row.id, email=row.email, name=row.name)
            for row in result
        ]
```
