# Pre-Analysis Plan Template

> Structured template for pre-analysis plans following AEA/OSF/EGAP conventions.
> Read during PAP mode of `/experiment-design`.

## PAP Structure

```markdown
# Pre-Analysis Plan: [Study Title]

## 1. Study Information

- **Title:** [Full study title]
- **Authors:** [Names and affiliations]
- **Registration:** [AEA RCT Registry / OSF / EGAP — to be registered]
- **IRB Approval:** [Institution, protocol number, approval date]
- **Funding:** [Funding source, if any]
- **Version:** [Date of this version]

## 2. Study Design

### 2.1 Research Question
[Primary research question in one sentence]

### 2.2 Hypotheses
- **H1 (primary):** [Directional hypothesis with expected sign]
- **H2 (secondary):** [Directional hypothesis]
- **H3 (exploratory):** [Clearly labelled as exploratory]

### 2.3 Experimental Design
- **Type:** [Between-subjects / Within-subjects / Factorial / Cluster-randomized]
- **Conditions:**
  - Treatment 1: [Description]
  - Treatment 2: [Description]
  - Control: [Description]
- **Randomization:** [Method, stratification variables, blocking]
- **Blinding:** [Single / Double / None — justify if none]

### 2.4 Sample
- **Population:** [Target population]
- **Recruitment:** [How participants are recruited]
- **Eligibility:** [Inclusion/exclusion criteria]
- **Sample size:** [N = X, justified by power analysis — cite power analysis script]

## 3. Variables

### 3.1 Primary Outcome
- **Name:** [Variable name]
- **Measurement:** [Scale, items, coding]
- **Timing:** [When measured relative to treatment]

### 3.2 Secondary Outcomes
[List each with same detail as primary]

### 3.3 Treatment Variable(s)
- **Assignment mechanism:** [Random, stratified, etc.]
- **Dosage/intensity:** [If applicable]

### 3.4 Control Variables
[List pre-treatment covariates to include in main specification]

### 3.5 Manipulation Checks
[How you verify the treatment worked as intended]

## 4. Analysis Plan

### 4.1 Main Specification
[Exact regression equation or statistical test]

$$Y_i = \alpha + \beta_1 T_i + \gamma X_i + \epsilon_i$$

where:
- $Y_i$ = [outcome]
- $T_i$ = [treatment indicator]
- $X_i$ = [covariates]

### 4.2 Inference
- **Standard errors:** [Clustered / Robust / HC2 — specify clustering level]
- **Significance level:** $\alpha = 0.05$
- **Multiple testing:** [Bonferroni / Holm / BH / Romano-Wolf — specify which comparisons]

### 4.3 Heterogeneous Effects
[Pre-specified subgroup analyses — must be registered]

### 4.4 Missing Data
- **Attrition:** [How handled — bounds analysis, Lee bounds, etc.]
- **Item non-response:** [Complete cases / multiple imputation / specify]

## 5. Robustness and Sensitivity

### 5.1 Robustness Checks
- [Alternative specification 1]
- [Alternative specification 2]

### 5.2 Sensitivity Analyses
- [Sensitivity to outliers]
- [Alternative coding of variables]

## 6. Power Analysis

[Reference power analysis script and results. Include minimum detectable effect size.]

Power analysis script: `code/power_analysis.R`
Minimum detectable effect: d = [value] at 80% power

## 7. Timeline

| Phase | Dates | Description |
|-------|-------|-------------|
| Registration | [date] | Register PAP |
| Data collection | [dates] | [platform/method] |
| Analysis | [dates] | Run pre-specified analyses |
| Reporting | [dates] | Write results section |
```

## Registration Platforms

| Platform | URL | Common for |
|----------|-----|-----------|
| AEA RCT Registry | socialscienceregistry.org | Economics RCTs |
| OSF Registries | osf.io/registries | General social science |
| EGAP Registry | egap.org/registry | Political science / governance |
| ClinicalTrials.gov | clinicaltrials.gov | Health / medical |
| RIDIE | ridie.3ieimpact.org | Development economics |

## What Counts as a Deviation

After registration, any change to the following counts as a deviation and must be disclosed:
- Main specification (estimating equation)
- Primary outcome definition
- Sample definition (inclusion/exclusion)
- Subgroup analyses
- Multiple testing corrections

Acceptable without disclosure:
- Adding exploratory analyses (clearly labelled)
- Fixing coding errors that don't change the specification
- Adding covariates to robustness checks (if the main spec is unchanged)
