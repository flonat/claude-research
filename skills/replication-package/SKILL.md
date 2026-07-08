---
name: replication-package
description: "Use when you need to assemble, anonymize, or audit a replication package."
allowed-tools: Bash(cp*), Bash(rm*), Bash(mkdir*), Bash(ls*), Bash(git*), Bash(find*), Bash(sed*), Bash(grep*), Bash(du*), Bash(wc*), Bash(dirname*), Bash(basename*), Bash(readlink*), Bash(rsync*), Bash(mv*), Read, Write, Edit, Glob, Grep, AskUserQuestion, Skill
argument-hint: "[project-path] [--mode assemble|blind|audit]"
---

# Replication Package — Assemble, Anonymize, and Audit

> Build publication-ready replication packages, optionally anonymize for double-blind review, or audit an existing package for reproducibility. The original project is never modified.

## Modes

| Mode | What it does | Use case |
|------|-------------|----------|
| **Assemble** | Clean copy + AI trace removal + AEA-style README | Sharing, Zenodo deposit, journal supplementary |
| **Blind** | Everything in Assemble + identity anonymization | Double-blind conference/journal submission |
| **Audit** | Read-only 11-check reproducibility validation | Pre-deposit quality gate, self-check |

**Default mode:** Assemble. Infer Blind if the user says "anonymize", "double-blind", or "blind review". Infer Audit if the user says "audit", "check reproducibility", or "validate package".

## When to Use

- Submitting supplementary materials or replication files to a journal
- Depositing a package on Zenodo, Dataverse, or ICPSR
- Sharing a project repo publicly (GitHub, institutional repository)
- Preparing for double-blind submission (Blind mode)
- Self-checking reproducibility before deposit (Audit mode)

## When NOT to Use

- Quick one-off cleanup of a single file — do it manually
- Removing a single AI artifact — just delete it directly
- Projects with no empirical or computational component

---

## Critical Rules

1. **Never modify the original project.** All work happens on a copy in a sibling folder.
2. **Dry-run mandatory.** Always show what will be removed/changed and get user confirmation before any deletions.
3. **Binary files are never modified.** Warn the user to manually check PDFs (Document Properties), images (EXIF data), and datasets for embedded metadata.
4. **Self-citations are always interactive.** Never auto-remove or auto-anonymize a citation. Flag each potential self-citation and let the user decide per citation. **In Blind mode, surface every self-citation against the loaded submission author list and require a per-citation decision (third-person OK / blind the entry).** When the cited paper's author list is a subset of the submission's, third-person is structurally insufficient and the bib entry MUST be blinded — see `_shared/double-blind-anonymity-checklist.md` §P4–P5.
5. **Resolve symlinks.** Use `rsync -aL` so symlinked content (e.g., Overleaf `paper/` symlinks) becomes real files in the copy.
6. **Preserve compilability.** The output must still compile/run — only infrastructure and identity are removed, not project functionality.
7. **Blind mode runs the structured-metadata field check (A2) before reporting clean.** `pyproject.toml` `[project] authors`, `package.json` `author`/`contributors`, `Cargo.toml` `[package] authors`, `CITATION.cff`, `LICENSE` holder, etc. — see `_shared/double-blind-anonymity-checklist.md` §"Structured-metadata field check (A2)" for the full target list. This was the CCS 2026 #1328 desk-reject trigger and is now non-skippable.

---

## Assemble Mode (Non-Blind)

Phases 1-7: Scan → Copy → Scrub AI Traces → Generate README → Verify → Fresh Git → Report.

Full workflow: [`references/assemble-workflow.md`](references/assemble-workflow.md)

---

## Blind Mode (Assemble + Anonymization)

Runs all Assemble phases, then continues with Phases 8-12: Collect Identity → Anonymize LaTeX → Anonymize Other Files → Anonymous Git → Leak Check Report.

Full workflow: [`references/blind-workflow.md`](references/blind-workflow.md)

---

## Audit Mode (Read-Only)

11-check reproducibility validation: Compilation, Script order, Output presence, Dependencies, Data provenance, README, File sizes, End-to-end clarity, AI traces, Identity leaks, Numeric reproduction.

Full workflow: [`references/audit-workflow.md`](references/audit-workflow.md)

