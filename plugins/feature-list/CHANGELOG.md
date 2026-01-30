# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc.1] - 2026-01-28

### Added

- Initial release candidate
- `/feature-list:init` command to initialize feature directory
- `/feature-list:analyze` command to extract features from codebase
- `/feature-list:design` command for interactive feature design
- `/feature-list:add` command to add new features
- `/feature-list:graph` command to regenerate dependency graphs
- `/feature-list:status` command to show implementation status
- Codebase analyzer agent (sonnet model)
- Feature designer agent (opus model)
- Feature specification skill with comprehensive references
- Support for 6 phases: core, workflow, lifecycle, analytics, integration, ui
- BR/US/AC identifier conventions
- Mermaid dependency graph generation
- Manual section preservation during regeneration
