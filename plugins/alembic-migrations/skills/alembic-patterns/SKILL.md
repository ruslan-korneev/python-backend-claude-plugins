# Alembic Patterns

Alembic migration patterns with automatic handling of problematic types.

## Triggers

Use this skill when the user:
- Creates an Alembic migration
- Gets errors during migration
- Works with enum, array, nullable changes

## Main principle: Automatic fixing

Alembic does not always correctly generate downgrade. The plugin automatically:
- Adds enum deletion in downgrade
- Warns about nullable changes without data migration
- Checks the order of FK operations

## Enum types

More details: `${CLAUDE_PLUGIN_ROOT}/skills/alembic-patterns/references/enum-handling.md`

### Creating table with enum

```python
status_type = sa.Enum("pending", "active", "inactive", name="status_type")

def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", status_type, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade() -> None:
    op.drop_table("orders")
    status_type.drop(op.get_bind(), checkfirst=False)  # IMPORTANT!
```

### Adding column with enum

```python
def upgrade() -> None:
    status_type = sa.Enum("pending", "active", name="status_type")
    status_type.create(op.get_bind(), checkfirst=True)
    op.add_column("orders", sa.Column("status", status_type))

def downgrade() -> None:
    op.drop_column("orders", "status")
    # Delete only if enum is not used elsewhere
    # sa.Enum(name="status_type").drop(op.get_bind(), checkfirst=True)
```

## Nullable changes

```python
# Changing NULL -> NOT NULL
def upgrade() -> None:
    # First update data
    op.execute("UPDATE users SET name = 'Unknown' WHERE name IS NULL")
    # Then change constraint
    op.alter_column("users", "name", nullable=False)

def downgrade() -> None:
    op.alter_column("users", "name", nullable=True)
```

## Foreign Keys

```python
# Correct order in downgrade
def downgrade() -> None:
    # First delete FK
    op.drop_constraint("fk_orders_user_id", "orders", type_="foreignkey")
    # Then table
    op.drop_table("users")
```

## Array types

```python
# Changing array element type
def upgrade() -> None:
    op.drop_column("users", "tags")
    op.add_column("users", sa.Column("tags", sa.ARRAY(sa.String(100))))

def downgrade() -> None:
    op.drop_column("users", "tags")
    op.add_column("users", sa.Column("tags", sa.ARRAY(sa.String(50))))
```

## Data migrations

```python
def upgrade() -> None:
    # Safe batch update for large tables
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE users
            SET status = 'active'
            WHERE status IS NULL
        """)
    )
```

## Commands

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current version
alembic current

# History
alembic history
```

## Plugin commands

- `/migrate:create <message>` — create migration with auto-fix
- `/migrate:check [revision]` — check migration for problems
- Agent `migration-reviewer` — full migration analysis
