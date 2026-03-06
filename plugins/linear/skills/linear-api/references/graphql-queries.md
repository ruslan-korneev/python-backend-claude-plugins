# GraphQL Queries & Mutations

All Linear API queries and mutations used by the plugin.

## Queries

### viewer — Current User

```graphql
query Viewer {
  viewer {
    id
    name
    email
  }
}
```

### teams — List Teams

```graphql
query Teams {
  teams {
    nodes {
      id
      name
      key
    }
  }
}
```

### projects — List Projects

```graphql
query Projects($teamId: String!) {
  projects(filter: { accessibleTeams: { id: { eq: $teamId } } }) {
    nodes {
      id
      name
      slugId
      state
    }
  }
}
```

### issue — Get Single Issue by Team Key + Number

```graphql
query Issue($teamKey: String!, $number: Float!) {
  issues(filter: { team: { key: { eq: $teamKey } }, number: { eq: $number } }) {
    nodes {
      id
      identifier
      title
      description
      priority
      priorityLabel
      estimate
      dueDate
      url
      createdAt
      updatedAt
      state {
        id
        name
        type
      }
      assignee {
        id
        name
        email
      }
      project {
        id
        name
      }
      cycle {
        id
        name
        number
      }
      labels {
        nodes {
          id
          name
          color
        }
      }
      comments {
        nodes {
          id
          body
          createdAt
          user {
            name
          }
        }
      }
    }
  }
}
```

### searchIssues — Search by Text

```graphql
query SearchIssues($term: String!, $first: Int) {
  searchIssues(term: $term, first: $first) {
    nodes {
      id
      identifier
      title
      description
      url
      priority
      priorityLabel
      estimate
      dueDate
      createdAt
      updatedAt
      state { name type }
      assignee { name }
      project { name }
      cycle { name number }
      labels {
        nodes { name }
      }
      comments {
        nodes {
          body
          createdAt
          user { name }
        }
      }
    }
  }
}
```

### issues — List with Filters

```graphql
query Issues($filter: IssueFilter, $first: Int, $after: String) {
  issues(filter: $filter, first: $first, after: $after) {
    nodes {
      id
      identifier
      title
      priority
      priorityLabel
      estimate
      dueDate
      state {
        name
        type
      }
      assignee {
        name
      }
      project {
        name
      }
      labels {
        nodes { name }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### workflowStates — Team States

```graphql
query WorkflowStates($teamId: String!) {
  workflowStates(filter: { team: { id: { eq: $teamId } } }) {
    nodes {
      id
      name
      type
      position
      color
    }
  }
}
```

### cycles — List Cycles

```graphql
query Cycles($teamId: String!, $filter: CycleFilter) {
  cycles(filter: { team: { id: { eq: $teamId } } }) {
    nodes {
      id
      name
      number
      startsAt
      endsAt
      completedAt
      progress
      scopeCompleted: completedScopeCount
      scopeTotal: scopeCount
      issues {
        nodes {
          id
          identifier
          title
          state { name type }
          assignee { name }
          estimate
        }
      }
    }
  }
}
```

### issueLabels — Available Labels

```graphql
query IssueLabels($teamId: String!) {
  issueLabels(filter: { team: { id: { eq: $teamId } } }) {
    nodes {
      id
      name
      color
    }
  }
}
```

### users — Team Members

```graphql
query Users {
  users {
    nodes {
      id
      name
      email
      displayName
    }
  }
}
```

## Mutations

### issueCreate

```graphql
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state { name }
      priority
      assignee { name }
    }
  }
}
```

**Variables** (`$input`):

```json
{
  "teamId": "uuid",
  "title": "Issue title",
  "description": "Markdown description",
  "priority": 2,
  "stateId": "uuid",
  "assigneeId": "uuid",
  "projectId": "uuid",
  "cycleId": "uuid",
  "labelIds": ["uuid"],
  "estimate": 3,
  "dueDate": "2026-03-15"
}
```

Priority values: 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low.

### issueUpdate

```graphql
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state { name }
      priority
      assignee { name }
    }
  }
}
```

Same fields as `issueCreate` in `$input`, only changed fields required.

### issueArchive

```graphql
mutation IssueArchive($id: String!) {
  issueArchive(id: $id) {
    success
  }
}
```

### issueDelete

```graphql
mutation IssueDelete($id: String!) {
  issueDelete(id: $id) {
    success
  }
}
```

### commentCreate

```graphql
mutation CommentCreate($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    success
    comment {
      id
      body
      createdAt
      user { name }
    }
  }
}
```

**Variables** (`$input`):

```json
{
  "issueId": "uuid",
  "body": "Comment text in markdown"
}
```

### commentUpdate

```graphql
mutation CommentUpdate($id: String!, $input: CommentUpdateInput!) {
  commentUpdate(id: $id, input: $input) {
    success
    comment {
      id
      body
    }
  }
}
```

### commentDelete

```graphql
mutation CommentDelete($id: String!) {
  commentDelete(id: $id) {
    success
  }
}
```

### cycleCreate

```graphql
mutation CycleCreate($input: CycleCreateInput!) {
  cycleCreate(input: $input) {
    success
    cycle {
      id
      name
      number
      startsAt
      endsAt
    }
  }
}
```

**Variables** (`$input`):

```json
{
  "teamId": "uuid",
  "name": "Sprint 42",
  "startsAt": "2026-03-10",
  "endsAt": "2026-03-24"
}
```

## Common Patterns

### Resolve Team ID by Key

```bash
TEAM_ID=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  -d '{"query": "{ teams { nodes { id key } } }"}' \
  | jq -r --arg key "$LINEAR_TEAM" '.data.teams.nodes[] | select(.key == $key) | .id')
```

### Resolve Project ID by Name

```bash
PROJECT_ID=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  -d "{\"query\": \"{ projects(filter: { name: { containsIgnoreCase: \\\"$PROJECT_NAME\\\" } }) { nodes { id name } } }\"}" \
  | jq -r '.data.projects.nodes[0].id')
```

### Resolve User ID by Name/Email

```bash
ASSIGNEE_ID=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  -d '{"query": "{ users { nodes { id name email displayName } } }"}' \
  | jq -r --arg name "$ASSIGNEE" '.data.users.nodes[] | select(.name == $name or .email == $name or .displayName == $name) | .id')
```

### Resolve State ID by Name

```bash
STATE_ID=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  -d "{\"query\": \"{ workflowStates(filter: { team: { id: { eq: \\\"$TEAM_ID\\\" } } }) { nodes { id name type } } }\"}" \
  | jq -r --arg name "$STATUS" '.data.workflowStates.nodes[] | select(.name == $name) | .id')
```

### Resolve Label IDs

```bash
LABEL_IDS=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $LINEAR_API_KEY" \
  -d "{\"query\": \"{ issueLabels(filter: { team: { id: { eq: \\\"$TEAM_ID\\\" } } }) { nodes { id name } } }\"}" \
  | jq -r --arg labels "$LABELS" '[.data.issueLabels.nodes[] | select(.name as $n | ($labels | split(",") | map(gsub("^ +| +$"; "")) | any(. == $n))) | .id]')
```

### Check for API Errors

```bash
if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
  ERROR=$(echo "$RESPONSE" | jq -r '.errors[0].message')
  echo "Linear API error: $ERROR"
  # Handle error
fi
```
