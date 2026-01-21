# Clean Code Principles

## DRY — Don't Repeat Yourself

**Every piece of knowledge must have a single, unambiguous representation in the system.**

### Types of Duplication

#### 1. Code Duplication

```python
# Bad — copy-paste
def create_admin_user(data: dict) -> User:
    if not data.get("email"):
        raise ValueError("Email required")
    if not data.get("password"):
        raise ValueError("Password required")
    if len(data["password"]) < 8:
        raise ValueError("Password too short")
    user = User(**data, role="admin")
    db.save(user)
    return user


def create_regular_user(data: dict) -> User:
    if not data.get("email"):
        raise ValueError("Email required")
    if not data.get("password"):
        raise ValueError("Password required")
    if len(data["password"]) < 8:
        raise ValueError("Password too short")
    user = User(**data, role="user")
    db.save(user)
    return user


# Good — abstraction
def validate_user_data(data: dict) -> None:
    if not data.get("email"):
        raise ValueError("Email required")
    if not data.get("password"):
        raise ValueError("Password required")
    if len(data["password"]) < 8:
        raise ValueError("Password too short")


def create_user(data: dict, role: str) -> User:
    validate_user_data(data)
    user = User(**data, role=role)
    db.save(user)
    return user
```

#### 2. Logic Duplication

```python
# Bad — same logic in different places
class Order:
    def total_with_tax(self) -> float:
        return self.subtotal * 1.2  # 20% tax


class Invoice:
    def calculate_tax(self, amount: float) -> float:
        return amount * 0.2  # 20% tax


# Good — single source of truth
TAX_RATE = 0.2


def calculate_tax(amount: float) -> float:
    return amount * TAX_RATE


class Order:
    def total_with_tax(self) -> float:
        return self.subtotal + calculate_tax(self.subtotal)
```

#### 3. Data Duplication

```python
# Bad — data in multiple places
class User:
    first_name: str
    last_name: str
    full_name: str  # Duplication!


# Good — computed property
class User:
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

### When NOT to Apply DRY

```python
# Coincidental similarity — NOT a DRY violation
def validate_email(email: str) -> bool:
    return "@" in email and "." in email


def validate_url(url: str) -> bool:
    return "." in url and url.startswith("http")


# Code looks similar, but these are DIFFERENT domains!
# Merging them would be a mistake
```

**Rule**: Code duplication is not always a DRY violation. DRY is about knowledge, not code.

---

## KISS — Keep It Simple, Stupid

**Simplicity is the main design goal. Avoid unnecessary complexity.**

### Examples

```python
# Bad — overengineering
class UserValidationStrategyFactory:
    def create_strategy(self, user_type: str) -> AbstractValidationStrategy:
        strategies = {
            "admin": AdminValidationStrategy,
            "user": UserValidationStrategy,
        }
        return strategies.get(user_type, DefaultValidationStrategy)()


class AbstractValidationStrategy(ABC):
    @abstractmethod
    def validate(self, data: dict) -> ValidationResult: ...


# Good — simple
def validate_user(data: dict) -> bool:
    return bool(data.get("email") and data.get("name"))
```

```python
# Bad — clever code
result = [x for x in (y.strip() for y in data.split(",")) if x and not x.startswith("#")]

# Good — clear code
def parse_values(data: str) -> list[str]:
    values = []
    for item in data.split(","):
        item = item.strip()
        if item and not item.startswith("#"):
            values.append(item)
    return values
```

### Signs of KISS Violation

- Code requires comments to understand
- Hard to explain to a colleague what the code does
- Many levels of abstraction for a simple task
- "Clever" one-liners

### Rule

> Debugging is twice as hard as writing the code. If you write code as cleverly as possible, you are by definition not smart enough to debug it.
> — Brian Kernighan

---

## YAGNI — You Aren't Gonna Need It

**Don't add functionality until it's needed.**

### Examples

```python
# Bad — features "for the future"
class User:
    id: int
    name: str
    email: str
    # "Might need it"
    phone: str | None = None
    fax: str | None = None
    secondary_email: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    twitter: str | None = None
    linkedin: str | None = None
    github: str | None = None


