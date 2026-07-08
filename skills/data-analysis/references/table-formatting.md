# Table Formatting Recipes

> Language-specific code for generating publication-ready LaTeX tables.
> Read during Phase 4 of `/data-analysis`.

## R: modelsummary

The preferred table package. Produces booktabs-formatted `.tex` directly.

### Regression Table
```r
library(modelsummary)
library(fixest)

models <- list(
  "OLS"   = feols(y ~ treatment + x1, data = df),
  "FE"    = feols(y ~ treatment + x1 | firm, data = df),
  "IV"    = feols(y ~ x1 | firm | treatment ~ instrument, data = df)
)

modelsummary(models,
  output   = "paper/tables/table1.tex",
  stars    = c("*" = 0.10, "**" = 0.05, "***" = 0.01),
  coef_map = c("treatment" = "Treatment",
               "x1" = "Control Variable"),
  gof_map  = c("nobs", "r.squared", "adj.r.squared"),
  title    = "Main Results",
  notes    = "Standard errors clustered at the firm level.",
  escape   = FALSE)
```

### Descriptive Statistics
```r
datasummary(y + x1 + x2 ~ N + Mean + SD + Min + Max,
            data = df,
            output = "paper/tables/tab-descriptives.tex",
            title = "Descriptive Statistics")
```

### Balance Table
```r
datasummary_balance(~ treatment, data = df,
                    output = "paper/tables/tab-balance.tex",
                    title = "Covariate Balance")
```

## R: kableExtra (for custom tables)

```r
library(kableExtra)
df_summary %>%
  kable("latex", booktabs = TRUE,
        caption = "Custom Summary",
        label = "tab:custom") %>%
  kable_styling(latex_options = "hold_position") %>%
  add_header_above(c(" " = 1, "Group A" = 2, "Group B" = 2)) %>%
  footnote(general = "Source: Author's calculations.") %>%
  save_kable("paper/tables/tab-custom.tex")
```

## Python: Manual LaTeX Export

Python lacks an equivalent to `modelsummary`. Build tables manually or use `stargazer` port.

### statsmodels → LaTeX
```python
import statsmodels.api as sm

results = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': cluster})

# Manual export
with open("paper/tables/table1.tex", "w") as f:
    f.write(results.summary().as_latex())
```

### pandas → LaTeX (descriptive tables)
```python
desc = df[['y', 'x1', 'x2']].describe().T
desc = desc[['count', 'mean', 'std', 'min', 'max']]
desc.columns = ['N', 'Mean', 'SD', 'Min', 'Max']

desc.to_latex("paper/tables/tab-descriptives.tex",
              caption="Descriptive Statistics",
              label="tab:desc",
              float_format="%.3f",
              escape=False)
```

## Stata: esttab/estout

```stata
* Store estimates
eststo clear
eststo: reg y treatment x1, cluster(firm)
eststo: reghdfe y treatment x1, absorb(firm) cluster(firm)
eststo: ivregress 2sls y x1 (treatment = instrument), cluster(firm)

* Export
esttab using "paper/tables/table1.tex", replace ///
    booktabs label se ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    title("Main Results") ///
    mtitles("OLS" "FE" "IV") ///
    scalars("N Observations" "r2 R-squared") ///
    note("Standard errors clustered at the firm level.")
```

## Julia: PrettyTables

```julia
using PrettyTables, DataFrames

# Regression output
open("paper/tables/table1.tex", "w") do io
    pretty_table(io, results_df,
        backend = Val(:latex),
        tf = tf_latex_booktabs,
        title = "Main Results",
        label = "tab:main")
end
```

## Inline Statistics Export

For numbers referenced in the paper text, export `\newcommand` definitions:

### R
```r
sink("paper/tables/inline-stats.tex")
cat(sprintf("\\newcommand{\\Nobs}{%s}\n", format(nrow(df), big.mark = ",")))
cat(sprintf("\\newcommand{\\maineffect}{%.3f}\n", coef(m1)["treatment"]))
cat(sprintf("\\newcommand{\\mainse}{%.3f}\n", se(m1)["treatment"]))
cat(sprintf("\\newcommand{\\mainpval}{%.3f}\n", pvalue(m1)["treatment"]))
sink()
```

### Python
```python
with open("paper/tables/inline-stats.tex", "w") as f:
    f.write(f"\\newcommand{{\\Nobs}}{{{len(df):,}}}\n")
    f.write(f"\\newcommand{{\\maineffect}}{{{coef:.3f}}}\n")
    f.write(f"\\newcommand{{\\mainse}}{{{se:.3f}}}\n")
```

### Stata
```stata
file open fh using "paper/tables/inline-stats.tex", write replace
file write fh "\newcommand{\Nobs}{`=string(e(N), "%12.0fc")'}" _n
file write fh "\newcommand{\maineffect}{`=string(_b[treatment], "%9.3f")'}" _n
file close fh
```
