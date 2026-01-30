---
id: <phase>-<number>
title: <Feature Title>
status: draft
phase: core | workflow | lifecycle | analytics | integration | ui
priority: high
dependencies: []
domain: XXX
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Feature Title>

## Overview

<!-- Brief description of what this feature provides and why it exists -->

## Business Rules

### BR-XXX-001: <Rule Title>

**Description**: What this rule defines or constrains.

**Rationale**: Why this rule exists (business justification).

**Constraints**:
- Constraint 1
- Constraint 2

---

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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/<resource>` | Create new resource |
| GET | `/api/v1/<resource>` | List resources |
| GET | `/api/v1/<resource>/{id}` | Get resource by ID |
| PUT | `/api/v1/<resource>/{id}` | Update resource |
| DELETE | `/api/v1/<resource>/{id}` | Delete resource |

## Data Model

```python
class <Model>(Base):
    __tablename__ = "<table_name>"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    # ... additional fields
```

## Dependencies

<!-- Dependencies on other features -->
- None

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Model | ❌ | Not started |
| Repository | ❌ | Not started |
| Service | ❌ | Not started |
| Router | ❌ | Not started |
| Tests | ❌ | Not started |

## Notes

<!-- manual -->
Add any manual notes here. This section is preserved during regeneration.
<!-- /manual -->
