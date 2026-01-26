# The Code Review Pyramid

## Philosophy

The Code Review Pyramid is a mental model for prioritizing what to focus on during code review. Like a food pyramid, the base is most important.

```
                    ▲
                   /|\
                  / | \         CODE STYLE
                 /  |  \        • Formatting
                /   |   \       • Naming (minor)
               /____|____\      • Comments
              /     |     \
             /      |      \    TESTS
            /       |       \   • Coverage
           /        |        \  • Test quality
          /_________|_________\ • Edge cases
         /          |          \
        /           |           \  DOCUMENTATION
       /            |            \ • Docstrings
      /             |             \• README
     /______________|______________\
    /               |               \
   /                |                \  IMPLEMENTATION SEMANTICS
  /                 |                 \ • Correctness
 /                  |                  \• Performance
/                   |                   \• Security
\___________________│___________________/
                    |
                    |                      API SEMANTICS
                    |                      • Contracts
                    |                      • Breaking changes
                    |                      • Naming (major)
                    ▼
```

## Levels Explained

### Level 1: API Semantics (CRITICAL)

**What**: The public interface — how other code interacts with this code.

**Why it's critical**:
- Hardest to change later (breaking changes)
- Affects all consumers
- Mistakes propagate widely

**Review focus**:
- Is the API minimal yet sufficient?
- Single way to accomplish each task?
- Follows Principle of Least Surprise?
- Consistent with existing codebase patterns?
- No breaking changes (or justified)?

**Examples**:
- REST endpoint contracts (URL, methods, request/response)
- Function signatures
- Class interfaces
- Module exports

### Level 2: Implementation Semantics (HIGH)

**What**: The actual logic — does it work correctly?

**Why it's high priority**:
- Bugs here cause runtime failures
- Security vulnerabilities often hide here
- Performance issues manifest here

**Review focus**:
- Does it match the requirements?
- All edge cases handled?
- Error paths covered?
- No race conditions?
- No performance footguns?
- No security vulnerabilities?

**Examples**:
- Business logic correctness
- Database query efficiency
- Concurrency handling
- Input validation

### Level 3: Documentation (MEDIUM)

**What**: Explanations for humans — comments, docstrings, README.

**Why it's medium priority**:
- Important for maintainability
- But wrong code with docs is worse than right code without

**Review focus**:
- Public APIs documented?
- Complex logic explained?
- README updated for user-facing changes?
- Docs accurate (not lying)?

### Level 4: Tests (MEDIUM)

**What**: Automated verification of behavior.

**Why it's medium priority**:
- Critical for long-term maintainability
- But tests of wrong code don't help

**Review focus**:
- New code has tests?
- Tests verify behavior, not implementation?
- Edge cases covered?
- Good unit/integration balance?

### Level 5: Code Style (NIT)

**What**: Formatting, naming conventions, code organization.

**Why it's lowest priority**:
- Mostly automatable (linters, formatters)
- Subjective disagreements common
- Easy to bikeshed here

**Review focus**:
- Only what linters missed
- Inconsistency with codebase patterns
- Genuinely confusing naming

**Always prefix with "Nit:"** — author can ignore.

## Anti-Patterns

### ❌ Style-Heavy Reviews
```
"Line 42 could use better variable name"
"Add blank line here"
"This comment has a typo"
```
...while missing a SQL injection vulnerability.

### ❌ Missing the Forest for Trees
Nitpicking style while the entire approach is flawed.

### ❌ Blocking on Nits
Refusing to approve because of minor style issues.

## The Right Approach

### ✅ Priority-Based Review
1. First pass: API changes — any breaking changes?
2. Second pass: Implementation — does it work correctly?
3. Third pass: Tests — is new code tested?
4. Fourth pass: Docs — is it documented?
5. Final pass: Style — anything the linter missed?

### ✅ Categorized Feedback
```markdown
## Critical (Must Fix)
- SQL injection vulnerability in user input handling

## High Priority (Should Fix)
- Race condition in concurrent order processing

## Medium (Recommended)
- Add docstring for public method

## Nit (Optional)
- Consider renaming `x` to `user_count`
```

### ✅ Proportional Effort
Spend 80% of review time on the bottom two levels (API + Implementation).

## Quick Reference

| Level | Priority | Automatable? | Block PR? |
|-------|----------|--------------|-----------|
| API Semantics | Critical | No | Yes |
| Implementation | High | Partial | Yes |
| Documentation | Medium | No | Maybe |
| Tests | Medium | Partial | Maybe |
| Code Style | Nit | Yes | No |
