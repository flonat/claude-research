# Quality Rubric: LaTeX Auto-Fix

> Scoring rubric for `/latex-autofix`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Compilation fails after 5 fix iterations | -100 | No PDF produced |
| PDF produced but with fatal rendering errors (blank pages, missing content) | -100 | Output is unusable |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Unresolved `\cite{}` — `??` or `[?]` in output | -15 | Per unique broken citation key |
| Unresolved `\ref{}` — `??` in output | -15 | Per unique broken reference |
| Auto-fix changed user intent (e.g., wrong citation key substituted) | -25 | Per instance — silent corruption |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Overfull hbox > 10pt remaining | -5 | Per instance |
| Missing `.latexmkrc` or incorrect `$out_dir` config | -10 | Build hygiene failure |
| Stale auxiliary files causing warnings | -5 | Should have been caught by cache clean |
| Package added but not strictly necessary | -5 | Per unnecessary package |
| Cited keys in `.tex` not found in `.bib` (audit) | -8 | Per missing key |
| Unused keys in `.bib` (audit, >20% unused) | -5 | Once for the pattern |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Overfull hbox 1-10pt | -2 | Per instance |
| Underfull hbox/vbox warnings | -1 | Per instance |
| Font substitution warnings | -2 | Per unique substitution |
| Multiple compilation iterations needed (>2) | -1 | Per extra iteration beyond 2 |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Pre-flight config | Phase 1 |
| Compilation errors | Phase 2 |
| Auto-fix quality | Phase 2 (fix accuracy) |
| Remaining warnings | Phase 3 |
| Citation audit | Phase 4 |
