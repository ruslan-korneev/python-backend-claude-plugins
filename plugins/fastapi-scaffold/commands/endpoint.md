---
name: fastapi:endpoint
description: Create a new endpoint with service and test
allowed_tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - name: method
    description: "HTTP method: GET, POST, PATCH, PUT, DELETE"
    required: true
  - name: path
    description: "Endpoint path (e.g.: /users/{id}/orders)"
    required: true
  - name: module
    description: "Module to add to (e.g.: users)"
    required: true
  - name: description
    description: "Description of what the endpoint does"
    required: false
---

# Command /fastapi:endpoint

Create a new endpoint with service and test.

## Instructions

### Step 1: Analyze existing module

Read module files:
- `src/modules/{{ module }}/routers.py`
- `src/modules/{{ module }}/services.py`
- `src/modules/{{ module }}/dto.py`

### Step 2: Determine what needs to be created

Based on `{{ method }} {{ path }}` determine:
- Are new DTOs needed
- Is a new service method needed
- Is a new repository method needed

### Step 3: Create components

#### Endpoint in routers.py

```python
@router.{{ method | lower }}("{{ path }}")
@inject
async def {{ endpoint_name }}(
    # Path parameters from {{ path }}
    id: int,
    # Body for POST/PATCH/PUT
    data: {{ DTO }}DTO,
    # DI
    service: Annotated[
        {{ module | capitalize }}Service,
        Depends(Provide[Container.{{ module }}_service]),
    ],
) -> {{ ResponseDTO }}:
    """{{ description }}."""
    return await service.{{ method_name }}(id, data)
```

#### Method in services.py

```python
async def {{ method_name }}(self, ...) -> {{ ReturnType }}:
    """{{ description }}."""
    # Business logic
    pass
```

#### Test in test_routers.py

```python
class Test{{ endpoint_name | capitalize }}:
    """Tests for {{ method }} {{ path }}."""

    async def test_{{ endpoint_name }}_success(
        self,
        client: AsyncClient,
    ) -> None:
        """Successfully {{ description | lower }}."""
        response = await client.{{ method | lower }}(
            "{{ path }}",
            json={...} if "{{ method }}" in ["POST", "PATCH", "PUT"] else None,
        )

        assert response.status_code == {{ expected_status }}

    async def test_{{ endpoint_name }}_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """{{ endpoint_name }} returns 404 when resource not found."""
        response = await client.{{ method | lower }}("{{ path_with_invalid_id }}")

        assert response.status_code == 404
```

## Examples

### GET /users/{user_id}/orders

```python
# routers.py
@router.get("/{user_id}/orders")
@inject
async def get_user_orders(
    user_id: int,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> list[OrderReadDTO]:
    """Get all orders for user."""
    return await service.get_orders(user_id)

# services.py
async def get_orders(self, user_id: int) -> list[OrderReadDTO]:
    """Get all orders for user."""
    user = await self.get_by_id(user_id)  # Validates user exists
    return await self._order_repository.get_by_user_id(user_id)
```

### POST /users/{user_id}/activate

```python
# routers.py
@router.post("/{user_id}/activate", status_code=status.HTTP_200_OK)
@inject
async def activate_user(
    user_id: int,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> UserReadDTO:
    """Activate user account."""
    return await service.activate(user_id)

# services.py
async def activate(self, user_id: int) -> UserReadDTO:
    """Activate user account."""
    user = await self.get_by_id(user_id)
    if user.is_active:
        raise ConflictError("User is already active")
    return await self._repository.update(user_id, {"is_active": True})
```

### DELETE /users/{user_id}/sessions

```python
# routers.py
@router.delete("/{user_id}/sessions", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout_all_sessions(
    user_id: int,
    service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> None:
    """Logout user from all sessions."""
    await service.logout_all(user_id)
```

## Status codes

- `GET` → 200 OK
- `POST` (create) → 201 Created
- `POST` (action) → 200 OK
- `PATCH/PUT` → 200 OK
- `DELETE` → 204 No Content

## Response Format

```
## Endpoint created: {{ method }} {{ path }}

### Added to routers.py
```python
[endpoint code]
```

### Added to services.py
```python
[service method code]
```

### Test created
`tests/modules/{{ module }}/test_routers.py`

### Run test
```bash
pytest tests/modules/{{ module }}/test_routers.py::Test{{ endpoint_name | capitalize }} -v
```
```
