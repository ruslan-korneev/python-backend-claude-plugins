# Generics in Python

## TypeVar

```python
from typing import TypeVar

# Simple TypeVar
T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

# Bound — restriction to subtypes
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

def validate(model: ModelT) -> ModelT:
    # model is guaranteed to have BaseModel methods
    model.model_dump()  # OK
    return model

# Constraints — only specific types
StrOrBytes = TypeVar("StrOrBytes", str, bytes)

def process(data: StrOrBytes) -> StrOrBytes:
    # data is either str or bytes, but not both at the same time
    return data
```

## Generic Classes

### Traditional Syntax

```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Repository(Generic[T]):
    """Generic repository."""

    def __init__(self, model: type[T]) -> None:
        self._model = model

    def get(self, id: int) -> T | None:
        ...

    def save(self, item: T) -> T:
        ...


class Cache(Generic[K, V]):
    """Generic cache with key-value types."""

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value
```

### Python 3.12+ Syntax

```python
# New syntax — cleaner
class Repository[T]:
    def __init__(self, model: type[T]) -> None:
        self._model = model

    def get(self, id: int) -> T | None:
        ...

    def save(self, item: T) -> T:
        ...


class Cache[K, V]:
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value


# With bounds
class Repository[T: BaseModel]:
    def validate(self, item: T) -> T:
        item.model_validate(item.model_dump())
        return item
```

## Covariance and Contravariance

```python
from typing import TypeVar

# Covariant — can use subtypes
T_co = TypeVar("T_co", covariant=True)

class Reader(Generic[T_co]):
    def read(self) -> T_co:
        ...

# Reader[Dog] can be assigned to Reader[Animal]


# Contravariant — can use supertypes
T_contra = TypeVar("T_contra", contravariant=True)

class Writer(Generic[T_contra]):
    def write(self, value: T_contra) -> None:
        ...

# Writer[Animal] can be assigned to Writer[Dog]
```

## Generic Functions

```python
from typing import TypeVar, overload

T = TypeVar("T")


# Simple generic function
def identity(x: T) -> T:
    return x


# With multiple TypeVars
def pair(a: T, b: K) -> tuple[T, K]:
    return (a, b)


# With constraints
def stringify(x: T) -> str:
    return str(x)


# Overload for different types
@overload
def process(x: int) -> int: ...
@overload
def process(x: str) -> str: ...
@overload
def process(x: list[T]) -> list[T]: ...

def process(x):
    if isinstance(x, int):
        return x * 2
    elif isinstance(x, str):
        return x.upper()
    else:
        return [item for item in x]
```

## Generic with Protocol

```python
from typing import Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool:
        ...


CT = TypeVar("CT", bound=Comparable)


def min_value(a: CT, b: CT) -> CT:
    return a if a < b else b


# Works with any type implementing __lt__
min_value(1, 2)  # OK
min_value("a", "b")  # OK
min_value([1, 2], [3, 4])  # OK
```

## Self Type

```python
from typing import Self


class Builder:
    def __init__(self) -> None:
        self._value = ""

    def add(self, s: str) -> Self:
        self._value += s
        return self

    def build(self) -> str:
        return self._value


class ExtendedBuilder(Builder):
    def add_line(self, s: str) -> Self:
        self._value += s + "\n"
        return self


# Self works correctly with inheritance
builder = ExtendedBuilder().add("hello").add_line("world")
# builder has type ExtendedBuilder, not Builder
```

## ParamSpec for Decorators

```python
from typing import ParamSpec, TypeVar, Callable
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@log_calls
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"


# Signature is preserved
greet("World")  # mypy knows argument types
```

## Concatenate

```python
from typing import ParamSpec, TypeVar, Callable, Concatenate

P = ParamSpec("P")
R = TypeVar("R")


def with_context(
    func: Callable[Concatenate[Context, P], R]
) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = Context()
        return func(ctx, *args, **kwargs)
    return wrapper


@with_context
def process(ctx: Context, name: str) -> str:
    return ctx.format(name)


# Call without ctx — it's added automatically
process("hello")
```

## TypeVarTuple (Python 3.11+)

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")


def concat(*args: Unpack[Ts]) -> tuple[Unpack[Ts]]:
    return args


result = concat(1, "hello", True)
# result: tuple[int, str, bool]
```
