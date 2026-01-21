# SOLID Principles

## S — Single Responsibility Principle (SRP)

**A class should have only one reason to change.**

### Signs of Violation

- Class has the word "And" in its description: "This class does X **and** Y"
- Changes in different parts of the system require changing the same class
- Class imports modules from different domains (email + database + pdf)

### Examples

```python
# Bad — multiple reasons to change
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def save(self) -> None:
        """Save to DB — reason 1"""
        db.execute("INSERT INTO users ...")

    def send_email(self, message: str) -> None:
        """Email logic — reason 2"""
        smtp.send(self.email, message)

    def generate_report(self) -> str:
        """Report generation — reason 3"""
        return f"Report for {self.name}..."


# Good — one responsibility per class
class User:
    """Only user data."""
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class UserRepository:
    """Only DB work."""
    def save(self, user: User) -> None:
        db.execute("INSERT INTO users ...")


class EmailService:
    """Only sending email."""
    def send(self, to: str, message: str) -> None:
        smtp.send(to, message)


class UserReportGenerator:
    """Only report generation."""
    def generate(self, user: User) -> str:
        return f"Report for {user.name}..."
```

### How to Determine Responsibility

Ask the question: "What does this class do?"

- Bad: "Manages users, sends email, and generates reports"
- Good: "Stores user data"

---

## O — Open/Closed Principle (OCP)

**Open for extension, closed for modification.**

### Signs of Violation

- `if/elif/elif...` chains by object type
- Adding a new type requires changing existing code
- `match/case` by string type

### Examples

```python
# Bad — adding new type requires modification
def calculate_area(shape: dict) -> float:
    if shape["type"] == "circle":
        return 3.14 * shape["radius"] ** 2
    elif shape["type"] == "rectangle":
        return shape["width"] * shape["height"]
    elif shape["type"] == "triangle":  # New type — modified function
        return 0.5 * shape["base"] * shape["height"]
    raise ValueError(f"Unknown shape: {shape['type']}")


# Good — extension through new classes
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14 * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


# New type — new class, existing code doesn't change
class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height


def calculate_total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)
```

### Patterns for OCP

- **Strategy** — algorithm selection at runtime
- **Template Method** — common algorithm with overridable steps
- **Decorator** — adding behavior without modifying class

---

## L — Liskov Substitution Principle (LSP)

**Subclass objects should be replaceable for base class objects without breaking the program.**

### Signs of Violation

- Subclass method throws `NotImplementedError`
- Subclass ignores parent method parameters
- Subclass returns `None` where parent returns a value
- Subclass strengthens preconditions or weakens postconditions

### Examples

```python
# Bad — contract violation
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def area(self) -> float:
        return self._width * self._height


class Square(Rectangle):
    def set_width(self, width: float) -> None:
        self._width = width
        self._height = width  # LSP violation!

    def set_height(self, height: float) -> None:
        self._width = height  # LSP violation!
        self._height = height


def test_rectangle(rect: Rectangle) -> None:
    rect.set_width(5)
    rect.set_height(10)
    assert rect.area() == 50  # Fails for Square!


# Good — correct hierarchy
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2
```

### Rule for LSP

If `S` is a subtype of `T`, then:
- `S` should not strengthen preconditions
- `S` should not weaken postconditions
- `S` should preserve invariants of `T`

---

## I — Interface Segregation Principle (ISP)

**Many specialized interfaces are better than one universal.**

### Signs of Violation

- Class implements interface methods as `pass` or `raise NotImplementedError`
- Clients depend on methods they don't use
- "Fat" interface with 10+ methods

### Examples

```python
# Bad — fat interface
class Document(Protocol):
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def delete(self) -> None: ...
    def print(self) -> None: ...
    def fax(self) -> None: ...
    def scan(self) -> bytes: ...


class SimpleDocument:
    """Simple document doesn't do fax and scan."""
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def delete(self) -> None: ...
    def print(self) -> None: ...
    def fax(self) -> None:
        raise NotImplementedError  # ISP violation
    def scan(self) -> bytes:
        raise NotImplementedError  # ISP violation


# Good — small interfaces
class Readable(Protocol):
    def read(self) -> str: ...


class Writable(Protocol):
    def write(self, content: str) -> None: ...


class Deletable(Protocol):
    def delete(self) -> None: ...


class Printable(Protocol):
    def print(self) -> None: ...


class Faxable(Protocol):
    def fax(self) -> None: ...


class Scannable(Protocol):
    def scan(self) -> bytes: ...


# Classes implement only needed interfaces
class SimpleDocument:
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def delete(self) -> None: ...
    def print(self) -> None: ...


class MultiFunctionDocument:
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def print(self) -> None: ...
    def fax(self) -> None: ...
    def scan(self) -> bytes: ...


# Functions depend only on what they use
def send_via_fax(doc: Faxable) -> None:
    doc.fax()
```

---

## D — Dependency Inversion Principle (DIP)

**High-level modules should not depend on low-level modules. Both should depend on abstractions.**

### Signs of Violation

- Importing concrete implementations in business logic
- `from infrastructure.postgres import PostgresDB`
- Creating dependencies via `new`/constructor inside class
- Hard to test (need mocks of concrete classes)

### Examples

```python
# Bad — dependency on concrete implementations
from infrastructure.postgres import PostgresDatabase
from infrastructure.sendgrid import SendGridEmailClient
from infrastructure.stripe import StripePaymentGateway


class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard coupling
        self.email = SendGridEmailClient()  # Hard coupling
        self.payment = StripePaymentGateway()  # Hard coupling

    def create_order(self, data: dict) -> Order:
        order = Order(**data)
        self.db.save(order)
        self.payment.charge(order.total)
        self.email.send(order.user_email, "Order created")
        return order


# Good — dependency on abstractions
from typing import Protocol


class DatabaseProtocol(Protocol):
    def save(self, entity: Any) -> None: ...
    def get(self, id: int) -> Any: ...


class EmailServiceProtocol(Protocol):
    def send(self, to: str, message: str) -> None: ...


class PaymentGatewayProtocol(Protocol):
    def charge(self, amount: float) -> None: ...


class OrderService:
    def __init__(
        self,
        db: DatabaseProtocol,
        email: EmailServiceProtocol,
        payment: PaymentGatewayProtocol,
    ):
        self.db = db
        self.email = email
        self.payment = payment

    def create_order(self, data: dict) -> Order:
        order = Order(**data)
        self.db.save(order)
        self.payment.charge(order.total)
        self.email.send(order.user_email, "Order created")
        return order


# Concrete implementations
class PostgresDatabase:
    def save(self, entity: Any) -> None: ...
    def get(self, id: int) -> Any: ...


# Dependency injection (at entry point / DI container)
service = OrderService(
    db=PostgresDatabase(),
    email=SendGridEmailClient(),
    payment=StripePaymentGateway(),
)
```

### Advantages of DIP

- **Testability** — easy to substitute mocks
- **Flexibility** — swap implementation without changing business logic
- **Loose coupling** — modules are independent
