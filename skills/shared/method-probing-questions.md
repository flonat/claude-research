# Method-Specific Probing Questions

> Shared reference for analysis skills and review agents. Mandatory questions before running any empirical analysis. Adapted from CommDAAF (Xu 2026), generalised beyond communication research.

## Principle

**Never run a method with default parameters.** Before executing any analysis, ask the method-specific probing questions. Do NOT proceed without explicit answers. Vague answers trigger the [escalation protocol](escalation-protocol.md).

## Expert Fast-Track

Experienced researchers can bypass probing by providing complete specs upfront:

```
DiD: treatment = policy_change_2020, control = neighbouring_states,
parallel trends tested 2015-2019, Callaway-Sant'Anna estimator,
clustered SEs at state level, 3 pre-treatment periods
```

If the spec is complete, acknowledge and proceed. If anything is missing, probe only the gaps.

---

## Probing Questions by Method

### Regression / OLS / Panel

1. What is your **estimand**? (ATE? ATT? Conditional mean?)
2. What is the **unit of analysis**? (Individual? Firm? Country-year?)
3. What is the **identification strategy**? (Selection on observables? IV? DiD? RDD?)
4. What **controls** and why? (Justify each — no kitchen sink)
5. How do you handle **standard errors**? (Clustered? HAC? At what level and why?)
6. What are the **key threats to validity**? (Omitted variables, reverse causality, measurement error)

### Difference-in-Differences

1. What is the **treatment** and when does it occur?
2. What are **treatment and control groups**? How defined?
3. Is treatment timing **staggered**? (If yes: TWFE is biased — use CS, Sun-Abraham, or similar)
4. **Parallel trends** evidence? (Pre-treatment dynamics, placebo tests)
5. Any **anticipation effects**? (Treatment effects before official treatment date)
6. Are there **spillovers** between treated and control units?
7. What is the **relevant pre-treatment window**?

### Instrumental Variables

1. What is the **instrument** and what is the **theoretical argument** for relevance?
2. What is the **exclusion restriction** argument? (Why does Z affect Y only through X?)
3. **Weak instrument** diagnostics? (First-stage F-statistic, Anderson-Rubin CIs)
4. Is the instrument **plausibly exogenous**? (What could violate this?)
5. Are there **multiple instruments**? (Over-identification tests)
6. What is the **LATE** you're estimating? (Who are the compliers?)

### Regression Discontinuity

1. What is the **running variable** and **cutoff**?
2. Is it **sharp or fuzzy**? (Compliance rate at cutoff)
3. **Bandwidth selection** method? (MSE-optimal? Cross-validation?)
4. Evidence against **manipulation** at cutoff? (McCrary test, density plot)
5. **Functional form**? (Local linear? Polynomial order? Sensitivity to choice)
6. Are there **multiple cutoffs** or **geographic boundaries**?

### Experiments / RCTs

1. What is the **randomisation unit**? (Individual? Cluster?)
2. **Power analysis**? (Effect size assumption, desired power, required N)
3. Was the experiment **pre-registered**? (Where? What deviations?)
4. How do you handle **attrition** and **non-compliance**?
5. **Multiple testing**? (How many outcomes? Correction method?)
6. **Demand effects**? (Can participants guess the hypothesis?)
7. Is there a **pre-analysis plan**?

### Survey / Psychometrics

1. What **scales** are you using? (Validated or ad hoc?)
2. **Common method variance** — single source, single method?
3. **Response rate** and non-response bias assessment?
4. **Sampling strategy**? (Probability? Convenience? Online panel?)
5. How do you handle **missing data**? (Listwise deletion? MI? FIML?)
6. **Measurement invariance** across groups? (If comparing subgroups)

### MCDM / Multi-Criteria Analysis

1. What **method** and **why this one**? (AHP? TOPSIS? PROMETHEE? ELECTRE?)
2. How are **criteria weights** determined? (Expert elicitation? Pairwise comparison? Equal?)
3. **Sensitivity analysis** on weights? (How much do rankings change?)
4. **Rank reversal** check? (Does adding/removing alternatives change the ranking?)
5. How many **decision-makers** and how are judgements aggregated?
6. Are criteria **independent**? (If not, how is correlation handled?)
7. **Normalisation method** and sensitivity to that choice?

### Topic Modeling / NLP

1. Why topic modeling specifically? (Exploratory? No predetermined categories?)
2. How many topics (K) and **how will you select K**? (Coherence score? Held-out likelihood?)
3. What **preprocessing**? (Stopwords, stemming, frequency thresholds — justify each)
4. What counts as one **document**? (Post? Paragraph? Article?)
5. How will you **validate topics are meaningful**? (Read 20+ docs per topic)
6. Who will **name topics** and how?

### Machine Learning / Classification

1. What is the **ground truth** and how was it generated?
2. **Train/test split** strategy? (Random? Temporal? Stratified?)
3. How do you prevent **data leakage**?
4. What **baselines** are you comparing against? (Are they serious or strawmen?)
5. **Evaluation metrics** and why? (Accuracy? F1? AUC? — justify for your class balance)
6. **Human validation** sample? (Required for any LLM annotation: N≥200, κ≥0.7)

### Simulation / Agent-Based Models

1. What is the **purpose** of the simulation? (Theoretical exploration? Mechanism testing? Calibration?)
2. How are **parameters chosen**? (Empirically calibrated? Assumed? Swept?)
3. **Sensitivity analysis** plan? (Which parameters vary? Over what range?)
4. How many **replications** per parameter configuration?
5. Does the model **validate against empirical data**? (Or is it purely theoretical?)
6. What **simplifying assumptions** are made and what do they rule out?
7. **Convergence check** — how do you know the simulation has run long enough?

### Content Analysis / Coding

1. Where is your **codebook**? (Must exist before coding)
2. How many **coders** and what is the reliability plan?
3. **Sampling strategy** for content to code?
4. **Training protocol** for coders?
5. How will you handle **ambiguous cases**?
6. **Inter-coder reliability** metric and threshold? (Fleiss' κ ≥ 0.7 for publication)

---

## How Skills and Agents Use This

### In analysis skills (`/data-analysis`, `/causal-design`, `/experiment-design`)

1. Detect the method type from user's request
2. Present the relevant probing questions
3. Wait for answers before proceeding
4. If answers are vague → [escalation protocol](escalation-protocol.md)
5. Expert fast-track: if user provides complete spec, acknowledge and proceed

### In review agents (`referee2-reviewer`, `domain-reviewer`)

1. Check whether the paper addresses these questions for its stated method
2. Flag unanswered questions as issues in the review report
3. Missing identification strategy → Critical; missing sensitivity analysis → Major

### In project agents (`data-engineer`, `econometrician`)

1. Before implementing any estimation, verify the probing questions are answered
2. Reference the answers from `.planning/state.md` or the paper's methodology section
3. If no answers exist, probe the user before writing code

---

## Adding New Methods

When a research project uses a method not covered above, create a method-specific question set following the pattern:

1. **What** — define the exact variant/specification
2. **Why** — justify the choice over alternatives
3. **How** — implementation details that affect validity
4. **Threats** — what could go wrong
5. **Validation** — how you'll know it's correct
6. **Sensitivity** — what happens when assumptions change
