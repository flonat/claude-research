# MCDM / Multi-Criteria Decision Making Checklist

> Load when the paper uses: AHP, TOPSIS, PROMETHEE, ELECTRE, VIKOR, MOORA, BWM, DEMATEL, ANP, or any multi-criteria decision analysis.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **Rank reversal** | Does adding/removing alternatives change the ranking of existing ones? (Known issue for AHP, TOPSIS) | Critical if not tested |
| **Weight sensitivity** | Do conclusions depend entirely on subjective weight choices? Small weight changes flip the ranking? | Critical if no sensitivity analysis |
| **Method selection unjustified** | Why this MCDM method and not another? Different methods can give different rankings for the same data | Major |
| **No comparison across methods** | Only one MCDM method applied without checking if results are robust to method choice | Major |

## Standard Checks

### Problem Formulation
- [ ] Decision problem clearly structured (goal, criteria, alternatives)
- [ ] Criteria independent (or correlation explicitly handled)
- [ ] Criteria exhaustive and non-redundant
- [ ] Alternatives are genuine options (not strawmen or foregone conclusions)
- [ ] Decision context specified (who decides, what stakes, what constraints)

### Weight Determination
- [ ] Weighting method stated (pairwise comparison, direct rating, BWM, equal, entropy, CRITIC)
- [ ] Number of decision-makers and their expertise
- [ ] Consistency check for pairwise comparisons (CR < 0.1 for AHP)
- [ ] Aggregation method for multiple decision-makers (geometric mean, voting)
- [ ] Subjective vs objective weights distinguished

### Sensitivity Analysis
- [ ] Weight sensitivity analysis performed (vary each criterion weight)
- [ ] Rank stability reported (at what weight change does the ranking flip?)
- [ ] Scenario analysis (optimistic, pessimistic, balanced weight sets)
- [ ] Sensitivity to normalisation method tested
- [ ] Cross-method validation (apply at least one alternative MCDM method)

### Data Quality
- [ ] Data sources for performance matrix documented
- [ ] Missing data in the performance matrix handled (how?)
- [ ] Normalisation method stated and justified (min-max, vector, sum)
- [ ] Benefit vs cost criteria correctly oriented
- [ ] Scale commensurability addressed

### Method-Specific Checks

**AHP:**
- [ ] Consistency ratio < 0.1 (Saaty threshold)
- [ ] Pairwise comparison matrices complete
- [ ] Rank reversal tested (open vs closed weight derivation)

**TOPSIS:**
- [ ] Distance metric specified (Euclidean standard, but alternatives exist)
- [ ] Ideal and anti-ideal solutions correctly identified
- [ ] Normalisation effect on results tested

**PROMETHEE:**
- [ ] Preference functions specified per criterion (Type I-VI)
- [ ] Thresholds (indifference, preference, Gaussian) justified
- [ ] PROMETHEE I (partial) vs II (complete) ranking — choice justified

**ELECTRE:**
- [ ] Concordance and discordance thresholds justified
- [ ] Veto thresholds set appropriately
- [ ] Outranking relation interpreted correctly

**BWM (Best-Worst Method):**
- [ ] Consistency ratio reported (should be near 0)
- [ ] Best and worst criteria selection justified
- [ ] Comparison to other weighting methods

## Common Mistakes to Flag

1. Presenting MCDM results as objective truth rather than structured subjective preference
2. No sensitivity analysis on weights — the ranking is meaningless without it
3. Applying a single method and treating the result as definitive
4. Ignoring rank reversal in methods known to be susceptible
5. Using AHP with more than 9 criteria without hierarchical decomposition
6. Treating MCDM ranking as causal evidence ("X is the best option because...")
7. Not reporting the full performance matrix (only showing final scores)

## Probing Questions

See `skills/shared/method-probing-questions.md` — section: MCDM / Multi-Criteria Analysis.
