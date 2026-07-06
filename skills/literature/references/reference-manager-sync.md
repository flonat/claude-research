# Reference Manager Sync — Phase 6c Details

> Referenced from: `literature/SKILL.md` Phase 6c

After assembling and validating the `.bib`, sync new references to Paperpile. Follow the filing sequence defined in [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Paperpile (Primary Reference Manager)

For each new entry not marked **ALREADY IN PAPERPILE** from Phase 1:

1. **Stage under `.paperpile-import/`** — write the new entry's BibTeX into a `.bib` under `.paperpile-import/` (Paperpile CLI is read-only; `write-bib --citekeys` only exports entries already in the library). Use a `\CiteTodo{...}` placeholder for any draft cite until imported.
2. **Report results** — show a summary table of what was staged for import.
3. **Remind user** — "Import the staged `.bib` under `.paperpile-import/` into Paperpile to complete the sync."

For entries already in Paperpile with better metadata than what was assembled, call `paperpile export-bib` and use those entries instead.

## Post-Run Maintenance

1. **Report what was staged** — list new `.bib` entries with file path.
2. **Remind user to import** into Paperpile.

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip with a warning. The `.bib` file on disk is still the primary output.
