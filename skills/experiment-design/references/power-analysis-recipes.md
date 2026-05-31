# Power Analysis Recipes

> Language-specific code patterns for common experimental designs.
> Read during Power mode of `/experiment-design`.

## R: DeclareDesign (Preferred)

### Simple Two-Group RCT
```r
library(DeclareDesign)

design <- declare_model(N = 200,
    U = rnorm(N),
    potential_outcomes(Y ~ 0.3 * Z + U)) +
  declare_inquiry(ATE = mean(Y_Z_1 - Y_Z_0)) +
  declare_assignment(Z = complete_ra(N)) +
  declare_measurement(Y = reveal_outcomes(Y ~ Z)) +
  declare_estimator(Y ~ Z, .method = lm)

# Power curve
diagnose_design(design, sims = 500)

# Redesign for different N
designs <- redesign(design, N = seq(50, 500, 50))
diagnosis <- diagnose_designs(designs, sims = 500)
```

### Cluster-Randomized Design
```r
design <- declare_model(
    clusters = add_level(N = 30, cluster_effect = rnorm(N, sd = 0.5)),
    individuals = add_level(N = 20, U = rnorm(N))) +
  declare_model(potential_outcomes(Y ~ 0.3 * Z + cluster_effect + U)) +
  declare_inquiry(ATE = mean(Y_Z_1 - Y_Z_0)) +
  declare_assignment(Z = cluster_ra(clusters = clusters)) +
  declare_measurement(Y = reveal_outcomes(Y ~ Z)) +
  declare_estimator(Y ~ Z, clusters = clusters, .method = lm_robust)
```

### 2x2 Factorial
```r
design <- declare_model(N = 400, U = rnorm(N),
    potential_outcomes(Y ~ 0.3 * Z1 + 0.2 * Z2 + 0.1 * Z1 * Z2 + U)) +
  declare_inquiry(
    main_Z1 = mean(Y_Z1_1_Z2_0 - Y_Z1_0_Z2_0 + Y_Z1_1_Z2_1 - Y_Z1_0_Z2_1) / 2,
    main_Z2 = mean(Y_Z1_0_Z2_1 - Y_Z1_0_Z2_0 + Y_Z1_1_Z2_1 - Y_Z1_1_Z2_0) / 2,
    interaction = mean(Y_Z1_1_Z2_1 - Y_Z1_1_Z2_0 - Y_Z1_0_Z2_1 + Y_Z1_0_Z2_0)
  ) +
  declare_assignment(Z1 = complete_ra(N), Z2 = complete_ra(N)) +
  declare_measurement(Y = reveal_outcomes(Y ~ Z1 + Z2)) +
  declare_estimator(Y ~ Z1 * Z2, .method = lm)
```

## R: pwr (Quick Calculations)

```r
library(pwr)

# Two-sample t-test
pwr.t.test(d = 0.3, power = 0.80, sig.level = 0.05, type = "two.sample")

# ANOVA (k groups)
pwr.anova.test(k = 3, f = 0.25, power = 0.80, sig.level = 0.05)

# Chi-squared test
pwr.chisq.test(w = 0.3, df = 2, power = 0.80, sig.level = 0.05)

# Correlation
pwr.r.test(r = 0.2, power = 0.80, sig.level = 0.05)

# Power curve
n_range <- seq(20, 200, 10)
power_vals <- sapply(n_range, function(n)
  pwr.t.test(d = 0.3, n = n, sig.level = 0.05)$power)
plot(n_range, power_vals, type = "l", xlab = "N per group", ylab = "Power")
abline(h = 0.80, lty = 2, col = "red")
```

## Python: statsmodels

```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
import numpy as np

# Two-sample t-test
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.3, power=0.80, alpha=0.05)

# Power curve
n_range = np.arange(20, 201, 10)
powers = [analysis.power(effect_size=0.3, nobs1=n, alpha=0.05) for n in n_range]

# ANOVA
anova = FTestAnovaPower()
n = anova.solve_power(effect_size=0.25, k_groups=3, power=0.80, alpha=0.05)
```

## Python: Simulation-Based

```python
import numpy as np
from scipy import stats

def simulate_power(n_per_group, effect_size, n_sims=1000, alpha=0.05):
    significant = 0
    for _ in range(n_sims):
        control = np.random.normal(0, 1, n_per_group)
        treatment = np.random.normal(effect_size, 1, n_per_group)
        _, p = stats.ttest_ind(treatment, control)
        if p < alpha:
            significant += 1
    return significant / n_sims
```

## Stata

```stata
* Two-sample means test
power twomeans 0 0.3, sd(1) power(0.80) alpha(0.05)

* Power curve
power twomeans 0 0.3, sd(1) n(50(50)500) graph

* Cluster-randomized
power twomeans 0 0.3, sd(1) power(0.80) cluster ///
    k1(15) k2(15) rho(0.05) m1(20) m2(20)
```

## Output Table Template

```
Power Analysis Results
=====================
Design:          [between/within/factorial/cluster]
Effect size:     [d/f/r/w] = [value] (source: [literature/pilot/SESOI])
Alpha:           0.05
Test:            [t-test/ANOVA/chi-squared/regression]

Required N per group for:
  Power = 0.80:  [N]
  Power = 0.90:  [N]
  Power = 0.95:  [N]

Total N:         [total across groups/conditions]
```
