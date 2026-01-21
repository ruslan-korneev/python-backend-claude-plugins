---
name: check
description: Run mypy/pyright for type checking
allowed_tools:
  - Bash
  - Read
  - Glob
arguments:
  - name: path
    description: Path to file or directory (default src/)
    required: false
  - name: tool
    description: "Tool: mypy (default), pyright"
    required: false
---

# Command /types:check

Run type checking and show errors with explanations.

## Instructions

### Step 1: Determine the tool

Check for configuration:
```bash
# mypy
test -f pyproject.toml && grep -q "tool.mypy" pyproject.toml && echo "mypy configured"

# pyright
test -f pyrightconfig.json && echo "pyright configured"
```

### Step 2: Run the check

```bash
# mypy
mypy {{ path | default: "src/" }} --show-error-codes

# pyright
pyright {{ path | default: "src/" }}
```

### Step 3: Group errors

Error categories:
- **Missing return type** — no return type annotation
- **Incompatible types** — incompatible types in assignment/call
- **Missing type annotation** — no annotation for variable
- **Optional handling** — working with Optional without None check
- **Generics** — errors with generic types

### Step 4: Show solutions

For each error show:
1. What the error means
2. How to fix it WITHOUT `type: ignore`

## NEVER SUGGEST

```python
# NEVER:
result = some_function()  # type: ignore
value: Any = something  # Avoid Any
cast(SomeType, value)  # Only if there's no other way
```

## Response Format

```
## Type Checking Results

### Tool: mypy
### Path: {{ path }}

### Errors found: X

#### Missing return type (N)
- `src/services/user.py:45` — `def process()` → add `-> None` or specific type

#### Incompatible types (N)
- `src/repositories/order.py:23` — `str` vs `int` → convert types explicitly

#### Optional handling (N)
- `src/api/routes.py:67` — possible `None` → add check `if value is not None`

### How to Fix

1. Add return type annotations to functions without them
2. Use `if x is not None` instead of `cast` or `type: ignore`
3. Replace `Any` with specific types or `TypeVar`
```
