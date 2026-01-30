---
name: feature-list:init
description: Initialize feature directory structure with templates
allowed_tools:
  - Read
  - Write
  - Glob
  - Bash
arguments:
  - name: path
    description: "Base path for features directory (default: docs/technical-requirements/features)"
    required: false
---

# Command /feature-list:init

Initialize the feature documentation directory structure.

## Instructions

### Step 1: Determine Target Path

Use the provided `path` argument or default to `docs/technical-requirements/features`.

### Step 2: Check for Existing Directory

Use `Glob` to check if the directory already exists:

```
{path}/*.md
```

If files exist, inform the user:
```markdown
⚠️ Feature directory already exists at `{path}`.

Found {count} feature files:
- {file1}
- {file2}
...

Use `/feature-list:analyze` to update from codebase or `/feature-list:add` to add new features.
```

### Step 3: Create Directory Structure

If the directory doesn't exist, create it:

```bash
mkdir -p {path}
```

### Step 4: Copy Templates

Read templates from the plugin and write them to the target directory:

1. Read `${CLAUDE_PLUGIN_ROOT}/templates/00-template.md`
2. Write to `{path}/00-template.md`

3. Read `${CLAUDE_PLUGIN_ROOT}/templates/readme-template.md`
4. Write to `{path}/README.md`

### Step 5: Confirm Completion

```markdown
✅ Feature directory initialized at `{path}`

Created files:
- `{path}/README.md` — Feature index with dependency graph
- `{path}/00-template.md` — Template for new features

## Next Steps

1. **Analyze existing codebase**: `/feature-list:analyze`
2. **Design new features**: `/feature-list:design`
3. **Add a feature manually**: `/feature-list:add core user-management`
```

## Response Format

```markdown
## Feature Directory Initialized

📁 Created `{path}/`

### Files Created

| File | Purpose |
|------|---------|
| `README.md` | Feature index with dependency graph |
| `00-template.md` | Template for new features |

### Next Steps

- Run `/feature-list:analyze` to extract features from existing code
- Run `/feature-list:design` for interactive feature design
- Run `/feature-list:add <phase> <name>` to add a single feature
```

## Edge Cases

### Directory Exists but Empty

If the directory exists but has no `.md` files, proceed with initialization.

### Partial Initialization

If only some files exist:
- Skip existing files
- Create missing files
- Report what was created vs skipped
