# Inter-Coder Reliability & LLM Annotation Validation

> Shared reference for content analysis, LLM annotation, and coding studies. Covers both human-coder and multi-model reliability assessment. Adapted from CommDAAF AgentAcademy protocol (Xu 2026).

## Principle

**Always report reliability per category, not just aggregate.** A global κ of 0.7 can hide the fact that one frame has κ = 0.3 — which means that frame's results are unreliable. Frame-specific (or category-specific) reliability is the minimum standard.

---

## When This Applies

- Any content analysis with 2+ coders (human or LLM)
- LLM annotation studies using multiple models
- Survey coding or qualitative coding with multiple raters
- Any study reporting inter-coder or inter-model agreement

---

## Metrics to Report

### For 2 coders

| Metric | When to use | Interpretation |
|--------|------------|----------------|
| **Cohen's κ** | Two coders, nominal categories | Chance-corrected agreement |
| **Weighted κ** | Two coders, ordinal categories | Accounts for degree of disagreement |
| **% Agreement** | Supplement only | Not chance-corrected; report alongside κ |

### For 3+ coders (including multi-model LLM)

| Metric | When to use | Interpretation |
|--------|------------|----------------|
| **Fleiss' κ** | 3+ coders, nominal categories | Multi-rater chance-corrected agreement |
| **Three-way agreement** | 3 models, quick check | Proportion where all 3 agree |
| **Majority agreement** | 3 models, voting | Proportion where ≥2/3 agree |
| **Pairwise κ** | 3+ coders, diagnostic | Which pairs agree/disagree |
| **Krippendorff's α** | Any number of coders, any scale | Most general; handles missing data |

---

## Thresholds

| κ range | Interpretation | Action |
|---------|---------------|--------|
| < 0.20 | Poor | Do not use this category. Redefine or merge. |
| 0.20–0.40 | Fair | Flag. Consider retraining or revising codebook. |
| 0.40–0.60 | Moderate | Acceptable for exploratory. Report limitation. |
| 0.60–0.80 | Substantial | Acceptable for publication. |
| > 0.80 | Excellent | Strong agreement. |

