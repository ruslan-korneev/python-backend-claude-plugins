# Changelog

All notable changes to the plugins in this repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and each plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [ruff-lint]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/lint:check`, `/lint:explain`, `/lint:config`
- ZERO noqa policy enforcement
- Recommended configurations for FastAPI, minimal, strict, monorepo

---

## [pytest-assistant]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/test:first`, `/test:fixture`, `/test:mock`
- TDD-first approach
- Real database testing patterns

---

## [fastapi-scaffold]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/fastapi:module`, `/fastapi:dto`, `/fastapi:endpoint`
- Repository pattern, DI, DTOs templates

---

## [python-typing]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/types:check`, `/types:explain`
- ZERO type:ignore policy
- TypedDict over dict[str, Any]

---

## [docker-backend]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/docker:run`, `/docker:file`
- docker run first philosophy
- Multi-stage Dockerfile templates

---

## [alembic-migrations]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/migrate:create`, `/migrate:check`
- Automatic enum handling in downgrade
- Migration reviewer agent

---

## [clean-code]

### [1.0.0] - 2026-01-21
- Initial release
- Commands: `/clean:review`, `/clean:refactor`
- SOLID principles
- Code smells detection
