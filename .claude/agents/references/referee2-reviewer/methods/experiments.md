# Experiments / RCTs Checklist

> Load when the paper uses: lab experiments, field experiments, RCTs, online experiments (MTurk, Prolific), survey experiments, or A/B tests.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **Underpowered study** | Power analysis reported? Sample size justified? Small N with large effects is suspicious — demand power calculation | Critical if N < 100 per cell without justification |
| **Multiple testing** | How many outcomes tested? Any correction (Bonferroni, Holm, BH/FDR)? | Critical if 5+ outcomes without correction |
| **Demand effects** | Can participants guess the hypothesis? Are there manipulation checks that reveal the hypothesis? | Major — often underappreciated |
| **Post-hoc hypotheses** | Was the experiment pre-registered? Deviations from the pre-analysis plan? | Major if unregistered with surprising results |

## Standard Checks

### Design
- [ ] Randomisation unit clearly stated (individual, cluster, stratified)
- [ ] Randomisation procedure described (how, by whom, when)
- [ ] Treatment and control conditions clearly described
- [ ] Blinding — single, double, or none? Justified?
- [ ] Consent and ethics approval documented

### Pre-Registration
- [ ] Pre-registration exists (AsPredicted, OSF, AEA RCT Registry)
- [ ] Deviations from pre-registered plan documented and justified
- [ ] Primary vs exploratory analyses clearly distinguished
- [ ] Pre-registered sample size matches actual sample

### Attrition and Compliance
- [ ] Attrition rates reported by condition
- [ ] Differential attrition tested (is attrition correlated with treatment?)
- [ ] ITT and LATE/TOT both reported if non-compliance exists
- [ ] Bounds on treatment effects under worst-case attrition (Lee bounds)

### Analysis
- [ ] Balance table (Table 1) shows pre-treatment covariates by condition
- [ ] Randomisation inference or conventional tests appropriate for design
- [ ] Clustered SEs if randomisation was at cluster level
- [ ] Covariates in regression justified (pre-specified? ANCOVA-motivated?)

### Effect Sizes
- [ ] Effect sizes reported in interpretable units (not just standardised)
- [ ] Comparison to existing literature benchmarks
- [ ] Minimum detectable effect size stated
- [ ] Economic/practical significance discussed (not just statistical)

## Common Mistakes to Flag

1. Claiming "no effect" from a null result without reporting power
2. Multiple outcome variables without correction — guaranteed false positives
3. Dropping participants post-randomisation without attrition analysis
4. Using observational language ("participants who chose X") when describing random assignment
5. Inflated effects from small samples (winner's curse)
6. Vague manipulation descriptions that prevent replication

## Probing Questions

See `skills/shared/method-probing-questions.md` — section: Experiments / RCTs.
