# Reference Manager Sync — Phase 6c Details

> Referenced from: `literature/SKILL.md` Phase 6c

After assembling and validating the `.bib`, sync new references to Paperpile. Follow the filing sequence defined in [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Paperpile (Primary Reference Manager)

For each new entry not marked **ALREADY IN PAPERPILE** from Phase 1:

1. **Stage as BibTeX** — call `mcp__paperpile__write_bib` with full metadata to generate a `.bib` staging file.
2. **Report results** — show a summary table of what was staged for import.
3. **Remind user** — "Import the staged `.bib` file into Paperpile to complete the sync."

For entries already in Paperpile with better metadata than what was assembled, call `mcp__paperpile__export_bib` and use those entries instead.

## Post-Run Maintenance

1. **Report what was staged** — list new `.bib` entries with file path.
2. **Remind user to import** into Paperpile.

**Graceful degradation:** If Paperpile MCP is unavailable, skip with a warning. The `.bib` file on disk is still the primary output.
