# Architecture Decision Records (ADR)

ADRs document significant architectural decisions, their context, and consequences.

## Template

```markdown
# ADR-{number}: {title}

## Status

{Proposed | Accepted | Deprecated | Superseded by ADR-XXX}

## Date

{YYYY-MM-DD}

## Context

{What is the issue that we're seeing that is motivating this decision or change?}

## Decision

{What is the change that we're proposing and/or doing?}

## Consequences

### Positive

- {Benefit 1}
- {Benefit 2}

### Negative

- {Drawback 1}
- {Drawback 2}

### Risks

- {Risk 1}
- {Risk 2}

## Alternatives Considered

### {Alternative 1}

{Description}

**Rejected because:** {Reason}

### {Alternative 2}

{Description}

**Rejected because:** {Reason}

## References

- {Link to relevant documentation}
- {Link to discussion}
```

## Example: Database Selection

```markdown
# ADR-001: Use PostgreSQL as Primary Database

## Status

Accepted

## Date

2024-01-15

## Context

We are building a new e-commerce platform that needs to handle:
- Complex product catalog with hierarchical categories
- Order management with ACID transactions
- Full-text search for products
- JSON storage for flexible product attributes
- Expected load: 10,000 daily active users, 1,000 orders/day

The team has experience with both PostgreSQL and MongoDB.

## Decision

We will use PostgreSQL 16 as the primary database for all application data.

Key features we'll utilize:
- JSONB for flexible product attributes
- Full-text search with pg_trgm for product search
- Table partitioning for orders (by date)
- Row-level security for multi-tenant data

## Consequences

### Positive

- ACID transactions ensure data consistency for orders and payments
- Single database simplifies operations and backups
- Team has strong PostgreSQL expertise
- Rich ecosystem of tools (pgAdmin, pg_dump, logical replication)
- JSONB provides flexibility without sacrificing query performance
- Built-in full-text search eliminates need for separate search service

### Negative

- Horizontal scaling is more complex than document databases
- Schema migrations require careful planning
- Full-text search is less powerful than dedicated solutions (Elasticsearch)

### Risks

- If we exceed 100,000 DAU, we may need read replicas
- Complex product search may eventually require Elasticsearch
- Large JSONB documents (>1MB) may impact performance

## Alternatives Considered

### MongoDB

Document database with flexible schema.

**Rejected because:**
- Weaker transaction support (multi-document transactions added recently)
- Team has less experience
- For our use case (orders, payments), ACID is critical

### PostgreSQL + Elasticsearch

PostgreSQL for transactions, Elasticsearch for search.

**Rejected because:**
- Additional operational complexity
- Data synchronization challenges
- Our search requirements are simple enough for PostgreSQL full-text
- Can migrate to this architecture later if needed

### CockroachDB

Distributed SQL database.

**Rejected because:**
- Higher operational complexity
- Our scale doesn't justify distributed database yet
- Can migrate later if horizontal scaling becomes necessary

## References

- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release-16.html)
- [JSONB Performance Guide](https://www.postgresql.org/docs/current/datatype-json.html)
- Team discussion: Slack #architecture, 2024-01-10
```

## Example: Authentication Strategy

```markdown
# ADR-002: JWT-based Authentication with Refresh Tokens

## Status

Accepted

## Date

2024-01-20

## Context

We need to implement authentication for our API. Requirements:
- Stateless authentication for horizontal scaling
- Mobile and web clients
- Token refresh without re-login
- Ability to revoke sessions
- Support for OAuth2 social login in future

Current team expertise: Session-based auth with Redis.

## Decision

We will implement JWT-based authentication with:

1. **Access Token (JWT)**
   - Short-lived: 15 minutes
   - Contains: user_id, roles, permissions
   - Stored in memory (not localStorage)

2. **Refresh Token (opaque)**
   - Long-lived: 7 days
   - Stored in database (revocable)
   - HttpOnly cookie for web, secure storage for mobile

3. **Token Rotation**
   - New refresh token issued on each refresh
   - Old refresh token invalidated

```python
# Token structure
class TokenPair:
    access_token: str   # JWT, 15 min
    refresh_token: str  # Opaque, 7 days
    token_type: str = "Bearer"

# Storage
class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID]
    user_id: Mapped[int]
    token_hash: Mapped[str]  # Hashed, not plain
    expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None]
    device_info: Mapped[str | None]
