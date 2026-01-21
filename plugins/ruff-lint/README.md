# ruff-lint

Plugin for seamless integration of [ruff](https://docs.astral.sh/ruff/) into the Claude Code workflow.

## Philosophy

**ZERO noqa policy** — the plugin never suggests ignoring linter errors. Every ruff error has a proper solution, and the plugin helps you find it.

## Features

- **Auto-formatting** — after editing Python files, `ruff format` and `ruff check --fix` are automatically run
- **Code checking** — `/lint:check` command for project analysis
- **Error explanation** — `/lint:explain` command shows how to fix errors properly (not noqa!)
- **Project configuration** — `/lint:config` command with presets for FastAPI

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install ruff-lint@python-backend-plugins
```

## Commands

### `/lint:check [path]`

Checks code for linting errors.

```
/lint:check
/lint:check src/
/lint:check src/services/user.py
```

Groups errors by category and shows a fix strategy.

### `/lint:explain <error>`

Explains the error and shows the **proper solution** (not noqa!).

```
/lint:explain E501
/lint:explain F401
/lint:explain src/main.py:15
```

### `/lint:config [preset]`

Configures ruff for the project.

```
/lint:config           # FastAPI preset (default)
/lint:config minimal   # Minimal rule set
/lint:config strict    # Strict rules
```

## Automatic Hook

After each `Edit` or `Write` of a Python file, the following is automatically run:
- `ruff format` — formatting
- `ruff check --fix --unsafe-fixes` — auto-fixing

## Plugin Structure

```
ruff-lint/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/
│   ├── check.md             # /lint:check
│   ├── explain.md           # /lint:explain
│   └── config.md            # /lint:config
├── hooks/
│   └── hooks.json           # PostToolUse hook
├── skills/
│   └── ruff-patterns/
│       ├── SKILL.md         # Main skill
│       ├── references/
│       │   ├── rule-solutions.md      # Solutions for rules
│       │   ├── recommended-config.md  # Recommended configs
│       │   └── why-no-noqa.md         # Why not noqa
│       └── examples/
│           └── fastapi-pyproject.toml # Config example
└── README.md
```

## Why Not noqa?

`# noqa` is not a solution, it's ignoring the problem:

1. **Hiding real problems** — the code remains bad
2. **Technical debt** — noqa comments multiply
3. **Masking bugs** — a real bug may be hidden behind noqa

Proper alternatives:
- Fix the code
- Configure `per-file-ignores` for specific files (tests, migrations)
- Disable the rule globally if it doesn't fit the project

## Recommended Configuration for FastAPI

```toml
[tool.ruff]
target-version = "py312"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "ANN101", "ANN102", "FBT003", "PLR0913", "S101", "COM812", "ISC001"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004"]
"alembic/versions/*.py" = ["ALL"]
"__init__.py" = ["F401"]
"src/*/routers.py" = ["B008"]
```

## Links

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Ruff Configuration](https://docs.astral.sh/ruff/configuration/)
