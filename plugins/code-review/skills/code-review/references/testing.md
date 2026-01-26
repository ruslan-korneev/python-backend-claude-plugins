# Testing Checklist

Tests are medium priority in the pyramid, but essential for maintainability.

## Test Existence

### Basic Check
- New code has corresponding test file?
- Test file follows naming convention (`test_*.py`)?
- Tests are discoverable by pytest?

```bash
# Verify tests exist
pytest --collect-only path/to/tests/
```

### Coverage Expectations

| Code Type | Expected Coverage |
|-----------|-------------------|
| Business logic | 80%+ |
| API endpoints | 100% happy paths |
| Edge cases | All documented |
| Error paths | All expected errors |

## Test Quality

### Tests Verify Behavior, Not Implementation

```python
# ❌ Testing implementation
def test_user_service():
    service = UserService()
    # Checking internal calls
    service.repo.find_by_email = Mock()
    service.get_by_email("test@example.com")
    service.repo.find_by_email.assert_called_once()

# ✅ Testing behavior
def test_get_user_by_email_returns_user():
    service = UserService(repo=FakeUserRepo([test_user]))
    result = service.get_by_email("test@example.com")
    assert result.email == "test@example.com"
```

### Test Names Describe Scenarios

```python
# ❌ Vague names
def test_user():
def test_create():
def test_validation():

# ✅ Descriptive names
def test_create_user_with_valid_email_succeeds():
def test_create_user_with_duplicate_email_raises_conflict():
def test_create_user_without_email_raises_validation_error():
```

### AAA Pattern (Arrange-Act-Assert)

```python
# ✅ Clear structure
def test_transfer_money_updates_both_accounts():
    # Arrange
    from_account = Account(balance=100)
    to_account = Account(balance=50)

    # Act
    transfer(from_account, to_account, amount=30)

    # Assert
    assert from_account.balance == 70
    assert to_account.balance == 80
```

### One Assertion Per Concept

```python
# ❌ Too many unrelated assertions
def test_user_creation():
    user = create_user(name="John", email="john@test.com")
    assert user.name == "John"
    assert user.email == "john@test.com"
    assert user.created_at is not None
    assert user.id > 0
    assert send_email.called  # Unrelated!
    assert log.info.called    # Unrelated!

# ✅ Focused tests
def test_user_creation_sets_name_and_email():
    user = create_user(name="John", email="john@test.com")
    assert user.name == "John"
    assert user.email == "john@test.com"

def test_user_creation_sends_welcome_email():
    ...

def test_user_creation_is_logged():
    ...
```

## Edge Cases

### Requirements-Based Edge Cases

If task says: *"Users can't have negative balance"*

```python
def test_withdrawal_with_exact_balance_succeeds():
    account = Account(balance=100)
    withdraw(account, 100)
    assert account.balance == 0

def test_withdrawal_exceeding_balance_raises_error():
    account = Account(balance=100)
    with pytest.raises(InsufficientFundsError):
        withdraw(account, 101)
```

### Common Edge Cases

| Category | Cases to Test |
|----------|---------------|
| Strings | Empty, whitespace, special chars, unicode |
| Numbers | 0, negative, max int, floats |
| Collections | Empty, single item, many items |
| Dates | Past, future, timezone edge cases |
| Nullable | None handling |

```python
# Edge case examples
@pytest.mark.parametrize("email", [
    "",                    # Empty
    "   ",                 # Whitespace
    "no-at-sign",          # Invalid format
    "a@b.c",               # Minimal valid
    "a" * 255 + "@b.com",  # Very long
])
def test_email_validation(email):
    ...
```

## Test Types Balance

### Unit Tests
- Fast, isolated
- Mock external dependencies
- Test single units of logic

```python
def test_calculate_discount():
    assert calculate_discount(100, percent=10) == 90
```

### Integration Tests
- Test component interaction
- Use real database (test instance)
- Slower but more realistic

```python
async def test_create_user_persists_to_db(db_session):
    user = await UserService(db_session).create(name="John")

    # Verify actually in DB
    result = await db_session.get(User, user.id)
    assert result.name == "John"
```

### E2E/API Tests
- Test full request/response cycle
- Use test client
- Verify HTTP contracts

```python
async def test_create_user_endpoint(client: AsyncClient):
    response = await client.post("/users", json={"name": "John"})

    assert response.status_code == 201
    assert response.json()["name"] == "John"
```

### Recommended Balance

```
      Unit Tests
      ████████████████████████  60%

      Integration Tests
      ████████████████          30%

      E2E Tests
      ████████                  10%
```

## Anti-Patterns to Catch

### ❌ Testing Framework Instead of Code
```python
def test_mock_works():
    mock = Mock(return_value=42)
    assert mock() == 42  # Tests Mock, not your code!
```

### ❌ Tautological Tests
```python
def test_get_user_returns_user():
    mock_repo.get.return_value = user
    result = service.get_user(1)
    assert result == user  # Of course it equals what you set up!
```

### ❌ Flaky Tests
```python
def test_timing_sensitive():
    start = time.time()
    operation()
    assert time.time() - start < 0.1  # Flaky on slow CI!
```

### ❌ Order-Dependent Tests
```python
def test_1_create():
    global user_id
    user_id = create_user()

def test_2_get():
    get_user(user_id)  # Fails if test_1 didn't run first!
```

## Review Questions

### Existence
- [ ] New functionality has tests?
- [ ] Tests discoverable by pytest?
- [ ] Test file naming follows convention?

### Quality
- [ ] Tests verify behavior, not implementation?
- [ ] Test names describe scenarios?
- [ ] AAA pattern followed?
- [ ] One concept per test?

### Coverage
- [ ] Happy paths covered?
- [ ] Error paths covered?
- [ ] Edge cases from requirements?
- [ ] Common edge cases (empty, null, boundaries)?

### Balance
- [ ] Good unit/integration ratio?
- [ ] Not over-mocking?
- [ ] Database tests use real DB?

### Red Flags
- [ ] No tautological tests?
- [ ] No order-dependent tests?
- [ ] No flaky tests (timing, random)?
- [ ] No testing of mocks/frameworks?
