# Referee 2 Report Template & Filing

## Output Format: The Referee Report

Produce a formal referee report with this structure:

```
=================================================================
                        REFEREE REPORT
              [Project Name] — Round [N]
              Date: YYYY-MM-DD
=================================================================

## Summary

[2-3 sentences: What was audited? What is the overall assessment?]

---

## Audit 1: Code Audit

### Findings
[Numbered list of issues found]

### Missing Value Handling Assessment
[Specific assessment of how missing values are treated]

---

## Audit 2: Cross-Language Replication

### Replication Scripts Created
- `code/replication/referee2_replicate_[name].do`
- `code/replication/referee2_replicate_[name].R`
- `code/replication/referee2_replicate_[name].py`

### Comparison Table

| Specification | R | Stata | Python | Match? |
|--------------|---|-------|--------|--------|
| Main estimate | X.XXXXXX | X.XXXXXX | X.XXXXXX | Yes/No |
| SE | X.XXXXXX | X.XXXXXX | X.XXXXXX | Yes/No |
| N | X | X | X | Yes/No |

### Discrepancies Diagnosed
[If any mismatches, explain the likely cause and which implementation is correct]

---

## Audit 3: Directory & Replication Package

### Replication Readiness Score: X/10

### Deficiencies
[Numbered list]

---

## Audit 4: Output Automation

### Tables: [Automated / Manual / Mixed]
### Figures: [Automated / Manual / Mixed]
### In-text statistics: [Automated / Manual / Mixed]

### Deductions
[List any issues]

---

## Audit 5: Empirical Methods ([paradigm(s) identified])

### Method Assessment
[Is the approach appropriate and correctly implemented?]

### Specification / Design Issues
[Numbered list of concerns from the relevant paradigm checklist(s)]

---

## Audit 6: Novelty & Literature

### Overall Novelty Verdict: [Novel / Incremental / Overlapping / Pre-empted]

### Per-Contribution Assessment

| Claimed Contribution | Novelty | Key Prior Work | Gap |
|---------------------|---------|---------------|-----|
| [Contribution 1] | 🟢/🟡/🟠/🔴 | [Closest paper] | [What's different] |

### Missing Citations
[Papers that should be cited but aren't]

### Literature Gaps
[Streams of literature the paper overlooks]

### Positioning Recommendation
[How to sharpen the contribution claim]

---

## Research Quality Scorecard

Load `skills/shared/research-quality-rubric.md` and score all 8 dimensions (1-5). If the paper targets a specific venue, also read `skills/shared/venue-guides/reviewer_expectations.md` to calibrate your critique to that venue's reviewer priorities.

| Dimension | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Problem Formulation | 15% | /5 | |
| Literature Review | 15% | /5 | |
| Methodology | 20% | /5 | |
| Data Collection | 10% | /5 | |
| Analysis | 15% | /5 | |
| Results | 10% | /5 | |
| Writing | 10% | /5 | |
| Citations | 5% | /5 | |
| **Weighted Total** | | **/5** | |

**Verdict:** [Exceptional / Strong / Good / Acceptable / Weak]

---

## Major Concerns
[Numbered list — MUST be addressed before acceptance]

1. **[Short title]**: [Detailed explanation and why it matters]

## Minor Concerns
[Numbered list — should be addressed]

1. **[Short title]**: [Explanation]

## Questions for Authors
[Things requiring clarification]

---

## Verdict

[ ] Accept
[ ] Minor Revisions
[ ] Major Revisions
[ ] Reject

**Justification:** [Brief explanation]

---

## Recommendations
[Prioritized list of what the author should do before resubmission]

=================================================================
                      END OF REFEREE REPORT
=================================================================
```

---

## Filing the Referee Report

After completing your audit and replication, you produce **two deliverables**:

### 1. The Referee Report (Markdown)

**Location:** `[project_root]/reviews/referee2-reviewer/YYYY-MM-DD_round[N]_report.md`

The detailed written report with all findings, comparison tables, and recommendations.

### 2. The Referee Report Deck (Beamer/PDF)

**Location:** `[project_root]/reviews/referee2-reviewer/YYYY-MM-DD_round[N]_deck.tex` (and compiled `.pdf`)

A presentation deck that **visualizes** the audit findings. The markdown report provides the detailed written record; the deck helps the author **understand** the problems through tables and figures.

---

#### The Deck Follows the Rhetoric of Decks

This deck must follow the same principles as any good presentation:

1. **MB/MC Equivalence**: Every slide should have the same marginal benefit to marginal cost ratio. No slide should be cognitively overwhelming; no slide should be trivial filler.

2. **Beautiful Tables**: Cross-language comparison tables should be properly formatted with:
   - Clear headers
   - Aligned decimal points
   - Visual indicators (checkmark/cross or color) for match/mismatch
   - Consistent precision (6 decimal places for point estimates)

3. **Beautiful Figures**: Where appropriate, visualize findings:
   - Bar charts comparing estimates across languages
   - Heatmaps showing which specifications match/mismatch
   - Progress bars for scores (replication readiness, automation)
   - Coefficient plots if comparing multiple specifications

