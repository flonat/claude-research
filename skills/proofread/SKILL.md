---
name: proofread
description: "Use when you need academic proofreading of a LaTeX paper (11 check categories)."
allowed-tools: Read, Glob, Grep
argument-hint: [project-path or tex-file]
---

# Academic Proofreading

**Report-only skill.** Never edit source files — produce `PROOFREAD-REPORT.md` only.

## When to Use

- Before sending a draft to supervisors
- Before submission to a journal/conference
- After major revisions to check consistency
- When you want a fresh-eyes check on writing quality

## When NOT to Use

- **Formal audits** — use the Referee 2 agent for systematic verification
- **Argument quality** — use `/devils-advocate` for logical scrutiny
- **Citation completeness** — use `/bib-validate` for bibliography cross-referencing (though this skill flags obvious citation format issues)

## Workflow

1. **Locate files**: Find all `.tex` files in the project (and `.log` files for LaTeX diagnostics)
2. **Read the document**: Read all `.tex` source files in order
3. **Run 11 check categories** (below)
4. **Produce report**: Write `YYYY-MM-DD_PROOFREAD-REPORT.md` in `reviews/proofread/` under the project directory (create the directory if it does not exist). Do NOT overwrite previous reports — each review is dated.

## Check Categories

### 1. Grammar & Spelling

- Spelling errors (including technical terms)
- Subject-verb agreement
- Sentence fragments or run-ons
- Misused words (e.g., "effect" vs "affect", "which" vs "that")
- American English is the default for all papers and conference articles. Flag any British English spellings (e.g., -ise, -our, -re, analyse, scepticism).

### 2. Notation Consistency

- Variable notation used consistently throughout (e.g., always `$x_i$` or always `$x_{i}$`, not both)
- Subscript/superscript style (e.g., `$\beta_1$` vs `$\beta_{OLS}$`)
- Matrix/vector formatting conventions (bold, uppercase, etc.)
- Consistent use of `\mathbb`, `\mathcal`, `\mathbf` for sets, operators, vectors
- Equation numbering: all referenced equations numbered, unreferenced ones unnumbered

### 3. Citation Format

- Consistent use of `\citet` (textual) vs `\citep` (parenthetical)
- No raw `\cite{}` when `\citet`/`\citep` is available
- Author name spelling matches between text mentions and citation keys
- Multiple citations in chronological or alphabetical order (check which convention)
- No "As shown by (Author, Year)" — should be "As shown by \citet{key}"

### 4. Academic Tone

