# Elicitation checklist

> Run through this before writing the preregistration. Every item should be either **ticked** (✓) or explicitly **waived** with a one-line reason. Anything ticked with `[UNVERIFIED — ...]` flags a gap that must be resolved before submission.

The checklist is the working draft's quality gate. If half the items are still `[UNVERIFIED]`, the user is not ready to register — they're ready to think more.

---

## 0. Foundations

- [ ] **Research question** stated as one sentence
- [ ] **Why now** — what would the user know after this study that they don't know now?
- [ ] **Existing data status** — confirmed pre-data, pilot-only, or partial collection (informs OSF §3a / AsPredicted Q1)
- [ ] **Ethics / IRB status** — approved, in review, or N/A (computational audit on public data)

## 1. Hypotheses

- [ ] Each hypothesis is **directional** ("X increases Y", not "X is related to Y")
- [ ] Each hypothesis is **falsifiable** — a specific outcome would reject it
- [ ] Each hypothesis is **numbered** and tied to a specific test (no orphan claims)
- [ ] Confirmatory hypotheses count: <K>. Anything `K > 5` is a yellow flag — split studies or move some to exploratory
- [ ] An **a priori effect size** is named for each H, with source (published study / pilot / SESOI)
- [ ] No hypothesis uses "explore", "investigate", or "examine" as its verb — those belong in the exploratory section

## 2. Design

- [ ] **Study type** specified (experimental / observational / survey / computational audit)
- [ ] **Assignment mechanism** specified (random / matched / block / stratified) with the tool used
- [ ] **Counterbalancing** specified for within-subjects designs
- [ ] **Blinding** specified, or explicit waiver with reason
- [ ] **Manipulation check(s)** named with verbatim wording in Appendix A

## 3. Sample

- [ ] **Source** specified (Prolific filter / lab pool / panel / archival source)
- [ ] **Sample size N** specified — total and per-cell
- [ ] **Power justification** specified — α, target power, effect size, source of effect size
- [ ] **Stopping rule** specified — fixed N / sequential with α-spending / time-bounded
- [ ] If sequential, the α-spending function is named
- [ ] **No interim peeks** at the focal DV unless sequential design is preregistered

## 4. Variables

- [ ] Each IV: name, levels, operationalisation, exposure mechanism
- [ ] Each DV: name, scale, anchors, source citation, scoring rule
- [ ] **Primary DV** identified (the one that adjudicates the main hypothesis)
- [ ] Secondary DVs identified and labelled as secondary
- [ ] Composite indices: formula + components specified

## 5. Analysis

- [ ] Each confirmatory H has one **named test** (model + adjudicating parameter)
- [ ] **Inference threshold** specified (p, CI, Bayes factor)
- [ ] **Multiple-comparison correction** specified or explicitly waived with reason
- [ ] **Pre-analysis transformations** specified (standardisation, log, winsorise)
- [ ] **Covariates** specified for each model — no post-hoc covariate fishing

## 6. Exclusions

- [ ] **Attention check(s)** specified verbatim with threshold
- [ ] **Completion-time floor / ceiling** specified
- [ ] **Duplicate handling** specified (Prolific ID, IP, browser fingerprint)
- [ ] **Missingness threshold** specified per variable
- [ ] **Order of application** specified — rules apply in a fixed order
- [ ] **Expected exclusion rate** specified — and a plan if observed rate is >2× expected
- [ ] No exclusion rule is conditional on the outcome variable

## 7. Outliers

- [ ] **Outlier definition** specified (e.g. ±3 SD on the DV, Cook's distance >4/n, or none)
- [ ] **Handling** specified — winsorise / exclude / robust estimator / none
- [ ] Outlier handling applied **before** model fit if applied (no post-hoc trimming)

## 8. Exploratory analysis

- [ ] Section exists — even if minimal
- [ ] Each exploratory analysis labelled as such (will be reported as exploratory in the paper)
- [ ] Subgroup analyses, alternative DV operationalisations, robustness checks all listed here

## 9. Computational-audit specifics (only if applicable)

- [ ] **Model under test** locked with full version string (`gpt-4o-2024-11-20`, not `GPT-4`)
- [ ] **API parameters** specified (temperature, top_p, max_tokens, seed if available)
- [ ] **Prompts** in Appendix A, with attestation that they will not change after registration
- [ ] **Re-run / model-deprecation policy** specified
- [ ] **Sampling stochasticity** addressed (n re-runs per prompt, aggregation rule)

## 10. Final sanity checks

- [ ] Each hypothesis in §2 is referenced by exactly one test in §5
- [ ] Each test in §5 adjudicates exactly one hypothesis in §2
- [ ] Anything `K > 3` exclusion rules has a justification
- [ ] No `[UNVERIFIED]` flags remain
- [ ] Word count is in range (OSF: 1,500–3,000; AsPredicted: 500–1,200)
- [ ] Appendix A (verbatim stimuli) is complete
- [ ] Appendix B (analysis code skeleton) compiles / runs on dummy data

---

## Common gaps to probe for

These are the items that most often come back `[UNVERIFIED]` on a first pass:

1. **Effect size with no anchor** — user defaults to `d = 0.5` because it's "medium". Push: where did 0.5 come from? If nowhere, write SESOI.
2. **Exclusion rules that depend on the analyst** — "we will exclude implausible responses". What counts as implausible? Specify the rule.
3. **Stopping rule = "until significant"** — not a stopping rule. Specify fixed N or a proper sequential design.
4. **Vague test specification** — "we will test the effect of X on Y". Which model, which parameter, which threshold?
5. **Missing computational-audit version lock** — "we use GPT-4". Six months later this is meaningless. Lock the version string.
6. **Exploratory section empty** — almost certainly wrong. Anything the user "might also look at" goes there. An empty exploratory section usually means hidden flexibility is hiding in the confirmatory plan.
7. **Manipulation check absent** — for any non-trivial manipulation. Without one, the prereg can't be defended against "the manipulation didn't work" reviewer attacks.

---

## Cross-references

- OSF-Standard template: `references/osf-standard-template.md`
- AsPredicted template: `references/aspredicted-template.md`
- Composed skills: `/hypothesis-generation`, `/experiment-design`, `/causal-design`, `/synthetic-data`, `/ethics-review`
- Global rule: `mark-unverified.md` — any unanchored effect size or unspecified rule must be tagged
