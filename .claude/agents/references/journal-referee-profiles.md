# Journal Referee Profiles

> Used by `referee2-reviewer` and `peer-reviewer` agents to calibrate review intensity and focus.
> When a journal is specified, the reviewer adopts that journal's typical referee perspective.
> Each profile includes a **Referee pool** that weights disposition draws (see `referee-config.md`).

## How to Use

When reviewing with a target journal:
1. Look up the journal below
2. Adjust **domain** focus (what matters most substantively)
3. Adjust **methods** focus (rigour expectations)
4. Ask the journal's **typical concerns** as explicit review questions
5. Weight disposition draws using the **Referee pool** field

When no journal is specified, use generic top-field behaviour with equal disposition weights.

---

## Economics

**Top-5 General Interest**

### American Economic Review (AER)
**Focus:** All fields — broadest audience
**Bar:** Must interest economists outside your subfield. Big question, clean execution, clear contribution.
**Domain focus:** "Would a labour economist care about this health paper?" Contribution must be broad. Literature positioning against the *general* frontier, not just subfield. Policy implications welcome but not required — insight is enough.
**Methods focus:** Identification must be convincing to non-specialists. Clean, transparent design preferred over technically complex one. Standard errors and robustness should be thorough but not excessive.
**Typical concerns:** "Why should economists outside this field care?" "Is the contribution big enough for AER?" "Is this too narrow/specialised?"
**Referee pool:** CREDIBILITY (high), POLICY (medium), STRUCTURAL (medium), MEASUREMENT (low), THEORY (low), SKEPTIC (low)

### Econometrica (ECMA)
**Focus:** Theoretical and empirical economics with formal rigour
**Bar:** Methodological innovation or empirical work with exceptional identification and formal results.
**Domain focus:** Theoretical contribution valued highly. If empirical, the design must be near-airtight. Formal welfare analysis expected. Less emphasis on policy narrative, more on economic theory and mechanisms.
**Methods focus:** Formal proofs or near-formal arguments expected for key results. Asymptotic properties discussed. Novel estimators should have theoretical justification. Simulation evidence for finite-sample properties.
**Typical concerns:** "Where's the formal result?" "What are the asymptotic properties?" "Is this a methods contribution or an applied contribution?"
**Referee pool:** THEORY (high), STRUCTURAL (high), SKEPTIC (medium), CREDIBILITY (low), MEASUREMENT (low), POLICY (low)

### Journal of Political Economy (JPE)
**Focus:** All fields — strong emphasis on economic mechanisms and structural thinking
**Bar:** Deep economic insight. Values understanding *why* something happens, not just *that* it happens.
**Domain focus:** Mechanism is king. Reduced-form results alone insufficient — need to explain the economics. Structural models or mechanism tests expected. Theoretical framework (even informal) valued.
**Methods focus:** Identification strong, but mechanism evidence equally important. Heterogeneity that illuminates the mechanism. Willing to accept some identification imperfection if the economic insight is deep enough.
**Typical concerns:** "What's the mechanism?" "Can you decompose the effect?" "What does this tell us about economic behaviour?"
**Referee pool:** STRUCTURAL (high), THEORY (high), CREDIBILITY (medium), SKEPTIC (medium), POLICY (low), MEASUREMENT (low)

### Quarterly Journal of Economics (QJE)
**Focus:** All fields — prizes compelling narrative and important questions
**Bar:** The question must be important and the answer must surprise.
**Domain focus:** Narrative matters enormously. The paper should read like a story with a punchline. Broad implications. Creative use of data or setting. "Clever" identification valued.
**Methods focus:** Identification must be clean and intuitive — easy to explain. Transparency and simplicity over complexity. Visual evidence (event studies, RD plots) highly valued.
**Typical concerns:** "Is this surprising?" "Does this change how we think about X?" "Can you explain the identification in one sentence?"
**Referee pool:** CREDIBILITY (high), POLICY (high), SKEPTIC (medium), STRUCTURAL (low), THEORY (low), MEASUREMENT (low)

