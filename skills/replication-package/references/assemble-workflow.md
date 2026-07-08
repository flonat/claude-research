# Assemble Mode Workflow

> Phases 1-7 for non-blind replication packages. Read when running Assemble mode.

## Phase 1: Scan

1. **Resolve the project path.** Accept as argument or use CWD. Resolve to an absolute path.
2. **Determine the project name** from the directory basename.
3. **Determine the output path:** `<parent>/<project-name>-replication/`. If it already exists, ask the user whether to overwrite or choose a different name.
4. **Scan for AI traces and replication requirements.** Search the project for:

| Category | What to look for |
|----------|-----------------|
| **Directories** | `.claude/`, `.context/`, `log/`, `packages/mcp-desktop/`, `packages/scholarly/`, `.scripts/`, `hooks/` |
| **Files** | `CLAUDE.md`, `MEMORY.md`, `*.jsonl`, `.env` |
| **Skill/agent infra** | `skills/` directory (only if it contains SKILL.md files — i.e., Claude skill infrastructure, not project code) |
| **Git trailers** | `Co-Authored-By:` lines mentioning Claude, Anthropic, or AI assistants |
| **Text markers** | "Generated with Claude Code", "Generated with Claude", "Claude Code" attribution lines in files |
| **Gitignore entries** | Lines in `.gitignore` referencing `.claude/`, `CLAUDE.md`, `.context/`, `log/`, `.mcp-server*` |
| **Scripts** | `.py`, `.R`, `.sh`, `.jl`, `.m` files — catalogue for execution order |
| **Data files** | Contents of `data/raw/`, `data/processed/`, `data/` — catalogue for provenance |
| **Dependencies** | `requirements.txt`, `pyproject.toml`, `renv.lock`, `DESCRIPTION`, `Makefile`, `Dockerfile` |
| **Outputs** | `output/`, `results/`, `out/`, `paper/figures/` — check freshness vs. source scripts |

5. **Present the dry-run report** to the user:

```
Replication Package — Dry Run (Assemble)
=========================================
Project:  <project-name>
Output:   <output-path>

AI Traces to Remove:
  Directories:  N (list)
  Files:        N (list)
  Git trailers: N commits contain Co-Authored-By AI lines
  Text markers: N files contain Claude attribution lines
  Gitignore:    N lines to clean

Replication Assets Detected:
  Scripts:      N files (list with execution order if determinable)
  Data files:   N files (XX MB)
  Dependencies: (list dependency files found)
  Outputs:      N files (list with freshness vs. source)

Binary files (manual check recommended): N files

Missing for Replication:
  [ ] No README with replication instructions
  [ ] No dependency manifest
  [ ] ...
```

6. **Ask the user to confirm** before proceeding. If denied, stop.

---

## Phase 2: Copy

1. **Create the output directory:**
   ```bash
   mkdir -p "<output-path>"
   ```

2. **Copy the project with symlink resolution:**
   ```bash
   rsync -aL --exclude='.git/' "<project-path>/" "<output-path>/"
   ```
   - `-a` preserves permissions and timestamps
   - `-L` resolves symlinks into real files
   - `--exclude='.git/'` skips git history (we create a fresh repo in Phase 6)

3. **Verify the copy** by comparing file counts:
   ```bash
   find "<project-path>" -not -path '*/.git/*' -type f | wc -l
   find "<output-path>" -type f | wc -l
   ```

---

## Phase 3: Scrub AI Traces

All operations target the **output directory only**. Never touch the original.

### 3a — Remove directories

Remove these directories if they exist in the output:

```
.claude/
.context/
log/
packages/mcp-desktop/
packages/scholarly/
.scripts/
hooks/
```

For `skills/` — only remove if it contains `SKILL.md` files (Claude skill infrastructure). If `skills/` contains project code (e.g., Python modules), leave it alone and warn the user.

### 3b — Remove files

Remove these files/patterns from the output:

```
CLAUDE.md
MEMORY.md
*.jsonl
.env
```

### 3c — Scrub text content

In all text files (`.tex`, `.md`, `.txt`, `.py`, `.R`, `.r`, `.sh`, `.yaml`, `.yml`, `.toml`, `.cfg`, `.ini`, `.bib`, `.cls`, `.sty`, `.Rmd`, `.qmd`, `.html`, `.css`, `.js`, `.ts`, `.json`, `.csv`):

1. **Remove Co-Authored-By AI lines.** Delete any line matching:
   ```
   Co-Authored-By:.*[Cc]laude.*
   Co-Authored-By:.*[Aa]nthropic.*
   Co-Authored-By:.*noreply@anthropic\.com.*
   ```

2. **Remove Claude attribution markers.** Delete any line matching:
   ```
   Generated with \[?Claude Code\]?.*
   Generated with Claude.*
   🤖 Generated with.*Claude.*
   ```

3. **Clean trailing blank lines** left behind by removals — collapse multiple consecutive blank lines into at most two.

### 3d — Clean .gitignore

If `.gitignore` exists in the output, remove lines that reference Claude infrastructure:
- Lines containing `.claude/`, `.claude`, `CLAUDE.md`, `.context/`, `log/`, `.mcp-server`, `.scripts/`, `hooks/`, `*.jsonl`, `MEMORY.md`

