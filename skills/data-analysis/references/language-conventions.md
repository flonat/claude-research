# Language Conventions — Supplementary Notes

> Project-specific conventions that extend `shared/multi-language-conventions.md`.
> Read when the shared file doesn't cover a specific need.

## Script Numbering Convention

Scripts are numbered to reflect execution order:

```
code/
├── 00_setup.R           # Environment setup, package loading
├── 01_eda.R             # Exploratory data analysis
├── 02_estimation.R      # Main estimation
├── 03_tables_figures.R  # Publication output
├── 04_robustness.R      # Robustness checks
└── A1_appendix.R        # Appendix analyses
```

Use the same convention across languages. For multi-language projects, add a language suffix: `01_eda_R.R`, `01_eda_py.py`.

## Reproducibility Requirements

### R
```r
# Top of every script
rm(list = ls())
set.seed(42)
options(scipen = 999)  # avoid scientific notation

# Package management
if (!require("pacman")) install.packages("pacman")
pacman::p_load(tidyverse, fixest, modelsummary)
```

### Python
```python
# Top of every script
import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)
```

### Stata
```stata
version 17
clear all
set more off
set seed 42
capture log close
log using "output/logs/02_estimation.log", replace
```

### Julia
```julia
using Random
Random.seed!(42)
```

## Data Loading Patterns

Always load from project-relative paths. Assume scripts run from project root.

| Language | Pattern |
|----------|---------|
| R | `df <- read_csv("data/processed/analysis_sample.csv")` |
| Python | `df = pd.read_csv("data/processed/analysis_sample.csv")` |
| Stata | `use "data/processed/analysis_sample.dta", clear` |
| Julia | `df = CSV.read("data/processed/analysis_sample.csv", DataFrame)` |

## Error Handling

Scripts should fail loudly, not silently:

- R: Use `stopifnot()` for assertions, `tryCatch()` for recoverable errors
- Python: Use `assert` for invariants, explicit `try/except` only for I/O
- Stata: Use `assert` and `confirm`
- Julia: Use `@assert` macro
