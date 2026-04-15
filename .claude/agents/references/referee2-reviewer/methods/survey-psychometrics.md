# Survey / Psychometrics Checklist

> Load when the paper uses: surveys, questionnaires, psychometric scales, Likert items, structural equation modelling, factor analysis, or self-report measures.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **Common method variance** | Single source, single method, single time point? All data from one survey with same response format? | Major — systematic inflation of correlations |
| **Unvalidated scales** | Ad hoc measures without psychometric validation? Existing validated scales available but not used? | Major |
| **Convenience samples claimed representative** | MTurk/Prolific/student samples claimed to generalise to a population? | Major if generalisability is claimed |
| **Missing reliability** | No Cronbach's alpha, McDonald's omega, or test-retest reported for multi-item scales? | Major |

## Standard Checks

### Measurement
- [ ] Scales identified (validated instruments with citations, or new scales)
- [ ] Reliability reported (alpha >= 0.7, or omega for multidimensional)
- [ ] Validity evidence provided (convergent, discriminant, criterion)
- [ ] Factor structure confirmed (CFA/EFA results match theoretical structure)
- [ ] Measurement invariance tested if comparing groups
- [ ] Response format appropriate (number of points, labelling)

### Sampling
- [ ] Sampling strategy described (probability, convenience, quota, snowball)
- [ ] Population of interest defined
- [ ] Sample representativeness assessed (compare demographics to population)
- [ ] Sample size justified (power analysis or rules of thumb for SEM)
- [ ] Response rate reported (for non-panel samples)
- [ ] Non-response bias assessed

### Survey Design
- [ ] Question wording provided (at minimum for key constructs)
- [ ] Item order effects considered (randomisation, blocks)
- [ ] Attention checks included
- [ ] Social desirability bias addressed (if sensitive topics)
- [ ] Survey length and completion time reported
- [ ] Pilot testing described

### Analysis
- [ ] Missing data mechanism assessed (MCAR, MAR, MNAR)
- [ ] Missing data handling described (listwise deletion, MI, FIML)
- [ ] Multicollinearity checks for regression-based analyses
- [ ] Appropriate estimator for data type (ordinal data needs WLSMV, not ML)
- [ ] SEM fit indices reported (CFI, TLI, RMSEA, SRMR — thresholds stated)
- [ ] Mediation analysis uses modern methods (bootstrap CI, not Baron-Kenny steps)

### Common Method Bias Remedies
If common method variance is a risk, look for at least one remedy:
- [ ] Temporal separation (DV measured at different time)
- [ ] Different sources (supervisor ratings, archival data alongside self-report)
- [ ] Procedural remedies (randomised item order, different response scales)
- [ ] Statistical remedies (Harman's single-factor test — weak; marker variable — better)

## Common Mistakes to Flag

1. Using Cronbach's alpha for scales with fewer than 4 items (use Spearman-Brown or omega)
2. Factor analysing a scale and then using item-level regression (circular)
3. Ignoring ceiling/floor effects in bounded scales
4. Treating ordinal Likert items as continuous without justification
5. Mediation with cross-sectional data and no temporal precedence
6. Claiming "no common method bias" from Harman's test alone (insufficient)

## Probing Questions

See `skills/shared/method-probing-questions.md` — section: Survey / Psychometrics.
