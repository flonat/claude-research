---
name: audit-project-research
description: "Use when you need to audit a research project against the init-project-research template."
allowed-tools: Bash(ls*), Bash(readlink*), Bash(git*), Bash(diff*), Bash(jq*), Read, Glob, Grep
argument-hint: "[project-path or no arguments for CWD]"
---

# Audit Project Research

Compare a research project's directory structure against the current `/init-project-research` template and report gaps. **Report-only.**

## When to Use

- After revisiting a project set up a while ago
- When the template has been updated and you want to check older projects
- Before submission — verify nothing is missing
- When a project "feels messy" and you want a structured audit

## When NOT to Use

- **Setting up a new project** — use `/init-project-research`
- **Fixing issues** — this skill only reports; user decides what to action
- **Auditing all projects at once** — use `/atlas-audit` (this skill is per-project)

## Modes

| Invocation | Behaviour |
|-----------|-----------|
| `/audit-project-research` (no args) | Audits CWD. Aborts if CWD is not a project directory. |
| `/audit-project-research <project-path>` | Audits the given path. Resolves to absolute first. |

## Critical Rules

1. **Read-only by default, narrow scaffold exception.** Phases are read-only with one exception: **Phase 2.11** auto-creates empty `.gitkeep`-stubbed *mandatory* template dirs (`reviews/`, `correspondence/editorial/`, `correspondence/referee-reviews/`, `knowledge/`, `to-sort/`), seeds `reviews/INDEX.md` and `knowledge/_index.md` with placeholders, and drops the canonical `.latexmkrc` into every directory containing `*.tex` that lacks one. These are decision-free safe defaults—no content choices are made, no existing files are touched. Every other "fix" action remains flag-only. Per `rules/review-artefact-routing.md`: never auto-create `correspondence/internal-reviews/` (legacy dir, superseded; existing instances handled by `/tidy-project-reviews`).
2. **Detect project type before checking.** Don't flag missing `code/` in theoretical projects.
3. **Distinguish "missing" from "intentionally absent."** Flag but don't alarm.
4. **Check content quality, not just existence.** Empty CLAUDE.md is worth flagging.
5. **Mirror `/init-project-research`.** Phases 2–8 below correspond 1:1 to init's Phases 3–9. When init adds a directory or convention, add the matching audit check here AND update `/atlas-audit` SA1.

---

## Architecture

Ten phases, in order:

1. **Identify Project** — resolve path, detect type, read CLAUDE.md metadata
2. **Scaffold** — common core dirs/files, conditional structure, settings, hooks, rules, LaTeX, GitHub repo, growth patterns *(mirrors init Phase 3)*
3. **Seed Files** — content quality of CLAUDE.md, README.md, MEMORY.md, current-focus.md *(mirrors init Phase 4)*
4. **Overleaf** — paper symlinks, Overleaf separation, sibling paper dirs, backup dirs, LaTeX build config, review correspondence *(mirrors init Phase 5)*
5. **Git** — repo health, branch, untracked files, nested repos, submodules *(mirrors init Phase 6)*
6. **Atlas** — atlas topic cross-reference, outputs drift *(mirrors init Phase 7)*
7. **Task Management Integration** — `_index.md`, `papers/<short>.md`, `current-focus.md` entries *(mirrors init Phase 8)*
8. **Literature & Discovery** — knowledge wiki, literature-review/, review agent outputs *(mirrors init Phase 9)*
9. **Report** — three-severity findings table
10. **Audit Log** — timestamped record to `.claude/audits/`

---

## Phase 1: Identify Project

