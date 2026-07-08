# Phase 8.3 — Review agent outputs

> Verify `reviews/` organisation follows the convention in `rules/review-artefact-routing.md`. Filename pattern: `reviews/<source>/YYYY-MM-DD.md` (or `YYYY-MM-DD-<descriptor>.md` for same-day reruns). The single allowed file at `reviews/` root is `INDEX.md`.

## Checks

| Check | What to look for | Severity |
|-------|-----------------|----------|
| `reviews/INDEX.md` exists | Required manifest at `reviews/` root | Required |
| Canonical source subdirs | Each subdir matches a slug in the rule's R1 source table | — |
| Variant source names | `referee2/` instead of `referee2-reviewer/`, `peer-review/` instead of `peer-reviewer/`, `fix/` instead of `fixer/`, etc. | Degraded → recommend `/tidy-project-reviews` |
| File naming | Files within subdirs follow `YYYY-MM-DD.md`, `YYYY-MM-DD-HHMM.md` (review-agent timestamp form, commit `23ebcfff` and later), or `YYYY-MM-DD-<descriptor>.md` | Degraded |
| Dual-file divergence | Both `reviews/INDEX.md` AND project-root `REVIEW-STATE.md` exist | Degraded → recommend `/tidy-project-reviews` (its Phase 5.2 dedup-merges by `(Check, Last Run)`) |
| Legacy 10-column INDEX.md | `reviews/INDEX.md` body starts with `\| Paper \| Check \| Last Run \| Verdict \| Score \| Open Issues \| Source \| Trigger \| Report \| Notes \|` instead of "## Latest per source" | Degraded — content schema lag from Batch A retrofit; recommend `/review-recap` to migrate |
| Stray files at `reviews/` root | Anything besides `INDEX.md` directly under `reviews/` | Degraded |
| Stray reports at project root | `CRITIC-REPORT.md`, `DOMAIN-REVIEW.md`, `REVIEW-STATE.md`, etc. at the project's top level | Degraded → recommend `/tidy-project-reviews` |
| Legacy `correspondence/internal-reviews/` | Dir exists with content | Legacy → recommend `/tidy-project-reviews` |
| Empty source subdirectories | `reviews/<source>/` exists but contains no files | Info |
| `reviews/<source>/archived/` ignored | If `.gitignore` doesn't include `reviews/**/archived/`, flag | Degraded |

## Canonical source slugs (R1 from the rule)


External AI tools: `codex-research`, `gemini-research`, `perplexity-manual`, `liner-manual`, `chatgpt-manual`, `claude-manual`, `external` (catch-all).

## Distinct from `correspondence/`

This check is for AI-produced review output (skills, agents, external tools). Human-produced content lives under `correspondence/` per the provenance test in rule R6:

- `correspondence/referee-reviews/` — venue referee reports (anonymous reviewer text)
- `correspondence/editorial/` — editor decisions and decision letters
- `correspondence/internal/` — supervisor / co-author feedback

A misclassified file (e.g. a paper-critic agent output filed under `correspondence/referee-reviews/`) is a Degraded finding — recommend `/tidy-project-reviews` to reclassify by content fingerprint.
