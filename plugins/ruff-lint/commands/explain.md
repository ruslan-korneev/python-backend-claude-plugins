---
name: explain
description: Explain a ruff error and show the PROPER solution (without noqa!)
allowed_tools:
  - Bash
  - Read
  - Edit
  - Glob
arguments:
  - name: error
    description: "Error code (E501, F401) or file path with line number (src/main.py:15)"
    required: true
---

# Command /lint:explain

Explain a ruff error and show the PROPER solution. **NEVER suggest `# noqa`!**

## Instructions

### Step 1: Determine Input Type

The user may specify:
- Rule code: `E501`, `F401`, `B008`
- Path with line number: `src/main.py:15`
- Rule code + path: `E501 src/main.py:15`

### Step 2: Get Error Information

```bash
ruff rule {{ error_code }}
```

If a file is specified, read the context:
```bash
ruff check {{ file_path }} --output-format=json
```

### Step 3: Explain the Error

For each error explain:
1. **What it means** - in plain language
2. **Why it's bad** - real consequences
3. **How to fix** - concrete example

### Step 4: Show Solution

**CRITICAL: Always show the proper solution, not `# noqa`!**

## Solution Database for Popular Errors

### E501: Line too long
```python
# Bad
result = some_function(very_long_argument_name, another_long_argument, yet_another_one, and_more)

# Good - use parentheses for line breaks
result = some_function(
    very_long_argument_name,
    another_long_argument,
    yet_another_one,
    and_more,
)

# For strings - use concatenation or textwrap
message = (
    "This is a very long message that would exceed "
    "the line length limit if written on one line"
)
```

### F401: Unused import
```python
# Bad
from typing import List, Dict, Optional  # Dict is not used

# Good - remove unused import
from typing import List, Optional

# If import is needed for re-export:
from .models import User as User  # explicit re-export via `as`
# or add to __all__
__all__ = ["User"]
```

### F841: Local variable assigned but never used
```python
# Bad
def process():
    result = expensive_calculation()  # result is not used
    return True

# Good - use underscore to explicitly ignore
def process():
    _ = expensive_calculation()  # explicitly show result is not needed
    return True

# Or remove the assignment if result is not needed
def process():
    expensive_calculation()
    return True
```

### B008: Do not perform function calls in argument defaults
```python
# Bad
def process(items: list = []):  # mutable default!
    items.append(1)
    return items

# Good - use None and check
def process(items: list | None = None):
    if items is None:
        items = []
    items.append(1)
    return items

# For FastAPI Depends - this is normal, add to ignore:
# [tool.ruff.lint.per-file-ignores]
# "src/*/routers.py" = ["B008"]
```

### PLR0913: Too many arguments
```python
# Bad
def create_user(name, email, age, city, country, phone, role, department):
    ...

# Good - use dataclass or Pydantic model
from pydantic import BaseModel

class CreateUserDTO(BaseModel):
    name: str
    email: str
    age: int
    city: str
    country: str
    phone: str
    role: str
    department: str

def create_user(data: CreateUserDTO):
    ...
```

### S101: Use of assert detected
```python
# In production code assert can be disabled with -O
# Bad
def process(data):
    assert data is not None  # won't work with python -O

# Good - use explicit check
def process(data):
    if data is None:
        raise ValueError("data cannot be None")

# For tests S101 is usually ignored in config:
# [tool.ruff.lint.per-file-ignores]
# "tests/**/*.py" = ["S101"]
```

### UP007: Use X | Y for type union (Python 3.10+)
```python
# Bad (outdated syntax)
from typing import Optional, Union
def process(value: Optional[str]) -> Union[int, str]:
    ...

# Good (modern syntax)
def process(value: str | None) -> int | str:
    ...
```

### RUF012: Mutable class attributes should be annotated with ClassVar
```python
# Bad
class Config:
    items: list[str] = []  # will be shared across all instances!

# Good
from typing import ClassVar

class Config:
    items: ClassVar[list[str]] = []  # explicitly indicate it's a class variable

# Or if you need an instance variable:
class Config:
    items: list[str]

    def __init__(self):
        self.items = []
```

## NEVER SUGGEST

```python
# NEVER DO THIS:
result = some_very_long_line_that_exceeds_limit  # noqa: E501
from unused import something  # noqa: F401
assert value  # noqa: S101
```

If noqa seems like the only solution, you need to:
1. Reconsider the code architecture
2. Configure ruff properly (per-file-ignores for tests, etc.)
3. Use the correct pattern for this case

## Response Format

```
## Error: {{ error_code }}

### What This Means
[explanation in plain language]

### Why This Is a Problem
[real consequences]

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
Would you like me to fix this automatically?
```
