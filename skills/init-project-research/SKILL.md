---
name: init-project-research
description: "Use when you need to bootstrap a full research project with directory scaffold and Overleaf symlink."
allowed-tools: Bash(mkdir*), Bash(ln*), Bash(ls*), Bash(git*), Bash(touch*), Bash(jq*), Bash(uv*), Bash(curl*), Bash(wget*), Read, Write, Edit, Glob, Grep, Task, WebSearch, WebFetch, AskUserQuestion
argument-hint: "[project-name or no arguments for guided setup]"
---

# Init Project Research

Interview-driven skill that scaffolds a research project directory, creates an Atlas topic, syncs to vault (Atlas + Pipeline + Venues), and integrates with the user's Task Management system.

## When to Use

- Starting a new research paper or project from scratch
- When the user says "new project", "set up a project", "init project", "bootstrap project"
- After deciding to pursue a new research idea that needs its own folder

## Modes

| Invocation | Behaviour |
|-----------|-----------|
| `/init-project-research` (no args) | Guided: full interview, no auto-detection unless CWD already contains project files |
| `/init-project-research <name>` | Targeted: uses `<name>` as the proposed slug, runs auto-detection if the directory exists, still walks the interview |

Both modes execute Phases 1–10 in order. The argument only seeds the slug guess in Round 1.

## Overview

Ten phases, in order:

1. **Interview** — gather project details via three structured rounds
2. **Validate** — pre-scaffold checks (atlas dup, sibling directories, existing files)
3. **Scaffold** — create directory structure based on project type
4. **Seed files** — populate CLAUDE.md, README.md, .gitignore from interview answers
5. **Overleaf symlink** — link `paper/` to Overleaf folder via mkdir + symlink
6. **Git init** — initialise repo and make first commit (conditional)
7. **Atlas sync** — create Atlas topic file, vault atlas entry, venue links
8. **Task Management integration** — update context library files
9. **Literature & Discovery** — run `/literature` +  in parallel
10. **Confirmation** — report what was created

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

1. **Project slug** — kebab-case identifier (e.g., `costly-voice`). Folder name on disk is Title Case with spaces (`Costly Voice`). Confirm the derived folder name.
2. **Working title** — full paper/project title.
3. **Authors / collaborators** — names and affiliations.
4. **Research area** — which parent folder under Projects/. Scan for existing theme folders and present as options. Also offer "New topic folder" and "Other location".
5. **Target venue** — journal, conference, or preprint. Ranking lookup, deadline capture, and CSV paths: [`references/round-1-venue.md`](references/round-1-venue.md).
6. **Deadline** — submission deadline if known.

### Round 2 — Setup Details

1. **Overleaf project** — exists or create? Read root from `~/.config/task-mgmt/overleaf-root` (fallback `~/Apps/Overleaf/`). Creating a folder under that root auto-creates the Overleaf project. Symlink details deferred to Phase 5.
2. **LaTeX template** — scan `Task Management/templates/` for options. Default: Working Paper (`templates/latex-wp/`). Also offer "None".
3. **Overleaf external sharing link** — read-only URL for collaborators.
4. **Git repository?** — Local git (Recommended) / GitHub remote / No git.
5. **GitHub release repo?** — only ask for Experimental, Computational, or Mixed projects. Yes / No / Later. Convention details: [`references/round-2-github.md`](references/round-2-github.md).
6. **Project type** — Experimental (`code/`, `data/`, `output/`) / Computational (`src/`, `tests/`, `experiments/`, `results/`) / Theoretical (minimal) / Mixed.
7. **HPC scaffold?** — only ask for Experimental, Computational, or Mixed. Yes / No / Later. Sbatch templates, sync scripts, project conventions: [`references/round-2-hpc.md`](references/round-2-hpc.md).

### Round 3 — Research Content

Paper type, abstract, key research questions, then paper-type-specific questions (empirical/theoretical/methodological/mixed) adapted from Lopez-Lira's idea evaluation template.

Full question set: [`references/interview-round3.md`](references/interview-round3.md).

---

## Phase 2: Validate

Pre-scaffold checks. Run before any directory creation. If any near-match is found, present the list to the user and confirm whether to proceed, merge, or extend. Do not silently scaffold alongside a duplicate.

1. **Atlas topic search** — grep for near-matches by title, slug keywords, theme:
   ```bash
   grep -ril "<title-keyword>" ~/Research-Vault/atlas/ 2>/dev/null
   ```
2. **Sibling directory listing** — list siblings in the parent theme folder, flag near-duplicates (same keywords, same stem with different venue suffix, typo-distance ≤ 2):
   ```bash
   ls -d "$RESEARCH_ROOT/<theme>/"*/ 2>/dev/null
   ```
