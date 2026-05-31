# Calibration Targets

> How to calibrate synthetic data to match published statistics.
> Read during Calibrated mode of `/synthetic-data`.

## Overview

Calibrated synthetic data reproduces the statistical properties of a real dataset without containing any real observations. The goal is to match published summary statistics closely enough that analysis code tested on the synthetic data will work correctly on the real data.

## What to Collect from the Source Paper

Before generating calibrated data, extract these statistics from the source paper's descriptive tables:

| Statistic | Where to find it | Priority |
|-----------|-----------------|----------|
| Means and SDs | Table 1 (descriptive statistics) | Required |
| Sample size | Abstract, Table 1, or methods section | Required |
| Variable types | Variable descriptions, codebook | Required |
| Correlation matrix | Table of correlations, or appendix | Strongly recommended |
| Effect sizes | Regression tables (coefficients, SEs) | Recommended |
| Distribution shape | Histograms, skewness/kurtosis stats | Nice to have |
| Missing data rates | Methods section, footnotes to tables | Nice to have |
| Subgroup proportions | Demographic breakdowns | Recommended |

**If the paper does not report correlations**, estimate them from regression coefficients or use domain-typical values from `references/calibration-targets.md` (this file, see Common Calibration Targets below).

---

## Matching Means and SDs

The simplest calibration: shift and scale each variable to match the target moments.

### R

```r
calibrate_normal <- function(n, target_mean, target_sd, seed = 42) {
  set.seed(seed)
  x <- rnorm(n)
  x * target_sd + target_mean
}

# Example: income (target mean = 52000, SD = 18000)
income <- calibrate_normal(500, 52000, 18000)
cat("Mean:", mean(income), "SD:", sd(income), "\n")
```

### Python

```python
import numpy as np

def calibrate_normal(n, target_mean, target_sd, seed=42):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    return x * target_sd + target_mean

income = calibrate_normal(500, 52000, 18000)
print(f"Mean: {income.mean():.0f}, SD: {income.std():.0f}")
```

### For Non-Normal Variables

Do not use mean/SD matching for variables with bounded or skewed distributions. Instead:

| Variable type | Calibration method |
|---------------|-------------------|
| Likert (1-7) | Ordinal: specify category probabilities matching reported means |
| Income, reaction time | Log-normal: match mean and SD on log scale |
| Counts | Poisson/NB: match mean (and variance for NB) |
| Proportions | Beta: match mean and variance |
| Binary | Bernoulli: match proportion |

---

## Matching Correlations

### Cholesky Decomposition Method

The standard approach for inducing a target correlation structure on continuous variables.

### R

```r
library(MASS)

set.seed(42)

# Target correlation matrix (from published Table 2)
target_cor <- matrix(c(
  1.00, 0.35, -0.20, 0.15,
  0.35, 1.00,  0.10, 0.40,
 -0.20, 0.10,  1.00, -0.05,
  0.15, 0.40, -0.05, 1.00
), nrow = 4, byrow = TRUE)

# Target means and SDs
target_means <- c(3.5, 4.2, 2.8, 5.1)
target_sds   <- c(1.2, 0.9, 1.5, 0.8)

# Generate correlated data
target_sigma <- diag(target_sds) %*% target_cor %*% diag(target_sds)
df <- mvrnorm(n = 500, mu = target_means, Sigma = target_sigma)
colnames(df) <- c("trust", "satisfaction", "risk", "intention")

# Verify
cat("Achieved correlations:\n")
round(cor(df), 3)
cat("\nTarget vs achieved means:\n")
rbind(target = target_means, achieved = colMeans(df))
```

### Python

```python
import numpy as np

np.random.seed(42)

target_cor = np.array([
    [1.00, 0.35, -0.20, 0.15],
    [0.35, 1.00,  0.10, 0.40],
    [-0.20, 0.10, 1.00, -0.05],
    [0.15, 0.40, -0.05, 1.00],
])

target_means = np.array([3.5, 4.2, 2.8, 5.1])
target_sds = np.array([1.2, 0.9, 1.5, 0.8])

# Convert correlation to covariance
target_cov = np.outer(target_sds, target_sds) * target_cor

# Generate
data = np.random.multivariate_normal(target_means, target_cov, size=500)
var_names = ["trust", "satisfaction", "risk", "intention"]

# Verify
achieved_cor = np.corrcoef(data.T)
print("Achieved correlations:")
print(np.round(achieved_cor, 3))
```