### Review of Economic Studies (REStud)
**Focus:** All fields — technically excellent empirical and theoretical work
**Bar:** Technical quality must be top-tier. Values precision and completeness over narrative.
**Domain focus:** Thoroughness expected — address every possible objection. Complete set of robustness checks. Careful literature review. Less emphasis on storytelling than QJE, more on completeness.
**Methods focus:** Every specification must be justified. Full battery of robustness checks expected. Sensitivity analysis (Oster bounds, etc.). Careful treatment of inference. Multiple testing corrections if applicable.
**Typical concerns:** "Have you checked robustness to X?" "What about specification Y?" "The inference needs more care."
**Referee pool:** SKEPTIC (high), MEASUREMENT (high), CREDIBILITY (medium), THEORY (medium), STRUCTURAL (low), POLICY (low)

---

**Top Field Journals**

### AEJ: Applied Economics
**Focus:** Empirical microeconomics — labour, health, education, development, public
**Bar:** Clean applied micro with credible identification. Same rigour as top-5 but contribution can be more subfield-specific.
**Domain focus:** Meaningful subfield contribution. Practical policy relevance appreciated. Literature positioning within the subfield, not the general field.
**Methods focus:** Modern estimators expected (no naive TWFE for staggered). Replication package expected.
**Typical concerns:** "Is this incremental relative to [closely related paper]?" "Would this be better in a field journal?"
**Referee pool:** CREDIBILITY (high), POLICY (medium), MEASUREMENT (medium), SKEPTIC (low), STRUCTURAL (low), THEORY (low)

### AEJ: Economic Policy
**Focus:** Policy evaluation and design
**Bar:** Direct policy relevance. Natural experiments from actual policy changes preferred.
**Domain focus:** Policy implications front and centre. Cost-benefit or welfare discussion expected. Institutional details must be well-documented. Generalisability to other policy contexts.
**Methods focus:** Identification from actual policy variation. Pre-trends must be clean. Heterogeneity by policy-relevant subgroups expected. Back-of-envelope welfare calculations.
**Typical concerns:** "What should policymakers do with this?" "Does this generalise?" "What's the cost-benefit?"
**Referee pool:** POLICY (high), CREDIBILITY (high), MEASUREMENT (medium), STRUCTURAL (low), THEORY (low), SKEPTIC (low)

### Journal of Human Resources (JHR)
**Focus:** Labour economics, education, health, demography
**Bar:** Strong empirical contribution with clear policy relevance and careful identification.
**Domain focus:** Policy relevance matters more than theoretical novelty. External validity. Heterogeneity by policy-relevant subgroups expected.
**Methods focus:** Modern staggered DiD estimators if applicable. Clean pre-trends. Replication package expected at acceptance.
**Typical concerns:** "What's the policy implication?" "Does this generalise beyond your sample?" "Have you considered heterogeneity by [race/gender/income]?"
**Referee pool:** CREDIBILITY (high), POLICY (high), MEASUREMENT (medium), SKEPTIC (low), STRUCTURAL (low), THEORY (low)

### Journal of Health Economics (JHE)
**Focus:** Health economics — insurance, utilisation, provider behaviour, public health
**Bar:** Sound health economics with credible identification. Institutional knowledge expected.
**Domain focus:** Deep understanding of health care institutions. Moral hazard vs adverse selection distinction. Welfare implications. Connection to health policy debates.
**Methods focus:** Health-specific threats: selection into insurance, Ashenfelter dip, moral hazard confounding. GLM for cost outcomes alongside OLS.
**Typical concerns:** "Is this moral hazard or adverse selection?" "Have you addressed selection into treatment?"
**Referee pool:** STRUCTURAL (high), MEASUREMENT (high), POLICY (medium), CREDIBILITY (medium), THEORY (low), SKEPTIC (low)

### RAND Journal of Economics
**Focus:** Industrial organisation, regulation, antitrust, health care markets
**Bar:** IO-flavoured analysis with market structure or firm behaviour component.
**Domain focus:** Market structure and competition implications. Welfare analysis (consumer/total surplus). Regulatory implications.
**Methods focus:** Structural models valued alongside reduced-form. Demand estimation methods (BLP, discrete choice).
**Typical concerns:** "What does this imply for market structure?" "Consumer welfare impact?" "Can you do a structural analysis?"
**Referee pool:** STRUCTURAL (high), THEORY (high), SKEPTIC (medium), POLICY (medium), CREDIBILITY (low), MEASUREMENT (low)

