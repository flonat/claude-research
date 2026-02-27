# Research Quality Rubric

> Dimension-weighted scoring rubric for evaluating research papers and proposals.
> Adapted from ScholarEval (Moussa et al., 2025, arXiv:2510.16234) with language
> adjusted for social science, management, economics, and political economy.
>
> **When to load:** Any agent performing a structured research quality assessment.
> **Complements:** `quality-scoring.md` (deduction-based) handles artifact polish;
> this rubric handles substantive research quality across 8 dimensions.

## Dimensions & Scales

Each dimension is scored 1-5. Only 3/5/5 anchors are provided to keep the file lean.
Score 2 = between Adequate and Weak; Score 1 = fundamental deficiencies.

### 1. Problem Formulation & Research Questions (15%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Novel contribution clearly situated in a gap; research questions are precise, falsifiable, and theoretically grounded; scope is well-bounded |
| **4 Good** | Clear contribution with minor gap-articulation issues; questions are specific but could be sharper; scope is reasonable |
| **3 Adequate** | Contribution exists but is vaguely stated; questions are broad or partially redundant; scope creep risk |

- [ ] Gap in literature explicitly identified
- [ ] Research questions are stated, specific, and answerable
- [ ] Scope is bounded (what is in/out)
- [ ] Contribution is distinguished from related work
- [ ] Practical or theoretical relevance is articulated

### 2. Literature Review (15%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Comprehensive coverage of key streams; synthesises rather than lists; positions paper in ongoing debates; includes seminal and recent work |
| **4 Good** | Covers main streams with minor omissions; mostly synthetic; positioning is clear |
| **3 Adequate** | Covers basics but misses a stream or relies on dated sources; more descriptive than analytical |

- [ ] Key theoretical streams identified and covered
- [ ] Seminal works cited (not just recent)
- [ ] Review is synthetic (themes/tensions) not a list
- [ ] Competing perspectives acknowledged
- [ ] Clear link from review to research questions
- [ ] No major stream conspicuously absent

### 3. Methodology & Research Design (20%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Design is well-justified for the research questions; identification strategy is explicit; assumptions stated and defended; threats to validity addressed |
| **4 Good** | Design fits questions; identification mostly clear; some assumptions implicit; validity threats partially addressed |
| **3 Adequate** | Design is standard but justification is thin; identification strategy unclear; limited validity discussion |

- [ ] Method choice justified for the research question
- [ ] Identification strategy / causal logic explicit (if causal claims made)
- [ ] Key assumptions stated
- [ ] Threats to internal and external validity discussed
- [ ] Robustness checks or sensitivity analyses planned
- [ ] Replicability: sufficient procedural detail

### 4. Data Collection & Sources (10%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Data sources are well-suited, clearly described, and limitations acknowledged; sampling strategy justified; measurement validity established |
| **4 Good** | Sources are appropriate with minor documentation gaps; sampling is reasonable; most measures validated |
| **3 Adequate** | Sources are acceptable but convenience-driven; limited discussion of measurement validity or representativeness |

- [ ] Data sources described (origin, timeframe, access)
- [ ] Sampling strategy explained and justified
- [ ] Key variables operationalised with clear measures
- [ ] Data limitations acknowledged
- [ ] Ethical considerations addressed (if human subjects)

### 5. Analysis & Interpretation (15%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Analysis follows logically from design; results interpreted carefully with appropriate caveats; alternative explanations considered; effect sizes contextualised |
| **4 Good** | Analysis is sound; interpretation is mostly careful; some alternative explanations explored |
| **3 Adequate** | Analysis is correct but mechanical; over-reliance on p-values; limited exploration of alternatives |

- [ ] Analysis matches the stated methodology
- [ ] Results interpreted with appropriate uncertainty
- [ ] Alternative explanations considered
- [ ] Effect sizes reported and contextualised (not just significance)
- [ ] Limitations of the analysis acknowledged
- [ ] Robustness checks reported

