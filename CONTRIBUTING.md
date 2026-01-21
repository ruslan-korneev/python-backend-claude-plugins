# Contributing to Python Backend Plugins

Thank you for your interest in contributing to this plugin collection!

## How to Contribute

### Adding a New Plugin

1. Create a new directory in `plugins/` with your plugin name
2. Follow the standard plugin structure:

```
plugins/your-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── your-command.md
├── skills/
│   └── your-skill/
│       ├── SKILL.md
│       └── references/
│           └── detailed-docs.md
├── agents/          # optional
├── hooks/           # optional
└── README.md
```

3. Create the `plugin.json` manifest:

```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "description": "Brief description of what your plugin does",
  "author": "Your Name",
  "commands_path": "../commands",
  "skills_path": "../skills",
  "repository": "https://github.com/ruslan-korneev/python-backend-claude-plugins",
  "keywords": ["python", "your-topic"]
}
```

4. Write clear documentation in README.md
5. Submit a Pull Request

### Improving Existing Plugins

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/improve-plugin-name`
3. Make your changes
4. Test your changes locally
5. Submit a Pull Request

### Quality Standards

- **Documentation**: All commands and skills must have clear documentation
- **Examples**: Include practical code examples
- **Consistency**: Follow the existing naming conventions
- **Language**: All content must be in English

### Plugin Guidelines

1. **Single Responsibility**: Each plugin should focus on one domain
2. **No Overlapping**: Avoid duplicating functionality from other plugins
3. **Best Practices**: Plugins should enforce Python best practices
4. **Testable**: Command outputs should be verifiable

### Reporting Issues

When reporting issues, please include:

1. Plugin name and version
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Claude Code version

### Pull Request Process

1. Update documentation if needed
2. Ensure your code follows existing patterns
3. Add yourself to contributors if not already listed
4. Request review from maintainers

## Local Development

```bash
# Clone the repository
git clone https://github.com/ruslan-korneev/python-backend-claude-plugins.git
cd python-backend-claude-plugins
```

Then inside Claude Code, run these slash commands:

```
# Add local marketplace for testing
/plugin marketplace add ./

# Install your plugin
/plugin install your-plugin@python-backend-plugins

# Test your changes
/your-command:test
```

## Git Workflow

We use a modified Gitflow for monorepo with independent plugin versioning.

### Branches

| Branch | Purpose |
|--------|---------|
| `master` | Stable releases, protected |
| `develop` | Integration branch for next release |
| `feature/<plugin>/<description>` | New features |
| `fix/<plugin>/<issue>` | Bug fixes |
| `release/<plugin>-v<version>` | Release preparation |

### Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) with plugin scope:

```bash
# Format
<type>(<plugin>): <description>

# Examples
feat(ruff-lint): add support for RUF100 rule
fix(pytest-assistant): correct fixture scope handling
docs(fastapi-scaffold): update repository pattern examples
chore(alembic-migrations): update dependencies
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

### Feature Development

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/ruff-lint/add-preview-rules

# 2. Make changes and commit
git add .
git commit -m "feat(ruff-lint): add preview rules support"

# 3. Push and create PR
git push origin feature/ruff-lint/add-preview-rules
# Create PR to develop branch
```

> **Important:** Contributors should NOT change version numbers.
> Versions are updated by maintainers during the release process.
> This prevents merge conflicts when multiple PRs are in progress.

### Bug Fixes

```bash
# For bugs in develop
git checkout -b fix/pytest-assistant/fixture-scope
git commit -m "fix(pytest-assistant): correct session fixture scope"

# For critical bugs in master (hotfix)
git checkout master
git checkout -b fix/ruff-lint/critical-123
git commit -m "fix(ruff-lint): resolve config parsing error"
# Create PR to master AND develop
```

## Versioning

Each plugin is versioned independently using [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes in commands or behavior
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, documentation updates

### Version Locations

Update version in these files when releasing:

1. `plugins/<plugin>/.claude-plugin/plugin.json` → `version` field
2. `.claude-plugin/marketplace.json` → plugin's `version` field
3. `CHANGELOG.md` → add release notes

### Git Tags

Tags follow the pattern: `<plugin>-v<version>`

```bash
# Examples
ruff-lint-v1.0.0
ruff-lint-v1.0.1
pytest-assistant-v1.1.0
alembic-migrations-v2.0.0
```

## Release Process

### 1. Prepare Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/ruff-lint-v1.1.0
```

### 2. Update Version

```bash
# Update plugin.json
# Update marketplace.json
# Update CHANGELOG.md
```

### 3. Create PR and Merge

```bash
git commit -m "chore(ruff-lint): bump version to 1.1.0"
git push origin release/ruff-lint-v1.1.0
# Create PR to master
# After approval, merge
```

### 4. Tag Release

```bash
git checkout master
git pull origin master
git tag ruff-lint-v1.1.0
git push origin ruff-lint-v1.1.0
```

### 5. Create GitHub Release

- Go to Releases → New Release
- Select tag: `ruff-lint-v1.1.0`
- Title: `ruff-lint v1.1.0`
- Copy changelog section to description
- Publish

### 6. Merge Back to Develop

```bash
git checkout develop
git merge master
git push origin develop
```

## Questions?

Open an issue with the `question` label.