```

## Consequences

### Positive

- Stateless access tokens — easy horizontal scaling
- Refresh tokens in DB — can revoke sessions
- Token rotation — limits damage from stolen refresh token
- Short access token lifetime — limits exposure window
- Prepared for OAuth2 social login

### Negative

- More complex than session-based auth
- Requires token refresh logic on clients
- Database lookup for refresh (mitigated by caching)

### Risks

- JWT secret key compromise would require re-issuing all tokens
- Refresh token database could become bottleneck (mitigate with Redis)

## Alternatives Considered

### Session-based with Redis

Store sessions in Redis, send session ID in cookie.

**Rejected because:**
- Redis becomes single point of failure
- More complex horizontal scaling
- Doesn't align with planned OAuth2 integration

### JWT-only (no refresh token)

Single long-lived JWT.

**Rejected because:**
- Cannot revoke tokens
- Long token lifetime increases security risk
- Forces re-login on token expiry

### OAuth2 with external provider (Auth0, Cognito)

Delegate authentication to third-party.

**Rejected because:**
- Additional cost
- Vendor lock-in concerns
- Our requirements are simple enough for in-house solution
- May revisit for enterprise features

## References

- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- Team discussion: Notion page "Auth Design", 2024-01-18
```

## Example: Modular Monolith Decision

```markdown
# ADR-003: Modular Monolith Architecture

## Status

Accepted

## Date

2024-02-01

## Context

We are starting a new project with:
- 3 developers
- MVP deadline: 3 months
- Expected initial users: <1,000
- Uncertain feature requirements (startup phase)

Architecture options: microservices vs monolith.

## Decision

We will build a **modular monolith** with clear module boundaries:

```
src/
├── core/                 # Shared infrastructure
├── modules/
│   ├── users/           # User management
│   ├── products/        # Product catalog
│   ├── orders/          # Order processing
│   └── payments/        # Payment handling
├── shared/
│   ├── events.py        # Event bus (in-process)
│   └── protocols.py     # Module interfaces
└── main.py
```

Module rules:
1. Modules communicate via events or protocols (not direct imports)
2. Each module has its own models, services, repositories
3. Shared database, but modules own their tables
4. No circular dependencies between modules

## Consequences

### Positive

- Fast development — single deployment, shared tooling
- Easy debugging — single process, full stack traces
- Simple testing — no service orchestration needed
- Clear boundaries — prepared for future extraction
- Low infrastructure cost — single container

### Negative

- Single deployment unit — any change deploys everything
- Cannot scale modules independently
- Shared database — no per-module database choice

### Risks

- Module boundaries may erode without discipline
- If one module has performance issues, affects all
- May need significant refactoring if microservices become necessary

## Migration Path

When/if we outgrow monolith:

1. **Extract most isolated module first** (e.g., notifications)
2. **Replace in-process events with message queue**
3. **Extract modules with different scaling needs**
4. **Keep core monolith for tightly coupled domains**

Triggers for extraction:
- Team grows beyond 10 developers
- Module needs independent scaling (>10x others)
- Module needs different tech stack
- Deployment coordination becomes painful

## Alternatives Considered

### Microservices from Start

Separate services for each domain.

**Rejected because:**
- Team is small (3 people)
- Requirements are uncertain
- Would slow down MVP development
- Operational overhead not justified at current scale

### Traditional Monolith (no modules)

Single codebase without internal boundaries.

**Rejected because:**
- Harder to maintain as codebase grows
- No preparation for future scaling
- Encourages tight coupling

## References

- [MonolithFirst - Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [Modular Monolith: A Primer](https://www.kamilgrzybek.com/design/modular-monolith-primer/)
- Team discussion: Architecture Review, 2024-01-28
```

## ADR Best Practices

### When to Write an ADR

- Choosing a technology (database, framework, language)
- Selecting an architectural pattern
- Making a trade-off decision
- Changing a significant part of the system
- Decisions that are hard to reverse

### When NOT to Write an ADR

- Library version updates
- Code formatting decisions
- Obvious choices (using HTTPS)
- Temporary solutions clearly marked as tech debt

### ADR Lifecycle

```
Proposed → Accepted → [Deprecated | Superseded]
```

- **Proposed**: Under discussion
- **Accepted**: Implemented and in use
- **Deprecated**: No longer recommended, but may still exist
- **Superseded**: Replaced by a newer ADR

### Naming Convention

```
docs/adr/
├── 001-use-postgresql.md
├── 002-jwt-authentication.md
├── 003-modular-monolith.md
├── 004-use-redis-caching.md
└── README.md  # Index of all ADRs
```

### Index Template

```markdown
# Architecture Decision Records

| ID | Title | Status | Date |
|----|-------|--------|------|
| [001](001-use-postgresql.md) | Use PostgreSQL | Accepted | 2024-01-15 |
| [002](002-jwt-authentication.md) | JWT Authentication | Accepted | 2024-01-20 |
| [003](003-modular-monolith.md) | Modular Monolith | Accepted | 2024-02-01 |
| [004](004-celery-background-tasks.md) | Use Celery for Background Tasks | Proposed | 2024-02-10 |
```
