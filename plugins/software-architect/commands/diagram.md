---
name: architect:diagram
description: Generate architecture diagram in Mermaid format
allowed_tools:
  - Read
  - Glob
  - Grep
arguments:
  - name: type
    description: "Diagram type: component, data-flow, sequence, er, deployment"
    required: true
  - name: path
    description: "Path to analyze (default: src/)"
    required: false
---

# Command /architect:diagram

Generate architecture diagrams in Mermaid format based on codebase analysis.

## Diagram Types

### 1. Component Diagram

Shows high-level system components and their relationships.

```mermaid
graph TD
    subgraph Presentation
        R[Routers]
        DTO[DTOs]
    end

    subgraph Application
        S[Services]
        E[Events]
    end

    subgraph Domain
        M[Models]
        VO[Value Objects]
    end

    subgraph Infrastructure
        REPO[Repositories]
        EXT[External APIs]
        CACHE[Cache]
    end

    R --> S
    S --> REPO
    S --> E
    REPO --> M
    S --> EXT
    S --> CACHE
```

### 2. Data Flow Diagram

Shows how data flows through the system.

```mermaid
flowchart LR
    Client([Client])
    API[FastAPI]
    Auth{Auth}
    Service[Service]
    DB[(Database)]
    Cache[(Redis)]
    Queue[Message Queue]

    Client -->|HTTP Request| API
    API --> Auth
    Auth -->|Valid| Service
    Auth -->|Invalid| Client
    Service -->|Query| DB
    Service -->|Cache| Cache
    Service -->|Event| Queue
    Service -->|Response| API
    API -->|HTTP Response| Client
```

### 3. Sequence Diagram

Shows interaction between components for a specific use case.

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant S as Service
    participant REPO as Repository
    participant DB as Database

    C->>R: POST /orders
    R->>R: Validate DTO
    R->>S: create_order(data)
    S->>S: Apply business rules
    S->>REPO: save(order)
    REPO->>DB: INSERT
    DB-->>REPO: order_id
    REPO-->>S: Order
    S->>S: Publish OrderCreated event
    S-->>R: OrderReadDTO
    R-->>C: 201 Created
```

### 4. ER Diagram

Shows database entity relationships.

```mermaid
erDiagram
    users {
        int id PK
        string email UK
        string name
        string password_hash
        boolean is_active
        datetime created_at
    }

    orders {
        int id PK
        int user_id FK
        string status
        decimal total
        datetime created_at
    }

    order_items {
        int order_id PK,FK
        int product_id PK,FK
        int quantity
        decimal unit_price
    }

    products {
        int id PK
        string name
        string sku UK
        decimal price
        int stock
    }

    users ||--o{ orders : places
    orders ||--|{ order_items : contains
    products ||--o{ order_items : "included in"
```

### 5. Deployment Diagram

Shows infrastructure and deployment topology.

```mermaid
graph TB
    subgraph Cloud["Cloud (AWS/GCP)"]
        subgraph LB["Load Balancer"]
            ALB[Application LB]
        end

        subgraph App["Application Layer"]
            API1[API Instance 1]
            API2[API Instance 2]
        end

        subgraph Data["Data Layer"]
            PG[(PostgreSQL)]
            Redis[(Redis)]
        end

        subgraph Queue["Message Queue"]
            RMQ[RabbitMQ]
        end

        subgraph Workers["Background Workers"]
            W1[Worker 1]
            W2[Worker 2]
        end
    end

    Internet([Internet]) --> ALB
    ALB --> API1 & API2
    API1 & API2 --> PG
    API1 & API2 --> Redis
    API1 & API2 --> RMQ
    RMQ --> W1 & W2
    W1 & W2 --> PG
```

## Instructions

### Step 1: Analyze Codebase

Based on diagram type, gather relevant information:

**For Component Diagram:**
```
Glob: **/routers.py, **/services.py, **/repositories.py, **/models.py
```

**For ER Diagram:**
```
Read: **/models.py
Grep: "class.*Base" in **/models.py
Grep: "ForeignKey" in **/models.py
Grep: "relationship" in **/models.py
```

**For Sequence Diagram:**
- Identify the use case to diagram
- Trace the call flow through layers

**For Data Flow:**
- Identify entry points (routers)
- Trace data transformation through layers

**For Deployment:**
- Check for Docker/Kubernetes configs
- Identify external services

### Step 2: Extract Entities

**Models:**
```python
# From models.py, extract:
- Table names
- Primary keys
- Foreign keys
- Relationships (1:1, 1:N, N:M)
```

**Services:**
```python
# From services.py, extract:
- Service names
- Dependencies (injected)
- Methods (public API)
```

**Routers:**
```python
# From routers.py, extract:
- Route prefixes
- Endpoints
- Dependencies
```

### Step 3: Generate Diagram

Based on extracted information, generate appropriate Mermaid diagram.

## Response Format

```markdown
## {{ type | capitalize }} Diagram

### Overview

{{ brief_description }}

### Diagram

```mermaid
{{ mermaid_code }}
```

### Legend

| Symbol | Meaning |
|--------|---------|
| {{ symbol }} | {{ meaning }} |

### Components Analyzed

| Component | Location | Dependencies |
|-----------|----------|--------------|
| {{ name }} | {{ file }} | {{ deps }} |

### Notes

{{ additional_notes }}

### Export Options

To export this diagram:
1. **VS Code**: Install Mermaid extension
2. **Online**: Use [Mermaid Live Editor](https://mermaid.live)
3. **CLI**: `npx @mermaid-js/mermaid-cli -i diagram.md -o diagram.png`

### Related Diagrams

- `/architect:diagram component` — High-level components
- `/architect:diagram er` — Database schema
- `/architect:diagram sequence` — Request flow
```
