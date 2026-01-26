# Code Review Skill

This skill should be used when the user asks for "code review", "review my changes", "review this PR", "check my code", "pre-merge review", "review diff", or mentions reviewing code quality, implementation correctness, or preparing changes for merge.

## Overview

Code review following the **Review Pyramid** methodology — a prioritized approach that focuses on what matters most.

## The Review Pyramid

```
         ▲
        /|\         5. Code Style (Nit) ← Least important, automatable
       / | \
      /  |  \       4. Tests
     /   |   \
    /    |    \     3. Documentation
   /     |     \
  /      |      \   2. Implementation Semantics ← High priority
 /       |       \
/________|________\ 1. API Semantics ← Most critical, review first
```

**Key insight**: Review from bottom to top. API and implementation issues are far more important than style issues.

## Two-Phase Review Strategy

### Phase 1: Quick Review (Automated Checks)
Fast first pass using `quick-reviewer` agent (sonnet):
- Linting (ruff check)
- Type checking (mypy)
- Security pattern scanning
- Test file existence

### Phase 2: Deep Review (Human-Like Analysis)
Thorough analysis using `code-reviewer` agent (opus):
- API semantics (breaking changes, naming, contracts)
- Implementation correctness (business logic, edge cases)
- Security (detailed analysis)
- Documentation completeness
- Test quality

## When to Use

| Trigger | Action |
|---------|--------|
| "Review my staged changes" | `/review:diff staged` |
| "Review before I merge" | `/review:diff main --mode=full` |
| "Quick check my code" | `/review:diff --mode=quick` |
| "Deep review this feature" | `/review:diff main --task="..." --mode=deep` |

## Best Practices

1. **Always provide task context** with `--task` flag for accurate business logic review
2. **Run quick review first** to catch obvious issues
3. **Review branch against target** before merging
4. **Fix critical issues first** — API/Implementation > Style

## References

- `pyramid.md` — Detailed explanation of the Review Pyramid
- `api-semantics.md` — API review checklist
- `implementation.md` — Implementation review checklist
- `security.md` — Security review checklist
- `testing.md` — Test review checklist
