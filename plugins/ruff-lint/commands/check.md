---
name: ruff:check
description: Run ruff check to analyze code for linting errors
allowed_tools:
  - Bash
  - Read
  - Glob
arguments:
  - name: path
    description: Path to file or directory to check (defaults to current directory)
    required: false
---

# Command /lint:check

Run Python code analysis using ruff.

## Instructions

1. Run `ruff check` for the specified path (or current directory if no path is specified):
   ```bash
   ruff check {{ path | default: "." }} --output-format=grouped
   ```

2. Analyze the result and group errors by category:
   - **Style errors** (E, W): formatting, whitespace, line length
   - **Potential bugs** (F): unused imports, variables, syntax errors
   - **Code complexity** (C): cognitive complexity, nesting
   - **Security** (S): potential vulnerabilities
   - **Library-specific** (B, UP, etc.)

3. For each error group:
   - Show the error count
   - Provide examples with line numbers
   - Suggest a fix strategy

4. **IMPORTANT: NEVER suggest `# noqa` as a solution!**
   - Every ruff error has a proper solution
   - If the user asks about a specific error, use `/lint:explain`

## Output Format

```
## Ruff Check Results

### Errors found: X

#### Style errors (E/W): N
- E501: Lines too long (5 files)
- W291: Trailing whitespace (2 files)

#### Potential bugs (F): N
- F401: Unused imports (3 files)
- F841: Unused variables (1 file)

### Auto-fixable
Run `ruff check --fix` to automatically fix X errors.

### Require manual fix
- E501 in src/services/user.py:45 - split into multiple lines
- ...
```

## Additional Flags

If the user wants more detailed output:
- `--statistics` - show statistics by rules
- `--show-fixes` - show which fixes can be applied automatically
