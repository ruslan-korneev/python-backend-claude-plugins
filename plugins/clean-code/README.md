# clean-code

Plugin for clean code principles: SOLID, code smells, refactoring patterns.

## Philosophy

Code is read more often than it is written. Clean code:
- Easy to read and understand
- Easy to modify and extend
- Easy to test
- Minimum surprises

## Installation

Inside Claude Code, run these slash commands:

```
# Add marketplace
/plugin marketplace add ruslan-korneev/python-backend-claude-plugins

# Install plugin
/plugin install clean-code@python-backend-plugins
```

## Commands

### `/clean:review <path>`

Analyze code for code smells and principle violations.

```
/clean:review src/services/user_service.py
/clean:review src/modules/orders/
```

### `/clean:refactor <smell> <path>`

Suggest a specific refactoring.

```
/clean:refactor long-method src/services/order_service.py
/clean:refactor god-class src/managers/user_manager.py
/clean:refactor primitive src/models/user.py
```

Smell types:
- `long-method` — Extract Method
- `long-params` — Introduce Parameter Object
- `god-class` — Extract Class
- `primitive` — Replace Primitive with Object
- `switch` — Replace Conditional with Polymorphism
- `duplicate` — Extract Method
- `deep-nesting` — Guard Clauses

## Skill

Triggers for automatic activation:
- Code is hard to read
- Questions about SOLID, DRY, KISS, YAGNI
- Refactoring needed
- Code review

## Contents

### SOLID

| Principle | Description |
|-----------|-------------|
| **S** — Single Responsibility | Class = one reason to change |
| **O** — Open/Closed | Open for extension, closed for modification |
| **L** — Liskov Substitution | Subclasses replace parents |
| **I** — Interface Segregation | Many small interfaces better than one large |
| **D** — Dependency Inversion | Depend on abstractions, not implementations |

### Other Principles

- **DRY** — Don't Repeat Yourself
- **KISS** — Keep It Simple
- **YAGNI** — You Aren't Gonna Need It
- **Composition over Inheritance**
- **Fail Fast**
- **Law of Demeter**

### Code Smells

#### Bloaters
- Long Method
- Long Parameter List
- Large Class / God Class
- Primitive Obsession

#### Object-Orientation Abusers
- Switch Statements
- Refused Bequest

#### Change Preventers
- Divergent Change
- Shotgun Surgery

#### Dispensables
- Dead Code
- Speculative Generality
- Comments (as a smell)

#### Couplers
- Feature Envy
- Inappropriate Intimacy
- Message Chains

### Naming

- Variables: nouns, reveal meaning
- Booleans: `is_`, `has_`, `can_`, `should_`
- Functions: verb + noun
- Classes: nouns, specific
- Constants: `SCREAMING_SNAKE_CASE`

## Structure

```
clean-code/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── review.md
│   └── refactor.md
├── skills/
│   └── clean-code-patterns/
│       ├── SKILL.md
│       └── references/
│           ├── solid.md
│           ├── principles.md
│           ├── code-smells.md
│           └── naming.md
└── README.md
```

## References

- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Refactoring by Martin Fowler](https://refactoring.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
