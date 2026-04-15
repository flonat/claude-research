# Fix Mode

> Referenced from: `bib-validate/SKILL.md`

After producing the validation report, automatically fix resolvable issues using the filing sequence from [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Auto-Fix Actions

1. **`DRIFT` entries** (in .bib but not in Paperpile):
   - Stage as BibTeX via `mcp__paperpile__write_bib` (output: `paperpile-stage-YYYY-MM-DD-HHMM.bib` in the project root).

2. **`MISSING` entries** (cited in .tex but not found anywhere):
   - Search via the resolution order (Paperpile → bibliography MCP → Crossref → web).
   - If found, export correct BibTeX and add the entry to the `.bib` file.
   - Stage for Paperpile import via `mcp__paperpile__write_bib`.

3. **Metadata issues** (DOI mismatch, stale preprint, missing fields):
   - Export correct BibTeX from Paperpile (`mcp__paperpile__export_bib`) or bibliography MCP (`scholarly_search`) for entries with metadata problems.
   - Present corrected entries for confirmation before overwriting.

## Post-Fix Maintenance

1. **Report summary** — show a table of all fixes applied: entry key, issue, action taken, status.
2. **Remind user to import** — if BibTeX was staged, remind to import into Paperpile.

## Skip Fix Mode

Fix mode is skipped when:
- The skill is invoked with `--report-only` or `--dry-run`
- No actionable issues are found (all entries are `HEALTHY`)
- Paperpile MCP is unavailable
