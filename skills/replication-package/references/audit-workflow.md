# Audit Mode Workflow

> Read-only 11-check reproducibility validation. Read when running Audit mode.

Audit mode performs a **read-only** 11-check reproducibility validation on an existing package. It does not copy, modify, or delete anything.

Accept the path to the package directory (not the source project). If no path is given, use CWD.

## The 11 Checks

Scoring rubric with Pass/Partial/Fail criteria: [`audit-rubric.md`](audit-rubric.md)
Deposit completeness checklist: [`deposit-checklist.md`](deposit-checklist.md)
Numeric-reproduction ground-truth convention: [`expected-values-schema.md`](expected-values-schema.md)

1. **Compilation.** If LaTeX files exist, do they compile? Invoke `/latex` in check-only mode or run `latexmk -outdir=out -pdf` and report success/failure.
2. **Script execution order.** Are scripts numbered, documented in a README, or orchestrated by a Makefile/run_all.sh? Can the order be determined unambiguously?
3. **Output presence.** Are declared output files (tables, figures) actually present in the package? Cross-reference the README's table/figure list against the file tree.
4. **Dependencies declared.** Does a dependency manifest exist (`requirements.txt`, `pyproject.toml`, `renv.lock`, etc.)? Are version numbers pinned?
5. **Data provenance.** Is every data file documented? Are sources cited? Are access conditions stated for restricted data?
6. **README present.** Does a README exist? Does it follow AEA or equivalent structure? Does it contain replication instructions?
7. **File sizes.** Are all files reasonably sized? Flag anything over 100 MB. Flag suspiciously empty directories.
8. **End-to-end clarity.** Could someone unfamiliar with the project reproduce results from the README alone? Assess completeness of instructions.
9. **AI traces.** Scan for lingering `.claude/`, `CLAUDE.md`, `MEMORY.md`, `.context/`, Co-Authored-By AI trailers, Claude attribution markers.
10. **Identity leaks.** (Blind packages only) Scan for author names, emails, institutions, ORCID. Use git config and LaTeX `\author{}` as reference if available.
11. **Numeric reproduction.** (Only if `expected_values.json` exists at the package root.) Parse each declared output file and score it against the manuscript's reported numbers within tolerance (see [`expected-values-schema.md`](expected-values-schema.md)). Read-only — does **not** re-run scripts; verifies the committed outputs match the paper, catching paper-vs-output drift. N/A when no `expected_values.json` is present.

## Audit Report

```
Replication Package — Audit Report
====================================
Package:  <package-path>
Date:     YYYY-MM-DD

Results:
  1. Compilation:        [Pass | Partial | Fail | N/A]
  2. Script order:       [Pass | Partial | Fail | N/A]
  3. Output presence:    [Pass | Partial | Fail]
  4. Dependencies:       [Pass | Partial | Fail]
  5. Data provenance:    [Pass | Partial | Fail]
  6. README:             [Pass | Partial | Fail]
  7. File sizes:         [Pass | Partial | Fail]
  8. End-to-end clarity: [Pass | Partial | Fail]
  9. AI traces:          [Pass | Partial | Fail]
  10. Identity leaks:    [Pass | Partial | Fail | N/A]
  11. Numeric reproduction:[Pass | Partial | Fail | N/A]

Score: X/Y (Y = 11 minus N/A count; default Y is 9-10, since check 11 is N/A
            without expected_values.json)

Verdict (proportional — passes / scored checks):
  ≥ 80%  →  Publishable
  50-79% →  Needs work (issues listed below)
  < 50%  →  Not ready (major issues listed below)

Issues:
  [Detailed findings for each Partial/Fail check]

Reproduction scoring (only if Check 11 scored):
  [Per-target 0-100 + named root cause for any target < 90]

Underspecified in the manuscript (optional):
  [Methodology the paper omits that forced a judgment call]

Recommendations:
  [Prioritized list of fixes]
```
