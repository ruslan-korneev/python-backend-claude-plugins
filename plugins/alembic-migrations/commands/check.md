---
name: check
description: Check migration for common problems
allowed_tools:
  - Bash
  - Read
  - Glob
  - Grep
arguments:
  - name: revision
    description: "Revision to check (default: head)"
    required: false
---

# Command /migrate:check

Check migration for common problems before applying.

## What we check

1. **Enum types** — is there drop in downgrade
2. **Nullable changes** — is there data migration
3. **Index/Constraint names** — are names unique
4. **Foreign keys** — correct order of operations
5. **Data loss** — potential data loss

## Instructions

### Step 1: Find migration file

```bash
# Latest migration
alembic heads

# Specific revision
alembic show {{ revision }}
```

### Step 2: Read migration

```bash
# Get file path
alembic show {{ revision }} | grep "Path"
```

### Step 3: Check for problems

#### Enum without drop in downgrade

```python
# Look for enum in upgrade
sa.Enum("value1", "value2", name="enum_name")

# Check downgrade
# Should be:
# sa.Enum(name="enum_name").drop(op.get_bind(), checkfirst=False)
```

#### Nullable False without data migration

```python
# Dangerous:
op.alter_column("users", "name", nullable=False)

# Safe:
op.execute("UPDATE users SET name = 'default' WHERE name IS NULL")
op.alter_column("users", "name", nullable=False)
```

#### Drop column without backup

```python
# Dangerous — data loss:
op.drop_column("users", "important_data")

# Recommendation: first deprecate, then delete
```

#### Foreign key order

```python
# Correct — first FK, then table:
def downgrade():
    op.drop_constraint("fk_orders_user_id", "orders")
    op.drop_table("users")

# Incorrect — FK constraint error:
def downgrade():
    op.drop_table("users")  # FK still exists!
```

### Step 4: Test upgrade/downgrade

```bash
# Full cycle
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## Checklist

- [ ] All enum types are deleted in downgrade
- [ ] Nullable changes have data migration
- [ ] No hardcoded constraint names (use naming convention)
- [ ] FK are deleted before tables in downgrade
- [ ] Drop column — conscious decision
- [ ] Test upgrade/downgrade passes

## Response format

```
## Migration check: {{ revision }}

### Status: OK / Needs attention / Problems

### Found problems

#### Enum without drop in downgrade
- `status_type` is created, but not deleted
- **Fix:** add to downgrade:
  ```python
  sa.Enum(name="status_type").drop(op.get_bind(), checkfirst=False)
  ```

#### Nullable change without data migration
- `users.name` changes to NOT NULL
- **Recommendation:** add:
  ```python
  op.execute("UPDATE users SET name = 'Unknown' WHERE name IS NULL")
  ```

### Recommendations
1. ...
2. ...

### Test
```bash
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```
```
