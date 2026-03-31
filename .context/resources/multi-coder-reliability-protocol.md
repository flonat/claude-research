# Multi-Coder Reliability Protocol

> Source: weiai-wayne-xu/commDAAF — Nonprofit Mission Framing Study (March 2026)
> Problem solved: Establishing inter-coder reliability for AI-assisted content analysis without human validation

## Overview

Traditional content analysis requires human coders for reliability. This protocol uses **three independent AI models** to establish reliability without human intervention while avoiding "single-coder circularity."

## The 3-Model Protocol

```
┌─────────────┐    ┌─────────────┐
│  Coder A    │    │  Coder B    │
│  (Codex)    │    │  (Gemini)   │
│  Batch 1    │    │  Batch 2    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬─────────┘
                ▼
        ┌─────────────┐
        │  Coder C    │
        │  (Claude)   │
        │ 30-item     │
        │ reliability │
        │ sample      │
        └─────────────┘
```

## Protocol Steps

### Step 1: Split Primary Coding
```python
# Divide dataset between two coders
batch_1 = missions[:len(missions)//2]  # → Codex
batch_2 = missions[len(missions)//2:]  # → Gemini
```

### Step 2: Code Independently
Each coder receives identical instructions but codes independently:
```python
codex_results = code_with_codex(batch_1, instructions)
gemini_results = code_with_gemini(batch_2, instructions)
```

### Step 3: Sample for Reliability
```python
import random
random.seed(42)  # Reproducible

# Sample from BOTH batches
combined = codex_results + gemini_results
reliability_sample = random.sample(combined, 30)
```

### Step 4: Third-Model Validation
```python
# Claude codes the 30-item sample independently
claude_results = code_with_claude(reliability_sample, instructions)

# Compare against original coders
kappa_vs_codex = cohens_kappa(
    [r for r in claude_results if r["original_coder"] == "codex"],
    [r for r in codex_results if r["id"] in sample_ids]
)
kappa_vs_gemini = cohens_kappa(
    [r for r in claude_results if r["original_coder"] == "gemini"],
    [r for r in gemini_results if r["id"] in sample_ids]
)
```

### Step 5: Report Both kappa Values
```markdown
### Inter-Coder Reliability

| Comparison | kappa | Agreement |
|------------|-------|-----------|
| Claude vs Codex | 0.94 | 97% |
| Claude vs Gemini | 0.92 | 96% |
| **Overall** | **0.935** | **96.7%** |
```

## Why This Works

| Concern | How Protocol Addresses It |
|---------|---------------------------|
| Single-model bias | Three different model families |
| Circular validation | Validator (Claude) never saw training data |
| Provider collusion | Codex (OpenAI), Gemini (Google), Claude (Anthropic) |
| Replicability | Fixed random seed, identical instructions |

## Minimum Requirements

- **3 distinct models** from different providers
- **30+ items** in reliability sample
- **Fixed random seed** for reproducibility
- **Identical instructions** to all coders
- **kappa > 0.80** for acceptable reliability (Landis & Koch)

## Landis & Koch kappa Interpretation

| kappa | Interpretation |
|-------|----------------|
| < 0.00 | Poor |
| 0.00-0.20 | Slight |
| 0.21-0.40 | Fair |
| 0.41-0.60 | Moderate |
| 0.61-0.80 | Substantial |
| **0.81-1.00** | **Almost perfect** |

## Code Template

```python
from sklearn.metrics import cohen_kappa_score
import random

def compute_reliability(primary_results: list, validator_results: list) -> dict:
    """Compute inter-coder reliability between primary coder and validator."""

    # Match items by ID
    matched = []
    for v in validator_results:
        for p in primary_results:
            if p["id"] == v["id"]:
                matched.append((p["code"], v["code"]))
                break

    primary_codes = [m[0] for m in matched]
    validator_codes = [m[1] for m in matched]

    # Cohen's kappa
    kappa = cohen_kappa_score(primary_codes, validator_codes)

    # Simple agreement
    agreement = sum(p == v for p, v in matched) / len(matched)

    return {
        "n_sample": len(matched),
        "cohens_kappa": round(kappa, 3),
        "simple_agreement": round(agreement * 100, 1),
        "interpretation": interpret_kappa(kappa),
    }

def interpret_kappa(k: float) -> str:
    if k >= 0.81: return "almost perfect"
    if k >= 0.61: return "substantial"
    if k >= 0.41: return "moderate"
    if k >= 0.21: return "fair"
    if k >= 0.00: return "slight"
    return "poor"
```

## Reporting Disagreements

Always report the nature of disagreements:

```markdown
### Disagreement Analysis

Single disagreement (1/30): County fair organization
- Codex: SERVICE (provides entertainment to community)
- Claude: FELLOWSHIP (exists for member exhibitors)

**Interpretation:** Borderline case illustrating reasonable ambiguity
in the scheme, not systematic divergence.
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Same model for coding + validation | Circular | Use different model families |
| No reliability sample | Unverifiable | Always sample 30+ items |
| Reconciliation before kappa | Inflated agreement | Compute kappa on independent codes |
| Reporting only agreement % | Ignores chance | Always report Cohen's kappa |
