# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is This

A collection of Claude Code plugins for Python backend development (FastAPI + SQLAlchemy 2.0 + uv).

## Plugin Architecture

Each plugin is an independent directory with the following structure:
```
plugin-name/
├── .claude-plugin/plugin.json   # Manifest
├── commands/*.md                # Slash commands
├── skills/*/SKILL.md            # Contextual knowledge
├── skills/*/references/*.md     # Detailed documentation
├── agents/*.md                  # Agents (optional)
├── hooks/hooks.json             # Hooks (optional)
└── README.md
```

## Plugins

| Plugin | Purpose | Key Commands |
|--------|---------|--------------|
| **ruff-lint** | Linting (ZERO noqa) | `/lint:check`, `/lint:explain` |
| **pytest-assistant** | TDD testing | `/test:first`, `/test:fixture` |
| **fastapi-scaffold** | Boilerplate generation | `/fastapi:module`, `/fastapi:dto` |
| **python-typing** | Type annotations (ZERO type:ignore) | `/types:check`, `/types:explain` |
| **docker-backend** | Docker (docker run first) | `/docker:run`, `/docker:file` |
| **alembic-migrations** | Migrations (enum handling) | `/migrate:create`, `/migrate:check` |
| **clean-code** | SOLID, code smells | `/clean:review`, `/clean:refactor` |

## Principles

- **ZERO noqa / ZERO type:ignore** — always fix properly, never suppress
- **TDD** — test first, then implementation
- **docker run first** — docker-compose only on explicit request
- **TypedDict > dict[str, Any]** — strict dictionary typing
- **Real test database** — never mock the database
- **Branch coverage** — more important than line coverage

## Plugin Activation

Inside Claude Code, run these slash commands:

```
# Add marketplace (from GitHub)
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Or add local marketplace (for development)
/plugin marketplace add ./

# Install plugin
/plugin install {plugin-name}@python-backend-plugins
```

## Plugin Development

When modifying a plugin:
1. SKILL.md — main entry point, activation triggers
2. references/*.md — detailed documentation by topic
3. commands/*.md — frontmatter with `name`, `description`, `allowed_tools`, `arguments`
4. hooks.json — PostToolUse for automation after Edit/Write
