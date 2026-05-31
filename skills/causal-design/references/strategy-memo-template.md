# Strategy Memo Template

> Use this template when producing the strategy memo in `/causal-design` Design Phase 3.
> Fill in every section. If a section is not applicable, state why rather than leaving it blank.

---

```markdown
# Causal Strategy Memo

**Project:** [project name]
**Date:** YYYY-MM-DD
**Status:** Draft | Locked

---

## 1. Research Question

**Causal question:** [State the causal question in one sentence. What is the effect of X on Y?]

**Treatment (X):** [Define precisely -- what is the treatment, intervention, or policy?]

**Outcome (Y):** [Define precisely -- what is the primary outcome variable? How is it measured?]

**Population:** [Who is the estimand defined over? What is the target population?]

## 2. Estimand

**Formal definition:**

$$\tau = E[Y_i(1) - Y_i(0) \mid \text{subpopulation}]$$

**Type:** [ATE / ATT / LATE / CATE / Other]

**Interpretation:** [One sentence explaining what the parameter means substantively.]

## 3. Identification Strategy

**Strategy:** [DiD / IV / RDD / SC / Event Study / Matching / Other]

**Source of variation:** [What generates exogenous variation in treatment? Why is this variation plausibly exogenous?]

**Intuition:** [2-3 sentences explaining the identification argument in plain language. A non-technical reader should understand why this comparison is valid.]

**Formal identification result:**

[State the formal result: under assumptions A1-An, the estimand is identified by [expression]. Reference the relevant econometric result if applicable.]

## 4. Key Assumptions

For each assumption, state it formally, provide a conceptual defence, and describe how (if possible) it will be tested.

### Assumption 1: [Name]

**Statement:** [Formal statement]

**Defence:** [Why should this hold in your setting?]

**Testable?** [Yes / No / Partially]

**Test plan:** [If testable, what diagnostic will you run? What would a failure look like?]

### Assumption 2: [Name]

[Same structure]

### Assumption N: [Name]

[Same structure]

## 5. Threats and Mitigations

| # | Threat | Severity | Mitigation | Residual risk |
|---|--------|----------|-----------|---------------|
| T1 | [What could go wrong] | High/Medium/Low | [How you address it] | [What risk remains] |
| T2 | ... | ... | ... | ... |
| T3 | ... | ... | ... | ... |

## 6. Diagnostics Plan

List every diagnostic test you will run before trusting the main estimates. These must be run **before** examining point estimates (per the `design-before-results` rule).

| # | Diagnostic | Purpose | Pass criterion |
|---|-----------|---------|----------------|
| D1 | [Test name] | [What it checks] | [What counts as passing] |
| D2 | ... | ... | ... |
| D3 | ... | ... | ... |

## 7. Robustness Checks

Pre-commit to alternative specifications. These are decided now, before seeing results. Post-hoc robustness checks added after seeing the main results are not credible.

| # | Specification | What it varies | Why informative |
|---|--------------|----------------|-----------------|
| R1 | [Description] | [What changes vs. main spec] | [What we learn] |
| R2 | ... | ... | ... |
| R3 | ... | ... | ... |

## 8. Alternative Strategies Considered

| Strategy | Why considered | Why rejected |
|----------|---------------|-------------|
| [Strategy 1] | [What made it a candidate] | [Why it was not chosen] |
| [Strategy 2] | ... | ... |

## 9. Data Requirements

| Variable | Source | Available? | Notes |
|----------|--------|-----------|-------|
| Treatment | [source] | Yes/No/Partial | |
| Outcome | [source] | Yes/No/Partial | |
| Running variable (RDD) | [source] | Yes/No/N/A | |
| Instrument (IV) | [source] | Yes/No/N/A | |
| Pre-treatment covariates | [source] | Yes/No/Partial | |
| Panel structure | [source] | Yes/No/N/A | |

## 10. Implementation Notes

**Estimator:** [What R/Python/Stata package and function will implement this? e.g., `did` (Callaway & Sant'Anna), `rdrobust`, `ivreg`]

**Standard errors:** [How will inference be conducted? Clustered at what level? Bootstrap?]

**Sample restrictions:** [Any sample restrictions beyond the target population?]

---

## Sign-Off

- [ ] Estimand is precisely defined
- [ ] Identification strategy matches the estimand
- [ ] All key assumptions are stated and defended
- [ ] Diagnostics plan is complete and pre-committed
- [ ] Robustness checks are pre-committed
- [ ] This memo has been reviewed by domain-reviewer agent

**Locked by:** [name]
**Lock date:** [date]
```
