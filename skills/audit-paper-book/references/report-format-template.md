# Report Format

Canonical audit report written to `~/vault/books/<slug>/.audit-report-YYYY-MM-DD.md`. Produced in every run regardless of `--apply` (when `--apply` is omitted, the report is the only output; when set, it logs what was changed and what's still pending).

## Template

```markdown
# Audit report — <slug>

**Date:** YYYY-MM-DD
**Mode:** report-only | applied
**Paper revision:** <git-sha-or-mtime of paper tex>
**Book last touched:** <git-sha-or-mtime of book vault dir>

## Summary

| Bucket | Count | Status |
|---|---:|---|
| Mechanical (bib + figures) | N | applied / pending |
| Overleaf-link (masthead) | N | applied / pending |
| Format-convention (masthead migration + H1 strip) | N | applied / pending |
| Citation-URL (hand-constructed `/paper/` links) | N | pending — user triage |
| Numeric | N | pending — user triage |
| Structural | N | pending — user triage |
| Accessibility | N | pending — user triage |
| New content | N | pending — user triage |

## Mechanical fixes

### New bib entries (N)
- `Smith2026-xx` — Smith, J. (2026). Title. *Journal*, 12(3). doi:10.xxxx
- ...

### New / changed figures (N)
- `figures/new_plot.png` — added (paper §5)
- `figures/budget_vs_harm.png` — content changed (mtime newer)
- ...

## Numeric drift

| Where in book | Old number | New paper number | Action |
|---|---|---|---|
| `results.md` line 42 | 2.82 ± 1.4 | 2.78 ± 1.2 | Update `results.md` to match paper §5.1 |

## Structural drift

| Paper change | Affected chapter | Suggested action |
|---|---|---|
| §4.5 added "Cost-aware selection" | `method.md` | Add a section after the VOI rule |
| §6 renamed to "Limitations and ethics" | `limitations.md` | Update chapter title + opening |

## Format-convention drift

| Type | Where | Action |
|---|---|---|
| Blockquote masthead | `intro.md` lines 6–9 | Migrated to definition-list (applied) |
| Redundant body H1 | `method.md` line 6 (`# Method`) | Stripped (applied) |
| Missing required field | `intro.md` masthead has no `Venue:` | Add field (manual) |

## Citation-URL drift

| Chapter | Line | Hand-constructed URL | Suggested replacement |
|---|---|---|---|
| `results.md` | 87 | `[Wells2021](https://atlas.example.com/paper/Wells2021-fb)` | `` {cite:t}`Wells2021-fb` `` |

## New content (no echo in book)

| Paper element | Book gap | Suggested action |
|---|---|---|
| Theorem 3 (paper §3.4) | No mention in `method.md` | Add a callout/short subsection summarising the result |

## Next actions

1. (optional) Re-run with `--apply` to take the mechanical fixes.
2. Triage numeric drift in `results.md`.
3. Add a sub-section in `method.md` for Theorem 3.
4. (optional) Run `/init-paper-book <slug>` only if the paper has restructured drastically — usually `audit` is faster.
```

## When sections are omitted

- **Mechanical fixes** — omit subsection when count is zero (don't print an empty section).
- **Format-convention drift** — same.
- **Citation-URL drift** — same.
- **Numeric / Structural / New content** — always include the section header even with zero items, so the report's structure is parseable.

The Summary table always lists all eight buckets, with `0` counts where applicable.
