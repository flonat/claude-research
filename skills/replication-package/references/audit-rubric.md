# Audit Rubric — 11-Check Reproducibility Scoring

> Scoring rubric for `/replication-package` Audit mode. Each check gets Pass, Partial, or Fail. The overall score is the count of passes.

---

## Scoring

| Score | Verdict | Action |
|-------|---------|--------|
| **8-10 passes** | Publishable | Ready to deposit. Minor issues (Partial) can be noted but are not blocking. |
| **5-7 passes** | Needs work | Address Fail items before deposit. Partial items should be improved. |
| **<5 passes** | Not ready | Significant gaps. Return to Assemble mode to rebuild. |

N/A checks are excluded from the denominator (e.g., if no LaTeX files exist, Check 1 is N/A and the score is out of 9). Check 11 (Numeric Reproduction) is N/A by default — it scores only when an `expected_values.json` is present at the package root — so the default denominator is unchanged from the original 10.

---

## The 11 Checks

### Check 1: Compilation

Does the package compile?

| Result | Criteria |
|--------|----------|
| **Pass** | LaTeX compiles without errors. All outputs generate correctly. |
| **Partial** | Compiles with warnings but produces correct output. Minor font/package warnings acceptable. |
| **Fail** | Does not compile. Missing packages, broken references, or fatal errors. |
| **N/A** | No LaTeX files in the package. |

**How to test:** Run `latexmk -pdf` (or invoke `/latex` in check-only mode) on the main `.tex` file.

---

### Check 2: Script Execution Order

Can scripts be run in an unambiguous order?

| Result | Criteria |
|--------|----------|
| **Pass** | Scripts are numbered (01_, 02_, ...), documented in README, or orchestrated by Makefile/run_all.sh. Order is unambiguous. |
| **Partial** | Order is determinable from file names or README but not explicitly stated. Or Makefile exists but is incomplete. |
| **Fail** | No ordering scheme. Scripts have arbitrary names. README does not document execution sequence. |
| **N/A** | No scripts in the package (pure LaTeX/theory paper). |

**How to test:** Read README and check for numbered scripts, Makefile, or run_all.sh. Verify that declared order matches file dependencies (outputs of script N are inputs to script N+1).

---

### Check 3: Output Presence

Are declared output files actually present?

| Result | Criteria |
|--------|----------|
| **Pass** | Every table and figure referenced in the README (or paper) has a corresponding file in the package. |
| **Partial** | Most outputs present but some are missing. Or outputs exist but in unexpected locations. |
| **Fail** | Multiple declared outputs are missing. Or no outputs are present at all. |

**How to test:** Cross-reference the README's "List of Tables and Figures" against the file tree. Check that `\input{}` and `\includegraphics{}` targets in `.tex` files exist.

---

### Check 4: Dependencies Declared

Is there a dependency manifest with pinned versions?

| Result | Criteria |
|--------|----------|
| **Pass** | Dependency file exists (`requirements.txt`, `pyproject.toml`, `renv.lock`, etc.) with pinned version numbers. All imports in scripts are covered. |
| **Partial** | Dependency file exists but versions are not pinned. Or file exists but some imports are missing from it. |
| **Fail** | No dependency manifest. Replicators would have to guess what to install. |

**How to test:** Check for dependency files. Parse import statements in scripts and verify they appear in the manifest. Check for version pins (e.g., `numpy==1.24.3` not just `numpy`).

---

### Check 5: Data Provenance

Is every data file documented with its source?

| Result | Criteria |
|--------|----------|
| **Pass** | Every file in `data/` is listed in the README with source, access method, and license. Restricted data has clear instructions for obtaining access. |
| **Partial** | Most data files documented but some lack source information. Or provenance is vague ("downloaded from the internet"). |
| **Fail** | Data files present with no documentation. Or README claims data is included but files are missing. |

**How to test:** List all files in `data/` (or equivalent). Check each against the README's Data Availability section. Verify that restricted data has access instructions.

---

### Check 6: README Present

Does a README exist with replication instructions?

| Result | Criteria |
|--------|----------|
| **Pass** | README exists, follows AEA-style structure (or equivalent), contains all sections: overview, data, requirements, scripts, instructions, outputs. |
| **Partial** | README exists but is incomplete (missing sections, sparse instructions). Or is a generic project README without replication focus. |
| **Fail** | No README. Or README contains only a project title with no substantive content. |

**How to test:** Check for `README.md`, `README`, `README.txt`. Evaluate against the AEA template sections. Use [`deposit-checklist.md`](deposit-checklist.md) for completeness.

---

### Check 7: File Sizes

Are file sizes reasonable for the deposit platform?

| Result | Criteria |
|--------|----------|
| **Pass** | No file exceeds 100 MB. Total package under 5 GB. No suspiciously empty directories. No unnecessary large files (e.g., `.git/`, compiled binaries, cached data). |
| **Partial** | Some files exceed 100 MB but are justified (large datasets). Total package within platform limits. |
| **Fail** | Files exceed platform limits. Or package contains unnecessary large files (build artifacts, cached downloads, `.git/` directory). |

**How to test:** Run `du -sh` on the package and `find . -size +100M`. Check for `.git/`, `__pycache__/`, `node_modules/`, `.venv/`, `out/` (LaTeX build artifacts).

---

### Check 8: End-to-End Clarity

Could someone unfamiliar reproduce results from the README alone?

