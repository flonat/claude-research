# Shared: Reference Resolution & Filing Sequence

Canonical lookup and filing sequence for all bibliography skills (`/literature`, `/bib-validate`, `/bib-parse`, `/bib-coverage`). Reference this module instead of reimplementing lookup logic.

## Resolution Order (Lookup)

When resolving a reference (checking if it exists, finding metadata, verifying DOIs), search in this order:

1. **Paperpile** (primary reference manager) — check membership **by DOI** (`paperpile lookup-by-doi`); `paperpile search-library` is a metadata-discovery aid, **not** a membership test (see "Membership Check" below). If found, reuse its `citekey`.
2. **Bibliography MCP** (scholarly sources) — `scholarly scholarly-search` across OpenAlex + Scopus + WoS for metadata enrichment.
3. **Crossref API** (DOI fallback) — `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` for DOI resolution.
4. **Web search** (last resort) — `WebSearch` for papers not found in any structured source.

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip it with a warning and continue with external sources.

## Membership Check — Before Tagging Any Reference `NEW`

**Verify Paperpile membership by DOI, never by topic/title search.** `paperpile search-library` is substring matching and is lossy — it misses papers whose stored title/metadata don't match the query terms, which is how citing-works walks, snowball discoveries, and hand-typed foundational papers get wrongly defaulted to `NEW`. A topic-search miss is **not** evidence of absence.

For **every** candidate reference — however it was found (Paperpile search, scholarly search, citing-works/snowball walk, or hand-typed classics) — before it can be tagged `NEW`:

1. **Collect its DOI** (verify the DOI itself first if unsure — a wrong DOI fails the lookup and produces a false `NEW`).
2. **Check membership by DOI:** `paperpile lookup-by-doi --doi <DOI> --json`. **Batch ≥6 candidates** — dispatch one Bash sub-agent that loops the lookups and returns a merged `{doi: citekey-or-null}` map (per [`_shared/cli-dispatch-policy.md`](../_shared/cli-dispatch-policy.md)), so the main context isn't flooded by per-call banners.
3. **Match → in Paperpile.** Use the returned citekey and pull the canonical entry with `paperpile export-bib --citekeys <key> --json`. Reconcile per "Key Reconciliation" below — do NOT invent a key or re-type metadata.
4. **No match → genuinely `NEW`.** Only now stage it for import and generate a BBT-style placeholder key.
5. **Mark every assembled `.bib` entry** `% IN PAPERPILE (<key>)` or `% NEW — add to Paperpile`, and report the IN-PAPERPILE / NEW split counts.

**Foundational classics are the most common false `NEW`.** Hand-typed canon (Simon, March, Levinthal, Cyert & March, …) is almost always already in the library — check them by DOI too; never assume they're new because you typed them from memory.

A DOI-less candidate can't be DOI-verified: fall back to the author+title `search-library` retry in trap 2 below, and flag it `% NEW (no DOI — membership unconfirmed)` rather than a clean `NEW`.

**A DOI-bearing candidate can still be a false `NEW` if the *held* copy is DOI-less.** `lookup-by-doi` matches the candidate's DOI against DOIs *stored in the library* — but arXiv/preprint items are frequently filed **without** the `10.48550/arXiv.*` DOI, so the lookup returns null even though the paper is held. (Incident 2026-07-04: `Hubinger2024-it` "Sleeper Agents", held with `journal = {arXiv [cs.CR]}` and no DOI, was mis-staged `NEW` because the arXiv-DOI lookup couldn't match a DOI-less library item — caught by the user, not the gate.) **For every arXiv/preprint candidate whose `lookup-by-doi` returns null, run a title + first-author `search-library` backstop before tagging `NEW`** (batch ≥6 via one Bash sub-agent, as above). A title hit → held: reconcile to its citekey. This is the mirror of the DOI-less-*candidate* case above — there the *candidate* lacks a DOI; here the *library item* does.

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

References with **no** Paperpile match — confirmed by the DOI Membership Check above, not merely a topic-search miss — are `NEW`; stage them for import per the Filing Sequence below. Do not invent a Paperpile key, and do not tag `NEW` off a `search-library` miss alone.

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

### 1. Stage under `.paperpile-import/`

Write the entry's BibTeX into a `.bib` file under a `.paperpile-import/` directory in the project (create it if absent). If the reference is cited in a draft, use a build-blocking `\CiteTodo{slug}{title; authors; year; DOI}` placeholder instead of a guessed key. The user imports the staged `.bib` into Paperpile manually — the CLI is **read-only** for the library (no import command; `paperpile write-bib --citekeys` only *exports* entries already in the library). After import, the user drops the minted Paperpile export (carrying the canonical key) back into `.paperpile-import/`; the `\CiteTodo` is then swapped to that key and the active `.bib` rebuilt. See `rules/paperpile-citations.md`.

**Convention:** stage under `.paperpile-import/` (the staging dir, excluded from the active bib by `rebuild_paperpile_bib.py`) — NOT a `paperpile-stage-*.bib` in the project root (the old convention, superseded).

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
