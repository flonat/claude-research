# Design Decision Tree

> Walk through these questions to select the strongest identification strategy for your research setting.
> Read during `/causal-design` Design Phase 2.

---

## Decision Tree

Start at Question 1. Follow the arrows.

### Q1: Do you assign treatment?

- **Yes** -- you control the assignment mechanism
  - **Random assignment?** --> **RCT** (use `/experiment-design`, not `/causal-design`)
  - **Non-random assignment but you control it?** --> Consider a designed quasi-experiment, continue to Q2
- **No** -- treatment is observational --> Continue to Q2

### Q2: Is there a threshold or cutoff that determines treatment?

- **Yes** -- a score, index, or running variable determines treatment eligibility at a known cutoff
  - **Sharp cutoff** (everyone above/below is treated) --> **Sharp RDD**
  - **Fuzzy cutoff** (treatment probability jumps but not from 0 to 1) --> **Fuzzy RDD**
  - **Geographic boundary** --> **Geographic RDD** (spatial discontinuity)
- **No** --> Continue to Q3

### Q3: Does treatment status change over time?

- **Yes** -- some units get treated at different times, others do not
  - **Treatment is absorbing** (once treated, always treated)?
    - **Multiple treated units, staggered adoption?** --> **Staggered DiD** (use Callaway-Sant'Anna or Sun-Abraham, NOT TWFE)
    - **Single treatment date, treated vs. untreated groups?** --> **Standard DiD** / **Event Study**
    - **One treated unit, many controls?** --> **Synthetic Control**
  - **Treatment switches on and off?** --> **Two-way fixed effects** (with caution) or **de Chaisemartin-D'Haultfoeuille**
- **No** -- treatment is cross-sectional --> Continue to Q4

### Q4: Do you have an instrument?

An instrument is a variable that:
1. Affects treatment (relevance)
2. Affects the outcome ONLY through treatment (exclusion restriction)
3. Is as good as randomly assigned (independence)

- **Yes** -- you can make a credible case for all three conditions --> **IV / 2SLS**
- **Maybe** -- you have a candidate but exclusion is questionable --> Flag as weak identification; consider IV as a complement to another strategy
- **No** --> Continue to Q5

### Q5: Can you credibly argue selection on observables?

- **Yes** -- you believe all confounders are observed and measured
  - **Rich covariate data available?** --> **Matching / IPW / Doubly Robust**
  - **But be honest:** This is the weakest strategy. It requires that NO unobserved confounder exists. Sensitivity analysis (Rosenbaum bounds, E-values) is mandatory.
- **No** --> **No credible identification strategy available.** Do not proceed with causal claims. Options:
  - Reframe as descriptive/predictive analysis
  - Search harder for an instrument or natural experiment
  - Consider a different research question where identification is feasible

---

## Strategy Comparison Matrix

| Strategy | Estimand | Key Assumption | Testable? | Strength | Common Pitfalls |
|----------|----------|----------------|-----------|----------|-----------------|
| **RCT** | ATE | Random assignment + SUTVA | Yes (balance tests) | Gold standard | Non-compliance, attrition, external validity |
| **Sharp RDD** | LATE at cutoff | Continuity of potential outcomes at cutoff | Partially (McCrary, balance) | Very strong | Manipulation, limited external validity, bandwidth choice |
| **Fuzzy RDD** | LATE for compliers at cutoff | Continuity + monotonicity | Partially | Strong | Weak first stage near cutoff, donut hole needed |
| **Standard DiD** | ATT | Parallel trends | Partially (pre-trends) | Strong if pre-trends hold | Differential trends, composition changes, anticipation |
| **Staggered DiD** | Group-time ATT | Parallel trends (dynamic) | Partially (pre-trends) | Strong if done correctly | TWFE bias, negative weights, heterogeneous effects |
| **Event Study** | Dynamic ATT | Parallel trends + no anticipation | Partially (pre-event coefficients) | Strong | Pre-trends contamination, binning endpoints, clean controls |
| **Synthetic Control** | ATT for treated unit | Pre-treatment fit = counterfactual fit | Partially (pre-fit, placebos) | Strong for single-unit | Small donor pools, poor pre-fit, interpolation bias |
| **IV / 2SLS** | LATE for compliers | Exclusion, relevance, independence, monotonicity | Partially (first stage) | Moderate-strong | Weak instruments, exclusion violations, monotonicity failures |
| **Matching / IPW** | ATE or ATT | CIA (no unobserved confounders) | No (sensitivity only) | Weak | Unmeasured confounding, poor overlap, model dependence |

---

## Strength Hierarchy

From strongest to weakest identification (holding quality of execution constant):

1. **RCT** -- randomisation solves selection by design
2. **RDD** -- local randomisation near cutoff; highly credible when manipulation is ruled out
3. **DiD / Event Study** -- credible when parallel trends are supported by pre-treatment data
4. **Synthetic Control** -- credible for single-unit studies with strong pre-treatment fit
5. **IV** -- credible when exclusion restriction has a strong institutional argument
6. **Matching / Selection on Observables** -- weakest; requires heroic assumption of no unmeasured confounders

This hierarchy is a starting point, not dogma. A well-executed IV with a compelling instrument is more credible than a poorly executed DiD with failing pre-trends.

---

## Combination Strategies

Some research settings support combining strategies for stronger identification:

| Combination | When to use | Example |
|-------------|-------------|---------|
| **DiD + Matching** | Improve parallel trends by matching on pre-treatment covariates | Match treated/control firms on industry and size, then estimate DiD |
| **IV + DiD** | Use DiD to address time-invariant confounders, IV for time-varying | Policy instrument interacted with pre/post |
| **RDD + DiD** | Combine spatial discontinuity with temporal variation | Border discontinuity with policy change over time |
| **SC + Event Study** | Synthetic control for aggregate effect, event study for dynamics | Single treated state, event study for timing |
| **IV + RDD** | Fuzzy RDD is essentially IV at the cutoff | Eligibility threshold with imperfect compliance |

---

## Red Flags by Strategy

### DiD Red Flags
- Pre-treatment trends are not parallel (the test fails and the paper ignores it)
- TWFE used with staggered adoption and heterogeneous effects
- Treatment and control groups differ on observables at baseline with no discussion
- Only 2 time periods (no pre-trends test possible)
- Treated group is trending differently before treatment for obvious reasons

### IV Red Flags
- First-stage F < 10 (or < 104.7 by Lee et al. 2022 standards)
- Exclusion restriction defended only by "it is plausible" without institutional detail
- The instrument is a lagged dependent variable or a "generated" instrument
- Reduced form is not reported (hiding what the instrument actually predicts)
- Multiple instruments used without over-identification test

### RDD Red Flags
- Running variable is self-reported or manipulable
- Global polynomial of degree 3+ used instead of local linear
- Only one bandwidth reported with no sensitivity analysis
- McCrary test not conducted or shows bunching
- Treatment effect only appears with a very narrow bandwidth

### SC Red Flags
- Poor pre-treatment fit (RMSPE is large relative to outcome variation)
- Donor pool was pruned to improve fit without justification
- No placebo tests (in-space or in-time)
- Treated unit is an extreme outlier on the outcome
- Very few donor units available (< 10)

### Matching Red Flags
- No sensitivity analysis for unmeasured confounding
- Balance table shows residual imbalance on key covariates (SMD > 0.1)
- Common support is poor (many treated units have no comparable controls)
- "Matching" is just adding controls to OLS without checking overlap
- CIA is asserted without discussion of what unobservables could confound

---

## Key References

| Strategy | Seminal reference | Modern methods |
|----------|------------------|----------------|
| DiD | Ashenfelter & Card (1985) | Callaway & Sant'Anna (2021), Sun & Abraham (2021), de Chaisemartin & D'Haultfoeuille (2020) |
| RDD | Thistlethwaite & Campbell (1960) | Calonico, Cattaneo & Titiunik (2014), Cattaneo, Idrobo & Titiunik (2020) |
| IV | Angrist & Krueger (1991) | Andrews, Stock & Sun (2019), Lee et al. (2022) |
| SC | Abadie, Diamond & Hainmueller (2010) | Abadie (2021), Arkhangelsky et al. (2021) |
| Matching | Rosenbaum & Rubin (1983) | Imbens (2015), King & Nielsen (2019) |
| Event Study | Jacobson, LaLonde & Sullivan (1993) | Borusyak, Jaravel & Spiess (2024), Roth (2022) |

---

## Cross-References

| Resource | Relationship |
|----------|-------------|
| `/causal-design` SKILL.md | Parent skill -- this tree is read during Design Phase 2 |
| `experiment-design/references/identification-strategies.md` | Overlapping content for experimental settings |
| `/data-analysis` references/estimation-recipes.md | Implementation recipes for each strategy |
| `design-before-results` rule | Strategy must be selected before examining results |
