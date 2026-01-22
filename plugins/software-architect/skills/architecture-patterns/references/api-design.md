# REST API Design

Best practices for designing RESTful APIs with FastAPI.

## Resource Naming

### URL Structure

```
# Collection
GET    /users              # List users
POST   /users              # Create user

# Single resource
GET    /users/{id}         # Get user
PUT    /users/{id}         # Replace user
PATCH  /users/{id}         # Update user
DELETE /users/{id}         # Delete user

# Nested resources (use sparingly)
GET    /users/{id}/orders  # User's orders
POST   /users/{id}/orders  # Create order for user

# Actions (when CRUD doesn't fit)
POST   /orders/{id}/cancel # Cancel order
POST   /users/{id}/verify  # Verify user
```

### Naming Conventions

```python
# Good — plural nouns, lowercase, hyphens
/api/v1/users
/api/v1/order-items
/api/v1/product-categories

# Bad
/api/v1/user           # Singular
/api/v1/getUsers       # Verb in URL
/api/v1/order_items    # Underscores
/api/v1/OrderItems     # CamelCase
```

## HTTP Methods and Status Codes

### Method Semantics

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | Yes | No |
| DELETE | Remove resource | Yes | No |

### Status Codes

```python
from fastapi import status

# Success codes
@router.get("/users/{id}")
async def get_user(id: int) -> UserReadDTO:
    """200 OK — successful retrieval."""
    return await service.get_by_id(id)

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateDTO) -> UserReadDTO:
    """201 Created — resource created."""
    return await service.create(data)

@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int) -> None:
    """204 No Content — deleted successfully."""
    await service.delete(id)

# Client error codes
@router.get("/users/{id}")
async def get_user(id: int) -> UserReadDTO:
    user = await service.get_by_id(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # 404 Not Found
            detail="User not found",
        )
    return user

# 400 Bad Request — validation errors (automatic via Pydantic)
# 401 Unauthorized — not authenticated
# 403 Forbidden — not authorized
# 409 Conflict — duplicate resource
# 422 Unprocessable Entity — semantic errors
```

## Request/Response DTOs

### Input Validation

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated


class UserCreateDTO(BaseModel):
    email: EmailStr
    name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=0, le=150)]
    password: Annotated[str, Field(min_length=8)]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserUpdateDTO(BaseModel):
    """Partial update — all fields optional."""
    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    age: Annotated[int, Field(ge=0, le=150)] | None = None
```

### Output Schemas

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserReadDTO(BaseDTO):
    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime


class UserDetailDTO(UserReadDTO):
    """Extended response with relations."""
    orders_count: int
    last_order_date: datetime | None
```

### Different DTOs for Different Operations

```python
# Create — required fields
class ProductCreateDTO(BaseModel):
    name: str
    sku: str
    price: Decimal

# Read — includes id and computed fields
class ProductReadDTO(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    is_available: bool
    created_at: datetime

# Update — all fields optional
class ProductUpdateDTO(BaseModel):
    name: str | None = None
    price: Decimal | None = None

# List item — minimal fields for lists
class ProductListItemDTO(BaseModel):
    id: int
    name: str
    price: Decimal
```

## Pagination

### Offset-based Pagination

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")


class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    offset: int
    limit: int
    has_more: bool


