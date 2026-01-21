# DTOs with Pydantic v2

## BaseDTO

```python
"""Base DTO configuration."""

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Base DTO with ORM mode and common settings."""

    model_config = ConfigDict(
        # Allows creating from ORM objects
        from_attributes=True,
        # Allows using alias or original name
        populate_by_name=True,
        # Strips whitespace from string edges
        str_strip_whitespace=True,
        # Strict type validation
        strict=False,
    )
```

## Create/Read/Update Pattern

```python
"""User DTOs."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# Base with common fields
class UserBaseDTO(BaseDTO):
    """Base user DTO."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)


# Create — without id and auto-generated fields
class UserCreateDTO(UserBaseDTO):
    """DTO for creating user."""

    password: str = Field(..., min_length=8)


# Read — all fields for reading
class UserReadDTO(UserBaseDTO):
    """DTO for reading user."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


# Update — all fields are optional
class UserUpdateDTO(BaseModel):
    """DTO for updating user."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None
```

## Field Validation

### Field constraints

```python
from pydantic import Field


class ProductCreateDTO(BaseDTO):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)  # greater than 0
    quantity: int = Field(..., ge=0)  # greater or equal 0
    description: str | None = Field(None, max_length=1000)
    sku: str = Field(..., pattern=r"^[A-Z]{3}-\d{4}$")
```

### Field validators

```python
from pydantic import field_validator


class UserCreateDTO(BaseDTO):
    email: str
    username: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()
```

### Model validators

```python
from pydantic import model_validator


class PasswordChangeDTO(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str

    @model_validator(mode="after")
    def validate_passwords(self) -> "PasswordChangeDTO":
        if self.new_password != self.new_password_confirm:
            raise ValueError("Passwords do not match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different")
        return self
```

## Nested DTOs

```python
"""Order DTOs with nested items."""

from pydantic import computed_field


class OrderItemReadDTO(BaseDTO):
    """Order item DTO."""

    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderReadDTO(BaseDTO):
    """Order DTO with items."""

    id: int
    user_id: int
    status: str
    items: list[OrderItemReadDTO]
    created_at: datetime

    @computed_field
    @property
    def total(self) -> float:
        """Calculate order total."""
        return sum(item.price * item.quantity for item in self.items)

    @computed_field
    @property
    def items_count(self) -> int:
        """Count of items."""
        return len(self.items)


class OrderCreateDTO(BaseDTO):
    """DTO for creating order."""

    items: list["OrderItemCreateDTO"]


class OrderItemCreateDTO(BaseDTO):
    """DTO for creating order item."""

    product_id: int
    quantity: int = Field(..., gt=0)
```

## Enum Fields

```python
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderReadDTO(BaseDTO):
    id: int
    status: OrderStatus


class OrderUpdateDTO(BaseModel):
    status: OrderStatus | None = None
```

## Aliases for API

```python
"""DTOs with camelCase aliases for JSON API."""

from pydantic import Field


class UserReadDTO(BaseDTO):
    """User DTO with camelCase JSON keys."""

    id: int
    full_name: str = Field(alias="fullName")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")


# JSON output: {"id": 1, "fullName": "John", "isActive": true, "createdAt": "..."}
# Python access: user.full_name, user.is_active
```

## Partial Updates

```python
"""Partial update pattern."""

from pydantic import BaseModel


class UserUpdateDTO(BaseModel):
    """All fields optional for partial update."""

    email: str | None = None
    name: str | None = None
    is_active: bool | None = None


# In service
async def update(self, user_id: int, data: UserUpdateDTO) -> User:
    # Only changed fields
    update_data = data.model_dump(exclude_unset=True)
    # {'name': 'New Name'} — if only name was passed

    return await self._repository.update(user_id, update_data)
```

## Response Models

```python
"""Paginated response."""

from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int

    @computed_field
    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


# Usage
async def get_users(
    limit: int = 20,
    offset: int = 0,
) -> PaginatedResponse[UserReadDTO]:
    users = await repo.get_all(limit=limit, offset=offset)
    total = await repo.count()
    return PaginatedResponse(
        items=users,
        total=total,
        limit=limit,
        offset=offset,
    )
```

## Serialization

```python
"""Serialization examples."""

# From ORM object
user = await session.get(User, 1)
dto = UserReadDTO.model_validate(user)

# To dict
data = dto.model_dump()
# {'id': 1, 'email': '...', 'name': '...'}

# To JSON
json_str = dto.model_dump_json()
# '{"id": 1, "email": "...", "name": "..."}'

# Only specific fields
data = dto.model_dump(include={"id", "email"})

# Exclude fields
data = dto.model_dump(exclude={"created_at", "updated_at"})

# With aliases
data = dto.model_dump(by_alias=True)
# {'id': 1, 'fullName': 'John', 'isActive': true}
```
