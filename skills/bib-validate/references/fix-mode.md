# Fix Mode

> Referenced from: `bib-validate/SKILL.md`

After producing the validation report, automatically fix resolvable issues using the filing sequence from [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Auto-Fix Actions

1. **`DRIFT` entries** (same paper IS in Paperpile, under a different citekey — locally-minted lookalike keys):
   - Run the verified rekey chain from Task-Management `scripts/bib/`:
     1. `rekey_to_canonical.py <bib> --apply` — remaps `\cite` keys in the `.tex` (pass `--extra-map OLD=NEW` for user-confirmed SUGGESTED/AMBIGUOUS cases; refuses on unresolved cited keys without `--force`)
     2. `rebuild_paperpile_bib.py <bib>` — regenerates the `.bib` from canonical Paperpile exports (generated-not-edited, per `rules/paperpile-citations.md`)
     3. `citation_lint.py <project>` — verify all cited keys canonical & present
     4. `latexmk` compile check — 0 undefined citations
   - Live-surface discipline applies (`rules/reconcile-before-rewriting.md`): fresh-Read baseline, dry-run mapping table shown before `--apply`.

2. **`NOT_FOUND` entries** (genuinely absent from the library — legacy alias: `MISSING`):
   - Search via the resolution order (Paperpile → `scholarly` CLI → Crossref → web).
   - If found, stage the entry as a `.bib` under `.paperpile-import/` and replace its draft cite with a build-blocking `\CiteTodo{slug}{title; authors; year; DOI}` — never a guessed key.
   - The Paperpile CLI is read-only (no import command). The user imports the staged `.bib` manually; after import they drop the minted export back into `.paperpile-import/` and the `\CiteTodo` is swapped to the canonical key. See `rules/paperpile-citations.md`.

3. **Metadata issues** (DOI mismatch, stale preprint, missing fields):
   - Export correct BibTeX from Paperpile (`paperpile export-bib`) or the `scholarly` CLI (`scholarly scholarly-search "<title>" --json`) for entries with metadata problems.
   - Present corrected entries for confirmation before overwriting.

## Post-Fix Maintenance

1. **Report summary** — show a table of all fixes applied: entry key, issue, action taken, status.
2. **Remind user to import** — if BibTeX was staged, remind to import into Paperpile.

## Skip Fix Mode

Fix mode is skipped when:
- The skill is invoked with `--report-only` or `--dry-run`
- No actionable issues are found (all entries are `HEALTHY`)
- the `paperpile` CLI is unavailable