- No informal contractions (don't, can't, won't → do not, cannot, will not)
- No first-person overuse (some "we" is fine; excessive "I think" is not)
- No casual hedging ("pretty much", "kind of", "a lot")
- Appropriate use of hedging language ("suggests" vs "proves")
- No exclamation marks in body text
- Consistent tense (present for established facts, past for specific studies)
- **Filler hedge phrases to flag** (delete on sight): "interestingly", "importantly", "it is worth noting", "it should be noted that", "needless to say", "of course", "obviously", "clearly" (unless something is literally clear from a figure)
- **Vague quantifiers to flag**: "very", "quite", "rather", "somewhat", "fairly" — replace with specific magnitudes or delete
- **Tautological constructions**: "significant and important", "novel and new", "unique and distinctive" — one adjective suffices

### 5. LaTeX-Specific Issues

- **Overfull hbox**: Check `.log` file for `Overfull \hbox` warnings — report line numbers and severity (badness)
- **Equation overflow**: Long equations that exceed column/page width
- **Float placement**: Check for `[h!]` or `[H]` overuse; prefer `[tbp]`
- **Missing labels**: Figures/tables/equations referenced but without `\label{}`
- **Orphan/widow lines**: Check for `\\` abuse that creates bad page breaks
- **Unresolved references**: `??` in output indicating broken `\ref{}` or `\cite{}`

### 6. Citation Voice Balance

Check the ratio of in-line (`\citet`) to parenthetical (`\citep`) citations:

- **Count in-line vs parenthetical citations** across the full document
- **Flag if ratio exceeds 1:1** (in-line should be the minority) — Major
- **Flag runs of 3+ consecutive in-line citations** in a paragraph or section — Major
- **Flag paragraphs that open with an in-line citation** when the author's identity isn't the point — Minor
- **Flag "As shown by \citet{}" patterns** where parenthetical would be more natural — Minor
- **Report the overall ratio** (e.g., "42 parenthetical, 28 in-line — ratio 1.5:1")

See `docs/reference/conventions.md` § Citation Voice Balance for the full convention.

### 7. TikZ Diagram Review

If the document contains TikZ code (`\begin{tikzpicture}` or `\tikz`):

- **Label positioning**: Labels not overlapping nodes or edges
- **Geometric accuracy**: Coordinates and angles consistent with intended layout
- **Visual semantics**: Arrow styles match meaning (solid = direct, dashed = indirect, etc.)
- **Spacing**: Nodes not too cramped or too spread out
- **Consistency**: Style matches across all diagrams in the document
- **Standalone compilability**: Each diagram should compile independently

For detailed spatial verification (Bezier depth calculations, gap minimums, shape boundary clearance), see [`../shared/tikz-rules.md`](../shared/tikz-rules.md).

### 8. Numeric Text↔Table Cross-Check

Cross-check every number mentioned in the prose against the corresponding table or figure. Flag ANY discrepancy, no matter how small.

- **Coefficient claims**: "a 3.2 percentage point increase" in text vs coefficient of 0.031 in the table — flag the mismatch
- **Sample sizes**: "N = 1,247" in text vs N row in table — must match exactly
- **Significance claims**: "statistically significant at the 5% level" in text vs the actual stars/p-value in the table
- **Summary statistics**: means, medians, standard deviations mentioned in prose must match the descriptive statistics table
- **Figure references**: claims about trends or magnitudes must be consistent with what the figure shows
- **Table/figure existence**: every table/figure referenced in text must exist; every table/figure in the document must be referenced in text
- **N consistency**: the number of observations should be consistent across related specifications unless there's an explained reason for differences

### 9. Causal Language Audit

Audit causal claims against the stated identification strategy. The strength of causal language must match the strength of the research design.

- **Flag "X causes Y"** or "the causal effect of X" when the identification strategy is observational (OLS with controls, correlational) — should be "is associated with" or "predicts"
- **Flag "proves"** — almost never appropriate; use "provides evidence consistent with"
- **Match language to design**:
  - DiD/RDD/IV → "we estimate the causal effect" is acceptable with qualifiers
  - OLS with controls → "we find a relationship" or "our estimates suggest"
  - Correlational → never use causal language
- **Flag "significant" ambiguity** — must always be clear whether "statistically significant" or "economically meaningful/large"
- **Flag coefficient descriptions without units or scale** — "a coefficient of 0.031" means nothing without knowing the units of X and Y
- **Flag correlation/causation conflation** — any statement that slides from an association to a causal claim without an identification argument

### 10. Equation Completeness

Verify that mathematical notation is complete and internally consistent.

- **Every variable in an equation must be defined** in the text (either before or immediately after the equation)
- **Error terms**: properly specified (ε_it vs u_i vs e_ij) and consistent with the econometric framework described
- **Equation numbering**: sequential, and all cross-references to equations are correct
- **Subscript/index structure must match the level of observation** — e.g., if the text describes individual-level variation, the equation should have individual subscripts, not county-level
- **Summation/expectation indices**: verify bounds match the described sample
- **Consistent notation across equations**: don't switch between β and b for the same coefficient, or between X_i and x_i

### 11. Preprint Staleness

For every citation that looks like a preprint or working paper, check whether a peer-reviewed version has since been published. Flag stale preprints as Major issues.

- **Detection signals**: URL contains `arxiv.org`, `ssrn.com`, `nber.org`; journal field says "Working Paper", "mimeo"; entry type is `@techreport` or `@unpublished`
- **Action**: note the stale citation and suggest the published venue/year
- **This is a lighter version of `/bib-validate`'s preprint check** — only flag obvious cases visible from the `.bib` or `\bibitem` entries. For thorough preprint checking, recommend running `/bib-validate` separately.

## Severity Levels

| Level | Definition | Example |
|-------|-----------|---------|
| **Critical** | Will be noticed by reviewers, may cause rejection | Broken references, major grammar errors, inconsistent core notation, text↔table number mismatch, causal overclaiming with weak design |
| **Major** | Noticeable quality issue | Inconsistent citation style, tone issues, overfull hbox > 10pt, undefined variable in equation, stale preprint, ambiguous "significant" |
| **Minor** | Polish issue | Occasional British/American mix, minor spacing, missing equation number for referenced equation |

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Insert the Score Block into the report after the summary table.

## Recurring Pattern Grouping

When the same issue appears 3+ times, **group it as a single pattern finding** instead of listing each instance separately. This prevents reports bloated with 50 individual items when the real message is "you have 3 recurring problems."

**Format:**
```
### M3: Hedge phrase "interestingly" (8 instances)
- **Category:** Academic tone
- **Locations:** lines 42, 67, 103, 145, 189, 203, 267, 301
- **Problem:** Filler hedge phrase adds no content
- **Fix:** Delete all 8 instances
```

One deduction for the pattern (not 8 separate deductions). Escalation still applies: 5+ instances of the same minor issue → one Major deduction.

## Report Format

```markdown
# Proofread Report

**Document:** [filename]
**Date:** YYYY-MM-DD
**Pages:** [approximate]

## Summary

| Category | Critical | Major | Minor |
|----------|----------|-------|-------|
| Grammar & spelling | 0 | 0 | 0 |
| Notation consistency | 0 | 0 | 0 |
| Citation format | 0 | 0 | 0 |
| Academic tone | 0 | 0 | 0 |
| LaTeX-specific | 0 | 0 | 0 |
| Citation voice balance | 0 | 0 | 0 |
| TikZ diagrams | 0 | 0 | 0 |
| Numeric cross-check | 0 | 0 | 0 |
| Causal language | 0 | 0 | 0 |
| Equation completeness | 0 | 0 | 0 |
| Preprint staleness | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** |

## Critical Issues

[List each with file, line/section, and specific issue]

## Major Issues

[List each with file, line/section, and specific issue]

## Minor Issues

[List each with file, line/section, and specific issue]

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | [description] | [tier] | -X | [category] |
| | **Total deductions** | | **-XX** | |

## Recommendations

[Optional: overall observations about the writing — prioritise fixes by deduction size]
```

## Council Mode (Optional)

For high-stakes pre-submission checks, run proofreading in council mode to get independent assessments from multiple LLM providers. Council mode surfaces formatting issues that any single model might miss.

**Trigger:** "Council proofread my paper" or "thorough proofread"

**How it works:**
1. The main session reads the document and constructs the proofreading prompt
2. The prompt is sent to 3 different models via `cli-council` (or `llm-council` for API mode)
3. Each model independently runs the 7 check categories
4. Cross-review identifies agreements and disputes
5. Chairman synthesis produces a single `PROOFREAD-REPORT.md` with council notes

**Invocation (CLI backend — free with existing subscriptions):**
```bash
cd packages/cli-council
uv run python -m cli_council \
    --prompt-file /tmp/proofread-prompt.txt \
    --context-file /tmp/paper-content.txt \
    --output-md /tmp/proofread-council.md \
    --chairman claude \
    --timeout 180
```

See `skills/shared/council-protocol.md` for the full orchestration protocol.

**Value:** Diminishing returns for pure formatting — council mode is most valuable when combined with citation voice balance and notation consistency checks, where different models have genuinely different pattern recognition.

## Cross-References

- **`/bib-validate`** — For thorough bibliography cross-referencing
- **`/latex`** — For compilation and error resolution (run before proofreading to ensure the document compiles cleanly)
- **Referee 2 agent** — For formal code + paper auditing
- **`/devils-advocate`** — For argument quality and logical scrutiny
