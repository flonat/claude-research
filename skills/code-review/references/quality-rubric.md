# Quality Rubric: Code Review

> Scoring rubric for `/code-review`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Syntax error preventing script from running | -100 | Script is broken |
| Missing critical dependency with no install instructions | -100 | Cannot reproduce without guessing |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Numerical project missing cross-language replication scripts | -20 | Once per project — no independent verification of results |
| Hardcoded absolute path (`/Users/...`, `C:\...`) | -20 | Per unique path — breaks on any other machine |
| Domain correctness bug (wrong estimator, wrong sample restriction) | -20 | Per instance — produces wrong results |
| No random seed before stochastic operation | -15 | Per stochastic block — results not reproducible |
| `setwd()` / `os.chdir()` in script | -15 | Breaks portability |
| Weights applied incorrectly or not summing to expected value | -15 | Domain error |
| Standard errors don't match paper specification | -15 | Domain error |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| No script header (purpose, author, date, I/O) | -10 | Per script |
| No environment documentation (renv.lock, requirements.txt) | -10 | Once per project |
| Expensive computation not cached | -8 | Per operation |
| Function without documentation | -5 | Per function |
| Stray print/cat pollution | -5 | Per script with pollution |
| Script > 500 lines without splits | -5 | Per script |
| Loaded but unused package | -5 | Per package |
| Figures not saved to file (only displayed) | -5 | Per figure |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Non-descriptive function name (`f1`, `do_stuff`) | -3 | Per function |
| Missing type hints (Python) | -3 | Once per script, not per function |
| `=` instead of `<-` for assignment (R) | -2 | Once for the pattern |
| Mixed pipe styles (`%>%` and `|>`) | -2 | Once for the pattern |
| `T`/`F` instead of `TRUE`/`FALSE` (R) | -2 | Once for the pattern |
| Default figure dimensions (not explicitly set) | -2 | Per figure |
| Non-colourblind-friendly palette | -2 | Per figure |
| Final output in non-portable format (`.RData` only) | -3 | Per output |
| Missing session info at end of script | -1 | Per script |

## Category Mapping

| Rubric category | SKILL.md check category |
|----------------|------------------------|
| Reproducibility | Category 1 |
| Script structure | Category 2 |
| Output hygiene | Category 3 |
| Function quality | Category 4 |
| Domain correctness | Category 5 |
| Figure quality | Category 6 |
| Data persistence | Category 7 |
| Dependencies | Category 8 |
| Python-specific | Category 9 |
| R-specific | Category 10 |
| Cross-language verification | Category 11 |
