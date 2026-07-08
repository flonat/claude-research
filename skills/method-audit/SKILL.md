---
name: method-audit
description: "Use when you need to extract and compare data collection methods across empirical papers."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv*), Bash(python*), Task, WebSearch, WebFetch, Bash(paperpile*)
argument-hint: "[topic, .bib file, or paper directory]"
---

# Method Audit

> Reverse-engineer the data collection and empirical methods across a corpus of papers. Produce a critical comparison table that surfaces methodological blind spots.

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `method-audit`
- **Write reports to:** `reviews/_project/method-audit/<YYYY-MM-DD-HHMM>.md` inside the project. Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** timestamps include hour+minute (HHMM) to disambiguate same-day runs; never overwrite an earlier run's report.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- Writing a methodology section — need to justify your approach relative to the literature
- Reviewing empirical papers — need to compare data quality across studies
- Identifying methodological gaps — what approach has nobody tried yet?
- Preparing a replication or extension — need to understand exactly how prior work was done

## When NOT to Use

- **Theoretical papers** — use `/theory-mapper` instead
- **Single-paper deep read** — use `/split-pdf`
- **Your own research design** — use `/causal-design` or `/experiment-design`
- **Code review** — use `/code-review`

## Input

Same as `/theory-mapper`: a `.bib` file, PDF directory, topic description, or list of papers. If ambiguous, ask.

## Workflow

### Phase 1: Corpus Assembly

Assemble 10-20 empirical papers using the same approach as `/theory-mapper` Phase 1. Prioritise papers with empirical content (filter out pure theory, editorials, commentaries).

### Phase 2: Method Extraction

For each paper, read using split-pdf methodology. Extract:

1. **Research design** — experimental, quasi-experimental, observational, survey, qualitative, mixed
2. **Data source** — where the data comes from (name the dataset, survey instrument, or archive)
3. **Sample**
   - Population and sampling frame
   - Sample size (N)
   - Unit of observation
   - Time period
   - Response rate (if survey)
   - Attrition (if longitudinal)
4. **Variables**
   - Dependent variable(s) and how measured
   - Key independent variable(s) and how measured
   - Controls included
5. **Estimation strategy**
   - Statistical method (OLS, IV, DiD, RCT, qualitative coding, etc.)
   - Identification strategy (what makes the estimate causal, if claimed)
   - Robustness checks reported
6. **Biases acknowledged** — what limitations the authors discuss
7. **Biases NOT acknowledged** — what you can spot that they don't mention

### Phase 3: Comparative Analysis

#### 3.1 Methods Comparison Table

| Paper | Design | Data Source | N | Period | Method | ID Strategy | Response Rate |
|-------|--------|-------------|---|--------|--------|-------------|--------------|

Sort by sample size (largest first).

#### 3.2 Technique Distribution

Count how many papers use each:
- Design type (experimental, observational, etc.)
- Estimation method (OLS, IV, DiD, etc.)
- Data type (survey, admin, experimental, scraped, etc.)

Flag any technique that is **dominant** (>60% of papers) — this signals a methodological monoculture.

#### 3.3 Bias Audit

For each paper, classify biases:

| Paper | Biases Acknowledged | Biases Missed | Severity |
|-------|-------------------|---------------|----------|

Common missed biases to check for:
- **Selection bias** — non-random sampling without correction
- **Measurement error** — self-reported outcomes, proxy variables
- **External validity** — single-country, single-firm, WEIRD samples
- **Survivorship bias** — studying only firms/people that survived
- **Publication bias** — significant results overrepresented
- **Endogeneity** — causal claims without credible identification
- **Multiple testing** — many outcomes tested without correction

#### 3.4 Methodological Gaps

- Designs nobody has tried (e.g., no RCT in a field of observational studies)
- Data sources nobody has used (e.g., admin data when everyone uses surveys)
- Robustness checks nobody runs (e.g., no placebo tests, no sensitivity analysis)
- Populations understudied (e.g., only US data in a global phenomenon)

### Phase 4: Output

Write to `METHOD-AUDIT.md` in the project directory.

## Output Format

```markdown
# Method Audit: [Topic]

**Date:** YYYY-MM-DD
**Corpus:** [N] empirical papers
**Dominant design:** [Most common research design]
**Dominant method:** [Most common estimation method]

## Comparison Table

| Paper | Design | Data | N | Period | Method | ID Strategy | Biases Noted |
|-------|--------|------|---|--------|--------|-------------|-------------|

## Technique Distribution

| Category | Count | Papers |
|----------|-------|--------|

## Bias Audit

### Commonly Acknowledged
- [Bias type] — mentioned by [N] papers

### Commonly Missed
- [Bias type] — present in [N] papers but acknowledged by [M]
  - **Why it matters:** [Impact on findings]
  - **Papers affected:** [List]

## Methodological Gaps

1. **No [design/method] studies** — [Why this matters]
2. **Understudied population:** [Who is missing]
3. **Missing robustness check:** [What should be tested]

## Implications for Your Research

- **Opportunity:** [What methodological gap you could fill]
- **Risk:** [What bias to watch for in your own design]
- **Benchmark:** [What sample size / design quality is expected in this field]
```

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/theory-mapper` | For theoretical rather than methodological comparison |
| `/causal-design` | To design your own identification strategy |
| `/experiment-design` | To design experiments or surveys |
| `/replication-audit` | To check which findings have been replicated |
