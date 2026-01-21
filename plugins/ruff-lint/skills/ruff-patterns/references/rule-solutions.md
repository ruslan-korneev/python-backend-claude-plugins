# Ruff Rule Solutions

Database of proper solutions for ruff errors. **Never use `# noqa`!**

## Official Documentation

For any rule you can view a detailed description:

```
https://docs.astral.sh/ruff/rules/{rule-code}
```

For example:
- E501: https://docs.astral.sh/ruff/rules/E501
- F401: https://docs.astral.sh/ruff/rules/F401
- B008: https://docs.astral.sh/ruff/rules/B008

The documentation contains:
- Problem description
- Why it's bad
- Examples of bad and good code
- Related rules

---

## Pycodestyle (E/W)

### E501: Line too long

**Problem**: Line exceeds the limit (usually 88 or 120 characters).

**Solutions**:

```python
# 1. Long function call — use parentheses
# Bad
result = some_function(very_long_argument_name, another_long_argument, yet_another_one, and_more)

# Good
result = some_function(
    very_long_argument_name,
    another_long_argument,
    yet_another_one,
    and_more,
)

# 2. Long string — use concatenation
# Bad
message = "This is a very long message that would exceed the line length limit if written on one line"

# Good
message = (
    "This is a very long message that would exceed "
    "the line length limit if written on one line"
)

# 3. Long import — split into lines
# Bad
from some_module import SomeClass, AnotherClass, YetAnotherClass, AndMoreClasses, EvenMoreClasses

# Good
from some_module import (
    AnotherClass,
    AndMoreClasses,
    EvenMoreClasses,
    SomeClass,
    YetAnotherClass,
)

# 4. URL in comment — extract to variable
# Bad
# See https://very-long-documentation-url.com/path/to/specific/section/with/many/params?foo=bar

# Good
# Documentation: https://docs.example.com/section
DOCS_URL = "https://very-long-documentation-url.com/path/to/specific/section"
```

### E711: Comparison to None

```python
# Bad
if value == None:
    ...

# Good
if value is None:
    ...
```

### E712: Comparison to True/False

```python
# Bad
if flag == True:
    ...

# Good
if flag:
    ...

# For explicit type check
if flag is True:  # only if you need to distinguish True from truthy
    ...
```

---

## Pyflakes (F)

### F401: Module imported but unused

**Solutions**:

```python
# 1. Simply remove the import
# Bad
from typing import List, Dict, Optional  # Dict is not used

# Good
from typing import List, Optional

# 2. If import is for re-export
# Option A: explicit re-export via `as`
from .models import User as User
from .schemas import UserDTO as UserDTO

# Option B: use __all__
from .models import User
from .schemas import UserDTO

__all__ = ["User", "UserDTO"]

# 3. If import is for TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User  # used only for type hints
```

### F811: Redefinition of unused name

```python
# Bad
def process():
    return 1

def process():  # redefinition
    return 2

# Good — remove first definition or rename
def process_v1():
    return 1

def process_v2():
    return 2
```

### F841: Local variable assigned but never used

```python
# 1. If result is not needed — use _
# Bad
def process():
    result = expensive_calculation()  # result is not used
    return True

# Good
def process():
    _ = expensive_calculation()
    return True

# 2. For unpacking
# Bad
x, y, z = get_coordinates()  # z is not used

# Good
x, y, _ = get_coordinates()

# 3. If result is really needed — use it
def process():
    result = expensive_calculation()
    logger.info("Calculated: %s", result)
    return True
```

---

## Flake8-bugbear (B)

### B008: Do not perform function calls in argument defaults

**Problem**: Mutable default argument or function call at definition time.

```python
# Bad — list is created once at function definition!
def process(items: list = []):
    items.append(1)
    return items

# Good
def process(items: list | None = None):
    if items is None:
        items = []
    items.append(1)
    return items

# Bad — datetime.now() is called at module import!
def log_event(timestamp: datetime = datetime.now()):
    ...

# Good
def log_event(timestamp: datetime | None = None):
    if timestamp is None:
        timestamp = datetime.now()
    ...

# Exception: FastAPI Depends — this is NORMAL!
# Configure per-file-ignores:
# [tool.ruff.lint.per-file-ignores]
# "src/*/routers.py" = ["B008"]

# Or use Annotated (Python 3.9+)
from typing import Annotated

async def get_items(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    ...
```

### B006: Do not use mutable data structures for argument defaults

```python
# Bad
def process(config: dict = {}):
    config["processed"] = True
    return config

# Good
def process(config: dict | None = None):
    if config is None:
        config = {}
    config["processed"] = True
    return config
```

### B007: Loop control variable not used within loop body

```python
# Bad
for i in range(10):
    do_something()

# Good
for _ in range(10):
    do_something()
```

---

## Pylint (PL)

### PLR0913: Too many arguments

**Problem**: Function takes too many arguments.

