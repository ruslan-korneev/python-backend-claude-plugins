# Full-Cycle Development Plugin

🔄 **Full TDD development cycle orchestrator** — from prompt to documented feature.

This plugin orchestrates the complete development workflow by integrating multiple specialized plugins into a cohesive TDD process.

## Features

- **Three-Phase Orchestration**: Explore → Plan → Execute
- **TDD Methodology**: Strict Red-Green-Refactor cycle
- **Plugin Integration**: Leverages pytest-assistant, clean-code, ruff-lint, python-typing
- **Memory Anchors**: Context persistence across sessions
- **Resume Capability**: Continue interrupted work automatically

## Installation

```bash
/plugin install full-cycle-dev@python-backend-plugins
```

### Recommended Plugins

For full functionality, also install:

```bash
/plugin install pytest-assistant@python-backend-plugins
/plugin install clean-code@python-backend-plugins
/plugin install ruff-lint@python-backend-plugins
/plugin install python-typing@python-backend-plugins
```

## Commands

### `/dev:cycle` — Full Development Cycle

Complete workflow from prompt to implemented feature:

```bash
/dev:cycle "Add user avatar upload with S3 storage"
```

With module hint:

```bash
/dev:cycle "Add password reset" --module=auth
```

### `/dev:plan` — Plan Only

Create a development plan without executing:

```bash
/dev:plan "Implement order checkout"
```

Plans are saved to `.claude/plans/dev-{slug}.md`

### `/dev:execute` — Execute Plan

Execute an existing plan (supports resume):

```bash
/dev:execute .claude/plans/dev-add-user-avatar-upload.md
```

## Workflow

```
User Prompt
    │
    ▼
┌─────────────────┐
│ Codebase        │  Fast module discovery
│ Explorer        │  (sonnet model)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Planning        │  Deep analysis + questions
│ Agent           │  (opus model)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Approval   │  Review plan in plan mode
│ (EnterPlanMode) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execution       │  TDD: Red → Green → Refactor
│ Agent           │  (opus model)
└────────┬────────┘
         │
         ▼
    ✅ Feature Complete
```

## TDD Cycle

For each test case:

1. **RED**: Create failing test (`pytest-assistant:first`)
2. **GREEN**: Write minimal implementation
3. **REFACTOR**: Improve code quality (`clean-code:review`)
4. **QUALITY**: Verify lint & types (auto via hooks)

## Plan Structure

Plans include:

```yaml
---
id: dev-{uuid}
feature: {name}
status: draft | approved | in_progress | completed
---
```

- Summary and key decisions
- Affected files table
- Ordered test cases
- Implementation steps
- Memory anchors

## Memory Anchors

Persist context across sessions:

```markdown
> TASK: Add user avatar upload with S3 storage
> APPROACH: Direct upload to S3 with presigned URLs
> CONSTRAINTS: Max 5MB, JPEG/PNG only
> DEPENDENCIES: boto3, existing User model
```

## Quality Principles

- **ZERO noqa** — Fix lint issues, don't suppress
- **ZERO type:ignore** — Fix type issues properly
- **Test first** — Never implement before test
- **Branch coverage** — More important than line coverage

## Example Session

```bash
# Start full cycle
> /dev:cycle "Add user avatar upload"

# Explorer finds relevant modules...
# Planning agent asks clarifying questions...
# Plan created at .claude/plans/dev-add-user-avatar-upload.md

# Review plan and approve...

# Execution begins:
# ✅ test_upload_avatar_success (RED → GREEN → REFACTOR)
# ✅ test_upload_invalid_format (RED → GREEN → REFACTOR)
# ✅ test_upload_too_large (RED → GREEN → REFACTOR)

# Final verification passes
# Feature complete!
```

## Troubleshooting

### Interrupted Session

Simply run the execute command again:

```bash
/dev:execute .claude/plans/dev-{slug}.md
```

The agent will resume from the last incomplete test case.

### Missing Plugins

The plugin works without dependencies but with reduced automation:

```
⚠️ Plugin pytest-assistant not found.
Falling back to manual test creation.
```

Install recommended plugins for full functionality.

## Contributing

See the main repository's [CLAUDE.md](../../CLAUDE.md) for development guidelines.

## License

MIT
