# Context Handoff Between Agents

This document describes how context flows between agents in the full-cycle workflow.

## Agent Pipeline

```
┌──────────────────┐
│  User Prompt     │
│  + Module Hint   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────────────┐
│ Codebase         │────▶│ Context Output:             │
│ Explorer         │     │ - Project structure         │
│ (sonnet)         │     │ - Relevant file paths       │
└──────────────────┘     │ - Module relationships      │
                         └─────────────┬───────────────┘
                                       │
                                       ▼
┌──────────────────┐     ┌─────────────────────────────┐
│ Planning         │────▶│ Context Output:             │
│ Agent            │     │ - Development plan          │
│ (opus)           │     │ - Test cases                │
└──────────────────┘     │ - Memory anchors            │
                         └─────────────┬───────────────┘
                                       │
                                       ▼
┌──────────────────┐     ┌─────────────────────────────┐
│ Execution        │────▶│ Context Output:             │
│ Agent            │     │ - Implemented code          │
│ (opus)           │     │ - Passing tests             │
└──────────────────┘     │ - Updated plan status       │
                         └─────────────────────────────┘
```

## Context Format

### From Codebase Explorer

```markdown
## Codebase Analysis

### Project Structure
- Framework: FastAPI
- ORM: SQLAlchemy 2.0
- Testing: pytest

### Relevant Modules

| Path | Role | Relevance |
|------|------|-----------|
| `src/users/` | User management | High - contains User model |
| `src/storage/` | File storage | High - S3 integration |
| `tests/users/` | User tests | Medium - test patterns |

### Key Patterns Found
- Repository pattern in `src/core/repository.py`
- DTO validation with Pydantic
- Dependency injection via FastAPI Depends
```

### From Planning Agent

The planning agent outputs a complete development plan (see [Plan Format](plan-format.md)).

Key context elements:
- **Memory Anchors** — Persist across sessions
- **Test Cases** — Ordered list for TDD execution
- **Affected Files** — What to create/modify

### To Execution Agent

The execution agent receives:

1. **Plan file path** — `.claude/plans/dev-{slug}.md`
2. **User approval** — Via EnterPlanMode confirmation
3. **Full codebase access** — All tools available

## Memory Anchor Usage

Memory anchors provide persistent context:

```markdown
> TASK: Add user avatar upload with S3 storage
> APPROACH: Direct upload to S3 with presigned URLs
> CONSTRAINTS: Max 5MB, JPEG/PNG only
```

Agents reference these anchors when:
- Making implementation decisions
- Validating approach consistency
- Resuming interrupted work

## Resuming Interrupted Work

If a session is interrupted:

1. Read plan file from `.claude/plans/`
2. Check `status` field in frontmatter
3. Find unchecked test cases `[ ]`
4. Resume from last incomplete step

```markdown
## Test Cases (TDD Order)

1. [x] `test_happy_path` — ✅ Completed
2. [x] `test_validation` — ✅ Completed
3. [ ] `test_edge_case` — ⏳ Resume here
4. [ ] `test_integration` — Pending
```

## Error Handling

If an agent fails:

1. **Codebase Explorer fails**: Ask user to specify module manually
2. **Planning Agent fails**: Save partial plan, allow manual editing
3. **Execution Agent fails**: Mark test case as blocked, continue with next

All errors are logged in the plan file under `## Execution Log`.
