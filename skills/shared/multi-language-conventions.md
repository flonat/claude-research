# Multi-Language Conventions

> Code style, packages, and output patterns for R, Python, Stata, and Julia.
> Referenced by `/data-analysis`, `/synthetic-data`, `/replication-package`.

## Language Detection

Detect from project context in this order:

1. Existing scripts in `code/` or `src/` → match language
2. `CLAUDE.md` or `MEMORY.md` mentions → follow stated preference
3. User request → explicit language choice
4. Default → R for econometrics/causal inference, Python for ML/simulation

## R Conventions

### Style
- Assignment: `<-` (never `=`)
- Pipe: `|>` (base R) preferred; `%>%` acceptable if tidyverse already loaded
- Naming: `snake_case` for variables and functions
- Line width: 80 characters

### Core Packages

| Task | Package |
|------|---------|
| Data wrangling | `dplyr`, `tidyr`, `data.table` |
| Estimation | `fixest`, `estimatr`, `lme4`, `survival` |
| Causal inference | `did`, `didimputation`, `synthdid`, `rdrobust`, `MatchIt` |
| Tables | `modelsummary`, `kableExtra`, `stargazer` |
| Figures | `ggplot2` + `ggthemes`, `patchwork` |
| Reporting | `rmarkdown`, `knitr` |
| Power analysis | `DeclareDesign`, `pwr`, `simr` |
| Survey | `survey`, `srvyr`, `qualtRics` |

### Output Pattern
```r
# Tables → LaTeX
modelsummary(models, output = "paper/tables/table1.tex",
             stars = c("*" = 0.10, "**" = 0.05, "***" = 0.01))

# Figures → PDF
ggsave("paper/figures/fig1.pdf", width = 6, height = 4)
```

## Python Conventions

### Style
- **Always use `uv`** — never bare `python` or `pip`
- Naming: `snake_case` for variables/functions, `PascalCase` for classes
- Type hints encouraged but not required for analysis scripts
- Line width: 88 characters (Black default)

### Core Packages

| Task | Package |
|------|---------|
| Data wrangling | `pandas`, `polars` |
| Estimation | `statsmodels`, `linearmodels`, `scikit-learn` |
| Causal inference | `econml`, `causalml`, `doubleml` |
| Tables | `stargazer` (via statsmodels), custom `.tex` export |
| Figures | `matplotlib`, `seaborn`, `plotnine` |
| Power analysis | `statsmodels.stats.power`, `numpy` simulation |
| Survey | `pandas` + manual parsing |

### Output Pattern
```python
import pandas as pd

# Tables → LaTeX
df.to_latex("paper/tables/table1.tex", index=False,
            caption="Descriptive Statistics", label="tab:desc")

# Figures → PDF
fig.savefig("paper/figures/fig1.pdf", bbox_inches="tight", dpi=300)
```

## Stata Conventions

### Style
- Use `//` for inline comments, `/* */` for blocks
- Naming: lowercase with underscores
- Always set `version` at script top
- Use `capture log close` / `log using` pattern

### Core Commands

| Task | Command |
|------|---------|
| Data wrangling | `gen`, `replace`, `reshape`, `merge`, `collapse` |
| Estimation | `reg`, `ivregress`, `xtreg`, `areg`, `ppmlhdfe` |
| Causal inference | `did_multiplegt`, `csdid`, `rdrobust`, `eventstudyinteract` |
| Tables | `esttab`, `outreg2`, `estout` |
| Figures | `twoway`, `coefplot`, `graph export` |
| Power analysis | `power`, `simulate` |

### Output Pattern
```stata
// Tables → LaTeX
esttab m1 m2 m3 using "paper/tables/table1.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01)

// Figures → PDF
graph export "paper/figures/fig1.pdf", replace
```

## Julia Conventions

### Style
- Naming: `snake_case` for functions/variables, `PascalCase` for types
- Use `using` not `import` for standard packages
- Line width: 92 characters

### Core Packages

| Task | Package |
|------|---------|
| Data wrangling | `DataFrames.jl`, `CSV.jl` |
| Estimation | `GLM.jl`, `FixedEffectModels.jl`, `MixedModels.jl` |
| Causal inference | `CausalInference.jl` (limited — often custom) |
| Tables | `PrettyTables.jl` (LaTeX backend) |
| Figures | `Makie.jl`, `AlgebraOfGraphics.jl`, `Plots.jl` |
| Power analysis | Custom simulation with `Distributions.jl` |

### Output Pattern
```julia
using PrettyTables
# Tables → LaTeX
open("paper/tables/table1.tex", "w") do io
    pretty_table(io, df, backend=Val(:latex))
end

# Figures → PDF
save("paper/figures/fig1.pdf", fig)
```

## Cross-Language Rules

1. **Output routing:** All `.tex` table files and figure files go to `paper/tables/` or `paper/figures/` per the `overleaf-separation` rule. Scripts stay in `code/` or `src/`.
2. **Reproducibility header:** Every script should start with a comment block stating purpose, inputs, outputs, and dependencies.
3. **Seed setting:** Always set random seeds explicitly (`set.seed()`, `np.random.seed()`, `set seed`, `Random.seed!`).
4. **Path convention:** Use project-relative paths, never absolute paths. Assume scripts run from project root.
5. **Data flow:** `data/raw/` → script → `data/processed/` → script → `paper/` output. Never write to `data/raw/`.
