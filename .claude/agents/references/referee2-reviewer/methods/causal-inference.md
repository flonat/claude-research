# Causal Inference / Econometrics Checklist

> Load when the paper uses: OLS with causal claims, IV, DiD, RDD, synthetic control, panel methods, or any quasi-experimental design.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **TWFE bias** | Staggered treatment timing? Heterogeneous treatment effects? If yes, TWFE is biased — demand Callaway-Sant'Anna, Sun-Abraham, de Chaisemartin-D'Haultfoeuille, or Borusyak-Jaravel-Spiess | Critical if staggered + TWFE used |
| **Weak instruments** | First-stage F-statistic reported? <10 is weak. Demand Anderson-Rubin confidence intervals, tF adjustment, or effective F-statistic | Critical if IV-based |
| **Bad controls** | Conditioning on post-treatment variables? Collider bias? Each control must be pre-determined or time-invariant | Critical if central controls are post-treatment |
| **Exclusion restriction** | For IV: is the theoretical argument for Z → Y only through X credible? What could violate it? | Critical — this is the identification |

## Standard Checks

### Difference-in-Differences
- [ ] Parallel trends evidence (visual + formal test)
- [ ] Pre-treatment dynamics plotted (event study)
- [ ] Anticipation effects considered
- [ ] Spillovers between treated and control units
- [ ] Appropriate estimator for staggered timing
- [ ] Clustering level justified (treatment assignment level)

### Instrumental Variables
- [ ] First-stage F-statistic reported and adequate
- [ ] Exclusion restriction argued (not just assumed)
- [ ] LATE interpretation provided (who are the compliers?)
- [ ] Over-identification test if multiple instruments
- [ ] Reduced form reported alongside 2SLS

### Regression Discontinuity
- [ ] Running variable and cutoff clearly defined
- [ ] Sharp vs fuzzy distinction made
- [ ] Bandwidth selection method stated (MSE-optimal preferred)
- [ ] McCrary manipulation test or density plot
- [ ] Sensitivity to polynomial order and bandwidth
- [ ] Donut hole robustness (exclude observations near cutoff)

### Panel / Fixed Effects
- [ ] Fixed effects justified (what variation is being used?)
- [ ] Time-varying confounders addressed
- [ ] Clustering appropriate for the design
- [ ] Within-variation sufficient (not just between)

### Synthetic Control
- [ ] Donor pool selection justified
- [ ] Pre-treatment fit quality reported
- [ ] Placebo tests (in-space, in-time)
- [ ] Sensitivity to donor pool composition

## Common Mistakes to Flag

1. Claiming "causal" results from OLS + controls without an identification strategy
2. Using significance stars as the primary evidence for causality
3. Reporting only the "preferred" specification without alternatives
4. Clustering standard errors at the wrong level
5. Ignoring treatment effect heterogeneity when theory predicts it
6. Conflating statistical significance with economic significance

## Probing Questions

See `skills/shared/method-probing-questions.md` — sections: Regression/OLS/Panel, Difference-in-Differences, Instrumental Variables, Regression Discontinuity.
