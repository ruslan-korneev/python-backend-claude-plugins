# API Semantics Checklist

The most critical level of code review. API issues are expensive to fix later.

## Core Principles

### 1. Minimal and Sufficient

- Does the API expose only what's needed?
- Is there unnecessary functionality?
- Any missing essential operations?

```python
# ❌ Over-exposed API
class UserService:
    def get_user(self, id): ...
    def get_user_by_email(self, email): ...
    def get_user_by_username(self, username): ...
    def get_user_by_phone(self, phone): ...
    def get_users_by_role(self, role): ...
    def get_active_users(self): ...
    def get_inactive_users(self): ...

# ✅ Minimal API with flexible query
class UserService:
    def get_user(self, id): ...
    def find_users(self, filters: UserFilters): ...
```

### 2. One Way to Do Things

- Is there only one obvious way to accomplish each task?
- Multiple paths to same result = confusion

```python
# ❌ Multiple ways
user.save()
user_repo.save(user)
db.session.add(user)

# ✅ Single way
user_repo.save(user)
```

### 3. Principle of Least Surprise

- Does it behave as expected?
- Method names match their behavior?
- No hidden side effects?

```python
# ❌ Surprising behavior
def get_user(self, id):
    user = self.repo.find(id)
    user.last_accessed = datetime.now()  # Side effect!
    return user

# ✅ No surprises
def get_user(self, id):
    return self.repo.find(id)
```

### 4. Consistent Naming

- Follows project conventions?
- Similar operations named similarly?

```python
# ❌ Inconsistent
def get_user(id): ...
def fetch_order(id): ...
def retrieve_product(id): ...

# ✅ Consistent
def get_user(id): ...
def get_order(id): ...
def get_product(id): ...
```

## REST API Checklist

### HTTP Methods

| Operation      | Method | Idempotent? |
| -------------- | ------ | ----------- |
| Read           | GET    | Yes         |
| Create         | POST   | No          |
| Full update    | PUT    | Yes         |
| Partial update | PATCH  | Yes         |
| Delete         | DELETE | Yes         |

### URL Structure

```
# ❌ Bad
POST /getUserById
GET /users/delete/123
POST /api/v1/users/create

# ✅ Good
GET /users/{id}
DELETE /users/{id}
POST /users
```

### Status Codes

| Scenario            | Code                      |
| ------------------- | ------------------------- |
| Success (with body) | 200 OK                    |
| Created             | 201 Created               |
| Accepted (async)    | 202 Accepted              |
| Success (no body)   | 204 No Content            |
| Bad request         | 400 Bad Request           |
| Unauthorized        | 401 Unauthorized          |
| Forbidden           | 403 Forbidden             |
| Not found           | 404 Not Found             |
| Conflict            | 409 Conflict              |
| Validation error    | 422 Unprocessable Entity  |
| Server error        | 500 Internal Server Error |

### Request/Response Design

```python
# ❌ Inconsistent responses
# GET /users returns: [{"id": 1, "name": "John"}]
# GET /users/1 returns: {"user": {"id": 1, "name": "John"}}

# ✅ Consistent
# GET /users returns: {"data": [...], "meta": {...}}
# GET /users/1 returns: {"data": {...}}
```

## Breaking Changes

### What Counts as Breaking?

- Removing endpoints/fields
- Renaming endpoints/fields
- Changing types
- Adding required parameters
- Changing behavior

### Non-Breaking Changes

- Adding optional fields
- Adding new endpoints
- Adding optional parameters
- Deprecating (not removing)

### If Breaking Change Required

1. Is it absolutely necessary?
2. Can we version the API?
3. Can we support both temporarily?
4. Is migration path documented?

## Review Questions

### For New APIs

- [ ] Is this the minimal API needed?
- [ ] Will this be easy to extend later?
- [ ] Does naming follow project conventions?
- [ ] Is the contract clearly documented?

### For API Changes

- [ ] Is this a breaking change?
- [ ] If breaking, is it justified?
- [ ] Are consumers notified?
- [ ] Is backward compatibility possible?

### For REST Endpoints

- [ ] Correct HTTP methods?
- [ ] Correct status codes?
- [ ] Consistent URL structure?
- [ ] Request validation clear?
- [ ] Response schema documented?

## Common Issues

### Over-Engineering

```python
# ❌ YAGNI violation
class UserService:
    def get_user(self, id, include_deleted=False,
                 include_relations=None, cache_ttl=None,
                 read_preference='primary', ...): ...

# ✅ Start simple
class UserService:
    def get_user(self, id): ...
```

### Leaky Abstractions

```python
# ❌ Internal implementation exposed
class UserAPI:
    async def get_user(self, id, session: AsyncSession): ...

# ✅ Clean abstraction
class UserAPI:
    async def get_user(self, id): ...
```

### Inconsistent Error Handling

```python
# ❌ Different error formats
# Endpoint A: {"error": "Not found"}
# Endpoint B: {"message": "Not found", "code": 404}
# Endpoint C: {"errors": [{"detail": "Not found"}]}

# ✅ Consistent format
# All endpoints: {"error": {"code": "NOT_FOUND", "message": "..."}}
```
