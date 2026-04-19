# Reference Manager Cross-Reference

> Referenced from: `bib-validate/SKILL.md`

After the disk-based cross-reference, check each cited key against Paperpile using the resolution order from [`../shared/reference-resolution.md`](../../shared/reference-resolution.md).

## Paperpile (Primary Reference Manager)

Cross-reference via the `paperpile` MCP server. For each citation key:

1. Call `paperpile search-library` with the citation key as query
2. If a DOI is available, also try `paperpile lookup-by-doi` for exact matching
3. Match on the `citekey` field in results
4. For entries with issues, call `paperpile get-item` for full metadata
5. Use `paperpile export-bib` to generate correct BibTeX for missing/outdated entries

**Additional checks:**
- Call `paperpile get-labels` to verify label organisation matches project themes
- For projects with a known Paperpile label, call `paperpile get-items-by-label` to find papers in the label but not cited (potential missing citations)

## Status Categories

| .bib | Paperpile | Status | Report |
|------|-----------|--------|--------|
| Yes | Yes | `HEALTHY` | `✓ In sync` |
| Yes | No | `DRIFT` | `⚠ In local .bib but not in Paperpile — stage for import` |
| No | Yes | `EXPORT_GAP` | `ℹ In Paperpile but not exported to local .bib` |
| No | No | `MISSING` | `✗ Missing from all — will stage as BibTeX for Paperpile import in Fix Mode` |

Include this as a "Reference Manager Sync" section in the report, after cross-reference results and before quality checks.

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip with a warning and continue with disk-only validation.
