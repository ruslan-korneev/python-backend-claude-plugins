# Changelog

All notable changes to the `code-review` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-25

### Added

- **Two-phase review strategy** based on the Code Review Pyramid:
  - `quick-reviewer` agent (sonnet) for automated checks (linting, types, security patterns)
  - `code-reviewer` agent (opus) for deep analysis (API semantics, implementation, tests)

- **Command `/review:diff`** with flexible targeting:
  - `staged` — review only staged changes
  - `HEAD~N` — review last N commits
  - `branch_name` — review current branch vs target branch
  - `commit..commit` — review commit range

- **Task context support** (`--task` parameter):
  - Enables business requirements compliance check
  - Verifies all use cases from task are covered
  - Detects over-engineering or missing functionality

- **Review modes**:
  - `quick` — fast automated checks only
  - `deep` — thorough analysis only
  - `full` — quick first, then deep if passed

- **Comprehensive reference documentation**:
  - `pyramid.md` — Review Pyramid methodology
  - `api-semantics.md` — API contract review checklist
  - `implementation.md` — Logic and correctness checklist
  - `security.md` — OWASP Top 10 for Python/FastAPI
  - `testing.md` — Test quality and coverage checklist

- **Python/FastAPI specialization**:
  - SQLAlchemy 2.0 patterns
  - Pydantic validation
  - Async code review
  - FastAPI DI patterns

### Notes

- First stable release
- Designed for Python backend projects with FastAPI + SQLAlchemy 2.0
