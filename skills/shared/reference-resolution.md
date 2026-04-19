# Shared: Reference Resolution & Filing Sequence

Canonical lookup and filing sequence for all bibliography skills (`/literature`, `/bib-validate`, `/bib-parse`, `/bib-coverage`). Reference this module instead of reimplementing lookup logic.

## Resolution Order (Lookup)

When resolving a reference (checking if it exists, finding metadata, verifying DOIs), search in this order:

1. **Paperpile** (primary reference manager) — `paperpile search-library` or `paperpile lookup-by-doi` if DOI is known. If found, reuse its `citekey`.
2. **Bibliography MCP** (scholarly sources) — `scholarly scholarly-search` across OpenAlex + Scopus + WoS for metadata enrichment.
3. **Crossref API** (DOI fallback) — `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` for DOI resolution.
4. **Web search** (last resort) — `WebSearch` for papers not found in any structured source.

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip it with a warning and continue with external sources.

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
