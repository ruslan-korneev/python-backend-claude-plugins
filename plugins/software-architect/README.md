# software-architect

System-level architecture plugin for Python backend projects (FastAPI + SQLAlchemy 2.0).

## Philosophy

Architecture is about making decisions that are expensive to change. This plugin helps:
- Design systems with clear boundaries
- Document decisions with ADRs
- Analyze dependencies and anti-patterns
- Modernize legacy code incrementally

## Abstraction Levels

| Plugin | Level | Focus |
|--------|-------|-------|
| **software-architect** | System | Architecture, modules, ADR |
| fastapi-scaffold | Module | Boilerplate generation |
| clean-code | Code | SOLID, code smells |

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install software-architect@python-backend-plugins
```

## Commands

### `/architect:design <name>`

Interactive architecture design for new projects or major features.

```
/architect:design my-ecommerce-api
/architect:design users-module
```

**Features:**
- Requirements gathering via questions
- Architecture style selection
- Module structure proposal
- Optional scaffold generation
- Initial ADR creation

### `/architect:modernize [path]`

Analyze legacy code and create phased modernization plan.

```
/architect:modernize
/architect:modernize ./legacy-app
```

**Features:**
- Current state analysis
- Risk assessment
- Strangler Fig migration plan
- Target architecture proposal

### `/architect:review [path]`

Comprehensive architecture review.

```
/architect:review
/architect:review src/
```

**Analyzes:**
- Project structure
- Layer separation
- Module boundaries
- Anti-patterns
- Security practices
- Scalability readiness

### `/architect:adr <title>`

Create Architecture Decision Record.

```
/architect:adr "Use PostgreSQL as primary database"
/architect:adr "JWT Authentication Strategy"
```

**Features:**
- Numbered ADR creation
- Context and consequences documentation
- Alternatives considered
- ADR index maintenance

### `/architect:diagram <type>`

Generate Mermaid architecture diagram.

```
/architect:diagram component
/architect:diagram er
/architect:diagram sequence
/architect:diagram data-flow
/architect:diagram deployment
```

**Diagram types:**
- `component` — High-level system components
- `data-flow` — Data flow through system
- `sequence` — Interaction sequence for use case
- `er` — Entity-Relationship diagram
- `deployment` — Infrastructure topology

### `/architect:deps [path]`

Analyze module dependencies.

```
/architect:deps
/architect:deps src/modules/
```

**Features:**
- Module dependency graph
- Circular dependency detection
- Coupling metrics (Ca, Ce, Instability)
- Layer violation detection

## Agents

### architecture-reviewer

Deep architecture analysis with comprehensive checklist.

**Triggers:** Architecture review requests, code quality concerns

**Analyzes:**
- Structure (10 points)
- Layers (10 points)
- Dependencies (10 points)
- Data model (10 points)
- API design (10 points)
- Security (10 points)
- Scalability (10 points)

### dependency-analyzer

Multi-level dependency analysis.

**Analyzes:**
- Module dependencies
- Package dependencies
- Layer dependencies
- Coupling metrics

## Skill

Triggers for automatic activation:
- Designing new system or major feature
- Questions about project structure
- Data modeling decisions
- API contract design
- Architecture trade-offs
- ADR creation or review
- Legacy modernization

## 5 Core Principles

1. **Modularity & Separation of Concerns** — Clear boundaries between modules
2. **Scalability** — Stateless services, horizontal scaling ready
3. **Maintainability** — Testable, well-organized code
4. **Security** — Defense in depth, least privilege
5. **Performance** — Efficient algorithms, strategic caching

## Architectural Patterns

### Layered Architecture

```
┌─────────────────────────────────┐
│       Presentation Layer        │
│     (Routers, DTOs, OpenAPI)    │
├─────────────────────────────────┤
│       Application Layer         │
│    (Services, Use Cases)        │
├─────────────────────────────────┤
│         Domain Layer            │
│   (Entities, Business Rules)    │
├─────────────────────────────────┤
│      Infrastructure Layer       │
│   (Repositories, External)      │
└─────────────────────────────────┘
```

### Repository Pattern

Abstract data access behind interfaces for testability and flexibility.

### Event-Driven Architecture

Loose coupling between modules via domain events.

### CQRS

Separate read and write operations for complex domains.

## Anti-Patterns Detected

| Anti-Pattern | Detection |
|--------------|-----------|
| Big Ball of Mud | No module structure |
| Golden Hammer | Same pattern everywhere |
| Tight Coupling | Direct instantiation |
| God Object | >20 methods in class |
| Circular Dependencies | Import cycles |
| Anemic Domain | Logic only in services |

## Structure

```
software-architect/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── design.md
│   ├── modernize.md
│   ├── review.md
│   ├── adr.md
│   ├── diagram.md
│   └── analyze-deps.md
├── agents/
│   ├── architecture-reviewer.md
│   └── dependency-analyzer.md
├── skills/
│   └── architecture-patterns/
│       ├── SKILL.md
│       └── references/
│           ├── layered-architecture.md
│           ├── data-modeling.md
│           ├── api-design.md
│           ├── anti-patterns.md
│           └── adr-template.md
├── CHANGELOG.md
└── README.md
```

## References

- [Clean Architecture by Robert C. Martin](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
- [Patterns of Enterprise Application Architecture](https://martinfowler.com/books/eaa.html)
- [Architecture Decision Records](https://adr.github.io/)
- [Domain-Driven Design by Eric Evans](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
