---
name: init-project-research
description: "Bootstrap a research project: interview for details, scaffold directory, create Overleaf symlink, init git, and sync with context library and Notion."
allowed-tools: Bash(mkdir*), Bash(ln*), Bash(ls*), Bash(git*), Bash(touch*), Bash(jq*), Read, Write, Edit, Glob, Grep, Task, AskUserQuestion, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-update-page
argument-hint: "[project-name or no arguments for guided setup]"
---

# Init Project Research

> Interview-driven skill that scaffolds a research project directory and integrates it with the user's Task Management system (context library + Notion).

## When to Use

- Starting a new research paper or project from scratch
- When the user says "new project", "set up a project", "init project", "bootstrap project"
- After deciding to pursue a new research idea that needs its own folder

## Overview

Seven phases, executed in order:

1. **Interview** — gather project details via structured questions
2. **Scaffold** — create directory structure based on project type
3. **Seed files** — populate CLAUDE.md, README.md, .gitignore with interview answers
4. **Overleaf symlink** — link `paper/` to Overleaf directory
5. **Git init** — initialise repo and make first commit
6. **Task Management sync** — update context library and create Notion entry
7. **Confirmation** — report what was created

---

## Phase 1: Interview

Use `AskUserQuestion` for structured input. Three rounds to avoid overwhelming.

### Pre-Interview: Auto-Detection

Before asking questions, scan the project directory (if it already exists) for metadata:
- **LaTeX files** — extract `\title{}`, `\author{}`, `\begin{abstract}`, `\begin{keyword}` from `.tex` files
- **Markdown files** — check for `README.md`, `notes.md` with `# Title` headings
- **BibTeX files** — note `.bib` presence for later phases
- **Overleaf symlink** — if `paper/` is a symlink, follow and scan the target

Present detected values as the first option (marked "Detected from paper") in interview questions. Always allow override. If the directory doesn't exist yet, skip auto-detection.

### Round 1 — Core Identity

1. **Project slug** — kebab-case identifier (e.g., `costly-voice`). Folder name on disk is Title Case with spaces (e.g., `Costly Voice`). Confirm the derived folder name.
2. **Working title** — full paper/project title
3. **Authors / collaborators** — names and affiliations
4. **Research area** — which parent folder under Research Projects/. Scan for existing theme folders and present as options. Also offer "New topic folder" and "Other location".
5. **Target venue** — journal, conference, or preprint:
   - **Journal:** Check CABS AJG ranking via `.context/resources/venue-rankings.md` and the CSV (`.context/resources/venue-rankings/abs_ajg_2024.csv`). For SJR score, query the Elsevier Serial Title API (see venue-rankings.md for snippet; requires `SCOPUS_API_KEY`). Flag journals below CABS 4 with alternatives.
   - **Conference:** Check CORE ranking via `.context/resources/venue-rankings.md` and the CSV (`.context/resources/venue-rankings/core_2026.csv`). Capture page limit, format, review type, anonymisation, deadlines.
   - **Preprint:** Note the server (arXiv, SSRN) — no ranking check needed.
6. **Deadline** — submission deadline if known

### Round 2 — Setup Details

1. **Overleaf project name** — folder under `~/Library/CloudStorage/YOUR-CLOUD/Apps/Overleaf/`. Verify path exists.
2. **LaTeX template** — scan `Task Management/templates/` for options. Default: Working Paper (`templates/latex-wp/`). Also offer "None".
3. **Overleaf external sharing link** — read-only URL for collaborators
4. **Git repository?** — Local git (Recommended) / GitHub remote / No git
5. **Project type** — Experimental (`code/`, `data/`, `output/`) / Computational (`src/`, `tests/`, `experiments/`, `results/`) / Theoretical (minimal) / Mixed

### Round 3 — Research Content

1. **Abstract / elevator pitch** — 1-2 sentences
2. **Key research questions** — up to 3
3. **Methodology overview** — one line

---

## Phase 1.5: Handle Existing Files

If the target directory already exists with files:

