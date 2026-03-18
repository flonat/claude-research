# Shared: Reference Resolution & Filing Sequence

Canonical lookup and filing sequence for all bibliography skills (`/literature`, `/bib-validate`, `/bib-parse`, `/bib-coverage`). Reference this module instead of reimplementing lookup logic.

## Resolution Order (Lookup)

When resolving a reference (checking if it exists, finding metadata, verifying DOIs), search in this order:

1. **Zotero** (active write target) — `mcp__refpile__search_library` by title/author. If found, reuse its `citationKey`.
2. **Paperpile** (read-only cross-reference) — `mcp__paperpile__search_library` by title/author. If found, note for status reporting. Paperpile is read-only; items cannot be added via MCP.
3. **Bibliography MCP** (scholarly sources) — `scholarly_search` across OpenAlex + Scopus + WoS for metadata enrichment.
4. **Crossref API** (DOI fallback) — `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` for DOI resolution.
5. **Web search** (last resort) — `WebSearch` for papers not found in any structured source.

**Graceful degradation:** If any MCP is unavailable, skip it with a warning and continue with the remaining sources.

## Status Categories

Based on where a reference is found, assign one of these statuses:

| Zotero | Paperpile | .bib | Status | Action |
|--------|-----------|------|--------|--------|
| Yes | Yes | Yes | `HEALTHY` | No action needed |
| Yes | — | Yes | `HEALTHY` | No action needed |
| No | Yes | Yes | `MIGRATE_TO_ZOTERO` | Auto-add to Zotero from Paperpile metadata |
| No | No | Yes | `DRIFT` | In local .bib but not in any reference manager — auto-add to Zotero |
| Yes | — | No | `EXPORT_GAP` | In Zotero but not in local .bib — export or cite |
| No | Yes | No | `EXPORT_GAP` | In Paperpile but not in local .bib — export or cite |
| No | No | No | `MISSING` | Not found anywhere — add via filing sequence below |

## Filing Sequence (Adding Items)

When a skill needs to add a reference to Zotero, follow this sequence:

### 1. Add to Zotero

Call `mcp__refpile__add_item` with full metadata (title, authors, year, journal/booktitle, DOI, itemType).

### 2. File into topic collection

Resolve the topic collection key from `zotero-collections.md` (in the project's research directory or the Task Management `.context/resources/` folder):

- **Explicit argument:** If the user passed `--topic <slug>`, use that slug to look up the collection key.
- **Project context:** Read the project's `CLAUDE.md` or topic frontmatter for the Atlas topic slug.
- **Directory name:** If inside a research project directory, use the directory name as the topic slug.

Call `mcp__refpile__add_to_collection(collection_key=<resolved_key>)` to file the item into the topic-specific collection.

### 3. Also tag for review

Call `mcp__refpile__add_to_collection` with the `_Needs Review` collection key. Items go into **both** the topic collection and `_Needs Review` — the topic collection for organisation, `_Needs Review` for the user to verify.

### 4. Report Paperpile gaps

List items that need manual import into Paperpile (read-only MCP — user must add via Paperpile app or browser extension).

### 5. Fallback

If the topic collection key cannot be resolved (no `--topic` argument, no project context, slug not found in `zotero-collections.md`), file into `_Needs Review` only and warn:

> "Could not resolve topic collection — filed into `_Needs Review` only. Specify `--topic <slug>` or ensure the project has an Atlas topic."

## Post-Run Maintenance

After any skill run that adds items to Zotero:

1. **Update `zotero-collections.md`** — increment item counts for affected collections.
2. **Report migration candidates** — list items found in Paperpile but not in Zotero as `MIGRATE_TO_ZOTERO`. Offer to auto-add them.

## Skills That Reference This Module

| Skill | Uses Resolution | Uses Filing | Notes |
|-------|----------------|-------------|-------|
| `/literature` | Phase 1 (pre-search check) | Phase 6c (sync to managers) | Full workflow |
| `/bib-validate` | Ref Manager Cross-Reference | Fix Mode (auto-add) | Reports + optional fixes |
| `/bib-parse` | Phase 3.5 (library check) | Phase 6.5 (sync to Zotero) | PDF extraction workflow |
| `/bib-coverage` | Collection comparison | — | Read-only comparison |
