# Integrity Verification Gates — Shared Protocol

> Pipeline-blocking checkpoints that prevent progression until citations, claims, and data are verified. Referenced by skills that produce or consume academic references.

## Core Principle

**No output file may contain an unverified reference.** Verification gates are hard blockers — not advisory warnings. A gate that fails prevents the pipeline from advancing. There is no "difficult to verify" category; every item must reach a terminal verdict.

## When This Protocol Applies

Any skill that writes references to output files:
- `/literature` — Phase 4 (synthesis) blocked until Phase 2 (verification) passes
- `/hypothesis-generation` — claims must cite verified sources
- `/bib-validate` — deep-verify mode is an integrity gate
- Paper-critic / domain-reviewer — can flag gate failures as blocking issues

## Gate Architecture

### Gate 1: Reference Existence (mandatory, 100% coverage)

Every reference written to any output must pass:

| Verdict | Condition | Action |
|---------|-----------|--------|
| VERIFIED | Found in 2+ databases (Crossref, OpenAlex, Scopus, S2) with matching metadata | Safe to write |
| SINGLE_SOURCE | Found in exactly 1 database | Write, flag as low-confidence |
| NOT_FOUND | Zero hits after 3 distinct search strategies | **Block — do not write** |
| MISMATCH | Similar paper found but metadata differs (wrong year, wrong authors, wrong venue) | **Block — do not write until corrected** |

### Gate 2: Bibliographic Accuracy (mandatory for VERIFIED refs)

For each verified reference, compare field-by-field:

| Field | Severity if wrong |
|-------|------------------|
| Authors (names, count, order) | SERIOUS |
| Year | SERIOUS |
| Title (exact match) | SERIOUS |
| Journal/venue name | SERIOUS |
| DOI | SERIOUS |
| Volume/issue/pages | MEDIUM |
| URL accessibility | MINOR |

### Gate 3: Claim-Source Alignment (sampling, 30%+ of claims)

For quantitative or factual claims derived from references:

| Verdict | Definition |
|---------|-----------|
| VERIFIED | Claim matches source exactly or within rounding |
| MINOR_DISTORTION | Meaning preserved but wording oversimplifies |
| MAJOR_DISTORTION | Claim exaggerates, misrepresents, or contradicts source |
| UNVERIFIABLE | Source doesn't contain the claimed information |

**Block on:** Any MAJOR_DISTORTION or UNVERIFIABLE verdict.

### Gate 4: Internal Consistency (mandatory)

- Same data point consistent across all mentions in the document
- Calculations correct (percentages, totals, ratios)
- Tables match prose descriptions
- No contradictions between sections

## Anti-Hallucination Rules

These rules override AI confidence:

1. **Never verify from memory.** Every reference must be checked via an external source (MCP tool, API, or web search) — regardless of how familiar it seems.
2. **No gray zones.** "Difficult to verify" is not a verdict. Classify as NOT_FOUND after 3 search attempts.
3. **Cross-check mashups.** When multiple references share authors or similar titles, verify each is a distinct real publication — not a hallucinated blend of two real papers.
4. **Book chapters need enhanced verification.** Confirm the specific chapter exists (not just the book) with correct authors, title, and page range.
5. **DOI misdirection.** If a DOI resolves to an unrelated paper, classify as MISMATCH.

## Known Hallucination Patterns

| Pattern | Description | Detection |
|---------|-------------|-----------|
| Total Fabrication | Entire paper doesn't exist | Zero hits across all sources |
| Plausible Author | Real scholar attributed to paper they never wrote | Check author's actual publication list |
| Mashup | Elements from 2-3 real papers blended into one fake | Cross-verify ALL metadata against ONE source |
| Subtle Distortion | Minor changes to a real paper (wrong year, expanded initials) | Compare each field against publisher page |
| DOI Misdirection | Fabricated DOI resolves to unrelated paper | Follow DOI and compare title/authors |

## Provenance Audit Trail

Every verified reference must have a traceable verification record:

```
Reference: {author} ({year}). {title}. {venue}.
Search 1: [query] → [result URL] → [matched fields]
Search 2: [query] → [result URL] → [confirmed/contradicted]
Verdict: VERIFIED | NOT_FOUND | MISMATCH
Verified via: [tool name] on [date]
```

Skills that write references should maintain this trail in a machine-readable format (JSON lines or structured markdown) so that subsequent skills can skip re-verification for already-verified items.

## Gate Verdicts and Pipeline Progression

| Gate result | Pipeline action |
|-------------|----------------|
| ALL PASS | Proceed to next stage |
| PASS WITH NOTES | Proceed; attach notes for human review |
| ANY FAIL (SERIOUS/MEDIUM) | **Block.** Produce correction list. Re-verify after fixes. Max 3 rounds. |
| FAIL after 3 rounds | Escalate to user with unresolvable items listed |

## Integration Points

### With existing `doi-verification` rule
The global rule (`rules/doi-verification.md`) establishes the "verify before writing" principle. This protocol extends it with:
- Formal gate verdicts (not just "check first")
- Pipeline blocking (not just flagging)
- Anti-hallucination taxonomy
- Audit trail requirements

### With `sources-cache.md`
Verified references can be cached in the sources cache to avoid redundant re-verification within a session. Cache entries expire after 24 hours.

### With paper-critic agent
Paper-critic should check whether the integrity gate was run. If no audit trail exists, flag as a blocking issue: "No integrity verification performed — run Gate 1-2 before review."

## Sampling Strategy by Context

| Context | Gate 1 | Gate 2 | Gate 3 | Gate 4 |
|---------|--------|--------|--------|--------|
| Literature review output | 100% | 100% | 30% | 100% |
| Paper draft (pre-review) | 100% | 100% | 30% | 100% |
| Paper draft (post-revision) | 100% | 100% | 100% | 100% |
| Hypothesis generation | 100% | 50% | 50% | N/A |
| Quick bibliography check | 100% | 50% | N/A | N/A |
