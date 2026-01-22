---
name: architect:review
description: Analyze project architecture (structure, dependencies, patterns, anti-patterns)
allowed_tools:
  - Read
  - Glob
  - Grep
  - Task
arguments:
  - name: path
    description: "Path to analyze (default: src/)"
    required: false
---

# Command /architect:review

Comprehensive architecture review for Python backend projects.

## Instructions

### Step 1: Discover Project Structure

Use `Glob` to map the project:

```
# Find main structure
Glob: **/main.py, **/app.py, **/wsgi.py
Glob: **/__init__.py
Glob: **/models.py, **/services.py, **/routers.py, **/repositories.py

# Find configuration
Glob: **/config.py, **/settings.py, **/.env.example

# Find tests
Glob: **/test_*.py, **/*_test.py, **/conftest.py
```

### Step 2: Analyze Layer Architecture

Check if proper separation exists:

| Layer | Files | Responsibility |
|-------|-------|----------------|
| Presentation | `routers.py`, `views.py` | HTTP handling, DTOs |
| Application | `services.py` | Business logic |
| Domain | `models.py` | Entities, business rules |
| Infrastructure | `repositories.py` | Data access |

**Check violations:**
- Business logic in routers (should be in services)
- Direct DB access in services (should be via repositories)
- Models returning DTOs (should return domain objects)

### Step 3: Check Module Boundaries

For each module, verify:

1. **Cohesion**: Related functionality grouped together
2. **Coupling**: Minimal dependencies on other modules
3. **Encapsulation**: Clear public API (`__init__.py` exports)

```python
# Check for cross-module imports
Grep: "from src.modules.users" in orders/
Grep: "from src.modules.orders" in users/
```

**Circular dependencies:**
```
Module A imports Module B
Module B imports Module A  ← Problem!
```

### Step 4: Analyze Dependency Injection

Check how dependencies are managed:

**Good patterns:**
```python
# Constructor injection
class UserService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

# DI container (dependency-injector)
user_service = providers.Factory(UserService, repository=user_repository)
```

**Bad patterns:**
```python
# Hard-coded dependencies
class UserService:
    def __init__(self):
        self._repository = UserRepository()  # Tight coupling!

# Global instances
user_service = UserService()  # Global state!
```

### Step 5: Review Data Model

Analyze SQLAlchemy models:

1. **Relationships**: Are they properly defined?
2. **Indexes**: Are frequently queried fields indexed?
3. **Normalization**: Appropriate level of normalization?
4. **Naming**: Consistent naming conventions?

```python
# Check for relationship issues
Grep: "relationship(" in **/models.py
Grep: "ForeignKey" in **/models.py
Grep: "index=True" in **/models.py
```

### Step 6: Check API Design

Review REST API patterns:

1. **URL structure**: RESTful resource naming
2. **HTTP methods**: Correct usage (GET, POST, PUT, PATCH, DELETE)
3. **Status codes**: Appropriate responses
4. **DTOs**: Separate input/output schemas

```python
# Check routers
Read: **/routers.py
```

### Step 7: Identify Anti-Patterns

Look for common architectural mistakes:

| Anti-Pattern | Detection Method |
|--------------|------------------|
| God Object | Class with >20 methods, >500 lines |
| Tight Coupling | Direct class instantiation in code |
| Circular Deps | Import statements inside functions |
| Anemic Domain | Models with no methods, all logic in services |
| Big Ball of Mud | No clear module structure |
| Shared Database | Multiple modules writing to same tables |

### Step 8: Security Review

Check security practices:

1. **Input validation**: Pydantic models with constraints
2. **Authentication**: JWT/session handling
3. **Authorization**: Permission checks
4. **SQL Injection**: Parameterized queries
5. **Secrets**: Not hardcoded

```python
# Check for hardcoded secrets
Grep: "password\s*=\s*['\"]"
Grep: "secret\s*=\s*['\"]"
Grep: "api_key\s*=\s*['\"]"
```

### Step 9: Scalability Assessment

Evaluate scalability readiness:

1. **Stateless**: No in-memory state between requests
2. **Async**: Async database operations
3. **Caching**: Proper caching strategy
4. **Database**: Connection pooling, read replicas support

## Review Checklist

### Structure
- [ ] Clear module boundaries
- [ ] Layered architecture (Router → Service → Repository)
- [ ] No circular dependencies
- [ ] Proper `__init__.py` exports

### Dependencies
- [ ] Constructor injection used
- [ ] DI container configured
- [ ] No global mutable state
- [ ] Interfaces/Protocols for dependencies

### Data Model
- [ ] Models properly typed (SQLAlchemy 2.0 style)
- [ ] Relationships correctly defined
- [ ] Indexes on frequently queried fields
- [ ] Soft delete pattern (if applicable)

### API Design
- [ ] RESTful URLs
- [ ] Correct HTTP methods
- [ ] Proper status codes
- [ ] Input/output DTOs

### Security
- [ ] Input validation
- [ ] No hardcoded secrets
- [ ] Parameterized queries
- [ ] Authentication/authorization checks

### Scalability
- [ ] Stateless services
- [ ] Async database operations
- [ ] Caching where appropriate
- [ ] Pagination for list endpoints

## Response Format

```markdown
## Architecture Review: {{ project_name }}

### Summary
| Aspect | Score | Status |
|--------|-------|--------|
| Structure | {{ score }}/5 | {{ status }} |
| Dependencies | {{ score }}/5 | {{ status }} |
| Data Model | {{ score }}/5 | {{ status }} |
| API Design | {{ score }}/5 | {{ status }} |
| Security | {{ score }}/5 | {{ status }} |
| Scalability | {{ score }}/5 | {{ status }} |

**Overall**: {{ overall_score }}/30 — {{ overall_status }}

### Project Structure

```
{{ current_structure }}
```

**Assessment**: {{ structure_assessment }}

### Layer Analysis

| Layer | Files Found | Issues |
|-------|-------------|--------|
| Presentation | {{ files }} | {{ issues }} |
| Application | {{ files }} | {{ issues }} |
| Domain | {{ files }} | {{ issues }} |
| Infrastructure | {{ files }} | {{ issues }} |

### Module Dependencies

```mermaid
graph TD
    {{ dependency_graph }}
```

**Circular Dependencies**: {{ circular_deps }}

### Anti-Patterns Found

#### Critical
- **{{ anti_pattern }}** at `{{ location }}`
  - Impact: {{ impact }}
  - Fix: {{ recommendation }}

#### Warning
- **{{ anti_pattern }}** at `{{ location }}`
  - Recommendation: {{ recommendation }}

### Security Issues

| Issue | Severity | Location | Fix |
|-------|----------|----------|-----|
| {{ issue }} | {{ severity }} | {{ location }} | {{ fix }} |

### Recommendations

#### Immediate (This Week)
1. {{ recommendation_1 }}
2. {{ recommendation_2 }}

#### Short-term (This Month)
1. {{ recommendation_3 }}
2. {{ recommendation_4 }}

#### Long-term (Next Quarter)
1. {{ recommendation_5 }}

### Reference
- `/architect:diagram component` — Generate component diagram
- `/architect:deps` — Detailed dependency analysis
- `/architect:adr "Fix circular dependencies"` — Document decision
```