3. **Paper sub-project check** — if scaffolding a new `paper-{venue}/` inside an existing project, list existing `paper*/` dirs and check for manuscript-content overlap (not just venue) before creating.
4. **Existing-files reorganisation** — if the target directory already exists with files, scan (excluding `.claude/`), read documents, present a reorganisation plan: keep in place / move to `docs/` / move to `docs/readings/` / move to `paper/` / move to `to-sort/` / absorb into seed files. Wait for approval, execute, double-check before deletions. Use any extracted interview content to reduce Round 3 questions.

If the directory doesn't exist, create it and proceed.

---

## Phase 3: Scaffold Directory

### Naming Convention

- **Slug** (kebab-case): `example-project` — citation keys, git refs.
- **Folder name** (Title Case with spaces): `Example Project` — directory on disk.

### Hard Rules

- **`paper/` is for LaTeX source files ONLY.** No code, data, scripts, computational artifacts. See `.claude/rules/overleaf-separation.md`.
- **Research papers are drafted in LaTeX (`.tex`), never Markdown.** Seed `paper-{venue}/paper/main.tex` from the LaTeX working-paper template. No Markdown drafts under `paper*/` — papers compile via `/latex` and sync to Overleaf. Markdown is reserved for README, notes, and context files outside `paper*/`.

### Common Core + Conditional Structure

**Common core** (always created): `CLAUDE.md`, `README.md`, `MEMORY.md`, `.gitignore`, `.context/`, `.claude/`, `docs/` (literature-review, readings, venues), `log/`, `paper-{venue}/` (with symlink + `correspondence/referee-reviews/`), `backup/`, `github-repo/` (optional), `knowledge/`, `correspondence/internal-reviews/`, `reviews/`, `to-sort/`.

| Project type | Adds |
|--------------|------|
| Experimental | `code/python/`, `code/R/`, `data/raw/`, `data/processed/`, `output/{figures,tables,logs}/` |
| Computational | `src/<project>/`, `tests/`, `experiments/configs/`, `results/`, `pyproject.toml`, `.python-version` |
| Theoretical | — |
| Mixed | Prompt user |

**HPC scaffold** (optional, when Round 2 Q7 = Yes): adds `hpc/{submit.sbatch,sweep.sbatch,env-setup.sh,sync-up.sh,sync-down.sh,README.md}`. Full template list and sbatch invariants: [`references/round-2-hpc.md`](references/round-2-hpc.md).

**Venues:** seed `docs/venues/<venue-slug>/submission/`; conference venues also get a submission checklist.

**Python tooling:** always `uv` — never bare `pip`, `python`, or `requirements.txt`.

Full scaffold tree, hook details, .gitkeep placement, implementation commands: [`references/scaffold-tree.md`](references/scaffold-tree.md).

---

## Phase 4: Seed Files

### CLAUDE.md vs README.md

- **CLAUDE.md** — instructions for Claude: safety rules, folder structure, conventions, symlink paths. Follow the `lean-claude-md` rule.
- **README.md** — human-readable overview: title, authors, abstract, status checklist, links.

Both overlap on basic metadata but diverge in purpose.

Full templates: [`templates/seed-files.md`](templates/seed-files.md).

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude instructions: overview, venue, RQs, setup, conventions |
| `README.md` | Human overview: title, authors, abstract, links, status |
| `.gitignore` | Standard ignores: OS, IDE, data, paper, Python, R, LaTeX |
| `MEMORY.md` | Knowledge base: notation, estimands, decisions, pitfalls |
| `.context/current-focus.md` | Initial "just initialised" state |
| `.context/field-calibration.md` | Per-project domain profile placeholder (`/interview-me` populates) |
| `.context/project-recap.md` | Research design notes |
| `.claude/hooks/copy-paper-pdf.sh` | PDF copy hook |
| `log/YYYY-MM-DD-HHMM-setup.md` | Initial setup log |
| `docs/pipeline-manifest.md` | **Experimental/Computational only** — script/data/figure manifest. Template: [`templates/pipeline-manifest.md`](templates/pipeline-manifest.md) |
| `run_all.sh` | **Experimental/Computational only** — multi-language pipeline executor. Template: [`templates/run-all.sh`](templates/run-all.sh). `chmod +x` after creation. |

### Permissions Sync

After writing `.claude/settings.local.json`, merge global permissions from `~/.claude/settings.json` into it so the new project starts with full permissions from day one. `jq` union command and deny-array handling: [`references/paper-directory.md`](references/paper-directory.md) § Permissions Sync.

---

## Phase 5: Overleaf Symlink & Template

