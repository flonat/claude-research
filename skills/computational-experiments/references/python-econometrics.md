# Python Econometrics Code Templates

> Copy-paste-ready code blocks for panel data, DiD, IV/2SLS, and table export. Use `linearmodels` for panel models and `pyfixest` for R-style `feols()` syntax.

**Critical:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`.

---

## Panel DiD with linearmodels

```python
import pandas as pd
from linearmodels.panel import PanelOLS

# Set multi-index: entity (firm/individual) × time
df = df.set_index(["entity_id", "year"])

# Basic two-way fixed effects DiD
mod = PanelOLS.from_formula(
    "y ~ treated_post + EntityEffects + TimeEffects",
    data=df,
)
res = mod.fit(cov_type="clustered", cluster_entity=True)
print(res.summary)
```

### Event study specification

```python
# Create event-time dummies (omit t=-1 as reference)
for t in range(-4, 6):
    if t != -1:
        df[f"evt_{t}"] = (df["event_time"] == t).astype(int)

evt_vars = " + ".join([f"evt_{t}" for t in range(-4, 6) if t != -1])
mod = PanelOLS.from_formula(
    f"y ~ {evt_vars} + EntityEffects + TimeEffects",
    data=df,
)
res = mod.fit(cov_type="clustered", cluster_entity=True)
```

---

## Panel DiD with pyfixest

```python
import pyfixest as pf

# Basic TWFE (mirrors R feols() syntax)
fit = pf.feols("y ~ treated_post | entity_id + year", data=df, vcov={"CRV1": "entity_id"})
fit.summary()

# Event study
fit_es = pf.feols("y ~ i(event_time, ref=-1) | entity_id + year", data=df, vcov={"CRV1": "entity_id"})
pf.iplot(fit_es)  # coefficient plot
```

### Multiple specifications at once

```python
# pyfixest supports stepwise FE
fits = pf.feols("y ~ treated_post | csw(entity_id, year)", data=df, vcov={"CRV1": "entity_id"})
pf.etable(fits)  # side-by-side table
```

---

## IV / 2SLS with linearmodels

```python
from linearmodels.iv import IV2SLS

# Endogenous: x_endog, Instrument: z
mod = IV2SLS.from_formula(
    "y ~ x_exog + [x_endog ~ z]",
    data=df,
)
res = mod.fit(cov_type="robust")
print(res.summary)

# First-stage diagnostics
print(f"First-stage F-stat: {res.first_stage.diagnostics['f.stat']:.2f}")
print(f"First-stage p-value: {res.first_stage.diagnostics['f.pval']:.4f}")
```

---

## Table Export to LaTeX

### From linearmodels

```python
# Export summary as LaTeX
with open("output/tables/table1.tex", "w") as f:
    f.write(res.summary.as_latex())
```

### From pyfixest (preferred — booktabs, multiple specs)

```python
pf.etable(
    [fit1, fit2, fit3],
    type="tex",
    file="output/tables/regression_table.tex",
    signif_code=[0.01, 0.05, 0.1],
)
```

### Custom table with stargazer-style output

```python
from stargazer.stargazer import Stargazer  # pip: stargazer

star = Stargazer([res1, res2, res3])
star.title("Main Results")
star.custom_columns(["OLS", "FE", "IV"], [1, 1, 1])
with open("output/tables/main_results.tex", "w") as f:
    f.write(star.render_latex())
```

---

## Panel Data Assembly Checklist

Run these checks before estimation:

```python
# 1. Balance check
panel_counts = df.groupby("entity_id")["year"].nunique()
is_balanced = panel_counts.nunique() == 1
print(f"Balanced panel: {is_balanced} ({panel_counts.unique()} periods)")

# 2. Duplicate check (critical — duplicates silently corrupt FE)
dupes = df.duplicated(subset=["entity_id", "year"], keep=False)
assert not dupes.any(), f"Found {dupes.sum()} duplicate entity-year pairs"

# 3. Missing data report
missing = df.isnull().sum()
print(f"Missing values:\n{missing[missing > 0]}")

# 4. Treatment variation check
treat_var = df.groupby("entity_id")["treated_post"].nunique()
print(f"Entities with treatment variation: {(treat_var > 1).sum()} / {len(treat_var)}")
```

---

## Common Pitfalls

| Pitfall | Why it matters | Fix |
|---------|---------------|-----|
| **TWFE with staggered adoption** | Biased estimates with heterogeneous treatment effects | Use `did2s`, Callaway-Sant'Anna (`csdid`), or Sun-Abraham |
| **Post-treatment controls** | Conditioning on outcomes of treatment biases estimates | Only include pre-treatment covariates |
| **GDP in levels vs logs** | Levels give scale-dependent results, confound trends | Use log(GDP) or GDP per capita growth rates |
| **Clustering at wrong level** | Underestimates SEs if treatment varies at higher level | Cluster at treatment assignment level |
| **Absorbing singleton FE** | Singletons inflate F-stats, bias SEs downward | pyfixest drops singletons automatically; linearmodels does not — check manually |
| **Not checking first-stage F** | Weak instruments → biased IV toward OLS | Require F > 10 (Stock-Yogo); report F-stat always |
