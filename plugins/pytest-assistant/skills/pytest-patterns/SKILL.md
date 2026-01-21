# Pytest Patterns

Quality testing patterns with pytest for FastAPI projects. **TDD-first approach**.

## Triggers

Use this skill when the user:
- Wants to write tests
- Asks about pytest, fixtures, mocks
- Wants to set up testing for FastAPI
- Uses TDD approach

## Main Principle: TDD

1. **Red** — write a failing test
2. **Green** — write minimal code
3. **Refactor** — improve while keeping tests green

## What Makes a Good Test

### 1. Clear Name

```python
# ✅ Good — describes what, when, and expectation
async def test_create_user_with_valid_data_returns_user_with_id():
async def test_create_user_with_duplicate_email_raises_conflict_error():
async def test_get_user_by_id_when_not_exists_raises_not_found():

# ❌ Bad
async def test_create_user():
async def test_user():
async def test_1():
```

### 2. Single Responsibility

```python
# ✅ Good — one test = one scenario
async def test_create_user_returns_user_with_id(service):
    result = await service.create(user_data)
    assert result.id is not None

async def test_create_user_saves_email(service):
    result = await service.create(user_data)
    assert result.email == user_data["email"]

# ❌ Bad — tests multiple things
async def test_create_user(service):
    result = await service.create(user_data)
    assert result.id is not None
    assert result.email == user_data["email"]
    assert result.created_at is not None
    assert await service.get(result.id) == result
```

### 3. Arrange-Act-Assert

```python
async def test_create_order_calculates_total(service):
    # Arrange — prepare data
    items = [
        {"product_id": 1, "quantity": 2, "price": 100},
        {"product_id": 2, "quantity": 1, "price": 50},
    ]

    # Act — execute action
    order = await service.create(items=items)

    # Assert — verify result
    assert order.total == 250
```

### 4. Isolation

Tests should not depend on each other:

```python
# ✅ Good — each test is independent
@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn) as session:
            yield session
        await conn.rollback()  # Rollback after each test

# ❌ Bad — shared state
_created_user = None

async def test_create_user(service):
    global _created_user
    _created_user = await service.create(data)

async def test_get_user(service):
    user = await service.get(_created_user.id)  # Depends on previous test!
```

## When to Use parametrize

```python
# ✅ Use parametrize for similar checks
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("user@subdomain.example.com", True),
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
])
def test_email_validation(email: str, is_valid: bool):
    assert validate_email(email) == is_valid

# ❌ Do NOT use parametrize for different scenarios
# Better to have separate tests with clear names
async def test_create_user_success(service):
    ...

async def test_create_user_duplicate_email(service):
    ...
```

## Async Testing

### pytest-asyncio Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

### Async Fixtures

```python
@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        yield client
```

## FastAPI Testing

More details: `${CLAUDE_PLUGIN_ROOT}/skills/pytest-patterns/references/fastapi-testing.md`

### Testing Endpoints

```python
from httpx import ASGITransport, AsyncClient

async def test_create_user_endpoint(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "Test"},
    )

    assert response.status_code == 201
    assert response.json()["id"] is not None
```

### Testing with DI Override

```python
@pytest.fixture
async def client(session: AsyncSession):
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        yield client
    app.dependency_overrides.clear()
```

## Fixtures for FastAPI

More details: `${CLAUDE_PLUGIN_ROOT}/skills/pytest-patterns/references/fixtures.md`

### Basic

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DATABASE_URL)

@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn)
        yield session
        await conn.rollback()

@pytest.fixture
async def client(session) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app)) as c:
        yield c
    app.dependency_overrides.clear()
```

## Test Database (IMPORTANT!)

**Use real database connection, not mocks.** Test database is created specifically for tests.

### Why Real DB, Not Mocks

- ✅ Test real SQL behavior
- ✅ Find migration issues
- ✅ Check constraints, indexes, triggers
- ✅ Confidence in production

```python
# ✅ Good — real test database
@pytest.fixture(scope="session")
def engine():
    return create_async_engine("postgresql+asyncpg://test:test@localhost:5432/test_db")

@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn) as session:
            yield session
        await conn.rollback()  # Isolation via transactions

# ❌ Bad — mock database
@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)  # Doesn't test real SQL!
```

### Parallel Tests (pytest-xdist)

Each worker gets its own DB: `gw{N}_test_{dbname}`

```python
def get_test_db_name(worker_id: str, base_name: str = "myapp") -> str:
    """gw0 → gw0_test_myapp, master → test_myapp"""
    if worker_id == "master":
        return f"test_{base_name}"
    return f"{worker_id}_test_{base_name}"

@pytest.fixture(scope="session")
def database_url(worker_id: str) -> str:
    db_name = get_test_db_name(worker_id)
    return f"postgresql+asyncpg://test:test@localhost:5432/{db_name}"
```

More details: `${CLAUDE_PLUGIN_ROOT}/skills/pytest-patterns/references/fixtures.md`

## Mocks — Only for External Services

More details: `${CLAUDE_PLUGIN_ROOT}/skills/pytest-patterns/references/mocking.md`

### When to Mock

- ✅ External APIs (email, SMS, payments, third-party)
- ✅ HTTP requests to external services
- ✅ File system (if not critical)
- ✅ Time (`datetime.now()`), random, uuid
- ❌ **Database** — use test database!
- ❌ Code under test
- ❌ Internal dependencies (repositories, services)

### AsyncMock for External Services

```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_email_service():
    """Mock EXTERNAL email service (SendGrid, AWS SES)."""
    mock = AsyncMock()
    mock.send.return_value = True
    return mock

@pytest.fixture
def mock_payment_gateway():
    """Mock EXTERNAL payment gateway."""
    mock = AsyncMock()
    mock.charge.return_value = {"status": "success", "transaction_id": "123"}
    return mock
```

## Coverage: Branch Coverage Matters More Than Line Coverage

**Branch coverage** — one of the most valuable metrics, not just line coverage.

### Why Branch Coverage

```python
def process(value: int | None) -> str:
    if value is not None:
        return f"Value: {value}"
    return "No value"

# Line coverage 100% with one test:
def test_process():
    assert process(42) == "Value: 42"
    # But branch `return "No value"` is NOT tested!

# Branch coverage requires both paths:
def test_process_with_value():
    assert process(42) == "Value: 42"

def test_process_with_none():
    assert process(None) == "No value"
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true  # IMPORTANT: enable branch coverage

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### Running with Branch Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-branch --cov-report=term-missing

# HTML report for detailed analysis
pytest --cov=src --cov-branch --cov-report=html
# Open htmlcov/index.html — shows uncovered branches
```

## Plugin Commands

- `/test:first <feature>` — create test BEFORE implementation (TDD)
- `/test:fixture <name>` — create a fixture
- `/test:mock <dependency>` — create a mock
- Agent `test-reviewer` — coverage and quality analysis
