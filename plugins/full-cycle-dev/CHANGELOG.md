# Changelog

All notable changes to the full-cycle-dev plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc.1] - 2025-01-24

### Added

- **Commands**
  - `/dev:cycle` — Full TDD development cycle (explore → plan → execute)
  - `/dev:plan` — Create development plan without execution
  - `/dev:execute` — Execute existing plan with resume support

- **Agents**
  - `codebase-explorer` — Fast codebase analysis (sonnet model)
  - `planning-agent` — Deep analysis and interactive planning (opus model)
  - `execution-agent` — TDD implementation with plugin integration (opus model)

- **Skills**
  - `tdd-workflow` — Documentation for TDD orchestration methodology

- **References**
  - `plan-format.md` — Development plan structure specification
  - `context-handoff.md` — How context flows between agents
  - `plugin-integration.md` — Integration with other plugins

### Features

- Three-phase orchestration (explore, plan, execute)
- Memory Anchors for context persistence across sessions
- Resume capability for interrupted work
- Integration with ecosystem plugins:
  - `pytest-assistant` for TDD test creation
  - `clean-code` for refactoring
  - `ruff-lint` for auto-formatting
  - `python-typing` for type checking
- Automatic plan file generation at `.claude/plans/`
- Quality gates with ZERO noqa/type:ignore policy