1. Resolve to absolute path (argument or CWD).
2. Determine project name from basename. **Convention is kebab-case** (matches the atlas slug, e.g. `article40-access-as-mechanism`). Title Case basenames (e.g. `Article 40 Access As Mechanism`) appear in older projects and are also valid — flag neither as a finding. Flag only basenames with non-conforming characters (spaces in kebab-case slugs, mixed-case-with-spaces, punctuation other than hyphens) as Info.
3. Check if git repo: `git -C "<path>" rev-parse --is-inside-work-tree 2>/dev/null`.
4. Detect project type:

   | Indicator | Implies |
   |-----------|---------|
   | `code/` or `data/` | Experimental |
   | `src/` or `tests/` | Computational |
   | Only `paper/`, `docs/`, `log/` | Theoretical |
   | Mix of above | Mixed |

5. Read `CLAUDE.md` if it exists — extract declared metadata (type, venue, authors, slug).
6. Try to find an Atlas topic file matching the project: `find ~/vault/atlas/ -name "<slug>.md"`. If found, note path for Phase 6.

---

## Phase 2: Scaffold

Audits init's Phase 3 outputs. Sub-steps run in order; results aggregate into the Phase 9 report.

### 2.1 Pre-template detection

If no `.context/` AND no `.claude/`, flag as **pre-template project** with consolidated remediation commands. Skip the rest of Phase 2 — this is a structural prerequisite. See [`references/pre-template-detection.md`](references/pre-template-detection.md).

### 2.2 Common core directories

Record present / missing / degraded. Check: `.context/`, `.claude/`, `docs/`, `docs/literature-review/`, `docs/readings/`, `docs/venues/`, `log/`, `paper*/`, `knowledge/` (required), `reviews/` (required, per `rules/review-artefact-routing.md`), `correspondence/referee-reviews/` (required), `correspondence/editorial/` (required), `to-sort/` (required).

**Legacy flag:** `correspondence/internal-reviews/` — if present, flag as `LEGACY` and recommend running `/tidy-project-reviews` to migrate content to `reviews/<source>/` (AI provenance) or `correspondence/internal/` (human provenance) per the routing rule.

### 2.3 Common core files

Check: `CLAUDE.md` (project root, non-empty), `README.md`, `MEMORY.md`, `reviews/INDEX.md` (required, per `rules/review-artefact-routing.md`), `.gitignore` (must include `paper-*/backup/` and `reviews/**/archived/`), `.context/current-focus.md`, `.context/project-recap.md`, `.claude/settings.local.json`.

**Legacy flag:** `REVIEW-STATE.md` at project root — if present, flag as `LEGACY` and recommend running `/tidy-project-reviews` to move it to `reviews/INDEX.md`.

**Dual-file flag (Gap A):** if BOTH `<project>/reviews/INDEX.md` AND `<project>/REVIEW-STATE.md` exist, flag as `DEGRADED` — divergent state. This can happen if the post-Bug-1-fix `review-state-log.sh` (commit `dcbcd9fb`) hit a project where the rename Batch A missed (or where a fresh REVIEW-STATE.md was hand-created after retrofit). Recommend running `/tidy-project-reviews` to merge contents (its Phase 5.2 dedup-merges rows by `(Check, Last Run)` key) and remove REVIEW-STATE.md.

### 2.4 Reviews directory canonicalisation

See [`references/review-consistency.md`](references/review-consistency.md) for canonical registry and legacy-location detection.

### 2.5 Conditional structure (by project type)

**Experimental:** `code/`, `code/python/` or `code/R/`, `data/`, `data/raw/`, `data/processed/`, `output/`, `output/figures/`.  
**Computational:** `src/`, `tests/`, `experiments/`, `results/`, `pyproject.toml`.  
**Python tooling:** flag `requirements.txt` as Degraded.  
**Theoretical:** no additional checks.

### 2.6 Permissions audit (read-only)

Compare `.claude/settings.local.json` `allow` against global `~/.claude/settings.json`. Flag missing as Degraded. See [`references/permissions-sync.md`](references/permissions-sync.md).

### 2.7 Hooks schema validation (read-only)

Every hook entry must use object format `{"type": "command", "command": "..."}`, not bare strings. See [`references/hooks-schema.md`](references/hooks-schema.md).

### 2.8 Rules hygiene (read-only)

