# Clean Code Patterns

Clean code principles for Python. Code should read like well-written prose.

## Triggers

Use this skill when:
- Code is hard to read or understand
- Function/class does too much
- Refactoring is needed
- Code review revealed issues
- Questions about SOLID, DRY, KISS

## SOLID

More details: `${CLAUDE_PLUGIN_ROOT}/skills/clean-code-patterns/references/solid.md`

### S — Single Responsibility

```python
# Bad — class does everything
class UserService:
    def create_user(self, data): ...
    def send_welcome_email(self, user): ...
    def generate_report(self, users): ...
    def export_to_csv(self, users): ...

# Good — each class = one responsibility
class UserService:
    def create_user(self, data): ...

class EmailService:
    def send_welcome_email(self, user): ...

class UserReportGenerator:
    def generate(self, users): ...
    def export_to_csv(self, users): ...
```

### O — Open/Closed

```python
# Bad — modify code when adding new type
def calculate_discount(order_type: str, amount: float) -> float:
    if order_type == "regular":
        return amount * 0.1
    elif order_type == "premium":
        return amount * 0.2
    elif order_type == "vip":  # Added new type — modified function
        return amount * 0.3

# Good — extend through new classes
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float: ...

class RegularDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount * 0.1

class PremiumDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount * 0.2

# Add VIP — create new class, don't modify existing code
class VIPDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount * 0.3
```

### L — Liskov Substitution

```python
# Bad — subclass violates parent's contract
class Bird:
    def fly(self) -> None: ...

class Penguin(Bird):
    def fly(self) -> None:
        raise NotImplementedError("Penguins can't fly")  # LSP violation!

# Good — correct hierarchy
class Bird:
    def move(self) -> None: ...

class FlyingBird(Bird):
    def fly(self) -> None: ...

class Penguin(Bird):
    def move(self) -> None:
        self.swim()
```

### I — Interface Segregation

```python
# Bad — fat interface
class Worker(Protocol):
    def work(self) -> None: ...
    def eat(self) -> None: ...
    def sleep(self) -> None: ...

class Robot:  # Robot doesn't need eat and sleep!
    def work(self) -> None: ...
    def eat(self) -> None: raise NotImplementedError
    def sleep(self) -> None: raise NotImplementedError

# Good — small interfaces
class Workable(Protocol):
    def work(self) -> None: ...

class Eatable(Protocol):
    def eat(self) -> None: ...

class Robot:  # Implements only what's needed
    def work(self) -> None: ...
```

### D — Dependency Inversion

```python
# Bad — dependency on concrete implementation
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard coupling!
        self.email = SendGridClient()  # Hard coupling!

# Good — dependency on abstractions
class OrderService:
    def __init__(
        self,
        db: DatabaseProtocol,
        email: EmailServiceProtocol,
    ):
        self.db = db
        self.email = email
```

## DRY / KISS / YAGNI

More details: `${CLAUDE_PLUGIN_ROOT}/skills/clean-code-patterns/references/principles.md`

### DRY — Don't Repeat Yourself

```python
# Bad — copy-paste
def create_admin(data):
    validate_email(data["email"])
    validate_password(data["password"])
    user = User(**data, role="admin")
    db.save(user)
    send_welcome_email(user)
    return user

def create_moderator(data):
    validate_email(data["email"])
    validate_password(data["password"])
    user = User(**data, role="moderator")
    db.save(user)
    send_welcome_email(user)
    return user

# Good — abstraction
def create_user(data: dict, role: str) -> User:
    validate_email(data["email"])
    validate_password(data["password"])
    user = User(**data, role=role)
    db.save(user)
    send_welcome_email(user)
    return user
```

### KISS — Keep It Simple

```python
# Bad — overengineering
class UserValidatorFactory:
    def create_validator(self, user_type: str) -> AbstractValidator:
        return self._validators[user_type]()

# Good — simple solution
def validate_user(user: User) -> bool:
    return user.email and user.name
```

### YAGNI — You Aren't Gonna Need It

```python
# Bad — features "for the future"
class User:
    name: str
    email: str
    phone: str | None  # "Might need it"
    fax: str | None    # "Just in case"
    secondary_email: str | None  # "Could be useful"

# Good — only what's needed now
class User:
    name: str
    email: str
```

## Code Smells

More details: `${CLAUDE_PLUGIN_ROOT}/skills/clean-code-patterns/references/code-smells.md`

### Long Functions

```python
# Bad — 100+ line function
def process_order(order):
    # validation (20 lines)
    # discount calculation (30 lines)
    # inventory update (25 lines)
    # notification sending (25 lines)
    ...

# Good — decomposition
def process_order(order: Order) -> ProcessedOrder:
    validated = validate_order(order)
    with_discount = apply_discounts(validated)
    update_inventory(with_discount)
    notify_customer(with_discount)
    return with_discount
```

### Too Many Parameters

```python
# Bad — too many parameters
def create_user(name, email, age, city, country, phone, role, department): ...

# Good — Parameter Object
@dataclass
class CreateUserRequest:
    name: str
    email: str
    age: int
    city: str
    country: str
    phone: str
    role: str
    department: str

def create_user(request: CreateUserRequest): ...
```

### Nested Conditionals

```python
# Bad — deep nesting
def process(user):
    if user:
        if user.is_active:
            if user.has_permission:
                if user.balance > 0:
                    return do_something(user)
    return None

# Good — guard clauses (early return)
def process(user):
    if not user:
        return None
    if not user.is_active:
        return None
    if not user.has_permission:
        return None
    if user.balance <= 0:
        return None
    return do_something(user)
```

## Naming

More details: `${CLAUDE_PLUGIN_ROOT}/skills/clean-code-patterns/references/naming.md`

### Variables

```python
# Bad
d = 86400
u = get_user()
tmp = calculate()

# Good
SECONDS_IN_DAY = 86400
current_user = get_user()
total_price = calculate()
```

### Boolean Variables

```python
# Bad
flag = True
status = False
check = user.admin

# Good
is_active = True
has_permission = False
is_admin = user.admin
```

### Functions

```python
# Bad — unclear what it does
def process(data): ...
def handle(x): ...
def do_stuff(): ...

# Good — verb + noun
def calculate_total_price(items): ...
def send_welcome_email(user): ...
def validate_order_items(order): ...
```

## Plugin Commands

- `/clean:review` — analyze code for code smells
- `/clean:refactor <smell>` — suggest refactoring