```python
# Bad
def create_user(
    name: str,
    email: str,
    age: int,
    city: str,
    country: str,
    phone: str,
    role: str,
    department: str,
) -> User:
    ...

# Good — use Pydantic model
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

def create_user(data: CreateUserDTO) -> User:
    ...

# Alternative — dataclass
from dataclasses import dataclass

@dataclass
class CreateUserParams:
    name: str
    email: str
    # ...
```

### PLR2004: Magic value used in comparison

```python
# Bad
if response.status_code == 200:
    ...
if len(items) > 100:
    ...

# Good — use constants with descriptive names
from http import HTTPStatus

if response.status_code == HTTPStatus.OK:
    ...

MAX_ITEMS = 100
if len(items) > MAX_ITEMS:
    ...
```

### PLW2901: Redefined loop variable

```python
# Bad
for item in items:
    for item in item.children:  # redefinition!
        process(item)

# Good
for item in items:
    for child in item.children:
        process(child)
```

### PLC0415: Import outside top-level

**Problem**: Import is not at the beginning of the file.

**Why it's bad**:
- Harder to understand module dependencies
- Implicit circular imports
- Unpredictable load time
- Violates PEP 8

```python
# Bad — import in the middle of file
def process_data(data: dict) -> str:
    import json  # PLC0415: Import outside top-level
    return json.dumps(data)

def calculate(x: int) -> float:
    from math import sqrt  # PLC0415
    return sqrt(x)

# Good — all imports at the beginning of file
import json
from math import sqrt


def process_data(data: dict) -> str:
    return json.dumps(data)

def calculate(x: int) -> float:
    return sqrt(x)
```

**Exceptions (rare cases)**:

```python
# 1. Optional dependencies — but better try/except at the top
try:
    import orjson as json
except ImportError:
    import json

# 2. TYPE_CHECKING — this is normal and recommended
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User  # This is OK — not executed at runtime

# 3. Avoiding circular imports — but better to refactor
# Bad
def get_user_service():
    from .services import UserService  # Workaround
    return UserService()

# Good — refactor architecture
# Extract common code to separate module or use DI
```

**Rule**: All imports should be at the beginning of the file. If you need an import in the middle of the file — it's a signal of architecture problems.

---

## Bandit (S) — Security

### S101: Use of assert detected

**Problem**: `assert` is disabled when running with `-O`.

```python
# Bad — won't work with python -O
def process(data):
    assert data is not None
    return data.value

# Good
def process(data):
    if data is None:
        raise ValueError("data cannot be None")
    return data.value

# For tests S101 is allowed via per-file-ignores:
# [tool.ruff.lint.per-file-ignores]
# "tests/**/*.py" = ["S101"]
```

### S105: Hardcoded password string

```python
# Bad
PASSWORD = "secret123"
db_url = "postgresql://user:password@localhost/db"

# Good — use environment variables
import os

PASSWORD = os.environ["DB_PASSWORD"]
db_url = f"postgresql://user:{os.environ['DB_PASSWORD']}@localhost/db"

# Or pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_password: str

    class Config:
        env_file = ".env"
```

### S311: Standard pseudo-random generators not suitable for security

```python
# Bad for security (tokens, passwords)
import random
token = random.randint(0, 999999)

# Good
import secrets
token = secrets.token_hex(16)
```

---

## Pyupgrade (UP)

### UP007: Use X | Y for type union

```python
# Bad (Python < 3.10 style)
from typing import Optional, Union

def process(value: Optional[str]) -> Union[int, str]:
    ...

# Good (Python 3.10+)
def process(value: str | None) -> int | str:
    ...
```

### UP035: Import from typing instead of typing_extensions

```python
# Bad (if Python >= 3.11)
from typing_extensions import Self

# Good
from typing import Self
```

---

## Ruff-specific (RUF)

### RUF012: Mutable class attributes should be annotated with ClassVar

```python
# Bad — will be shared across all instances!
class Config:
    items: list[str] = []

# Good — explicitly indicate ClassVar
from typing import ClassVar

class Config:
    items: ClassVar[list[str]] = []

# Or for instance variable
class Config:
    items: list[str]

    def __init__(self) -> None:
        self.items = []
```

### RUF013: PEP 484 prohibits implicit Optional

```python
# Bad
def process(value: str = None):  # implicit Optional
    ...

# Good
def process(value: str | None = None):
    ...
```

---

## FastAPI-specific Solutions

### B008 in routers

FastAPI uses `Depends()` in default arguments — this is by design.

```toml
# pyproject.toml
[tool.ruff.lint.per-file-ignores]
"src/*/routers.py" = ["B008"]
"src/**/api/**/*.py" = ["B008"]
```

### Long endpoint signatures

```python
# Use Annotated for cleaner code
from typing import Annotated
from fastapi import Depends, Query

SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[Pagination, Depends(get_pagination)]

@router.get("/items")
async def get_items(
    session: SessionDep,
    pagination: PaginationDep,
    filters: Annotated[ItemFilters, Query()],
) -> list[ItemDTO]:
    ...
```