Compare project's `.claude/rules/` against global rules. Flag byte-identical duplicates as **Redundant**. See [`references/rules-sync.md`](references/rules-sync.md).

### 2.9 GitHub release repo

Validate structure and hygiene. See [`references/github-release-repo.md`](references/github-release-repo.md).

**Submission-ready projects without an artifact:** flag when atlas `outputs[]` entry is Drafting/Submission-ready/Submitted/R&R and `github-repo/` is absent or vault/atlas lack `artifact_repo:` fields. Recommend `/anonymous-artifact`. Do not auto-fix.

**Skip for theoretical/qualitative projects:** Skip artifact-missing check when (a) Project type detected as Theoretical in Phase 1, (b) No `.py`/`.R`/`.jl`/`.do`/`.ipynb`/`.m` files outside excluded dirs, AND (c) Atlas `methods:` contains only non-computational entries.

### 2.10 Post-init growth patterns

Classify items beyond scaffold as recognised growth or unrecognised (Info). See [`references/growth-patterns.md`](references/growth-patterns.md).

### 2.11 Auto-scaffold mandatory template dirs and files

Create if absent: `reviews/` with `INDEX.md` seeded from the routing-rule template (manifest only — per-source subdirs created lazily), `correspondence/editorial/`, `correspondence/referee-reviews/`, `knowledge/` (with seed `_index.md`), `to-sort/` (with `.gitkeep`), `.latexmkrc` in every dir with `*.tex` (detect via `find -L`). Record in audit log. Never overwrite existing files; flag drift as Degraded.

**Per `rules/review-artefact-routing.md`: do NOT auto-create `correspondence/internal-reviews/`** — that legacy dir is superseded by the human-vs-AI provenance split (`correspondence/internal/` for human collaborator feedback, `reviews/<source>/` for AI output). If it exists in the project, flag as `LEGACY` rather than re-create it.