### Handling Mixed Variable Types

When the dataset has both continuous and categorical/ordinal variables:

1. Generate all variables as latent continuous using Cholesky decomposition
2. Transform to target types:
   - Binary: threshold at the proportion's quantile
   - Ordinal (Likert): threshold at cumulative category probabilities
   - Count: apply inverse CDF of Poisson/NB to uniform quantiles of the normal

```r
# Example: latent -> binary (target proportion = 0.35)
latent_female <- df[, "latent_female"]
female <- as.integer(latent_female > qnorm(1 - 0.35))
mean(female)  # should be ~0.35

# Example: latent -> 7-point Likert (target mean = 4.2)
latent_trust <- df[, "latent_trust"]
# Determine thresholds from target distribution
probs <- c(0.05, 0.10, 0.15, 0.25, 0.20, 0.15, 0.10)  # category proportions
thresholds <- qnorm(cumsum(probs[-7]))
trust_likert <- findInterval(latent_trust, thresholds) + 1
table(trust_likert) / length(trust_likert)
```

---

## Matching Effect Sizes

Calibrate treatment effects to match published regression coefficients.

### From Cohen's d

```r
# Published effect: d = 0.45 (treatment vs control)
# Control group: mean = 3.2, SD = 1.1
d <- 0.45
control_mean <- 3.2
control_sd <- 1.1
treatment_mean <- control_mean + d * control_sd  # 3.695

# Generate
control <- rnorm(250, mean = control_mean, sd = control_sd)
treatment <- rnorm(250, mean = treatment_mean, sd = control_sd)
```

### From Regression Coefficients

```r
# Published: Y = 2.1 + 0.35*Treatment + 0.02*Age - 0.15*Female, R^2 = 0.12
# Residual SD = sqrt(Var(Y) * (1 - R^2))

var_y <- 1.5^2       # from descriptive table
r_squared <- 0.12
residual_sd <- sqrt(var_y * (1 - r_squared))

df <- fabricate(
  N = 500,
  treatment = draw_binary(prob = 0.5, N = N),
  age = round(rnorm(N, 35, 10)),
  female = draw_binary(prob = 0.52, N = N),
  noise = rnorm(N, sd = residual_sd),
  Y = 2.1 + 0.35 * treatment + 0.02 * age - 0.15 * female + noise
)
```

### From Odds Ratios (Logistic Regression)

```python
import numpy as np
from scipy.special import expit

np.random.seed(42)
N = 500

# Published: log-odds = -1.2 + 0.8*Treatment + 0.03*Age
treatment = np.random.binomial(1, 0.5, N)
age = np.random.normal(35, 10, N)

log_odds = -1.2 + 0.8 * treatment + 0.03 * age
prob = expit(log_odds)
outcome = np.random.binomial(1, prob)

print(f"Base rate: {outcome[treatment == 0].mean():.2%}")
print(f"Treatment rate: {outcome[treatment == 1].mean():.2%}")
```

---

## Matching Distributions (Skew and Kurtosis)

When the published paper reports non-normal distributions.

### Log-Normal (Income, Reaction Times)

```r
# Target: mean = 52000, SD = 18000, right-skewed
# Log-normal parameters from moments:
target_mean <- 52000
target_sd <- 18000
sigma2 <- log(1 + (target_sd / target_mean)^2)
mu <- log(target_mean) - sigma2 / 2

income <- rlnorm(500, meanlog = mu, sdlog = sqrt(sigma2))
cat("Mean:", mean(income), "SD:", sd(income), "\n")
```

### Beta (Proportions, Bounded Scales)

```python
import numpy as np

# Target: mean = 0.65, SD = 0.15, bounded [0, 1]
target_mean = 0.65
target_sd = 0.15

# Beta parameters from moments
alpha = target_mean * (target_mean * (1 - target_mean) / target_sd**2 - 1)
beta = (1 - target_mean) * (target_mean * (1 - target_mean) / target_sd**2 - 1)

scores = np.random.beta(alpha, beta, 500)
print(f"Mean: {scores.mean():.3f}, SD: {scores.std():.3f}")
```

