# Exception Handling

## Exception Hierarchy

```python
"""Application exceptions."""

from typing import Any


class AppError(Exception):
    """Base application error.

    All custom exceptions should inherit from this class.
    """

    status_code: int = 500
    detail: str = "Internal server error"
    headers: dict[str, str] | None = None

    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = detail or self.detail
        self.headers = headers or self.headers
        super().__init__(self.detail)


# 4xx Client Errors

class BadRequestError(AppError):
    """400 Bad Request."""

    status_code = 400
    detail = "Bad request"


class UnauthorizedError(AppError):
    """401 Unauthorized."""

    status_code = 401
    detail = "Not authenticated"
    headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenError(AppError):
    """403 Forbidden."""

    status_code = 403
    detail = "Not enough permissions"


class NotFoundError(AppError):
    """404 Not Found."""

    status_code = 404
    detail = "Resource not found"


class ConflictError(AppError):
    """409 Conflict."""

    status_code = 409
    detail = "Resource already exists"


class ValidationError(AppError):
    """422 Unprocessable Entity."""

    status_code = 422
    detail = "Validation error"

    def __init__(
        self,
        detail: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(detail)
        self.errors = errors or []


class TooManyRequestsError(AppError):
    """429 Too Many Requests."""

    status_code = 429
    detail = "Too many requests"


# 5xx Server Errors

class InternalError(AppError):
    """500 Internal Server Error."""

    status_code = 500
    detail = "Internal server error"


class ServiceUnavailableError(AppError):
    """503 Service Unavailable."""

    status_code = 503
    detail = "Service temporarily unavailable"
```

## Exception Handlers

```python
"""Exception handlers."""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from .exceptions import AppError


async def app_exception_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unhandled exceptions.

    In production, don't expose internal error details.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception: %s", exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

## Registering Handlers

```python
"""Application setup."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.core.exceptions import AppError
from src.core.handlers import (
    app_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)


def create_app() -> FastAPI:
    app = FastAPI()

    # Register exception handlers
    app.add_exception_handler(AppError, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    return app
```

## Usage in Services

```python
"""User service."""

from src.core.exceptions import NotFoundError, ConflictError
from .repositories import UserRepository
from .dto import UserCreateDTO, UserReadDTO


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_by_id(self, user_id: int) -> UserReadDTO:
        """Get user by ID."""
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User with id {user_id} not found")
        return UserReadDTO.model_validate(user)

    async def create(self, data: UserCreateDTO) -> UserReadDTO:
        """Create new user."""
        existing = await self._repository.get_by_email(data.email)
        if existing:
            raise ConflictError(f"User with email {data.email} already exists")

        user = await self._repository.save(data)
        return UserReadDTO.model_validate(user)
```

## Testing Exceptions

```python
"""Test exception handling."""

import pytest
from httpx import AsyncClient


class TestExceptionHandling:
    async def test_not_found_returns_404(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/api/v1/users/999999")

        assert response.status_code == 404
        assert response.json() == {"detail": "User with id 999999 not found"}

    async def test_conflict_returns_409(
        self,
        client: AsyncClient,
        sample_user,
    ) -> None:
        # Try to create user with existing email
        response = await client.post(
            "/api/v1/users",
            json={"email": sample_user.email, "name": "New User"},
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_validation_error_returns_422(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/users",
            json={"email": "invalid-email", "name": ""},
        )

        assert response.status_code == 422
        assert "errors" in response.json()
```

## Domain-specific Exceptions

```python
"""Order exceptions."""

from src.core.exceptions import AppError, ConflictError


class OrderError(AppError):
    """Base order error."""

    pass


class OrderAlreadyPaidError(OrderError):
    """Order is already paid."""

    status_code = 409
    detail = "Order is already paid"


class OrderCancelledError(OrderError):
    """Order is cancelled."""

    status_code = 409
    detail = "Cannot modify cancelled order"


class InsufficientStockError(OrderError):
    """Not enough items in stock."""

    status_code = 409

    def __init__(self, product_id: int, requested: int, available: int) -> None:
        self.detail = (
            f"Insufficient stock for product {product_id}: "
            f"requested {requested}, available {available}"
        )
        super().__init__(self.detail)


class PaymentError(OrderError):
    """Payment processing error."""

    status_code = 402  # Payment Required

    def __init__(self, reason: str) -> None:
        self.detail = f"Payment failed: {reason}"
        super().__init__(self.detail)
```
