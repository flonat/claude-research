# Quality Rubric: Quarto Deck

> Scoring rubric for `/quarto-deck`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| `reveal-md` render fails — no HTML output | -100 | Deck is broken |
| Markdown syntax error breaking slide structure | -100 | Slides don't parse correctly |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| No narrative arc (no Problem → Investigation → Resolution structure) | -20 | Fundamental rhetoric failure |
| Label title instead of assertion (e.g., "Results" not a claim) | -15 | Per slide |
| Multiple ideas on a single slide | -15 | Per slide |
| MathJax rendering failure (broken equations) | -15 | Per broken equation |
| Image/figure not found (broken `![](path)`) | -15 | Per broken image |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Content overflow (text runs off slide) | -5 | Per slide |
| Missing transitions between sections | -8 | Per missing transition |
| Aristotelian balance off for audience type | -5 | Once for the deck |
| Code block syntax highlighting broken | -5 | Per block |
| Inline styles in Markdown (should be in CSS) | -5 | Per instance — violates Critical Rule 5 |
| Figure sizing wrong (too small/large for slide) | -5 | Per figure |
| Colour palette not accessible | -5 | Once for the deck |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Conclusion-last instead of conclusion-first (Pyramid Principle) | -3 | Per slide |
| Speaker notes missing on key slides | -2 | Per key slide |
| Slide visually cramped | -3 | Per slide |
| Inconsistent formatting between slides | -2 | Once for the deck |
| `---` separator issues (extra blank lines, inconsistent spacing) | -1 | Per instance |
| Cognitive load spike | -3 | Per instance |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Rendering & structure | Phase 3-4 |
| Rhetoric (arc, titles, one-idea) | Phase 5 |
| Visual quality (figures, code, layout) | Phase 4 |
| Final polish | Phase 6 |
