---
name: init-project-research
description: "Use when you need to bootstrap a full research project with directory scaffold and Overleaf symlink."
allowed-tools: Bash(mkdir*), Bash(ln*), Bash(ls*), Bash(git*), Bash(touch*), Bash(jq*), Bash(uv*), Bash(curl*), Bash(wget*), Read, Write, Edit, Glob, Grep, Task, WebSearch, WebFetch, AskUserQuestion
argument-hint: "[project-name or no arguments for guided setup]"
---

# Init Project Research

> Interview-driven skill that scaffolds a research project directory, creates an Atlas topic, syncs to vault (Atlas + Pipeline + Venues), and integrates with the user's Task Management system.

## When to Use

- Starting a new research paper or project from scratch
- When the user says "new project", "set up a project", "init project", "bootstrap project"
- After deciding to pursue a new research idea that needs its own folder

## Overview

Eight phases, executed in order:

1. **Interview** — gather project details via structured questions
2. **Scaffold** — create directory structure based on project type
3. **Seed files** — populate CLAUDE.md, README.md, .gitignore with interview answers
4. **Overleaf symlink** — link `paper/` to Overleaf directory
5. **Git init** — initialise repo and make first commit
6. **Atlas sync** — create Atlas topic file, vault atlas entry, venue links, Dropbox folder
7. **Task Management sync** — update context library files
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
5. **GitHub release repo?** — Yes / No / Later. Only ask for Experimental, Computational, or Mixed projects. If Yes, create a `github-repo/` subdirectory with its own git repo for public code releases. If Later, just add `github-repo/` to `.gitignore` so it's ready when needed. Convention details: [`references/github-release-repo.md`](references/github-release-repo.md)
6. **Project type** — Experimental (`code/`, `data/`, `output/`) / Computational (`src/`, `tests/`, `experiments/`, `results/`) / Theoretical (minimal) / Mixed
7. **HPC scaffold?** — Only ask for Experimental, Computational, or Mixed. "Will this need Warwick Avon (GPU, long sweeps, large state spaces)?" Yes / No / Later. If Yes, scaffold `hpc/` with `submit.sbatch` + `sweep.sbatch` + `sync-up.sh` + `sync-down.sh` + `env-setup.sh` (+ `prestage-models.sh` for LLM projects) from `templates/slurm/` and reference implementations under `Projects/NLP/{adversarial-benchmark-detection,benchmark-gaming-llm-safety}/hpc/`. If Later, add `hpc/` to `.gitignore` placeholder — scaffold on demand. See [`docs/guides/hpc.md`](../../docs/guides/hpc.md) in Task Management.

### Round 3 — Research Content

Paper type, abstract, key research questions, then paper-type-specific questions (empirical/theoretical/methodological/mixed) adapted from Lopez-Lira's idea evaluation template.

Full question set and storage instructions: [`references/interview-round3.md`](references/interview-round3.md)

---

## Phase 1.4: Pre-Scaffold Duplication Check

**Run this before creating any directory.** Catches near-duplicate projects and paper sub-projects that would otherwise get scaffolded alongside an existing one.

1. **Atlas topic search** — grep for near-matches by title, slug keywords, and theme:
   ```bash
   grep -ril "<title-keyword>" ~/Research-Vault/atlas/ 2>/dev/null
   ```
   Review hits. If any existing atlas topic covers the same scope, stop and ask the user whether to extend the existing topic or proceed with a new one.

2. **Sibling directory listing** — list siblings in the parent theme folder:
   ```bash
   ls -d "$RESEARCH_ROOT/<theme>/"*/ 2>/dev/null
   ```
   Compare proposed folder name against siblings. Flag near-duplicates (same keywords, same stem with different venue suffix, typo-distance ≤ 2).

3. **Paper sub-project check** — if scaffolding a new `paper-{venue}/` inside an existing project, list existing `paper*/` dirs and check for overlap in manuscript content (not just venue) before creating.

If any near-match is found, present the list to the user and confirm whether to proceed, merge, or extend. Do not silently scaffold alongside a duplicate.

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

### LaTeX-First Default (Hard Rule)

**Research papers are drafted in LaTeX (`.tex`), never Markdown.** When scaffolding, seed `paper-{venue}/paper/main.tex` from the LaTeX working-paper template. Do not create Markdown drafts under `paper*/` or propose Markdown as an interim format — papers compile via `/latex` and sync to Overleaf. Markdown is reserved for README, notes, and context files outside `paper*/`.

### Common Core + Conditional Structure

