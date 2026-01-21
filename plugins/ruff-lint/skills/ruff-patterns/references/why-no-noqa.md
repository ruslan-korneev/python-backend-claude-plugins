# Why NEVER Use noqa

## Principle

**Every linter error has a proper solution.** Using `# noqa` is not a solution, it's ignoring the problem.

## Problems with noqa

### 1. Hiding Real Problems

```python
# Bad — hiding the problem
result = some_very_long_function_call(arg1, arg2, arg3, arg4)  # noqa: E501

# What's hidden:
# - Code is hard to read
# - Code review is difficult
# - Git blame shows a long line
```

### 2. Technical Debt

```python
# Starts with one noqa
from module import unused_function  # noqa: F401

# A month later
from module import unused_function  # noqa: F401
from another import also_unused  # noqa: F401
MAGIC_NUMBER = 42  # noqa: PLR2004
result = risky_code()  # noqa: S101, B008

# noqa multiplies like a virus
```

### 3. Masking Bugs

```python
# noqa can hide a real bug
def process(data = []):  # noqa: B006
    data.append(item)    # Bug! Shared mutable state
    return data
```

### 4. Degrading Code Quality

A team accustomed to noqa stops thinking about quality:
- "Just add noqa and push"
- "Linter is getting in the way, let's ignore it"
- Code review passes noqa without questions

## Proper Alternatives

### Instead of noqa on a specific line

| Situation | Bad | Good |
|-----------|-----|------|
| Long line | `# noqa: E501` | Split into multiple lines |
| Unused import | `# noqa: F401` | Remove or add to `__all__` |
| Mutable default | `# noqa: B006` | `None` + check |
| Assert | `# noqa: S101` | `if not x: raise` |

### For file groups — per-file-ignores

If a rule doesn't fit certain files:

```toml
[tool.ruff.lint.per-file-ignores]
# Tests — assert is normal
"tests/**/*.py" = ["S101", "PLR2004"]

# Migrations — auto-generated code
"alembic/versions/*.py" = ["ALL"]

# __init__.py — re-export
"__init__.py" = ["F401"]

# FastAPI routers — Depends in defaults
"src/*/routers.py" = ["B008"]
```

### For the whole project — global ignore

If a rule doesn't fit the project philosophy:

```toml
[tool.ruff.lint]
ignore = [
    "D",       # docstrings — code should be self-documenting
    "ANN101",  # self annotation — redundant
    "ANN102",  # cls annotation — redundant
]
```

## When noqa SEEMS Like the Only Way Out

### "The linter doesn't understand my code"

```python
# Seems like noqa is needed
value: Any = get_dynamic_value()
result = value.method()  # type checker complains

# Proper solution — explicit typing
if isinstance(value, ExpectedType):
    result = value.method()
else:
    raise TypeError(f"Expected ExpectedType, got {type(value)}")
```

### "It's legacy code"

```python
# Bad — ignoring legacy
import old_module  # noqa: F401 (legacy)

# Good — refactoring or migration
# 1. Create a task for refactoring
# 2. Use per-file-ignores temporarily
# 3. Remove after refactoring
```

### "An external library requires it"

```python
# Seems like noqa is needed
callback(lambda x: x * 2)  # noqa: E731

# Proper solution
def double(x):
    return x * 2

callback(double)
```

## Exception: TYPE_CHECKING

The only "acceptable" case is `if TYPE_CHECKING` blocks, but even there it's better to use `__all__` or explicit re-export:

```python
# Acceptable, but better to avoid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User  # used only for types

# Better
from .models import User as User  # explicit re-export
```

## Conclusion

noqa is:
- An admission of defeat
- Technical debt
- A potential source of bugs

The proper solution always exists. If you can't find it — ask, use `/lint:explain`.
