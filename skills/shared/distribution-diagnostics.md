# Distribution Diagnostics Before Model Selection

> Shared reference for `/data-analysis` and review agents. Mandatory checks on dependent variables before selecting a statistical model. Prevents misspecification. Adapted from CommDAAF AgentAcademy protocol (Xu 2026).

## Principle

**Never run a regression without inspecting the DV distribution first.** OLS on count data, Poisson on overdispersed data, and linear models on zero-inflated outcomes all produce misleading results. Five minutes of diagnostics prevents weeks of wasted analysis.

---

## Mandatory Checks

Run these on every dependent variable before model selection:

| Diagnostic | What to compute | Why it matters |
|-----------|----------------|----------------|
| **Basic stats** | N, mean, median, SD, range | Understand the variable |
| **Skewness** | `scipy.stats.skew(y)` or `moments::skewness(y)` | \|skew\| > 1 → OLS assumptions likely violated |
| **Zero proportion** | `sum(y == 0) / N` | > 15% zeros → consider zero-inflated or hurdle models |
| **Overdispersion** | `var(y) / mean(y)` | > 1.5 → Poisson is wrong, use Negative Binomial |
| **Normality** | QQ-plot + Shapiro-Wilk (if N < 5000) | Formal test, but visual inspection matters more |
| **Outliers** | IQR method or robust Mahalanobis distance | Extreme values can dominate OLS estimates |

---

## Model Selection Decision Tree

```
Is the DV a count (0, 1, 2, ...)?
├── Yes → Check overdispersion (var/mean > 1.5?)
│   ├── Yes → Check zero proportion (> 30%?)
│   │   ├── Yes → Zero-inflated NB or Hurdle model
│   │   └── No  → Negative Binomial
│   └── No → Check zero proportion (> 30%?)
│       ├── Yes → Zero-inflated Poisson
│       └── No  → Poisson
├── Is the DV a proportion or bounded [0, 1]?
│   └── Yes → Beta regression (or fractional logit)
├── Is the DV binary (0/1)?
│   └── Yes → Logistic regression
├── Is the DV ordinal (ordered categories)?
│   └── Yes → Ordered logistic/probit
└── Is the DV continuous?
    └── Check skewness and normality of residuals
        ├── Residuals ~normal → OLS
        ├── Highly skewed DV → Log-transform, then OLS (report both)
        └── Heavy tails → Robust regression or quantile regression
```

**Key rule:** Never use OLS on raw counts without explicit justification. Social media engagement, citation counts, survey response counts — these are almost never normally distributed.

---

## Effect Size Reporting

### For count models (NB, Poisson): report Incidence Rate Ratios (IRR)

| IRR | Interpretation |
|-----|---------------|
| 1.0 | No effect |
| 1.2 | 20% increase |
| 1.5 | 50% increase |
| 2.0 | Double |
| 0.5 | Half |

**Always translate to practical meaning:** "Posts with frame X received 50% more engagement (IRR = 1.50, 95% CI [1.22, 1.84])" — not just "β = 0.41, p < 0.01".

### For OLS: report standardised coefficients alongside raw

Help readers judge magnitude, not just significance.

### For logistic: report odds ratios AND predicted probabilities

Odds ratios are hard to interpret. Show predicted probability at meaningful values of the IV.

---

## Multiple Testing

When testing multiple predictors or outcomes:

| Method | When to use |
|--------|------------|
| **Bonferroni** | Conservative; few tests (< 10) |
| **Holm** | Less conservative; sequential rejection |
| **FDR (Benjamini-Hochberg)** | Many tests (> 10); controls false discovery rate |

**Always report both raw and adjusted p-values.** Let readers assess.

---

## Implementation

### Python

```python
import numpy as np
from scipy import stats

def distribution_diagnostics(y, name="DV"):
    """Run mandatory diagnostics before model selection."""
    n = len(y)
    skewness = stats.skew(y)
    pct_zeros = np.sum(y == 0) / n * 100
    var_mean = np.var(y) / np.mean(y) if np.mean(y) > 0 else float('inf')

    diagnostics = {
        'n': n, 'mean': np.mean(y), 'median': np.median(y),
        'sd': np.std(y), 'skewness': skewness,
        'pct_zeros': pct_zeros, 'var_mean_ratio': var_mean,
    }

    # Model recommendation
    if pct_zeros > 30:
        diagnostics['recommendation'] = 'Zero-inflated model or Hurdle'
    elif var_mean > 1.5:
        diagnostics['recommendation'] = 'Negative Binomial'
    elif abs(skewness) > 1:
        diagnostics['recommendation'] = 'Log-transform or GLM'
    else:
        diagnostics['recommendation'] = 'OLS (verify residuals)'

    return diagnostics
```

### R

```r
distribution_diagnostics <- function(y, name = "DV") {
  n <- length(y)
  skew <- moments::skewness(y)
  pct_zeros <- sum(y == 0) / n * 100
  var_mean <- var(y) / mean(y)

  cat(sprintf("=== %s (N=%d) ===\n", name, n))
  cat(sprintf("Mean: %.3f | Median: %.3f | SD: %.3f\n", mean(y), median(y), sd(y)))
  cat(sprintf("Skewness: %.3f | Zeros: %.1f%% | Var/Mean: %.3f\n", skew, pct_zeros, var_mean))

  if (pct_zeros > 30) cat("→ Zero-inflated or Hurdle model\n")
  else if (var_mean > 1.5) cat("→ Negative Binomial\n")
  else if (abs(skew) > 1) cat("→ Log-transform or GLM\n")
  else cat("→ OLS (verify residuals)\n")
}
```

---

## Integration

### In `/data-analysis` Phase 1 (EDA)

Run `distribution_diagnostics()` on every DV and key IVs before proceeding to estimation. If the diagnostics suggest a non-OLS model, flag this before the user locks their specification.

### In review agents

Check whether the paper reports distribution diagnostics or justifies model choice. A paper using OLS on count data without justification → flag as Major issue.

### Validation tier interaction

| Tier | Requirement |
|------|------------|
| 🟢 Exploratory | Run diagnostics, note recommendation |
| 🟡 Pilot | Run diagnostics, justify model choice in notes |
| 🔴 Publication | Run diagnostics, report in paper, compare 2+ model families |
