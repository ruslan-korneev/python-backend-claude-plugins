---
name: review
description: Analyze code for code smells and principle violations
allowed_tools:
  - Read
  - Glob
  - Grep
arguments:
  - name: path
    description: Path to file or directory
    required: true
---

# Command /clean:review

Analyze code for code smells and clean code principle violations.

## Instructions

### Step 1: Read the code

Read the specified file or files in the directory.

### Step 2: Check for code smells

Look for the following problems:

#### Bloaters
- [ ] **Long Method** — functions > 20-30 lines
- [ ] **Long Parameter List** — > 3-4 parameters
- [ ] **Large Class** — classes > 200 lines with unrelated methods
- [ ] **Primitive Obsession** — primitives instead of Value Objects

#### Object-Orientation Abusers
- [ ] **Switch Statements** — long if/elif by type
- [ ] **Refused Bequest** — subclass doesn't use parent's methods

#### Change Preventers
- [ ] **Divergent Change** — class changes for different reasons
- [ ] **Shotgun Surgery** — one change affects many classes

#### Dispensables
- [ ] **Dead Code** — unused code
- [ ] **Speculative Generality** — code "for the future"
- [ ] **Comments** — comments instead of clear code

#### Couplers
- [ ] **Feature Envy** — method envies another class's data
- [ ] **Inappropriate Intimacy** — classes are too coupled
- [ ] **Message Chains** — long call chains

### Step 3: Check principles

#### SOLID
- [ ] **SRP** — class has one reason to change?
- [ ] **OCP** — extension without modification?
- [ ] **LSP** — subclasses replace parents?
- [ ] **ISP** — interfaces not "fat"?
- [ ] **DIP** — dependency on abstractions?

#### Other
- [ ] **DRY** — no knowledge duplication?
- [ ] **KISS** — no unnecessary complexity?
- [ ] **YAGNI** — no code "for the future"?

### Step 4: Check naming

- [ ] Variables — nouns, reveal meaning
- [ ] Booleans — is_/has_/can_/should_
- [ ] Functions — verb + noun
- [ ] Classes — nouns, specific names
- [ ] Constants — SCREAMING_SNAKE_CASE

## Response Format

```markdown
## Code Review: {{ path }}

### Summary
- **Overall assessment**: Good / Needs attention / Critical
- **Issues found**: X

### Code Smells

#### Critical
- **Long Method** (lines X-Y): `function_name` — 80 lines
  - Recommendation: Extract Method

#### Warning
- **Primitive Obsession** (line X): `email: str` instead of `Email` Value Object

### Principle Violations

#### SRP
- `UserService` — 3 reasons to change: DB work, validation, notifications

### Naming Issues

- Line X: `d = 86400` → `SECONDS_IN_DAY = 86400`
- Line Y: `def process()` → `def calculate_order_total()`

### Recommendations

1. **Priority 1**: Split `process_order()` into separate functions
2. **Priority 2**: Extract `EmailService` from `UserService`
3. **Priority 3**: Create Value Object for Email
```
