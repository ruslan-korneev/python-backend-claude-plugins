# Feature List Plugin

Generate structured feature specifications with Business Rules (BR), User Stories (US), and Acceptance Criteria (AC).

## Features

- **Analyze mode** — Extract features from existing codebase
- **Design mode** — Interactive feature design for new projects
- **Dependency graphs** — Visualize feature relationships with Mermaid
- **Status tracking** — Track implementation progress by phase

## Installation

```bash
/plugin marketplace add https://github.com/your-repo/python-backend-plugins
/plugin install feature-list@python-backend-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/feature-list:init` | Initialize feature directory structure |
| `/feature-list:analyze` | Analyze codebase and generate feature specs |
| `/feature-list:design` | Interactive feature design session |
| `/feature-list:add <phase> <name>` | Add a new feature to a phase |
| `/feature-list:graph` | Regenerate dependency graph |
| `/feature-list:status` | Show implementation status by phase |

## Feature Structure

Features are organized by phases:

| Phase | Prefix | Description |
|-------|--------|-------------|
| Core | `core-` | Fundamental entities and operations |
| Workflow | `workflow-` | Business processes and flows |
| Lifecycle | `lifecycle-` | State transitions and notifications |
| Analytics | `analytics-` | Reporting and metrics |
| Integration | `integration-` | External service connections |
| UI | `ui-` | User interface components |

## Output Structure

```
docs/technical-requirements/features/
├── README.md                      # Index with dependency graph
├── 00-template.md                 # Feature template
├── core-01-user-management.md     # Core features
├── workflow-01-order-creation.md  # Workflow features
└── ...
```

## Feature File Format

Each feature file uses YAML frontmatter:

```yaml
---
id: core-01
title: User Management
status: draft | in_progress | completed
phase: core
priority: critical | high | medium | low
dependencies: []
---
```

## Identifier Conventions

- **BR-XXX-YYY** — Business Rules (BR-USR-001)
- **US-XXX-YYY** — User Stories (US-USR-001)
- **AC-XXX-YYY** — Acceptance Criteria (AC-USR-001)

## Manual Sections

Preserve manual edits during regeneration:

```markdown
<!-- manual -->
This content is preserved during regeneration
<!-- /manual -->
```

## License

MIT
