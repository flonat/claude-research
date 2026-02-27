# Quality Rubric: Beamer Deck

> Scoring rubric for `/beamer-deck`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Compilation fails — no PDF produced | -100 | Deck is broken |
| Default Beamer theme used (Warsaw, Madrid, etc.) | -100 | Violates Critical Rule 5 |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| No narrative arc (no Problem → Investigation → Resolution structure) | -20 | Fundamental rhetoric failure |
| Label title instead of assertion (e.g., "Results" not a claim) | -15 | Per frame — violates Critical Rule 3 |
| Multiple ideas on a single slide | -15 | Per slide — violates Critical Rule 4 |
| Unresolved `\cite{}` — `??` or `[?]` in output | -15 | Per broken citation |
| Unresolved `\ref{}` — `??` in output | -15 | Per broken reference |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Overfull hbox/vbox warning remaining | -5 | Per instance — violates Critical Rule 2 |
| Missing transitions between sections (audience loses thread) | -8 | Per missing transition |
| Aristotelian balance off (e.g., 0% pathos in teaching) | -5 | Once for the deck |
| Placeholder image instead of code-generated figure | -10 | Per figure — violates Critical Rule 6 |
| Figure axes unlabelled or legend missing | -5 | Per figure |
| Colour palette not accessible (low contrast, red-green reliance) | -5 | Once for the deck |
| `.bib` used but not validated | -8 | Once — violates Critical Rule 7 |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Conclusion-last instead of conclusion-first on a slide (Pyramid Principle) | -3 | Per slide |
| Speaker notes missing on key slides | -2 | Per key slide |
| Slide overloaded visually (too much text, cramped layout) | -3 | Per slide |
| Inconsistent font sizing across slides | -2 | Once for the deck |
| Minor TikZ alignment issue | -2 | Per diagram |
| Cognitive load spike (too much new information at once) | -3 | Per instance |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Compilation & warnings | Phase 3-4 |
| Rhetoric (arc, titles, one-idea) | Phase 5 |
| Graphics (figures, TikZ, colour) | Phase 6 |
| Final polish | Phase 7 |
