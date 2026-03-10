---
name: init-project-research
description: "Bootstrap a research project: interview, scaffold directory, Overleaf symlink, git init, Atlas topic, Notion Pipeline entry, venue links. Triggers: 'new research project', 'start a new paper', 'add this to the atlas'. Not for lightweight setups — use /init-project-light instead."
allowed-tools: Bash(mkdir*), Bash(ln*), Bash(ls*), Bash(git*), Bash(touch*), Bash(jq*), Bash(uv*), Read, Write, Edit, Glob, Grep, Task, AskUserQuestion, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-fetch, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-update-page
argument-hint: "[project-name or no arguments for guided setup]"
---

# Init Project Research

> Interview-driven skill that scaffolds a research project directory, creates an Atlas topic, syncs to Notion (Atlas + Pipeline + Venues), and integrates with the user's Task Management system.

## When to Use

- Starting a new research paper or project from scratch
- When the user says "new project", "set up a project", "init project", "bootstrap project"
- After deciding to pursue a new research idea that needs its own folder
- When scaffolding ideas from Scout reports, brainstorming, or supervisor meetings

## Overview

Eight phases, executed in order:

1. **Interview** — gather project details via structured questions
2. **Scaffold** — create directory structure based on project type
3. **Seed files** — populate CLAUDE.md, README.md, .gitignore with interview answers
4. **Overleaf symlink** — link `paper/` to Overleaf directory
5. **Git init** — initialise repo and make first commit
6. **Atlas & Pipeline sync** — create Atlas topic file, Notion Atlas entry, Pipeline row, venue links, Dropbox folder
7. **Task Management sync** — update context library files
8. **Confirmation** — report what was created

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
│   ├── field-calibration.md
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
mkdir -p .claude/state                   # Machine-specific memory (gitignored)
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
| `.context/field-calibration.md` | Per-project domain profile for agents (placeholder template — `/interview-me` Phase 7 populates it) |
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

## Phase 6: Atlas & Pipeline Sync

Creates the research topic in all 6 systems: local file → Notion Atlas → Notion Pipeline → Venues → Dropbox → documentation.

### 6a. Create Atlas Topic File

1. Read `research/atlas/themes.md` — current themes and topic lists
2. Glob `research/atlas/topics/**/*.md` — existing slugs (avoid duplicates)
3. Determine the **slug** (kebab-case, 2-4 words). **Names the idea, not a venue or output.** Anti-patterns: `mres-dissertation`, `icml-paper`. Good: `information-entropy`, `carbon-collusion`.
4. Write `research/atlas/topics/{theme-dir}/{slug}.md` using the YAML frontmatter template from [`references/atlas-schema.md`](references/atlas-schema.md). Include `## Description`, `## Key References`, `## Open Questions`.
5. Update `research/atlas/themes.md` — add slug to the correct theme's topic list. If new theme needed: add row, create directory, create Notion theme entry (`data_source_id: 2e8baef4-3e2e-4ea5-b25a-18a71ed47690`).

### 6b. Create Notion Atlas Entry

1. Look up the theme's Notion page ID via `notion-search`
2. Create Atlas entry via `notion-create-pages` with parent `data_source_id: 0a227f82-60f4-451a-a163-bff2ce8fa9c3`
3. Map YAML fields to Notion properties per [`references/atlas-schema.md`](references/atlas-schema.md)
4. Set Theme relation: `"[\"https://www.notion.so/{theme-page-id}\"]"`
5. Only use valid Methods multi-select values (see schema reference)

### 6c. Create Notion Pipeline Entry

1. Create Pipeline row via `notion-create-pages` with parent `data_source_id: YOUR-PIPELINE-DATABASE-ID-HERE`
2. Set: Name (title), Stage, Target Journal, Co-authors, Priority ("Medium")
3. Link to Atlas topic via "Related Topics" relation
4. Link to Venues via "Target Venue" relation (search Venues DB `YOUR-CONFERENCES-DATABASE-ID-HERE` for venue pages)
5. Save the Pipeline Notion page URL for the confirmation report

### 6d. Create Dropbox Folder

```bash
mkdir -p "~/Library/CloudStorage/YOUR-CLOUD/Research/{Theme Name}/{Project Name}"
```

### 6e. Regenerate RECAP.md

```bash
uv run python research/atlas/generate_recap.py
```

### 6f. Update Atlas Counts

If topic or theme count changed, update `research/atlas/CLAUDE.md` topic/theme counts and theme directory listing.

### Atlas Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Status | `Idea` | User specifies |
| Priority | `Medium` | User specifies |
| Data Availability | `None` | User specifies |
| Feasibility | `Medium` | User specifies |
| Institution | Infer from theme/co-author | User specifies |

---

## Phase 7: Task Management Integration

All paths relative to Task Management root.

### 7a. Update `.context/projects/_index.md`

Add a new row to the "Papers in Progress" table. Stage is typically "Idea" or "Literature Review".

### 7b. Create `.context/projects/papers/<short-name>.md`

Template in [references/scaffold-details.md](references/scaffold-details.md#papers-context-file-template).

### 7c. Update `.context/current-focus.md`

Add to Top 3 Active Projects or as an Open Loop. Use targeted `Edit` — do NOT rewrite the file.

---

## Phase 8: Confirmation Report

```
Created research project: <Working Title>

Directory:  <full path>
Structure:  <N> folders, <N> files
Git:        initialised on branch main (<short commit hash>)
GitHub:     <URL or "local-only (Dropbox sync)">
Overleaf:   paper/ → <target path>

Atlas & Pipeline:
  - Atlas topic file:             research/atlas/topics/{theme}/{slug}.md
  - Notion Atlas entry:           created (<URL>)
  - Notion Pipeline entry:        created (<URL>)
  - Venue links:                  <venue names>
  - Dropbox folder:               created
  - RECAP.md:                     regenerated

Task Management updates:
  - projects/_index.md:           added row
  - projects/papers/<name>.md:    created
  - current-focus.md:             updated

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
- **Duplicate Atlas slug:** Flag and skip Atlas creation — may need merge into existing topic.

## Never Do These (Atlas)

- Never create a topic file without YAML frontmatter — it breaks RECAP.md generation
- Never hard-code Notion theme page IDs — always look them up (they change if recreated)
- Never use Methods values outside the valid multi-select options — the API will reject
- Never use venue/output names as slugs — the slug names the research idea
- Never create a separate topic file for a companion paper of an existing idea — add it as an output instead

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/literature` | Run after init to begin literature search |
| `/project-safety` | Already handled — .gitignore and settings created during init |
| `/save-context` | Context library entries created during Phase 7 |
| `/session-log` | Offer to create a session log after init completes |
| `/interview-me` | To develop the research idea before scaffolding |
| `/deploy-atlas` | After init, run to compile and deploy changes to atlas.user.com |
| `/audit-atlas-portfolio` | **Drift trigger:** new projects change theme dir counts — see `audit-atlas-portfolio/references/drift-checks.md` |
