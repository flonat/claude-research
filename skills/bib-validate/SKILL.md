---
name: bib-validate
description: "Use when cross-referencing LaTeX citation keys against .bib files or bibliography entries to find missing, unused, or mismatched references before compilation. Validates BibTeX metadata, detects stale preprints, and syncs with Zotero/Paperpile."
allowed-tools: Read, Glob, Grep, Task, Write, Bash(mkdir*), Bash(ls*), Bash(rm*), mcp__refpile__add_item, mcp__refpile__add_to_collection, mcp__refpile__search_library
argument-hint: [project-path or tex-file]
---

# Bibliography Validation

**Citation key rule:** Existing keys in the project always take precedence. They come from the user's reference management system and are canonical. When suggesting replacements (typo corrections, preprint upgrades, metadata fixes), always keep the user's key and update the `.bib` entry metadata around it — never suggest renaming a key to match some "standard" format.

## When to Use

- Before compiling a final version of a paper
- After adding new citations to check nothing was missed
- When `biber`/`bibtex` reports undefined citations
- As part of a pre-submission checklist (pair with `/proofread`)

## When NOT to Use

- **Finding new references** — use `/literature` for discovery
- **Building a bibliography from scratch** — use `/literature` with `.bib` generation
- **General proofreading** — use `/proofread` (which also flags citation format issues)

## Phase 0: Session Log (Suggested)

Bibliography validation with preprint staleness checks can be context-heavy (OpenAlex lookups, web searches for published versions). Before starting, **suggest** running `/session-log` to capture prior work as a recovery checkpoint. If the user declines, proceed without it.

## Convention

**Default bibliography file is `references.bib`** — this is the standard across all projects (per the `/latex` skill convention). The skill also supports any `.bib` file found in the same directory as the `.tex` files, embedded bibliographies using `\begin{thebibliography}` / `\bibitem{key}` blocks, or both simultaneously.

## Bibliography Detection

At the start of validation, detect which bibliography method the project uses:

### 1. External `.bib` file (standard)

Look for `.bib` files in the project directory. Priority: `references.bib` first, then any other `.bib` file in the `.tex` directory. If **multiple `.bib` files** are found, validate all and produce a combined report noting which file each issue belongs to. Flag legacy-named files (e.g., `paperpile.bib`) alongside `references.bib` as potential cleanup opportunities. Full validation applies: cross-reference checks **and** quality checks.

### 2. Embedded `\begin{thebibliography}` / `\bibitem{key}`

Detect by scanning `.tex` files for `\begin{thebibliography}`. Extract keys from `\bibitem{key}` (standard) and `\bibitem[label]{key}` (optional label — key is in the second set of braces). Only **cross-reference checks** apply; quality checks are skipped because embedded bibliographies lack structured metadata.

### 3. Both (rare)

If a project has both, validate the `.bib` file fully and run cross-reference checks on `\bibitem` entries, merging both key sets when checking for missing citations.

## Workflow

1. **Find files**: Locate all `.tex` files in the project
2. **Detect bibliography type**: Check for `.bib` files and/or `\begin{thebibliography}` blocks
3. **Extract citation keys from .tex**: Scan for all citation commands
4. **Extract entry keys from bibliography source(s)**:
   - External: Parse all `@type{key,` entries from `.bib` file(s)
   - Embedded: Parse all `\bibitem{key}` and `\bibitem[label]{key}` entries
5. **Cross-reference**: Compare the two sets
6. **Quality checks**: Validate `.bib` entry completeness (external only)
7. **Produce report**: Write results to stdout (or save if requested)

## Citation Commands to Scan

Scan `.tex` files for all `\cite`, `\citet`, `\citep`, `\textcite`, `\autocite`, `\parencite`, `\citeauthor`, `\citeyear`, and `\nocite` commands. Also handle **multi-key citations**: `\citep{key1, key2, key3}`.

## Cross-Reference Checks

### Critical: Missing Entries

Citation keys used in `.tex` but not defined in the bibliography source (`.bib` file or `\bibitem` entries).

