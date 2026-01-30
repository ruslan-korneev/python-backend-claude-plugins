# Feature Phases Reference

Features are organized into 6 phases based on their architectural role and implementation order.

## Phase Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FEATURE PHASES                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐              │
│  │  CORE   │───▶│ WORKFLOW │───▶│ LIFECYCLE │              │
│  │         │    │          │    │           │              │
│  │ Entities│    │ Processes│    │  States   │              │
│  └─────────┘    └──────────┘    └───────────┘              │
│       │              │                │                     │
│       ▼              ▼                ▼                     │
│  ┌─────────────────────────────────────────────┐           │
│  │              INTEGRATION                     │           │
│  │         External Services & APIs             │           │
│  └─────────────────────────────────────────────┘           │
│                        │                                    │
│       ┌────────────────┼────────────────┐                  │
│       ▼                                 ▼                   │
│  ┌───────────┐                    ┌─────────┐              │
│  │ ANALYTICS │                    │   UI    │              │
│  │           │                    │         │              │
│  │ Reporting │                    │  Views  │              │
│  └───────────┘                    └─────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Phase Definitions

### Core (`core-`)

**Purpose**: Fundamental entities and their basic operations.

**Characteristics**:
- Domain models (User, Product, Order)
- CRUD operations
- Basic validations
- No dependencies on other features

**Examples**:
- `core-01-user-management` — User entity, registration, profile
- `core-02-product-catalog` — Product entity, categories
- `core-03-organization` — Company, teams, roles

**Typical Components**:
- SQLAlchemy models
- Basic repositories
- Simple services
- CRUD endpoints

---

### Workflow (`workflow-`)

**Purpose**: Business processes that involve multiple steps or entities.

**Characteristics**:
- Multi-step processes
- Cross-entity operations
- Business logic orchestration
- Depends on Core features

**Examples**:
- `workflow-01-checkout` — Cart → Order → Payment
- `workflow-02-approval` — Request → Review → Approve/Reject
- `workflow-03-onboarding` — Registration → Verification → Setup

**Typical Components**:
- Orchestration services
- Process state management
- Multi-step endpoints
- Transaction coordination

---

### Lifecycle (`lifecycle-`)

**Purpose**: State transitions, notifications, and event-driven behaviors.

**Characteristics**:
- State machines
- Event emission
- Notifications (email, push, webhook)
- Scheduled tasks

**Examples**:
- `lifecycle-01-order-status` — Created → Processing → Shipped → Delivered
- `lifecycle-02-notifications` — Event-based notifications
- `lifecycle-03-reminders` — Scheduled reminders

**Typical Components**:
- State machine implementations
- Event handlers
- Notification services
- Background tasks

---

### Analytics (`analytics-`)

**Purpose**: Reporting, metrics, and data analysis.

**Characteristics**:
- Read-only operations
- Aggregations and calculations
- Dashboard data
- Export functionality

**Examples**:
- `analytics-01-sales-reports` — Revenue, orders, trends
- `analytics-02-user-metrics` — Active users, retention
- `analytics-03-audit-log` — Activity tracking

**Typical Components**:
- Report generators
- Aggregation queries
- Export services
- Dashboard endpoints

---

### Integration (`integration-`)

**Purpose**: External service connections and third-party APIs.

**Characteristics**:
- External API clients
- Webhooks (incoming and outgoing)
- Data synchronization
- Authentication with external services

**Examples**:
- `integration-01-email` — SendGrid, SES, SMTP
- `integration-02-payment` — Stripe, PayPal
- `integration-03-storage` — S3, CloudStorage
- `integration-04-oauth` — Google, GitHub, Apple

**Typical Components**:
- API clients
- Webhook handlers
- Adapter services
- Configuration management

---

### UI (`ui-`)

**Purpose**: User interface components and view-specific logic.

**Characteristics**:
- View models
- UI-specific endpoints
- Form handling
- Frontend-optimized responses

**Examples**:
- `ui-01-admin-panel` — Admin dashboard views
- `ui-02-public-site` — Public page data
- `ui-03-mobile-api` — Mobile-optimized endpoints

**Typical Components**:
- View DTOs
- Aggregated endpoints
- Form validation
- UI state management

## Implementation Order

Recommended implementation sequence:

1. **Core** — Build foundation first
2. **Workflow** — Add business processes
3. **Integration** — Connect external services
4. **Lifecycle** — Add state management
5. **Analytics** — Add reporting
6. **UI** — Optimize for presentation

## Dependency Rules

| Phase | Can Depend On |
|-------|---------------|
| Core | Nothing |
| Workflow | Core |
| Lifecycle | Core, Workflow |
| Integration | Core |
| Analytics | Core, Workflow, Lifecycle |
| UI | All phases |
