---
name: architect:design
description: Interactive architecture design for new project or module
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
arguments:
  - name: name
    description: "Project or module name (e.g.: my-api, users-service)"
    required: true
---

# Command /architect:design

Interactive architecture design workflow for new projects or major features.

## Instructions

### Step 1: Gather Requirements

Use `AskUserQuestion` to understand the project scope:

**Questions to ask:**
1. What is the primary purpose of this system?
2. What are the main use cases / user stories?
3. Expected scale (users, requests/sec, data volume)?
4. What external systems need integration (databases, APIs, queues)?
5. Any specific constraints (tech stack, compliance, team expertise)?

### Step 2: Analyze Existing Codebase (if applicable)

If this is a new module in existing project:
- Check existing structure with `Glob`
- Identify patterns already in use
- Ensure consistency with existing modules

### Step 3: Choose Architecture Style

Based on requirements, recommend one of:

| Style | When to Use |
|-------|-------------|
| **Modular Monolith** | Small team (<10), uncertain requirements, MVP |
| **Microservices** | Large team, independent scaling needs, different tech stacks |
| **Event-Driven** | Real-time processing, loose coupling between modules |
| **Layered (Clean/Hexagonal)** | Complex business logic, long-term maintainability |

### Step 4: Design Module Structure

For FastAPI + SQLAlchemy projects, propose structure:

```
src/
├── core/
│   ├── __init__.py
│   ├── config.py           # Settings with pydantic-settings
│   ├── database.py         # AsyncSession setup
│   ├── container.py        # DI container
│   ├── dependencies.py     # FastAPI dependencies
│   ├── exceptions.py       # Base exceptions
│   └── repositories.py     # BaseRepository
│
├── modules/
│   └── {{ name }}/
│       ├── __init__.py     # Public API exports
│       ├── models.py       # SQLAlchemy models
│       ├── dto.py          # Pydantic DTOs
│       ├── repositories.py # Data access layer
│       ├── services.py     # Business logic
│       ├── routers.py      # HTTP endpoints
│       └── events.py       # Domain events (if needed)
│
├── shared/
│   ├── protocols.py        # Shared interfaces
│   └── events.py           # Event bus
│
└── main.py                  # FastAPI app entry point
```

### Step 5: Define Module Boundaries

Identify modules and their responsibilities:

```markdown
## Modules

### users
- **Responsibility**: User management, authentication
- **Owns**: users, refresh_tokens tables
- **Dependencies**: none
- **Exposes**: UserService, get_current_user dependency

### orders
- **Responsibility**: Order lifecycle management
- **Owns**: orders, order_items tables
- **Dependencies**: users (via UserServiceProtocol)
- **Exposes**: OrderService, OrderCreated event

### payments
- **Responsibility**: Payment processing
- **Owns**: payments, transactions tables
- **Dependencies**: orders (via events)
- **Exposes**: PaymentService
```

### Step 6: Generate Scaffold (Optional)

Ask user if they want to generate initial files:

```bash
mkdir -p src/{core,modules/{{ name }},shared}
mkdir -p tests/modules/{{ name }}
```

Create `config.py`:
```python
"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "{{ name }}"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/{{ name }}"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


settings = Settings()
```

Create `database.py`:
```python
"""Database configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


async def get_session() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        yield session
```

Create `exceptions.py`:
```python
"""Application exceptions."""


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An internal error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found."""

    status_code = 404
    error_code = "not_found"
    message = "Resource not found"


class ConflictError(AppError):
    """Resource already exists."""

    status_code = 409
    error_code = "conflict"
    message = "Resource already exists"


class ValidationError(AppError):
    """Validation failed."""

    status_code = 422
    error_code = "validation_error"
    message = "Validation failed"


class UnauthorizedError(AppError):
    """Not authenticated."""

    status_code = 401
    error_code = "unauthorized"
    message = "Not authenticated"


class ForbiddenError(AppError):
    """Not authorized."""

    status_code = 403
    error_code = "forbidden"
    message = "Not authorized"
```

### Step 7: Create Initial ADR

Document the architectural decisions:

```markdown
# ADR-001: Architecture for {{ name }}

## Status
Accepted

## Date
{{ today }}

## Context
{{ context_from_requirements }}

## Decision
{{ chosen_architecture }}

## Consequences
### Positive
{{ benefits }}

### Negative
{{ drawbacks }}

## Alternatives Considered
{{ alternatives }}
```

## Response Format

```markdown
## Architecture Design: {{ name }}

### Requirements Summary
- **Purpose**: {{ purpose }}
- **Scale**: {{ scale }}
- **Integrations**: {{ integrations }}

### Recommended Architecture
**Style**: {{ style }} (e.g., Modular Monolith)

**Rationale**: {{ rationale }}

### Module Structure
```
{{ proposed_structure }}
```

### Module Boundaries
| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| {{ module1 }} | {{ responsibility1 }} | {{ deps1 }} |
| {{ module2 }} | {{ responsibility2 }} | {{ deps2 }} |

### Data Model Overview
```mermaid
erDiagram
    {{ er_diagram }}
```

### Next Steps
1. Review and approve architecture
2. Generate scaffold: `/architect:design {{ name }} --scaffold`
3. Create ADR: `/architect:adr "Architecture for {{ name }}"`
4. Start implementation with first module

### Files Created
- `src/core/config.py`
- `src/core/database.py`
- `src/core/exceptions.py`
- `docs/adr/001-architecture.md`
```