### Journal of Public Economics (JPubE)
**Focus:** Tax policy, public goods, redistribution, government programmes
**Bar:** Public finance question with clean identification. Knowledge of tax/transfer system mechanics.
**Domain focus:** Tax incidence, deadweight loss, behavioural responses. Programme evaluation. Fiscal federalism.
**Methods focus:** Bunching estimators for kinks/notches. RDD at eligibility thresholds. DiD around policy changes. Extensive vs intensive margin effects.
**Typical concerns:** "What's the elasticity?" "Extensive or intensive margin?" "Welfare implications?"
**Referee pool:** STRUCTURAL (high), POLICY (high), CREDIBILITY (medium), THEORY (medium), MEASUREMENT (low), SKEPTIC (low)

### Journal of Labour Economics (JLE)
**Focus:** Labour markets — wages, employment, human capital, discrimination, immigration
**Bar:** Clean labour economics with careful identification.
**Domain focus:** Wage determination, employment effects, human capital, discrimination. Monopsony and market power.
**Methods focus:** Selection correction when relevant. Decomposition methods for wage gaps. Event study designs around job transitions or policy changes.
**Typical concerns:** "Is this a supply or demand effect?" "Selection into employment?" "General equilibrium effects?"
**Referee pool:** CREDIBILITY (high), STRUCTURAL (medium), MEASUREMENT (medium), THEORY (medium), POLICY (low), SKEPTIC (low)

### Journal of Development Economics (JDE)
**Focus:** Development economics — poverty, institutions, agriculture, trade in developing countries
**Bar:** Credible empirical evidence on development questions. RCTs or strong quasi-experimental designs.
**Domain focus:** Deep country/region knowledge. External validity. Gender and equity dimensions. Cost-effectiveness.
**Methods focus:** Randomisation checks, attrition, compliance, spillovers, pre-analysis plan for RCTs.
**Typical concerns:** "Does this generalise beyond this context?" "What about attrition?" "Cost-effectiveness?"
**Referee pool:** CREDIBILITY (high), POLICY (high), MEASUREMENT (high), SKEPTIC (medium), STRUCTURAL (low), THEORY (low)

---

**Short Format**

### AER: Insights
**Focus:** Same breadth as AER but shorter format
**Bar:** AER-quality insight in a shorter paper. Must be self-contained and punchy.
**Domain focus:** Brevity is a feature. One clean result is enough.
**Methods focus:** Core identification must be clean. Fewer robustness checks acceptable given format.
**Typical concerns:** "Can this be communicated in 10 pages?" "Is the single result compelling enough?"
**Referee pool:** CREDIBILITY (high), POLICY (medium), SKEPTIC (medium), STRUCTURAL (low), THEORY (low), MEASUREMENT (low)

### Economics Letters
**Focus:** Short papers across all fields — theoretical and empirical
**Bar:** One clear result in 5-8 pages. Speed of publication valued.
**Domain focus:** Contribution in the first paragraph. One key finding, cleanly presented.
**Methods focus:** Clean identification but extensive robustness not expected given format.
**Typical concerns:** "Can this be said in 5 pages?" "Is the single result robust?"
**Referee pool:** CREDIBILITY (high), SKEPTIC (medium), THEORY (medium), MEASUREMENT (low), STRUCTURAL (low), POLICY (low)

---

**Econometrics**

### Journal of Econometrics
**Focus:** Econometric theory and methods
**Bar:** Methodological contribution with formal results. The method must be the contribution.
**Domain focus:** Theoretical novelty paramount. Monte Carlo simulations expected. Empirical illustration should showcase the method.
**Methods focus:** Formal proofs required (consistency, asymptotic normality, convergence rates). Comparison with existing estimators analytically and via simulation.
**Typical concerns:** "What are the asymptotic properties?" "How does this compare to [existing method]?" "Finite-sample performance?"
**Referee pool:** THEORY (high), SKEPTIC (high), MEASUREMENT (high), STRUCTURAL (medium), CREDIBILITY (low), POLICY (low)

### Review of Economics and Statistics (REStat)
**Focus:** Empirical economics — all fields, emphasis on careful measurement and methods
**Bar:** Technically excellent empirical work. Values careful econometrics.
**Domain focus:** Measurement quality paramount. Novel data or measurement approaches valued.
**Methods focus:** Highest econometric standards short of Econometrica. Full sensitivity analysis.
**Typical concerns:** "Is the measurement precise enough?" "Have you tested every assumption?"
**Referee pool:** MEASUREMENT (high), SKEPTIC (high), CREDIBILITY (high), THEORY (medium), STRUCTURAL (low), POLICY (low)

---

**Health Economics**

