---
name: clean-code:refactor
description: Suggest refactoring for a specific code smell
allowed_tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
arguments:
  - name: smell
    description: "Problem type: long-method, long-params, god-class, primitive, switch, duplicate"
    required: true
  - name: path
    description: Path to file
    required: true
---

# Command /clean:refactor

Suggest a specific refactoring for the indicated problem.

## Instructions

### Step 1: Determine refactoring type

| Smell | Refactoring |
|-------|-------------|
| `long-method` | Extract Method |
| `long-params` | Introduce Parameter Object |
| `god-class` | Extract Class |
| `primitive` | Replace Primitive with Object |
| `switch` | Replace Conditional with Polymorphism |
| `duplicate` | Extract Method / Pull Up Method |
| `feature-envy` | Move Method |
| `deep-nesting` | Replace Nested Conditional with Guard Clauses |

### Step 2: Read the code

Read the specified file and find the problematic area.

### Step 3: Suggest refactoring

#### Extract Method (long-method)

```python
# Before
def process_order(order):
    # Validate (10 lines)
    ...
    # Calculate (15 lines)
    ...
    # Save (10 lines)
    ...

# After
def process_order(order):
    validate_order(order)
    totals = calculate_totals(order)
    save_order(order, totals)

def validate_order(order): ...
def calculate_totals(order): ...
def save_order(order, totals): ...
```

#### Introduce Parameter Object (long-params)

```python
# Before
def create_user(name, email, age, city, country, phone): ...

# After
@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int
    city: str
    country: str
    phone: str

def create_user(request: CreateUserRequest): ...
```

#### Extract Class (god-class)

```python
# Before
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# After
class UserRepository:
    def create(self): ...

class EmailService:
    def send(self): ...

class ReportGenerator:
    def generate(self): ...
```

#### Replace Primitive with Object

```python
# Before
email: str = "test@example.com"

# After
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")
```

#### Guard Clauses (deep-nesting)

```python
# Before
def process(user):
    if user:
        if user.is_active:
            if user.has_permission:
                return do_work(user)
    return None

# After
def process(user):
    if not user:
        return None
    if not user.is_active:
        return None
    if not user.has_permission:
        return None
    return do_work(user)
```

### Step 4: Ask for confirmation

Before applying changes, ask the user:
- Show diff of changes
- Confirm application

## Response Format

```markdown
## Refactoring: {{ smell }}

### Problem

File: `{{ path }}`
Lines: X-Y

```python
# Current code
```

### Proposed Solution

**Refactoring type**: Extract Method

```python
# After refactoring
```

### Steps

1. Create function `validate_order()`
2. Move lines X-Y to the new function
3. Replace original code with function call

### Apply?

- [ ] Yes, apply changes
- [ ] Show diff
- [ ] Cancel
```