class UserService:
    def get_user(self, id: int) -> User: ...
    def create_user(self, data: dict) -> User: ...
    # "For the future"
    def export_to_xml(self, user: User) -> str: ...
    def import_from_xml(self, xml: str) -> User: ...
    def sync_with_ldap(self, user: User) -> None: ...
    def generate_qr_code(self, user: User) -> bytes: ...


# Good — only what's needed now
class User:
    id: int
    name: str
    email: str


class UserService:
    def get_user(self, id: int) -> User: ...
    def create_user(self, data: dict) -> User: ...
```

### Why YAGNI Matters

1. **Code that isn't written doesn't need maintenance**
2. **Requirements change** — the "needed" feature may never be required
3. **Premature abstractions** are often wrong
4. **Time** — spent on unnecessary things could be spent on necessary ones

### Exceptions

- Public APIs — breaking changes are expensive
- Security — better to be safe
- Architectural decisions — hard to change later

---

## Composition over Inheritance

**Prefer composition over inheritance.**

### Problems with Inheritance

```python
# Bad — fragile hierarchy
class Animal:
    def move(self): ...
    def eat(self): ...


class Bird(Animal):
    def fly(self): ...


class Penguin(Bird):  # Penguins don't fly!
    def fly(self):
        raise NotImplementedError


# Bad — multiple inheritance
class FlyingSwimmingBird(FlyingAnimal, SwimmingAnimal):
    pass  # Diamond problem
```

### Composition

```python
# Good — composition through protocols
class CanFly(Protocol):
    def fly(self) -> None: ...


class CanSwim(Protocol):
    def swim(self) -> None: ...


class CanWalk(Protocol):
    def walk(self) -> None: ...


# Behaviors as separate classes
class FlightBehavior:
    def fly(self) -> None:
        print("Flying!")


class SwimBehavior:
    def swim(self) -> None:
        print("Swimming!")


class WalkBehavior:
    def walk(self) -> None:
        print("Walking!")


# Behavior composition
class Duck:
    def __init__(self):
        self._flight = FlightBehavior()
        self._swim = SwimBehavior()
        self._walk = WalkBehavior()

    def fly(self) -> None:
        self._flight.fly()

    def swim(self) -> None:
        self._swim.swim()

    def walk(self) -> None:
        self._walk.walk()


class Penguin:
    def __init__(self):
        self._swim = SwimBehavior()
        self._walk = WalkBehavior()
        # No _flight — penguin doesn't fly

    def swim(self) -> None:
        self._swim.swim()

    def walk(self) -> None:
        self._walk.walk()
```

---

## Fail Fast

**System should fail as early as possible when an error is detected.**

```python
# Bad — error manifests later
def process_order(order: Order | None) -> None:
    # Lots of code...
    # ...
    # ...
    if order:  # Check at the end — too late!
        save(order)


# Good — fail fast
def process_order(order: Order | None) -> None:
    if order is None:
        raise ValueError("Order cannot be None")

    # Now order is definitely not None
    validate(order)
    calculate(order)
    save(order)
```

### Guard Clauses

```python
# Bad — deep nesting
def calculate_pay(employee: Employee) -> float:
    if employee is not None:
        if employee.is_active:
            if employee.salary is not None:
                if employee.hours_worked >= 0:
                    return employee.salary * employee.hours_worked
    return 0


# Good — guard clauses
def calculate_pay(employee: Employee | None) -> float:
    if employee is None:
        return 0
    if not employee.is_active:
        return 0
    if employee.salary is None:
        return 0
    if employee.hours_worked < 0:
        return 0

    return employee.salary * employee.hours_worked
```

---

## Law of Demeter

**An object should only interact with its immediate "friends".**

```python
# Bad — call chain
total = order.customer.wallet.balance.amount

# Good — delegation method
total = order.get_customer_balance()


# Bad
def send_notification(order: Order) -> None:
    email = order.customer.contact_info.primary_email.address
    send_email(email, "Order shipped")


# Good
def send_notification(order: Order) -> None:
    email = order.get_notification_email()
    send_email(email, "Order shipped")


class Order:
    def get_notification_email(self) -> str:
        return self.customer.get_primary_email()
```

### Rule: Only talk to

- `self`
- Method parameters
- Objects created inside the method
- Direct components of `self`
