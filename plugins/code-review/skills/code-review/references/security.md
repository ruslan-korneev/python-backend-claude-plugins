# Security Checklist

Security issues are high-priority findings that should block merges.

## OWASP Top 10 Quick Reference

### 1. Injection

#### SQL Injection
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ Parameterized
stmt = select(User).where(User.name == user_input)
```

#### Command Injection
```python
# ❌ Vulnerable
os.system(f"convert {user_filename} output.png")

# ✅ Safe
subprocess.run(["convert", user_filename, "output.png"], check=True)
```

#### Template Injection
```python
# ❌ Vulnerable (Jinja2)
template = Template(user_input)

# ✅ Safe
template = env.get_template("safe_template.html")
template.render(user_data=user_input)
```

### 2. Broken Authentication

#### Weak Password Handling
```python
# ❌ Storing plaintext
user.password = password

# ✅ Proper hashing
user.password_hash = pwd_context.hash(password)
```

#### Session Issues
```python
# ❌ Predictable session ID
session_id = str(user.id)

# ✅ Secure random
session_id = secrets.token_urlsafe(32)
```

#### JWT Issues
```python
# ❌ Weak secret
SECRET = "secret123"

# ❌ No expiration
token = jwt.encode({"user_id": 1}, SECRET)

# ✅ Strong secret + expiration
token = jwt.encode({
    "user_id": 1,
    "exp": datetime.utcnow() + timedelta(hours=1)
}, settings.JWT_SECRET, algorithm="HS256")
```

### 3. Sensitive Data Exposure

#### Logging Sensitive Data
```python
# ❌ Logging passwords
logger.info(f"Login attempt: {username}, {password}")

# ✅ Redacted
logger.info(f"Login attempt: {username}")
```

#### Error Messages
```python
# ❌ Stack trace in response
except Exception as e:
    return {"error": str(e), "trace": traceback.format_exc()}

# ✅ Generic error
except Exception as e:
    logger.exception("Internal error")
    return {"error": "Internal server error"}
```

#### Hardcoded Secrets
```python
# ❌ Hardcoded
API_KEY = "sk-1234567890abcdef"

# ✅ Environment
API_KEY = os.environ["API_KEY"]
```

### 4. Broken Access Control

#### Missing Authorization
```python
# ❌ No auth check
@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    await repo.delete(user_id)

# ✅ With authorization
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(403, "Admin required")
    await repo.delete(user_id)
```

#### IDOR (Insecure Direct Object Reference)
```python
# ❌ No ownership check
@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    return await repo.get(order_id)  # Any user can access any order!

# ✅ Ownership verified
@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
):
    order = await repo.get(order_id)
    if order.user_id != current_user.id:
        raise HTTPException(403, "Not your order")
    return order
```

### 5. Security Misconfiguration

#### CORS
```python
# ❌ Too permissive
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Dangerous with *
)

# ✅ Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
)
```

#### Debug Mode in Production
```python
# ❌ Debug in prod
app = FastAPI(debug=True)

# ✅ Environment-based
app = FastAPI(debug=settings.DEBUG)
```

### 6. Cryptographic Failures

#### Weak Algorithms
```python
# ❌ MD5/SHA1 for passwords
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()

# ✅ Proper password hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hash = pwd_context.hash(password)
```

#### Insecure Random
```python
# ❌ Predictable
import random
token = ''.join(random.choices(string.ascii_letters, k=32))

# ✅ Cryptographically secure
import secrets
token = secrets.token_urlsafe(32)
```

## Input Validation

### Path Traversal
```python
# ❌ Vulnerable
def get_file(filename):
    return open(f"/uploads/{filename}").read()
    # filename = "../etc/passwd" works!

# ✅ Safe
def get_file(filename):
    path = Path("/uploads") / filename
    if not path.resolve().is_relative_to(Path("/uploads").resolve()):
        raise ValueError("Invalid path")
    return path.read_text()
```

### Type Coercion
```python
# ❌ Relying on string comparison
if user_input == "true":
    do_admin_thing()

# ✅ Strict validation with Pydantic
class Request(BaseModel):
    is_admin: bool  # Type enforced
```

### Size Limits
```python
# ❌ Unlimited upload
@router.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()  # Could be 10GB!

# ✅ Size limited
@router.post("/upload")
async def upload(file: UploadFile):
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(413, "File too large")
```

## Review Checklist

### Authentication
- [ ] Passwords properly hashed (bcrypt/argon2)?
- [ ] Sessions use secure random tokens?
- [ ] JWT has expiration and strong secret?
- [ ] No credentials in logs?

### Authorization
- [ ] All endpoints have auth checks?
- [ ] Resource ownership verified?
- [ ] Role checks present where needed?
- [ ] Admin operations protected?

### Input Validation
- [ ] All user input validated?
- [ ] SQL queries parameterized?
- [ ] No command injection possible?
- [ ] File paths sanitized?

### Data Protection
- [ ] No hardcoded secrets?
- [ ] Sensitive data not logged?
- [ ] HTTPS enforced?
- [ ] Proper error messages (no stack traces)?

### Configuration
- [ ] Debug mode off in prod?
- [ ] CORS properly configured?
- [ ] Security headers present?

## Severity Levels

| Issue | Severity | Block PR? |
|-------|----------|-----------|
| SQL/Command Injection | Critical | Yes |
| Authentication Bypass | Critical | Yes |
| IDOR | High | Yes |
| Hardcoded Secrets | High | Yes |
| Missing Auth Check | High | Yes |
| Weak Crypto | Medium | Maybe |
| Missing Rate Limiting | Medium | No |
| Verbose Errors | Low | No |
