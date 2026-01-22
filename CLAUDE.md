# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is This

A collection of Claude Code plugins for Python backend development (FastAPI + SQLAlchemy 2.0 + uv).

## Commands

```bash
# Validate all plugins (run before committing)
python .github/scripts/validate_plugins.py

# Add local marketplace for testing
/plugin marketplace add ./

# Install specific plugin
/plugin install {plugin-name}@python-backend-plugins
```

## Repository Structure

```
├── plugins/                     # 7 independent plugins
│   └── {plugin-name}/
│       ├── .claude-plugin/plugin.json
│       ├── commands/*.md
│       ├── skills/*/SKILL.md
│       ├── skills/*/references/*.md
│       ├── agents/*.md          # optional
│       └── hooks/hooks.json     # optional
├── external_plugins/            # Third-party plugins
├── .claude-plugin/
│   └── marketplace.json         # Central plugin catalog
└── .github/scripts/
    └── validate_plugins.py      # CI validation script
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

## Core Principles

- **ZERO noqa / ZERO type:ignore** — always fix properly, never suppress
- **TDD** — test first, then implementation
- **docker run first** — docker-compose only on explicit request
- **TypedDict > dict[str, Any]** — strict dictionary typing
- **Real test database** — never mock the database
- **Branch coverage** — more important than line coverage

## Commit Convention

```bash
# Format: <type>(<plugin>): <description>
feat(ruff-lint): add support for RUF100 rule
fix(pytest-assistant): correct fixture scope handling
docs(fastapi-scaffold): update repository pattern examples
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

## Plugin Development

### Component Responsibilities

1. **SKILL.md** — main entry point, activation triggers (when to use this skill)
2. **references/*.md** — detailed documentation by topic
3. **commands/*.md** — frontmatter with `name`, `description`, `allowed_tools`, `arguments`
4. **hooks.json** — PostToolUse for automation after Edit/Write
5. **agents/*.md** — specialized subagents (e.g., test-reviewer, migration-reviewer)

### Version Locations

When releasing, update version in:
1. `plugins/<plugin>/.claude-plugin/plugin.json` → `version` field
2. `.claude-plugin/marketplace.json` → plugin's `version` field
3. `plugins/<plugin>/CHANGELOG.md` → add release notes

### Testing Changes

```bash
# 1. Run validation
python .github/scripts/validate_plugins.py

# 2. Add local marketplace in Claude Code
/plugin marketplace add ./

# 3. Install and test your plugin
/plugin install {plugin-name}@python-backend-plugins
```
