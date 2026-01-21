---
name: module
description: Create a complete FastAPI module (routers, services, repositories, dto, models + tests)
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: name
    description: "Module name (e.g.: users, orders, products)"
    required: true
  - name: fields
    description: "Model fields in 'name:type' format separated by comma (e.g.: email:str,age:int,is_active:bool)"
    required: false
---

# Command /fastapi:module

Create a complete FastAPI module with best practices.

## Module Structure

```
src/modules/{name}/
├── __init__.py
├── models.py       # SQLAlchemy model
├── dto.py          # Pydantic DTOs (Create, Read, Update)
├── repositories.py # Repository with generics
├── services.py     # Business logic
└── routers.py      # FastAPI endpoints

tests/modules/{name}/
├── __init__.py
├── conftest.py     # Module fixtures
├── test_services.py
└── test_routers.py
```

## Instructions

### Step 1: Create directories

```bash
mkdir -p src/modules/{{ name }}
mkdir -p tests/modules/{{ name }}
```

### Step 2: Create module files

#### models.py

```python
"""{{ name | capitalize }} models."""

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class {{ name | capitalize }}(Base):
    """{{ name | capitalize }} model."""

    __tablename__ = "{{ name }}"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Add fields based on {{ fields }}

    def __repr__(self) -> str:
        return f"<{{ name | capitalize }}(id={self.id})>"
```

#### dto.py

```python
"""{{ name | capitalize }} DTOs."""

from pydantic import BaseModel, ConfigDict


class {{ name | capitalize }}BaseDTO(BaseModel):
    """Base DTO with common fields."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Common fields
    pass


class {{ name | capitalize }}CreateDTO({{ name | capitalize }}BaseDTO):
    """DTO for creating {{ name }}."""

    # Fields for creation (without id)
    pass


class {{ name | capitalize }}ReadDTO({{ name | capitalize }}BaseDTO):
    """DTO for reading {{ name }}."""

    id: int
    # All fields for reading


class {{ name | capitalize }}UpdateDTO(BaseModel):
    """DTO for updating {{ name }}."""

    model_config = ConfigDict(from_attributes=True)

    # Optional fields for update
    pass
```

#### repositories.py

```python
"""{{ name | capitalize }} repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositories import BaseRepository
from .models import {{ name | capitalize }}
from .dto import {{ name | capitalize }}CreateDTO, {{ name | capitalize }}ReadDTO


class {{ name | capitalize }}Repository(
    BaseRepository[{{ name | capitalize }}, {{ name | capitalize }}CreateDTO, {{ name | capitalize }}ReadDTO]
):
    """Repository for {{ name }} operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, {{ name | capitalize }})

    async def get_by_id(self, id: int) -> {{ name | capitalize }}ReadDTO | None:
        """Get {{ name }} by ID."""
        result = await self._session.execute(
            select({{ name | capitalize }}).where({{ name | capitalize }}.id == id)
        )
        entity = result.scalar_one_or_none()
        return {{ name | capitalize }}ReadDTO.model_validate(entity) if entity else None

    # Add specific methods
```

#### services.py

```python
"""{{ name | capitalize }} service."""

from src.core.exceptions import NotFoundError, ConflictError
from .repositories import {{ name | capitalize }}Repository
from .dto import {{ name | capitalize }}CreateDTO, {{ name | capitalize }}ReadDTO, {{ name | capitalize }}UpdateDTO


class {{ name | capitalize }}Service:
    """Service for {{ name }} business logic."""

    def __init__(self, repository: {{ name | capitalize }}Repository) -> None:
        self._repository = repository

    async def create(self, data: {{ name | capitalize }}CreateDTO) -> {{ name | capitalize }}ReadDTO:
        """Create new {{ name }}."""
        return await self._repository.save(data)

    async def get_by_id(self, id: int) -> {{ name | capitalize }}ReadDTO:
        """Get {{ name }} by ID."""
        result = await self._repository.get_by_id(id)
        if result is None:
            raise NotFoundError(f"{{ name | capitalize }} with id {id} not found")
        return result

    async def get_all(self) -> list[{{ name | capitalize }}ReadDTO]:
        """Get all {{ name }}s."""
        return list(await self._repository.get_all())

    async def update(self, id: int, data: {{ name | capitalize }}UpdateDTO) -> {{ name | capitalize }}ReadDTO:
        """Update {{ name }}."""
        existing = await self.get_by_id(id)  # Raises NotFoundError if not exists
        return await self._repository.update(id, data)

    async def delete(self, id: int) -> None:
        """Delete {{ name }}."""
        await self.get_by_id(id)  # Raises NotFoundError if not exists
        await self._repository.delete(id)
```

#### routers.py

