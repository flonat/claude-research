# Content Analysis / Qualitative Coding Checklist

> Load when the paper uses: manual coding, content analysis, qualitative analysis, thematic analysis, discourse analysis, or mixed-methods with a coding component.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **No codebook** | Coding without a pre-defined codebook? Categories emerged "during analysis" with no systematic process? | Critical |
| **No inter-coder reliability** | Single coder with no reliability assessment? | Critical for quantitative content analysis |
| **Below-threshold reliability** | Fleiss' kappa or Krippendorff's alpha < 0.67? | Major (< 0.67 is tentative; < 0.41 is poor) |
| **Category-level reliability missing** | Only aggregate reliability reported, not per-category? Some categories may be unreliable | Major |

## Standard Checks

### Codebook
- [ ] Codebook exists and is described (categories, definitions, examples)
- [ ] Codebook development process described (deductive from theory? inductive from data? hybrid?)
- [ ] Categories are mutually exclusive and exhaustive (or coding rules for overlap stated)
- [ ] Decision rules for ambiguous cases documented

### Sampling
- [ ] Sampling frame defined (what content, from where, what time period)
- [ ] Sampling strategy justified (census, random, stratified, purposive)
- [ ] Sample size adequate for the claims being made
- [ ] Unit of analysis defined (post, article, paragraph, utterance)

### Coding Process
- [ ] Number of coders stated
- [ ] Coder training described
- [ ] Pilot coding with reliability assessment before full coding
- [ ] Disagreement resolution process described
- [ ] Coding was independent (coders didn't discuss during coding)

### Reliability
- [ ] Reliability metric appropriate (Cohen's kappa for 2 coders, Fleiss' kappa or Krippendorff's alpha for 3+)
- [ ] Per-category reliability reported (not just aggregate)
- [ ] Reliability thresholds stated and justified
- [ ] Reliability sample size adequate (10-25% of full sample)
- [ ] If using automated coding (LLM, dictionary): validated against human gold standard

### Analysis
- [ ] Descriptive results (frequencies, distributions) before inferential
- [ ] If using coded data in regression: measurement error from coding acknowledged
- [ ] Qualitative findings illustrated with representative quotes
- [ ] Negative cases or disconfirming evidence discussed

## Reliability Thresholds

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Cohen's/Fleiss' kappa | > 0.80 | 0.67-0.80 | 0.41-0.67 | < 0.41 |
| Krippendorff's alpha | > 0.80 | 0.67-0.80 | tentative | < 0.67 |
| Percent agreement | Not recommended as sole metric — inflated by chance agreement | | | |

## Common Mistakes to Flag

1. Reporting only percent agreement (ignores chance agreement)
2. Single coder claiming "reliability was ensured by..."  — reliability requires multiple coders
3. Post-hoc codebook revision without re-coding earlier material
4. Convenience quotes that only support the argument (no negative cases)
5. Treating qualitative themes as quantitative variables without proper operationalisation
6. Using LLM annotations without human validation (N >= 200, kappa >= 0.7)

## Related Shared References

- Inter-coder reliability details: `skills/shared/intercoder-reliability.md`

## Probing Questions

See `skills/shared/method-probing-questions.md` — section: Content Analysis / Coding.