| Result | Criteria |
|--------|----------|
| **Pass** | A competent researcher in the field could reproduce all results by following the README step-by-step, without consulting any other documentation or contacting the authors. |
| **Partial** | Most steps are clear but some require domain knowledge not documented. Or instructions assume specific OS/environment without stating it. |
| **Fail** | Instructions are too vague, incomplete, or assume significant undocumented knowledge. Key steps are missing (e.g., "run the analysis" without specifying which script). |

**How to test:** Read the README as if you know nothing about the project. Can you determine: what to install, where to get data, which scripts to run, in what order, and how to verify success? Flag any ambiguities.

---

### Check 9: AI Traces

Are there lingering AI/Claude artifacts?

| Result | Criteria |
|--------|----------|
| **Pass** | No `.claude/`, `CLAUDE.md`, `MEMORY.md`, `.context/`, Co-Authored-By AI trailers, or Claude attribution markers found anywhere in the package. |
| **Partial** | Minor traces found (e.g., a single comment mentioning Claude in a script) that don't affect replication. |
| **Fail** | AI infrastructure directories or files present. Or multiple AI attribution markers in code/text. |

**How to test:** Search for:
- Directories: `.claude/`, `.context/`, `log/`, `.mcp-server*/`, `.scripts/`, `hooks/`
- Files: `CLAUDE.md`, `MEMORY.md`, `*.jsonl`
- Text: `Co-Authored-By:.*[Cc]laude`, `Generated with.*Claude`, `anthropic`, `claude` (case-insensitive, review context for false positives like "Claude Shannon")

---

### Check 10: Identity Leaks (Blind Packages Only)

Are there any remaining identity traces?

| Result | Criteria |
|--------|----------|
| **Pass** | No author names, emails, institutional affiliations, ORCID, or personal paths found. Git history shows "Anonymous" only. |
| **Partial** | Minor traces found in non-obvious locations (e.g., a comment deep in a script). Main paper and README are clean. |
| **Fail** | Author identity discoverable from the package (name in LaTeX, email in metadata, institution in README, personal paths in scripts). |
| **N/A** | Package is not intended for double-blind review. |

**How to test:** Build identity list from git config and any LaTeX `\author{}` blocks. Search entire package for every identity item (case-insensitive). Check git log for author/committer identity. Check PDF Document Properties if a compiled PDF is included.

---

### Check 11: Numeric Reproduction (only when `expected_values.json` present)

Do the package's committed output files match the manuscript's reported numbers, within tolerance?

| Result | Criteria |
|--------|----------|
| **Pass** | Every scored target ≥ 90/100 — all reported coefficients, SEs, N, and figure data reproduce within the declared tolerances. |
| **Partial** | Most targets ≥ 90; each remaining near-miss has a documented root cause (e.g. data-vintage difference, rounding). |
| **Fail** | One or more targets disagree beyond tolerance with no explanation, OR `expected_values.json` references output files the package does not contain. |
| **N/A** | No `expected_values.json` at package root (default). |

**Scope:** read-only. This check **parses the package's already-committed outputs** (the same files Check 3 cross-references) and compares them to the external ground truth in `expected_values.json`. It does **not** re-run scripts (per the skill's standing rule) — it catches paper-vs-output drift, not full fresh-run reproduction.

**How to test:** Read `expected_values.json`; for each target, parse its `source_file` and compute a 0–100 score per the rubric in [`expected-values-schema.md`](expected-values-schema.md) (regression: coeffs 30 / SEs 20 / N 15 / vars 10 / loglik 10 / pseudo-R² 15; figure: type 15 / data 40 / axes 15 / visual 15 / layout 15). For every target below 90, name a root cause, not just the gap. Surface the per-target scores in the report's detail block.

---

## Report Format

```
Replication Package — Audit Report
====================================
Package:  <package-path>
Date:     YYYY-MM-DD

Results:
   1. Compilation:        [Pass | Partial | Fail | N/A]  — [brief note]
   2. Script order:       [Pass | Partial | Fail | N/A]  — [brief note]
   3. Output presence:    [Pass | Partial | Fail]        — [brief note]
   4. Dependencies:       [Pass | Partial | Fail]        — [brief note]
   5. Data provenance:    [Pass | Partial | Fail]        — [brief note]
   6. README:             [Pass | Partial | Fail]        — [brief note]
   7. File sizes:         [Pass | Partial | Fail]        — [brief note]
   8. End-to-end clarity: [Pass | Partial | Fail]        — [brief note]
   9. AI traces:          [Pass | Partial | Fail]        — [brief note]
  10. Identity leaks:     [Pass | Partial | Fail | N/A]  — [brief note]
  11. Numeric reproduction:[Pass | Partial | Fail | N/A] — [e.g. "3/3 tables within tol; Fig 4 89.8/100"]

Score: X/Y passes (Y = 11 minus N/A count)

Verdict: [Publishable | Needs work | Not ready]

Detailed Findings:
  [For each Partial or Fail, explain what was found and how to fix it]

Reproduction scoring (only if Check 11 scored):
  [Per-target 0-100 score + named root cause for any target < 90]

Underspecified in the manuscript (optional):
  [Methodology the paper omits — weighting, IV details, coding conventions —
   that forced a judgment call during reproduction]

Recommendations (prioritized):
  1. [Most critical fix]
  2. [Next most critical]
  ...
```
