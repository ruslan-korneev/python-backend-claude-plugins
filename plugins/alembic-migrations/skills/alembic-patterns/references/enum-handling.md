# Enum Handling in Alembic

## Problem

Alembic autogenerate creates enum types in upgrade, but **does not delete them in downgrade**. This leads to:
- Accumulation of orphan enum types in DB
- Errors when reapplying migrations
- Problems with testing (upgrade/downgrade cycle)

## Solution

Always explicitly manage the lifecycle of enum types.

## Patterns

### 1. Creating table with enum

```python
import sqlalchemy as sa
from alembic import op

# Define enum at module level
status_type = sa.Enum("pending", "processing", "completed", name="order_status")


def upgrade() -> None:
    # Enum is created automatically when creating the table
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", status_type, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # First delete the table
    op.drop_table("orders")
    # Then delete the enum type
    status_type.drop(op.get_bind(), checkfirst=False)
```

### 2. Adding column with enum

```python
def upgrade() -> None:
    # First create enum type
    priority_type = sa.Enum("low", "medium", "high", name="task_priority")
    priority_type.create(op.get_bind(), checkfirst=True)

    # Then add column
    op.add_column(
        "tasks",
        sa.Column("priority", priority_type, nullable=True),
    )


def downgrade() -> None:
    # Delete column
    op.drop_column("tasks", "priority")

    # Delete enum if not used elsewhere
    sa.Enum(name="task_priority").drop(op.get_bind(), checkfirst=True)
```

### 3. Changing enum values

PostgreSQL does not support removing values from enum. Need to recreate the type.

```python
old_status = sa.Enum("pending", "active", name="user_status")
new_status = sa.Enum("pending", "active", "suspended", name="user_status")


def upgrade() -> None:
    # Adding new value (PostgreSQL 9.1+)
    op.execute("ALTER TYPE user_status ADD VALUE IF NOT EXISTS 'suspended'")


def downgrade() -> None:
    # Removing value requires recreating the type
    # 1. Create temporary type
    op.execute("CREATE TYPE user_status_old AS ENUM ('pending', 'active')")

    # 2. Update data
    op.execute("""
        UPDATE users
        SET status = 'active'
        WHERE status = 'suspended'
    """)

    # 3. Change column type
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN status TYPE user_status_old
        USING status::text::user_status_old
    """)

    # 4. Delete old type
    op.execute("DROP TYPE user_status")

    # 5. Rename
    op.execute("ALTER TYPE user_status_old RENAME TO user_status")
```

### 4. Enum used in multiple tables

```python
# Create enum with separate migration
def upgrade() -> None:
    status_type = sa.Enum("active", "inactive", name="common_status")
    status_type.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Check if used somewhere
    # If yes — do not delete
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT COUNT(*)
        FROM pg_type t
        JOIN pg_depend d ON t.oid = d.objid
        WHERE t.typname = 'common_status'
    """))

    if result.scalar() == 0:
        sa.Enum(name="common_status").drop(op.get_bind(), checkfirst=True)
```

### 5. Rename enum

```python
def upgrade() -> None:
    op.execute("ALTER TYPE old_name RENAME TO new_name")


def downgrade() -> None:
    op.execute("ALTER TYPE new_name RENAME TO old_name")
```

## Checking existing enums

```sql
-- List all enum types
SELECT typname, enumlabel
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
ORDER BY typname, enumsortorder;

-- Enum usage in tables
SELECT
    c.table_name,
    c.column_name,
    c.udt_name as enum_type
FROM information_schema.columns c
WHERE c.udt_name IN (
    SELECT typname FROM pg_type WHERE typtype = 'e'
);
```

## Common errors

### DuplicateObject: type already exists

```python
# Bad — enum already exists
op.execute("CREATE TYPE status AS ENUM ('a', 'b')")

# Good — check existence
status_type = sa.Enum("a", "b", name="status")
status_type.create(op.get_bind(), checkfirst=True)
```

### DependentObjectsStillExist

```python
# Bad — column still uses enum
sa.Enum(name="status").drop(op.get_bind())

# Good — first delete column
op.drop_column("users", "status")
sa.Enum(name="status").drop(op.get_bind(), checkfirst=True)
```

## SQLAlchemy model with Enum

```python
from enum import Enum as PyEnum
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column


class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
    )
```
