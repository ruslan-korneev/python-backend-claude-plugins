# Python Typing Patterns

Python type annotation patterns without `type: ignore`. Always the correct solution.

## Triggers

Use this skill when the user:
- Gets mypy/pyright errors
- Asks about Python type annotations
- Wants to add type hints
- Works with generics, protocols, TypeVar

## Main Principle: NEVER type: ignore

Every type error has a correct solution. `type: ignore` is:
- Masking potential bugs
- Disabling type checking
- Technical debt

More details: `${CLAUDE_PLUGIN_ROOT}/skills/typing-patterns/references/why-no-type-ignore.md`

## Dictionary Typing — TypedDict Instead of dict

More details: `${CLAUDE_PLUGIN_ROOT}/skills/typing-patterns/references/dict-typing.md`

```python
# Bad: Weak level
def process(data: dict): ...

# Warning: Medium level
def process(data: dict[str, Any]): ...

# Good: Strong level
class UserData(TypedDict):
    id: int
    email: str
    name: str

def process(data: UserData): ...
```

**Why TypedDict is better:**
- Key checking at compile time (`data["emial"]` → error)
- Value type checking
- IDE autocomplete
- Data structure documentation

**When `dict[K, V]` is acceptable:**
- Homogeneous collections: `dict[str, User]`, `dict[int, float]`
- Caches, counters, ID → object mappings

## Basic Types (Python 3.10+)

```python
# Primitives
x: int = 1
y: str = "hello"
z: bool = True
f: float = 1.5

# Collections (built-in)
items: list[str] = ["a", "b"]
mapping: dict[str, int] = {"a": 1}
unique: set[int] = {1, 2, 3}
pair: tuple[int, str] = (1, "a")

# Union (Python 3.10+)
value: int | str = 1
optional: str | None = None

# Callable
from collections.abc import Callable
handler: Callable[[int, str], bool] = lambda x, s: True
```

## Generics

More details: `${CLAUDE_PLUGIN_ROOT}/skills/typing-patterns/references/generics.md`

```python
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
    def save(self, item: T) -> T: ...


# Usage
class UserRepository(Repository[User]):
    pass


# Python 3.12+ syntax
class Repository[T]:
    def get(self, id: int) -> T | None: ...
```

## Protocols

```python
from typing import Protocol


class Readable(Protocol):
    def read(self) -> str: ...


class Writable(Protocol):
    def write(self, data: str) -> None: ...


# Structural subtyping — no explicit inherit needed
class MyFile:
    def read(self) -> str:
        return "content"


def process(source: Readable) -> str:
    return source.read()


process(MyFile())  # OK — MyFile implements Readable
```

## TypeVar with Constraints

```python
from typing import TypeVar

# Bound — only subtypes
T = TypeVar("T", bound=BaseModel)

def validate(model: T) -> T:
    # model is guaranteed to have BaseModel methods
    return model


# Constraints — only specific types
S = TypeVar("S", str, bytes)

def process(data: S) -> S:
    # data is either str or bytes
    return data
```

## Overload

```python
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

## TypeGuard

```python
from typing import TypeGuard


def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


items: list[object] = ["a", "b", "c"]
if is_string_list(items):
    # mypy knows: items is list[str]
    print(items[0].upper())
```

## Common Error Solutions

### Optional Without Check

```python
# Bad
def get_name(user: User | None) -> str:
    return user.name  # Error: Item "None" has no attribute "name"

# Good
def get_name(user: User | None) -> str:
    if user is None:
        raise ValueError("User is required")
    return user.name
```

### Missing Return Type

```python
# Bad
def process(x):
    return x * 2

# Good
def process(x: int) -> int:
    return x * 2
```

### list Without Type

```python
# Bad
items = []  # Need type annotation

# Good
items: list[str] = []
```

### Callable Types

```python
# Bad
def register(callback):
    ...

# Good
from collections.abc import Callable

def register(callback: Callable[[int], str]) -> None:
    ...

# Or with ParamSpec for exact signature passing
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def decorator(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper
```

## Configuration

### mypy (strict)

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_untyped_calls = true
```

### pyright

```json
{
  "typeCheckingMode": "strict",
  "pythonVersion": "3.12"
}
```

## Plugin Commands

- `/types:check [path]` — check types
- `/types:explain <error>` — explain error + solution
