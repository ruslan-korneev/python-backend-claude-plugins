# ID Conventions Reference

Standardized identifier formats for Business Rules, User Stories, and Acceptance Criteria.

## Identifier Format

```
<TYPE>-<DOMAIN>-<NUMBER>
```

| Component | Description | Example |
|-----------|-------------|---------|
| TYPE | BR, US, or AC | BR |
| DOMAIN | 3-letter code | USR |
| NUMBER | 3-digit sequential | 001 |

**Full example**: `BR-USR-001`

## Identifier Types

### Business Rules (BR)

**Format**: `BR-XXX-YYY`

**Purpose**: Define constraints, policies, and business logic.

**Examples**:
- `BR-USR-001` — Users must have unique email addresses
- `BR-ORD-001` — Orders cannot be modified after shipping
- `BR-PAY-001` — Payments require 3D Secure for amounts > $100

**Usage in documentation**:
```markdown
### BR-USR-001: Unique Email Constraint

**Description**: Each user account must have a unique email address.

**Rationale**: Email serves as the primary identifier for authentication
and communication.

**Constraints**:
- Email validation must occur before account creation
- Email changes require verification
```

---

### User Stories (US)

**Format**: `US-XXX-YYY`

**Purpose**: Describe user goals from the user's perspective.

**Template**: "As a [role], I want [goal] so that [benefit]"

**Examples**:
- `US-USR-001` — As a user, I want to register an account
- `US-ORD-001` — As a customer, I want to track my order
- `US-ADM-001` — As an admin, I want to view all users

**Usage in documentation**:
```markdown
### US-USR-001: As a user, I want to register an account so that I can access the platform

**Priority**: High

**Acceptance Criteria**:
- [ ] AC-USR-001: Given valid email and password, when I submit registration, then account is created
- [ ] AC-USR-002: Given existing email, when I submit registration, then error is shown
```

---

### Acceptance Criteria (AC)

**Format**: `AC-XXX-YYY`

**Purpose**: Define testable conditions for user story completion.

**Template**: "Given [context], when [action], then [outcome]"

**Examples**:
- `AC-USR-001` — Given valid credentials, when login, then JWT is returned
- `AC-ORD-001` — Given empty cart, when checkout, then error is shown
- `AC-PAY-001` — Given valid card, when payment, then order is confirmed

**Usage in documentation**:
```markdown
- [ ] AC-USR-001: Given valid email and password, when I submit registration, then:
  - Account is created with `status: pending`
  - Verification email is sent
  - Response contains user ID
```

## Domain Codes

Common 3-letter domain codes:

| Code | Domain | Description |
|------|--------|-------------|
| `USR` | User | User management, profiles |
| `AUT` | Auth | Authentication, authorization |
| `ORD` | Order | Orders, cart, checkout |
| `PAY` | Payment | Payments, transactions |
| `PRD` | Product | Products, catalog, inventory |
| `CAT` | Category | Categories, taxonomies |
| `NTF` | Notification | Notifications, alerts |
| `RPT` | Report | Reports, analytics |
| `ADM` | Admin | Administration, settings |
| `INT` | Integration | External integrations |
| `FIL` | File | File uploads, storage |
| `MSG` | Message | Messaging, chat |
| `SUB` | Subscription | Subscriptions, billing |
| `INV` | Inventory | Stock, warehouses |
| `SHP` | Shipping | Shipping, delivery |
| `REV` | Review | Reviews, ratings |
| `SRC` | Search | Search, filters |
| `LOG` | Log | Audit logs, activity |

## Numbering Rules

1. **Sequential within domain**: Numbers increment per domain
2. **No gaps**: Don't skip numbers
3. **No reuse**: Deleted items keep their numbers

**Example sequence**:
```
BR-USR-001  ← First user business rule
BR-USR-002  ← Second user business rule
BR-ORD-001  ← First order business rule (new domain, restart numbering)
US-USR-001  ← First user story (new type, restart numbering)
```

## Cross-Referencing

Reference other identifiers using backticks:

```markdown
This feature implements `US-USR-001` and satisfies `BR-USR-002`.

See also: `AC-ORD-001` for order validation requirements.
```

## Feature ID Format

Feature files use a different format:

```
<phase>-<number>
```

**Examples**:
- `core-01` — First core feature
- `workflow-03` — Third workflow feature
- `integration-01` — First integration feature

**In frontmatter**:
```yaml
---
id: core-01
title: User Management
dependencies:
  - integration-01  # References another feature
---
```
