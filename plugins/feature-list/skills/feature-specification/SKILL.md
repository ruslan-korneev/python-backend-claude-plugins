# Feature Specification Skill

Generate structured feature specifications with Business Rules (BR), User Stories (US), and Acceptance Criteria (AC).

## When to Use This Skill

Use this skill when the user wants to:
- Document project features systematically
- Extract feature specifications from existing code
- Design features for a new project interactively
- Create a structured requirements document
- Visualize feature dependencies

**Trigger phrases:**
- "Create feature list for this project"
- "Document the features"
- "What features does this codebase have?"
- "Help me plan features for..."
- "Generate requirements specification"
- "Extract business rules from code"

## Core Concepts

### Feature Phases

Features are organized into 6 phases based on their role:

| Phase | Prefix | Description |
|-------|--------|-------------|
| **Core** | `core-` | Fundamental entities (users, products, orders) |
| **Workflow** | `workflow-` | Business processes (checkout, approval) |
| **Lifecycle** | `lifecycle-` | State transitions, notifications |
| **Analytics** | `analytics-` | Reporting, metrics, dashboards |
| **Integration** | `integration-` | External APIs, third-party services |
| **UI** | `ui-` | User interface components |

### Identifier Format

Each requirement uses a standardized identifier:

- **BR-XXX-YYY** — Business Rule (e.g., BR-USR-001)
- **US-XXX-YYY** — User Story (e.g., US-USR-001)
- **AC-XXX-YYY** — Acceptance Criteria (e.g., AC-USR-001)

Where:
- `XXX` — 3-letter domain code (USR, ORD, PAY, etc.)
- `YYY` — Sequential number (001, 002, ...)

### Feature Anatomy

```markdown
## BR-XXX-001: Business Rule Title

**Description**: What this rule defines

**Rationale**: Why this rule exists

### User Stories

#### US-XXX-001: As a [role], I want [goal]

**Acceptance Criteria:**
- [ ] AC-XXX-001: Given [context], when [action], then [outcome]
- [ ] AC-XXX-002: Given [context], when [action], then [outcome]
```

## Two Operating Modes

### Analyze Mode

For existing codebases:
1. Scan models, routes, services
2. Extract entities and operations
3. Infer business rules from code
4. Generate feature specifications
5. Detect dependencies from imports

### Design Mode

For new projects:
1. Ask about project type
2. Identify user roles
3. Define core workflows
4. Plan integrations
5. Generate feature specifications

## Output Structure

```
docs/technical-requirements/features/
├── README.md                      # Index with dependency graph
├── 00-template.md                 # Feature template
├── core-01-user-management.md     # Core features
├── core-02-authentication.md
├── workflow-01-order-creation.md  # Workflow features
├── lifecycle-01-notifications.md  # Lifecycle features
├── analytics-01-reports.md        # Analytics features
├── integration-01-email.md        # Integration features
└── ui-01-admin-panel.md           # UI features
```

## References

- [Feature Template](references/feature-template.md) — Full feature file structure
- [Phases](references/phases.md) — Detailed phase definitions
- [ID Conventions](references/id-conventions.md) — Identifier format rules
- [Dependency Graph](references/dependency-graph.md) — Mermaid graph generation

## Key Principles

### Idempotency
- Check if files exist before creating
- Merge new content with existing during re-analysis

### Preserve Manual Edits
```markdown
<!-- manual -->
This content is preserved during regeneration
<!-- /manual -->
```

### Cross-Reference Validation
- Warn about non-existent dependencies
- Detect circular dependencies

### Status Inference
- `draft` — File exists, no code yet
- `in_progress` — Code exists, tests failing
- `completed` — Code + tests passing
