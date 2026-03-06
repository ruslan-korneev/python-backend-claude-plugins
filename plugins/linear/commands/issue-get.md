---
name: "linear:get"
description: Get details of a Linear issue
allowed_tools:
  - Bash
  - Read
  - Grep
arguments:
  - name: id
    description: "Issue identifier (e.g., TEAM-123) or part of issue title to search"
    required: true
---

# Command /linear:get

Show full details of a Linear issue.

## Instructions

### Step 0: Validate Configuration

Check `LINEAR_API_KEY` is set. Show setup instructions if missing.

### Step 1: Determine Lookup Method

Parse the `id` argument:
- If it matches pattern `[A-Z]+-[0-9]+` (e.g., TEAM-123): extract team key and number, use `issues` query with filter `{ team: { key: { eq: "TEAM" } }, number: { eq: 123 } }`
- Otherwise: treat as search text, use `searchIssues` query

### Step 2: Fetch Issue

For identifier lookup, use the `issue` query from [graphql-queries.md](../skills/linear-api/references/graphql-queries.md) with team key + number filter. Request all fields including comments.

For text search, use `searchIssues` query (parameter `term`, not `query`). If multiple results, show a selection list and ask the user to pick one.

### Step 3: Display Result

```markdown
## TEAM-123: Issue Title

| Field | Value |
|-------|-------|
| Status | In Progress |
| Priority | High (2) |
| Assignee | John Doe |
| Project | backend-api |
| Cycle | Sprint 42 |
| Estimate | 3 points |
| Due Date | 2026-03-15 |
| Labels | bug, backend |
| Created | 2026-03-01 |
| Updated | 2026-03-05 |
| URL | https://linear.app/... |

### Description

Issue description text here...

### Comments (2)

**John Doe** (2026-03-03):
> First comment text

**Jane Smith** (2026-03-05):
> Second comment text
```
