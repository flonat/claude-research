---
name: latex-health-check
description: "Compile all LaTeX projects, auto-fix known errors, and check cross-project consistency. Self-healing build agent for the multi-project research ecosystem."
allowed_tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash(latexmk*)
  - Bash(pdflatex*)
  - Bash(biber*)
  - Bash(bibtex*)
  - Bash(ls*)
  - Bash(mkdir*)
  - Bash(cp*)
  - Bash(ln*)
  - Bash(wc*)
  - Bash(readlink*)
argument-hint: "[project-path | 'all' | 'quick']"
---

# LaTeX Health Check: Self-Healing Build Agent

> Compile all LaTeX projects, auto-fix known errors iteratively, and verify cross-project consistency (symlinks, shared bibliographies, Overleaf separation).

## When to Use

- Periodically (weekly) to catch build rot before it becomes debugging sessions
- After major infrastructure changes (template updates, symlink reorganisation)
- Before submission season to verify all papers compile cleanly
- When the user says "check my LaTeX", "build health", "compile everything"

## Modes

| Mode | Trigger | What it does |
|------|---------|-------------|
| **Single project** | Path argument | Compile + fix + verify one project |
| **All projects** | `all` argument | Discover and compile every LaTeX project |
| **Quick** | `quick` argument | Compile only, no fixes, report errors |

## Phase 1: Discover LaTeX Projects

Find all directories containing a `\documentclass` in a .tex file:

Search locations:
- `~/Library/CloudStorage/YOUR-CLOUD/Research Projects/`
- `~/Library/CloudStorage/YOUR-CLOUD/Task Management/docs/`

For each discovered project, record:
- Project name (directory name)
- Main .tex file path
- Whether it has a `.latexmkrc`
- Whether it has an `out/` directory
- Whether it's inside a `paper/` subdirectory (Overleaf-linked)

## Phase 2: Build Loop (per project)

For each project:

### 2a. Pre-flight
- Check for `.latexmkrc` — create if missing (with `$out_dir = 'out'` and PDF copy-back)
- Create `out/` directory if missing

### 2b. Compile
```bash
cd <project-dir> && latexmk -interaction=nonstopmode <main.tex> 2>&1
```

**Engine selection:** Do NOT hardcode `-pdf`. The project's `.latexmkrc` (created in 2a) controls the engine — it auto-detects xelatex via `fontspec`, or defaults to pdflatex. Passing `-pdf` overrides this and breaks xelatex/lualatex projects. Let latexmk read `.latexmkrc`.

### 2c. Parse log
Extract from `out/*.log`:
- Error count (lines starting with `!`)
- Warning count (Overfull/Underfull hbox/vbox)
- Undefined citation count
- Missing package count

### 2d. Auto-fix (up to 3 iterations)

For each error, apply the known fix from the database:

| Error pattern | Fix |
|--------------|-----|
| Missing package `X` | Add `\usepackage{X}` — but NEVER try `xltabular` or `ltablex` (use `longtable` instead) |
| Undefined citation `key` | Check .bib file exists and is referenced; check for typos via edit distance |
| Overfull hbox | Flag location and width — do NOT auto-fix (requires human judgment) |
| tcolorbox `=` or `,` in title | Wrap title in braces: `title={...}` |
| Font encoding warning | Add `\usepackage[T1]{fontenc}` if missing |
| Missing `\begin{document}` | Check for corrupted preamble |
| Broken symlink in `\input{}` or `\includegraphics{}` | Find the target and report |
| Build artifacts in source dir | Flag — offer to move to `out/` |

After each fix, recompile. Max 3 iterations per project.

**Why 3 iterations (not 5)?** `/latex-autofix` runs up to 5 iterations on a single project with deep error analysis. This skill trades depth for breadth — 3 iterations is enough to catch the common fleet-wide issues (missing packages, broken symlinks, stale cache) without spending excessive time on any one project. If a project still has errors after 3 iterations, mark it as ERROR and recommend running `/latex-autofix` on it directly for deeper diagnosis.

### 2e. Record result
```json
{
  "project": "project-name",
  "path": "/full/path",
  "status": "OK | FIXED | ERROR",
  "errors_initial": 3,
  "errors_final": 0,
  "fixes_applied": ["added fontenc", "fixed tcolorbox title"],
  "warnings": 2,
  "undefined_citations": 0
}
```

## Phase 3: Cross-Project Checks

After all projects are compiled:

1. **Symlink integrity** — verify all symlinks in skills/, agents/, rules/, hooks/ resolve
2. **Shared .bib consistency** — if multiple projects reference the same .bib file (e.g., via symlink), verify they're all pointing to the same version
3. **Overleaf separation** — scan every `paper/` directory for forbidden file types (.py, .R, .csv, .ipynb, etc.)
4. **Template consistency** — check if projects using the working paper template have diverged from the current template version

## Phase 4: Report

Generate a summary report:

```
LaTeX Health Check — YYYY-MM-DD

Projects scanned:  N
Compiled OK:       N (list)
Fixed and OK:      N (list + fixes applied)
Still broken:      N (list + remaining errors)
Skipped:           N (list + reason)

Cross-project issues:
  Broken symlinks:        N
  Overleaf violations:    N
  Template drift:         N

Warnings (not auto-fixed):
  Overfull hboxes:        N across M projects
  Underfull hboxes:       N across M projects
```

Print to stdout. If `--save` flag or 10+ projects scanned, also write to `log/latex-health/YYYY-MM-DD.md`.

## What This Skill Does NOT Do

- Does NOT fix overfull/underfull boxes (requires human judgment on rewording)
- Does NOT modify paper content (only build configuration and missing packages)
- Does NOT push to git (compilation fixes should be reviewed first)
- Does NOT touch Overleaf-synced files without permission (per overleaf-separation rule)

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/latex-autofix` | Single-project deep fix (5 iterations). This skill runs a lighter version (3 iterations) at fleet scale. For ERROR projects, recommend running `/latex-autofix` directly. |
| `/latex` | Manual compilation config and `.latexmkrc` reference — health-check creates `.latexmkrc` files using the conventions defined there. |
| `/audit-project-structure` | Checks project structure (directories, files). This skill checks build health. |
| `/validate-bib` | Validates bibliography entries. This skill checks if citations compile. |
| `/audit-template-compliance` | Checks preamble alignment with the working paper template. Complementary: run after health-check to ensure preamble consistency. |
