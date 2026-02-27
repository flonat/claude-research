# Quality Scoring Framework

> Shared framework for numeric quality scoring across review skills. Each skill has its own rubric in `references/quality-rubric.md` — this file defines the common structure.

## How It Works

1. **Start at 100.** Every artefact begins with a perfect score.
2. **Deduct per issue.** Each issue found subtracts points based on its severity tier (see rubric).
3. **Floor at 0.** Score cannot go negative.
4. **Apply verdict.** Map the final score to a verdict using the thresholds below.

## Severity Tiers

| Tier | Deduction range | Definition |
|------|----------------|------------|
| **Blocker** | -100 | Artefact is broken — cannot compile, render, or run. Single blocker = automatic 0. |
| **Critical** | -15 to -25 | Will be noticed by reviewers/users. May cause rejection or misinterpretation. |
| **Major** | -5 to -14 | Noticeable quality issue. Degrades professionalism or correctness. |
| **Minor** | -1 to -4 | Polish issue. Individually harmless, accumulates. |

Each skill's rubric maps specific issues to a tier and exact deduction. When an issue doesn't fit an existing rubric entry, classify it by tier definition and use the midpoint of the range.

## Verdicts and Thresholds

| Score | Verdict | Meaning |
|-------|---------|---------|
| **95-100** | Ship | Ready for submission, sharing, or publication. |
| **90-94** | Ship with notes | Minor issues noted in report — acceptable to proceed. |
| **80-89** | Revise | Meaningful issues that should be fixed before sharing. |
| **60-79** | Revise (major) | Significant problems. Do not share in current state. |
| **0-59** | Blocked | Fundamental issues. Artefact needs substantial rework. |

## Deduction Rules

- **One deduction per unique issue.** If the same typo appears 5 times, deduct once for the pattern + note the count.
- **Repeated minor issues escalate.** 5+ instances of the same minor issue → treat as one major deduction instead of 5 minor ones.
- **Blockers are absolute.** Any single blocker sets the score to 0 regardless of other findings.
- **N/A categories don't penalise.** If a rubric category doesn't apply (e.g., no TikZ diagrams), skip it — don't award bonus points.

## Score Block Template

Include this block at the top of every review report, after the summary table:

```markdown
## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | [description] | Critical | -15 | [rubric category] |
| 2 | [description] | Minor | -2 | [rubric category] |
| ... | | | | |
| | **Total deductions** | | **-XX** | |
```

## Applying the Framework

When a skill says "Apply quality scoring":

1. Read the skill's `references/quality-rubric.md` for issue-to-deduction mappings.
2. As you review, log each issue with its rubric entry and deduction.
3. Sum deductions, compute final score (100 - total), apply verdict.
4. Insert the Score Block into the report at the designated location.
5. In the Recommendations section, prioritise fixes by deduction size (biggest impact first).
