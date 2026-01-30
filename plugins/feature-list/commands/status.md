---
name: feature-list:status
description: Show implementation status by phase
allowed_tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Command /feature-list:status

Display the implementation status of all features grouped by phase.

## Instructions

### Step 1: Find All Feature Files

Use `Glob` to find feature files:

```
docs/technical-requirements/features/*.md
```

Exclude `README.md` and `00-template.md`.

### Step 2: Parse Each Feature

For each file, extract from YAML frontmatter:
- `id`
- `title`
- `status` (draft | in_progress | completed)
- `phase`
- `priority`

### Step 3: Calculate Statistics

Group features by phase and status:

```python
stats = {
    "core": {"completed": 0, "in_progress": 0, "draft": 0},
    "workflow": {"completed": 0, "in_progress": 0, "draft": 0},
    # ...
}

for feature in features:
    stats[feature.phase][feature.status] += 1
```

Calculate totals and percentages:

```python
total = len(features)
completed = sum(1 for f in features if f.status == "completed")
completion_rate = (completed / total * 100) if total > 0 else 0
```

### Step 4: Generate Report

#### Summary Table

```markdown
## Feature Implementation Status

### Summary

| Phase | Total | ✅ Completed | 🔄 In Progress | 📝 Draft | Progress |
|-------|-------|--------------|----------------|----------|----------|
| Core | 4 | 2 | 1 | 1 | 50% |
| Workflow | 2 | 0 | 1 | 1 | 0% |
| Integration | 3 | 3 | 0 | 0 | 100% |
| **Total** | **9** | **5** | **2** | **2** | **56%** |
```

#### Detailed by Phase

```markdown
### Core Features

| ID | Feature | Status | Priority |
|----|---------|--------|----------|
| core-01 | User Management | ✅ Completed | Critical |
| core-02 | Product Catalog | ✅ Completed | High |
| core-03 | Inventory | 🔄 In Progress | Medium |
| core-04 | Categories | 📝 Draft | Low |

### Workflow Features

| ID | Feature | Status | Priority |
|----|---------|--------|----------|
| workflow-01 | Checkout | 🔄 In Progress | Critical |
| workflow-02 | Returns | 📝 Draft | Medium |
```

#### Progress Bar (ASCII)

```markdown
### Overall Progress

[████████████░░░░░░░░] 56% (5/9 features completed)
```

### Step 5: Optional Code Status Check

If detailed status is requested, check actual code:

Use `Grep` to find implementations:

```
# Check if model exists
Grep: class {ModelName}

# Check if tests pass
Bash: pytest tests/{module}/ -q --tb=no
```

Infer status:
- No code files → `draft`
- Code exists, tests fail → `in_progress`
- Code + tests pass → `completed`

## Response Format

```markdown
## Feature Status Report

Generated: {date}

### Overview

```
Total Features: 9
├── Completed:   5 (56%)
├── In Progress: 2 (22%)
└── Draft:       2 (22%)

[████████████░░░░░░░░] 56%
```

### By Phase

#### Core (4 features)

| Status | ID | Feature | Priority |
|--------|-----|---------|----------|
| ✅ | core-01 | User Management | Critical |
| ✅ | core-02 | Product Catalog | High |
| 🔄 | core-03 | Inventory | Medium |
| 📝 | core-04 | Categories | Low |

Progress: ██████████░░░░░░░░░░ 50%

#### Workflow (2 features)

| Status | ID | Feature | Priority |
|--------|-----|---------|----------|
| 🔄 | workflow-01 | Checkout | Critical |
| 📝 | workflow-02 | Returns | Medium |

Progress: ░░░░░░░░░░░░░░░░░░░░ 0%

#### Integration (3 features)

| Status | ID | Feature | Priority |
|--------|-----|---------|----------|
| ✅ | integration-01 | Email Service | High |
| ✅ | integration-02 | Payment Gateway | Critical |
| ✅ | integration-03 | Storage | Medium |

Progress: ████████████████████ 100%

### Critical Path

Features blocking others:

1. **core-01** (User Management) — Blocks: workflow-01, workflow-02
2. **integration-02** (Payment Gateway) — Blocks: workflow-01

### Recommendations

1. Complete `core-03` (Inventory) to unblock product features
2. Start `workflow-01` (Checkout) — critical for MVP
3. Consider deprioritizing `core-04` (Categories) — low priority
```

## Format Options

The `format` argument supports:

| Value | Output |
|-------|--------|
| `summary` | Just the summary table |
| `detailed` | Full report with all features |
| `json` | JSON output for tooling |
| `markdown` (default) | Full markdown report |

### JSON Output Example

```json
{
  "generated": "2026-01-28",
  "summary": {
    "total": 9,
    "completed": 5,
    "in_progress": 2,
    "draft": 2,
    "completion_rate": 0.56
  },
  "by_phase": {
    "core": {
      "total": 4,
      "completed": 2,
      "features": [...]
    }
  }
}
```
