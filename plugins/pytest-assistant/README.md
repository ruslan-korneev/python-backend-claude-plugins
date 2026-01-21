# pytest-assistant

Plugin for TDD-first testing with pytest. Test first, then implementation.

## Philosophy

**TDD — Test-Driven Development**:
1. **Red** — write a failing test
2. **Green** — write minimal code to pass
3. **Refactor** — improve code while keeping tests green

## Features

- **TDD workflow** — `/test:first` command for creating tests BEFORE implementation
- **Fixtures** — `/test:fixture` command for creating pytest fixtures
- **Mocks** — `/test:mock` command for mocking dependencies
- **Code review** — `test-reviewer` agent for analyzing test quality

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install pytest-assistant@python-backend-plugins
```

## Commands

### `/test:first <feature>`

Creates a test **BEFORE** writing implementation (TDD red phase).

```
/test:first user creation with email validation
/test:first payment error handling
```

### `/test:fixture <name> [type]`

Creates a pytest fixture.

```
/test:fixture session db
/test:fixture client http
/test:fixture sample_user sample
/test:fixture mock_email mock
```

Types:
- `session` — AsyncSession for database
- `client` — AsyncClient for API
- `db` — full test database setup
- `mock` — dependency mock
- `sample` — test data

### `/test:mock <dependency>`

Creates a mock for an external dependency.

```
/test:mock EmailService
/test:mock httpx.AsyncClient
/test:mock PaymentGateway
```

## Agent test-reviewer

Analyzes test quality:
- Code coverage
- Test case quality (naming, isolation, AAA)
- Missing scenarios
- Improvement recommendations

## Plugin Structure

```
pytest-assistant/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── first.md      # /test:first
│   ├── fixture.md    # /test:fixture
│   └── mock.md       # /test:mock
├── agents/
│   └── test-reviewer.md
├── skills/
│   └── pytest-patterns/
│       ├── SKILL.md
│       ├── references/
│       │   ├── fastapi-testing.md
│       │   ├── fixtures.md
│       │   └── mocking.md
│       └── examples/
│           └── conftest.py
└── README.md
```

## What Makes a Good Test

### Clear Name
```python
# ✅ Good
async def test_create_user_with_duplicate_email_raises_conflict():

# ❌ Bad
async def test_create_user():
```

### Single Responsibility
```python
# ✅ One test = one scenario
async def test_order_total_calculated_correctly():
    ...

# ❌ Multiple assertions
async def test_order():
    assert order.total == 100
    assert order.status == "pending"
    assert order.items_count == 3
```

### Arrange-Act-Assert
```python
async def test_create_order():
    # Arrange
    items = [{"product_id": 1, "quantity": 2}]

    # Act
    order = await service.create(items)

    # Assert
    assert order.id is not None
```

## Recommended Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
│   └── modules/
│       └── users/
│           ├── conftest.py
│           ├── test_services.py
│           └── test_repositories.py
├── integration/         # Integration tests
│   └── test_api.py
└── e2e/                 # End-to-end tests
    └── test_user_flow.py
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx testing](https://www.python-httpx.org/advanced/#testing)
