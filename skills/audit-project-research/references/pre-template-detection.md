# Phase 2.1: Pre-Template Detection & Remediation

> Detailed check for `/audit-project-research` Phase 2.1.

## Pre-template project detection

If the project has **no `.context/`** AND **no `.claude/`**, flag it as a **pre-template project** and add a consolidated note:

```
Pre-template project detected
===============================
This project predates the current init-project-research template.
To bring it into the framework, consider adding:

  1. mkdir -p .context && touch .context/current-focus.md .context/project-recap.md
  2. mkdir -p .claude && copy settings.local.json from another project
  3. Create a CLAUDE.md (see /init-project-research Phase 4 for template)
  4. mkdir to-sort && touch to-sort/.gitkeep
  5. Run /sync-permissions to set up symlinks

Or run /init-project-research in "retrofit" mode if available.
```

## Remediation suggestions

For each missing common core item, include a one-line remediation suggestion:

| Missing item | Suggestion |
|-------------|------------|
| `.context/` | `mkdir -p .context && touch .context/current-focus.md .context/project-recap.md` |
| `.gitignore` | Copy template from `/init-project-research` Phase 4 |
| `.claude/settings.local.json` | Run `/sync-permissions` to create |
| `to-sort/` | `mkdir to-sort && touch to-sort/.gitkeep` |
| `CLAUDE.md` | See `/init-project-research` Phase 4 for template |
| `README.md` | See `/init-project-research` Phase 4 for template |
| `correspondence/` | `mkdir -p correspondence/referee-reviews && touch correspondence/referee-reviews/.gitkeep` |
| `docs/` | `mkdir -p docs/{literature-review,readings}` |
| `docs/literature-review/` | `mkdir -p docs/literature-review && touch docs/literature-review/.gitkeep` -- `/literature` outputs go here |
| `docs/venues/` | `mkdir -p docs/venues && touch docs/venues/.gitkeep` |
| `log/` | `mkdir log && touch log/.gitkeep` |
| `MEMORY.md` | Seed from `/init-project-research` Phase 4 template (research or teaching variant) |
