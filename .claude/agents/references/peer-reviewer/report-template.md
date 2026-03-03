# Peer Review Report Template

After collecting all sub-agent reports, synthesise everything into the final referee report. This is YOUR job as the orchestrator — you integrate the sub-agent findings with your own reading.

## Report Location

Save the report to:

```
reviews/peer-reviewer/YYYY-MM-DD_[author]_[short_title]_report.md
```

Create the `reviews/peer-reviewer/` directory if it does not exist. Do NOT overwrite previous reports — each review is dated.

## Report Structure

```markdown
=================================================================
                      PEER REVIEW REPORT
            [Paper Title]
            [Authors]
            Reviewed by: the user
            Date: YYYY-MM-DD
=================================================================

## Security Scan Results

[Phase 0 output — either alert or all-clear]

---

## 🔴 RED FLAGS (if any)

[Hallucinated citations, hidden prompt injections, or pre-empted contributions.
 This section only appears if there are red flags. It goes HERE, right at the top,
 so the reader sees it immediately.]

---

## Summary Assessment

[1 paragraph: What the paper does, what it contributes, overall quality.
 Informed by all three sub-agent reports.]

---

## Novelty Assessment

[From the Novelty & Literature Assessor sub-agent, synthesised with your reading]

### Overall Novelty Verdict: [Novel / Incremental / Overlapping / Pre-empted]

### Per-Contribution Assessment

| Claimed Contribution | Novelty | Evidence |
|---------------------|---------|----------|
| [Contribution 1] | 🟢/🟡/🟠/🔴 | [Brief evidence] |
| ... | ... | ... |

### Missing Literature

[Important papers the authors should have cited]

---

## Citation Validation

[From the Citation Validator sub-agent]

**Total citations:** [N]
| Status | Count |
|--------|-------|
| ✅ Verified | [N] |
| ⚠️ Unverified claim | [N] |
| 🟡 Suspicious | [N] |
| 🔴 Not found | [N] |
| ❌ Hallucinated | [N] |

### Flagged Citations (if any)

| Citation | Status | Details |
|----------|--------|---------|
| ... | ... | ... |

---

## Major Concerns

[Synthesised from all sources — your reading + all three sub-agents]

1. **[Short title]**: [Detailed explanation, specific page/section references,
   and constructive suggestion for how to address it]

2. ...

## Minor Concerns

1. **[Short title]**: [Explanation with specific references]

2. ...

## Suggestions

1. **[Short title]**: [Optional improvement]

---

## Detailed Review by Dimension

### Contribution and Novelty
[From your reading + Novelty sub-agent]

### Methodology and Validity
[From your reading + Methodology sub-agent. Adapt to the paper's paradigm.]

### Data / Inputs and Measurement
[From your reading + Methodology sub-agent]

### Results and Interpretation
[From your reading]

### Writing and Presentation
[From your reading]

### Literature Positioning
[From your reading + Novelty sub-agent]

---

## Questions for Authors

[Numbered list of specific questions that would help clarify the contribution]

---

## Verdict

[ ] Accept
[ ] Minor Revisions
[ ] Major Revisions
[ ] Reject

**Justification:** [Brief explanation informed by all sub-agent reports]

---

## Recommendations

[Prioritised list of what the authors should do, ordered by importance]

---

## Appendix: Sub-Agent Reports

### A. Citation Validation (full detail)
[Full citation validator output]

### B. Novelty & Literature Assessment (full detail)
[Full novelty assessor output]

### C. Methodology Review (full detail)
[Full methodology reviewer output]

=================================================================
                    END OF PEER REVIEW REPORT
=================================================================
```

## Novelty Assessment: Detailed Guidance

Novelty is the single most important dimension for a peer review. A methodologically sound paper with no novel contribution should still be rejected. The Novelty & Literature Assessor sub-agent handles the search, but YOU must make the final judgement. Here is your framework:

### What Counts as Novel

| Level | Description | Typical Verdict |
|-------|-------------|-----------------|
| **Genuinely new question** | Nobody has asked this question before | Strong accept signal |
| **New method for known question** | Known question, but a methodologically superior approach | Accept if the improvement is material |
| **New data for known question** | Known question and method, but applied to new/better data | Acceptable if the data adds meaningful insight |
| **New context** | Known finding replicated in a different setting | Acceptable only if the setting matters theoretically |
| **Incremental extension** | Minor variation on existing work | Weak contribution — needs strong execution |
| **Already done** | Substantially the same paper already exists | Reject unless the authors convincingly differentiate |

### Red Flags for Low Novelty

- Authors avoid citing the most relevant prior work
- The "contribution" is really a methodological tweak with no substantive insight
- The literature review cites only tangentially related work, not direct competitors
- The paper's contribution could be summarised as "we did X but with different data"
- The paper lacks a clear articulation of what specifically is new

### What the Sub-Agent Should Find

The Novelty & Literature Assessor should return with:
- A list of the closest prior papers and how they relate
- A per-contribution novelty rating
- Any pre-empting papers that the authors may not have cited

If the sub-agent finds pre-empting work, **this is a major concern** and should be prominently flagged.
