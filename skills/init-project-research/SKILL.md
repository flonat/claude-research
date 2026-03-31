---
name: init-project-research
description: "Use when you need to bootstrap a full research project with directory scaffold and Overleaf symlink."
allowed-tools: Bash(mkdir*), Bash(ln*), Bash(ls*), Bash(git*), Bash(touch*), Bash(jq*), Bash(uv*), Bash(scout *), Bash(curl*), Bash(wget*), Read, Write, Edit, Glob, Grep, Task, WebSearch, WebFetch, AskUserQuestion
argument-hint: "[project-name or no arguments for guided setup]"
---

# Init Project Research

> Interview-driven skill that scaffolds a research project directory, creates an Atlas topic, syncs to vault (Atlas + Pipeline + Venues), and integrates with the user's Task Management system.

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
6. **Atlas & Pipeline sync** — create Atlas topic file, vault atlas entry, Pipeline row, venue links, Dropbox folder
7. **Task Management sync** — update context library files
8. **Literature & Discovery** — run literature review + scout novelty assessment
9. **Confirmation** — report what was created

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
4. **Research area** — which parent folder under Projects/. Scan for existing theme folders and present as options. Also offer "New topic folder" and "Other location".
5. **Target venue** — journal, conference, or preprint:
   - **Journal:** Check CABS AJG ranking via `.context/resources/venue-rankings.md` and the CSV (`.context/resources/venue-rankings/abs_ajg_2024.csv`). For SJR score, query the Elsevier Serial Title API (see venue-rankings.md for snippet; requires `SCOPUS_API_KEY`). Flag journals below CABS 4 with alternatives.
   - **Conference:** Check CORE ranking via `.context/resources/venue-rankings.md` and the CSV (`.context/resources/venue-rankings/core_2026.csv`). Capture page limit, format, review type, anonymisation, deadlines.
   - **Preprint:** Note the server (arXiv, SSRN) — no ranking check needed.
6. **Deadline** — submission deadline if known

### Round 2 — Setup Details

1. **Overleaf project** — ask: "Does the Overleaf project already exist, or should I create it?" If it exists, get the folder name under the Overleaf root (read from `~/.config/task-mgmt/overleaf-root`, fallback `~/Apps/Overleaf/`) and verify the path. If it doesn't exist, create it via `mkdir` (creating a folder in the Overleaf root automatically creates an Overleaf project).
2. **LaTeX template** — scan `Task Management/templates/` for options. Default: Working Paper (`templates/latex-wp/`). Also offer "None".
3. **Overleaf external sharing link** — read-only URL for collaborators
4. **Git repository?** — Local git (Recommended) / GitHub remote / No git
5. **Project type** — Experimental (`code/`, `data/`, `output/`) / Computational (`src/`, `tests/`, `experiments/`, `results/`) / Theoretical (minimal) / Mixed

### Round 3 — Research Content

Paper type, abstract, key research questions, then paper-type-specific questions (empirical/theoretical/methodological/mixed) adapted from Lopez-Lira's idea evaluation template.

Full question set and storage instructions: [`references/interview-round3.md`](references/interview-round3.md)

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
│   │   └── copy-paper-pdf.sh   # PostToolUse hook — copies paper-*/paper/main.pdf → backup/*_vcurrent.pdf
│   └── settings.local.json
├── correspondence/
│   └── reviews/           # .gitkeep (see scaffold-details.md for review structure)
├── docs/
│   ├── literature-review/  # .gitkeep
│   ├── readings/           # .gitkeep
│   └── venues/             # .gitkeep (submission/venue material only)
├── log/                   # .gitkeep
├── paper/                 # Paper directory (Phase 4):
│   └── paper/             #   Symlink → Overleaf — LaTeX source ONLY
│                          #   Venue-specific files (checklists, cover letters) live in parent
├── backup/                # Local backups of Overleaf paper directories (subdirs per paper)
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

### Paper Directory Convention (Nested Pattern)

Each paper submission gets its own **real directory** at project root (e.g., `paper/`, `paper-ccs/`, `paper-rg/`). Inside that directory, a `paper/` **symlink** points to the Overleaf folder. This nesting allows venue-specific files (submission checklists, cover letters, response documents, reviewer correspondence) to live alongside the Overleaf content without being synced to Overleaf.

**Structure:**
```
paper-ccs/                    # Real directory (venue wrapper)
├── paper/                    # Symlink → Overleaf directory
├── submission-checklist.md   # Venue-specific (not in Overleaf)
├── cover-letter.tex          # Venue-specific
└── response-to-reviewers.tex # Added after R&R
```

**Single-paper projects** use the same pattern:
```
paper/                        # Real directory (venue wrapper)
└── paper/                    # Symlink → Overleaf directory
```

**Naming convention:** `Paper {THEME_PREFIX} {Title Cased Slug}` — e.g., `Paper ASG Privacy Compliance Gaming`, `Paper BDS Identity Belief Alignment`. The theme prefix is a short abbreviation of the research theme:

