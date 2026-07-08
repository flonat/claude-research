# AsPredicted 9-question template

> Paste each answer into the corresponding text box at https://aspredicted.org/. Answers are short by design — AsPredicted enforces brevity to keep the prereg readable. Typical full document is 500–1,200 words.
>
> The AsPredicted form's strength is its terseness; resist the urge to write OSF-length sections.

---

```markdown
---
title: <Study title>
study_slug: <kebab-case-slug>
template: aspredicted
created: <YYYY-MM-DD>
project: <project name>
authors:
  - <Name 1, affiliation>
status: draft
aspredicted_url: <fill after submission>
data_collection_status: not_yet_started
---

# Preregistration — <Study title>  (AsPredicted format)

## Q1. Have any data been collected for this study already?
<Yes / No. If "Yes", the prereg is invalid for AsPredicted's purposes; consider switching to OSF or write a registered report instead.>

## Q2. What's the main question being asked or hypothesis being tested in this study?
<One or two sentences. Be specific about direction. "We test whether AI-assisted decision-makers produce higher decision quality than unassisted decision-makers on the MCDM task in Section 3 of Smith (2023)." Avoid: "We explore the effect of AI on decisions.">

## Q3. Describe the key dependent variable(s) specifying how they will be measured.
<For each DV: name, scale, anchors, source. "Decision quality, measured as the deviation between participant ranking and expert-consensus ranking using Kendall's τ on the 8 alternatives." Keep to 2–4 sentences total across all DVs.>

## Q4. How many and which conditions will participants be assigned to?
<Number of conditions, assignment rule, randomisation tool. "2 conditions (AI-assistance / no AI), between-subjects, random assignment via Qualtrics randomiser, allocation 1:1.">

## Q5. Specify exactly which analyses you will conduct to examine the main question/hypothesis.
<For each H, name the model and the adjudicating parameter. "H1 tested via OLS regression of decision quality on a Condition dummy with age and gender as covariates. We reject H0 if the Condition coefficient is positive with p < .05 (two-sided).">

## Q6. Describe exactly how outliers will be defined and handled, and your precise rule(s) for missing data, attention checks, and exclusion (e.g., for failing manipulation checks).
<Pre-specified rules, in order of application. "Exclude: (a) participants who fail the attention check on Q12 ('Click strongly disagree'); (b) participants completing the task in under 60s (implausibly fast); (c) duplicate Prolific IDs. We do not exclude on outcome variables. Missing data on the focal DV: complete-case analysis. Expected exclusion rate ~10%.">

## Q7. How many observations will be collected or what will determine sample size?
<Total N, per-cell n, stopping rule, power justification. "N = 400 (200 per cell). Stopping rule: collect until N = 400, no interim peeks. Power justification: 80% power to detect d = 0.28 at α = .05, two-sided, anchored to the smallest effect of interest given prior decision-quality literature.">

## Q8. Anything else you would like to pre-register? (e.g., secondary analyses, variables collected for exploratory purposes, unusual analyses planned?)
<Exploratory analyses, secondary DVs, robustness checks, planned subgroup analyses. Everything that's not in Q5 goes here. "Exploratory: (a) interaction between Condition and prior AI experience (collected via screening); (b) heterogeneous effects by gender; (c) robustness with Spearman ρ as alternative DV operationalisation.">

## Q9. Have any of the authors of this submission collected, or had access to, the data referenced in this preregistration?
<Yes / No. AsPredicted's parallel to OSF's "existing data" disclosure.>
```

---

## Field-by-field guidance

- **Q2** — Direction matters. "We test whether X increases Y" is acceptable. "We explore X and Y" is a fishing expedition, not a hypothesis.
- **Q3** — If the study has more than 2 DVs, push the user to nominate the **primary** DV. The rest go in Q8 as exploratory or secondary.
- **Q5** — One sentence per hypothesis, naming the parameter. AsPredicted reviewers (and replicators) will hold the analysis to whatever is written here.
- **Q6** — Each exclusion rule must be applicable from the data alone, no analyst judgement at the point of exclusion. "We will exclude inattentive participants" is too vague; "fail attention check on Q12" is specific.
- **Q7** — Power without a target effect size is empty. Write either a published anchor (with citation) or a SESOI ("smallest effect of interest").
- **Q8** — Generous use of this field protects the confirmatory hypothesis in Q5. Anything the user "might look at" goes here, not Q5.

## When AsPredicted is the wrong choice

Switch to OSF-Standard when any of these are true:

- The study has >3 confirmatory hypotheses (AsPredicted gets crowded)
- The design is multilevel, longitudinal, or has a complex randomisation scheme
- The analysis plan involves Bayesian inference, structural models, or anything that needs a paragraph to describe
- The study is a computational audit and the prompt protocol needs an appendix
- The team needs a permanent DOI (AsPredicted gives a short URL, not a DOI)
