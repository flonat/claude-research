# Identification Strategies Reference

> Quick-reference for identification approaches in experimental and quasi-experimental designs.
> Read during Design mode of `/experiment-design`. For full causal design workflows, see `/causal-design`.

## Strategy Selection Guide

| Your setting | Best strategy | Key assumption |
|-------------|---------------|----------------|
| You assign treatment randomly | RCT | SUTVA, compliance |
| Treatment assigned at a threshold | RDD | Continuity at cutoff |
| Treatment rolls out over time to different groups | Staggered DiD | Parallel trends (dynamic) |
| Treatment happens to all at once vs. a comparison | Standard DiD | Parallel trends |
| You have an instrument for treatment | IV | Exclusion restriction, relevance |
| One unit gets treated, many don't | Synthetic control | Pre-treatment fit |
| Observational, selection on observables only | Matching / IPW | CIA / unconfoundedness |

## For Experiments (RCTs)

### Estimand
$$\tau_{ATE} = E[Y_i(1) - Y_i(0)]$$

### Key Assumptions
1. **SUTVA:** No interference between units; no hidden versions of treatment
2. **Random assignment:** $T_i \perp (Y_i(0), Y_i(1))$
3. **Compliance:** Perfect compliance (ITT = ATE) or instrument for LATE

### Threats to Flag
- Non-compliance → estimate ITT and LATE separately
- Attrition → bounds analysis (Lee bounds)
- Spillovers → design-based prevention (cluster randomization)
- Hawthorne effects → behavioural placebo control
- Experimenter demand → double-blind, implicit measures

### Design Choices
| Choice | Options | When |
|--------|---------|------|
| Assignment | Complete, block, cluster, stratified | Always specify |
| Blocking | Pre-stratify on key covariates | When baseline data available |
| Clustering | Cluster-randomize | When spillovers within clusters |
| Factorial | Cross treatments | When studying interactions |

## For Quasi-Experiments

### Difference-in-Differences
- **Estimand:** ATT under parallel trends
- **Key test:** Pre-treatment trends plot + joint test of pre-period coefficients
- **Modern methods:** Callaway & Sant'Anna (2021), Sun & Abraham (2021) for staggered adoption
- **Red flag:** If pre-trends are not parallel, DiD is not credible

### Regression Discontinuity
- **Estimand:** LATE at the cutoff
- **Key tests:** McCrary density test (no bunching), covariate balance at cutoff
- **Bandwidth:** Use MSE-optimal (rdrobust default), report sensitivity
- **Red flag:** Manipulation of the running variable

### Instrumental Variables
- **Estimand:** LATE for compliers
- **Key tests:** First-stage F > 10 (Stock-Yogo), exclusion restriction (argue, can't test)
- **Red flag:** Weak instruments, plausible violations of exclusion

## Reporting Checklist

Every design document should state:

1. **Estimand:** What causal parameter are we estimating?
2. **Identification:** What assumption(s) make the estimate causal?
3. **Threats:** What could violate the assumptions?
4. **Diagnostics:** How will we test (where possible) the assumptions?
5. **Robustness:** What alternative specifications will we run?