These will cause compilation errors.

### Warning: Unused Entries

Keys defined in the bibliography source but never cited in any `.tex` file.

Not errors, but may indicate:
- Forgotten citations (should they be `\nocite`?)
- Leftover entries from earlier drafts
- Entries intended for a different paper

### Warning: Possible Typos (Fuzzy Match)

For each missing key, check if a similar key exists in the bibliography using edit distance:
- Edit distance = 1: Very likely a typo
- Edit distance = 2: Possibly a typo
- Flag these with the suggested correction

Common typo patterns:
- Year off by one: `smith2020` vs `smith2021`
- Missing/extra letter: `santanna` vs `sant'anna` vs `santana`
- Underscore vs camelCase: `smith_jones` vs `smithjones`

## Reference Manager Cross-Reference

After the disk-based cross-reference, check each cited key against the user's reference libraries using the resolution order from [`shared/reference-resolution.md`](../shared/reference-resolution.md). Two sources are available — check both when possible.

### Zotero (Active Write Target — via RefPile MCP)

Cross-reference via the `refpile` MCP server. For each citation key:

1. Call `mcp__refpile__search_library` with the citation key as query
2. Match on the `citationKey` field in results

### Paperpile (Read-Only Cross-Reference)

Cross-reference via the `paperpile` MCP server. For each citation key found in the `.tex` files:

1. Call `mcp__paperpile__search_library` with the citation key as query
2. Match on the citekey field in results
3. For entries with issues, call `mcp__paperpile__get_item` for full metadata
4. Use `mcp__paperpile__export_bib` to generate correct BibTeX for missing/outdated entries

**Additional checks:**
- Call `mcp__paperpile__get_labels` to verify folder organisation matches project themes
- For projects with a known Paperpile label, call `mcp__paperpile__get_items_by_label` to find papers in the folder but not cited (potential missing citations)

### Combined Status Categories

| .bib | Zotero | Paperpile | Status | Report |
|------|--------|-----------|--------|--------|
| Yes | Yes | Yes | `HEALTHY` | `✓ In sync across all` |
| Yes | Yes | No | `HEALTHY` | `✓ Zotero ↔ .bib in sync (not in Paperpile)` |
| Yes | No | Yes | `MIGRATE_TO_ZOTERO` | `⚠ In Paperpile + .bib but not Zotero — auto-add?` |
| Yes | No | No | `DRIFT` | `⚠ In local .bib but not in any reference manager` |
| No | Yes | — | `EXPORT_GAP` | `ℹ In Zotero but not exported to local .bib` |
| No | No | Yes | `EXPORT_GAP` | `ℹ In Paperpile but not exported to local .bib` |
| No | No | No | `MISSING` | `✗ Missing from all — will add to Zotero in Fix Mode` |

Include this as a "Reference Manager Sync" section in the report, after cross-reference results and before quality checks.

**Graceful degradation:** If either MCP is unavailable, skip that source with a warning and continue with whatever is available. If both are unavailable, continue with disk-only validation.

## Quality Checks on .bib Entries

**These checks apply only to external `.bib` files.** Embedded bibliographies lack structured metadata, so quality checks are skipped for them.

### Required Fields

Check each entry type has its standard required BibTeX fields (author, title, year, plus type-specific fields like journal for `@article`, booktitle for `@inproceedings`, publisher for `@book`, etc.).

### Year and Author Checks

- Flag entries with year < 1900, year > current year + 1, or no year
- Flag "and others" or "et al." in author fields — never valid in BibTeX (Warning)
- Flag inconsistent author formats and unbraced organisation names

### DOI Resolution (optional — `--verify-dois` flag)

**Preferred:** Call `scholarly_verify_dois` with all DOIs (up to 50 per call) for batch verification across OpenAlex, Scopus, WoS. Results: VERIFIED (2+ sources), SINGLE_SOURCE (spot-check), NOT_FOUND (resolve manually).

**Fallback for NOT_FOUND:** Resolve via `https://doi.org/[DOI]` and check title/author/journal match. Flag mismatches as Warning. Process in batches of 5.

