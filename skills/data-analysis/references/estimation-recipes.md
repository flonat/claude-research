# Estimation Recipes

> Language-specific code patterns for common estimation methods.
> Read during Phase 3 of `/data-analysis`.

## OLS with Fixed Effects

### R (fixest)
```r
library(fixest)
m1 <- feols(y ~ treatment + x1 + x2 | firm + year, data = df,
            cluster = ~firm)
m2 <- feols(y ~ treatment + x1 + x2 | firm + year + industry,
            data = df, cluster = ~firm)
```

### Python (linearmodels)
```python
from linearmodels.panel import PanelOLS
mod = PanelOLS(df.y, df[['treatment', 'x1', 'x2']],
               entity_effects=True, time_effects=True)
res = mod.fit(cov_type='clustered', cluster_entity=True)
```

### Stata
```stata
reghdfe y treatment x1 x2, absorb(firm year) cluster(firm)
```

### Julia
```julia
using FixedEffectModels
m = reg(df, @formula(y ~ treatment + x1 + x2 + fe(firm) + fe(year)),
        Vcov.cluster(:firm))
```

## Instrumental Variables

### R (fixest)
```r
m_iv <- feols(y ~ x1 | firm + year | treatment ~ instrument,
              data = df, cluster = ~firm)
fitstat(m_iv, type = "ivf")  # first-stage F
```

### Python (linearmodels)
```python
from linearmodels.iv import IV2SLS
mod = IV2SLS(df.y, df[['x1']], df[['treatment']], df[['instrument']])
res = mod.fit(cov_type='clustered', clusters=df['firm'])
```

### Stata
```stata
ivregress 2sls y x1 (treatment = instrument), cluster(firm)
estat firststage
```

## Difference-in-Differences

### R — Callaway & Sant'Anna (2021)
```r
library(did)
att_gt <- att_gt(yname = "y", tname = "year", idname = "id",
                 gname = "first_treat", data = df)
agg <- aggte(att_gt, type = "dynamic")
ggdid(agg)
```

### R — Sun & Abraham (2021)
```r
library(fixest)
m_sa <- feols(y ~ sunab(first_treat, year) | id + year,
              data = df, cluster = ~id)
iplot(m_sa)
```

### Python (doubleml)
```python
from doubleml import DoubleMLDID
dml_did = DoubleMLDID(obj_dml_data, ml_g, ml_m)
dml_did.fit()
```

### Stata
```stata
csdid y x1 x2, ivar(id) time(year) gvar(first_treat)
csdid_plot
```

## Regression Discontinuity

### R (rdrobust)
```r
library(rdrobust)
rd <- rdrobust(y = df$y, x = df$running_var, c = 0)
summary(rd)
rdplot(y = df$y, x = df$running_var, c = 0)
```

### Stata
```stata
rdrobust y running_var, c(0)
rdplot y running_var, c(0)
```

## Synthetic Control

### R (synthdid)
```r
library(synthdid)
setup <- panel.matrices(df, unit = "state", time = "year",
                        outcome = "y", treatment = "treated")
tau <- synthdid_estimate(setup$Y, setup$N0, setup$T0)
plot(tau)
```

### Stata
```stata
synth y y(1980) y(1985) x1 x2, trunit(1) trperiod(1990)
```

## Diagnostics Checklist

| Method | Key diagnostic | What to report |
|--------|---------------|----------------|
| OLS/FE | Multicollinearity | VIF < 10 |
| IV | First-stage F | F > 10 (Stock-Yogo) |
| DiD | Parallel trends | Pre-treatment coefficients + joint test |
| RDD | McCrary density test | No bunching at cutoff |
| SC | Pre-treatment fit | RMSPE ratio |
| All | Heteroskedasticity | Clustered or robust SEs |
