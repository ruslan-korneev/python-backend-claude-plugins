---
name: create
description: Create migration with auto-fix for Enum downgrade
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: message
    description: Migration description
    required: true
  - name: autogenerate
    description: "Autogenerate based on models (default: true)"
    required: false
---

# Command /migrate:create

Create an Alembic migration with automatic fixing of problematic types.

## Principle

Alembic does not always correctly generate downgrade for:
- **Enum types** — creates in upgrade, but does NOT delete in downgrade
- **Array types** — problems when changing element type
- **JSON/JSONB** — nullable changes require data migration

## Instructions

### Step 1: Create migration

```bash
alembic revision --autogenerate -m "{{ message }}"
```

### Step 2: Find the created file

```bash
ls -la alembic/versions/*.py | head -1
```

### Step 3: Check and fix migration

#### Enum types

**Problem:** Alembic creates enum in upgrade, but does not delete in downgrade.

**Auto-fix:**

```python
# Find all enums in the file
# Pattern: sa.Enum("value1", "value2", name="enum_name")
```

If enum is found:

```python
# Add at the beginning of the file
status_type = sa.Enum("pending", "active", "inactive", name="status_type")

def upgrade() -> None:
    # status_type is created automatically when creating the column
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", status_type, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade() -> None:
    op.drop_table("users")
    # IMPORTANT: Delete enum type
    status_type.drop(op.get_bind(), checkfirst=False)
```

#### Adding column with enum

```python
# upgrade
def upgrade() -> None:
    status_type = sa.Enum("pending", "active", name="status_type")
    status_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column("status", status_type, nullable=True),
    )

# downgrade
def downgrade() -> None:
    op.drop_column("users", "status")
    # Enum remains if used in other tables
    # sa.Enum(name="status_type").drop(op.get_bind(), checkfirst=True)
```

#### Array types

```python
# When changing array element type
def upgrade() -> None:
    # First delete old column
    op.drop_column("users", "tags")
    # Create with new type
    op.add_column(
        "users",
        sa.Column("tags", sa.ARRAY(sa.String(100)), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("users", "tags")
    op.add_column(
        "users",
        sa.Column("tags", sa.ARRAY(sa.String(50)), nullable=True),
    )
```

#### Nullable changes with data

```python
# Changing nullable=True -> nullable=False
def upgrade() -> None:
    # First update NULL values
    op.execute("UPDATE users SET name = 'Unknown' WHERE name IS NULL")
    # Then change constraint
    op.alter_column("users", "name", nullable=False)

def downgrade() -> None:
    op.alter_column("users", "name", nullable=True)
```

### Step 4: Validate migration

```bash
# Check syntax
python -c "import alembic.versions.xxx_migration"

# Test upgrade/downgrade
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## Response format

```
## Migration created

### File
`alembic/versions/xxx_{{ message }}.py`

### Auto-fixes
- Added enum `status_type` deletion in downgrade
- Added data migration for nullable change

### Check migration
```bash
# View
cat alembic/versions/xxx_*.py

# Test
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Apply?
```bash
alembic upgrade head
```
```