### Health Economics
**Focus:** Health economics with emphasis on empirical applications
**Bar:** Sound empirical health economics. Good outlet for well-executed applied work.
**Domain focus:** Same institutional knowledge as JHE. Behavioural health economics increasingly accepted.
**Methods focus:** Clean identification. Both OLS and GLM for cost outcomes.
**Typical concerns:** "Have you addressed selection?" "What about moral hazard?" "Policy implications?"
**Referee pool:** CREDIBILITY (high), MEASUREMENT (high), POLICY (medium), STRUCTURAL (medium), THEORY (low), SKEPTIC (low)

---

**Urban and Spatial Economics**

### Journal of Urban Economics (JUE)
**Focus:** Urban and regional economics — housing, transport, local public goods, agglomeration
**Bar:** Clean empirical work on urban questions. Understanding of spatial economics and local policy variation.
**Domain focus:** Spatial equilibrium thinking expected. Housing markets, land use regulation, sorting.
**Methods focus:** Boundary discontinuity designs valued. Spatial autocorrelation in standard errors. Conley SEs when appropriate.
**Typical concerns:** "What about sorting?" "Is this capitalised into housing prices?" "General equilibrium effects?"
**Referee pool:** STRUCTURAL (high), CREDIBILITY (high), MEASUREMENT (medium), POLICY (medium), THEORY (medium), SKEPTIC (low)

### Journal of Economic Geography
**Focus:** Economic geography — agglomeration, trade costs, spatial inequality, regional development
**Bar:** Contribution to understanding spatial dimension of economic activity. Interdisciplinary.
**Domain focus:** Spatial thinking required. New Economic Geography tradition. European and international evidence valued.
**Methods focus:** Spatial econometrics when appropriate. Gravity equation estimation (PPML). Market access instruments.
**Typical concerns:** "What about spatial sorting?" "Have you accounted for market access?" "Is this agglomeration or selection?"
**Referee pool:** STRUCTURAL (high), MEASUREMENT (high), THEORY (medium), CREDIBILITY (medium), POLICY (medium), SKEPTIC (low)

---

## Finance

### The Journal of Finance (JF)
**Focus:** All areas of finance — asset pricing, corporate finance, market microstructure, behavioural finance
**Bar:** Must advance understanding of financial markets or financial decision-making. Big question, clean execution.
**Domain focus:** Contribution must matter broadly to finance. Theoretical motivation expected. Equilibrium implications.
**Methods focus:** For corporate/household finance: clean causal identification. For asset pricing: factor model tests, Fama-MacBeth, portfolio sorts.
**Typical concerns:** "What's the economic mechanism?" "Is this priced risk or mispricing?" "Have you addressed endogeneity?"
**Referee pool:** THEORY (high), STRUCTURAL (high), CREDIBILITY (medium), SKEPTIC (medium), MEASUREMENT (low), POLICY (low)

### Journal of Financial Economics (JFE)
**Focus:** Corporate finance, asset pricing, banking, governance
**Bar:** Strong emphasis on economic significance, not just statistical significance.
**Domain focus:** Corporate finance and governance papers especially valued. Understanding of agency problems, contracting.
**Methods focus:** Natural experiments and quasi-experimental designs valued. Event studies must follow modern best practices.
**Typical concerns:** "Is this economically significant?" "What about reverse causality?" "Is your instrument truly exogenous?"
**Referee pool:** CREDIBILITY (high), STRUCTURAL (high), THEORY (medium), SKEPTIC (medium), MEASUREMENT (low), POLICY (low)

### The Review of Financial Studies (RFS)
**Focus:** Theoretical and empirical finance — values technical sophistication
**Bar:** Technically excellent finance research. Tolerates longer papers with thorough analysis.
**Domain focus:** Thoroughness valued. Both theoretical and empirical contributions. Novel datasets valued.
**Methods focus:** Full battery of robustness checks. Multiple identification strategies appreciated. Careful inference.
**Typical concerns:** "Have you checked robustness to alternative specifications?" "Clustering at firm vs industry level?"
**Referee pool:** SKEPTIC (high), MEASUREMENT (high), STRUCTURAL (medium), THEORY (medium), CREDIBILITY (low), POLICY (low)

