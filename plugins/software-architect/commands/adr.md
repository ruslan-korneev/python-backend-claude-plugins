---
name: architect:adr
description: Create Architecture Decision Record
allowed_tools:
  - Read
  - Write
  - Glob
  - AskUserQuestion
arguments:
  - name: title
    description: "ADR title (e.g.: 'Use PostgreSQL', 'JWT Authentication')"
    required: true
---

# Command /architect:adr

Create an Architecture Decision Record (ADR) to document significant architectural decisions.

## Instructions

### Step 1: Check Existing ADRs

Find existing ADRs to determine the next number:

```
Glob: docs/adr/*.md, **/adr/*.md, ADR-*.md
```

### Step 2: Gather Context

Use `AskUserQuestion` to understand the decision:

**Questions:**
1. What problem are you solving?
2. What constraints do you have? (tech stack, team expertise, timeline)
3. What alternatives did you consider?
4. What are the expected benefits?
5. What are the potential risks?

### Step 3: Create ADR Directory (if needed)

```bash
mkdir -p docs/adr
```

### Step 4: Generate ADR

Create file: `docs/adr/{{ next_number }}-{{ title | slugify }}.md`

```markdown
# ADR-{{ number }}: {{ title }}

## Status

Proposed

## Date

{{ today }}

## Context

{{ context }}

### Problem Statement

{{ problem }}

### Constraints

- {{ constraint_1 }}
- {{ constraint_2 }}
- {{ constraint_3 }}

### Requirements

- {{ requirement_1 }}
- {{ requirement_2 }}

## Decision

{{ decision }}

### Key Points

1. {{ key_point_1 }}
2. {{ key_point_2 }}
3. {{ key_point_3 }}

### Implementation Details

{{ implementation_details }}

## Consequences

### Positive

- {{ positive_1 }}
- {{ positive_2 }}
- {{ positive_3 }}

### Negative

- {{ negative_1 }}
- {{ negative_2 }}

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{ risk_1 }} | {{ likelihood }} | {{ impact }} | {{ mitigation }} |
| {{ risk_2 }} | {{ likelihood }} | {{ impact }} | {{ mitigation }} |

## Alternatives Considered

### {{ alternative_1 }}

{{ description }}

**Pros:**
- {{ pro_1 }}
- {{ pro_2 }}

**Cons:**
- {{ con_1 }}
- {{ con_2 }}

**Rejected because:** {{ rejection_reason }}

### {{ alternative_2 }}

{{ description }}

**Pros:**
- {{ pro_1 }}

**Cons:**
- {{ con_1 }}

**Rejected because:** {{ rejection_reason }}

## References

- {{ reference_1 }}
- {{ reference_2 }}

## Notes

{{ additional_notes }}
```

### Step 5: Update ADR Index

Update or create `docs/adr/README.md`:

```markdown
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the project.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences.

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [001](001-initial-architecture.md) | Initial Architecture | Accepted | 2024-01-15 |
| [002](002-database-choice.md) | Use PostgreSQL | Accepted | 2024-01-20 |
| [{{ number }}]({{ filename }}) | {{ title }} | Proposed | {{ today }} |

## Statuses

- **Proposed**: Under discussion
- **Accepted**: Decision made and implemented
- **Deprecated**: No longer relevant
- **Superseded**: Replaced by another ADR
```

## ADR Templates for Common Decisions

### Database Selection

Key considerations:
- ACID vs BASE
- Relational vs Document vs Key-Value
- Scaling requirements
- Team expertise
- Cost

### Authentication Strategy

Key considerations:
- Session vs JWT vs OAuth2
- Token storage (cookies vs localStorage)
- Refresh token strategy
- Revocation capability

### Architecture Style

Key considerations:
- Team size and expertise
- Scale requirements
- Deployment complexity
- Development speed vs maintainability

### API Protocol

Key considerations:
- REST vs GraphQL vs gRPC
- Client requirements
- Caching needs
- Real-time requirements

### Message Queue

Key considerations:
- At-least-once vs exactly-once
- Message ordering
- Throughput requirements
- Operational complexity

## Response Format

```markdown
## ADR Created: {{ title }}

**File**: `docs/adr/{{ number }}-{{ slug }}.md`
**Status**: Proposed
**Date**: {{ today }}

### Summary

**Context**: {{ brief_context }}

**Decision**: {{ brief_decision }}

**Key Consequences**:
- ✅ {{ positive_1 }}
- ✅ {{ positive_2 }}
- ⚠️ {{ negative_1 }}

### Next Steps

1. Share ADR with team for review
2. Discuss in architecture review meeting
3. Update status to "Accepted" after approval
4. Begin implementation

### Related Commands

- `/architect:review` — Review current architecture
- `/architect:diagram component` — Visualize architecture
```