Remove any resulting blank lines at the end of the file. If `.gitignore` becomes empty, delete it.

---

## Phase 4: Generate Replication README

Generate an AEA-style data and code availability README from [`aea-readme-template.md`](aea-readme-template.md).

1. **Read the template** and populate each section using information gathered in Phase 1.
2. **Overview:** Project title, authors (from git config or LaTeX), brief description.
3. **Data Availability:** List all data files with provenance (original source, access conditions, license). Flag any restricted-use data. If data is not included, explain where to obtain it.
4. **Computational Requirements:** Software, packages, hardware. Extract from dependency files. Estimate runtime if scripts are documented.
5. **Description of Programs:** List all scripts in execution order. For each: filename, purpose, inputs, outputs.
6. **Instructions to Replicators:** Step-by-step from a clean machine to reproduced results.
7. **List of Tables and Figures:** Map each table/figure in the paper to the script that produces it.
8. **References:** Data source citations.
9. **Append the Figure/Table Crosswalk + Paper-Consistency check** from [`figure-table-crosswalk.md`](figure-table-crosswalk.md): one entry per manuscript & appendix figure/table (Output · Script · Log · **LaTeX Label** · Notes) in paper order, plus the paper-source consistency check (every cited figure/table + in-text number traces to an output). The AEA body documents *programs*; this maps *paper artefacts* — both are required.

Write the completed README to `<output-path>/README.md` (overwriting any existing README — the original is safe in the source project).

---

## Phase 5: Verify Reproducibility

1. **Script execution order.** If a `Makefile`, `run_all.sh`, or numbered scripts exist, verify the declared order matches file dependencies. If no execution order is documented, infer one and flag for user confirmation.
2. **Output freshness.** Compare modification times of output files vs. their source scripts. Flag outputs older than their generating scripts (stale).
3. **Data provenance.** Check that every data file in `data/` is documented in the README. Flag undocumented data files.
4. **Dependency manifest.** Verify that a dependency file exists (`requirements.txt`, `pyproject.toml`, `renv.lock`, etc.). If missing, generate one from import statements using conventions from `shared/multi-language-conventions.md`.
5. **Per-script logging + session info.** Verify every public script writes a `logs/<script>.log`, a `session_info.log` exists from a real full run, and a master script runs everything in order + records elapsed time. If the source project lacks this, offer the language-appropriate skeleton from [`logging-skeletons.md`](logging-skeletons.md) (R/Python/Julia/Stata) — don't force it if the project already logs cleanly.

---

## Phase 6: Fresh Git Repository

1. **Initialize a fresh repo:**
   ```bash
   cd "<output-path>" && git init
   ```

2. **Determine the user's real identity** from git config:
   ```bash
   git config --global user.name
   git config --global user.email
   ```

3. **Stage and commit everything:**
   ```bash
   cd "<output-path>" && git add -A && git commit -m "Initial commit: replication package"
   ```
   This uses the user's real name and email — no AI trailers.

4. **Verify the commit** has no AI traces:
   ```bash
   cd "<output-path>" && git log --format=full
   ```

5. **Dropbox-synced projects:** if the source project syncs via Dropbox, copy [`rules.dropboxignore`](rules.dropboxignore) to the package root (complements `.gitignore` — keeps `.Rproj.user/`, `__pycache__/`, `.DS_Store`, and caches out of the synced package). Keep the package a *sibling* of any Overleaf folder, never nested inside it.

---

## Phase 7: Report

Present a comprehensive summary:

```
Replication Package — Complete (Assemble)
==========================================
Project:     <project-name>
Output:      <output-path>
Status:      Assembled

AI Traces Removed:
  Directories:  N removed
  Files:        N removed
  Text scrubs:  N lines across M files
  Gitignore:    N lines cleaned

Replication Assets:
  README:       Generated (AEA-style)
  Scripts:      N files, execution order documented
  Data:         N files (XX MB), provenance documented
  Dependencies: <manifest-file> present
  Outputs:      N files (XX MB)

Size comparison:
  Original:  XX MB
  Package:   XX MB

Verification:
  "claude" in text files:     0 matches
  "anthropic" in text files:  0 matches
  "Co-Authored-By" in files:  0 matches
  AI trailers in git log:     0

Manual checks recommended:
  - Binary files (PDFs, images) may contain embedded metadata
  - Verify script execution order produces expected outputs
  - Test on a clean machine if possible
```

Run the verification grep across all text files in the output. If any matches remain, list them with file and line number, and ask the user whether they are false positives or need manual fixing.

**Also emit the release-readiness checklist** to `<output-path>/RELEASE-READINESS.md` — the 14-point PASS/FAIL gate from [`release-readiness-checklist.md`](release-readiness-checklist.md) (fresh-session run, relative paths, per-script logs, `session_info.log`, crosswalk completeness, in-text numbers trace, restricted-data docs, stable filenames, no AI traces). **Any FAIL is a release blocker** until fixed or explicitly waived (record the waiver reason).
