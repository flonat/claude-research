# Proposal Review Report Template

After collecting sub-agent reports, synthesise everything into the final feedback report.

## Report Location

Save the report to:

```
reviews/proposal-reviewer/YYYY-MM-DD_[short_title]_report.md
```

Create the `reviews/proposal-reviewer/` directory if it does not exist. Do NOT overwrite previous reports — each review is dated.

## Report Structure

```markdown
=================================================================
                    PROPOSAL REVIEW REPORT
            [Proposal Title]
            [Author(s)]
            Reviewed by: the user
            Date: YYYY-MM-DD
=================================================================

## Security Scan Results (if PDF)

[Phase 0 output — either alert or all-clear, or "N/A — not a PDF"]

---

## Executive Summary

[2-3 sentences: What is proposed, is it worth pursuing, what are the main
 risks. This is the "elevator pitch" version of the review.]

---

## Overall Assessment

### Is this worth pursuing?

**Verdict:** [Strongly Yes / Yes with Caveats / Needs Major Rework / No]

**Key strengths:**
1. [Strength]
2. [Strength]

**Key risks:**
1. [Risk]
2. [Risk]

---

## Novelty Assessment

### Overall Novelty: [Novel / Incremental / Crowded / Pre-empted]
### Scoop Risk: [Low / Medium / High]

| Proposed Contribution | Novelty | Key Prior Work | Gap |
|----------------------|---------|---------------|-----|
| [Contribution 1] | 🟢/🟡/🟠/🔴 | [Closest paper] | [What's different] |

### Missing Literature
[Papers the proposer should cite / be aware of]

### Positioning Advice
[How to sharpen the contribution claim]

---

## Feasibility Assessment

### Overall Feasibility: [Highly Feasible / Feasible / Risky / Infeasible]

### Method Appropriateness
[Is the proposed approach right for the question?]

### Key Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| [Risk 1] | High/Med/Low | [Suggested mitigation] |

### What's Missing
[Elements the proposal should address before starting]

### Recommended Preliminary Work
[Pilots, data checks, or scoping work that would de-risk the project]

---

## Detailed Feedback

### Research Question
[Is it well-defined? Important? Answerable?]

### Proposed Methodology
[Assessment — adapted to the paradigm]

### Data / Input Plan
[Feasibility, access, appropriateness]

### Timeline (if provided)
[Realistic? What's likely to slip?]

### Writing and Presentation
[Is the proposal well-written? Clear? Persuasive?]

---

## Constructive Suggestions

[Numbered, prioritised list of specific things to improve or consider.
 These should be ACTIONABLE — not vague "consider X" but specific
 "add a pilot study testing Y with N participants to verify Z".]

---

## Questions for the Proposer

[Specific questions that would help clarify the proposal's viability]

---

## If This Were a Grant Panel

**Fundability:** [Fund / Fund with Conditions / Revise & Resubmit / Do Not Fund]

**One-line summary for panel:** [The kind of sentence a panellist would write]

---

## Appendix: Sub-Agent Reports

### A. Novelty & Literature Assessment (full detail)
[Full novelty assessor output]

### B. Feasibility & Methods Assessment (full detail)
[Full feasibility assessor output]

=================================================================
                  END OF PROPOSAL REVIEW REPORT
=================================================================
```
