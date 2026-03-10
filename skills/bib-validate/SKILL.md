---
name: bib-validate
description: "Cross-reference \\cite{} keys against .bib files or embedded \\bibitem entries. Finds missing, unused, and typo'd citation keys. Deep verification mode spawns parallel agents for DOI/metadata validation at scale. Read-only in standard mode."
allowed-tools: Read, Glob, Grep, Task, Write, Bash(mkdir*), Bash(ls*), Bash(rm*)
argument-hint: [project-path or tex-file]
---

# Bibliography Validation

**Read-only skill.** Never edit source files — produce a categorised report only.

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

**Default bibliography file is `references.bib`** — this is the standard across all projects (per the `/latex` skill convention). However, the skill also supports:

- Any `.bib` file found in the same directory as the `.tex` files being audited
- Embedded bibliographies using `\begin{thebibliography}` / `\bibitem{key}` blocks
- Both external and embedded simultaneously (rare but possible)

## Bibliography Detection

At the start of validation, detect which bibliography method the project uses:

### 1. External `.bib` file (standard)

Look for `.bib` files in the project directory. Priority order:
1. `references.bib` (preferred — standard naming convention across all projects)
2. Any other `.bib` file in the same directory as the `.tex` files

If **multiple `.bib` files** are found, validate all of them and produce a combined report. Note which file each issue belongs to. If a legacy-named `.bib` file (e.g., `paperpile.bib`) exists alongside `references.bib`, flag it as a potential cleanup opportunity (the project may have migrated from Paperpile).

Full validation applies: cross-reference checks **and** quality checks.

### 2. Embedded `\begin{thebibliography}` / `\bibitem{key}`

Some LaTeX documents define references inline rather than using an external `.bib` file. Detect by scanning `.tex` files for `\begin{thebibliography}`.

Extract keys from `\bibitem` entries:
- `\bibitem{key}` — standard form, key is the argument in braces
- `\bibitem[label]{key}` — optional label form (e.g., `\bibitem[Smith et al., 2020]{smith2020}`), key is in the **second** set of braces

Only **cross-reference checks** apply (missing keys, unused keys, typos). Quality checks (required fields, year, author formatting) are **skipped** because embedded bibliographies don't have structured metadata.

### 3. Both (rare)

If a project has both a `.bib` file and `\begin{thebibliography}` blocks, validate both:
- Run full validation on the `.bib` file
- Run cross-reference checks on `\bibitem` entries
- Merge both key sets when checking for missing citations

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

Scan `.tex` files for all of these patterns:

| Command | Example |
|---------|---------|
| `\cite{key}` | Basic citation |
| `\citet{key}` | Textual: Author (Year) |
| `\citep{key}` | Parenthetical: (Author, Year) |
| `\textcite{key}` | biblatex textual |
| `\autocite{key}` | biblatex auto |
| `\parencite{key}` | biblatex parenthetical |
| `\citeauthor{key}` | Author name only |
| `\citeyear{key}` | Year only |
| `\nocite{key}` | Include in bibliography without in-text citation |

Also handle **multi-key citations**: `\citep{key1, key2, key3}`

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

After the disk-based cross-reference, check each cited key against the user's reference libraries. Two sources are available — check both when possible.

### Paperpile (Primary)

Cross-reference via the `paperpile` MCP server. For each citation key found in the `.tex` files:

1. Call `mcp__paperpile__search_library` with the citation key as query
2. Match on the citekey field in results
3. For entries with issues, call `mcp__paperpile__get_item` for full metadata
4. Use `mcp__paperpile__export_bib` to generate correct BibTeX for missing/outdated entries

**Additional checks:**
- Call `mcp__paperpile__get_labels` to verify folder organisation matches project themes
- For projects with a known Paperpile label, call `mcp__paperpile__get_items_by_label` to find papers in the folder but not cited (potential missing citations)

### Zotero (Legacy — via RefPile MCP)

Cross-reference via the `refpile` MCP server. For each citation key:

1. Call `search_library` (refpile MCP) with the citation key as query
2. Match on the `citationKey` field in results

### Combined Status Categories

| .bib | Paperpile | Zotero | Status | Report |
|------|-----------|--------|--------|--------|
| Yes | Yes | Yes | Healthy | `✓ In sync across all` |
| Yes | Yes | No | Partial | `✓ Paperpile ↔ .bib in sync (not in Zotero)` |
| Yes | No | Yes | Partial | `✓ Zotero ↔ .bib in sync (not in Paperpile)` |
| Yes | No | No | Drift | `⚠ In local .bib but not in any reference manager` |
| No | Yes | — | Export gap | `ℹ In Paperpile but not exported to local .bib` |
| No | — | Yes | Export gap | `ℹ In Zotero but not exported to local .bib` |
| No | No | No | Missing | `✗ Missing from all — add to Paperpile first` |

