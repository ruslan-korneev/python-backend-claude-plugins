# Code Smells

Code smell — a sign of a problem in the code. Not a bug, but an indicator of poor design.

## Bloaters

### Long Method / Function

**Problem**: Function does too much.

**Signs**:
- More than 20-30 lines
- Need to scroll to see the whole function
- Multiple levels of abstraction in one function
- Comments separate "sections" of the function

```python
# Bad
def process_order(order_data: dict) -> Order:
    # Validate order data
    if not order_data.get("items"):
        raise ValueError("No items")
    if not order_data.get("user_id"):
        raise ValueError("No user")
    for item in order_data["items"]:
        if item["quantity"] <= 0:
            raise ValueError("Invalid quantity")
        if item["price"] < 0:
            raise ValueError("Invalid price")

    # Calculate totals
    subtotal = 0
    for item in order_data["items"]:
        subtotal += item["quantity"] * item["price"]
    tax = subtotal * 0.2
    shipping = 10 if subtotal < 100 else 0
    total = subtotal + tax + shipping

    # Apply discounts
    discount = 0
    user = db.get_user(order_data["user_id"])
    if user.is_premium:
        discount = total * 0.1
    if order_data.get("promo_code"):
        promo = db.get_promo(order_data["promo_code"])
        if promo and promo.is_valid:
            discount += promo.discount_amount
    total -= discount

    # Create order
    order = Order(
        user_id=order_data["user_id"],
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        discount=discount,
        total=total,
    )

    # Save and notify
    db.save(order)
    for item in order_data["items"]:
        db.save(OrderItem(order_id=order.id, **item))
    email_service.send_confirmation(user.email, order)
    inventory_service.reserve(order_data["items"])

    return order


# Good — Extract Method
def process_order(order_data: dict) -> Order:
    validate_order_data(order_data)
    totals = calculate_totals(order_data["items"])
    discount = calculate_discount(order_data, totals.total)
    order = create_order(order_data, totals, discount)
    finalize_order(order, order_data["items"])
    return order


def validate_order_data(data: dict) -> None:
    if not data.get("items"):
        raise ValueError("No items")
    if not data.get("user_id"):
        raise ValueError("No user")
    for item in data["items"]:
        validate_item(item)


def calculate_totals(items: list[dict]) -> OrderTotals:
    subtotal = sum(item["quantity"] * item["price"] for item in items)
    tax = subtotal * 0.2
    shipping = 10 if subtotal < 100 else 0
    return OrderTotals(subtotal=subtotal, tax=tax, shipping=shipping)
```

**Refactoring**: Extract Method

---

### Long Parameter List

**Problem**: Function takes too many parameters.

**Signs**:
- More than 3-4 parameters
- Parameters are logically related
- Need to remember parameter order

```python
# Bad
def create_user(
    name: str,
    email: str,
    password: str,
    age: int,
    city: str,
    country: str,
    phone: str,
    role: str,
    department: str,
    manager_id: int | None,
) -> User:
    ...


# Good — Introduce Parameter Object
@dataclass
class CreateUserRequest:
    name: str
    email: str
    password: str
    age: int
    city: str
    country: str
    phone: str
    role: str
    department: str
    manager_id: int | None = None


def create_user(request: CreateUserRequest) -> User:
    ...


# Or group related parameters
@dataclass
class Address:
    city: str
    country: str


@dataclass
class Employment:
    role: str
    department: str
    manager_id: int | None = None


def create_user(
    name: str,
    email: str,
    password: str,
    age: int,
    address: Address,
    employment: Employment,
) -> User:
    ...
```

**Refactoring**: Introduce Parameter Object, Preserve Whole Object

---

### Large Class / God Class

**Problem**: Class knows and does too much.

**Signs**:
- More than 200-300 lines
- Many unrelated methods
- Many fields of different "topics"
- Name too generic: `Manager`, `Processor`, `Handler`

```python
# Bad — God Class
class UserManager:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def authenticate(self): ...
    def reset_password(self): ...
    def send_welcome_email(self): ...
    def send_password_reset_email(self): ...
    def generate_user_report(self): ...
    def export_users_to_csv(self): ...
    def import_users_from_csv(self): ...
    def validate_user_data(self): ...
    def calculate_user_statistics(self): ...


# Good — Extract Class
class UserRepository:
    def create(self, data: CreateUserDTO) -> User: ...
    def update(self, id: int, data: UpdateUserDTO) -> User: ...
    def delete(self, id: int) -> None: ...


class AuthenticationService:
    def authenticate(self, email: str, password: str) -> User: ...
    def reset_password(self, email: str) -> None: ...


class UserEmailService:
    def send_welcome(self, user: User) -> None: ...
    def send_password_reset(self, user: User, token: str) -> None: ...


class UserReportService:
    def generate_report(self, users: list[User]) -> Report: ...
    def export_to_csv(self, users: list[User]) -> bytes: ...


class UserImportService:
    def import_from_csv(self, data: bytes) -> list[User]: ...
```

**Refactoring**: Extract Class, apply SRP

---

## Object-Orientation Abusers

### Switch Statements / Long if-elif chains

**Problem**: Branching by object type.

**Signs**:
- `if/elif/elif...` by string type
- `match/case` by type
- Same switch in different places