### Preprint Staleness Check

**For every entry that looks like a preprint**, check whether a peer-reviewed version has since been published. Full detection signals, lookup protocol, and classification: [`references/preprint-check.md`](references/preprint-check.md)

## Severity Levels

| Level | Meaning |
|-------|---------|
| **Critical** | Missing entry for a cited key — will cause compilation error |
| **Warning** | Unused entry, possible typo, missing required field |
| **Info** | Year oddity, formatting suggestion, bibliography type note |

## Bibliography Output

After validation, offer these actions if applicable:

- **Embedded bibliography → offer to create `references.bib`**: If the project uses `\begin{thebibliography}`, offer to extract the references into a proper `references.bib` file (one `@misc` entry per `\bibitem`, with the full text as a `note` field). The author can then enrich the entries with proper metadata.
- **Non-standard `.bib` name → offer to rename**: If the existing `.bib` file is not named `references.bib`, offer to rename it to `references.bib` and update the `\bibliography{}` command in the `.tex` file.

These are **offers only** — do not make changes without explicit confirmation.

## Report Format

Full report template with all sections: [`references/report-template.md`](references/report-template.md)

Sections: Summary table → Critical (missing entries) → Warning (typos, unused, missing fields, DOI mismatches, stale preprints) → Info (year issues) → Limitations (for embedded bibliographies).

## Metadata Verification via MCP Tools

When missing entries or suspicious metadata are flagged, check these sources in order: (1) **Paperpile** — `mcp__paperpile__search_library` by title, then `mcp__paperpile__export_bib` for correct BibTeX; (2) **Zotero** — `search_library` by title; (3) **Bibliography MCP** — `scholarly_search` by title across OpenAlex + Scopus + WoS, `scholarly_verify_dois` for batch DOI verification, `openalex_lookup_doi` for full metadata.

For Python client fallback (citation networks, institution analysis): [`references/openalex-verification.md`](references/openalex-verification.md)

## Deep Verification Mode

Triggered by `--deep-verify` flag, 40+ entries, or "deep verify" / "verify all references". Full architecture and batch format: [references/deep-verify.md](references/deep-verify.md)

## Council Mode

For high-stakes submissions. Trigger: "council bib-validate" or "thorough bib check". Full details: [references/council-mode.md](references/council-mode.md)

## Fix Mode

After producing the validation report, automatically fix resolvable issues using the filing sequence from [`shared/reference-resolution.md`](../shared/reference-resolution.md).

### Auto-Fix Actions

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

### Post-Fix Maintenance

1. **Update `zotero-collections.md`** — increment item counts for affected collections.
2. **Report summary** — show a table of all fixes applied: entry key, issue, action taken, status.

### Skip Fix Mode

Fix mode is skipped when:
- The skill is invoked with `--report-only` or `--dry-run`
- No actionable issues are found (all entries are `HEALTHY`)
- Both refpile MCP and paperpile MCP are unavailable

## Quality Scoring

When producing a full validation report, apply numeric quality scoring using the shared framework:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules

Map validation findings to the framework tiers:
- **Critical** (-15 to -25): Missing entry for a cited key (compilation error)
- **Major** (-5 to -14): DOI mismatch, stale preprint with published version available, "et al." in author field
- **Minor** (-1 to -4): Missing optional fields, year oddities, unused entries

Compute the score and include the Score Block in the report after the summary table.

## Cross-References

- **`/proofread`** — For overall paper quality including citation format
- **`/literature`** — For finding and adding new references (includes full OpenAlex workflows)
- **`/bib-coverage`** — Compare project `.bib` vs Zotero topic collection — find uncited papers and unfiled references
- **`/latex`** — For compilation with reference checking
- **`/latex-autofix`** — For compilation and error resolution. Run after fixing bibliography issues to verify citations compile cleanly.
- **`shared/reference-resolution.md`** — Canonical lookup + filing sequence used by Ref Manager Cross-Reference and Fix Mode
