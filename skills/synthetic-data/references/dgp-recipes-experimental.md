# DGP Recipes: Experimental Designs

> Data generating process recipes for experimental designs (RCT, factorial, cluster). Read during all modes of /synthetic-data.

## Simple RCT (Binary Treatment, Continuous Outcome)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

df <- fabricate(
  N = 500,
  age = round(runif(N, 18, 65)),
  female = draw_binary(prob = 0.52, N = N),
  treatment = draw_binary(prob = 0.5, N = N),
  noise = rnorm(N, mean = 0, sd = 1),
  outcome = 0.5 + 0.3 * treatment + 0.02 * age - 0.1 * female + noise
)

write.csv(df, "data/synthetic/rct_simple.csv", row.names = FALSE)
summary(df)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

N = 500
age = np.random.randint(18, 66, size=N)
female = np.random.binomial(1, 0.52, size=N)
treatment = np.random.binomial(1, 0.5, size=N)
noise = np.random.normal(0, 1, size=N)
outcome = 0.5 + 0.3 * treatment + 0.02 * age - 0.1 * female + noise

df = pd.DataFrame({
    "id": range(1, N + 1),
    "age": age,
    "female": female,
    "treatment": treatment,
    "outcome": outcome,
})

df.to_csv("data/synthetic/rct_simple.csv", index=False)
print(df.describe())
```

---

## Factorial Design (2x2 with Interaction)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

df <- fabricate(
  N = 800,
  factor_a = draw_binary(prob = 0.5, N = N),        # e.g., AI vs Human
  factor_b = draw_binary(prob = 0.5, N = N),        # e.g., Hedonic vs Utilitarian
  noise = rnorm(N, sd = 1),
  outcome = 2.0
    + 0.4 * factor_a                                 # main effect A
    + 0.2 * factor_b                                 # main effect B
    + 0.15 * factor_a * factor_b                     # interaction
    + noise
)

# Verify balance
table(df$factor_a, df$factor_b)
write.csv(df, "data/synthetic/factorial_2x2.csv", row.names = FALSE)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

N = 800
factor_a = np.random.binomial(1, 0.5, size=N)
factor_b = np.random.binomial(1, 0.5, size=N)
noise = np.random.normal(0, 1, size=N)

outcome = 2.0 + 0.4 * factor_a + 0.2 * factor_b + 0.15 * factor_a * factor_b + noise

df = pd.DataFrame({
    "id": range(1, N + 1),
    "factor_a": factor_a,
    "factor_b": factor_b,
    "outcome": outcome,
})

df.to_csv("data/synthetic/factorial_2x2.csv", index=False)
print(pd.crosstab(df["factor_a"], df["factor_b"]))
```

### Extension: 2x3 Factorial

```r
library(fabricatr)

set.seed(42)

df <- fabricate(
  N = 900,
  factor_a = draw_binary(prob = 0.5, N = N),
  factor_b = sample(c("low", "medium", "high"), N, replace = TRUE),
  fb_med = as.integer(factor_b == "medium"),
  fb_high = as.integer(factor_b == "high"),
  noise = rnorm(N, sd = 1),
  outcome = 2.0
    + 0.4 * factor_a
    + 0.2 * fb_med + 0.5 * fb_high
    + 0.1 * factor_a * fb_med + 0.25 * factor_a * fb_high
    + noise
)

table(df$factor_a, df$factor_b)
write.csv(df, "data/synthetic/factorial_2x3.csv", row.names = FALSE)
```

---

## Cluster-Randomized Design (with ICC)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

icc <- 0.10  # intraclass correlation
sigma_cluster <- sqrt(icc / (1 - icc))  # cluster-level SD
sigma_individual <- 1                     # individual-level SD

df <- fabricate(
  cluster = add_level(
    N = 30,                                           # 30 clusters
    cluster_effect = rnorm(N, sd = sigma_cluster),
    treatment = draw_binary(prob = 0.5, N = N)        # cluster-level assignment
  ),
  individual = add_level(
    N = 20,                                           # 20 per cluster
    noise = rnorm(N, sd = sigma_individual),
    outcome = 1.0 + 0.3 * treatment + cluster_effect + noise
  )
)

# Verify ICC
library(lme4)
m <- lmer(outcome ~ 1 + (1 | cluster), data = df)
vc <- as.data.frame(VarCorr(m))
cat("Achieved ICC:", vc$vcov[1] / sum(vc$vcov), "\n")

write.csv(df, "data/synthetic/cluster_rct.csv", row.names = FALSE)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

n_clusters = 30
n_per_cluster = 20
icc = 0.10
sigma_cluster = np.sqrt(icc / (1 - icc))

cluster_ids = np.repeat(range(n_clusters), n_per_cluster)
cluster_effects = np.random.normal(0, sigma_cluster, size=n_clusters)
treatment = np.random.binomial(1, 0.5, size=n_clusters)  # cluster-level

rows = []
for c in range(n_clusters):
    for i in range(n_per_cluster):
        noise = np.random.normal(0, 1)
        outcome = 1.0 + 0.3 * treatment[c] + cluster_effects[c] + noise
        rows.append({
            "cluster": c + 1,
            "individual": i + 1,
            "treatment": treatment[c],
            "outcome": outcome,
        })

df = pd.DataFrame(rows)
df.to_csv("data/synthetic/cluster_rct.csv", index=False)
print(f"N clusters: {n_clusters}, N total: {len(df)}")
print(f"Target ICC: {icc:.2f}")
```
