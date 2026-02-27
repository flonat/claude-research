# Replication Protocol

> Step-by-step process for replicating results from a published paper before extending.

## When to Use

- Replicating a paper's empirical results as a foundation for your own work
- Verifying a coauthor's code produces the claimed results
- R&R where a referee asks you to demonstrate you can replicate a benchmark

## Principles

1. **Replicate first, extend later** — never "improve" during replication
2. **Line-by-line translation** — match the original code's logic exactly
3. **Programmatic comparison** — no eyeballing; use tolerances
4. **Document everything** — every discrepancy gets recorded

## Phase 1: Inventory Gold Standard Numbers

Before writing any code:

1. Open the original paper
2. Extract **every** numerical result you plan to replicate:
   - Point estimates (coefficients, means, treatment effects)
   - Standard errors / confidence intervals
   - Sample sizes (N)
   - Test statistics (t-stats, F-stats, p-values)
   - Summary statistics from descriptive tables
3. Record them in `replication-targets.md`:

```markdown
# Replication Targets

Source: [Author (Year), "Title"]

## Table 1: Summary Statistics
| Variable | Paper Value | Our Value | Match? |
|----------|-------------|-----------|--------|
| Mean income | 45,230 | | |
| N | 12,500 | | |

## Table 2: Main Results
| Specification | Estimate | SE | Our Estimate | Our SE | Match? |
|--------------|----------|-----|-------------|--------|--------|
| OLS baseline | 0.034 | 0.012 | | | |
| IV | 0.051 | 0.018 | | | |
```

## Phase 2: Line-by-Line Translation

1. Obtain the original code (replication package, GitHub, or request from authors)
2. Translate to your language (R or Python) **without modifying the logic**:
   - Same variable names where possible
   - Same sample restrictions
   - Same model specifications
   - Same standard error clustering
3. Comment each block referencing the original code line numbers

**Do NOT:**
- Fix "bugs" in the original code
- Use "better" estimators
- Add robustness checks
- Clean the code style

## Phase 3: Programmatic Comparison

Compare your results against Phase 1 targets using these tolerances:

| Metric | Tolerance | Rationale |
|--------|-----------|-----------|
| Integers (N, counts) | Exact match | No reason for any difference |
| Point estimates | < 0.01 | Numerical precision differences |
| Standard errors | < 0.05 | Clustering/bootstrap can vary slightly |
| p-values | < 0.01 | Derived from above |
| R-squared | < 0.001 | Numerical precision |

Generate a comparison programmatically:

```r
# R example
compare_results <- function(paper_value, our_value, tolerance) {
  diff <- abs(paper_value - our_value)
  list(
    paper = paper_value,
    ours = our_value,
    diff = diff,
    match = diff <= tolerance
  )
}
```

```python
# Python example
def compare_results(paper_value, our_value, tolerance):
    diff = abs(paper_value - our_value)
    return {
        "paper": paper_value,
        "ours": our_value,
        "diff": diff,
        "match": diff <= tolerance
    }
```

## Phase 4: Extend

Only after Phase 3 produces a clean replication report:

1. Create a **separate script** for extensions (never modify replication code)
2. Document what you're changing and why
3. Compare extended results against replication baseline

## Output Files

At the end of a replication, the project directory should contain:

```
project/
├── replication-targets.md    ← Phase 1: gold standard numbers
├── replication-report.md     ← Phase 3: comparison results
├── code/
│   ├── 01-replicate.R        ← Phase 2: line-by-line translation
│   └── 02-extend.R           ← Phase 4: your extensions
└── data/
    └── ...
```

### Replication Report Format

```markdown
# Replication Report

**Paper:** [Author (Year), "Title"]
**Date:** YYYY-MM-DD
**Replicated by:** the user

## Summary
- Tables replicated: X/Y
- Figures replicated: X/Y
- Overall: PASS / PARTIAL / FAIL

## Detailed Results
[Table-by-table comparison with match status]

## Discrepancies
[Any values outside tolerance, with investigation notes]

## Notes
[Software versions, data access issues, ambiguities in original code]
```

## Cross-References

- **`/code-review`** — Run on replication scripts before finalising
- **Referee 2 agent** — For formal verification of the full replication
- **`/code-archaeology`** — If the original replication package needs understanding first
