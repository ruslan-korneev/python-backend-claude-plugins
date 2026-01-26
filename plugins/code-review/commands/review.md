---
name: review:diff
description: "Review code changes using the Review Pyramid methodology"
arguments:
  - name: target
    description: "What to review: staged (default), HEAD~N, commit..commit, or branch_name"
    required: false
    default: "staged"
  - name: task
    description: "Business requirements being implemented (highly recommended for accurate review)"
    required: false
  - name: mode
    description: "Review mode: quick (fast checks only), deep (thorough analysis), full (both)"
    required: false
    default: "full"
allowed_tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Task
---

# Code Review Command

Review code changes following the **Code Review Pyramid** methodology.

## Arguments

- **target**: What to review
  - `staged` (default) — Only staged changes (`git diff --cached`)
  - `HEAD~N` — Last N commits (`git diff HEAD~N`)
  - `commit..commit` — Range of commits (`git diff abc..def`)
  - `branch_name` — Current branch vs specified branch (`git diff branch...HEAD`)

- **task**: Business requirements description (optional but recommended)
  - Enables verification that implementation matches requirements
  - Allows checking if all use cases are covered
  - Without this, review is limited to technical aspects only

- **mode**: Review depth
  - `quick` — Only automated checks (linting, types, security patterns)
  - `deep` — Only thorough code analysis
  - `full` (default) — Quick first, then deep if passed

## Usage Examples

```bash
# Review staged changes
/review:diff

# Review last 2 commits
/review:diff HEAD~2

# Review current branch against main before merge
/review:diff main

# Review with task context (RECOMMENDED!)
/review:diff development --task="Add PUT /users/{id}/profile endpoint with email validation and role change protection"

# Quick check only (faster)
/review:diff --mode=quick

# Deep review only (skip automated checks)
/review:diff main --mode=deep
```

## Workflow

### Step 1: Gather Context

Determine the diff command based on target:

```bash
# For staged changes
git diff --cached

# For HEAD~N
git diff HEAD~N

# For branch comparison (current vs target)
git diff {target}...HEAD

# For commit range
git diff {start}..{end}
```

Get the diff and list of changed files:
```bash
git diff {appropriate_flags} --name-only  # List of files
git diff {appropriate_flags}               # Full diff
```

### Step 2: Categorize Files

Group changed files by layer:
- **API layer**: `*/api.py`, `*/routes.py`, `*/endpoints.py`
- **Service layer**: `*/service*.py`, `*/use_case*.py`
- **Repository layer**: `*/repository*.py`, `*/repo*.py`
- **Models**: `*/models.py`, `*/entities.py`
- **DTOs**: `*/dto*.py`, `*/schemas.py`
- **Tests**: `tests/**/*.py`
- **Config**: `*.toml`, `*.yaml`, `*.json`, `*.env*`
- **Migrations**: `*/versions/*.py`, `alembic/*`

### Step 3: Execute Review Based on Mode

#### Mode: quick
Run only the `quick-reviewer` agent:
```
Use Task tool with subagent_type: "code-review:quick-reviewer"
Provide: git diff, list of changed files
```

#### Mode: deep
Run only the `code-reviewer` agent:
```
Use Task tool with subagent_type: "code-review:code-reviewer"
Provide: git diff, list of changed files, task description (if provided)
```

#### Mode: full (default)
1. Run `quick-reviewer` first
2. If "Ready for deep review: Yes" → run `code-reviewer`
3. If "Ready for deep review: No" → report blockers and stop

### Step 4: Present Results

Combine results into final report following the output format from the agents.

## Important Notes

1. **Always get the actual diff first** before spawning review agents
2. **Pass task description** to code-reviewer if provided
3. **Respect the pyramid** — critical issues (API/Implementation) are more important than style
4. **Be constructive** — every issue should have a suggestion for fixing

## Task Context Importance

Without `--task`:
```
⚠️ Task description not provided.
Business logic verification limited to technical correctness.
Cannot verify:
- Requirements compliance
- Use case coverage
- Business rule correctness
```

With `--task`:
```
✅ Full review including:
- Requirements compliance check
- Use case coverage analysis
- Business logic verification
```

**Always encourage providing task context for accurate reviews!**
