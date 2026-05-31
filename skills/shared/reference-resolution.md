# Shared: Reference Resolution & Filing Sequence

Canonical lookup and filing sequence for all bibliography skills (`/literature`, `/bib-validate`, `/bib-parse`, `/bib-coverage`). Reference this module instead of reimplementing lookup logic.

## Resolution Order (Lookup)

When resolving a reference (checking if it exists, finding metadata, verifying DOIs), search in this order:

1. **Paperpile** (primary reference manager) — `paperpile search-library` or `paperpile lookup-by-doi` if DOI is known. If found, reuse its `citekey`.
2. **Bibliography MCP** (scholarly sources) — `scholarly scholarly-search` across OpenAlex + Scopus + WoS for metadata enrichment.
3. **Crossref API** (DOI fallback) — `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` for DOI resolution.
4. **Web search** (last resort) — `WebSearch` for papers not found in any structured source.

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip it with a warning and continue with external sources.

## Key Reconciliation (when a reference matches an existing Paperpile item)

### Use the helper — never hand-roll the matcher

**For any reconciliation of more than a handful of entries, call `skills/_shared/reconcile_bib.py` instead of writing an ad-hoc matching loop.** Hand-rolled fuzzy matchers caused an unrecoverable file corruption on 2026-05-30 (a surname+year matcher collapsed one author's four papers onto a single key, with no backup). The helper bakes in the invariants below.

```bash
python3 ~/.claude/skills/_shared/reconcile_bib.py <bib>                  # dry-run report (default)
python3 ~/.claude/skills/_shared/reconcile_bib.py <bib> --apply         # swap keys + backfill DOIs (backs up first)
python3 ~/.claude/skills/_shared/reconcile_bib.py <bib> --apply --enrich # also Crossref-by-DOI enrich authors/journal/vol/pages
```

**Non-negotiable invariants (the helper enforces them; honour them in any manual fallback):**

1. **Back up before any mutation.** Copy `<bib>` → `<bib>.bak-<UTC>` before writing. A destructive bulk rewrite with no backup is how a corruption becomes unrecoverable.
2. **Dry-run first.** Report matched / NEW / conflicts; apply only after the report looks right.
3. **DOI-first, then STRICT triple match.** Match on exact DOI, else require *all three*: folded-title similarity ≥ 0.85 **AND** exact first-author surname **AND** exact year. Never `surname-prefix AND (year OR title)` — that "OR" is what collapses one author's multiple papers.
4. **Bijective (one-to-one).** Each Paperpile key may be claimed by at most one local entry; a second claim is a **CONFLICT**, reported and left NEW — never silently merged onto the same key.
5. **Abort on duplicate keys.** After applying, if the result contains any duplicate citekey, abort and keep the backup — do not write.
6. **Consistent diacritic folding on both sides** (LaTeX `\'o` → `o` *and* Unicode `ó` → `o` via NFKD), so `Mikl{\'o}s-Thal` and `Miklós-Thal` compare equal.

### What reconciliation copies

When the helper (or a manual fallback) finds a Paperpile match, reconcile the local `.bib` entry as follows:

1. **Copy the Paperpile citekey into the local entry** — replace the locally-generated Better BibTeX key with the Paperpile `citekey` so `\cite{}` resolves against the user's library. This is the default behaviour, not optional.
2. **Backfill the DOI** from Paperpile if the local entry lacks one (`paperpile export-bib --citekeys <key>` / `lookup-by-doi` carries DOIs the source PDF often doesn't print).
3. **Keep the richer local metadata** — do NOT wholesale-replace the local entry with Paperpile's `export-bib` output. Paperpile's export is metadata-thin: it emits everything as `@misc`, abbreviates authors (`Calvano E and ...`), and frequently omits `journal`/`volume`/`pages`. Take only the key + DOI from Paperpile; keep the local entry's type, journal, volume, pages, and full author names.
4. **Leave a breadcrumb** — add `note = {key reconciled to Paperpile <key>}` (or append to an existing note) so the swap is auditable.

Working-paper → published **year drift** (e.g. local SSRN/NBER 2023 vs Paperpile published 2025) is a genuine match, not a conflict: adopt the Paperpile (published) key — it's the version the user will cite.

### Two recall/normalization traps (both cost real matches on 2026-05-30)

1. **Fold diacritics consistently on BOTH sides before comparing surnames.** A local `.bib` LaTeX-escaped name (`Mikl{\'o}s-Thal`) and Paperpile's Unicode form (`Miklós-Thal`) must normalize to the *same* string. Naively stripping `{}\` leaves the base letter (`Mikl'os` → `miklos`) while stripping non-ASCII deletes the accented char entirely (`Miklós` → `mikls`) — the prefixes then diverge and a true top-hit match is silently rejected. Fix: convert LaTeX accent escapes to their base letter AND `unicodedata.normalize('NFKD', s)` + drop combining marks on the Paperpile side, so both collapse to `miklos`. Never compare a LaTeX-stripped string against a non-ASCII-stripped string.
2. **Query with first-author surname + title keywords, and use a generous limit (≥10).** A title-only query on a topic the library is dense in (e.g. `competition pricing algorithms`) buries the true match below the result cutoff — it never enters the candidate set even though it exists. Always include the first-author surname in the search query; if a DOI is known, prefer `lookup-by-doi` (exact). If a title-only search misses, retry with author added before concluding `NEW`.

References with **no** Paperpile match are `NEW` — stage them for import per the Filing Sequence below; do not invent a Paperpile key.

> Rationale: this is the reconciliation behaviour applied in the 2026-05-30 Werner-2024 bib-parse run — copy keys + backfill DOIs, keep the fuller local metadata. Codified here so `/bib-parse`, `/bib-validate` (fix mode), `/literature` (Phase 4.4), and `/bib-coverage` all behave the same way.

## Status Categories

Based on where a reference is found, assign one of these statuses:

| Paperpile | .bib | Status | Action |
|-----------|------|--------|--------|
| Yes | Yes | `HEALTHY` | No action needed |
| Yes | No | `EXPORT_GAP` | In Paperpile but not in local .bib — export or cite |
| No | Yes | `DRIFT` | In local .bib but not in Paperpile — stage BibTeX for import |
| No | No | `MISSING` | Not found anywhere — add via filing sequence below |

## Filing Sequence (Adding Items)

When a skill needs to add a reference, follow this sequence:

### 1. Stage as BibTeX

Call `paperpile write-bib` with full metadata to generate a `.bib` file. The user imports this into Paperpile manually (Paperpile's BibTeX import handles deduplication).

**Naming convention:** `paperpile-stage-YYYY-MM-DD-HHMM.bib` — written to the project's root directory. The `paperpile-stage-` prefix distinguishes staging files from project bibliographies (`references.bib`). Timestamp prevents collisions across multiple runs.

### 2. Report to user

Present a summary table of what was staged:

| # | Citekey | Title | Status | Action |
|---|---------|-------|--------|--------|
| 1 | Smith2020-xy | Title... | MISSING — staged for import | |
| 2 | Doe2019-ab | Title... | ALREADY IN PAPERPILE (skipped) | |

### 3. Fallback

If `write_bib` fails or the `paperpile` CLI is unavailable, write a standard `.bib` file to disk and instruct the user to import it manually.

## Post-Run Maintenance

After any skill run that stages items for Paperpile import:

1. **Report what was staged** — list new `.bib` entries with file path.
2. **Remind user to import** — "Import `<path>` into Paperpile to complete the sync."

## Skills That Reference This Module

| Skill | Uses Resolution | Uses Filing | Notes |
|-------|----------------|-------------|-------|
| `/literature` | Phase 1 (pre-search check) | Phase 6c (sync to Paperpile) | Full workflow |
| `/bib-validate` | Ref Manager Cross-Reference | Fix Mode (auto-stage) | Reports + optional fixes |
| `/bib-parse` | Phase 3.5 (library check) | Phase 6.5 (stage for Paperpile) | PDF extraction workflow |
| `/bib-coverage` | Label comparison | — | Read-only comparison |