**Common core** (always created): `CLAUDE.md`, `README.md`, `MEMORY.md`, `.gitignore`, `.context/`, `.claude/`, `docs/` (literature-review, readings, venues), `log/`, `paper-{venue}/` (with symlink + `correspondence/referee-reviews/`), `backup/`, `github-repo/` (optional), `knowledge/`, `correspondence/internal-reviews/`, `reviews/`, `to-sort/`.

| Project type | Adds |
|--------------|------|
| Experimental | `code/python/`, `code/R/`, `data/raw/`, `data/processed/`, `output/{figures,tables,logs}/` |
| Computational | `src/<project>/`, `tests/`, `experiments/configs/`, `results/`, `pyproject.toml`, `.python-version` |
| Theoretical | — |
| Mixed | Prompt user |

**HPC scaffold** (optional, when Round 2 Q7 answered Yes): adds `hpc/{submit.sbatch,sweep.sbatch,env-setup.sh,sync-up.sh,sync-down.sh,README.md}` — entry point matches the project's `src/` package. For LLM projects also add `prestage-models.sh`. All sbatch files log `git-sha.txt` + `git-status.txt` to `OUT_DIR` before `srun`. See Task Management `templates/slurm/` + [`docs/guides/hpc.md`](../../docs/guides/hpc.md).

**Venues:** seed `docs/venues/<venue-slug>/submission/`; conference venues also get a submission checklist.

**Python tooling:** always `uv` — never bare `pip`, `python`, or `requirements.txt`.

**Full scaffold tree** (directory comments, hook details, .gitkeep placement) and implementation commands: [`references/scaffold-tree.md`](references/scaffold-tree.md).

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

After writing `.claude/settings.local.json` (with hook config), merge global permissions from `~/.claude/settings.json` into it so the new project starts with full permissions from day one. `jq` union command and deny-array handling: [`references/paper-directory.md`](references/paper-directory.md) § Permissions Sync.

---

## Phase 4: Overleaf Symlink & Template

**Nested pattern:** each paper submission is a real directory at project root (e.g., `paper/`, `paper-ccs/`) containing a `paper/` **symlink** to the Overleaf folder. Venue-specific files (checklists, cover letters, R&R responses) live alongside the symlink without being synced to Overleaf.

**Overleaf naming:** `Paper {THEME_PREFIX} {Title Cased Slug}` — theme prefix is a short abbreviation (ASG, BDS, EnvEcon, HAI, IO, MechDes, NLP, OR, OrgStrat, PolSci). For multi-venue: append venue in parentheses.

**Create the Overleaf folder via `mkdir`** (Overleaf auto-creates a project from a new folder in the Overleaf root read from `~/.config/task-mgmt/overleaf-root`). Never rename or delete Overleaf folders — see `.claude/rules/overleaf-separation.md`.

**Backup:** create `backup/<paper-dir-name>/` subdirectories for each paper. The daily `backup-overleaf-papers.sh` script populates them.

**Full nested structure, theme-prefix table, symlink commands, and backup loop:** [`references/paper-directory.md`](references/paper-directory.md)

---

## Phase 5: Git Init (conditional)

**Skip entirely if the user chose "No git" in Round 2.**

```bash
cd "<project-path>" && git init && git branch -m main && git add . && git commit -m "Initialize project: <working-title>"
```

If GitHub remote requested: `gh repo create "user/<project-name>" --private --source=. --remote=origin --push`

If local git only: remind to push before switching machines. **Do NOT push unless a remote was explicitly requested.**

---

## Phase 6: Atlas Sync

Creates the research topic in all systems: local file → vault atlas → Venues → project folder → documentation.

Full steps (6a–6e) and Atlas defaults: [`references/atlas-sync.md`](references/atlas-sync.md)

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
|  | Runs automatically in Phase 8b — novelty assessment |
| `/project-safety` | Already handled — .gitignore and settings created during init |
| `/save-context` | Context library entries created during Phase 7 |
| `/session-log` | Offer to create a session log after init completes |
| `/interview-me` | To develop the research idea before scaffolding |
| `/atlas-deploy` | After init, run to compile and deploy changes to atlas.user.com |
| `/audit-project-research` | **Must mirror this scaffold.** When init adds a new directory or convention (e.g., `github-repo/`), add a matching audit phase there and update `/atlas-audit` SA1. |
| `/atlas-audit` | **Drift trigger:** new projects change theme dir counts — see `atlas-audit/references/drift-checks.md`. SA1 structure checks must stay consistent with this scaffold. |
| `references/domain-profile-template.md` | Template for economics/field-specific domain profiles — copy to project's `docs/domain-profile.md` during init for economics papers |