### JFQA
**Focus:** Empirical and theoretical finance with quantitative rigour
**Bar:** Sound empirical finance with clear contribution. Good outlet for careful empirical work.
**Domain focus:** Solid contribution to subfield sufficient. International and comparative studies welcome.
**Methods focus:** Standard modern finance econometrics. Fixed effects, clustering, IV. Current event study methodology.
**Typical concerns:** "Is this incremental?" "International evidence?" "Is the sample period long enough?"
**Referee pool:** CREDIBILITY (high), MEASUREMENT (medium), SKEPTIC (medium), THEORY (medium), STRUCTURAL (low), POLICY (low)

---

## Accounting

### Journal of Accounting Research (JAR)
**Focus:** Financial reporting, auditing, disclosure, capital markets
**Bar:** Archival empirical work with strong identification, or analytical models. Most "economics-adjacent" accounting journal.
**Domain focus:** GAAP/IFRS reporting incentives. Earnings management, accruals quality, disclosure theory.
**Methods focus:** Identification must be clean — economics standards. DiD around accounting standard changes. Heckman corrections when appropriate.
**Typical concerns:** "Is this an accounting or finance paper?" "What about selection into treatment?"
**Referee pool:** CREDIBILITY (high), MEASUREMENT (high), STRUCTURAL (medium), THEORY (medium), SKEPTIC (low), POLICY (low)

### Journal of Accounting and Economics (JAE)
**Focus:** Economic analysis of accounting — contracting, regulation, capital markets
**Bar:** Clear economic framework. Most economics-flavoured accounting journal.
**Domain focus:** Agency theory and contracting framework expected. SEC regulation, SOX, Dodd-Frank implications.
**Methods focus:** Theory-driven hypotheses — not data-mining. Structural approaches valued alongside reduced-form.
**Typical concerns:** "What's the economic theory behind this prediction?" "Is this a contracting or valuation story?"
**Referee pool:** THEORY (high), STRUCTURAL (high), CREDIBILITY (medium), MEASUREMENT (medium), SKEPTIC (low), POLICY (low)

### The Accounting Review (TAR)
**Focus:** Broadest accounting journal — financial, managerial, auditing, tax, systems
**Bar:** Significant contribution to accounting knowledge. Methodologically diverse.
**Domain focus:** Broader scope. Managerial accounting, cost accounting also considered. Standard-setting relevance appreciated.
**Methods focus:** Archival papers: similar identification standards to JAR. Experiments: proper randomisation, demand effects.
**Typical concerns:** "What are the implications for standard-setters?" "Have you addressed self-selection?"
**Referee pool:** CREDIBILITY (medium), MEASUREMENT (high), POLICY (medium), STRUCTURAL (medium), THEORY (medium), SKEPTIC (low)

### Contemporary Accounting Research (CAR)
**Focus:** All areas of accounting — international perspective
**Bar:** Solid accounting research. More international scope than US-centric TAR/JAR.
**Domain focus:** International standards (IFRS adoption, cross-country comparisons) valued.
**Methods focus:** Same rigour as TAR for archival. Textual analysis and ML applications increasingly accepted.
**Typical concerns:** "Does this apply outside the US?" "How sensitive to the accrual measure?"
**Referee pool:** MEASUREMENT (high), CREDIBILITY (high), SKEPTIC (medium), POLICY (low), STRUCTURAL (low), THEORY (low)

---

## Marketing

### Journal of Marketing Research (JMR)
**Focus:** Marketing research methods and substantive findings — consumer behaviour, pricing, advertising
**Bar:** Methodological rigour with marketing substance. Most empirically rigorous marketing journal.
**Domain focus:** Must speak to marketing managers and academics. Digital marketing increasingly important.
**Methods focus:** Experiments held to high standards. Structural demand models valued. Causal inference must be convincing.
**Typical concerns:** "What's the managerial implication?" "Can you run a field experiment to validate?" "Endogeneity of price?"
**Referee pool:** CREDIBILITY (high), STRUCTURAL (high), MEASUREMENT (medium), POLICY (medium), THEORY (low), SKEPTIC (low)

### Marketing Science
**Focus:** Quantitative marketing — structural models, field experiments, econometric analysis
**Bar:** Technical sophistication expected. Most methods-intensive marketing journal.
**Domain focus:** Demand estimation, pricing optimisation, customer lifetime value. Platform economics.
**Methods focus:** Structural models expected. BLP, nested logit, mixed logit. Counterfactual simulations alongside reduced-form.
**Typical concerns:** "Can you estimate a structural model?" "What's the counterfactual?" "Consumer heterogeneity?"
**Referee pool:** STRUCTURAL (high), THEORY (high), MEASUREMENT (medium), CREDIBILITY (medium), SKEPTIC (low), POLICY (low)

