# docker-backend

Plugin for working with Docker in backend development. **docker run first** — docker-compose only on explicit request.

## Philosophy

- Simplicity: `docker run` for a single service
- Ask user about preferences
- docker-compose only when really needed

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install docker-backend@python-backend-plugins
```

## Commands

### `/docker:run <service>`

Generates a `docker run` command for a service.

```
/docker:run postgres
/docker:run redis
/docker:run mongodb
/docker:run rabbitmq
```

Supported services:
- PostgreSQL
- Redis
- MongoDB
- RabbitMQ
- Kafka
- Elasticsearch
- MinIO

### `/docker:file [type]`

Creates an optimal Dockerfile.

```
/docker:file           # FastAPI (default)
/docker:file celery    # Celery worker
/docker:file script    # One-time script
```

## Examples

### PostgreSQL

```bash
docker run -d --name postgres-dev \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=app_db \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16-alpine
```

### Dockerfile (FastAPI + uv)

```dockerfile
FROM python:3.12-slim as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY src/ src/
RUN uv sync --frozen --no-dev

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

## Structure

```
docker-backend/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── run.md
│   └── file.md
├── skills/
│   └── docker-patterns/
│       └── SKILL.md
└── README.md
```