| Theme | Prefix |
|-------|--------|
| Category A | ASG |
| Category B | BDS |
| Category C | EnvEcon |
| Category D | HAI |
| Industrial Organisation | IO |
| Mechanism Design | MechDes |
| NLP & Computational AI | NLP |
| Operations Research | OR |
| Category F | OrgStrat |
| Category G | PolSci |

For multi-venue submissions, append the venue abbreviation in parentheses: `Paper ASG Privacy Compliance Gaming (CCS)`.

**Commands:**
```bash
# Create the Overleaf project folder if it doesn't exist yet
# (creating a folder in the Overleaf root automatically creates an Overleaf project)
overleaf_root="$(cat ~/.config/task-mgmt/overleaf-root 2>/dev/null || echo ~/Apps/Overleaf)"
mkdir -p "$overleaf_root/Paper ASG Privacy Compliance Gaming (CCS)"

# For each venue:
mkdir -p paper-ccs
ln -s "$overleaf_root/Paper ASG Privacy Compliance Gaming (CCS)" paper-ccs/paper

# Single paper:
mkdir -p paper
ln -s "$overleaf_root/Paper BDS Identity Belief Alignment" paper/paper
```

**Important:** Never rename or delete Overleaf folders — see `.claude/rules/overleaf-separation.md` (Overleaf Folder Lifecycle).

Ensure `.latexmkrc` exists inside the Overleaf target (the symlink destination), not in the wrapper directory. Full template setup: [references/scaffold-details.md](references/scaffold-details.md#overleaf-symlink-commands-phase-4).

### Backup Directory

After creating paper directories, create a `backup/` directory with one subdirectory per paper:

```bash
mkdir -p backup/
for d in paper*/; do
  mkdir -p "backup/$(basename "$d")"
done
```

**Convention:** One `backup/` directory at project root, with subdirectories matching each `paper*` directory name. The daily `backup-overleaf-papers.sh` script copies `.tex`/`.bib`/style files from the Overleaf symlink targets into these subdirectories.

**Examples:**
- Single paper: `backup/paper/`
- Multi-paper: `backup/paper-ccs/`, `backup/paper-rg/`

---

## Phase 5: Git Init (conditional)

**Skip entirely if the user chose "No git" in Round 2.**

```bash
cd "<project-path>" && git init && git branch -m main && git add . && git commit -m "Initialize project: <working-title>"
```

If GitHub remote requested: `gh repo create "user/<project-name>" --private --source=. --remote=origin --push`

If local git only: remind to push before switching machines. **Do NOT push unless a remote was explicitly requested.**

---

## Phase 6: Atlas & Pipeline Sync

Creates the research topic in all systems: local file → vault atlas → vault pipeline → Venues → project folder → documentation.

Full steps (6a–6f) and Atlas defaults: [`references/atlas-pipeline-sync.md`](references/atlas-pipeline-sync.md)

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

## Phase 8: Literature & Discovery

After scaffolding and syncing, automatically run a literature review (`/literature`) and scout novelty assessment (`/scout`) in parallel via sub-agents.

Full steps (8a–8c) and error handling: [`references/literature-discovery.md`](references/literature-discovery.md)

---

## Phase 9: Confirmation Report

Print the structured confirmation after all phases complete.

Full template: [`references/confirmation-report.md`](references/confirmation-report.md)

---

## Error Handling

- **Overleaf path doesn't exist:** Create symlink anyway (resolves when Overleaf syncs). Warn user.
- **gh CLI not available:** Skip GitHub, note in report.
- **taskflow MCP server fails:** Skip vault entry, offer to retry.
- **Directory already exists:** Ask whether to continue or abort.
- **Duplicate Atlas slug:** Flag and skip Atlas creation — may need merge into existing topic.

## Never Do These (Atlas)

- Never create a topic file without YAML frontmatter — it breaks RECAP.md generation
- Never hard-code vault theme paths — always look them up (they change if recreated)
- Never use Methods values outside the valid multi-select options — the API will reject
- Never use venue/output names as slugs — the slug names the research idea
- Never create a separate topic file for a companion paper of an existing idea — add it as an output instead

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/literature` | Runs automatically in Phase 8a — initial literature review |
| `/scout` | Runs automatically in Phase 8b — novelty assessment |
| `/project-safety` | Already handled — .gitignore and settings created during init |
| `/save-context` | Context library entries created during Phase 7 |
| `/session-log` | Offer to create a session log after init completes |
| `/interview-me` | To develop the research idea before scaffolding |
| `/atlas-deploy` | After init, run to compile and deploy changes to atlas.user.com |
| `/atlas-review` | **Drift trigger:** new projects change theme dir counts — see `atlas-review/references/drift-checks.md` |
| `references/domain-profile-template.md` | Template for economics/field-specific domain profiles — copy to project's `docs/domain-profile.md` during init for economics papers |