### Johnson SU (Matching Arbitrary Skew and Kurtosis)

```python
from scipy import stats

# Target: mean = 50, SD = 10, skew = 1.2, kurtosis = 4.5
# Use Johnson SU distribution
a, b, loc, scale = stats.johnsonsu.fit(
    stats.johnsonsu.rvs(1.2, 1.5, size=10000),
    floc=50, fscale=10
)
data = stats.johnsonsu.rvs(a, b, loc=loc, scale=scale, size=500)
print(f"Skew: {stats.skew(data):.2f}, Kurtosis: {stats.kurtosis(data):.2f}")
```

---

## Matching Missing Data Rates

### MCAR (Missing Completely at Random)

```r
add_mcar <- function(df, columns, rate = 0.05) {
  for (col in columns) {
    mask <- runif(nrow(df)) < rate
    df[[col]][mask] <- NA
  }
  df
}
```

### MAR (Missing at Random)

```python
def add_mar(df, target_col, predictor_col, base_rate=0.05, effect=0.03):
    """Missingness in target_col depends on predictor_col."""
    from scipy.special import expit
    log_odds = np.log(base_rate / (1 - base_rate)) + effect * df[predictor_col]
    prob_missing = expit(log_odds)
    mask = np.random.random(len(df)) < prob_missing
    df.loc[mask, target_col] = np.nan
    return df

# Example: older respondents more likely to have missing trust scores
df = add_mar(df, "trust_score", "age", base_rate=0.08, effect=0.02)
```

### Matching Published Rates

```r
# From paper: "12% of trust scores were missing, 8% of satisfaction"
missing_rates <- list(trust = 0.12, satisfaction = 0.08)

for (var in names(missing_rates)) {
  mask <- runif(nrow(df)) < missing_rates[[var]]
  df[[var]][mask] <- NA
}

# Verify
sapply(df[names(missing_rates)], function(x) mean(is.na(x)))
```

---

## Common Calibration Targets by Field

### Psychology / Behavioural Science

| Parameter | Typical value | Source |
|-----------|--------------|-------|
| Treatment effect (d) | 0.20-0.50 | Open Science Collaboration (2015) |
| Likert means | 3.5-5.0 on 7-point scales | Varies by construct |
| Likert SDs | 0.8-1.5 | Varies by construct |
| Scale reliability (alpha) | 0.70-0.90 | Target > 0.70 |
| Attention check pass rate | 85-95% | Meade & Craig (2012) |
| Survey completion rate | 70-90% | Platform dependent |
| Median response time | 5-15 minutes | Survey length dependent |
| Inter-item correlation | 0.30-0.60 | Within validated scales |

### Economics / Policy Evaluation

| Parameter | Typical value | Source |
|-----------|--------------|-------|
| Treatment effect (d) | 0.05-0.30 | Smaller than psychology |
| Program effect (% change) | 2-15% | Development economics |
| ICC for cluster designs | 0.01-0.15 | Varies by level |
| Panel attrition rate | 5-20% per wave | Survey dependent |
| Income: mean/SD ratio | ~0.5-0.8 | Right-skewed |
| Regression R-squared | 0.10-0.40 | Cross-sectional individual |
| Regression R-squared (panel FE) | 0.40-0.80 | Within-unit variation |

### Management / Organisational Behaviour

| Parameter | Typical value | Source |
|-----------|--------------|-------|
| Survey response rate | 30-60% | Baruch & Holtom (2008) |
| Effect sizes (d) | 0.15-0.40 | Bosco et al. (2015) |
| Team-level ICC | 0.05-0.25 | Bliese (2000) |
| Scale means (5-point) | 2.8-4.0 | Avoid ceiling/floor |
| Common method variance | 10-25% of variance | Podsakoff et al. (2003) |
| Job satisfaction mean | 3.5-4.0 (5-point) | Judge et al. (2001) |
| Turnover intention mean | 2.0-3.0 (5-point) | Lower is typical |

---

## Validation: Comparing Synthetic vs. Target

