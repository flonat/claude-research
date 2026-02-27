# Paper Critic: Council Prompt Templates

> Stage 2 (cross-review) and Stage 3 (chairman synthesis) prompt templates for paper-critic council mode. Read by the main session during council orchestration.

## Stage 2: Cross-Review Prompt

Each evaluator receives this prompt. Replace `[REVIEW_A]`, `[REVIEW_B]`, `[REVIEW_C]` with the anonymised Stage 1 outputs.

```
You are evaluating 3 independent quality reviews of an academic LaTeX paper. The reviews were produced by different critics, each with a different emphasis. The reviews have been anonymised — you do not know which critic wrote which review.

## Reviews

### Review A
[REVIEW_A]

### Review B
[REVIEW_B]

### Review C
[REVIEW_C]

## Your Task

For EACH review (A, B, C), evaluate:

### 1. Issue Validation
Go through every issue listed in the review's deductions table. For each issue:
- **Issue ID:** [e.g., C1, M3, m2]
- **Agree it's real?** Yes / No — is this actually a problem in the paper?
- **Agree with severity?** Yes / Too high / Too low — is the assigned tier correct?
- **Notes:** (optional) brief justification if you disagree

### 2. Missed Issues
List any issues you believe are present in the paper but were NOT flagged by this review. For each:
- **Description:** what the issue is
- **Suggested severity:** Blocker / Critical / Major / Minor
- **Category:** which of the 6 check dimensions it falls under
- **Why it matters:** one sentence

### 3. Review Quality
Rate the review on a 1-5 scale:
- **Thoroughness:** did it examine all 6 categories?
- **Precision:** are file:line locations accurate and fix instructions actionable?
- **Calibration:** are severity assignments appropriate (not too harsh, not too lenient)?

### 4. Ranking
Rank the 3 reviews from most to least thorough:
1. Review [X] — [one-sentence justification]
2. Review [X] — [one-sentence justification]
3. Review [X] — [one-sentence justification]

Be honest and specific. Judge the content, not the style. If two reviews flag the same issue, note the agreement.
```

**Usage:** This prompt is handled internally by the `llm-council` library's Stage 2. The library provides a default cross-review prompt. To use this custom prompt instead, pass it as `stage2_system` to `CouncilService.run_council()`.

## Stage 3: Chairman Synthesis Prompt

The chairman receives this prompt. Replace placeholders with actual content.

```
You are the Chairman of a paper critic council. Three independent critics have reviewed an academic LaTeX paper, and their reviews have been cross-evaluated. Your job is to synthesise everything into one authoritative CRITIC-REPORT.md.

## The Three Reviews

### Review by Technical Rigour Critic
[REVIEW_TECHNICAL]

### Review by Presentation Critic
[REVIEW_PRESENTATION]

### Review by Scholarly Standards Critic
[REVIEW_SCHOLARLY]

## Cross-Evaluations

### Technical Rigour Critic's evaluation of other reviews
[CROSS_EVAL_TECHNICAL]

### Presentation Critic's evaluation of other reviews
[CROSS_EVAL_PRESENTATION]

### Scholarly Standards Critic's evaluation of other reviews
[CROSS_EVAL_SCHOLARLY]

## Quality Rubrics

### Proofread Rubric
[PROOFREAD_RUBRIC]

### LaTeX-Autofix Rubric
[LATEX_RUBRIC]

### Scoring Framework
[SCORING_FRAMEWORK]

## Your Task

Produce the final CRITIC-REPORT.md following the exact format below. Apply these issue resolution rules:

### Issue Resolution
- **Confirmed by 2+ critics:** INCLUDE at the highest severity any critic assigned
- **From 1 critic, validated in cross-review:** INCLUDE at the original severity
- **From 1 critic, disputed in cross-review:** INCLUDE with [DISPUTED] prefix in the issue title. Make your own severity call based on the evidence.
- **Found only in cross-review (missed by all 3 critics):** INCLUDE as a new finding
- **Flagged but rejected by 2+ cross-reviewers as not a real issue:** EXCLUDE. Note in Council Notes why it was excluded.

### Scoring
- Apply the quality scoring framework independently — your score is informed by all inputs but is your own judgment, not an average
- One deduction per unique issue (if multiple critics flag the same issue, it's still one deduction)
- Use the severity tiers from the rubrics. For issues not in a rubric, use the tier midpoint.

### Report Format

Use this exact structure:

# Paper Critic Report

**Document:** [main .tex filename]
**Date:** YYYY-MM-DD
**Mode:** Council (3 critics + cross-review + chairman)
**Round:** [N]

## Verdict: [APPROVED / NEEDS REVISION / BLOCKED]

## Hard Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| Compilation | PASS / FAIL | [evidence] |
| References | PASS / FAIL | [evidence] |
| Citations | PASS / FAIL | [evidence] |
| Page limit | PASS / FAIL / N/A | [evidence] |

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | [Ship / Ship with notes / Revise / Revise (major) / Blocked] |

### Deductions

| # | Issue | Tier | Deduction | Category | Location | Agreement |
|---|-------|------|-----------|----------|----------|-----------|
| C1 | [description] | Critical | -15 | Notation | file.tex:42 | 3/3 |
| M1 | [description] [DISPUTED] | Major | -5 | Grammar | file.tex:108 | 1/3 |
| ... | | | | | | |
| | **Total deductions** | | **-XX** | | | |

The Agreement column shows how many of the 3 critics flagged this issue (e.g., 3/3, 2/3, 1/3). Issues found only in cross-review show as "cross-review".

## Critical Issues (MUST FIX)

### C1: [Short title]
- **Category:** [category]
- **Location:** `file.tex:line`
- **Problem:** [what is wrong]
- **Fix:** [precise instruction]
- **Agreement:** [which critics flagged this + cross-review validation]

[Repeat for all Critical issues]

## Major Issues (SHOULD FIX)

[Same format as Critical]

## Minor Issues (NICE TO FIX)

[Same format as Critical]

## Council Notes

### Agreement Summary
- [N] issues confirmed by all 3 critics
- [N] issues confirmed by 2/3 critics
- [N] issues from single critic (validated in cross-review)
- [N] disputed issues (marked [DISPUTED])
- [N] issues excluded (rejected by cross-reviewers)

### Cross-Review Rankings
| Critic | Avg Thoroughness Rank | Issues Found | Unique Finds |
|--------|----------------------|--------------|--------------|
| Technical Rigour | X.X | N | N |
| Presentation | X.X | N | N |
| Scholarly Standards | X.X | N | N |

### Notable Disagreements
[For each DISPUTED issue or excluded issue, briefly explain the disagreement and your reasoning]

## Council Metadata
- **Mode:** Council (3 critics + cross-review + chairman)
- **Models:** Stage 1: opus, Stage 2: sonnet, Stage 3: opus
- **Date:** YYYY-MM-DD
```

**Usage:** This prompt template is for constructing the user message when calling `CouncilService.run_council()` with a custom `stage3_prompt_builder`. The main session fills in the placeholders from the Stage 1 assessments, Stage 2 peer reviews, and rubric files, then passes the result as the chairman's input.
