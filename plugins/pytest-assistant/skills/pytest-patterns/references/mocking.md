# Mocking in pytest

## Main Principle: Mocks Only for EXTERNAL Services

**Database — NEVER mock.** Use a real test database.

## When to Mock

### ✅ Should Mock

- **External APIs** — HTTP requests to third-party services (Stripe, SendGrid, Twilio)
- **Email/SMS services** — don't send real messages
- **Payment systems** — don't make real transactions
- **File system** — for test isolation (optional)
- **Time** — `datetime.now()`, `time.sleep()`
- **Random values** — `random`, `uuid4`

### ❌ NEVER Mock

- **Database** — use test DB with transaction rollback!
- **Repositories** — they work with real DB
- **Internal services** — test real logic
- **Code under test** — pointless
- **Pydantic models** — they work fast

### Why Not Mock Database

```python
# ❌ BAD — mock database
@pytest.fixture
def mock_user_repository():
    mock = AsyncMock()
    mock.get_by_email.return_value = User(id=1, email="test@example.com")
    return mock

# Problems:
# - Doesn't test real SQL
# - Doesn't find migration issues
# - Doesn't check constraints
# - False confidence in functionality

# ✅ GOOD — real test database
@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn) as session:
            yield session
        await conn.rollback()  # Isolation via transactions

@pytest.fixture
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)  # Real repository with real DB
```

## AsyncMock vs MagicMock

```python
from unittest.mock import AsyncMock, MagicMock

# AsyncMock — for async functions
async_service = AsyncMock()
await async_service.process()  # Works

# MagicMock — for sync functions
sync_service = MagicMock()
sync_service.process()  # Works

# ERROR: MagicMock for async
mock = MagicMock()
await mock.process()  # TypeError: object MagicMock can't be used in 'await'
```

## Mocking Patterns

### 1. Mock via fixture

```python
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_email_service() -> AsyncMock:
    """Mock email service."""
    mock = AsyncMock()
    mock.send_welcome.return_value = True
    mock.send_reset_password.return_value = True
    return mock


async def test_registration_sends_email(
    mock_email_service: AsyncMock,
) -> None:
    service = UserService(email=mock_email_service)

    await service.register({"email": "test@example.com"})

    mock_email_service.send_welcome.assert_called_once_with("test@example.com")
```

### 2. Mock via patch

```python
from unittest.mock import patch, AsyncMock


async def test_external_api_call() -> None:
    with patch(
        "src.modules.payments.client.httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        result = await payment_service.process(order_id=1)

        assert result.success is True
        mock_post.assert_called_once()
```

### 3. Patch as decorator

```python
from unittest.mock import patch, MagicMock


@patch("src.modules.users.services.datetime")
async def test_created_at_timestamp(mock_datetime: MagicMock) -> None:
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    user = await service.create(data)

    assert user.created_at == datetime(2024, 1, 1, 12, 0, 0)
```

### 4. pytest-mock

```python
async def test_with_mocker(mocker) -> None:
    mock_send = mocker.patch(
        "src.modules.notifications.client.send_push",
        new_callable=AsyncMock,
    )
    mock_send.return_value = True

    await notification_service.notify(user_id=1)

    mock_send.assert_called_once()
```

## Configuring Mock Behavior

### return_value

```python
mock = AsyncMock()

# Simple value
mock.get.return_value = {"id": 1, "name": "Test"}

# For nested calls
mock.client.get.return_value = response
```

### side_effect — different values

```python
mock = AsyncMock()

# Sequence of values
mock.get.side_effect = [
    {"id": 1},
    {"id": 2},
    None,
]

# First call → {"id": 1}
# Second call → {"id": 2}
# Third call → None
```

### side_effect — exception

```python
mock = AsyncMock()

# Always raises exception
mock.process.side_effect = ConnectionError("Service unavailable")

# Exception on specific call
mock.get.side_effect = [
    {"id": 1},
    NotFoundException("Not found"),
    {"id": 3},
]
```

