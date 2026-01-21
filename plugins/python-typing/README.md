# python-typing

Plugin for Python type annotations. **ZERO type: ignore policy** — always the correct solution.

## Philosophy

Every type error indicates a potential problem. `type: ignore` doesn't solve the problem — it hides it.

## Features

- **Automatic checking** — hook runs mypy after editing Python files
- **Project checking** — `/types:check` command for full validation
- **Error explanations** — `/types:explain` command shows the correct solution

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install python-typing@python-backend-plugins
```

## Commands

### `/types:check [path]`

Checks types in the specified path.

```
/types:check
/types:check src/modules/users/
/types:check src/services/user.py
```

### `/types:explain <error>`

Explains the error and shows the correct solution (not type: ignore).

```
/types:explain "Incompatible types in assignment"
/types:explain src/main.py:45
```

## Automatic Hook

After each `Edit` or `Write` of a Python file, `mypy` runs to check types.

## Common Errors and Solutions

### Item "None" has no attribute

```python
# Bad
user = get_user(id)  # Returns User | None
print(user.name)  # type: ignore

# Good
user = get_user(id)
if user is None:
    raise NotFoundError("User not found")
print(user.name)
```

### Missing return type annotation

```python
# Bad
def process(x):  # type: ignore
    return x * 2

# Good
def process(x: int) -> int:
    return x * 2
```

### Incompatible types in assignment

```python
# Bad
x: str = 123  # type: ignore

# Good
x: int = 123
# or
x: str = str(123)
```

## mypy Configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_untyped_calls = true
```

## Plugin Structure

```
python-typing/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── check.md
│   └── explain.md
├── hooks/
│   └── hooks.json
├── skills/
│   └── typing-patterns/
│       ├── SKILL.md
│       └── references/
│           ├── generics.md
│           └── why-no-type-ignore.md
└── README.md
```

## References

- [mypy documentation](https://mypy.readthedocs.io/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [pyright](https://github.com/microsoft/pyright)