```python
# Bad
def calculate_pay(employee: dict) -> float:
    if employee["type"] == "hourly":
        return employee["hours"] * employee["rate"]
    elif employee["type"] == "salaried":
        return employee["salary"] / 12
    elif employee["type"] == "commission":
        return employee["sales"] * employee["commission_rate"]


def generate_report(employee: dict) -> str:
    if employee["type"] == "hourly":
        return f"Hourly: {employee['hours']} hours"
    elif employee["type"] == "salaried":
        return f"Salaried: {employee['salary']}/year"
    elif employee["type"] == "commission":
        return f"Commission: {employee['sales']} sales"


# Good — Replace Conditional with Polymorphism
class Employee(ABC):
    @abstractmethod
    def calculate_pay(self) -> float: ...

    @abstractmethod
    def generate_report(self) -> str: ...


class HourlyEmployee(Employee):
    def __init__(self, hours: float, rate: float):
        self.hours = hours
        self.rate = rate

    def calculate_pay(self) -> float:
        return self.hours * self.rate

    def generate_report(self) -> str:
        return f"Hourly: {self.hours} hours"


class SalariedEmployee(Employee):
    def __init__(self, salary: float):
        self.salary = salary

    def calculate_pay(self) -> float:
        return self.salary / 12

    def generate_report(self) -> str:
        return f"Salaried: {self.salary}/year"
```

**Refactoring**: Replace Conditional with Polymorphism, Strategy Pattern

---

### Primitive Obsession

**Problem**: Using primitives instead of small objects.

**Signs**:
- Email as `str`, Money as `float`, Phone as `str`
- Validation of primitives scattered throughout code
- Special values: `-1` means "not found"

```python
# Bad
def create_user(email: str, phone: str, balance: float) -> User:
    # Validation scattered
    if "@" not in email:
        raise ValueError("Invalid email")
    if not phone.startswith("+"):
        raise ValueError("Invalid phone")
    if balance < 0:
        raise ValueError("Invalid balance")
    ...


def send_notification(phone: str) -> None:
    # Same validation
    if not phone.startswith("+"):
        raise ValueError("Invalid phone")
    ...


# Good — Value Objects
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")


@dataclass(frozen=True)
class Phone:
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("+"):
            raise ValueError(f"Invalid phone: {self.value}")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)


def create_user(email: Email, phone: Phone, balance: Money) -> User:
    # Validation already happened when objects were created
    ...
```

**Refactoring**: Replace Primitive with Object, Introduce Value Object

---

## Change Preventers

### Divergent Change

**Problem**: One class changes for different reasons.

**Signs**: DB changes -> modify class X. UI changes -> modify class X.

**Solution**: Extract Class, apply SRP.

---

### Shotgun Surgery

**Problem**: One change requires edits in many classes.

**Signs**: Adding a field -> edit 10 files.

**Solution**: Move Method, Move Field — gather related things together.

---

## Dispensables

### Dead Code

**Problem**: Code that never executes.

```python
# Bad
def process(value: int) -> int:
    if value > 0:
        return value * 2
    elif value <= 0:  # Always True if we didn't hit the first condition
        return value * 3
    else:
        return 0  # Dead code — never executes


# Commented out code
# def old_function():
#     ...
```

**Solution**: Delete — remove it. Git remembers history.

---

### Speculative Generality

**Problem**: Code "for the future" that isn't used.

```python
# Bad — YAGNI violation
class AbstractFactoryFactoryBuilder:
    """Might need it..."""
    pass


class User:
    plugin_system: PluginManager | None = None  # "For the future"
```

**Solution**: Delete. Add it when actually needed.

---

### Comments (as a smell)

**Problem**: Comments compensate for bad code.

```python
# Bad — comment explains unclear code
# Check if user is active and has permission to access premium content
if u.s == 1 and u.p & 4:
    ...

# Good — self-documenting code
if user.is_active and user.has_premium_access:
    ...
```

**When comments are needed**:
- Explaining "why", not "what"
- Warnings about non-obvious consequences
- TODOs with context
- Public API (docstrings)

---

## Couplers

### Feature Envy

**Problem**: Method is more interested in another class's data.

```python
# Bad — method envies Order's data
class OrderPrinter:
    def print_order(self, order: Order) -> str:
        return (
            f"Order #{order.id}\n"
            f"Items: {len(order.items)}\n"
            f"Subtotal: {order.subtotal}\n"
            f"Tax: {order.tax}\n"
            f"Total: {order.total}"
        )


# Good — method in the class with the data
class Order:
    def format_for_print(self) -> str:
        return (
            f"Order #{self.id}\n"
            f"Items: {len(self.items)}\n"
            f"Subtotal: {self.subtotal}\n"
            f"Tax: {self.tax}\n"
            f"Total: {self.total}"
        )
```

**Refactoring**: Move Method

---

### Inappropriate Intimacy

**Problem**: Classes know too much about each other.

```python
# Bad — Order reaches into User's internals
class Order:
    def apply_discount(self) -> None:
        if self.user._internal_loyalty_points > 1000:  # Private field!
            self.discount = self.user._calculate_internal_discount()


# Good — public interface
class User:
    def get_discount_percent(self) -> float:
        if self._internal_loyalty_points > 1000:
            return 0.1
        return 0


class Order:
    def apply_discount(self) -> None:
        self.discount = self.total * self.user.get_discount_percent()
```

**Refactoring**: Move Method, Hide Delegate, Extract Class
