# Cross-Cutting Methodology Checks

> Always loaded regardless of paradigm. These apply to every empirical paper.

## Causal Language Audit

**Scan every instance** of these linguistic markers:
- Causal verbs: `causes`, `leads to`, `drives`, `determines`, `results in`, `produces`, `generates`, `triggers`
- Causal prepositions: `because of`, `due to`, `as a result of`, `owing to`
- Effect language: `the effect of`, `the impact of`, `the causal effect`
- Mechanism claims: `through`, `via`, `the channel is`, `the mechanism is`, `works by`

For each instance, **quote the exact sentence** and state whether the identification strategy justifies the causal language. Flag unhedged causal claims without credible design as Major; systematic overclaiming is Critical.

## Mechanism Claims

If the paper claims X works "through" or "via" a mechanism, demand:
- Formal mediation analysis, OR
- At minimum suggestive evidence (heterogeneity, placebo, mechanism-specific outcome)

**Quote the exact mechanism claim** and specify what test is missing. Vague mechanism stories without empirical support are a Major concern.

## Hedging Failures

Claims stated as fact that should be hedged:
- "our results show" when the design only supports "our results are consistent with"
- "we find that X causes Y" in an observational study
- "the effect is" when the estimate could be biased

**Quote the exact sentence and the hedged alternative.** Systematic over-claiming is Critical.

## Other Universal Checks

| Check | What to look for | Severity if missing |
|-------|-----------------|-------------------|
| **p-hacking / specification searching** | Pre-registration? Robustness across specifications? How many outcomes tested? | Major |
| **Missing heterogeneity analysis** | Average effects can mask important variation. Are subgroup analyses reported? | Major (if theoretically motivated subgroups exist) |
| **Ecological fallacy** | Group-level findings claimed at individual level? | Critical if central to the argument |
| **External validity** | How generalizable? Sample representativeness discussed? | Major |
| **Replication concerns** | Code/data available? Seeds set? Analysis reproducible? | Major |
| **Claims-methods mismatch** | Are conclusions supported by the analytical approach used? | Critical if systematic |

## Related Shared References

- Probing questions for all methods: `skills/shared/method-probing-questions.md`
- Escalation protocol (when methodology is vague): `skills/shared/escalation-protocol.md`
- Validation tiers: `skills/shared/validation-tiers.md`
