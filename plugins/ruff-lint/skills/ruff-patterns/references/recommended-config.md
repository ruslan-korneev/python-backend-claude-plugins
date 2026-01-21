# Recommended Ruff Configuration

## For FastAPI Projects (recommended)

```toml
[tool.ruff]
# Target Python version
target-version = "py312"

# Line length — 120 for better readability
line-length = 120

# Source code directories (for proper import sorting)
src = ["src"]

# Excluded directories
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "alembic/versions",
]

[tool.ruff.lint]
# Enable ALL rules and disable unnecessary ones
select = ["ALL"]

ignore = [
    # Documentation — code should be self-documenting
    "D",

    # Annotations for self/cls — redundant
    "ANN101",
    "ANN102",

    # Boolean positional argument — often needed in FastAPI
    "FBT003",

    # Too many arguments — normal for DI with dependency-injector
    "PLR0913",

    # Assert — allowed in tests via per-file-ignores
    "S101",

    # Conflict with formatter
    "COM812",  # Trailing comma
    "ISC001",  # Implicit string concatenation
]

[tool.ruff.lint.per-file-ignores]
# Tests — allow assert and magic values
"tests/**/*.py" = ["S101", "PLR2004", "ARG001"]

# Conftest — fixtures may be unused
"conftest.py" = ["ARG001"]

# Alembic migrations — auto-generated code
"alembic/versions/*.py" = ["ALL"]

# __init__.py — re-export
"__init__.py" = ["F401"]

# FastAPI routers — Depends() in default arguments
"src/*/routers.py" = ["B008"]
"src/**/api/**/*.py" = ["B008"]

[tool.ruff.lint.isort]
# Own packages for proper sorting
known-first-party = ["src"]

# Don't split each import onto a separate line
force-single-line = false

# Two blank lines after imports
lines-after-imports = 2

# Import sections
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]

[tool.ruff.lint.flake8-type-checking]
# Proper handling of TYPE_CHECKING
runtime-evaluated-base-classes = [
    "pydantic.BaseModel",
    "sqlalchemy.orm.DeclarativeBase",
]

[tool.ruff.format]
# Double quotes (like black)
quote-style = "double"

# Spaces for indentation
indent-style = "space"

# Preserve trailing comma
skip-magic-trailing-comma = false

# Auto-detect line ending
line-ending = "auto"

# Docstrings in double quotes
docstring-code-format = true
```

## Minimal Configuration

For small projects or quick start:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]

[tool.ruff.format]
quote-style = "double"
```

## Strict Configuration

For projects with high quality requirements:

```toml
[tool.ruff]
target-version = "py312"
line-length = 88  # Like black default

[tool.ruff.lint]
select = ["ALL"]

ignore = [
    "ANN101",  # self annotation
    "ANN102",  # cls annotation
    "COM812",  # trailing comma conflict
    "ISC001",  # implicit string concat conflict
]

# Minimum exceptions
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]

[tool.ruff.lint.pylint]
# Strict limits
max-args = 5
max-branches = 10
max-returns = 3
max-statements = 30

[tool.ruff.format]
quote-style = "double"
```

## Monorepo Configuration

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

# Multiple code directories
src = ["services/auth/src", "services/api/src", "libs/common/src"]

# Common exclusions
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "**/alembic/versions",
    "**/node_modules",
]

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "ANN101", "ANN102", "COM812", "ISC001"]

[tool.ruff.lint.per-file-ignores]
"**/tests/**/*.py" = ["S101", "PLR2004"]
"**/__init__.py" = ["F401"]
"**/routers.py" = ["B008"]
```

## Integration with Other Tools

### With mypy

```toml
# Ruff doesn't replace mypy — use both
[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.ruff.lint]
select = ["ALL"]
# ANN* rules complement but don't replace mypy
```

### With pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### With GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: "check --output-format=github"
      - uses: astral-sh/ruff-action@v1
        with:
          args: "format --check"
```

## Migration from Other Tools

### From black + isort

```bash
# Remove dependencies
uv remove black isort

# Remove configuration from pyproject.toml
# [tool.black] and [tool.isort] sections

# Add ruff
uv add ruff --dev
```

### From flake8

```bash
# Remove dependencies
uv remove flake8 flake8-bugbear flake8-comprehensions

# Remove .flake8 file
rm .flake8

# Add ruff
uv add ruff --dev
```

Ruff supports most flake8 plugins natively:
- flake8-bugbear -> B
- flake8-comprehensions -> C4
- flake8-simplify -> SIM
- flake8-print -> T20
- and many others
