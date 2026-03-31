# Fix Mode

> Referenced from: `bib-validate/SKILL.md`

After producing the validation report, automatically fix resolvable issues using the filing sequence from [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Auto-Fix Actions

1. **`DRIFT` entries** (in .bib but not in any reference manager):
   - Add to Zotero via `mcp__refpile__add_item` using metadata from the `.bib` entry.
   - File into topic collection + `_Needs Review` per the filing sequence.

2. **`MISSING` entries** (cited in .tex but not found anywhere):
   - Search via the resolution order (Zotero → Paperpile → bibliography MCP → Crossref → web).
   - If found, export correct BibTeX and add the entry to the `.bib` file.
   - Add to Zotero and file per the filing sequence.

3. **`MIGRATE_TO_ZOTERO` entries** (in Paperpile but not Zotero):
   - Auto-add to Zotero using Paperpile metadata.
   - File into topic collection + `_Needs Review`.

4. **Metadata issues** (DOI mismatch, stale preprint, missing fields):
   - Export correct BibTeX from Paperpile (`mcp__paperpile__export_bib`) or bibliography MCP (`scholarly_search`) for entries with metadata problems.
   - Present corrected entries for confirmation before overwriting.

## Post-Fix Maintenance

1. **Update `zotero-collections.md`** — increment item counts for affected collections.
2. **Report summary** — show a table of all fixes applied: entry key, issue, action taken, status.

## Skip Fix Mode

Fix mode is skipped when:
- The skill is invoked with `--report-only` or `--dry-run`
- No actionable issues are found (all entries are `HEALTHY`)
- Both refpile MCP and paperpile MCP are unavailable