After generating calibrated data, validate the match.

### Validation Checklist

| Check | Acceptable tolerance | Method |
|-------|---------------------|--------|
| Means | Within 2% of target | `abs(achieved - target) / target < 0.02` |
| SDs | Within 5% of target | `abs(achieved - target) / target < 0.05` |
| Correlations | Within 0.05 of target | `abs(achieved_r - target_r) < 0.05` |
| Proportions (binary) | Within 3 pp of target | `abs(achieved_p - target_p) < 0.03` |
| Skewness | Within 0.3 of target | `abs(achieved_skew - target_skew) < 0.3` |
| Effect sizes | Within 10% of target | `abs(achieved_d - target_d) / target_d < 0.10` |

### Validation Script Template

```r
validate_calibration <- function(synthetic, targets) {
  results <- data.frame(
    variable = names(targets$means),
    target_mean = targets$means,
    achieved_mean = colMeans(synthetic[names(targets$means)], na.rm = TRUE),
    target_sd = targets$sds,
    achieved_sd = sapply(synthetic[names(targets$means)], sd, na.rm = TRUE)
  )

  results$mean_pct_diff <- abs(results$achieved_mean - results$target_mean) /
                           abs(results$target_mean) * 100
  results$sd_pct_diff <- abs(results$achieved_sd - results$target_sd) /
                         results$target_sd * 100
  results$mean_ok <- results$mean_pct_diff < 2
  results$sd_ok <- results$sd_pct_diff < 5

  cat("=== Calibration Validation ===\n")
  print(results, digits = 3)

  if (all(results$mean_ok & results$sd_ok)) {
    cat("\nAll checks PASSED.\n")
  } else {
    cat("\nWARNING: Some checks FAILED. Review discrepancies.\n")
  }

  # Correlation check (if target provided)
  if (!is.null(targets$cor_matrix)) {
    achieved_cor <- cor(synthetic[names(targets$means)], use = "pairwise.complete.obs")
    cor_diff <- abs(achieved_cor - targets$cor_matrix)
    max_diff <- max(cor_diff[upper.tri(cor_diff)])
    cat("\nMax correlation discrepancy:", round(max_diff, 4), "\n")
    if (max_diff > 0.05) cat("WARNING: Correlation mismatch exceeds tolerance.\n")
  }

  invisible(results)
}
```

```python
import pandas as pd
import numpy as np

def validate_calibration(synthetic_df, targets):
    """
    targets: dict with keys 'means', 'sds', 'cor_matrix' (optional)
    Each is a dict mapping variable name -> target value.
    """
    results = []
    for var in targets["means"]:
        achieved_mean = synthetic_df[var].mean()
        achieved_sd = synthetic_df[var].std()
        target_mean = targets["means"][var]
        target_sd = targets["sds"][var]

        mean_pct = abs(achieved_mean - target_mean) / abs(target_mean) * 100
        sd_pct = abs(achieved_sd - target_sd) / target_sd * 100

        results.append({
            "variable": var,
            "target_mean": target_mean,
            "achieved_mean": round(achieved_mean, 3),
            "mean_%_diff": round(mean_pct, 2),
            "mean_ok": mean_pct < 2,
            "target_sd": target_sd,
            "achieved_sd": round(achieved_sd, 3),
            "sd_%_diff": round(sd_pct, 2),
            "sd_ok": sd_pct < 5,
        })

    report = pd.DataFrame(results)
    print("=== Calibration Validation ===")
    print(report.to_string(index=False))

    if report["mean_ok"].all() and report["sd_ok"].all():
        print("\nAll checks PASSED.")
    else:
        print("\nWARNING: Some checks FAILED.")

    return report
```

---

## Increasing Sample Size for Better Calibration

Small samples have higher sampling variability, so calibration tolerances should adjust:

| N | Expected mean error | Expected correlation error |
|---|--------------------|-----------------------------|
| 100 | ~5% | ~0.10 |
| 500 | ~2% | ~0.05 |
| 1000 | ~1.5% | ~0.03 |
| 5000 | ~0.7% | ~0.015 |

For tight calibration (< 1% mean error), generate N >= 2000 or use post-hoc reweighting.
