# Domain Profile Template

> Copy this template to your project's `docs/domain-profile.md` and fill it in.
> All agents and skills read this file to calibrate field-specific behaviour.
> Adapted from Sant'Anna's clo-author domain-profile system.

## Field

**Primary:** [e.g., Health Economics, Labour Economics, Development, IO, Public Finance, Organisational Behaviour]
**Adjacent subfields:** [e.g., Labour, Public, IO — fields whose methods and journals overlap]

---

## Target Journals (ranked by tier)

<!-- Used for journal selection and literature prioritisation. -->

| Tier | Journals |
|------|----------|
| Top-5 | AER, Econometrica, JPE, QJE, REStud |
| Top field | [e.g., JHE, RAND JE, AEJ:EP, AEJ:Applied, Management Science] |
| Strong field | [e.g., Health Affairs, AJHE, JPubE, JHR, Organization Science] |
| Specialty | [e.g., Medical Care, Health Services Research, JEBO] |

---

## Common Data Sources

<!-- Prioritised during data discovery. -->

| Dataset | Type | Access | Notes |
|---------|------|--------|-------|
| [e.g., CPS] | [survey/admin/panel] | [public/restricted] | [key strengths and limitations] |

---

## Common Identification Strategies

<!-- Considered first during strategy design. -->

| Strategy | Typical Application | Key Assumption to Defend |
|----------|-------------------|--------------------------|
| [e.g., State-level DiD] | [Policy variation across states] | [Parallel trends in outcomes across treated/control states] |
| [e.g., RDD at eligibility threshold] | [Programme eligibility cutoff] | [No manipulation of running variable at cutoff] |
| [e.g., IV with shift-share] | [Labour supply shocks] | [Exclusion restriction: instrument affects outcome only through treatment] |

---

## Field Conventions

<!-- Followed by estimation and writing skills. -->

- [e.g., Binary outcomes → report LPM alongside logit/probit marginal effects]
- [e.g., Cost outcomes → log transform or GLM (Gamma, log link)]
- [e.g., Clustering at state level for state-level policy variation]
- [e.g., Always discuss moral hazard / adverse selection implications]
- [e.g., Welfare analysis expected in top-5 submissions]
- [e.g., Stars: * p < 0.10, ** p < 0.05, *** p < 0.01]

---

## Notation Conventions

<!-- Enforced in paper writing and reviewing. -->

| Symbol | Meaning | Anti-pattern |
|--------|---------|-------------|
| [e.g., $Y_{it}$] | [Outcome for individual i at time t] | [Don't use $y$ without subscripts] |
| [e.g., $D_{it}$] | [Treatment indicator] | [Don't use $T$ — conflicts with time] |
| [e.g., $\beta$] | [Parameter of interest] | [Don't use $b$ for coefficients] |

---

## Seminal References

<!-- Ensures these are cited when relevant. -->

| Paper | Why It Matters |
|-------|---------------|
| [e.g., Finkelstein et al. (2012)] | [Oregon HIE — gold standard for insurance effects] |
| [e.g., Callaway & Sant'Anna (2021)] | [Modern DiD with staggered treatment] |

---

## Field-Specific Referee Concerns

<!-- Watch list for peer review simulation. -->

- [e.g., "Why not use the Oregon HIE?" — must address if studying insurance effects]
- [e.g., "Selection into treatment" — always a concern in health care utilisation studies]
- [e.g., "External validity" — Medicaid population ≠ general population]
- [e.g., "Moral hazard vs adverse selection" — referees expect you to distinguish]

---

## Quality Tolerance Thresholds

<!-- Customise for your domain's standards. -->

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Point estimates | [e.g., 1e-6] | [Numerical precision] |
| Standard errors | [e.g., 1e-4] | [MC variability] |
| Coverage rates | [e.g., ± 0.01] | [Simulation with B reps] |