1. Scan for existing files (excluding `.claude/`)
2. Read documents to understand content
3. Present a reorganisation plan: keep in place / move to `docs/` / move to `docs/readings/` / move to `paper/` / move to `to-sort/` / absorb into seed files
4. Wait for approval, execute, double-check before deletions
5. Use interview content from existing docs to reduce Round 3 questions

If the directory doesn't exist, create it and proceed.

---

## Phase 2: Scaffold Directory

### Naming Convention

- **Slug** (kebab-case): `example-project` — citation keys, git refs
- **Folder name** (Title Case with spaces): `Example Project` — directory on disk

### Overleaf Separation (Hard Rule)

**`paper/` is for LaTeX source files ONLY.** No code, data, scripts, or computational artifacts. See `.claude/rules/overleaf-separation.md`.

### Common Core (always created)

```
<Folder Name>/
├── CLAUDE.md
├── README.md
├── MEMORY.md
├── .gitignore
├── .context/
│   ├── current-focus.md
│   └── project-recap.md
├── .claude/
│   ├── hooks/
│   │   └── copy-paper-pdf.sh   # PostToolUse hook — copies paper*/main.pdf → *_vcurrent.pdf
│   └── settings.local.json
├── correspondence/
│   └── reviews/           # .gitkeep (see scaffold-details.md for review structure)
├── docs/
│   ├── literature-review/  # .gitkeep
│   ├── readings/           # .gitkeep
│   └── venues/             # .gitkeep (submission/venue material only)
├── log/                   # .gitkeep
├── paper/                 # Symlink → Overleaf (Phase 4) — LaTeX source ONLY
├── reviews/               # .gitkeep (subdirs created on demand by review agents)
└── to-sort/               # .gitkeep
```

### Conditional Structure

**Experimental** — add: `code/python/`, `code/R/`, `data/raw/`, `data/processed/`, `output/figures/`, `output/tables/`, `output/logs/`

**Computational** — add: `src/<project-name>/` (with `__init__.py`), `tests/`, `experiments/configs/`, `results/`, `output/logs/`, `pyproject.toml`, `.python-version`

**Theoretical** — nothing extra.

**Mixed** — present elements and ask which to include.

**Venues:** When a target venue is known, seed `docs/venues/<venue-slug>/submission/`. For conference venues, also seed a submission checklist. Full venue structure and checklist template: [references/scaffold-details.md](references/scaffold-details.md).

### Python Tooling

**Always use `uv` — never bare `pip`, `python`, or `requirements.txt`.** For computational projects, init with `uv init`. For experimental projects, add `pyproject.toml` when dependencies are first needed.

### Implementation

```bash
mkdir -p <dir> && touch <dir>/.gitkeep  # Create all directories
mkdir -p .claude/hooks                   # Create hook, chmod +x
```

---

## Phase 3: Seed Files

### CLAUDE.md vs README.md

- **CLAUDE.md** — Instructions for Claude: safety rules, folder structure, conventions, symlink paths
- **README.md** — Human-readable overview: title, authors, abstract, status checklist, links

Both overlap on basic metadata but diverge in purpose. Follow the `lean-claude-md` rule for CLAUDE.md.

### Seed File Templates

Full templates: [`templates/seed-files.md`](templates/seed-files.md)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude instructions: overview, venue, RQs, setup, conventions |
| `README.md` | Human overview: title, authors, abstract, links, status |
| `.gitignore` | Standard ignores: OS, IDE, data, paper, Python, R, LaTeX |
| `MEMORY.md` | Knowledge base: notation, estimands, decisions, pitfalls |
| `.context/current-focus.md` | Initial "just initialised" state |
| `.context/project-recap.md` | Research design notes |
| `.claude/hooks/copy-paper-pdf.sh` | PDF copy hook |
| `log/YYYY-MM-DD-HHMM-setup.md` | Initial setup log: project name, creation date, scaffold type, next steps |
| `docs/pipeline-manifest.md` | **(Experimental/Computational only)** Script status, data files, manuscript figure manifest. Template: [`templates/pipeline-manifest.md`](templates/pipeline-manifest.md) |
| `run_all.sh` | **(Experimental/Computational only)** Multi-language pipeline executor (Python via uv, R, Stata). Template: [`templates/run-all.sh`](templates/run-all.sh). `chmod +x` after creation. |

