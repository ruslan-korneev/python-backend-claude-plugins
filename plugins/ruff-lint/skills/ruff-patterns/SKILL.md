# Ruff Patterns

Knowledge about the ruff linter and patterns for solving errors. **ZERO noqa policy** — always look for the proper solution.

## Triggers

Use this skill when the user:
- Asks "how to configure ruff"
- Gets a ruff error and wants to understand how to fix it
- Wants to migrate from black/isort/flake8/pylint
- Asks about a specific rule (E501, F401, etc.)

## Main Principle: NEVER USE NOQA

**Every ruff error has a proper solution.** Using `# noqa` is:
- Hiding the problem, not solving it
- Technical debt
- A potential source of bugs

Instead of noqa:
1. Fix the code properly
2. Configure per-file-ignores for specific cases (tests, migrations)
3. Disable the rule globally if it doesn't fit the project

More details: `${CLAUDE_PLUGIN_ROOT}/skills/ruff-patterns/references/why-no-noqa.md`

## Quick Start

### Installation
```bash
uv add ruff --dev
```

### Basic Usage
```bash
# Check
ruff check .

# Format
ruff format .

# Auto-fix safe errors
ruff check --fix .

# Auto-fix all errors (including potentially unsafe)
ruff check --fix --unsafe-fixes .
```

## Recommended Configuration

### For FastAPI Projects
```toml
[tool.ruff]
target-version = "py312"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D",       # docstrings
    "ANN101",  # self annotation
    "ANN102",  # cls annotation
    "FBT003",  # boolean positional arg
    "PLR0913", # too many arguments
    "S101",    # assert (allowed in tests via per-file-ignores)
    "COM812",  # trailing comma conflict
    "ISC001",  # implicit string concat conflict
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004"]
"alembic/versions/*.py" = ["ALL"]
"__init__.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"
```

Full example: `${CLAUDE_PLUGIN_ROOT}/skills/ruff-patterns/examples/fastapi-pyproject.toml`

## Solutions for Popular Errors

Detailed solution database: `${CLAUDE_PLUGIN_ROOT}/skills/ruff-patterns/references/rule-solutions.md`

### Quick Reference

| Code | Problem | Solution |
|------|---------|----------|
| E501 | Line too long | Use parentheses for line breaks |
| F401 | Unused import | Remove or add to `__all__` |
| F841 | Unused variable | Use `_` or remove |
| B008 | Function call in default | `None` + check |
| PLR0913 | Too many arguments | Dataclass/Pydantic model |
| S101 | Assert in code | Explicit check + raise |
| UP007 | Outdated Union | Use `X \| Y` |

## Migration from Other Linters

### From black + isort + flake8

Ruff completely replaces these tools:
- `ruff format` = black
- `ruff check --select I` = isort
- `ruff check` = flake8 + plugins

```bash
# Remove old dependencies
uv remove black isort flake8 flake8-bugbear flake8-comprehensions

# Add ruff
uv add ruff --dev

# Remove old configs
rm .flake8 .isort.cfg
# Remove [tool.black], [tool.isort] sections from pyproject.toml
```

### From pylint

Ruff covers most pylint rules through PL* groups:
- PLC: Convention
- PLE: Error
- PLR: Refactor
- PLW: Warning

## CI/CD Integration

### GitHub Actions
```yaml
- name: Lint with ruff
  run: |
    ruff check --output-format=github .
    ruff format --check .
```

### Pre-commit
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Plugin Commands

- `/lint:check [path]` — check code
- `/lint:explain <error>` — error explanation + solution
- `/lint:config [preset]` — configure ruff for the project
