# Docker Patterns

Docker patterns for backend development. **docker run first** — docker-compose only on explicit request.

## Triggers

Use this skill when the user:
- Wants to start a service (PostgreSQL, Redis, etc.)
- Creates a Dockerfile
- Asks about Docker for development

## Main principle: docker run first

Always ask the user:
1. **Existing service?** — connect to an already running one
2. **docker run?** — recommended for a single service
3. **docker-compose?** — only if explicitly requested

## Quick start services

### PostgreSQL

```bash
docker run -d --name postgres-dev \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=app_db \
  -p 5432:5432 -v postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine
```

### Redis

```bash
docker run -d --name redis-dev \
  -p 6379:6379 -v redis-data:/data \
  redis:7-alpine redis-server --appendonly yes
```

### MongoDB

```bash
docker run -d --name mongo-dev \
  -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 -v mongo-data:/data/db \
  mongo:7
```

### RabbitMQ

```bash
docker run -d --name rabbitmq-dev \
  -e RABBITMQ_DEFAULT_USER=app -e RABBITMQ_DEFAULT_PASS=secret \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3-management-alpine
```

## Dockerfile Best Practices

### Multi-stage build

```dockerfile
# Build stage
FROM python:3.12-slim as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src/ src/
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim as runtime
RUN useradd --uid 1000 --create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src/ src/
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Non-root user

```dockerfile
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app
USER app
```

### Health check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Layer caching

```dockerfile
# First dependencies (rarely change)
COPY pyproject.toml uv.lock ./
RUN uv sync

# Then code (changes frequently)
COPY src/ src/
```

## Container management

```bash
# Status
docker ps -a

# Logs
docker logs -f container-name

# Shell
docker exec -it container-name /bin/bash

# Stop/Start
docker stop container-name
docker start container-name

# Remove
docker rm -f container-name
docker volume rm volume-name
```

## Plugin commands

- `/docker:run <service>` — docker run command for a service
- `/docker:file [type]` — create a Dockerfile