### Permissions Sync

After writing `.claude/settings.local.json` (with hook config), merge global permissions into it so the new project starts with full permissions from day one:

1. Read `~/.claude/settings.json` → extract `permissions.allow` array
2. Read the newly created `.claude/settings.local.json`
3. Compute the union: `local_permissions ∪ global_permissions`
4. Write the merged `permissions.allow` back to `.claude/settings.local.json` (preserving the `hooks` key)

```bash
# Merge global permissions into the new project's settings
jq -s '.[0].permissions.allow as $global |
  .[1] | .permissions.allow = ((.permissions.allow // []) + $global | unique | sort)' \
  ~/.claude/settings.json .claude/settings.local.json > .claude/settings.local.json.tmp \
  && mv .claude/settings.local.json.tmp .claude/settings.local.json
```

Also merge the `permissions.deny` array using the same logic.

---

## Phase 4: Overleaf Symlink & Template

Create symlink, seed template files if selected, ensure `.latexmkrc` exists. Full commands and steps: [references/scaffold-details.md](references/scaffold-details.md#overleaf-symlink-commands-phase-4).

---

## Phase 5: Git Init (conditional)

**Skip entirely if the user chose "No git" in Round 2.**

```bash
cd "<project-path>" && git init && git branch -m main && git add . && git commit -m "Initialize project: <working-title>"
```

If GitHub remote requested: `gh repo create "user/<project-name>" --private --source=. --remote=origin --push`

If local git only: remind project syncs via Dropbox. **Do NOT push unless a remote was explicitly requested.**

---

## Phase 6: Task Management Integration

All paths relative to Task Management root.

### 6a. Update `.context/projects/_index.md`

Add a new row to the "Papers in Progress" table. Stage is typically "Idea" or "Literature Review".

### 6b. Create `.context/projects/papers/<short-name>.md`

Template in [references/scaffold-details.md](references/scaffold-details.md#papers-context-file-template).

### 6c. Update `.context/current-focus.md`

Add to Top 3 Active Projects or as an Open Loop. Use targeted `Edit` — do NOT rewrite the file.

### 6d. Create Notion Research Pipeline Entry

```
Database: YOUR-PIPELINE-DATABASE-ID-HERE
Properties: Name (title), Stage, Target Journal, Co-authors, Priority ("Medium")
```

Save the Notion page URL for the confirmation report.

---

## Phase 7: Confirmation Report

```
Created research project: <Working Title>

Directory:  <full path>
Structure:  <N> folders, <N> files
Git:        initialised on branch main (<short commit hash>)
GitHub:     <URL or "local-only (Dropbox sync)">
Overleaf:   paper/ → <target path>

Task Management updates:
  - projects/_index.md:           added row
  - projects/papers/<name>.md:    created
  - current-focus.md:             updated
  - Notion Research Pipeline:     created entry (<URL>)

Setup log:  log/<filename>    created

Next steps:
  1. Open Overleaf and set up main.tex
  2. Run /literature to begin literature review
  3. Start drafting in paper/
```

---

## Error Handling

- **Overleaf path doesn't exist:** Create symlink anyway (resolves when Overleaf syncs). Warn user.
- **gh CLI not available:** Skip GitHub, note in report.
- **Notion API fails:** Skip Notion entry, offer to retry.
- **Directory already exists:** Ask whether to continue or abort.

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/literature` | Run after init to begin literature search |
| `/project-safety` | Already handled — .gitignore and settings created during init |
| `/save-context` | Context library entries created during Phase 6 |
| `/session-log` | Offer to create a session log after init completes |
| `/interview-me` | To develop the research idea before scaffolding |
