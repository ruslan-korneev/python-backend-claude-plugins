# Why NEVER Use type: ignore

## Principle

**Every type error indicates a potential problem.** `type: ignore` doesn't solve the problem — it hides it.

## Problems with type: ignore

### 1. Bug Masking

```python
# With type: ignore the bug hides
def get_user(id: int) -> User:
    result = db.query(User).get(id)  # Can return None!
    return result  # type: ignore[return-value]

# Truth comes out at runtime
get_user(999).name  # AttributeError: 'NoneType' has no attribute 'name'
```

### 2. False Sense of Security

```python
# type: ignore says "everything is fine", but it's not
def process(data: dict[str, int]) -> int:
    return data["key"]  # type: ignore

# Runtime error if "key" doesn't exist
process({})  # KeyError: 'key'
```

### 3. Technical Debt

```python
# Starts with one
result = api_call()  # type: ignore

# A month later
result = api_call()  # type: ignore
data = parse(result)  # type: ignore
value = transform(data)  # type: ignore[arg-type]
final = validate(value)  # type: ignore[return-value]
```

### 4. Loss of Refactoring Safety

```python
# If you change the function signature
def process(data: str) -> str:  # Was list[str]
    return data.upper()

# type: ignore will hide the error
result = process(["a", "b"])  # type: ignore
# Runtime error: AttributeError: 'list' object has no attribute 'upper'
```

## Correct Alternatives

### Instead of ignore — Fix the Code

```python
# Bad
def get_user(id: int) -> User:
    return db.get(id)  # type: ignore

# Good
def get_user(id: int) -> User | None:
    return db.get(id)

# Or with exception
def get_user(id: int) -> User:
    user = db.get(id)
    if user is None:
        raise NotFoundError(f"User {id} not found")
    return user
```

### Instead of ignore — Add Annotations

```python
# Bad
def process(items):  # type: ignore
    return [x * 2 for x in items]

# Good
def process(items: list[int]) -> list[int]:
    return [x * 2 for x in items]
```

### Instead of ignore — Use TypeGuard

```python
# Bad
def process(data: object) -> str:
    return data.upper()  # type: ignore

# Good
from typing import TypeGuard

def is_string(val: object) -> TypeGuard[str]:
    return isinstance(val, str)

def process(data: object) -> str:
    if is_string(data):
        return data.upper()
    raise TypeError("Expected string")
```

### Instead of ignore — Use Protocol

```python
# Bad
def serialize(obj) -> str:  # type: ignore
    return obj.to_json()

# Good
from typing import Protocol

class Serializable(Protocol):
    def to_json(self) -> str: ...

def serialize(obj: Serializable) -> str:
    return obj.to_json()
```

## When It Seems Like ignore Is the Only Way Out

### "Library is not typed"

```python
# Bad
import untyped_lib
result = untyped_lib.process(data)  # type: ignore

# Good — create a stub or wrapper
# stubs/untyped_lib.pyi
def process(data: dict[str, Any]) -> list[str]: ...

# Or a wrapper with types
def typed_process(data: dict[str, Any]) -> list[str]:
    return untyped_lib.process(data)
```

### "Mypy doesn't understand my code"

```python
# Bad
value = complex_expression  # type: ignore

# Good — break into steps
intermediate: ExpectedType = step_one()
value: FinalType = step_two(intermediate)
```

### "This is legacy code"

```python
# Bad
def legacy_function():  # type: ignore
    ...

# Good — add types gradually
def legacy_function() -> None:  # Start with return type
    ...
```

## Exception: External Code

The only acceptable case — when the problem is in an external library and there's no way to fix it:

```python
# Only if the library has a bug in types
from buggy_lib import broken_function

result = broken_function()  # type: ignore[return-value]  # FIXME: buggy_lib#123
```

And even then:
1. Add a reference to the issue
2. Isolate it in one place
3. Create a wrapper when possible

## Conclusion

`type: ignore` is an admission of defeat. Instead:

1. **Understand the error** — what is mypy trying to say?
2. **Fix the code** — add types, checks, annotations
3. **Use the right patterns** — TypeGuard, Protocol, overload

Every `type: ignore` is a potential bug in production.
