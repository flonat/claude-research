# Bibliography Validation Report Template

> Reference file for `/bib-validate`. Use this format for all validation reports.

```markdown
# Bibliography Validation Report

**Project:** [path]
**Date:** YYYY-MM-DD
**Files scanned:** [list of .tex files]
**Bibliography type:** External .bib / Embedded / Both
**Bibliography:** [filename] ([N] entries) | Embedded ([N] \bibitem entries) | Both ([N] .bib + [N] \bibitem)
**Citations found:** [N] unique keys across [N] citation commands

## Summary

| Check | Count |
|-------|-------|
| Missing entries (Critical) | 0 |
| Possible typos (Warning) | 0 |
| Unused entries (Warning) | 0 |
| Missing required fields (Warning) | 0 |
| DOI mismatches (Warning) | 0 |
| Stale preprints (Warning) | 0 |
| Year issues (Info) | 0 |

## Critical: Missing Entries

| Cited Key | File | Line | Suggested Match |
|-----------|------|------|-----------------|
| `smith2020` | main.tex | 42 | `smith2021` (edit dist: 1) |

## Warning: Possible Typos

[Keys with close fuzzy matches]

## Warning: Unused Entries

[Keys in bibliography not cited anywhere — listed for review]

## Warning: Missing Required Fields

*External .bib only — skipped for embedded bibliographies.*

| Key | Type | Missing Fields |
|-----|------|---------------|
| `jones2019` | article | journal |

## Warning: Stale Preprints

| Key | Current Source | Published In | Year | DOI |
|-----|---------------|--------------|------|-----|
| `smith2020arxiv` | arXiv:2020.12345 | *J. of ML Research* | 2022 | 10.xxxx/yyyy |

## Info: Year Issues

[Entries with suspicious years]

## Reference Manager Cross-Reference

| Key | .bib | Zotero | Paperpile | Status |
|-----|------|--------|-----------|--------|
| `smith2020` | Yes | Yes | Yes | HEALTHY |
| `jones2019` | Yes | No | Yes | MIGRATE_TO_ZOTERO |
| `doe2021` | Yes | No | No | MISSING |

## Fix Mode Actions

*Omit this section if `--no-fix` was passed or no fixable issues were found.*

| Action | Key | Result |
|--------|-----|--------|
| Added to Zotero | `doe2021` | Filed → [Topic Collection] + _Needs Review |
| Migrated to Zotero | `jones2019` | Copied from Paperpile → [Topic Collection] + _Needs Review |
| Metadata corrected | `smith2020` | Updated year: 2019 → 2020 |

**Post-fix:** Updated `zotero-collections.md` item counts for [collection].

## Limitations

*If embedded:* Embedded bibliographies (`\bibitem`) lack structured metadata (author, year, journal as separate fields). Only cross-reference checks were performed. Quality checks (required fields, year reasonableness, author formatting) require an external `.bib` file.
```
