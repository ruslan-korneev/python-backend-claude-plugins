---
name: dev:execute
description: Execute an existing development plan using TDD. Resumes from last incomplete test case.
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Skill
arguments:
  - name: plan_path
    description: Path to plan file (e.g., .claude/plans/dev-avatar.md)
    required: true
---

# Execute Plan Command

Execute an existing development plan using TDD methodology. Supports resuming interrupted work.

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│               /dev:execute ".claude/plans/dev-{slug}.md"        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: LOAD PLAN                                              │
│                                                                 │
│ - Read plan file                                                │
│ - Parse test cases                                              │
│ - Find first uncompleted [  ] test case                         │
│ - Load memory anchors for context                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: TDD EXECUTION                                          │
│                                                                 │
│ For each uncompleted test case:                                 │
│                                                                 │
│ ┌─────────┐    ┌─────────┐    ┌───────────┐                    │
│ │   RED   │───▶│  GREEN  │───▶│ REFACTOR  │                    │
│ │ Failing │    │  Pass   │    │  Quality  │                    │
│ │  Test   │    │  Test   │    │   Check   │                    │
│ └─────────┘    └─────────┘    └───────────┘                    │
│                                                                 │
│ Plugins used:                                                   │
│ - pytest-assistant:first (RED)                                  │
│ - clean-code:review (REFACTOR)                                  │
│ - ruff-lint hooks (auto)                                        │
│ - python-typing hooks (auto)                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: COMPLETION                                             │
│                                                                 │
│ - Run full test suite                                           │
│ - Verify quality gates                                          │
│ - Update plan status to "completed"                             │
│ - Suggest commit message                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Execution Instructions

### Step 1: Load and Validate Plan

Read the plan file and validate structure:

```
Read(file_path="${plan_path}")
```

Validate:
- Plan has frontmatter with `status`
- Plan has `## Test Cases` section
- At least one test case exists

### Step 2: Find Resume Point

Parse test cases and find first uncompleted:

```markdown
## Test Cases (TDD Order)

1. [x] test_happy_path — ✅ Already done
2. [x] test_validation — ✅ Already done
3. [ ] test_edge_case — ⏳ START HERE
4. [ ] test_error_handling — Pending
```

### Step 3: Launch Execution Agent

```
Task(
  subagent_type="execution-agent",
  prompt="""
    Execute the development plan.

    Plan path: ${plan_path}

    Memory Anchors:
    {parsed memory anchors from plan}

    Test cases to implement:
    {list of uncompleted test cases}

    Instructions:
    1. For each test case, follow Red-Green-Refactor
    2. Use pytest-assistant:first for creating tests
    3. Use clean-code:review after each implementation
    4. Update plan file after each completed test
    5. Ensure ZERO noqa and ZERO type:ignore
  """,
  model="opus"
)
```

### Step 4: Final Verification

After all test cases complete:

```bash
# Full test suite
pytest tests/ -v --tb=short

# Lint check
ruff check src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

### Step 5: Update Plan Status

Edit plan frontmatter:

```yaml
---
status: completed
updated: {current timestamp}
---
```

Add final entry to execution log:

```markdown
## Execution Log

| Timestamp | Action | Result |
|-----------|--------|--------|
| ... | ... | ... |
| {now} | All tests complete | ✅ Feature done |
```

### Step 6: Suggest Commit

Based on the plan, suggest a commit message:

```
feat({module}): {feature description}

- Added {list of new files}
- Modified {list of changed files}
- Tests: {number} passing

Closes #{issue if mentioned in plan}
```

## Usage Examples

### Basic usage
```
/dev:execute .claude/plans/dev-add-user-avatar-upload.md
```

### Resume interrupted work
```
# After session restart, simply run again:
/dev:execute .claude/plans/dev-add-user-avatar-upload.md
# Agent will continue from last [  ] test case
```

### List available plans
```bash
ls -la .claude/plans/
```

## Resume Capability

The execution agent automatically resumes from the last incomplete test case:

1. Reads plan file
2. Finds first `[ ]` (unchecked) test case
3. Continues TDD cycle from there
4. Skips already completed `[x]` test cases

This enables:
- Session interruption recovery
- Partial execution
- Step-by-step development

## Error Handling

### Plan file not found
```
❌ Plan file not found: ${plan_path}

Available plans:
{list files in .claude/plans/}

Create a new plan with: /dev:plan "{feature}"
```

### Invalid plan structure
```
❌ Invalid plan structure.

Missing required sections:
- [ ] Frontmatter with status
- [ ] Test Cases section
- [ ] Memory Anchors

Please fix the plan or create a new one.
```

### Test execution failure
```
⚠️ Test case failed after implementation.

Test: test_edge_case
Error: {error message}

Options:
1. Fix implementation and retry
2. Fix test expectations
3. Mark as blocked and continue
```

## Related Commands

- `/dev:cycle` — Full workflow (explore + plan + execute)
- `/dev:plan` — Create plan only
