---
paths:
  - "**/*.tex"
  - "**/*.bib"
---

# Rule: Overleaf Separation — No Code or Data in Paper Directories

## Principle

**The `paper/` directory (Overleaf symlink inside `paper-{venue}/paper/`) is for LaTeX source files ONLY.** All code, data, and computational artifacts belong in the project directory itself — never inside `paper/`.

## What Belongs in `paper/`

- LaTeX source files: `.tex`, `.sty`, `.cls`, `.bst`, `.bbl`
- Bibliography files: `.bib`
- Figures for the paper: `.pdf`, `.png`, `.eps`, `.jpg`, `.svg`, `.tikz`
- LaTeX config: `.latexmkrc`, `latexmkrc`
- Build output directory: `out/`

## What NEVER Belongs in `paper/`

- **Code files:** `.py`, `.R`, `.jl`, `.m`, `.sh`, `.ipynb`, `.do`
- **Data files:** `.csv`, `.xlsx`, `.json`, `.dta`, `.parquet`, `.rds`, `.pkl`, `.feather`, `.h5`
- **Computational output:** raw results, logs, intermediate artifacts
- **Scripts that generate figures** — the script goes in `code/` or `src/`, only the exported figure goes in `paper/`
- **Notebooks** — analysis notebooks belong in `code/` or `experiments/`, never in `paper/`
- **Virtual environments, package files:** `.venv/`, `requirements.txt`, `pyproject.toml`, `renv/`

## Where Code and Data Go Instead

| Content | Location |
|---------|----------|
| Python/R scripts | `code/python/`, `code/R/`, or `src/` |
| Data (raw) | `data/raw/` |
| Data (processed) | `data/processed/` |
| Generated figures | Export to `paper/figures/` or `paper/` directly (the *image file* only) |
| Generated tables | Export `.tex` table files to `paper/` (the *table file* only) |
| Experiment configs | `experiments/configs/` |
| Results | `results/` or `output/` |

## When This Applies

- **Always.** Every research project, every session, no exceptions.
- When creating new files — never place code/data inside `paper/`
- When reorganising projects — move any code/data out of `paper/`
- When writing scripts that generate outputs — script in project, output exported to `paper/`
- When running `/init-project-research` — the scaffold already enforces this separation

## What To Do If You Find Violations

1. **Flag immediately:** "I found code/data files inside `paper/` — this violates the Overleaf separation rule."
2. **Propose moves:** Show where each file should go in the project directory.
3. **Wait for approval** before moving anything.
4. **Never silently leave** code or data in `paper/`.

## Overleaf Folder Lifecycle

Creating a folder in the Overleaf root automatically creates an Overleaf project. This has implications for what Claude can and cannot do:

| Action | Claude allowed? | Notes |
|--------|:-:|-------|
| **Create** | Yes | `mkdir` in the Overleaf root creates a project. Use during `/init-project-research` scaffolding. |
| **Rename** | No — ask user | Renaming loses Overleaf project history. The user must rename via the Overleaf UI to preserve history. Flag as a manual TODO. |
| **Delete** | Break the glass | Deleting a folder destroys the Overleaf project and all its history. Requires explicit confirmation per the `break-the-glass` rule. |

**When scaffolding:** Ask if the Overleaf project already exists. If yes, get the folder name and symlink to it. If no, create the folder via `mkdir` and then symlink.

**When renaming:** Never rename an Overleaf folder. Update the symlink to point to the new name only after the user confirms they've renamed it in the Overleaf UI.

## Why This Matters

`paper/` syncs to Overleaf. Code and data in Overleaf causes sync bloat, version confusion, and breaks the clean separation between the paper (collaborative, LaTeX-only) and the research project (local, computational). Overleaf is not a code repository.
