# Feature Template Reference

This document describes the complete structure of a feature specification file.

## File Structure

```markdown
---
id: <phase>-<number>
title: <Feature Title>
status: draft | in_progress | completed
phase: core | workflow | lifecycle | analytics | integration | ui
priority: critical | high | medium | low
dependencies: []
domain: <3-letter code>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Feature Title>

## Overview

Brief description of what this feature provides and why it exists.

## Business Rules

### BR-XXX-001: <Rule Title>

**Description**: What this rule defines or constrains.

**Rationale**: Why this rule exists (business justification).

**Constraints**:
- Constraint 1
- Constraint 2

---

### BR-XXX-002: <Another Rule>

...

## User Stories

### US-XXX-001: As a <role>, I want <goal> so that <benefit>

**Priority**: High | Medium | Low

**Acceptance Criteria**:
- [ ] AC-XXX-001: Given <context>, when <action>, then <outcome>
- [ ] AC-XXX-002: Given <context>, when <action>, then <outcome>

**Technical Notes**:
- Implementation consideration 1
- Implementation consideration 2

---

### US-XXX-002: As a <role>, I want <goal>

...

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/<resource>` | Create new resource |
| GET | `/api/v1/<resource>` | List resources |
| GET | `/api/v1/<resource>/{id}` | Get resource by ID |
| PUT | `/api/v1/<resource>/{id}` | Update resource |
| DELETE | `/api/v1/<resource>/{id}` | Delete resource |

## Data Model

\`\`\`python
class <Model>(Base):
    __tablename__ = "<table_name>"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    # ... fields
\`\`\`

## Dependencies

<!-- Dependencies on other features -->
- `core-01` — User Management (for ownership)
- `integration-01` — Email Service (for notifications)

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Model | ✅ | `src/models/<model>.py` |
| Repository | ✅ | `src/repositories/<model>.py` |
| Service | 🔄 | In progress |
| Router | ❌ | Not started |
| Tests | ❌ | Not started |

## Notes

<!-- manual -->
Any manual notes that should be preserved during regeneration.
<!-- /manual -->
```

## YAML Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (phase-number format) |
| `title` | Yes | Human-readable feature name |
| `status` | Yes | Current implementation status |
| `phase` | Yes | Feature category |
| `priority` | Yes | Implementation priority |
| `dependencies` | No | List of feature IDs this depends on |
| `domain` | Yes | 3-letter code for BR/US/AC prefixes |
| `created` | No | Creation date |
| `updated` | No | Last update date |

## Status Values

| Status | Icon | Description |
|--------|------|-------------|
| `draft` | 📝 | Documented, not yet implemented |
| `in_progress` | 🔄 | Implementation started |
| `completed` | ✅ | Fully implemented and tested |

## Priority Values

| Priority | Description |
|----------|-------------|
| `critical` | Must have for MVP |
| `high` | Important, implement early |
| `medium` | Standard priority |
| `low` | Nice to have |
