# Code Review Plugin

Efficient code review following the **Review Pyramid** methodology for Python/FastAPI projects.

## Features

- **Two-phase review strategy**: Quick automated checks + deep semantic analysis
- **Review Pyramid prioritization**: API > Implementation > Docs > Tests > Style
- **Task context support**: Verify implementation matches requirements
- **Python/FastAPI specialization**: SQLAlchemy 2.0, Pydantic, async patterns

## Quick Start

```bash
# Review staged changes
/review:diff

# Review branch before merge
/review:diff main

# Review with task context (recommended!)
/review:diff main --task="Add PUT /users/{id}/profile with email validation"
```

## Commands

| Command | Description |
|---------|-------------|
| `/review:diff [target]` | Review code changes |

### Arguments

- **target**: What to review
  - `staged` (default) — Staged changes only
  - `HEAD~N` — Last N commits
  - `branch_name` — Current branch vs target
  - `commit..commit` — Commit range

- **task**: Business requirements (optional, recommended)
- **mode**: `quick` / `deep` / `full` (default)

## The Review Pyramid

```
         ▲
        /|\        Code Style (Nit)
       / | \       Tests
      /  |  \      Documentation
     /   |   \     Implementation Semantics
    /    |    \    API Semantics (Critical)
   /_____|_____\
```

Review from bottom to top — API and implementation issues are far more important than style.

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `quick-reviewer` | sonnet | Automated checks: linting, types, security patterns |
| `code-reviewer` | opus | Deep analysis: API semantics, implementation, tests |

## Documentation

See `skills/code-review/references/` for detailed checklists:
- `pyramid.md` — Review Pyramid methodology
- `api-semantics.md` — API contract review
- `implementation.md` — Logic and correctness
- `security.md` — OWASP Top 10 for Python
- `testing.md` — Test quality guidelines
