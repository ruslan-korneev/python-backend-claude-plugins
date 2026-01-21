---
name: dto
description: Create Create/Read/Update DTOs from model
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: model
    description: "Path to model file or model name (e.g.: User or src/modules/users/models.py)"
    required: true
---

# Command /fastapi:dto

Create Pydantic DTOs (Create, Read, Update) based on SQLAlchemy model.

## Instructions

### Step 1: Read model

Find and read SQLAlchemy model:
```bash
# If path is provided
cat {{ model }}

# If name is provided
grep -r "class {{ model }}" src/
```

### Step 2: Extract fields

Determine:
- All model fields
- Field types
- Nullable fields
- Fields with default values
- Relationships

### Step 3: Create DTOs

#### SQLAlchemy → Pydantic Type Mapping

| SQLAlchemy | Pydantic |
|------------|----------|
| `Integer` | `int` |
| `String` | `str` |
| `Boolean` | `bool` |
| `Float` | `float` |
| `DateTime` | `datetime` |
| `Date` | `date` |
| `Text` | `str` |
| `JSON` | `dict` or `list` |
| `Enum` | `Literal[...]` or `Enum` |
| `UUID` | `uuid.UUID` |

#### BaseDTO

```python
"""{{ model }} DTOs."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class {{ model }}BaseDTO(BaseModel):
    """Base DTO with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
```

#### CreateDTO

```python
class {{ model }}CreateDTO({{ model }}BaseDTO):
    """DTO for creating {{ model }}.

    Excludes: id, created_at, updated_at (auto-generated).
    """

    # Required fields (without default)
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

    # Optional fields
    description: str | None = None
    is_active: bool = True
```

#### ReadDTO

```python
class {{ model }}ReadDTO({{ model }}BaseDTO):
    """DTO for reading {{ model }}.

    Includes all fields including auto-generated.
    """

    id: int
    name: str
    email: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
```

#### UpdateDTO

```python
class {{ model }}UpdateDTO(BaseModel):
    """DTO for updating {{ model }}.

    All fields are optional.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    description: str | None = None
    is_active: bool | None = None
```

## Special Cases

### Nested DTOs (relationships)

```python
# If model has relationships
class OrderReadDTO(OrderBaseDTO):
    id: int
    user_id: int
    items: list["OrderItemReadDTO"]  # Forward reference
    user: "UserReadDTO | None" = None  # Optional nested

    model_config = ConfigDict(from_attributes=True)


class OrderItemReadDTO(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)
```

### Enum fields

```python
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderCreateDTO(BaseModel):
    status: OrderStatus = OrderStatus.PENDING


class OrderReadDTO(BaseModel):
    status: OrderStatus
```

### Computed fields

```python
from pydantic import computed_field


class OrderReadDTO(BaseModel):
    items: list[OrderItemReadDTO]

    @computed_field
    @property
    def total(self) -> float:
        """Calculate total from items."""
        return sum(item.price * item.quantity for item in self.items)
```

### Validation

```python
from pydantic import field_validator, model_validator


class UserCreateDTO(BaseModel):
    email: str
    password: str
    password_confirm: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreateDTO":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

### Alias for API

```python
class UserReadDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    full_name: str = Field(alias="fullName")  # JSON: fullName, Python: full_name
    is_active: bool = Field(alias="isActive")
```

## Response Format

```
## DTOs created for model: {{ model }}

### {{ model }}CreateDTO
```python
[code]
```

### {{ model }}ReadDTO
```python
[code]
```

### {{ model }}UpdateDTO
```python
[code]
```

### Location
`src/modules/{{ module }}/dto.py`
```