If `.gitignore` exists and lacks `paper-*/backup/` or `reviews/**/archived/`, flag as `DEGRADED` and suggest adding (don't auto-edit).

---

## Phase 3: Seed Files

Audits init's Phase 4 outputs. Beyond existence — verify meaningful content.

### 3.1 CLAUDE.md content

Must have: Project Overview (title, authors, venue, type), Research Questions (≥1), Setup/Overleaf, Folder Structure, Conventions. Flag placeholder text (`<title>`, `TODO`, `TBD`) and excessive length (>200 lines). Vault sync requires Project Overview fields for metadata extraction.

### 3.2 README.md content

Title, authors, abstract/description, status checklist.

### 3.3 reviews/INDEX.md content

Per `rules/review-artefact-routing.md`, the manifest must have:
- Frontmatter or header naming the project
- `## Latest per source` section (table or list of latest report per source slug)
- `## Open issues` section (aggregated from per-report headers)
- `## Stale sources` section (producers with no report in last 60 days)

If the project still has a legacy `REVIEW-STATE.md` at root instead of `reviews/INDEX.md`, flag as `LEGACY` and direct to `/tidy-project-reviews`.

**Legacy 10-column schema (Gap C).** If `reviews/INDEX.md` exists but its content starts with the legacy 10-column REVIEW-STATE.md table header (`| Paper | Check | Last Run | Verdict | Score | Open Issues | Source | Trigger | Report | Notes |`), flag as `DEGRADED — legacy schema`. This is the Batch A (2026-05-17) retrofit pattern: 278 projects had their REVIEW-STATE.md renamed to reviews/INDEX.md verbatim without translating the content into the "Latest per source" manifest. The legacy schema is functional (rows continue to append correctly via the helper) but doesn't render the way `/review-recap` expects post-2026-05-17. Recommend running `/review-recap` to migrate content; do NOT auto-rewrite (audit is read-only here).

### 3.4 .gitignore content

Must include: `.DS_Store`, `__pycache__/`, `out/`, `paper/` (if Overleaf-managed), `paper-*/backup/` (Overleaf snapshots, per routing rule), `reviews/**/archived/` (archived reports, per routing rule).

### 3.5 .context/current-focus.md content

Should be updated beyond "Project just initialised" if commits exist beyond the initial one.

---

## Phase 4: Overleaf

Audits init's Phase 5 outputs. The nested-pattern paper directory is the cross-cutting concern.

### 4.1 Paper directory convention (nested pattern)

Each `paper*/` must contain a `paper/` symlink → Overleaf with **relative** path (absolute paths break across machines). See [`references/paper-dir-conventions.md`](references/paper-dir-conventions.md).

### 4.2 Overleaf separation

Scan all `paper*/` directories for forbidden file types (code, data, package files). Hard rule — violations are Missing. See [`references/overleaf-separation.md`](references/overleaf-separation.md).

### 4.3 Sibling paper directory check

Detect near-duplicate `paper-*/` dirs and overlapping symlink targets. See [`references/paper-dir-conventions.md`](references/paper-dir-conventions.md).

### 4.4 Backup directory

Each `paper-{venue}/` should contain `backup/` subdirectory. Flag root-level `backup/` as wrong-convention. See [`references/paper-dir-conventions.md`](references/paper-dir-conventions.md).

### 4.5 LaTeX build config

Every dir with `.tex` must have `.latexmkrc` with `$out_dir = 'out'`. **Critical:** use `find -L` to traverse Overleaf symlinks. Auto-scaffolded by Phase 2.11. See [`references/latex-build-config.md`](references/latex-build-config.md).

### 4.6 Review correspondence consistency

Verify `paper-{venue}/correspondence/referee-reviews/` structure. See [`references/review-consistency.md`](references/review-consistency.md).

### 4.7 Talk directory convention

If the project has a talk/deck (a `paper-{venue}/talk/` dir, or a `presentations/` dir, or any `*-talk.tex`/landing page), verify it follows the convention: the `talk/` layout (`{venue}-talk.tex`, `speaker-script.md`, `references.bib`, `.latexmkrc`, `figures/` incl. `qr-{slug}.png`, `out/`), a project-local `links/{slug}/index.html` as source of truth, and the correct folder pattern (archival → `paper-{venue}/talk/`; non-archival/seminar → `presentations/`). Flag deploy-only landing pages (no project copy), a missing `speaker-script.md`, a QR subtitle that over-promises resources the landing page lacks, and a local `paper.pdf` card that should be a DOI link. **Report-only** (these are talk artefacts, not init-scaffolded). See [`references/talk-dir-conventions.md`](references/talk-dir-conventions.md).

---

## Phase 5: Git

Audits init's Phase 6 outputs. If **not** a git repo: flag as Missing (default since Feb 2026). If git repo, check: branch name (`main` or `master`), untracked files, remote status, nested repos (`.git/` subdir → Missing; note: submodules have `.git` as **file**, use `find -mindepth 2 -name .git`), submodule tracking (if `.gitmodules` exists, verify checked out).

---

## Phase 6: Atlas

Audits init's Phase 7 outputs. Skip if no Atlas topic file found in Phase 1. Check drift on slug / status / venue / paper-dir / co-authors fields. See [`references/atlas-checks.md`](references/atlas-checks.md).

---

## Phase 7: Task Management Integration

Audits init's Phase 8 outputs. Verify context library entries: **7.1** index row in `.context/projects/_index.md`; **7.2** paper file at `.context/projects/papers/<short>.md` with valid frontmatter; **7.3** mention in `.context/current-focus.md`. See [`references/task-management-integration.md`](references/task-management-integration.md).

---

## Phase 8: Literature & Discovery

Audits init's Phase 9 outputs.

### 8.1 Knowledge wiki

`knowledge/_index.md` should exist if non-empty. If last updated > 90 days with recent activity, flag Degraded.

### 8.2 Literature review presence

If project status > Idea: expect `*-initial-review.md` or `literature_summary.md`. If any `paper-*/` has `\cite{}`, expect `references.bib`.

### 8.3 Review agent outputs

If `reviews/` exists, verify structure follows the routing rule (`rules/review-artefact-routing.md`):
- Per-source subdirs match the canonical R1 source slug table (`paper-critic/`, `domain-reviewer/`, `referee2-reviewer/`, etc. — NOT variants like `referee2/`, `peer-review/`, `fix/`)
- Files inside each source folder follow `YYYY-MM-DD.md`, `YYYY-MM-DD-HHMM.md` (the timestamp-precision form review agents now write after the 5-agent patch commit `23ebcfff`), OR `YYYY-MM-DD-<descriptor>.md` (manual descriptor form for same-day reruns)
- `reviews/INDEX.md` exists at the `reviews/` root
- No review reports at the project root (`./CRITIC-REPORT.md` and similar are rule violations)
- No content files under `correspondence/internal-reviews/` (legacy)

If any of these checks fail, flag as `DEGRADED` and recommend `/tidy-project-reviews` to retrofit. See [`references/review-agent-outputs.md`](references/review-agent-outputs.md) for the legacy reference (now superseded by the routing rule).

---

## Phase 9: Report

Three severity levels:

| Level | Meaning |
|-------|---------|
| **Missing** | Expected by template, not present |
| **Degraded** | Present but incomplete or has issues |
| **Info** | May be intentional — no action needed unless it bothers you |

Full report format with severity markers and remediation lines: [`references/report-format.md`](references/report-format.md).

---

## Phase 10: Audit Log

After presenting the report, save a timestamped log to `.claude/audits/` in the project:

1. Create `.claude/audits/` if it doesn't exist (this is the only directory the skill creates — it's a self-contained audit trail, not a project-state mutation).
2. Write `YYYY-MM-DD-structure-audit.md` with:
   - Date, project name, detected type
   - Summary table (Missing / Degraded / Info counts with items)
   - Remaining items (not addressable by user via standard skill commands)
