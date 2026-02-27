# Scott Cunningham — Multi-Language Code Audits

> Source: Substack (Feb 2026). First in a series on Claude Code for causal inference pipelines.

## Core Idea

Frame LLM coding errors as **measurement error**: random, language-specific syntax mistakes that are independent across languages. If errors in R, Python, and Stata are independent:

```
P(all three wrong) = ε_R × ε_P × ε_S ≈ very small
```

Therefore: replicate your entire data pipeline in 2-3 languages and compare outputs numerically (coefficients, test statistics, table values) to catch implementation bugs.

## Key Claims

1. **Hallucination as measurement error.** LLM code errors are random draws from a language-specific error distribution — analogous to classical measurement error (variable = true value + noise).
2. **Independence across languages.** Syntax-specific errors (Stata's missing-value trap, R's factor ordering, Python's 0-indexing) are plausibly independent because they stem from different language grammars.
3. **Full pipeline replication, not just code review.** Replicate cleaning, merging, and estimation end-to-end in 2+ languages. Compare outputs table-by-table, coefficient-by-coefficient.

## When It Works

- Deterministic computations: OLS, DiD, IV, F-tests, analytical standard errors, R-squared
- Data processing: cleaning, merging, variable construction
- Any pipeline where the same inputs should produce identical numerical outputs

## When It Doesn't Work

- Bootstrap (language-specific seeds)
- Simulation-based estimators (simulated MLE, method of simulated moments)
- Bayesian MCMC (Gibbs, HMC)
- EM algorithms with random starting points
- Machine learning (SGD, random forests, neural net initialisation)

## Limitation: Independence Breaks Down for Conceptual Errors

The independence assumption holds for *syntax-specific* bugs but NOT for *design errors* (wrong estimand, wrong merge logic, wrong identification strategy). Conceptual errors replicate across languages because they're language-agnostic. This approach catches implementation bugs, not design bugs.

## Illustrative Example: Stata Missing-Value Trap

```stata
* WRONG — also replaces missing values to 10
replace olddog = 10 if olddog > 10

* CORRECT — excludes missing values
replace olddog = 10 if olddog > 10 & olddog ~= .
```

Claude Code knows the correct version (trained on Stata manuals + Nick Cox's listserv posts) but may randomly omit the missing-value guard. If you only run Stata, this propagates silently. If you also run R and Python (where `NA` handling differs), the discrepancy surfaces in the output comparison.

## Case Study

Callaway & Sant'Anna DiD applied to Brazilian deinstitutionalisation (CAPS) and homicides. Packages used:
- **Stata:** `csdid`, `csdid2`
- **R:** `did`
- **Python:** `differences` (Dionisi), `diff-diff` (Gerber)

## Relevance

- Complements existing `/code-review` skill (which already has cross-language verification as category 7/11) — but Cunningham's version is more aggressive: full pipeline replication, not just spot-checking
- Does NOT replace design-level audits (`/devils-advocate`, `design-before-results` rule) — those catch the conceptual errors this approach misses
- Most applicable to empirical papers with deterministic estimation pipelines
