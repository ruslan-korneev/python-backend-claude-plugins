# Dictionary Typing

## Maturity Levels

```python
# Bad: Weak level — no information about contents
def process(data: dict): ...

# Warning: Medium level — slightly better, but still Any
def process(data: dict[str, Any]): ...

# Good: Strong level — full information about structure
class UserData(TypedDict):
    id: int
    email: str
    name: str

def process(data: UserData): ...
```

## Why `dict` and `dict[str, Any]` Are Bad

### Problem 1: No Key Checking

```python
def process(data: dict[str, Any]) -> None:
    # Error at runtime, not during type checking
    print(data["emial"])  # Typo — mypy won't see it

def process(data: UserData) -> None:
    print(data["emial"])  # Error: TypedDict "UserData" has no key "emial"
```

### Problem 2: No Value Type Checking

```python
def process(data: dict[str, Any]) -> None:
    age: int = data["age"]  # Any is assigned to int without error
    # But data["age"] could be a string!

def process(data: UserData) -> None:
    age: int = data["age"]  # If age: str in TypedDict — error
```

### Problem 3: No Autocomplete

```python
# dict[str, Any] — IDE doesn't know what keys exist
data["???"]

# TypedDict — IDE suggests: id, email, name
data[""]  # Autocomplete works!
```

## TypedDict

### Basic Usage

```python
from typing import TypedDict


class UserDTO(TypedDict):
    id: int
    email: str
    name: str


# Creation
user: UserDTO = {"id": 1, "email": "test@example.com", "name": "Test"}

# Errors during creation
user: UserDTO = {"id": "1", "email": "test@example.com", "name": "Test"}
# Error: Expected int, got str for key "id"

user: UserDTO = {"id": 1, "email": "test@example.com"}
# Error: Missing key "name"
```

### Optional Fields

```python
from typing import TypedDict, NotRequired, Required


# All fields required by default
class UserCreate(TypedDict):
    email: str
    name: str
    age: NotRequired[int]  # Optional field


# All fields optional by default
class UserUpdate(TypedDict, total=False):
    email: str
    name: str
    age: int


# Mixed variant with total=False
class UserPatch(TypedDict, total=False):
    email: str
    name: str
    id: Required[int]  # Required field
```

### Inheritance

```python
class BaseUser(TypedDict):
    id: int
    email: str


class AdminUser(BaseUser):
    role: str
    permissions: list[str]


# AdminUser has: id, email, role, permissions
```

### ReadOnly Fields (Python 3.13+)

```python
from typing import TypedDict, ReadOnly


class Config(TypedDict):
    debug: ReadOnly[bool]
    version: ReadOnly[str]
    settings: dict[str, str]  # Mutable


config: Config = {"debug": True, "version": "1.0", "settings": {}}
config["debug"] = False  # Error: "debug" is read-only
config["settings"]["key"] = "value"  # OK
```

## When to Use What

### TypedDict — For Structured Data

```python
# API responses
class APIResponse(TypedDict):
    status: str
    data: dict[str, Any]  # Nested Any is acceptable if structure is unknown
    errors: list[str]


# Config objects
class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str


# DTOs from external sources
class WebhookPayload(TypedDict):
    event: str
    timestamp: int
    data: dict[str, Any]
```

### dict[K, V] — For Homogeneous Collections

```python
# Cache with same value type
cache: dict[str, User] = {}

# Counters
counters: dict[str, int] = {"views": 0, "clicks": 0}

# ID → object mapping
users_by_id: dict[int, User] = {}
```

### Mapping — For Read-Only Access

```python
from collections.abc import Mapping


def process_config(config: Mapping[str, str]) -> None:
    # Read-only, no modification
    value = config.get("key")


# Accepts dict, frozendict, ChainMap, etc.
```

## Converting dict → TypedDict

```python
from typing import TypedDict, cast


class UserData(TypedDict):
    id: int
    name: str


# If confident about structure (e.g., after validation)
raw_data: dict[str, Any] = json.loads(response)
user = cast(UserData, raw_data)

# Better — validation via Pydantic
from pydantic import TypeAdapter

adapter = TypeAdapter(UserData)
user = adapter.validate_python(raw_data)  # Runtime validation
```

## Integration with Pydantic

```python
from pydantic import BaseModel
from typing import TypedDict


# Pydantic model
class UserModel(BaseModel):
    id: int
    email: str
    name: str


# TypedDict for dict representation
class UserDict(TypedDict):
    id: int
    email: str
    name: str


def process_user(data: UserDict) -> UserModel:
    return UserModel(**data)


# model_dump() returns dict, but can be typed
user_dict: UserDict = user_model.model_dump()  # type: ignore[assignment]
# Here type: ignore is acceptable — Pydantic guarantees the structure
```

## Nested TypedDict

```python
class Address(TypedDict):
    city: str
    street: str
    zip_code: str


class Company(TypedDict):
    name: str
    address: Address


class User(TypedDict):
    id: int
    name: str
    company: Company


user: User = {
    "id": 1,
    "name": "John",
    "company": {
        "name": "Acme",
        "address": {
            "city": "NYC",
            "street": "123 Main St",
            "zip_code": "10001",
        },
    },
}
```

## Checklist Before Using dict

Before writing `dict` or `dict[str, Any]`, ask yourself:

1. **Do I know the dictionary structure?**
   - Yes → use `TypedDict`
   - No, but I know key and value types → `dict[K, V]`
   - No, dynamic structure → `dict[str, Any]` (last resort)

2. **Is the dictionary read-only?**
   - Yes → `Mapping[K, V]` instead of `dict[K, V]`

3. **Is this an API response / config / DTO?**
   - Yes → almost always `TypedDict`

4. **Is this a homogeneous collection (all values same type)?**
   - Yes → `dict[str, ValueType]`