```python
"""{{ name | capitalize }} API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from src.core.container import Container
from .dto import {{ name | capitalize }}CreateDTO, {{ name | capitalize }}ReadDTO, {{ name | capitalize }}UpdateDTO
from .services import {{ name | capitalize }}Service


router = APIRouter(prefix="/{{ name }}", tags=["{{ name }}"])


@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_{{ name }}(
    data: {{ name | capitalize }}CreateDTO,
    service: Annotated[
        {{ name | capitalize }}Service,
        Depends(Provide[Container.{{ name }}_service]),
    ],
) -> {{ name | capitalize }}ReadDTO:
    """Create new {{ name }}."""
    return await service.create(data)


@router.get("/{id}")
@inject
async def get_{{ name }}(
    id: int,
    service: Annotated[
        {{ name | capitalize }}Service,
        Depends(Provide[Container.{{ name }}_service]),
    ],
) -> {{ name | capitalize }}ReadDTO:
    """Get {{ name }} by ID."""
    return await service.get_by_id(id)


@router.get("")
@inject
async def get_all_{{ name }}s(
    service: Annotated[
        {{ name | capitalize }}Service,
        Depends(Provide[Container.{{ name }}_service]),
    ],
) -> list[{{ name | capitalize }}ReadDTO]:
    """Get all {{ name }}s."""
    return await service.get_all()


@router.patch("/{id}")
@inject
async def update_{{ name }}(
    id: int,
    data: {{ name | capitalize }}UpdateDTO,
    service: Annotated[
        {{ name | capitalize }}Service,
        Depends(Provide[Container.{{ name }}_service]),
    ],
) -> {{ name | capitalize }}ReadDTO:
    """Update {{ name }}."""
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_{{ name }}(
    id: int,
    service: Annotated[
        {{ name | capitalize }}Service,
        Depends(Provide[Container.{{ name }}_service]),
    ],
) -> None:
    """Delete {{ name }}."""
    await service.delete(id)
```

### Step 3: Create tests

#### tests/modules/{{ name }}/conftest.py

```python
"""{{ name | capitalize }} test fixtures."""

import pytest
from unittest.mock import AsyncMock

from src.modules.{{ name }}.services import {{ name | capitalize }}Service
from src.modules.{{ name }}.repositories import {{ name | capitalize }}Repository


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mock {{ name }} repository."""
    return AsyncMock(spec={{ name | capitalize }}Repository)


@pytest.fixture
def service(mock_repository: AsyncMock) -> {{ name | capitalize }}Service:
    """{{ name | capitalize }} service with mocked repository."""
    return {{ name | capitalize }}Service(repository=mock_repository)
```

#### tests/modules/{{ name }}/test_services.py

```python
"""{{ name | capitalize }} service tests."""

import pytest
from unittest.mock import AsyncMock

from src.core.exceptions import NotFoundError
from src.modules.{{ name }}.services import {{ name | capitalize }}Service
from src.modules.{{ name }}.dto import {{ name | capitalize }}CreateDTO, {{ name | capitalize }}ReadDTO


class Test{{ name | capitalize }}Service:
    """Tests for {{ name | capitalize }}Service."""

    async def test_create_success(
        self,
        service: {{ name | capitalize }}Service,
        mock_repository: AsyncMock,
    ) -> None:
        """Successfully create {{ name }}."""
        # Arrange
        create_data = {{ name | capitalize }}CreateDTO(...)  # Fill in fields
        mock_repository.save.return_value = {{ name | capitalize }}ReadDTO(id=1, ...)

        # Act
        result = await service.create(create_data)

        # Assert
        assert result.id == 1
        mock_repository.save.assert_called_once()

    async def test_get_by_id_not_found_raises_error(
        self,
        service: {{ name | capitalize }}Service,
        mock_repository: AsyncMock,
    ) -> None:
        """Get non-existent {{ name }} raises NotFoundError."""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_by_id(999)
```

### Step 4: Update DI container

Add to `src/core/container.py`:

```python
from src.modules.{{ name }}.repositories import {{ name | capitalize }}Repository
from src.modules.{{ name }}.services import {{ name | capitalize }}Service

class Container(containers.DeclarativeContainer):
    # ... existing providers ...

    {{ name }}_repository = providers.Factory(
        {{ name | capitalize }}Repository,
        session=session_maker,
    )

    {{ name }}_service = providers.Factory(
        {{ name | capitalize }}Service,
        repository={{ name }}_repository,
    )
```

### Step 5: Connect router

Add to `src/main.py`:

```python
from src.modules.{{ name }}.routers import router as {{ name }}_router

app.include_router({{ name }}_router, prefix="/api/v1")
```

## Response Format

```
## Module created: {{ name }}

### Structure
```
src/modules/{{ name }}/
├── __init__.py
├── models.py
├── dto.py
├── repositories.py
├── services.py
└── routers.py

tests/modules/{{ name }}/
├── conftest.py
├── test_services.py
└── test_routers.py
```

### Next Steps
1. Update `src/core/container.py` — add providers
2. Connect router in `src/main.py`
3. Create migration: `alembic revision --autogenerate -m "add {{ name }}"`
4. Run tests: `pytest tests/modules/{{ name }}/ -v`
```
