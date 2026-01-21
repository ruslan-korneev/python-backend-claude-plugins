# Python Backend Plugins for Claude Code

A curated collection of Claude Code plugins for Python backend development with FastAPI, SQLAlchemy 2.0, and modern tooling.

## Available Plugins

| Plugin | Description | Key Commands |
|--------|-------------|--------------|
| [**ruff-lint**](plugins/ruff-lint/) | Linting with ruff (ZERO noqa policy) | `/lint:check`, `/lint:explain`, `/lint:config` |
| [**pytest-assistant**](plugins/pytest-assistant/) | TDD testing patterns | `/test:first`, `/test:fixture`, `/test:mock` |
| [**fastapi-scaffold**](plugins/fastapi-scaffold/) | FastAPI boilerplate generation | `/fastapi:module`, `/fastapi:dto`, `/fastapi:endpoint` |
| [**python-typing**](plugins/python-typing/) | Type annotations (ZERO type:ignore) | `/types:check`, `/types:explain` |
| [**docker-backend**](plugins/docker-backend/) | Docker for development | `/docker:run`, `/docker:file` |
| [**alembic-migrations**](plugins/alembic-migrations/) | Database migrations with enum handling | `/migrate:create`, `/migrate:check` |
| [**clean-code**](plugins/clean-code/) | SOLID principles & code smells | `/clean:review`, `/clean:refactor` |

## Installation

### From GitHub (recommended)

Inside Claude Code, run these slash commands:

```
# Add this marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install individual plugins
/plugin install ruff-lint@python-backend-plugins
/plugin install pytest-assistant@python-backend-plugins

# Or install all plugins at once
/plugin install ruff-lint pytest-assistant fastapi-scaffold python-typing docker-backend alembic-migrations clean-code@python-backend-plugins
```

### From local clone

```bash
git clone https://github.com/ruslan-korneev/python-backend-claude-plugins.git
cd python-backend-claude-plugins
```

Then inside Claude Code:

```
# Add local marketplace
/plugin marketplace add ./

# Install plugins
/plugin install ruff-lint@python-backend-plugins
```

## Core Principles

These plugins enforce best practices for Python backend development:

- **ZERO noqa / ZERO type:ignore** — Always fix properly, never suppress warnings
- **TDD (Test-Driven Development)** — Write tests first, then implementation
- **docker run first** — Use simple `docker run` before docker-compose
- **TypedDict > dict[str, Any]** — Strict dictionary typing with TypedDict
- **Real test database** — Never mock the database in tests
- **Branch coverage** — More important than line coverage

## Plugin Structure

Each plugin follows a consistent structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/
│   └── *.md                 # Slash commands
├── skills/
│   └── skill-name/
│       ├── SKILL.md         # Main skill entry point
│       └── references/
│           └── *.md         # Detailed documentation
├── agents/                  # (optional) Specialized agents
│   └── *.md
├── hooks/                   # (optional) Automation hooks
│   └── hooks.json
└── README.md
```

## Usage Examples

### Linting with ruff

```
/lint:check src/
/lint:explain E501
/lint:config fastapi
```

### TDD Testing

```
/test:first UserService.create
/test:fixture async_session
/test:mock external_api
```

### FastAPI Scaffolding

```
/fastapi:module users
/fastapi:dto User
/fastapi:endpoint GET /users/{id}
```

### Type Checking

```
/types:check src/
/types:explain "Argument of type X is not assignable to parameter of type Y"
```

### Docker

```
/docker:run postgres
/docker:file fastapi
```

### Database Migrations

```
/migrate:create add_user_status
/migrate:check
```

### Code Review

```
/clean:review src/services/
/clean:refactor extract_method
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new plugins
- Improving existing plugins
- Submitting bug reports

## License

MIT License - see [LICENSE](LICENSE) for details.

## Security

For security concerns, see [SECURITY.md](SECURITY.md).
