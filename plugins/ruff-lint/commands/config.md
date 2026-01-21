---
name: ruff:config
description: Configure ruff for the project with FastAPI recommendations
allowed_tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
arguments:
  - name: preset
    description: "Configuration preset: fastapi (default), minimal, strict"
    required: false
---

# Command /lint:config

Configure ruff for the project. The FastAPI preset is used by default.

## Instructions

### Step 1: Check Existing Configuration

```bash
# Check for pyproject.toml
ls pyproject.toml 2>/dev/null || echo "pyproject.toml not found"

# Check for ruff.toml
ls ruff.toml 2>/dev/null || echo "ruff.toml not found"
```

Read the existing file if it exists.

### Step 2: Determine Preset

- **fastapi** (default) - optimized for FastAPI + SQLAlchemy projects
- **minimal** - basic rule set
- **strict** - maximum strictness

### Step 3: Apply Configuration

Add or update the `[tool.ruff]` section in `pyproject.toml`.

## Presets

### FastAPI (recommended)

```toml
[tool.ruff]
target-version = "py312"
line-length = 120
src = ["src"]

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    # Documentation - disabled since code should be self-documenting
    "D",
    # Type annotations for self/cls - redundant
    "ANN101",
    "ANN102",
    # Boolean positional arg - often needed in FastAPI
    "FBT003",
    # Too many arguments - normal for DI
    "PLR0913",
    # Assert in tests - normal
    "S101",
    # Trailing comma / implicit string concat - conflict with formatter
    "COM812",
    "ISC001",
]

[tool.ruff.lint.per-file-ignores]
# Tests - allow assert and magic values
"tests/**/*.py" = ["S101", "PLR2004"]
# Migrations - auto-generated code
"alembic/versions/*.py" = ["ALL"]
# __init__.py - allow unused imports for re-export
"__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["src"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### Minimal

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
]

[tool.ruff.format]
quote-style = "double"
```

### Strict

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "D",      # docstrings - optional
    "ANN101", # self annotation
    "ANN102", # cls annotation
    "COM812", # trailing comma conflict
    "ISC001", # implicit string concat conflict
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]

[tool.ruff.format]
quote-style = "double"
```

## Migration from Other Tools

### From black + isort + flake8

1. Remove from `pyproject.toml`:
   - `[tool.black]`
   - `[tool.isort]`
   - `[tool.flake8]` (if present)

2. Remove files:
   - `.flake8`
   - `setup.cfg` (flake8/isort sections)

3. Remove from dependencies:
   ```bash
   uv remove black isort flake8
   uv add ruff --dev
   ```

### From pylint

Ruff covers most pylint rules. Add:
```toml
[tool.ruff.lint]
select = ["ALL"]  # includes PL* rules (pylint)
```

## Response Format

```
## Ruff Configuration

### Applied preset: {{ preset }}

### Changes to pyproject.toml
[show diff or new section]

### Next Steps
1. Run `ruff check .` to check
2. Run `ruff format .` to format
3. Configure per-file-ignores for specific files if needed
```