Include this as a "Reference Manager Sync" section in the report, after cross-reference results and before quality checks.

**Graceful degradation:** If either MCP is unavailable, skip that source with a warning and continue with whatever is available. If both are unavailable, continue with disk-only validation.

## Quality Checks on .bib Entries

**These checks apply only to external `.bib` files.** Embedded bibliographies lack structured metadata, so quality checks are skipped for them.

### Required Fields by Entry Type

| Entry Type | Required Fields |
|-----------|----------------|
| `@article` | author, title, journal, year |
| `@book` | author/editor, title, publisher, year |
| `@incollection` | author, title, booktitle, publisher, year |
| `@inproceedings` | author, title, booktitle, year |
| `@techreport` | author, title, institution, year |
| `@unpublished` | author, title, note, year |
| `@phdthesis` | author, title, school, year |

### Year Reasonableness

- Flag entries with year < 1900 or year > current year + 1
- Flag entries with no year at all

### Author Formatting

- Check for inconsistent author formats within the file
- **Flag entries where author field contains "and others" or "et al."** — this is never valid in BibTeX. All authors must be listed explicitly. Severity: **Warning**.
- Flag entries with organisation names that might need `{{braces}}` to prevent splitting

### DOI Resolution (optional — triggered by `--verify-dois` flag or when issues are suspected)

**Preferred method: bibliography MCP `scholarly_verify_dois`.** Collect all DOIs from the `.bib` file and call `scholarly_verify_dois` (up to 50 per call). This batch-verifies each DOI against all enabled sources (OpenAlex, Scopus, WoS). Results:
- **VERIFIED** (2+ sources confirm) — DOI is valid, metadata can be trusted
- **SINGLE_SOURCE** (1 source only) — DOI exists but warrants a manual spot-check
- **NOT_FOUND** — DOI not found in any source; resolve manually via WebFetch

**Fallback for NOT_FOUND DOIs:** Resolve via `https://doi.org/[DOI]` and confirm the returned metadata matches the entry:

1. **Title match**: Does the DOI landing page title match the `.bib` title?
2. **Author match**: Does the first author on the landing page match the `.bib` first author?
3. **Journal match**: Does the venue match?

Flag mismatches as:
- **Warning: DOI mismatch** — DOI resolves to a different paper than claimed. This usually means the DOI is wrong (adjacent DOI in the same journal volume) or the authors are wrong (conflation of researchers in the same subfield).

This check catches:
- Wrong DOIs (e.g., off-by-one in the DOI suffix)
- Author conflation (real researchers incorrectly attributed to a paper)
- Metadata copied from secondary sources without verification

For manual WebFetch resolution, process in batches of 5 to avoid rate limiting. Only flag confirmed mismatches — if the DOI cannot be resolved (404, timeout), note it as "unresolvable" at Info level.

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

## Optional: Metadata Verification via MCP Tools

When missing entries or suspicious metadata are flagged, check these sources in order:

1. **Paperpile** (paperpile MCP) — call `mcp__paperpile__search_library` by title. If found, use `mcp__paperpile__export_bib` to get correct BibTeX.
2. **Zotero library** (refpile MCP) — call `search_library` by title. The user may already have the reference but with a different key.
3. **Bibliography MCP** (scholarly sources):
   - **`scholarly_search`** — search by title to find the correct entry across OpenAlex + Scopus + WoS
   - **`scholarly_verify_dois`** — batch-verify DOIs across all sources (preferred over manual DOI resolution)
   - **`openalex_lookup_doi`** — look up full metadata for a specific DOI

For Python client fallback (citation networks, institution analysis): [`references/openalex-verification.md`](references/openalex-verification.md)

## Deep Verification Mode (Parallel, Disk-Based)

Triggered by: `--deep-verify` flag, 40+ entries, or "deep verify" / "verify all references". Spawns parallel sub-agents that verify batches and write results to disk. Full architecture, batch JSON format, and assembly: [references/deep-verify.md](references/deep-verify.md)

## Council Mode (Optional)

For high-stakes submissions. Trigger: "council bib-validate", "thorough bib check". Full details: [references/council-mode.md](references/council-mode.md)

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
- **`/latex`** — For compilation with reference checking
- **`/latex-autofix`** — For compilation and error resolution. Run after fixing bibliography issues to verify citations compile cleanly.
- **`/latex-autofix`** — After fixing bibliography issues, run to verify citations compile cleanly