@router.get("/users")
async def list_users(
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[UserListItemDTO]:
    users, total = await service.get_paginated(
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return PaginatedResponse(
        items=users,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
        has_more=pagination.offset + len(users) < total,
    )
```

### Cursor-based Pagination

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    next_cursor: str | None
    has_more: bool


@router.get("/feed")
async def get_feed(
    cursor: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
) -> CursorPaginatedResponse[FeedItemDTO]:
    """Cursor pagination for infinite scroll."""
    items, next_cursor = await service.get_feed(cursor=cursor, limit=limit)
    return CursorPaginatedResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=next_cursor is not None,
    )
```

## Filtering and Sorting

### Query Parameters

```python
from enum import Enum
from fastapi import Query


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class UserSortField(str, Enum):
    CREATED_AT = "created_at"
    NAME = "name"
    EMAIL = "email"


@router.get("/users")
async def list_users(
    # Filtering
    is_active: bool | None = None,
    search: str | None = Query(None, min_length=1, max_length=100),
    created_after: datetime | None = None,

    # Sorting
    sort_by: UserSortField = UserSortField.CREATED_AT,
    order: SortOrder = SortOrder.DESC,

    # Pagination
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[UserListItemDTO]:
    return await service.search(
        is_active=is_active,
        search=search,
        created_after=created_after,
        sort_by=sort_by,
        order=order,
        offset=offset,
        limit=limit,
    )
```

### Filter DTO Pattern

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserFilters:
    is_active: bool | None = None
    search: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


def get_user_filters(
    is_active: bool | None = None,
    search: str | None = Query(None, min_length=1),
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> UserFilters:
    return UserFilters(
        is_active=is_active,
        search=search,
        created_after=created_after,
        created_before=created_before,
    )


@router.get("/users")
async def list_users(
    filters: Annotated[UserFilters, Depends(get_user_filters)],
) -> list[UserReadDTO]:
    return await service.search(filters)
```

## Error Responses

### Consistent Error Format

```python
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ErrorDetail] | None = None


# Example responses
"""
400 Bad Request:
{
    "error": "validation_error",
    "message": "Request validation failed",
    "details": [
        {"field": "email", "message": "Invalid email format", "code": "invalid_format"},
        {"field": "age", "message": "Must be positive", "code": "invalid_value"}
    ]
}

404 Not Found:
{
    "error": "not_found",
    "message": "User not found"
}

409 Conflict:
{
    "error": "conflict",
    "message": "User with this email already exists"
}
"""
```

### Custom Exception Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An internal error occurred"

    def __init__(self, message: str | None = None):
        self.message = message or self.message


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"
    message = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"
    message = "Resource already exists"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"
    message = "Validation failed"


async def app_exception_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
        },
    )


# Register handler
app.add_exception_handler(AppError, app_exception_handler)
```

## API Versioning

### URL Path Versioning (Recommended)

```python
from fastapi import APIRouter

# Version 1
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(users_v1.router, prefix="/users", tags=["users"])
v1_router.include_router(orders_v1.router, prefix="/orders", tags=["orders"])

# Version 2
v2_router = APIRouter(prefix="/api/v2")
v2_router.include_router(users_v2.router, prefix="/users", tags=["users"])

# Main app
app.include_router(v1_router)
app.include_router(v2_router)
```

### Header Versioning

```python
from fastapi import Header, HTTPException


async def get_api_version(
    x_api_version: str = Header(default="1", alias="X-API-Version"),
) -> str:
    if x_api_version not in ("1", "2"):
        raise HTTPException(400, "Unsupported API version")
    return x_api_version


@router.get("/users")
async def list_users(
    version: Annotated[str, Depends(get_api_version)],
):
    if version == "2":
        return await service.get_users_v2()
    return await service.get_users_v1()
```

## OpenAPI Documentation

### Documenting Endpoints

```python
from fastapi import APIRouter, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with the provided information.",
    response_description="The created user",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "User with this email already exists"},
        422: {"description": "Validation error"},
    },
)
async def create_user(
    data: UserCreateDTO,
) -> UserReadDTO:
    """
    Create a new user with the following information:

    - **email**: unique email address
    - **name**: user's display name
    - **password**: minimum 8 characters
    """
    return await service.create(data)
```

### Response Examples

```python
from pydantic import BaseModel, Field


class UserReadDTO(BaseModel):
    id: int = Field(example=1)
    email: str = Field(example="user@example.com")
    name: str = Field(example="John Doe")
    is_active: bool = Field(example=True)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
            }
        }
    )
```

## HATEOAS (Hypermedia)

```python
from pydantic import BaseModel


class Link(BaseModel):
    href: str
    rel: str
    method: str = "GET"


class UserReadDTO(BaseModel):
    id: int
    email: str
    name: str
    links: list[Link] = []

    @classmethod
    def from_orm_with_links(cls, user, request) -> "UserReadDTO":
        base_url = str(request.base_url)
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            links=[
                Link(href=f"{base_url}users/{user.id}", rel="self"),
                Link(href=f"{base_url}users/{user.id}", rel="update", method="PATCH"),
                Link(href=f"{base_url}users/{user.id}", rel="delete", method="DELETE"),
                Link(href=f"{base_url}users/{user.id}/orders", rel="orders"),
            ],
        )


"""
Response:
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "links": [
        {"href": "http://api.example.com/users/1", "rel": "self", "method": "GET"},
        {"href": "http://api.example.com/users/1", "rel": "update", "method": "PATCH"},
        {"href": "http://api.example.com/users/1", "rel": "delete", "method": "DELETE"},
        {"href": "http://api.example.com/users/1/orders", "rel": "orders", "method": "GET"}
    ]
}
"""
```

## Idempotency

### Idempotency Keys for POST

```python
from fastapi import Header, HTTPException
from uuid import UUID


@router.post("/orders")
async def create_order(
    data: OrderCreateDTO,
    idempotency_key: UUID = Header(alias="Idempotency-Key"),
) -> OrderReadDTO:
    """
    Create order with idempotency support.

    If the same Idempotency-Key is sent again, returns the original response.
    """
    # Check if we've seen this key before
    existing = await cache.get(f"idempotency:{idempotency_key}")
    if existing:
        return OrderReadDTO.model_validate_json(existing)

    # Create new order
    order = await service.create(data)

    # Store response for future requests with same key
    await cache.set(
        f"idempotency:{idempotency_key}",
        order.model_dump_json(),
        ttl=86400,  # 24 hours
    )

    return order
```

## Rate Limiting

```python
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


@router.get("/search")
@limiter.limit("10/minute")
async def search(
    request: Request,
    query: str,
) -> list[SearchResultDTO]:
    """Search with rate limiting: 10 requests per minute."""
    return await service.search(query)


@router.post("/orders")
@limiter.limit("100/hour")
async def create_order(
    request: Request,
    data: OrderCreateDTO,
) -> OrderReadDTO:
    """Create order with rate limiting: 100 per hour."""
    return await service.create(data)
```
