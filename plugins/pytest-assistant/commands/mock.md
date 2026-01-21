---
name: pytest:mock
description: Create a mock for an external dependency
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: dependency
    description: What to mock (class, function, module)
    required: true
  - name: behavior
    description: Expected mock behavior
    required: false
---

# Command /test:mock

Create a mock for an external dependency in tests.

## When to Use Mocks

- **External services** — email, SMS, payment gateways
- **Network requests** — HTTP clients, API calls
- **File system** — file read/write operations
- **Time** — datetime.now(), time.sleep()
- **Random values** — random, uuid

## Do NOT Mock

- **Code under test** — pointless
- **Simple functions** — if you can use real ones
- **Database** — better to use a test database with rollback

## Instructions

### Step 1: Identify what to mock

Find the dependency in code:
```python
# src/modules/users/services.py
class UserService:
    def __init__(self, email_service: EmailService) -> None:
        self._email = email_service

    async def register(self, data: UserCreate) -> User:
        user = await self._repo.create(data)
        await self._email.send_welcome(user.email)  # ← this needs to be mocked
        return user
```

### Step 2: Create the mock

## Mock Examples

### AsyncMock for async dependencies

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


# Usage
async def test_register_sends_welcome_email(
    mock_email_service: AsyncMock,
) -> None:
    service = UserService(email_service=mock_email_service)

    await service.register({"email": "test@example.com"})

    mock_email_service.send_welcome.assert_called_once_with("test@example.com")
```

### MagicMock for sync dependencies

```python
from unittest.mock import MagicMock


@pytest.fixture
def mock_cache() -> MagicMock:
    """Mock cache."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock
```

### patch for module-level replacement

```python
from unittest.mock import patch, AsyncMock


async def test_external_api_call():
    with patch(
        "src.modules.orders.services.httpx.AsyncClient.post",
        new_callable=AsyncMock,
    ) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}

        result = await order_service.create_payment(order_id=1)

        assert result["success"] is True
        mock_post.assert_called_once()
```

### patch as decorator

```python
@patch("src.modules.users.services.datetime")
async def test_user_created_at(mock_datetime: MagicMock) -> None:
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    user = await service.create(data)

    assert user.created_at == datetime(2024, 1, 1, 12, 0, 0)
```

### pytest-mock (cleaner syntax)

```python
async def test_with_mocker(mocker) -> None:
    mock_send = mocker.patch(
        "src.modules.notifications.services.send_push",
        new_callable=AsyncMock,
    )
    mock_send.return_value = True

    await notification_service.notify_user(user_id=1)

    mock_send.assert_called_once()
```

### Mock with side_effect

```python
@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mock repository with different behaviors."""
    mock = AsyncMock()

    # Different responses for different calls
    mock.get_by_id.side_effect = [
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
        None,  # third call returns None
    ]

    return mock


@pytest.fixture
def mock_failing_service() -> AsyncMock:
    """Mock that raises an exception."""
    mock = AsyncMock()
    mock.process.side_effect = ConnectionError("Service unavailable")
    return mock
```

### Mock HTTP client (httpx)

```python
import pytest
from unittest.mock import AsyncMock
import httpx


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Mock httpx.AsyncClient."""
    mock = AsyncMock(spec=httpx.AsyncClient)

    # Configure response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "value"}
    mock_response.raise_for_status = MagicMock()

    mock.get.return_value = mock_response
    mock.post.return_value = mock_response

    return mock
```

### Mock datetime (freezegun alternative)

```python
from unittest.mock import patch
from datetime import datetime


@pytest.fixture
def frozen_time():
    """Frozen time."""
    frozen = datetime(2024, 6, 15, 12, 0, 0)
    with patch("src.modules.orders.services.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield frozen
```

### Mock file system

```python
from unittest.mock import mock_open, patch


def test_read_config():
    config_content = '{"key": "value"}'

    with patch("builtins.open", mock_open(read_data=config_content)):
        result = load_config("config.json")

    assert result == {"key": "value"}
```

## Mock Assertions

```python
# Was called
mock.method.assert_called()

# Was called exactly once
mock.method.assert_called_once()

# Was called with arguments
mock.method.assert_called_with(arg1, arg2, key=value)

# Was called once with arguments
mock.method.assert_called_once_with(arg1, arg2)

# Call count
assert mock.method.call_count == 3

# Check all calls
from unittest.mock import call
mock.method.assert_has_calls([
    call(1),
    call(2),
    call(3),
])

# Was not called
mock.method.assert_not_called()
```

## Response Format

```
## Mock Created: {{ dependency }}

### Fixture
```python
[fixture code]
```

### Usage in Test
```python
[usage example]
```

### Assertions
- `mock.method.assert_called_once()` — verify call
- `mock.method.assert_called_with(...)` — verify arguments
```