3. If an audit log already exists for today, append a suffix: `-2`, `-3`, etc.

Persistent audit trail so future sessions can see what was checked and when.

---

## What This Skill Does NOT Do

- Does not create or fix anything in the project (except writing the audit log to `.claude/audits/` in Phase 10)
- Does not check file content beyond seed files
- Does not compare against other projects (use `/atlas-audit` for that)
- Does not enforce uniformity — identifies unintentional gaps

---

## Cross-References

- `/init-project-research` — the template this skill audits against. **Structural checks here mirror init's scaffold.** When init adds a new directory or convention (e.g., `github-repo/`), add a matching audit check here AND update `/atlas-audit` SA1.
- `/atlas-audit` — batch-audits all projects via SA1. SA1's structure checks must stay consistent with this skill's phases.
- `/sync-permissions` — fixes Phase 2.5 permissions findings.
- `/project-safety` — safety rules and folder guardrails.
- `/update-project-doc` — fixes stale documentation (run after this audit).
- `/compile-knowledge` — fixes Phase 8.1 empty-knowledge-wiki findings.
## Papers-layout checks (2026-07-03, FB directive)

Per rules/submission-file-archive.md § Topic-folder layout, audit:

1. **No stray submission artifacts** outside `paper-<venue>/` — flag any `docs/submission-history/`, `docs/venues/*/submission/`, or root-level as-submitted PDFs.
2. **Archive dirs resolve** — every `files:`/`submitted_files:` pointer in the project's vault submissions + atlas outputs exists on disk under `paper-<venue>/submission/archive/` (or `published/`, `correspondence/`, `talk/`, `presentations/`).
3. **`PAPER-HISTORY.md` freshness** — run `uv run "$(head -1 ~/.config/task-mgmt/path)/scripts/generate-paper-history.py" --project . --check`; report `stale`/`missing` (fix = regenerate, one command).
4. **Filename taxonomy** — archived files follow `{surface}-{stage}[-{role}]` (no exemptions).
