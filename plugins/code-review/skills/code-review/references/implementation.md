# Implementation Semantics Checklist

The logic layer — does the code actually work correctly?

## Core Areas

### 1. Correctness

#### Does it implement the requirements?

- All requirements covered?
- Business logic matches specifications?
- Edge cases from requirements handled?

```python
# Requirement: "Users can update profile, but not their own role"

# ❌ Requirement not fully implemented
async def update_profile(user_id: int, data: ProfileUpdate):
    return await repo.update(user_id, data)  # No role check!

# ✅ Complete implementation
async def update_profile(
    user_id: int,
    data: ProfileUpdate,
    current_user: User,
):
    if data.role is not None and user_id == current_user.id:
        raise ForbiddenError("Cannot change own role")
    return await repo.update(user_id, data)
```

#### Logical errors

- Off-by-one errors?
- Boundary conditions?
- Null/empty handling?

```python
# ❌ Off-by-one
def get_last_n_items(items, n):
    return items[len(items) - n:]  # Fails when n > len

# ✅ Safe
def get_last_n_items(items, n):
    return items[-n:] if n > 0 else []
```

### 2. Error Handling

#### All error paths covered?

```python
# ❌ Happy path only
async def transfer_money(from_id, to_id, amount):
    from_account = await get_account(from_id)
    to_account = await get_account(to_id)
    from_account.balance -= amount
    to_account.balance += amount

# ✅ Error handling
async def transfer_money(from_id, to_id, amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")

    from_account = await get_account(from_id)
    if not from_account:
        raise NotFoundError(f"Account {from_id} not found")

    if from_account.balance < amount:
        raise InsufficientFundsError()

    to_account = await get_account(to_id)
    if not to_account:
        raise NotFoundError(f"Account {to_id} not found")

    # Transaction logic...
```

#### Exceptions properly propagated?

```python
# ❌ Swallowing exceptions
try:
    result = risky_operation()
except Exception:
    pass  # Silent failure!

# ✅ Proper handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed", exc_info=True)
    raise OperationFailedError() from e
```

### 3. Concurrency

#### Race conditions?

```python
# ❌ Race condition
async def increment_counter(id):
    counter = await get_counter(id)
    counter.value += 1
    await save_counter(counter)

# ✅ Atomic operation
async def increment_counter(id):
    await db.execute(
        update(Counter)
        .where(Counter.id == id)
        .values(value=Counter.value + 1)
    )
```

#### Deadlocks?

```python
# ❌ Potential deadlock
async def transfer(from_id, to_id, amount):
    async with lock(from_id):  # Lock A
        async with lock(to_id):  # Lock B (what if another transfer locks B then A?)
            ...

# ✅ Ordered locking
async def transfer(from_id, to_id, amount):
    first, second = sorted([from_id, to_id])
    async with lock(first):
        async with lock(second):
            ...
```

### 4. Performance

#### N+1 Queries

```python
# ❌ N+1 problem
async def get_users_with_orders():
    users = await session.execute(select(User))
    for user in users:
        orders = await session.execute(
            select(Order).where(Order.user_id == user.id)
        )  # Query per user!

# ✅ Eager loading
async def get_users_with_orders():
    users = await session.execute(
        select(User).options(selectinload(User.orders))
    )
```

#### Unbounded operations

```python
# ❌ No limit
async def get_all_users():
    return await session.execute(select(User))  # Could be millions!

# ✅ Paginated
async def get_users(page: int, size: int = 20):
    return await session.execute(
        select(User).offset(page * size).limit(size)
    )
```

#### Blocking in async

```python
# ❌ Blocking call in async
async def process_file(path):
    content = open(path).read()  # Blocks event loop!

# ✅ Async I/O
async def process_file(path):
    async with aiofiles.open(path) as f:
        content = await f.read()
```

### 5. Resource Management

#### Resources cleaned up?

```python
# ❌ Resource leak
def read_file(path):
    f = open(path)
    return f.read()  # File never closed!

# ✅ Context manager
def read_file(path):
    with open(path) as f:
        return f.read()
```

#### Connection pools respected?

```python
# ❌ Connection leak
async def long_operation():
    async with get_session() as session:
        # Long-running operation holds connection
        await slow_external_api()
        return await session.execute(query)

# ✅ Release connection early
async def long_operation():
    async with get_session() as session:
        data = await session.execute(query)

    # Process outside session
    await slow_external_api()
    return data
```

## Review Questions

### Correctness

- [ ] Does it implement all requirements?
- [ ] Are edge cases handled?
- [ ] Boundary conditions correct?

### Error Handling

- [ ] All error paths have handling?
- [ ] Errors informative for debugging?
- [ ] No silent failures?

### Concurrency

- [ ] Race conditions possible?
- [ ] Shared mutable state protected?
- [ ] Deadlock potential?

### Performance

- [ ] N+1 queries present?
- [ ] Unbounded loops/queries?
- [ ] Blocking calls in async code?

### Resources

- [ ] All resources cleaned up?
- [ ] Connections properly pooled?
- [ ] Memory usage bounded?

## Python/FastAPI Specific

### Pydantic Validators

```python
# ❌ Side effects in validator
@field_validator('email')
def validate_email(cls, v):
    send_email(v, "Welcome!")  # Side effect!
    return v

# ✅ Pure validation
@field_validator('email')
def validate_email(cls, v):
    if not is_valid_email(v):
        raise ValueError("Invalid email format")
    return v.lower()
```

### Dependency Injection

```python
# ❌ Hidden dependency
async def get_user(user_id: int):
    session = get_global_session()  # Where does this come from?
    return await session.get(User, user_id)

# ✅ Explicit dependency
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await session.get(User, user_id)
```

### SQLAlchemy 2.0

```python
# ❌ Legacy style
users = session.query(User).filter_by(active=True).all()

# ✅ SQLAlchemy 2.0 style
stmt = select(User).where(User.active == True)
result = await session.execute(stmt)
users = result.scalars().all()
```
