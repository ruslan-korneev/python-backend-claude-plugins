# Repository Pattern

## BaseRepository with Generics (Python 3.12+)

```python
"""Base repository with generic CRUD operations."""

from typing import Generic, TypeVar
from collections.abc import Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


ModelT = TypeVar("ModelT")
CreateDTOT = TypeVar("CreateDTOT", bound=BaseModel)
ReadDTOT = TypeVar("ReadDTOT", bound=BaseModel)


class BaseRepository(Generic[ModelT, CreateDTOT, ReadDTOT]):
    """
    Base repository providing common CRUD operations.

    Type parameters:
        ModelT: SQLAlchemy model class
        CreateDTOT: Pydantic model for creation
        ReadDTOT: Pydantic model for reading

    Example:
        class UserRepository(BaseRepository[User, UserCreateDTO, UserReadDTO]):
            def __init__(self, session: AsyncSession) -> None:
                super().__init__(session, User)
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ReadDTOT]:
        """Get all entities with pagination."""
        result = await self._session.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_by_id(self, id: int) -> ModelT | None:
        """Get entity by ID."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()

    async def save(self, data: ModelT | CreateDTOT) -> ModelT:
        """Save entity (create or update)."""
        if isinstance(data, self._model):
            entity = data
        else:
            entity = self._model(**data.model_dump())

        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, id: int, data: BaseModel) -> ModelT | None:
        """Update entity by ID."""
        entity = await self.get_by_id(id)
        if entity is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        result = await self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        return result.rowcount > 0

    async def exists(self, id: int) -> bool:
        """Check if entity exists."""
        result = await self._session.execute(
            select(self._model.id).where(self._model.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        """Count all entities."""
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count()).select_from(self._model)
        )
        return result.scalar_one()
```

## Concrete Repository

```python
"""User repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositories import BaseRepository
from .models import User
from .dto import UserCreateDTO, UserReadDTO


class UserRepository(BaseRepository[User, UserCreateDTO, UserReadDTO]):
    """Repository for user operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self) -> Sequence[User]:
        """Get all active users."""
        result = await self._session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[User]:
        """Search users by name or email."""
        result = await self._session.execute(
            select(User)
            .where(
                (User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
            )
            .limit(limit)
        )
        return result.scalars().all()

    async def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        from datetime import datetime

        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
```

## Repository with Relationships

```python
"""Order repository with eager loading."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from .models import Order, OrderItem


class OrderRepository(BaseRepository[Order, OrderCreateDTO, OrderReadDTO]):
    """Repository for order operations."""

    async def get_with_items(self, order_id: int) -> Order | None:
        """Get order with items (eager loaded)."""
        result = await self._session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_with_user(self, order_id: int) -> Order | None:
        """Get order with user (eager loaded)."""
        result = await self._session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(joinedload(Order.user))
        )
        return result.unique().scalar_one_or_none()

    async def get_user_orders(
        self,
        user_id: int,
        status: str | None = None,
    ) -> Sequence[Order]:
        """Get all orders for user."""
        query = select(Order).where(Order.user_id == user_id)

        if status:
            query = query.where(Order.status == status)

        query = query.options(selectinload(Order.items))
        result = await self._session.execute(query)
        return result.scalars().all()
```

## Unit of Work Pattern

```python
"""Unit of Work pattern for transactions."""

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """Unit of Work for managing transactions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = UserRepository(session)
        self.orders = OrderRepository(session)
        self.order_items = OrderItemRepository(session)

    async def commit(self) -> None:
        """Commit transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self._session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()


# Usage
async def create_order_with_items(
    uow: UnitOfWork,
    order_data: OrderCreateDTO,
) -> Order:
    async with uow:
        order = await uow.orders.save(order_data)

        for item_data in order_data.items:
            item = OrderItem(order_id=order.id, **item_data.model_dump())
            await uow.order_items.save(item)

        return order
```

## Soft Delete

```python
"""Repository with soft delete support."""

from datetime import datetime
from sqlalchemy import select, update


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    async def soft_delete(self, id: int) -> bool:
        """Soft delete entity by setting deleted_at."""
        result = await self._session.execute(
            update(self._model)
            .where(self._model.id == id)
            .where(self._model.deleted_at.is_(None))
            .values(deleted_at=datetime.utcnow())
        )
        return result.rowcount > 0

    async def restore(self, id: int) -> bool:
        """Restore soft-deleted entity."""
        result = await self._session.execute(
            update(self._model)
            .where(self._model.id == id)
            .where(self._model.deleted_at.is_not(None))
            .values(deleted_at=None)
        )
        return result.rowcount > 0

    async def get_all_with_deleted(self) -> Sequence:
        """Get all entities including soft-deleted."""
        result = await self._session.execute(select(self._model))
        return result.scalars().all()


class UserRepository(BaseRepository, SoftDeleteMixin):
    """User repository with soft delete."""

    async def get_all(self) -> Sequence[User]:
        """Get all non-deleted users."""
        result = await self._session.execute(
            select(User).where(User.deleted_at.is_(None))
        )
        return result.scalars().all()
```
