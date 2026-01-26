# Plugin Integration

This document describes how full-cycle-dev integrates with other plugins in the ecosystem.

## Integration Matrix

| Phase | Plugin | Command/Skill | Purpose |
|-------|--------|---------------|---------|
| **Explore** | — | codebase-explorer agent | Find relevant modules |
| **Plan** | software-architect | `/architect:design` | Architecture decisions |
| **Red** | pytest-assistant | `/test:first` | Create failing tests |
| **Green** | — | Direct implementation | Make tests pass |
| **Refactor** | clean-code | `/clean:review` | Detect code smells |
| **Quality** | ruff-lint | PostToolUse hooks | Auto-format on save |
| **Quality** | python-typing | PostToolUse hooks | Type checking |
| **Docs** | — | Plan file update | Document completion |

## Plugin Invocation

### pytest-assistant (Red Phase)

```
Skill: pytest-assistant:first
Purpose: Create a failing test BEFORE implementation
```

The execution agent calls this for each test case in the plan:

```markdown
## Test Cases (TDD Order)
1. [ ] test_upload_avatar_success
```

Becomes:

```python
# tests/users/test_avatar.py
def test_upload_avatar_success(client, user):
    """Test successful avatar upload."""
    response = client.post(
        f"/users/{user.id}/avatar",
        files={"file": ("avatar.png", b"...", "image/png")}
    )
    assert response.status_code == 200
    assert response.json()["avatar_url"] is not None
```

### clean-code (Refactor Phase)

```
Skill: clean-code:review
Purpose: Analyze code for SOLID violations and code smells
```

After Green phase, review implementation:

```markdown
## Code Review Results
- ✅ Single Responsibility: OK
- ⚠️ Consider extracting validation logic
- ✅ No code duplication detected
```

### ruff-lint (Quality Gates)

Hooks automatically trigger on file save:

```json
{
  "event": "PostToolUse",
  "tools": ["Edit", "Write"],
  "command": "ruff check --fix ${file} && ruff format ${file}"
}
```

### python-typing (Quality Gates)

Type checking runs automatically:

```json
{
  "event": "PostToolUse",
  "tools": ["Edit", "Write"],
  "command": "mypy ${file} --ignore-missing-imports"
}
```

## Workflow Integration

### Complete TDD Cycle

```
For each test_case in plan.test_cases:

    # RED: Create failing test
    Skill("pytest-assistant:first", feature=test_case)
    Bash("pytest {test_file} -x")  # Verify it fails

    # GREEN: Implement
    # Write minimal code to pass
    Bash("pytest {test_file} -x")  # Verify it passes

    # REFACTOR: Improve
    Skill("clean-code:review", path=implementation_file)
    # Apply suggestions

    # QUALITY: Auto-checks via hooks
    # ruff-lint and python-typing run automatically

    # Update plan
    Mark test_case as [x] completed
```

### Final Quality Gates

Before marking feature complete:

```bash
# Run full test suite
pytest tests/ -v --cov

# Full lint check
ruff check src/ tests/

# Full type check
mypy src/ --strict

# All must pass for completion
```

## Error Recovery

### Plugin Not Installed

If a required plugin is missing:

```markdown
⚠️ Plugin pytest-assistant not found.
Falling back to manual test creation.
```

The execution agent will:
1. Log warning in plan file
2. Create tests manually using pytest patterns
3. Continue with workflow

### Hook Failures

If ruff or mypy hooks fail:

1. Agent receives error output
2. Fixes the issue immediately
3. Continues with workflow

This maintains the "ZERO noqa / ZERO type:ignore" principle.

## Recommended Plugin Set

For full functionality, install these plugins:

```bash
/plugin install pytest-assistant@python-backend-plugins
/plugin install clean-code@python-backend-plugins
/plugin install ruff-lint@python-backend-plugins
/plugin install python-typing@python-backend-plugins
/plugin install software-architect@python-backend-plugins
```

The full-cycle-dev plugin will work without them, but with reduced automation.