### 6. Results & Findings (10%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Findings directly address research questions; tables/figures are clear and self-contained; null or unexpected results reported honestly |
| **4 Good** | Findings address questions with minor gaps; presentation mostly clear; negative results acknowledged |
| **3 Adequate** | Findings partially address questions; tables overloaded or under-explained; selective reporting suspected |

- [ ] Each research question has a corresponding finding
- [ ] Tables and figures are well-labelled and interpretable
- [ ] Null or unexpected results reported
- [ ] Key numbers are precise (CIs, effect sizes, sample sizes)
- [ ] No cherry-picking of specifications

### 7. Scholarly Writing & Presentation (10%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | Argument flows logically; prose is concise and precise; structure supports the narrative; transitions between sections are smooth |
| **4 Good** | Writing is clear with occasional redundancy; structure is sound; minor flow issues |
| **3 Adequate** | Writing is understandable but verbose or disorganised in places; structure follows conventions but feels mechanical |

- [ ] Abstract accurately summarises the paper
- [ ] Logical flow from introduction to conclusion
- [ ] No unnecessary jargon or undefined acronyms
- [ ] Consistent terminology throughout
- [ ] Within page/word limits (if applicable)

### 8. Citations & References (5%)

| Score | Indicators |
|-------|-----------|
| **5 Excellent** | All claims supported; no orphan citations or missing references; formatting consistent; bibliography is complete and accurate |
| **4 Good** | Minor formatting inconsistencies; one or two unsupported claims; bibliography mostly complete |
| **3 Adequate** | Several formatting issues; some claims lack support; bibliography has gaps or duplicates |

- [ ] All factual claims have citations
- [ ] No orphan `\cite{}` keys (all resolve)
- [ ] Reference list matches in-text citations (no extras, no missing)
- [ ] Formatting consistent with target venue style
- [ ] DOIs or stable URLs present where appropriate

## Weighted Scoring

```
Score = (0.15 x D1) + (0.15 x D2) + (0.20 x D3) + (0.10 x D4)
      + (0.15 x D5) + (0.10 x D6) + (0.10 x D7) + (0.05 x D8)
```

| Range | Verdict | Interpretation |
|-------|---------|---------------|
| 4.5 - 5.0 | Exceptional | Ready for top-tier venue submission |
| 4.0 - 4.4 | Strong | Minor revisions needed |
| 3.5 - 3.9 | Good | Major revisions required |
| 3.0 - 3.4 | Acceptable | Significant rework before submission |
| < 3.0 | Weak | Fundamental issues to address |

## Contextual Adjustments

**By stage:** Proposals — relax D4, D5, D6 (no results yet); weight D1, D2, D3 more heavily. Working drafts — expect D7, D8 to be lower; focus on D1-D6. Final manuscripts — full rubric, no relaxation.

**By venue tier:** Workshop/conference papers — accept 3.5+ overall. CABS 3 journals — target 4.0+. CABS 4/4* or FT 50 — target 4.5+; all dimensions should be 4+.

**By paper type:** Theoretical papers — D4 may be N/A (re-weight to D1-D3). Empirical papers — full rubric applies. Review/survey papers — D4-D6 may be N/A; weight D2 at 30%.

When a dimension is N/A, redistribute its weight proportionally across the remaining dimensions.

## Agent Integration

| Agent | Loads | Dimensions used |
|-------|-------|----------------|
| `referee2-reviewer` | Always | All 8 (full scorecard) |
| `domain-reviewer` | When scoring requested | D1, D3, D5 (overlap with its domain lenses) |
| `paper-critic` | When scoring requested | D7, D8 (overlap with writing/citation categories) |
| `/pre-submission-report` | Always | Aggregate weighted score in summary |

Agents should report per-dimension scores in a table, then the weighted aggregate, then the verdict. Use the checklist items as evidence anchors for each score.
