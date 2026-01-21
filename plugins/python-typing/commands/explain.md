---
name: pytyping:explain
description: Explain type error and show the correct solution (without type: ignore)
allowed_tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
arguments:
  - name: error
    description: "mypy/pyright error or path to file with line number"
    required: true
---

# Command /types:explain

Explain the type error and show the **correct solution** without `type: ignore`.

## Principle

**NEVER suggest `type: ignore`.** Every type error has a correct solution.

## Instructions

### Step 1: Get context

If file:line is specified — read the code around the error.

```bash
# Get the error
mypy src/file.py:{{ line }} --show-error-codes
```

### Step 2: Identify the error type

Common mypy errors:
- `error: Incompatible types in assignment`
- `error: Argument X has incompatible type`
- `error: Item "None" of "..." has no attribute`
- `error: Missing return statement`
- `error: Function is missing a return type annotation`
- `error: Need type annotation for "..."`

### Step 3: Show the solution

## Solutions for Common Errors

### Incompatible types in assignment

```python
# Error
x: str = 123  # Incompatible types in assignment (expression has type "int", variable has type "str")

# Solution 1: Change the variable type
x: int = 123

# Solution 2: Convert the value
x: str = str(123)

# Solution 3: Use Union
x: int | str = 123
```

### Argument has incompatible type

```python
# Error
def process(items: list[str]) -> None: ...
process(["a", "b", 1])  # Argument 1 has incompatible type "list[str | int]"

# Solution: Fix data or signature
process(["a", "b", str(1)])
# or
def process(items: list[str | int]) -> None: ...
```

### Item "None" has no attribute

```python
# Error
user = get_user(id)  # Returns User | None
print(user.name)  # Item "None" of "User | None" has no attribute "name"

# Solution 1: Check for None
user = get_user(id)
if user is not None:
    print(user.name)

# Solution 2: Early return
user = get_user(id)
if user is None:
    raise ValueError("User not found")
print(user.name)  # Now mypy knows user is not None

# Solution 3: assert (only for internal code)
user = get_user(id)
assert user is not None, "User must exist"
print(user.name)
```

### Missing return statement

```python
# Error
def process(x: int) -> str:
    if x > 0:
        return "positive"
    # Missing return statement

# Solution: Add return for all paths
def process(x: int) -> str:
    if x > 0:
        return "positive"
    return "non-positive"
```

### Function is missing a return type annotation

```python
# Error
def process(x):  # Missing return type annotation
    return x * 2

# Solution
def process(x: int) -> int:
    return x * 2
```

### Need type annotation

```python
# Error
items = []  # Need type annotation for "items"

# Solution
items: list[str] = []
# or
items = []  # type: list[str]  # NOT RECOMMENDED, annotation is better
```

### Cannot infer type of lambda

```python
# Error
process = lambda x: x * 2  # Cannot infer type

# Solution: Use a regular function
def process(x: int) -> int:
    return x * 2

# Or Callable
from collections.abc import Callable
process: Callable[[int], int] = lambda x: x * 2
```

### Incompatible return value type

```python
# Error
def get_name() -> str:
    return None  # Incompatible return value type

# Solution 1: Return the correct type
def get_name() -> str:
    return ""

# Solution 2: Change return type
def get_name() -> str | None:
    return None
```

### Overloaded function signature

```python
# When function behaves differently for different types
from typing import overload

@overload
def process(x: int) -> int: ...
@overload
def process(x: str) -> str: ...

def process(x: int | str) -> int | str:
    if isinstance(x, int):
        return x * 2
    return x.upper()
```

### Generic type issues

```python
# Error
def first(items):  # Missing type parameters
    return items[0]

# Solution with TypeVar
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

## NEVER DO

```python
# Bad: type: ignore
result = problematic_code  # type: ignore

# Bad: Any everywhere
def process(x: Any) -> Any: ...

# Bad: cast without necessity
from typing import cast
result = cast(MyType, unknown_value)
```

## When cast is Acceptable

```python
# Only when you KNOW the type better than mypy
# For example, after isinstance check elsewhere
from typing import cast

# After check in calling code
def internal_process(user: User) -> None:
    # Here we know user is definitely User
    pass

# Or with TypeGuard
from typing import TypeGuard

def is_user(obj: object) -> TypeGuard[User]:
    return isinstance(obj, User)

if is_user(obj):
    obj.name  # mypy knows this is User
```

## Response Format

```
## Type Error

### What Happened
[error explanation]

### Why This is a Problem
[consequences of ignoring]

### How to Fix

**Before:**
```python
[problematic code]
```

**After:**
```python
[fixed code]
```

### Apply the Fix?
```