**Nested pattern:** each paper submission is a real directory at project root (e.g., `paper-ccs/`) containing a `paper/` **symlink** to the Overleaf folder. Venue-specific files (checklists, cover letters, R&R responses) live alongside the symlink without being synced to Overleaf.

**Overleaf naming:** `Paper {THEME_PREFIX} {Title Cased Slug} ({VENUE})` — theme prefix AND venue suffix both required, even for single-venue papers. Examples: `Paper ASG Privacy Compliance Gaming (CCS)`, `Paper MechDes Strategic Compliance (NeurIPS 26)`.

**Create the Overleaf folder via `mkdir`** under the root from `~/.config/task-mgmt/overleaf-root`. Overleaf auto-creates a project from a new folder. Never rename or delete Overleaf folders — see `.claude/rules/overleaf-separation.md`.

**Backup:** create `backup/<paper-dir-name>/` for each paper. Daily `backup-overleaf-papers.sh` populates them.

Full nested structure, theme-prefix table, symlink commands, backup loop: [`references/paper-directory.md`](references/paper-directory.md).

---

## Phase 6: Git Init (conditional)

Skip entirely if the user chose "No git" in Round 2.

```bash
cd "<project-path>" && git init && git branch -m main && git add . && git commit -m "Initialize project: <working-title>"
```

If GitHub remote requested: `gh repo create "user/<project-name>" --private --source=. --remote=origin --push`.

If local git only: remind to push before switching machines. **Do NOT push unless a remote was explicitly requested.**

---

## Phase 7: Atlas Sync

Creates the research topic in all systems: local file → vault atlas → Venues → project folder → documentation.

Full steps, Atlas defaults, and Atlas anti-patterns ("Never Do These"): [`references/atlas-sync.md`](references/atlas-sync.md).

---

## Phase 8: Task Management Integration

Three sub-steps writing into the Task Management context library: index update, paper context file, current-focus integration.

Full sub-steps, templates, edit policies: [`references/task-mgmt-sync.md`](references/task-mgmt-sync.md).

---

## Phase 9: Literature & Discovery

After scaffolding and syncing, run `/literature` and  in parallel via sub-agents for initial literature review + novelty assessment.

Full steps and error handling: [`references/literature-discovery.md`](references/literature-discovery.md).

---

## Phase 10: Confirmation Report

Print the structured confirmation after all phases complete.

Full template: [`references/confirmation-report.md`](references/confirmation-report.md).

---

## Error Handling & Rollback

Per the `multi-system-completeness` rule, partial state is the dominant failure mode for this skill. Track which phases completed, surface incomplete state, do not silently move on.

| Error | Response |
|-------|----------|
| Overleaf path doesn't exist | Create symlink anyway (resolves when Overleaf syncs). Warn user. |
| `gh` CLI not available | Skip GitHub remote, note in Phase 10 report. |
| `taskflow` MCP server fails | Skip vault entry, offer to retry. Note as incomplete in Phase 10. |
| Directory already exists with files | Phase 2 handles via reorganisation plan, not an error. |
| Duplicate Atlas slug | Flag and skip Atlas creation — may need merge into existing topic. |
| Phase fails after a previous phase wrote to disk | Phase 10 must list which systems were touched (local dir / Overleaf / vault / atlas / git remote) and which were not, so manual cleanup is targeted, not a guess. |

---

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/literature` | Runs in Phase 9 — initial literature review |
|  | Runs in Phase 9 — novelty assessment |
| `/project-safety` | Already handled — `.gitignore` and settings created during init |
| `/save-context` | Context library entries created during Phase 8 |
| `/session-log` | Offer to create a session log after init completes |
| `/interview-me` | To develop the research idea before scaffolding |
| `packages/atlas-vault/generate_recap.py` | Optional after init — regenerates `RECAP.md` portfolio index. Not required for `atlas.user.com` (atlas-workspace reads vault directly via Syncthing). |
| `/atlas-deploy` | Manual-only skill — user can run for schema validation + Mac Mini launchd restart. NOT needed for atlas.user.com to surface a new topic; that's automatic via Syncthing. |
| `/audit-project-research` | **Must mirror this scaffold.** When init adds a new directory or convention, add a matching audit phase there and update `/atlas-audit` SA1. |
| `/atlas-audit` | **Drift trigger:** new projects change theme dir counts — see `atlas-audit/references/drift-checks.md`. SA1 structure checks must stay consistent with this scaffold. |
| [`references/domain-profile-template.md`](references/domain-profile-template.md) | Template for economics/field-specific domain profiles — copy to project's `docs/domain-profile.md` during init for economics papers. |
