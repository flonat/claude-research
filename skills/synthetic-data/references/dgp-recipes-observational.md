# DGP Recipes: Observational Designs

> Data generating process recipes for quasi-experimental designs (DiD, RDD). Read during all modes of /synthetic-data.

## DiD Panel Data (Staggered Treatment)

### R: fabricatr

```r
library(fabricatr)
library(dplyr)

set.seed(42)

n_units <- 100
n_periods <- 10

# Staggered adoption: units adopt treatment at different times
df <- fabricate(
  unit = add_level(
    N = n_units,
    unit_fe = rnorm(N, sd = 0.5),
    # Treatment timing: 30% never treated, rest adopt in periods 4-7
    treatment_period = sample(c(NA, 4, 5, 6, 7),
                              N, replace = TRUE,
                              prob = c(0.3, 0.175, 0.175, 0.175, 0.175))
  ),
  period = add_level(
    N = n_periods,
    time_fe = 0.1 * (period - 1),  # linear time trend
    nest = FALSE
  )
) |>
  mutate(
    treated = !is.na(treatment_period) & period >= treatment_period,
    # Heterogeneous effects by cohort
    te = ifelse(treated, 0.5 + 0.1 * (period - treatment_period), 0),
    noise = rnorm(n(), sd = 0.3),
    outcome = 2.0 + unit_fe + time_fe + te + noise
  )

# Verify treatment timing
table(df$treatment_period, useNA = "always")

write.csv(df, "data/synthetic/did_staggered.csv", row.names = FALSE)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

n_units = 100
n_periods = 10

unit_fe = np.random.normal(0, 0.5, size=n_units)

# Staggered treatment: 30% never treated, rest adopt in periods 4-7
treatment_period = np.random.choice(
    [0, 4, 5, 6, 7], size=n_units,
    p=[0.3, 0.175, 0.175, 0.175, 0.175]
)
treatment_period[treatment_period == 0] = 999  # never-treated sentinel

rows = []
for i in range(n_units):
    for t in range(1, n_periods + 1):
        treated = 1 if t >= treatment_period[i] else 0
        te = (0.5 + 0.1 * (t - treatment_period[i])) if treated else 0
        time_fe = 0.1 * (t - 1)
        noise = np.random.normal(0, 0.3)
        outcome = 2.0 + unit_fe[i] + time_fe + te + noise
        rows.append({
            "unit": i + 1,
            "period": t,
            "treatment_period": int(treatment_period[i]) if treatment_period[i] < 999 else None,
            "treated": treated,
            "outcome": round(outcome, 4),
        })

df = pd.DataFrame(rows)
df.to_csv("data/synthetic/did_staggered.csv", index=False)
print(f"N units: {n_units}, N periods: {n_periods}, N rows: {len(df)}")
print(f"Never treated: {(df['treatment_period'].isna()).sum() // n_periods}")
```

---

## RDD (Running Variable with Cutoff)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

cutoff <- 50

df <- fabricate(
  N = 1000,
  # Running variable (e.g., test score 0-100)
  running_var = runif(N, min = 0, max = 100),
  # Treatment: assigned if running_var >= cutoff
  treatment = as.integer(running_var >= cutoff),
  # Distance from cutoff (centered)
  centered = running_var - cutoff,
  # Outcome with discontinuity at cutoff
  noise = rnorm(N, sd = 2),
  outcome = 10
    + 0.1 * centered                          # slope below cutoff
    + 3.0 * treatment                          # treatment effect (jump at cutoff)
    + 0.05 * centered * treatment              # different slope above cutoff
    + noise
)

# Verify: density around cutoff (McCrary-style check)
cat("N below cutoff:", sum(df$running_var < cutoff), "\n")
cat("N above cutoff:", sum(df$running_var >= cutoff), "\n")

write.csv(df, "data/synthetic/rdd.csv", row.names = FALSE)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

N = 1000
cutoff = 50

running_var = np.random.uniform(0, 100, size=N)
treatment = (running_var >= cutoff).astype(int)
centered = running_var - cutoff
noise = np.random.normal(0, 2, size=N)

outcome = (
    10
    + 0.1 * centered
    + 3.0 * treatment
    + 0.05 * centered * treatment
    + noise
)

df = pd.DataFrame({
    "id": range(1, N + 1),
    "running_var": np.round(running_var, 2),
    "treatment": treatment,
    "centered": np.round(centered, 2),
    "outcome": np.round(outcome, 4),
})

df.to_csv("data/synthetic/rdd.csv", index=False)
print(f"Cutoff: {cutoff}")
print(f"N below: {(treatment == 0).sum()}, N above: {(treatment == 1).sum()}")
```