**Check 11 (Numeric reproduction)** is N/A unless an `expected_values.json` (the manuscript's reported numbers) sits at the package root. When present, the audit parses the package's **committed output files** and scores them against that ground truth within tolerance — catching paper-vs-output drift. It is read-only and never re-runs scripts. Convention + scoring rubric: [`references/expected-values-schema.md`](references/expected-values-schema.md).

### HPC-run results

If the project used [HPC cluster] (`hpc/` directory with `*.sbatch`), the results in `out/<jobid>/` should include `git-sha.txt` + `git-status.txt` (written by the sbatch templates before `srun`). Audit must verify these exist and the SHA matches a commit in the repo — this is the compute-reproducibility equivalent of Script order + Dependencies for HPC runs. The Assemble README should document the `hpc/` entry point and the HF/conda env-setup script alongside `code/` + `data/`. See Task Management [`docs/guides/hpc.md`](../../docs/guides/hpc.md).

---

## What This Skill Does NOT Do

- **Does not modify the original project** — all changes are in the sibling folder (Assemble/Blind) or purely read-only (Audit).
- **Does not modify binary files** — PDFs, images, datasets are copied as-is. User must check these manually for embedded metadata.
- **Does not auto-handle self-citations** — every potential self-citation requires user decision.
- **Does not anonymize the paper title** — titles are generally not considered identifying (but some venues disagree; user should check).
- **Does not strip PDF metadata** — if a compiled PDF exists, its Document Properties may contain author info. User should recompile from the anonymized source or use `exiftool` to strip metadata.
- **Does not run scripts** — it verifies their presence and order but does not execute them (too risky without a controlled environment). Check 11 (Numeric reproduction) likewise compares the package's *already-committed* output files against the manuscript; it never re-runs the pipeline, so it catches paper-vs-output drift, not full fresh-run reproduction.

---

## Examples

### Assemble mode (default)

> "Build a replication package for my research paper"

Runs Assemble mode on the current project, creates `../mcdm-paper-replication/`.

### Blind mode

> "Anonymize my paper for AAAI double-blind submission"

Runs Blind mode, creates `../mcdm-paper-replication-blind/`.

### Audit mode

> "Audit the reproducibility of my replication package"

Runs Audit mode (read-only) on the specified package directory.

### Explicit path and mode

> "/replication-package ~/papers/negotiation-model --mode blind"

Runs Blind mode on the specified project path.

---

## Cross-References

- **`data-sensitivity` rule** — raw data is read-only; replication packages must document data provenance without modifying `data/raw/`
- **`overleaf-separation` rule** — `paper/` structure is preserved; symlinks resolved by rsync
- **`shared/multi-language-conventions.md`** — dependency detection patterns for Python, R, Julia, MATLAB
- **`shared/publication-output.md`** — output file verification and freshness checks
- **`/latex`** — compilation check in Audit mode
- **`references/aea-readme-template.md`** — AEA-style README template for Assemble mode
- **`references/figure-table-crosswalk.md`** — per-figure/table crosswalk (with LaTeX Label) + paper-consistency check, appended to the README (Phase 4)
- **`references/logging-skeletons.md`** — per-script logging + master-script skeletons (R/Python/Julia/Stata) offered in Phase 5
- **`references/release-readiness-checklist.md`** — 14-point PASS/FAIL pre-release gate emitted at Phase 7 (`RELEASE-READINESS.md`)
- **`references/rules.dropboxignore`** — Dropbox-sync ignore file for Dropbox-synced packages (Phase 6)
- **`references/anonymization-patterns.md`** — replacement tables for Blind mode
- **`references/audit-rubric.md`** — 11-check scoring rubric for Audit mode
- **`references/expected-values-schema.md`** — `expected_values.json` convention + numeric-reproduction scoring rubric (Check 11)
- **`references/deposit-checklist.md`** — platform-specific deposit completeness checklist
- **`references/report-template.md`** — report format for Blind mode
- **`_shared/double-blind-anonymity-checklist.md`** — authoritative paper+artifact anonymity matrix (P1–P8, A1–A9). Blind mode must run all artifact-side checks (A1–A9) before reporting clean.

---

> **Note:** This skill replaces the former `/export-project-clean` and `/export-project-anon` skills. All their functionality is preserved in Assemble and Blind modes respectively.

---

## Output Verification (Guard)

This skill writes files. Before any auto-commit, emit an outputs manifest and run the shared verifier. See [`skills/_shared/verify-outputs.md`](../_shared/verify-outputs.md) for the full protocol.

**Required tail steps** (before `git commit`):

1. Write manifest to `<project>/.claude/state/outputs-manifest-<UTC-timestamp>.json` listing every file this skill claims to have written in this invocation (paths relative to the project root).
2. Run:

   ```bash
   python3 "$HOME/.claude/skills/_shared/verify_outputs.py" \
       --manifest "$MANIFEST" \
       --project-root "$PROJECT_ROOT"
   ```

3. If the verifier exits non-zero, **do not commit** — surface the missing-files list to the user and stop. The verifier has already logged an `error` entry to `~/.claude/ecc/skill-outcomes.jsonl`, which feeds the launcher dashboard.

**Why:** closes the "hallucinated outputs" failure class (commit `b2cff75`, 2026-04-18).
