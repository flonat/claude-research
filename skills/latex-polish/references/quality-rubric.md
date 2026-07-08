# Quality Rubric: LaTeX Polish

> Scoring rubric for `/latex-polish`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).
>
> Combines source-pathology findings (mirrors `/latex` Phase 4) with vision findings (this skill's distinct contribution).

## Deductions

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| PDF stale or missing | -100 | Skill aborts before scoring |
| `pdftoppm` not installed | -100 | Skill aborts before scoring |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Vision: clipped content (text/table/figure cut off at margin or page edge) | -15 | Per page where it occurs |
| Vision: visible overlap of content (text over text, figure over text) | -20 | Per page where it occurs |
| Vision: `??` or `[?]` visibly rendered in body | -15 | Per page where it occurs |
| Vision: blank or near-blank page (≥80% empty without justification) | -15 | Per page |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Source: Pattern 1 spacing-hack (titlepage/center under global non-single spacing) | -5 | Per affected block |
| Source: Pattern 3 line-breaks-as-layout inside `\section` / `\caption` | -5 | Per instance |
| Source: Pattern 5 shrink-to-fit float (`\resizebox` to `\textwidth`) | -5 | Per instance |
| Source: Pattern 7 absolute/overlap positioning outside math | -3 | Per instance, cap at -10 |
| Source: Pattern 9 label-before-caption | -5 | Per instance |
| Vision: unreadable shrunken text in a table or figure | -10 | Per occurrence |
| Vision: visibly broken float placement (float far from reference, awkward edge anchor) | -5 | Per occurrence |
| Vision: title-page line-spacing inconsistency between consecutive lines of same block | -8 | Per block |
| Vision: weight-hierarchy collapse on title page (title not visibly heavier than subtitle) | -5 | Once |

### Moderate (-2 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Source: Pattern 2 manual vertical-rhythm surgery (1-5 in body) | -1 each | Cap at -5 |
| Source: Pattern 2 (>5 in body) | -5 once | Additional Major flag |
| Source: Pattern 4 forced-float (>3 instances) | -3 once | |
| Source: Pattern 6 tiny-table typography hacks (single symptom) | -2 each | Cap at -8 |
| Source: Pattern 8 fixed-width layout (`p{Xcm}`, `minipage{Xcm}`) | -1 each | Cap at -5 |
| Vision: inconsistent paragraph spacing | -3 | Per page where it dominates |
| Vision: hyphenation rivers or 3+ stacked end-of-line hyphens | -2 | Per page |
| Vision: widow or orphan line | -2 | Per occurrence |
| Vision: caption stranded from its float | -3 | Per occurrence |
| Vision: bibliography entry inconsistency (e.g., one entry without hanging indent) | -3 | Per page |

### Minor (-1)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Source: Pattern 4 forced-float (≤3 instances) | -1 once | |
| Vision: small alignment imperfection | -1 | Per occurrence |
| Vision: mildly inconsistent inter-block gap | -1 | Per occurrence |
| `chktex` warning (`-q -n8 -n44`) | -1 each | Cap at -10 |
| `latexindent -k` non-zero exit | -3 once | Source-cleanliness smoke test |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Pre-flight verification | Phase 1 |
| Source-pathology findings | Phase 2 |
| Page-selection coverage | Phase 3 |
| Vision findings | Phase 5 |
| Consolidated verdict | Phase 6 |
| Score | Phase 7 |

## Verdict thresholds

Standard thresholds per shared/quality-scoring.md, lightly adjusted for polish-specific calibration:

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90+ | **Ship** | No layout issues block presentation |
| 80–89 | **Ship with notes** | Minor cosmetic items, can ship if time-pressured |
| 70–79 | **Revise** | At least one Major issue should be fixed before sharing |
| 60–69 | **Revise (major)** | Multiple Major or one Critical — do not share |
| <60 | **Blocked** | Critical structural issue (clipping, overlap, broken refs) — must fix |

## Notes on calibration

- Source-pathology deductions in this rubric are intentionally **softer** than `/latex`'s for the same patterns. Rationale: `/latex-polish` is the "deeper look" skill — its main signal is the vision pass, and weighting source patterns at the same level would double-count. Specifically, Pattern 2/4/8 deduct less here than in `/latex`.
- Vision findings deduct more aggressively than source findings — this reflects that a human reader sees the rendered output, not the source.
- Critical-tier vision findings (clipping, overlap, broken refs visible) effectively force REVISE / Blocked. That's the right shape.