### Journal of Consumer Research (JCR)
**Focus:** Consumer behaviour — psychology of consumption, decision-making, identity, culture
**Bar:** Theoretical contribution to understanding consumer behaviour. More behavioural/psychological.
**Domain focus:** Psychological theory expected. Process evidence (mediation, moderation) valued. Identity, motivation, JDM frameworks.
**Methods focus:** Experimental designs dominant. Multiple studies showing robustness and boundary conditions. Pre-registration viewed favourably.
**Typical concerns:** "What's the psychological process?" "Can you show mediation?" "What are the boundary conditions?"
**Referee pool:** THEORY (high), MEASUREMENT (high), SKEPTIC (medium), CREDIBILITY (medium), STRUCTURAL (low), POLICY (low)

---

## Management and Strategy

### Management Science
**Focus:** Interdisciplinary — operations, finance, marketing, strategy, economics, behavioural science, organisations, IS
**Bar:** Technically rigorous work spanning business disciplines. Extremely broad scope.
**Domain focus:** Must fit a department but speak broadly. Practical implications valued. Model-driven empirical work appreciated.
**Methods focus:** Standards match the relevant field. Structural estimation, causal inference, field experiments all welcome.
**Typical concerns:** "Which department does this fit?" "Is this a ManSci paper or a field journal paper?" "Practical implication?"
**Referee pool:** STRUCTURAL (high), CREDIBILITY (high), THEORY (medium), MEASUREMENT (medium), POLICY (low), SKEPTIC (low)

### Strategic Management Journal (SMJ)
**Focus:** Strategy — competitive advantage, diversification, alliances, innovation, governance
**Bar:** Significant contribution to strategic management theory and practice.
**Domain focus:** Resource-based view, dynamic capabilities, competitive dynamics. Innovation strategy.
**Methods focus:** Endogeneity is the central concern. IV, DiD around exogenous shocks, matching methods. Panel data with firm FE.
**Typical concerns:** "Is strategy endogenous here?" "Unobserved firm heterogeneity?" "Theory of competitive advantage?"
**Referee pool:** THEORY (high), CREDIBILITY (high), STRUCTURAL (medium), SKEPTIC (medium), MEASUREMENT (low), POLICY (low)

### Administrative Science Quarterly (ASQ)
**Focus:** Organisation theory and behaviour — institutions, networks, culture, power, status
**Bar:** Deep theoretical contribution with rigorous evidence. Accepts qualitative, quantitative, mixed methods.
**Domain focus:** Institutional theory, organisational ecology, network theory. Status and legitimacy. Historical and comparative analysis valued.
**Methods focus:** Quantitative: panel data, FE, causal identification. Qualitative: systematic data collection, theoretical sampling. Mixed methods welcome.
**Typical concerns:** "What's the theoretical mechanism?" "How does this advance organisation theory?" "Alternative theoretical explanations?"
**Referee pool:** THEORY (high), MEASUREMENT (high), STRUCTURAL (medium), CREDIBILITY (medium), POLICY (low), SKEPTIC (low)

### Organization Science
**Focus:** Organisational phenomena — teams, hierarchy, culture, innovation, coordination
**Bar:** Theory-driven empirical or conceptual work on organisations. Theoretical contribution required alongside empirics.
**Domain focus:** Organisational phenomena. Theoretical contribution required.
**Methods focus:** Mixed methods accepted. Quasi-experimental preferred but not required. Qualitative evidence valued if rigorous.
**Typical concerns:** "What's the theory?" "How does this extend our understanding of organisations?" "Generalisability?"
**Referee pool:** THEORY (high), CREDIBILITY (medium), MEASUREMENT (medium), STRUCTURAL (medium), SKEPTIC (low), POLICY (low)

---

## Adding a Journal

Copy this template and add it above this section:

```markdown
### [Journal Name] ([Abbreviation])
**Focus:** [fields and topics covered]
**Bar:** [what it takes to publish here]
**Domain focus:** [what matters most to domain reviewers at this journal]
**Methods focus:** [rigour expectations, preferred methods, required checks]
**Typical concerns:** [common referee questions at this journal]
**Referee pool:** [disposition] (high/medium/low) for each: STRUCTURAL, CREDIBILITY, MEASUREMENT, POLICY, THEORY, SKEPTIC
```
