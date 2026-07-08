# `expected_values.json` — manuscript ground truth for numeric-reproduction scoring

> Optional convention that powers **Check 11 (Numeric Reproduction)** in Audit mode. When a package root contains `expected_values.json`, the audit parses the package's **committed output files** and scores them against the manuscript's reported numbers within explicit tolerances. Absent → Check 11 is `N/A` and the audit behaves exactly as before.

Pattern adapted from [`kubotaso/AI_Social_Replication`](https://github.com/kubotaso/AI_Social_Replication) (Werner et al., 2026). See `docs/research/2026-06-20-replication-scoring-pattern.md` for the rationale.

## Why a separate file (compute-don't-copy boundary)

The manuscript's reported numbers live in `expected_values.json`, **not** in the analysis code. The audit reads the package's own output files (the same ones Check 3 cross-references) and compares them to this external truth. Keeping the expected values out of the code under test means the check is independent of it — it cannot be satisfied by the code copying its own target.

**Scope guard (important):** Check 11 is **read-only and does not run scripts** (per the skill's standing rule). It verifies that the *committed outputs already in the package* match the manuscript — i.e. it catches paper-vs-output drift. It does **not** re-execute the pipeline; a fresh-run reproduction check is out of scope for this skill.

## Schema

A top-level object keyed by target id (`table1`, `figure2`, …). Each target declares a `type` and per-target `tolerances` (falling back to the defaults below if omitted).

```json
{
  "_defaults": {
    "tolerances": { "coef": 0.05, "se": 0.02, "n_pct": 0.05, "loglik": 1.0, "pseudo_r2": 0.02 }
  },
  "table1": {
    "type": "regression",
    "source_file": "output/table1.csv",
    "models": {
      "model1": {
        "coefficients": { "income": 0.34, "education": 0.12 },
        "std_errors":   { "income": 0.04, "education": 0.03 },
        "n": 1200,
        "log_likelihood": -450.2,
        "pseudo_r2": 0.18
      }
    }
  },
  "figure2": {
    "type": "figure",
    "source_file": "output/figure2_data.csv",
    "tolerance": 0.02,
    "series": { "trend": [[1960, 0.20], [1964, 0.25], [1968, 0.31]] }
  }
}
```

| Field | Meaning |
|-------|---------|
| `type` | `regression` or `figure` (selects the scoring rubric). |
| `source_file` | Package-relative path to the **committed output** the audit parses (CSV preferred; a `.tex` table or a figure's backing data file also work). If the figure has no backing data file, the target is scored structurally only and flagged for manual visual check. |
| `models` / `series` | The manuscript's reported numbers. |
| `tolerances` / `tolerance` | Per-target overrides of `_defaults`. |

## Scoring (0–100 per target)

**Regression** — points awarded when the parsed output is within tolerance of the declared value:

| Component | Points | Default tolerance |
|---|---|---|
| Coefficients | 30 | within 0.05 |
| Standard errors | 20 | within 0.02 |
| Sample size N | 15 | within 5% per model |
| Variables present | 10 | all declared appear |
| Log-likelihood | 10 | within 1.0 |
| Pseudo-\(R^2\) | 15 | within 0.02 |

**Figure** — plot type/series 15, data accuracy 40 (declared series points within tolerance), axis ranges 15, visual elements 15, layout 15. Where only a backing data file exists, score the data-accuracy component and mark the rest `manual`.

Tolerances are **discipline-tunable** — loosen for noisy survey data, tighten for deterministic simulations. Document any non-default tolerance inline in the JSON.

## Mapping the 0–100 score to the Pass/Partial/Fail count

Check 11 contributes one Pass/Partial/Fail to the audit count (like every other check), and reports the underlying per-target scores + discrepancy notes as detail:

| Result | Criteria |
|--------|----------|
| **Pass** | Every scored target ≥ 90/100 — all reported numbers reproduce within tolerance. |
| **Partial** | Most targets ≥ 90; remaining near-misses each have a documented cause (e.g. data-vintage difference). |
| **Fail** | One or more targets disagree beyond tolerance with no explanation, OR `expected_values.json` references output files the package does not contain. |
| **N/A** | No `expected_values.json` at package root. |

## Discrepancy notes + "Underspecified in the manuscript"

For every target below 90, the audit names a root cause (`wrong variable`, `missing standardization`, `data vintage`, …) rather than just the gap — so a fixer pass is targeted, not random. The audit report may also carry an **"Underspecified in the manuscript"** section listing methodology the paper omits (weighting, IV details, coding conventions) that forced a judgment call during reproduction. This is reviewer-grade reproducibility-gap documentation and strengthens the package.
