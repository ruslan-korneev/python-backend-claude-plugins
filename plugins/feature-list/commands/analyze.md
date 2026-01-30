---
name: feature-list:analyze
description: Analyze codebase and generate feature specifications
allowed_tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
arguments:
  - name: path
    description: "Source code path to analyze (default: src/ or app/)"
    required: false
  - name: phase
    description: "Specific phase to analyze (core, workflow, etc.)"
    required: false
---

# Command /feature-list:analyze

Analyze existing codebase and generate feature specifications.

## Instructions

### Step 1: Launch Codebase Analyzer

Use the `Task` tool to spawn the `codebase-analyzer` agent:

```
Analyze the codebase at {path} and extract:
1. Domain entities (models, tables)
2. API endpoints (routes, handlers)
3. Business services
4. External integrations

For each entity, identify:
- CRUD operations
- Business rules (validations, constraints)
- Relationships and dependencies
- Current implementation status
```

### Step 2: Process Analysis Results

From the analyzer output, categorize findings:

**Core Features** (from models):
- Each major model → potential core feature
- Identify domain codes from model names

**Workflow Features** (from services):
- Multi-step processes
- Cross-entity operations

**Integration Features** (from clients/adapters):
- External API clients
- Third-party service connections

### Step 3: Check Existing Features

Use `Glob` to find existing feature files:

```
docs/technical-requirements/features/*.md
```

Compare with analysis to identify:
- New features to create
- Existing features to update
- Obsolete features to flag

### Step 4: Confirm with User

Use `AskUserQuestion` to confirm the proposed features:

```markdown
## Proposed Features

Based on codebase analysis, I found these features:

### Core (entities)
- [ ] `core-01-user` — User model with authentication
- [ ] `core-02-product` — Product catalog

### Workflow (processes)
- [ ] `workflow-01-checkout` — Order creation flow

### Integration (external)
- [ ] `integration-01-email` — SendGrid integration

Should I generate these feature specifications?
```

### Step 5: Generate Feature Files

For each confirmed feature:

1. Determine next number for phase:
   ```
   Glob: docs/technical-requirements/features/{phase}-*.md
   ```

2. Generate feature file using template from SKILL.md

3. Extract business rules from code:
   - Model validations → BR-XXX rules
   - Unique constraints → BR-XXX rules
   - Required fields → BR-XXX rules

4. Generate user stories from endpoints:
   - POST → "As a user, I want to create..."
   - GET (list) → "As a user, I want to view..."
   - PUT → "As a user, I want to update..."
   - DELETE → "As a user, I want to remove..."

### Step 6: Update README

After creating feature files:

1. Read existing README.md
2. Update feature index tables
3. Regenerate dependency graph
4. Update statistics

## Response Format

```markdown
## Codebase Analysis Complete

### Summary

| Phase | Found | Created | Updated |
|-------|-------|---------|---------|
| Core | 3 | 2 | 1 |
| Workflow | 1 | 1 | 0 |
| Integration | 2 | 2 | 0 |

### Features Created

1. `core-01-user-management.md`
   - 3 Business Rules
   - 5 User Stories

2. `core-02-product-catalog.md`
   - 2 Business Rules
   - 4 User Stories

### Next Steps

- Review generated features for accuracy
- Add missing business context
- Run `/feature-list:graph` to update dependencies
```

## Merge Strategy

When updating existing features:

1. **Preserve manual sections**: Content between `<!-- manual -->` markers
2. **Add new items**: New BR/US/AC get appended
3. **Update status**: Infer from code presence
4. **Flag conflicts**: If generated differs from manual

```markdown
⚠️ Conflict in `core-01-user-management.md`:

**Current**: BR-USR-001 requires email verification
**Generated**: No email verification found in code

Keep current? [Y/n]
```
