---
name: feature-list:add
description: Add a new feature to a specific phase
allowed_tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
arguments:
  - name: phase
    description: "Feature phase (core, workflow, lifecycle, analytics, integration, ui)"
    required: true
  - name: name
    description: "Feature name in kebab-case (e.g., user-management)"
    required: true
---

# Command /feature-list:add

Add a new feature file to the specified phase.

## Instructions

### Step 1: Validate Phase

Ensure `phase` is one of:
- `core`
- `workflow`
- `lifecycle`
- `analytics`
- `integration`
- `ui`

If invalid, show error:
```markdown
❌ Invalid phase: `{phase}`

Valid phases:
- `core` — Fundamental entities
- `workflow` — Business processes
- `lifecycle` — State transitions
- `analytics` — Reporting
- `integration` — External services
- `ui` — User interface
```

### Step 2: Determine Next Number

Use `Glob` to find existing features in the phase:

```
docs/technical-requirements/features/{phase}-*.md
```

Parse filenames to find the highest number, then increment:
- If `core-01-user.md` and `core-02-product.md` exist
- Next number is `03`

### Step 3: Generate Domain Code

Derive 3-letter domain code from the feature name:

| Name | Domain Code |
|------|-------------|
| user-management | USR |
| product-catalog | PRD |
| order-processing | ORD |
| payment-gateway | PAY |
| email-service | EML |
| notifications | NTF |

If unclear, ask user:

```yaml
questions:
  - question: "What 3-letter domain code should be used for {name}?"
    header: "Domain"
    options:
      - label: "{suggested1}"
        description: "Based on feature name"
      - label: "{suggested2}"
        description: "Alternative"
```

### Step 4: Gather Feature Details

Use `AskUserQuestion`:

```yaml
questions:
  - question: "What is the priority of this feature?"
    header: "Priority"
    options:
      - label: "Critical"
        description: "Must have for MVP"
      - label: "High"
        description: "Important, implement early"
      - label: "Medium"
        description: "Standard priority"
      - label: "Low"
        description: "Nice to have"
```

### Step 5: Check Directory Exists

Use `Glob` to verify `docs/technical-requirements/features/` exists.

If not, run init first:
```markdown
⚠️ Feature directory not found.

Running `/feature-list:init` first...
```

### Step 6: Create Feature File

Read the template and customize:

1. Read `docs/technical-requirements/features/00-template.md`
2. Replace placeholders:
   - `<phase>-<number>` → `{phase}-{number}`
   - `<Feature Title>` → Title case of name
   - `XXX` → Domain code
   - `<YYYY-MM-DD>` → Today's date

3. Write to `docs/technical-requirements/features/{phase}-{number}-{name}.md`

### Step 7: Update README

1. Read `docs/technical-requirements/features/README.md`
2. Add entry to appropriate phase table
3. Update statistics
4. Write back

### Step 8: Confirm Creation

```markdown
✅ Feature created: `{phase}-{number}-{name}.md`

## Feature Summary

| Field | Value |
|-------|-------|
| ID | `{phase}-{number}` |
| Title | {Title} |
| Phase | {phase} |
| Priority | {priority} |
| Domain | {domain_code} |

## File Location

`docs/technical-requirements/features/{phase}-{number}-{name}.md`

## Next Steps

1. Edit the feature file to add business rules
2. Define user stories with acceptance criteria
3. Update dependencies if needed
4. Run `/feature-list:graph` to update the diagram
```

## Response Format

```markdown
## Feature Added

📄 Created `docs/technical-requirements/features/{phase}-{number}-{name}.md`

### Details

- **ID**: {phase}-{number}
- **Title**: {Title Case Name}
- **Phase**: {phase}
- **Priority**: {priority}
- **Domain Code**: {domain_code}

### Template Sections

The new feature file includes:
- [ ] Overview (to be filled)
- [ ] Business Rules (BR-{domain}-001, ...)
- [ ] User Stories (US-{domain}-001, ...)
- [ ] API Endpoints
- [ ] Data Model
- [ ] Implementation Status

### Edit the Feature

Open `docs/technical-requirements/features/{phase}-{number}-{name}.md` to:
1. Add specific business rules
2. Define user stories
3. Document API endpoints
4. Describe the data model
```

## Examples

### Example 1: Add User Management

```bash
/feature-list:add core user-management
```

Creates: `core-01-user-management.md` with domain code `USR`

### Example 2: Add Checkout Workflow

```bash
/feature-list:add workflow checkout
```

Creates: `workflow-01-checkout.md` with domain code `CHK`

### Example 3: Add Email Integration

```bash
/feature-list:add integration email-service
```

Creates: `integration-01-email-service.md` with domain code `EML`