4. **Titles Are Assertions**: Slide titles should state the finding, not describe the content:
   - GOOD: "Python implementation differs by 0.003 on main specification"
   - BAD: "Cross-language comparison results"

5. **No Compilation Warnings**: Fix ALL overfull/underfull hbox warnings. The deck must compile cleanly.

6. **Check Positioning**: Verify that:
   - Table/figure labels are positioned correctly
   - TikZ coordinates are where you intend
   - Text doesn't overflow frames
   - Fonts are readable

---

#### Deck Structure

| Slide | Content |
|-------|---------|
| 1 | **Title**: Project name, "Referee Report — Round N", date |
| 2 | **Executive Summary**: Verdict + 3-4 key findings in bullet form |
| 3-5 | **Cross-Language Replication**: Comparison tables showing R/Stata/Python results side-by-side. One slide per major specification. Highlight discrepancies. |
| 6 | **Replication Discrepancies Diagnosed**: If mismatches found, explain likely causes with evidence |
| 7 | **Replication Readiness Score**: Visual scorecard (X/10) with checklist |
| 8 | **Code Audit Findings**: Severity breakdown (N major, N minor) with top concerns listed |
| 9 | **Methods Assessment**: Key specification/design concerns from the relevant paradigm checklist |
| 10 | **Novelty & Literature**: Contribution novelty ratings, missing citations, positioning |
| 11 | **Output Automation**: Checklist of what's automated vs manual |
| 12 | **Recommendations**: Prioritized action items for resubmission |

Adjust slide count based on findings — more slides if more discrepancies to show, fewer if the audit is clean.

---

#### Compilation Requirements

Before filing the deck:

1. **Always compile to `out/` subdirectory**: Use `latexmk -pdf -outdir=out <file>.tex`
2. **Copy the final PDF back** to the source directory: `cp out/<file>.pdf .`
3. **Never leave build artifacts** (`.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.nav`, `.snm`, `.toc`, `.out`) in the source directory — they belong in `out/`
4. **Compile with no errors**
5. **Fix ALL warnings** — overfull hbox, underfull hbox, font substitutions
6. **Visual inspection**: Open the PDF and verify:
   - Tables are centered and readable
   - Figures don't overflow
   - TikZ elements are positioned correctly
   - No text is cut off
7. **Re-compile** after any fixes (again to `out/`)

---

#### Files Produced

- `reviews/referee2-reviewer/YYYY-MM-DD_round1_report.md` — Detailed written report
- `reviews/referee2-reviewer/YYYY-MM-DD_round1_deck.tex` — LaTeX source
- `reviews/referee2-reviewer/YYYY-MM-DD_round1_deck.pdf` — Compiled presentation

The markdown and deck go hand-in-hand: the markdown is the permanent written record; the deck is how the author reviews and understands the audit findings.

The report does NOT go into `CLAUDE.md`. It is a standalone document that the author will read and respond to.

---

## The Revise & Resubmit Process

### Round 1: Initial Submission

1. Author completes analysis in their main Claude session
2. The Referee 2 agent is launched (via the Task tool) to audit the project
3. Referee 2 performs five audits, creates replication scripts, files referee report
4. Agent returns findings

### Author Response to Round 1

The author reads the referee report and must:

1. **For each Major Concern**: Either FIX it or JUSTIFY why not (with detailed reasoning)
2. **For each Minor Concern**: Either FIX it or ACKNOWLEDGE and explain deprioritization
3. **Answer all Questions for Authors**
4. **Describe code changes made** (what files, what changes)
5. **File response** at: `reviews/referee2-reviewer/YYYY-MM-DD_round1_response.md`

**Response format:**
```
=================================================================
                    AUTHOR RESPONSE TO REFEREE REPORT
                    Round 1 — Date: YYYY-MM-DD
=================================================================

## Response to Major Concerns

### Major Concern 1: [Title]
**Action taken:** [Fixed / Justified]
[Detailed explanation of fix OR justification for not fixing]

### Major Concern 2: [Title]
...

## Response to Minor Concerns

### Minor Concern 1: [Title]
**Action taken:** [Fixed / Acknowledged]
[Brief explanation]

...

## Answers to Questions

### Question 1
[Answer]

...

## Summary of Code Changes

| File | Change |
|------|--------|
| `code/01_clean.R` | Fixed missing value handling on line 47 |
| ... | ... |

=================================================================
```

### Round 2+: Revision Review

1. The Referee 2 agent is launched again with instructions to read:
   - The original referee report (`round1_report.md`)
   - The author response (`round1_response.md`)
   - The revised code
2. Referee 2 re-runs all five audits
3. Referee 2 assesses whether concerns were adequately addressed:
   - **Fixed**: Remove from concerns
   - **Justified**: Accept justification OR push back if unconvincing
   - **Ignored**: Flag and escalate
   - **New issues introduced**: Add to concerns
4. Referee 2 files Round 2 report at `reviews/referee2-reviewer/YYYY-MM-DD_round2_report.md`

### Termination

The process continues until:
- Verdict is **Accept** or **Minor Revisions** (with minor revisions being addressable without re-review)
- OR Referee 2 recommends **Reject** with justification
