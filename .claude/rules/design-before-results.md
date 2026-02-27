# Rule: Design Before Results

## Principle

**Lock the research design before examining point estimates.** Specify the estimand, identification strategy, and analysis plan before looking at results. This prevents post-hoc rationalisation and keeps the research credible.

## When This Applies

- Writing or reviewing estimation code (regression specifications, simulation parameters)
- Discussing identification strategy or research design
- Setting up robustness checks or sensitivity analyses
- Choosing between competing econometric/statistical approaches
- Reviewing meeting notes where research design was discussed

## When to Skip

- Read-only tasks (proofreading, code archaeology, literature search)
- Documentation and context updates
- Quick mode / exploratory data analysis (EDA)
- Descriptive statistics and data exploration (before the design phase)
- Tasks with no empirical component (pure theory, teaching prep)

## What This Means in Practice

**DO:**
- Specify the estimand before writing any estimation code
- Write down identifying assumptions before running the first regression
- Pre-commit to a main specification before examining coefficient estimates
- Define "success" criteria for simulations before running them
- Document the analysis plan in `.context/project-recap.md` or the paper's methodology section

**DON'T:**
- Run a regression and then decide what the estimand is based on which coefficients are significant
- Choose between OLS, IV, and DiD based on which gives the "best" results
- Add or drop control variables to get a desired p-value
- Modify simulation parameters after seeing initial results without documenting why
- Present robustness checks only for specifications that "work"

## The Falsifiability Test

Before running any analysis, ask:

> "If I specified my analysis plan before running it, would I change anything about what I'm about to do?"

If the answer is yes, stop and specify the plan first. If the answer is "I don't have a plan yet", write one before proceeding.

## How to Apply This

1. When the user asks to "run the regression" or "check the results", first confirm the specification is locked
2. If no analysis plan exists, draft one and get approval before executing
3. When results are surprising, document the surprise *before* changing the specification
4. Treat specification changes after seeing results as a new analysis requiring justification
