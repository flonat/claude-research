# Journal Referee Profiles

> Used by `referee2-reviewer` and `peer-reviewer` agents to calibrate review intensity and focus.
> When a journal is specified, the reviewer adopts that journal's typical referee perspective.
> Adapted from Sant'Anna's clo-author journal-profiles system.

## How to Use

When reviewing with a target journal:
1. Look up the journal below
2. Adjust **domain** focus (what matters most substantively)
3. Adjust **methods** focus (rigour expectations)
4. Ask the journal's **typical concerns** as explicit review questions

When no journal is specified, use generic top-field behaviour.

---

## Top-5 General Interest

### American Economic Review (AER)
**Focus:** All fields — broadest audience
**Bar:** Must interest economists outside your subfield. Big question, clean execution, clear contribution.
**Domain focus:** "Would a labour economist care about this health paper?" Contribution must be broad. Literature positioning against the *general* frontier, not just subfield.
**Methods focus:** Identification must be convincing to non-specialists. Clean, transparent design preferred over technically complex one.
**Typical concerns:** "Why should economists outside this field care?" "Is the contribution big enough?" "Is this too narrow/specialised?"

### Econometrica (ECMA)
**Focus:** Theoretical and empirical economics with formal rigour
**Bar:** Methodological innovation or empirical work with exceptional identification and formal results.
**Domain focus:** Theoretical contribution valued highly. If empirical, the design must be near-airtight. Formal welfare analysis expected.
**Methods focus:** Formal proofs or near-formal arguments expected. Asymptotic properties discussed. Novel estimators need theoretical justification.
**Typical concerns:** "Where's the formal result?" "What are the asymptotic properties?" "Is this a methods or applied contribution?"

### Journal of Political Economy (JPE)
**Focus:** All fields — strong emphasis on economic mechanisms and structural thinking
**Bar:** Deep economic insight. Values understanding *why* something happens, not just *that* it happens.
**Domain focus:** Mechanism is king. Reduced-form results alone insufficient. Structural models or mechanism tests expected.
**Methods focus:** Identification strong, but mechanism evidence equally important. Willing to accept some identification imperfection if the economic insight is deep enough.
**Typical concerns:** "What's the mechanism?" "Can you decompose the effect?" "What does this tell us about economic behaviour?"

### Quarterly Journal of Economics (QJE)
**Focus:** All fields — prizes compelling narrative and important questions
**Bar:** The question must be important and the answer must surprise.
**Domain focus:** Narrative matters enormously. The paper should read like a story with a punchline. Creative use of data or setting.
**Methods focus:** Identification must be clean and intuitive — easy to explain. Visual evidence (event studies, RD plots) highly valued.
**Typical concerns:** "Is this surprising?" "Does this change how we think about X?" "Can you explain the identification in one sentence?"

### Review of Economic Studies (REStud)
**Focus:** All fields — technically excellent empirical and theoretical work
**Bar:** Technical quality must be top-tier. Values precision and completeness over narrative.
**Domain focus:** Thoroughness expected — address every possible objection. Complete set of robustness checks.
**Methods focus:** Every specification must be justified. Full battery of robustness checks. Sensitivity analysis (Oster bounds, etc.). Multiple testing corrections if applicable.
**Typical concerns:** "Have you checked robustness to X?" "What about specification Y?" "The inference needs more care."

---

## Top Field Journals

### AEJ: Applied Economics
**Bar:** Clean applied micro with credible identification. Same rigour as top-5 but contribution can be more subfield-specific.
**Domain focus:** Meaningful subfield contribution. Practical policy relevance appreciated.
**Methods focus:** Modern estimators expected (no naive TWFE for staggered). Replication package expected.

### AEJ: Economic Policy
**Bar:** Direct policy relevance. Natural experiments from actual policy changes preferred.
**Domain focus:** Policy implications front and centre. Cost-benefit or welfare discussion expected. Generalisability to other contexts.
**Methods focus:** Identification from actual policy variation. Pre-trends must be clean. Back-of-envelope welfare calculations.

### Journal of Human Resources (JHR)
**Bar:** Strong empirical contribution in labour, education, health, demography.
**Domain focus:** Policy relevance matters more than theoretical novelty. Heterogeneity by policy-relevant subgroups expected.
**Methods focus:** Modern staggered DiD if applicable. Replication package expected at acceptance.

### Journal of Health Economics (JHE)
**Bar:** Sound health economics with credible identification.
**Domain focus:** Deep health care institutional knowledge. Moral hazard vs adverse selection distinction. Welfare implications.
**Methods focus:** Health-specific threats: selection into insurance, Ashenfelter dip, moral hazard confounding. GLM for cost outcomes alongside OLS.

### RAND Journal of Economics
**Bar:** IO-flavoured analysis with market structure or firm behaviour component.
**Domain focus:** Market structure and competition implications. Welfare analysis (consumer/total surplus).
**Methods focus:** Structural models valued alongside reduced-form. Demand estimation methods.

### Journal of Public Economics (JPubE)
**Bar:** Public finance question with clean identification.
**Domain focus:** Tax incidence, deadweight loss, behavioural responses. Programme evaluation.
**Methods focus:** Bunching estimators for kinks/notches. RDD at eligibility thresholds. Extensive vs intensive margin effects.

### Journal of Labour Economics (JLE)
**Bar:** Clean labour economics with careful identification.
**Domain focus:** Wage determination, employment effects, human capital, discrimination. Monopsony and market power.
**Methods focus:** Selection correction when relevant. Decomposition methods for wage gaps.

### Journal of Development Economics (JDE)
**Bar:** Credible empirical evidence on development questions. RCTs or strong quasi-experimental.
**Domain focus:** Deep country/region knowledge. External validity. Gender and equity dimensions.
**Methods focus:** Randomisation checks, attrition, compliance, spillovers, pre-analysis plan for RCTs.

### Review of Economics and Statistics (REStat)
**Bar:** Technically excellent empirical work. Values careful measurement.
**Domain focus:** Measurement quality paramount. Novel data or measurement approaches valued.
**Methods focus:** Highest econometric standards short of Econometrica. Full sensitivity analysis.

### Management Science
**Bar:** Rigorous empirical or theoretical work at the intersection of economics and management.
**Domain focus:** Managerial implications. Decision-making, organisational behaviour, operations. Cross-disciplinary appeal.
**Methods focus:** Accepts broader range of methods (experiments, surveys, structural). Causal identification still expected for empirical work.

### Organization Science
**Bar:** Theory-driven empirical or conceptual work on organisations.
**Domain focus:** Organisational phenomena: teams, hierarchy, culture, innovation, coordination. Theoretical contribution required alongside empirics.
**Methods focus:** Mixed methods accepted. Quasi-experimental preferred but not required. Qualitative evidence valued if rigorous.

---

## Adding a Journal

Copy this template:

```markdown
### [Journal Name] ([Abbreviation])
**Bar:** [what it takes to publish here]
**Domain focus:** [what matters most substantively]
**Methods focus:** [rigour expectations and preferred methods]
**Typical concerns:** [common referee questions]
```
