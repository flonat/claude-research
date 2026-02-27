# Bibliography Validation Report Template

> Reference file for `/validate-bib`. Use this format for all validation reports.

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

## Limitations

*If embedded:* Embedded bibliographies (`\bibitem`) lack structured metadata (author, year, journal as separate fields). Only cross-reference checks were performed. Quality checks (required fields, year reasonableness, author formatting) require an external `.bib` file.
```
