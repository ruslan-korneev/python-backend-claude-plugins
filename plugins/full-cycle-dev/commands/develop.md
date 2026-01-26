---
name: dev:cycle
description: Full TDD development cycle - from prompt to documented feature. Orchestrates exploration, planning, and execution.
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - Task
  - Skill
  - EnterPlanMode
arguments:
  - name: prompt
    description: Feature description (what to build)
    required: true
  - name: module
    description: Target module hint (optional, e.g., "users", "orders")
    required: false
---

# Full Development Cycle Command

This command orchestrates the complete TDD development workflow: explore → plan → execute.

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     /dev:cycle "{prompt}"                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: EXPLORE                                                │
│                                                                 │
│ Agent: codebase-explorer (sonnet - fast)                        │
│ Task: Find relevant modules and understand project structure    │
│                                                                 │
│ Output:                                                         │
│ - Project structure analysis                                    │
│ - Relevant file paths                                           │
│ - Patterns to follow                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PLAN                                                   │
│                                                                 │
│ Agent: planning-agent (opus - deep analysis)                    │
│ Task: Create detailed development plan with test cases          │
│                                                                 │
│ Actions:                                                        │
│ - Deep analysis of relevant files                               │
│ - Ask clarifying questions (AskUserQuestion)                    │
│ - Create plan with Memory Anchors                               │
│ - Save to .claude/plans/dev-{slug}.md                           │
│                                                                 │
│ Output:                                                         │
│ - Development plan file                                         │
│ - Ordered test cases                                            │
│ - Implementation steps                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: APPROVE                                                │
│                                                                 │
│ Action: EnterPlanMode                                           │
│ Task: User reviews and approves the plan                        │
│                                                                 │
│ User sees:                                                      │
│ - Summary of changes                                            │
│ - Files to be created/modified                                  │
│ - Test cases to implement                                       │
│                                                                 │
│ User action: Approve or request changes                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: EXECUTE                                                │
│                                                                 │
│ Agent: execution-agent (opus - full control)                    │
│ Task: Implement using TDD (Red-Green-Refactor)                  │
│                                                                 │
│ For each test case:                                             │
│ 1. RED: Create failing test (pytest-assistant:first)            │
│ 2. GREEN: Write minimal implementation                          │
│ 3. REFACTOR: Improve code (clean-code:review)                   │
│ 4. QUALITY: Verify lint & types pass                            │
│                                                                 │
│ Output:                                                         │
│ - Implemented feature with tests                                │
│ - Updated plan status                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: COMPLETE                                               │
│                                                                 │
│ Final actions:                                                  │
│ - Run full test suite                                           │
│ - Verify all quality gates                                      │
│ - Update plan status to "completed"                             │
│ - Suggest commit message                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Execution Instructions

### Step 1: Launch Codebase Explorer

```
Task(
  subagent_type="codebase-explorer",
  prompt="""
    Feature request: ${prompt}
    Module hint: ${module}

    Analyze the codebase and find:
    1. Project structure
    2. Relevant modules for this feature
    3. Patterns to follow
    4. Files to analyze in detail
  """,
  model="sonnet"
)
```

### Step 2: Launch Planning Agent

```
Task(
  subagent_type="planning-agent",
  prompt="""
    Feature request: ${prompt}

    Codebase analysis:
    {explorer_output}

    Create a development plan:
    1. Analyze relevant files in detail
    2. Ask clarifying questions
    3. Create plan with test cases
    4. Save to .claude/plans/dev-{slug}.md
  """,
  model="opus"
)
```

### Step 3: Enter Plan Mode

After the plan is created, enter plan mode for user approval:

```
EnterPlanMode()
```

Present the plan summary to the user and wait for approval.

### Step 4: Launch Execution Agent

After approval:

```
Task(
  subagent_type="execution-agent",
  prompt="""
    Execute the development plan at: .claude/plans/dev-{slug}.md

    Follow TDD cycle for each test case:
    1. RED: Create failing test
    2. GREEN: Make it pass
    3. REFACTOR: Improve quality

    Use plugins:
    - pytest-assistant:first for tests
    - clean-code:review for refactoring

    Update plan status as you progress.
  """,
  model="opus"
)
```

### Step 5: Final Verification

After execution completes:

1. Run full test suite: `pytest tests/ -v`
2. Run lint check: `ruff check src/ tests/`
3. Run type check: `mypy src/`
4. Update plan status to "completed"
5. Suggest commit message based on changes

## Usage Examples

### Basic usage
```
/dev:cycle "Add user avatar upload with S3 storage"
```

### With module hint
```
/dev:cycle "Add password reset functionality" --module=auth
```

### Complex feature
```
/dev:cycle "Implement order checkout with payment processing and email notifications"
```

## Plan File Location

Plans are saved to: `.claude/plans/dev-{feature-slug}.md`

The slug is generated from the feature name:
- "Add user avatar upload" → `dev-add-user-avatar-upload.md`

## Interruption Recovery

If the process is interrupted:
1. Plan file remains at `.claude/plans/`
2. Use `/dev:execute .claude/plans/dev-{slug}.md` to resume
3. Execution agent will continue from last uncompleted test case

## Related Commands

- `/dev:plan` — Only create a plan, don't execute
- `/dev:execute` — Execute an existing plan
