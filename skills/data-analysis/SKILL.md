---
name: data-analysis
description: "Use when you need an end-to-end analysis pipeline: EDA, estimation, or publication output."
allowed-tools: Bash(uv*, Rscript*, R*, stata*, julia*, mkdir*, ls*, cp*), Read, Write, Edit, Glob, Grep, AskUserQuestion, Skill
argument-hint: "[data-path or project-path] [--mode eda|estimation|full]"
---

# Data Analysis Pipeline

> Generate, execute, and verify analysis scripts across R, Python, Stata, and Julia.

## Modes

| Mode | What it does | Phases |
|------|-------------|--------|
| **EDA** | Exploratory data analysis only | 1–2 |
| **Estimation** | Estimation + publication output (requires locked design) | 1, 3–4 |
| **Full** | Complete pipeline | 1–5 |

Default: **Full**. Detect mode from user request or ask if ambiguous.

## When to Use

- "Analyse this data" / "Run EDA on this CSV" / "Estimate the model"
- "Generate results tables" / "Create publication figures"
- Any task requiring data → script → output pipeline

## When NOT to Use

- Experimental design or power analysis → `/experiment-design`
- Generating synthetic data for testing → `/synthetic-data`
- Auditing identification strategy → `/causal-design`
- Proofreading or compiling the paper → `/proofread`, `/latex`

## Shared References

- Method probing questions: `shared/method-probing-questions.md` — ask before running any analysis
- Validation tiers: `shared/validation-tiers.md` — declare tier before examining results
- Escalation protocol: `shared/escalation-protocol.md` — escalate when methodology answers are vague
- Distribution diagnostics: `shared/distribution-diagnostics.md` — mandatory DV checks before model selection
- Engagement-stratified sampling: `shared/engagement-stratified-sampling.md` — stratify by engagement tiers for social media data
- Inter-coder reliability: `shared/intercoder-reliability.md` — per-category reliability for content analysis and LLM annotation

## Workflow

### Phase 1: Setup

1. **Detect project structure:** Read `CLAUDE.md`, check for `data/`, `code/`, `paper/` directories.
2. **Detect language:** Check existing scripts, user preference, or ask. Read `shared/multi-language-conventions.md` for the chosen language's conventions.
3. **Locate data:** Find datasets in `data/raw/` or `data/processed/`. **Never modify `data/raw/`** (per `data-sensitivity` rule). For social-media datasets, follow [`shared/engagement-stratified-sampling.md`](../shared/engagement-stratified-sampling.md) when constructing analysis samples.
4. **Confirm validation tier** per [`shared/validation-tiers.md`](../shared/validation-tiers.md). Tier dictates claim-strength language allowed in Phase 4 outputs and how strict the locked-design gate (step 5) is enforced.
5. **Check for locked design:** Look for analysis plan in `log/plans/`, `.context/project-recap.md`, or `MEMORY.md` estimand registry. If running Estimation or Full mode and no design exists, **stop and warn:** "No locked research design found. Run `/experiment-design` or `/causal-design` first, or confirm the specification before proceeding." Use [`shared/method-probing-questions.md`](../shared/method-probing-questions.md) to probe gaps if the user pushes back on the gate.

### Phase 2: Exploratory Data Analysis

Generate and execute an EDA script that produces:

1. **Data overview:** dimensions, types, missingness summary
2. **Univariate distributions:** histograms/density for continuous, bar charts for categorical
3. **Bivariate relationships:** correlation matrix, key scatterplots, cross-tabulations
4. **Outlier detection:** box plots, IQR-based flags
5. **Distribution diagnostics** (mandatory): run `distribution_diagnostics()` from `shared/distribution-diagnostics.md` on every DV and key IVs. Report skewness, zero proportion, overdispersion, and model recommendation. Flag if OLS is inappropriate.
6. **Balance tables** (if treatment variable identified): pre-treatment covariate balance

