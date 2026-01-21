---
name: file
description: Create an optimal Dockerfile (multi-stage, uv)
allowed_tools:
  - Bash
  - Read
  - Write
  - Glob
arguments:
  - name: type
    description: "Type: fastapi (default), celery, script"
    required: false
---

# Command /docker:file

Create an optimal Dockerfile for a Python application.

## Principles

1. **Multi-stage build** — minimal final image
2. **uv** — fast dependency installation
3. **Non-root user** — security
4. **Layer caching** — fast rebuilds
5. **Health checks** — monitoring

## Templates

### FastAPI with uv (recommended)

```dockerfile
# syntax=docker/dockerfile:1.4

# =============================================================================
# Build stage
# =============================================================================
FROM python:3.12-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY src/ src/

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.12-slim as runtime

# Create non-root user
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy source code
COPY --chown=app:app src/ src/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### FastAPI with pip (alternative)

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.12-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-slim as runtime

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Install wheels
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY --chown=app:app src/ src/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER app
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Celery Worker

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.12-slim as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY src/ src/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim as runtime

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src/ src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER app

# Health check via celery inspect
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD celery -A src.celery inspect ping -d celery@$HOSTNAME || exit 1

CMD ["celery", "-A", "src.celery", "worker", "--loglevel=info"]
```

### Development (with hot reload)

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install all dependencies including dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Source mounted as volume
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## .dockerignore

```
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
.venv
venv
.pytest_cache
.mypy_cache
.ruff_cache

# IDE
.idea
.vscode
*.swp
*.swo

# Docker
Dockerfile*
docker-compose*.yml
.docker

# Tests
tests/
.coverage
htmlcov/

# Docs
docs/
*.md
!README.md

# Local config
.env
.env.*
*.local

# Build artifacts
dist/
build/
*.egg-info/
```

## Build & Run

```bash
# Build
docker build -t myapp:latest .

# Run
docker run -d \
  --name myapp \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  myapp:latest

# Logs
docker logs -f myapp

# Shell
docker exec -it myapp /bin/bash
```

## Response format

```
## Created Dockerfile

### Type: {{ type }}

### Features
- Multi-stage build
- uv for fast installation
- Non-root user (app:1000)
- Health check
- Optimized layer caching

### Build
```bash
docker build -t myapp:latest .
```

### Run
```bash
docker run -d --name myapp -p 8000:8000 myapp:latest
```
```
