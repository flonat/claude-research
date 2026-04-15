# R&R Comment Classification and Routing

> Used during Phase 5 (Comment Tracker) to classify referee comments for efficient revision routing.
> Adapted from Sant'Anna's clo-author revision protocol.

## Classification System

Every atomic referee comment is classified into one of four categories:

| Classification | Definition | Signal Words | Routing |
|---------------|------------|-------------|---------|
| **NEW ANALYSIS** | Requires new estimation, data work, or robustness checks | "run", "test", "control for", "check", "estimate", "add specification", "heterogeneity" | Code changes → table/figure updates → paper text |
| **CLARIFICATION** | Text revision sufficient — no new analysis needed | "explain", "clarify", "discuss", "motivate", "justify", "elaborate", "rewrite" | Paper text only |
| **DISAGREE** | The reviewer asks for something the authors believe is wrong or infeasible | "fundamentally", "reject the premise", contradicts identification strategy | Flag for user — never auto-respond to disagreements |
| **MINOR** | Typos, formatting, citation fixes, wording tweaks | "typo", "citation", "footnote", "spelling", "format" | Quick paper edits |

## Classification Rules

1. **When in doubt between NEW ANALYSIS and CLARIFICATION:** If the reviewer's concern *could* be addressed with better writing but would be *stronger* with additional evidence, classify as NEW ANALYSIS. Referees notice when you only clarify instead of substantiate.

2. **DISAGREE is rare.** Most referee comments that feel wrong are actually CLARIFICATION requests — the reviewer misunderstood, and better exposition fixes it. Only classify as DISAGREE when:
   - The reviewer asks for an analysis that would violate the identification strategy
   - The reviewer's suggestion contradicts established methodology (e.g., "use naive TWFE for staggered treatment")
   - The reviewer wants you to change the research question
   - The request is infeasible given data limitations

3. **Split compound comments.** A single referee paragraph may contain both a CLARIFICATION and a NEW ANALYSIS request. Split into separate IDs with cross-references.

4. **Always classify praise.** Even positive comments should be logged (Type: Praise, Priority: Low) to reference in the response letter: "We thank the reviewer for noting..."

## Priority Assignment

| Priority | Definition | Classification Overlap |
|----------|-----------|----------------------|
| **Critical** | Threatens acceptance if not addressed | Usually NEW ANALYSIS or DISAGREE |
| **High** | Significant concern, must address thoroughly | NEW ANALYSIS or CLARIFICATION |
| **Medium** | Reasonable concern, should address | CLARIFICATION |
| **Low** | Minor or editorial | MINOR or Praise |

### Priority Heuristics

- **Multiple reviewers raise the same concern** → bump to Critical
- **Reviewer uses words like "fatal", "fundamental", "serious"** → Critical
- **Concern about identification/causality** → at least High
- **"Interesting but..."** → the "but" is the real concern, classify that
- **Editor's letter highlights specific comments** → those are Critical regardless

## Routing in the Response

### NEW ANALYSIS workflow
1. Identify the required analysis (new regression, robustness check, subsample)
2. Write the estimation code → generate new table/figure
3. Update paper text to discuss new results
4. Reference new results in response letter with specific table/figure number

### CLARIFICATION workflow
1. Identify the section(s) that need revision
2. Rewrite to address the concern
3. Quote the changed passage in the response letter (before/after)

### DISAGREE workflow
1. **Flag for user** — Claude never autonomously pushes back on referees
2. Draft a diplomatic response that:
   - Acknowledges the reviewer's concern
   - Explains why the current approach is preferred
   - Offers a compromise if possible (e.g., mention in footnote, add to appendix)
3. User reviews and approves before including in response

### MINOR workflow
1. Fix directly in the paper
2. Brief acknowledgement in response letter: "We have corrected the typo on p.X"

## Response Letter Structure

For each referee comment:

```markdown
**[R1-C3]** Reviewer 1, Comment 3: "[first ~100 chars of comment]"

**Classification:** NEW ANALYSIS
**Action taken:** We estimated an additional specification controlling for X.
The results, reported in Table A3 of the Online Appendix, confirm that our
main findings are robust. Specifically, the coefficient on treatment changes
from 0.045 (s.e. 0.012) to 0.042 (s.e. 0.013).

**Changes:** Table A3 (new), Section 5.2 paragraph 3 (revised),
Appendix B.1 (new subsection)
```

## Cross-Cutting Themes

When the same concern appears across reviewers, create a theme entry:

```markdown
**Theme T1:** External validity concerns
**Raised by:** R1-C5, R2-C2, R3-C8
**Response strategy:** Address once comprehensively in Section 7 (Discussion),
then cross-reference from each individual response.
```

This avoids repetitive responses and shows the authors took the concern seriously.