### side_effect — function

```python
mock = AsyncMock()

async def dynamic_response(user_id: int):
    if user_id == 1:
        return {"id": 1, "name": "Admin"}
    return None

mock.get.side_effect = dynamic_response
```

## Assertions

### Was it called

```python
# Was called (at least once)
mock.method.assert_called()

# Was called exactly once
mock.method.assert_called_once()

# Was not called
mock.method.assert_not_called()

# Call count
assert mock.method.call_count == 3
```

### With what arguments

```python
# Last call with arguments
mock.method.assert_called_with(arg1, arg2, key=value)

# Single call with arguments
mock.method.assert_called_once_with(arg1, arg2)

# Any call contained arguments
from unittest.mock import call
mock.method.assert_any_call(arg1, arg2)

# Check all calls
mock.method.assert_has_calls([
    call(1),
    call(2),
    call(3),
], any_order=False)
```

### Manual argument checking

```python
# Get arguments of last call
args, kwargs = mock.method.call_args

# Get all calls
all_calls = mock.method.call_args_list
for call_args in all_calls:
    args, kwargs = call_args
    print(f"Called with: {args}, {kwargs}")
```

## Mocking HTTP Clients

### httpx.AsyncClient

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Mock httpx.AsyncClient."""
    client = AsyncMock(spec=httpx.AsyncClient)

    # Configure response
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": "value"}
    response.text = '{"data": "value"}'
    response.raise_for_status = MagicMock()

    client.get.return_value = response
    client.post.return_value = response

    # Context manager
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None

    return client
```

### requests (synchronous)

```python
@pytest.fixture
def mock_requests(mocker):
    """Mock requests."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    mock_get = mocker.patch("requests.get", return_value=mock_response)
    mock_post = mocker.patch("requests.post", return_value=mock_response)

    return {"get": mock_get, "post": mock_post, "response": mock_response}
```

## Mocking Time

### datetime

```python
from unittest.mock import patch
from datetime import datetime


@pytest.fixture
def frozen_time():
    """Frozen time."""
    frozen = datetime(2024, 6, 15, 12, 0, 0)

    with patch("src.modules.orders.services.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        mock_dt.utcnow.return_value = frozen
        # Allow creating datetime objects
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield frozen


async def test_order_created_at(frozen_time):
    order = await service.create(data)
    assert order.created_at == frozen_time
```

### time.sleep (skip)

```python
from unittest.mock import patch


@patch("time.sleep", return_value=None)
async def test_retry_logic(mock_sleep):
    """Test retry without real waiting."""
    result = await service.retry_operation()

    assert result.success
    assert mock_sleep.call_count == 3  # 3 retries
```

## Mocking File System

```python
from unittest.mock import mock_open, patch


def test_read_config():
    config_content = '{"database": "test"}'

    with patch("builtins.open", mock_open(read_data=config_content)):
        config = load_config("config.json")

    assert config["database"] == "test"


def test_write_file():
    m = mock_open()

    with patch("builtins.open", m):
        write_file("output.txt", "content")

    m.assert_called_once_with("output.txt", "w")
    m().write.assert_called_once_with("content")
```

## Mocking random/uuid

```python
from unittest.mock import patch
import uuid


@patch("uuid.uuid4")
def test_generates_unique_id(mock_uuid):
    mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")

    result = service.create_with_uuid()

    assert result.id == "12345678-1234-5678-1234-567812345678"


@patch("random.randint")
def test_random_code(mock_randint):
    mock_randint.return_value = 123456

    code = service.generate_verification_code()

    assert code == "123456"
```

## Partial Mock (spec)

```python
from unittest.mock import AsyncMock, create_autospec
from src.modules.users.services import UserService


# Mock with signature checking
mock_service = create_autospec(UserService, instance=True)

# Calling non-existent method raises AttributeError
mock_service.nonexistent_method()  # AttributeError

# Calling with wrong arguments raises TypeError
mock_service.create("wrong", "args")  # TypeError
```
