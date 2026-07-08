# Check Project Structure — Report Format

> Phase 9 report template for `/audit-project-research`. Adapt to actual audit findings.

## Severity Levels

| Level | Meaning |
|-------|---------|
| **Missing** | Expected by template, not present. Should probably be added. |
| **Degraded** | Present but incomplete, empty, or has issues. |
| **Info** | Deviation from template that may be intentional. No action needed unless it bothers you. |

## Example Report

```
Project Structure Audit
========================
Project:  <name>
Path:     <path>
Type:     <detected type>
Git:      yes/no (branch: <name>)

Common Core:
  CLAUDE.md               ✓ present (5/5 sections)
  README.md               ✓ present
  .gitignore              ⚠ degraded — missing `out/` pattern
  .context/               ✓ present
    current-focus.md      ⚠ degraded — still has initial template text
    project-recap.md      ✓ present
  .claude/                ✓ present
    settings.local.json   ✓ present
  docs/                   ✓ present
    readings/             ✓ present
    venues/               ✓ present
  log/                    ✓ present
  paper/                  ✓ symlink → /path/to/Overleaf/... (resolves)
  to-sort/                ✗ missing

Conditional (experimental):
  code/                   ✓ present
    python/               ✓ present
    R/                    ✗ missing
  data/                   ✓ present
    raw/                  ✓ present
    processed/            ✓ present
  output/                 ✓ present
    figures/              ✓ present
    tables/               ✗ missing

Git:
  Branch:                 main
  Remote:                 none (Dropbox-only)
  Untracked:              2 files (listed below)

Summary:
  ✓ Present:    18
  ⚠ Degraded:    2
  ✗ Missing:     3
  ℹ Info:        1

Post-init growth:
  experiments/            ℹ recognized — experiment configs and results
  legacy/                 ℹ recognized — preserved old code
  scratch/                ℹ unrecognized — review whether this belongs

Missing items:
  1. to-sort/              — inbox for unsorted materials
     Remediation: mkdir to-sort && touch to-sort/.gitkeep
  2. code/R/               — R code directory (may not be needed)
  3. output/tables/        — table output directory

Degraded items:
  1. .gitignore            — missing `out/` pattern for LaTeX build artifacts
     Remediation: copy template from /init-project-research Phase 4
  2. current-focus.md      — still has initial template text after 12 commits

Rules Sync:
  .claude/rules/             ⚠ created directory, copied 12 rules

Info:
  1. code/R/ may be intentionally absent if project is Python-only
```

## Remediation Suggestions

For each missing common core item, include a one-line suggestion:

| Missing item | Suggestion |
|-------------|------------|
| `.context/` | `mkdir -p .context && touch .context/current-focus.md .context/project-recap.md` |
| `.gitignore` | Copy template from `/init-project-research` Phase 4 |
| `.claude/settings.local.json` | Run `/sync-permissions` to create |
| `to-sort/` | `mkdir to-sort && touch to-sort/.gitkeep` |
| `CLAUDE.md` | See `/init-project-research` Phase 4 for template |
| `README.md` | See `/init-project-research` Phase 4 for template |
| `docs/` | `mkdir -p docs/{literature-review,readings}` |
| `docs/literature-review/` | `mkdir -p docs/literature-review && touch docs/literature-review/.gitkeep` — `/literature` outputs go here |
| `docs/venues/` | `mkdir -p docs/venues && touch docs/venues/.gitkeep` |
| `log/` | `mkdir log && touch log/.gitkeep` |
| `requirements.txt` (present) | Migrate to `pyproject.toml` with `uv` — delete `requirements.txt` |
| `.python-version` (missing, computational) | Create with `uv python pin 3.12` or `echo "3.12" > .python-version` |