**Publication threshold:** κ ≥ 0.7 (or α ≥ 0.7 for Krippendorff's α).

**LLM annotation minimum:** Human validation sample N ≥ 200, κ ≥ 0.7 between LLM and human.

---

## Category-Specific Reliability

### Why aggregate isn't enough

```
Aggregate Fleiss' κ = 0.72  ← looks fine

Per-category:
  SOLIDARITY:    κ = 0.89  ✅
  INJUSTICE:     κ = 0.81  ✅
  MOBILISATION:  κ = 0.74  ✅
  HUMANITARIAN:  κ = 0.31  ⚠️  ← this category's results are unreliable
  CULTURAL:      κ = 0.65  ⚠️  ← borderline
```

If HUMANITARIAN has κ = 0.31, any finding about that category should be treated as exploratory regardless of the aggregate score.

### Implementation

```python
from sklearn.metrics import cohen_kappa_score
import itertools

def category_specific_reliability(coded_data, code_var='frame', coders=None):
    """
    Calculate reliability per category across all coders.

    coded_data: list of dicts, each with '{coder}_{code_var}' keys
    coders: list of coder names (e.g., ['claude', 'glm', 'kimi'] or ['coder1', 'coder2'])
    """
    # Collect all categories
    categories = set()
    for d in coded_data:
        for c in coders:
            categories.add(d.get(f'{c}_{code_var}'))

    results = {}
    for cat in categories:
        # For each item, create binary: did coder assign this category?
        binary_codes = {c: [] for c in coders}
        for d in coded_data:
            for c in coders:
                binary_codes[c].append(1 if d.get(f'{c}_{code_var}') == cat else 0)

        # Three-way agreement (for 3 coders)
        if len(coders) == 3:
            n_relevant = sum(1 for i in range(len(coded_data))
                           if any(binary_codes[c][i] for c in coders))
            if n_relevant < 5:
                results[cat] = {'n': n_relevant, 'kappa': None, 'flag': 'Too few cases'}
                continue

            three_way = sum(
                1 for i in range(len(coded_data))
                if all(binary_codes[c][i] == binary_codes[coders[0]][i] for c in coders)
                and any(binary_codes[c][i] for c in coders)
            ) / max(n_relevant, 1)

            results[cat] = {
                'n': n_relevant,
                'agreement': three_way,
                'flag': '✅' if three_way >= 0.6 else '⚠️ Low reliability'
            }

        # Pairwise kappa
        kappas = []
        for c1, c2 in itertools.combinations(coders, 2):
            try:
                k = cohen_kappa_score(binary_codes[c1], binary_codes[c2])
                kappas.append(k)
            except ValueError:
                pass

        if kappas:
            results[cat]['mean_pairwise_kappa'] = sum(kappas) / len(kappas)

    return results
```

### R

```r
library(irr)

category_reliability <- function(coded_data, code_var, coders) {
  categories <- unique(unlist(coded_data[paste0(coders, "_", code_var)]))

  results <- list()
  for (cat in categories) {
    binary <- sapply(coders, function(c) {
      as.integer(coded_data[[paste0(c, "_", code_var)]] == cat)
    })

    n_relevant <- sum(rowSums(binary) > 0)
    if (n_relevant < 5) next

    k <- kappam.fleiss(binary)
    results[[cat]] <- list(
      n = n_relevant,
      fleiss_kappa = k$value,
      flag = ifelse(k$value >= 0.6, "OK", "Low")
    )
  }
  results
}
```

---

## LLM Annotation Protocol

When using LLMs as annotators (a growing practice):

### Multi-Model Design

| Requirement | Standard |
|-------------|----------|
| **Number of models** | ≥ 2 (ideally 3 from different providers) |
| **Human validation** | N ≥ 200, κ ≥ 0.7 between LLM majority vote and human gold standard |
| **Prompt documentation** | Full prompt text in appendix or replication package |
| **Disagreement analysis** | Report which categories models disagree on most |
| **Temperature** | 0 or near-0 for reproducibility |

### Majority Vote

For 3-model annotation, use majority vote (2/3 agreement):

```python
from collections import Counter

def majority_vote(codes_by_model):
    """codes_by_model: {'claude': 'X', 'gpt': 'Y', 'gemini': 'X'} → 'X'"""
    counter = Counter(codes_by_model.values())
    majority, count = counter.most_common(1)[0]
    return majority, count  # count = 2 or 3
```

### When Models Disagree

| Agreement level | Action |
|----------------|--------|
| 3/3 agree | High confidence — use the label |
| 2/3 agree | Moderate confidence — use majority, flag for spot-check |
| 0/3 agree (three-way split) | Low confidence — requires human adjudication |

---

## Reporting Template

```markdown
## Inter-Coder Reliability

### Overall
- Fleiss' κ = X.XX (N = XXX items, K = X coders)
- Three-way agreement: XX.X%
- Majority agreement (≥2/3): XX.X%

### Per Category
| Category | N | Three-way | Fleiss' κ | Status |
|----------|---|-----------|-----------|--------|
| X        | XX | XX.X%    | X.XX      | ✅/⚠️  |
| Y        | XX | XX.X%    | X.XX      | ✅/⚠️  |

### Low-Reliability Categories
⚠️ [Category] had κ = X.XX (below 0.60 threshold).
Findings involving this category should be interpreted with caution.

### Human Validation (if LLM-annotated)
- Gold standard sample: N = XXX
- LLM majority vs. human: κ = X.XX
- Model-specific: Claude κ = X.XX, GPT κ = X.XX, Gemini κ = X.XX
```

---

## Integration

### In `/data-analysis`

When the dataset includes coded/annotated variables:
1. Check if reliability metrics are reported
2. If multi-model LLM annotation, verify human validation exists
3. Flag categories below κ = 0.6 threshold

### In review agents

Check whether content analysis papers:
- Report per-category reliability (not just aggregate)
- Flag low-reliability categories as limitations
- Include human validation for LLM annotations
- Missing reliability → Major issue; aggregate-only → Minor issue

### Validation tier interaction

| Tier | Requirement |
|------|------------|
| 🟢 Exploratory | Multi-model agreement reported; human validation optional |
| 🟡 Pilot | Multi-model agreement + spot-check (N ≥ 50) |
| 🔴 Publication | Full reliability battery + human validation (N ≥ 200, κ ≥ 0.7) |