**Output routing:**
- Exploratory figures → `output/figures/` (not `paper/figures/`)
- Summary statistics → `output/tables/` as `.csv`
- EDA script → `code/01_eda.R` (or `.py`/`.do`/`.jl`)

**EDA mode stops here.**

### Phase 3: Estimation

**Gate check:** Verify the research design is locked before proceeding. The specification (estimand, identifying assumptions, main model) must be documented. This enforces the `design-before-results` rule. If the user resists the gate, follow [`shared/escalation-protocol.md`](../shared/escalation-protocol.md) — escalate rather than accommodate. For analyses involving human or LLM coding (content analysis, annotation), require per-category reliability per [`shared/intercoder-reliability.md`](../shared/intercoder-reliability.md) before estimation.

Generate estimation script(s) covering:

1. **Main specification** — as defined in the locked design
2. **Robustness checks** — pre-committed alternatives (different SEs, controls, subsamples)
3. **Diagnostics** — specification-appropriate tests (first-stage F for IV, parallel trends for DiD, bandwidth sensitivity for RDD)

Read `references/estimation-recipes.md` for language-specific estimation patterns.

**Output:**
- Estimation script → `code/02_estimation.R` (or equivalent)
- Coefficient estimates → `output/results/` as `.rds`/`.pkl`/`.dta` for downstream table generation

### Phase 4: Publication Output

Generate publication-ready tables and figures. Read `shared/publication-output.md` for format standards and `references/table-formatting.md` for language-specific recipes.

1. **Main results table** — booktabs three-line format, exported as `.tex` to `paper/tables/`
2. **Robustness tables** — same format, appendix naming convention
3. **Publication figures** — coefficient plots, event study plots, mechanism figures → `paper/figures/` as PDF
4. **Inline statistics** — export `\newcommand` definitions for key numbers referenced in text

**Critical rule:** All numbers in `.tex` files must come from generated files via `\input{}`. **Never hard-code results** (per `no-hardcoded-results` rule). Scripts in `code/`, outputs in `paper/` (per `overleaf-separation` rule).

**Output script** → `code/03_tables_figures.R` (or equivalent)

### Phase 5: Save & Review

1. **Verify outputs exist:** Check all expected files in `paper/tables/` and `paper/figures/`
2. **Run `/code-review`** on all generated scripts (auto-invoke via Skill tool)
3. **Log the analysis:** Record what was done, which scripts were created, which outputs were generated
4. **Suggest next steps:** compilation with `/latex`, or additional analyses

## Script Structure

Every generated script follows this header template:

```
# ============================================================
# Script: [filename]
# Purpose: [one-line description]
# Inputs: [list of input files]
# Outputs: [list of output files]
# Dependencies: [packages used]
# Author: [from git config]
# Date: [today]
# ============================================================
```

## Cross-References

| Resource | When read |
|----------|-----------|
| `shared/multi-language-conventions.md` | Phase 1 (language setup) |
| `shared/publication-output.md` | Phase 4 (table/figure format) |
| `references/estimation-recipes.md` | Phase 3 (estimation code patterns) |
| `references/econ-visualisation.md` | Phase 2 & 4 (economics figure/table conventions) |
| `references/table-formatting.md` | Phase 4 (language-specific table export) |
| `references/language-conventions.md` | Phase 1 (additional language notes) |
| `design-before-results` rule | Phase 3 gate check |
| `data-sensitivity` rule | Phase 1 (data access) |
| `no-hardcoded-results` rule | Phase 4 (output routing) |
| `overleaf-separation` rule | Phase 4 (file placement) |
| `/code-review` skill | Phase 5 (auto-invoked) |
| `/experiment-design` skill | Suggested if no design exists |
| `/causal-design` skill | Suggested if no design exists |
| `/econ-plots` skill | Economics-specific figures |
| `/r-econometrics` skill | R-specific estimation |
| `/econ-data` skill | Data download from public APIs |
