# Linear Filtering Syntax

Linear's GraphQL API uses a structured filter system for querying issues.

## Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `{ priority: { eq: 1 } }` |
| `neq` | Not equals | `{ priority: { neq: 0 } }` |
| `in` | In list | `{ priority: { in: [1, 2] } }` |
| `nin` | Not in list | `{ priority: { nin: [0, 4] } }` |
| `lt` | Less than | `{ estimate: { lt: 5 } }` |
| `gt` | Greater than | `{ estimate: { gt: 0 } }` |
| `lte` | Less than or equal | `{ dueDate: { lte: "2026-03-15" } }` |
| `gte` | Greater than or equal | `{ createdAt: { gte: "2026-03-01" } }` |
| `contains` | Contains substring | `{ title: { contains: "auth" } }` |
| `containsIgnoreCase` | Case-insensitive contains | `{ title: { containsIgnoreCase: "auth" } }` |
| `startsWith` | Starts with | `{ title: { startsWith: "feat" } }` |

## Compound Filters

### AND (implicit)

Multiple fields at the same level are ANDed:

```json
{
  "filter": {
    "priority": { "in": [1, 2] },
    "state": { "type": { "eq": "started" } }
  }
}
```

### AND (explicit)

```json
{
  "filter": {
    "and": [
      { "priority": { "eq": 1 } },
      { "estimate": { "gt": 3 } }
    ]
  }
}
```

### OR

```json
{
  "filter": {
    "or": [
      { "priority": { "eq": 1 } },
      { "priority": { "eq": 2 } }
    ]
  }
}
```

## Common Filter Patterns

### By Team

```json
{ "team": { "key": { "eq": "ENG" } } }
```

### By Project Name

```json
{ "project": { "name": { "containsIgnoreCase": "backend" } } }
```

### By Assignee

```json
{ "assignee": { "name": { "eq": "John Doe" } } }
```

### Assigned to Me

```json
{ "assignee": { "isMe": { "eq": true } } }
```

### By Status Type

```json
{ "state": { "type": { "in": ["started", "unstarted"] } } }
```

### By Status Name

```json
{ "state": { "name": { "eq": "In Progress" } } }
```

### By Priority

Priority values: 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low.

```json
{ "priority": { "in": [1, 2] } }
```

### By Label

```json
{ "labels": { "name": { "eq": "bug" } } }
```

### By Cycle

```json
{ "cycle": { "number": { "eq": 42 } } }
```

### Active (not completed/canceled)

> **Warning:** Using `nin` on `state.type` may cause a false 401 error from the Linear API. Use client-side filtering instead: fetch all issues, then exclude those with `state.type` equal to `"completed"` or `"canceled"` in the response.

```json
// Do NOT use this server-side filter:
// { "state": { "type": { "nin": ["completed", "canceled"] } } }

// Instead, fetch without state filter and filter results on the client side.
```

### Due Soon

```json
{
  "dueDate": {
    "gte": "2026-03-06",
    "lte": "2026-03-13"
  }
}
```

### No Assignee

```json
{ "assignee": { "null": true } }
```

## Building Filter in Bash

Construct the filter JSON dynamically:

```bash
FILTER='{"team": {"key": {"eq": "'$LINEAR_TEAM'"}}}'

# Add project filter
if [ -n "$PROJECT" ]; then
  FILTER=$(echo "$FILTER" | jq --arg p "$PROJECT" '. + {project: {name: {containsIgnoreCase: $p}}}')
fi

# Add status filter
if [ -n "$STATUS" ]; then
  FILTER=$(echo "$FILTER" | jq --arg s "$STATUS" '. + {state: {name: {eq: $s}}}')
fi

# Add priority filter
if [ -n "$PRIORITY" ]; then
  PVAL=$(echo "$PRIORITY" | tr '[:upper:]' '[:lower:]')
  case "$PVAL" in
    urgent) PNUM=1 ;; high) PNUM=2 ;; medium) PNUM=3 ;; low) PNUM=4 ;; *) PNUM=$PVAL ;;
  esac
  FILTER=$(echo "$FILTER" | jq --argjson p "$PNUM" '. + {priority: {eq: $p}}')
fi

# Add assignee filter
if [ -n "$ASSIGNEE" ]; then
  if [ "$ASSIGNEE" = "me" ]; then
    FILTER=$(echo "$FILTER" | jq '. + {assignee: {isMe: {eq: true}}}')
  else
    FILTER=$(echo "$FILTER" | jq --arg a "$ASSIGNEE" '. + {assignee: {name: {eq: $a}}}')
  fi
fi
```
