# Naming

Names should reveal intent. Code is read more often than it is written.

## General Principles

### 1. Name Should Answer Questions

- **Why does it exist?**
- **What does it do?**
- **How is it used?**

```python
# Bad — needs a comment
d = 86400  # seconds in a day

# Good — name explains everything
SECONDS_IN_DAY = 86400
```

### 2. Avoid Disinformation

```python
# Bad — it's not a list
accounts_list = {}  # This is a dict!

# Bad — too similar names
XYZControllerForEfficientHandlingOfStrings
XYZControllerForEfficientStorageOfStrings

# Good
accounts: dict[int, Account] = {}
```

### 3. Use Pronounceable Names

```python
# Bad
genymdhms  # generation year month day hour minute second
modymdhms

# Good
generation_timestamp
modification_timestamp
```

### 4. Use Searchable Names

```python
# Bad — try to find 7 in the code
if status == 7:
    ...

# Good
STATUS_APPROVED = 7
if status == STATUS_APPROVED:
    ...
```

---

## Variables

### Nouns for Data

```python
# Good
user = get_current_user()
total_price = calculate_total(items)
active_orders = filter_active(orders)
```

### Boolean Variables — is/has/can/should

```python
# Bad
active = True
permission = user.can_edit
logged = False

# Good
is_active = True
has_edit_permission = user.can_edit
is_logged_in = False
can_delete = user.is_admin
should_notify = preferences.notifications_enabled
```

### Collections — Plural

```python
# Bad
user = [user1, user2]  # This is a list!
item_list = []         # Redundant

# Good
users = [user1, user2]
items = []
active_users = filter_active(users)
```

### Dictionaries — by/to

```python
# Good
users_by_id: dict[int, User] = {}
status_to_label: dict[Status, str] = {}
email_to_user: dict[str, User] = {}
```

### Avoid Single-Letter Names

```python
# Bad
for i in items:
    for j in i.subitems:
        process(j)

# Good
for item in items:
    for subitem in item.subitems:
        process(subitem)

# Exceptions: mathematical formulas, coordinates
x, y, z = get_coordinates()
for i in range(n):  # Index is acceptable
```

---

## Functions

### Verb + Noun

```python
# Bad
def user_data(): ...
def process(): ...
def handle(): ...
def do_stuff(): ...

# Good
def get_user_data(): ...
def calculate_total_price(): ...
def send_welcome_email(): ...
def validate_order_items(): ...
```

### Verbs by Purpose

| Action | Verb |
|--------|------|
| Getting | `get_`, `fetch_`, `find_`, `load_` |
| Creating | `create_`, `build_`, `make_`, `generate_` |
| Checking | `is_`, `has_`, `can_`, `should_`, `validate_` |
| Changing | `set_`, `update_`, `change_`, `modify_` |
| Deleting | `delete_`, `remove_`, `clear_` |
| Transforming | `to_`, `convert_`, `parse_`, `format_` |
| Calculating | `calculate_`, `compute_`, `count_` |

### Verb Consistency

```python
# Bad — different verbs for the same action
def get_user(): ...
def fetch_order(): ...
def retrieve_product(): ...
def obtain_category(): ...

# Good — one verb
def get_user(): ...
def get_order(): ...
def get_product(): ...
def get_category(): ...
```

### Boolean Functions

```python
# Bad
def check_admin(user): ...
def user_active(user): ...

# Good
def is_admin(user: User) -> bool: ...
def is_active(user: User) -> bool: ...
def has_permission(user: User, permission: str) -> bool: ...
def can_edit(user: User, resource: Resource) -> bool: ...
```

---

## Classes

### Nouns, Not Verbs

```python
# Bad — verbs
class ProcessOrder: ...
class ManageUsers: ...
class HandlePayment: ...

# Good — nouns
class Order: ...
class OrderProcessor: ...
class UserManager: ...
class PaymentHandler: ...
```

### Avoid Generic Names

```python
# Bad — too generic
class Manager: ...
class Processor: ...
class Data: ...
class Info: ...
class Helper: ...
class Util: ...

# Good — specific
class UserRepository: ...
class OrderValidator: ...
class PriceCalculator: ...
class EmailSender: ...
```

### Suffixes by Purpose

| Purpose | Suffix | Example |
|---------|--------|---------|
| DB work | `Repository` | `UserRepository` |
| Business logic | `Service` | `OrderService` |
| Validation | `Validator` | `EmailValidator` |
| Transformation | `Converter`, `Mapper` | `UserDTOMapper` |
| Object creation | `Factory`, `Builder` | `OrderFactory` |
| Strategy | `Strategy` | `DiscountStrategy` |
| Handler | `Handler` | `PaymentHandler` |

---

## Constants

### SCREAMING_SNAKE_CASE

```python
# Good
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"

# Grouping through class
class HTTPStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404


class UserRole:
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
```

---

## Modules and Packages

### snake_case, Short, Descriptive

```python
# Bad
myModule.py
MyUtilities.py
helperfunctions.py

# Good
user_repository.py
order_service.py
email_validator.py
```

### Package Structure

```
src/
├── modules/
│   ├── users/
│   │   ├── models.py
│   │   ├── repositories.py
│   │   ├── services.py
│   │   ├── dto.py
│   │   └── routers.py
│   └── orders/
│       ├── models.py
│       └── ...
├── core/
│   ├── database.py
│   ├── security.py
│   └── config.py
└── infrastructure/
    ├── email/
    └── storage/
```

---

## Anti-patterns

### Hungarian Notation

```python
# Bad — type in name
str_name = "John"
int_age = 25
lst_users = []

# Good — type in annotation
name: str = "John"
age: int = 25
users: list[User] = []
```

### Redundant Context

```python
# Bad — in User class no need for user_ prefix
class User:
    user_name: str
    user_email: str
    user_age: int

# Good
class User:
    name: str
    email: str
    age: int
```

### Abbreviations

```python
# Bad
def calc_ttl_prc(itms): ...
usr_repo = UserRepo()

# Good
def calculate_total_price(items): ...
user_repository = UserRepository()

# Exceptions: commonly accepted (URL, HTTP, API, ID, DTO)
api_url: str
user_id: int
```
