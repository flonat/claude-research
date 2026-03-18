# Reference Manager Sync — Phase 6c Details

> Referenced from: `literature/SKILL.md` Phase 6c

After assembling and validating the `.bib`, sync new references to the user's reference libraries. Follow the filing sequence defined in [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Zotero (Active Write Target)

For each new entry not marked **ALREADY IN ZOTERO** from Phase 1:

1. **Add to Zotero** — call `mcp__refpile__add_item` with full metadata (title, authors, year, journal, DOI, itemType).
2. **File into topic collection** — resolve the topic collection key (from Phase 1 step 6) and call `mcp__refpile__add_to_collection(collection_key=<topic_key>)`.
3. **Tag for review** — also call `mcp__refpile__add_to_collection` with the `_Needs Review` collection key. Items go into both the topic collection and `_Needs Review`.
4. **Report results** — show a summary table of what was added and which collections they were filed into.

## Paperpile (Read-Only Cross-Reference)

For each new entry not already in Paperpile:

1. **Report additions needed** — list entries that need manual import into Paperpile (Paperpile MCP is read-only; the user adds via the Paperpile app or browser extension).
2. **Export BibTeX** — if Paperpile has entries with better metadata than what was assembled, call `mcp__paperpile__export_bib` and use those entries instead.

## Migration Candidates

For entries found in Paperpile but not in Zotero (status `MIGRATE_TO_ZOTERO` from Phase 1):

1. **Auto-add to Zotero** using Paperpile metadata.
2. **File into topic collection + `_Needs Review`** per the filing sequence.
3. **Report** the migration count.

## Post-Run Maintenance

1. **Update `zotero-collections.md`** — increment item counts for affected collections.
2. **Report Paperpile gaps** — items the user should manually add to Paperpile.

**Graceful degradation:** If either MCP is unavailable, skip that source with a warning. The `.bib` file on disk is still the primary output.
