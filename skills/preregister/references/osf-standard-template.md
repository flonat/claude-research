# OSF-Standard Pre-Data Collection Registration — template

> Paste sections directly into https://osf.io/registries/osf/new (select "OSF Preregistration Template"). Section headings and order match the OSF form exactly so the transcription is one-to-one.
>
> Anything in `<angle brackets>` is a placeholder for the user to fill. Anything in `[UNVERIFIED — ...]` is a `mark-unverified.md` flag that must be resolved before submission.

---

```markdown
---
title: <Study title>
study_slug: <kebab-case-slug>
template: osf-standard
created: <YYYY-MM-DD>
project: <project name>
authors:
  - <Name 1, affiliation>
  - <Name 2, affiliation>
status: draft
osf_url: <fill after submission>
data_collection_status: not_yet_started
---

# Preregistration — <Study title>

## 1. Study information

### 1a. Title
<Study title>

### 1b. Authors
<List with affiliations and contributions. Use CRediT taxonomy if known.>

### 1c. Description
<One-paragraph summary: what is the research question, why does it matter, what is the design in one sentence. ~100–200 words.>

### 1d. Hypotheses
For each hypothesis, state direction, predicted effect size (with source or SESOI), and the test that will adjudicate it.

- **H1.** <Directional claim>. Predicted effect: <d / OR / β / Δ>. Source of estimate: <prior study | pilot | SESOI>. Adjudicating test: §6, Test 1.
- **H2.** ...

Hypotheses are confirmatory. Anything not listed here is exploratory and reported as such (§9).

## 2. Design plan

### 2a. Study type
<Experimental | Observational | Survey | Computational audit | Meta-analysis | Other>

### 2b. Blinding
<Single-blind (participants) | Double-blind | Triple-blind | None>. <Justify if none.>

### 2c. Is there any additional study design information you would like to include?
<Pre-registration is not pre-acceptance. Note any departures from standard practice that reviewers would want to see flagged.>

### 2d. Study design
<Between-subjects / Within-subjects / Mixed factorial. Specify factors and levels. Describe assignment mechanism (random / matched / block / stratified). For repeated measures, specify order counterbalancing.>

### 2e. Randomisation
<Method: simple random / block / stratified / minimisation. Block size if blocked. Allocation ratio. Tool used (Qualtrics random branch, Prolific custom screener, R `sample()` with seed `<N>`).>

## 3. Sampling plan

### 3a. Existing data
<One of: (a) No data have been collected for this study yet; (b) Pilot data only — describe; (c) Some data have been collected but not analysed; (d) Data analysis has begun.>
If (a), the prereg is "pre-data". Any other status weakens the prereg's evidentiary value and must be disclosed.

### 3b. Explanation of existing data
<If 3a is not (a), describe what exists, why it was collected, and what role it will play.>

### 3c. Data collection procedures
<Where (Prolific / MTurk / lab / online panel / archival source). Recruitment criteria. Compensation. Procedure: timing, platform, instructions. Attention/comprehension checks (verbatim text). Pre-screen criteria.>

### 3d. Sample size
N = <total> across <K conditions>, n = <per cell>.

### 3e. Sample size rationale
<Power analysis: α = <.05>, target power = <.80>, smallest effect size of interest = <d = .25 / OR = 1.5>. Tool used (`pwr` in R, G*Power, `/synthetic-data` simulation). Justify the chosen effect size: prior literature (cite), pilot data, SESOI, or computational simulation. If no defensible anchor exists, use SESOI and say so explicitly.>

### 3f. Stopping rule
<One of: (a) Fixed N — collect until 3d is reached; (b) Sequential — describe stopping rule and α-spending function; (c) Time-bounded — collect for <X days> then stop. State who makes the stop decision, and that no interim peeks at the dependent variable will occur unless sequential design is specified.>

## 4. Variables

### 4a. Manipulated variables
For each IV: name, levels, operationalisation, exposure mechanism, attention check (if any).

- **IV1: <name>** — Levels: <list>. Operationalisation: <how the levels were realised>. Manipulation check: <variable + threshold>.
- **IV2: ...**

### 4b. Measured variables
For each DV / moderator / mediator: name, scale, anchors, source, scoring.

- **DV1: <name>** — Type: <continuous / ordinal / binary / count>. Scale: <e.g. 7-point Likert>. Source: <citation or self-developed>. Scoring: <mean / sum / latent>. Reliability: <expected α / ω from prior work>.
- **DV2: ...**

### 4c. Indices
<Composite scores, multilevel constructs, derived variables. Specify formula and component variables.>

## 5. Analysis plan

### 5a. Statistical models
For each confirmatory hypothesis, name the model and the parameter that adjudicates the hypothesis.

- **Test for H1.** Model: <e.g. `lm(DV1 ~ Condition + covariates)` | mixed model `lmer(DV1 ~ Condition + (1|participant))` | logistic GLM | …>. Adjudicating parameter: <coefficient name>. Inference threshold: <p < .05 two-sided | 95% CI excluding zero | Bayes factor >3>.
- **Test for H2.** ...

### 5b. Transformations
<Any pre-analysis transformations: standardisation, log, winsorisation, reverse-coding. Specify before-vs-after fit choice.>

### 5c. Inference criteria
<Multiple-comparison correction: Bonferroni, Holm, BH-FDR, none. If none, justify. Specify family of tests for the correction.>

### 5d. Data exclusion
Pre-specified exclusion rules (apply in this order):

1. <Failed attention check on item <X> (verbatim wording)>
2. <Completion time below <T> seconds — implausibly fast>
3. <Duplicate Prolific ID / IP>
4. <Missing >X% of focal DV>
5. <Other — name + threshold>

Expected exclusion rate: <X%>. If observed exclusion rate exceeds <2× expected>, report and discuss but do not change the rules post hoc.

### 5e. Missing data
<Strategy: complete-case analysis | multiple imputation (MICE, m = <n>) | FIML | last-observation-carried-forward. Justify in light of expected missingness mechanism (MCAR / MAR / MNAR).>

### 5f. Exploratory analysis
<Any analyses planned but not confirmatory. These will be reported as exploratory in the paper. Examples: subgroup effects not in H1–Hk, dose-response checks, robustness with alternative DV operationalisations.>

## 6. Other

### 6a. For computational audits / agent studies
- **Model under test:** <e.g. `gpt-4o-2024-11-20`, `claude-opus-4-7`>
- **API parameters:** <temperature, top_p, max_tokens, seed if available>
- **Prompt protocol:** <attestation that the prompts in Appendix A are fixed and will not be edited after registration>
- **Re-run policy:** <if the model is deprecated mid-collection, what happens>

### 6b. Anything else
<Anything important not captured above. Conflicts of interest, funder constraints, IRB/ethics approval reference number, data-sharing plan, materials-sharing plan.>

---

## Appendix A — Prompts / stimuli / questionnaire
<Verbatim text of all stimuli. The whole point of registering this is that nothing about the wording can change after submission.>

## Appendix B — Analysis code skeleton
<A minimal R / Python script that, given the expected data structure, would reproduce the confirmatory analyses. This isn't a complete pipeline; it's a commitment to the model spec.>
```

---

## Field-by-field guidance

- **1d Hypotheses** — Most common preregistration mistake: vague directional claims with no test. Force the user to write each hypothesis next to its adjudicating test.
- **3e Sample size rationale** — A power calculation without a justified effect size is theatre. If the user has no prior anchor, write SESOI ("smallest effect of interest") rather than inventing `d`.
- **3f Stopping rule** — Sequential designs are fine but must specify the α-spending function (Pocock, O'Brien-Fleming, etc.) up front. "Collect until significant" is **not** a stopping rule.
- **5a Statistical models** — Specify the parameter, not just the test. "We will run a t-test" is too vague; "the coefficient on `Condition` from a linear model with `age` and `gender` as covariates" is specific.
- **5d Data exclusion** — Each rule must be *operationalisable from the data alone*, with no analyst judgement at apply-time.
- **5f Exploratory analysis** — Generous coverage here protects the confirmatory plan. Anything the user "might also look at" goes here.
- **6a Computational audits** — Lock the exact model string. "GPT-4" is not specific enough; six months later it could mean a dozen different things.
