---
name: "linear:list"
description: List Linear issues with filters
allowed_tools:
  - Bash
  - Read
  - Grep
arguments:
  - name: project
    description: "Filter by project name (default: basename of pwd)"
    required: false
  - name: status
    description: "Filter by status name or type (e.g., 'In Progress', 'started')"
    required: false
  - name: priority
    description: "Filter by priority: urgent, high, medium, low"
    required: false
  - name: assignee
    description: "Filter by assignee name or 'me'"
    required: false
  - name: label
    description: "Filter by label name"
    required: false
  - name: cycle
    description: "Filter by cycle number or 'current'"
    required: false
  - name: sort
    description: "Sort by: priority (default), updated, created"
    required: false
  - name: limit
    description: "Max issues to show (default: 25)"
    required: false
---

# Command /linear:list

List Linear issues with filters. Defaults to current project issues sorted by priority.

## Instructions

### Step 0: Validate Configuration

Check `LINEAR_API_KEY` and `LINEAR_TEAM` are set.

### Step 1: Build Filter

Start with team filter:

```json
{ "team": { "key": { "eq": "$LINEAR_TEAM" } } }
```

Add filters based on provided arguments. See [filtering.md](../skills/linear-api/references/filtering.md) for syntax.

**Defaults:**
- `project`: `basename $(pwd)` — filter by current directory name
- `sort`: priority
- `limit`: 25
- Exclude completed/canceled by default — filter on client side after fetching (do NOT use server-side `state.type.nin` filter, it causes 401 errors)

If `assignee=me`, use `{ "assignee": { "isMe": { "eq": true } } }`.

If `cycle=current`, resolve current active cycle first.

### Step 2: Execute Query

Use `issues` query from [graphql-queries.md](../skills/linear-api/references/graphql-queries.md) with constructed filter.

Set `first` to `limit` value. Do NOT pass `orderBy` — it causes 401 errors with complex filters. Sort results on the client side after fetching (by priority by default, or by `sort` argument).

### Step 3: Display Results

Render as compact table:

```markdown
## Issues (15 found)

| ID | Title | Status | Priority | Pts | Due | Assignee |
|----|-------|--------|----------|-----|-----|----------|
| TEAM-123 | Fix auth flow | In Progress | Urgent | 5 | Mar 10 | John |
| TEAM-124 | Add pagination | Todo | High | 3 | Mar 15 | Jane |
| TEAM-125 | Update docs | Backlog | Medium | 1 | - | - |
```

If no issues found, display a helpful message with current filter criteria.

Truncate title to 40 characters if needed. Format due date as short month-day. Show first name only for assignee.
