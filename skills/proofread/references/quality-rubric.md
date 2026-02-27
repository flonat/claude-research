# Quality Rubric: Proofread

> Scoring rubric for `/proofread`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Broken `\ref{}` producing `??` in output | -100 | Document has unresolved references — not submission-ready |
| Broken `\cite{}` producing `??` or `[?]` | -100 | Missing bibliography entries — not submission-ready |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Inconsistent core notation (e.g., `$x_i$` vs `$x_{i}$` for the same variable) | -15 | Per notation inconsistency pattern |
| Wrong citation command (`\cite` instead of `\citet`/`\citep` throughout) | -15 | Per systematic misuse pattern |
| Major grammar error (subject-verb disagreement, dangling modifier) | -15 | Per instance in body text |
| Major grammar error in abstract or introduction | -15 | Higher visibility = higher cost |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Informal contraction in body text (don't, can't) | -5 | Per unique contraction |
| Overfull hbox > 10pt | -5 | Per instance |
| Inconsistent citation ordering (mixed chronological/alphabetical) | -5 | Once for the pattern |
| British/American English mixing (systematic) | -5 | Once for the pattern |
| Equation referenced but unnumbered | -5 | Per instance |
| "As shown by (Author, Year)" instead of `\citet{}` | -5 | Per instance |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Academic tone slip (casual hedging, exclamation mark) | -3 | Per instance |
| Overfull hbox 1-10pt | -2 | Per instance |
| Minor spelling error (non-technical) | -1 | Per instance |
| Inconsistent tense (isolated, not systematic) | -2 | Per instance |
| Minor spacing or formatting inconsistency | -1 | Per instance |
| Paragraph opens with in-line citation unnecessarily | -2 | Per instance |
| "As shown by \citet{}" where parenthetical fits better | -2 | Per instance |

### Citation Voice Balance (-5 to -10)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| In-line:parenthetical ratio exceeds 1:1 | -10 | Once for the document — systematic overuse |
| Run of 3+ consecutive in-line citations | -5 | Per run (paragraph or section) |

## Category Mapping

| Rubric category | SKILL.md check category |
|----------------|------------------------|
| Grammar & spelling | Check 1 |
| Notation consistency | Check 2 |
| Citation format | Check 3 |
| Academic tone | Check 4 |
| LaTeX-specific | Check 5 |
| Citation voice balance | Check 6 |
| TikZ diagrams | Check 7 |
