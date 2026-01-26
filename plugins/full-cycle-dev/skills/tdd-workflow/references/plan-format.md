# Development Plan Format

This document describes the structure of development plans created by the planning agent.

## Plan File Location

Plans are saved to: `.claude/plans/dev-{feature-slug}.md`

## Plan Structure

```markdown
---
id: dev-{uuid}
feature: {feature-name}
status: draft | approved | in_progress | completed
created: {ISO-8601 timestamp}
updated: {ISO-8601 timestamp}
---

# Development Plan: {Feature Name}

## Summary

{One sentence describing the end goal}

## Key Decisions

- **Decision 1**: {description and rationale}
- **Decision 2**: {description and rationale}

## Affected Files

| File | Action | Purpose |
|------|--------|---------|
| `path/to/file.py` | create | New service implementation |
| `path/to/test.py` | create | Test cases |
| `path/to/model.py` | modify | Add new field |

## Test Cases (TDD Order)

Tests are ordered by complexity — start with happy path, then edge cases:

1. [ ] `test_happy_path` — Basic functionality works
2. [ ] `test_validation_error` — Invalid input handled
3. [ ] `test_edge_case` — Boundary conditions
4. [ ] `test_integration` — Components work together

## Implementation Steps

1. **Step 1**: {description}
   - Sub-task A
   - Sub-task B

2. **Step 2**: {description}

## Memory Anchors

> TASK: {Clear statement of the end goal}
> APPROACH: {Chosen implementation strategy}
> CONSTRAINTS: {Technical or business constraints}
> DEPENDENCIES: {Required external services or modules}
```

## Status Transitions

```
draft ──▶ approved ──▶ in_progress ──▶ completed
                           │
                           └──▶ blocked (optional)
```

- **draft**: Plan created, awaiting user review
- **approved**: User approved via EnterPlanMode
- **in_progress**: Execution agent is implementing
- **completed**: All test cases pass, feature done
- **blocked**: Implementation blocked by external factor

## Best Practices

### Test Case Ordering

1. **Happy path first** — Validate core functionality
2. **Validation errors** — Input validation
3. **Edge cases** — Boundary conditions
4. **Error handling** — External failures
5. **Integration** — Cross-module behavior

### Key Decisions

Document decisions that affect architecture:

- Database schema choices
- API design decisions
- Dependency choices
- Trade-offs made

### Memory Anchors

Keep anchors concise but complete:

```markdown
> TASK: Add user avatar upload with S3 storage
> APPROACH: Direct upload to S3 with presigned URLs
> CONSTRAINTS: Max 5MB, JPEG/PNG only, no server-side processing
> DEPENDENCIES: boto3, existing User model
```
