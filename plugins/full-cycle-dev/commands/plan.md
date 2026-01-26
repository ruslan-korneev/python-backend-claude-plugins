---
name: dev:plan
description: Create a development plan without execution. Plan is saved for later execution with /dev:execute.
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Task
arguments:
  - name: prompt
    description: Feature description (what to build)
    required: true
  - name: module
    description: Target module hint (optional)
    required: false
---

# Plan-Only Command

Create a development plan without executing it. Useful for:
- Reviewing plans before implementation
- Creating plans for team discussion
- Breaking down complex features
- Preparing work for later sessions

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                     /dev:plan "{prompt}"                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: EXPLORE                                                │
│ Agent: codebase-explorer (sonnet)                               │
│ Find relevant modules and patterns                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PLAN                                                   │
│ Agent: planning-agent (opus)                                    │
│ Create detailed plan with test cases                            │
│ Ask clarifying questions                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT: Plan saved to .claude/plans/dev-{slug}.md               │
│ Status: draft                                                   │
│ Ready for: /dev:execute or manual review                        │
└─────────────────────────────────────────────────────────────────┘
```

## Execution Instructions

### Step 1: Create Plans Directory

Ensure the plans directory exists:

```bash
mkdir -p .claude/plans
```

### Step 2: Launch Codebase Explorer

```
Task(
  subagent_type="codebase-explorer",
  prompt="""
    Feature request: ${prompt}
    Module hint: ${module}

    Find relevant modules and patterns for planning.
  """,
  model="sonnet"
)
```

### Step 3: Launch Planning Agent

```
Task(
  subagent_type="planning-agent",
  prompt="""
    Feature request: ${prompt}

    Codebase analysis:
    {explorer_output}

    Create a development plan and save it to:
    .claude/plans/dev-{slug}.md

    Include:
    - Summary and key decisions
    - Affected files table
    - Ordered test cases (TDD)
    - Implementation steps
    - Memory anchors

    Set status: draft
  """,
  model="opus"
)
```

### Step 4: Report Plan Location

After plan creation, inform the user:

```markdown
## Plan Created

📄 **Location**: `.claude/plans/dev-{slug}.md`

### Summary
{plan summary}

### Test Cases
{list of test cases}

### Next Steps
1. Review the plan at the location above
2. Make any desired changes
3. Execute with: `/dev:execute .claude/plans/dev-{slug}.md`

Or continue with full cycle: `/dev:cycle "{prompt}"`
```

## Usage Examples

### Basic usage
```
/dev:plan "Add user avatar upload"
```

### With module hint
```
/dev:plan "Add order history endpoint" --module=orders
```

### Complex feature
```
/dev:plan "Implement real-time notifications with WebSocket"
```

## Plan Structure

The created plan includes:

```markdown
---
id: dev-{uuid}
feature: {feature-name}
status: draft
created: {timestamp}
---

# Development Plan: {Feature}

## Summary
{One sentence goal}

## Key Decisions
- Decision 1: {rationale}

## Affected Files
| File | Action | Purpose |

## Test Cases (TDD Order)
1. [ ] test_happy_path
2. [ ] test_validation
3. [ ] test_edge_case

## Implementation Steps
1. Step 1
2. Step 2

## Memory Anchors
> TASK: ...
> APPROACH: ...
> CONSTRAINTS: ...
```

## Manual Plan Editing

After creation, you can:
1. Edit the plan file directly
2. Add/remove test cases
3. Modify implementation steps
4. Update memory anchors

Then execute with `/dev:execute`.
