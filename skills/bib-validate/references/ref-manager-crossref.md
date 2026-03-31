# Reference Manager Cross-Reference

> Referenced from: `bib-validate/SKILL.md`

After the disk-based cross-reference, check each cited key against the user's reference libraries using the resolution order from [`../shared/reference-resolution.md`](../../shared/reference-resolution.md). Two sources are available — check both when possible.

## Zotero (Active Write Target — via RefPile MCP)

Cross-reference via the `refpile` MCP server. For each citation key:

1. Call `mcp__refpile__search_library` with the citation key as query
2. Match on the `citationKey` field in results

## Paperpile (Read-Only Cross-Reference)

Cross-reference via the `paperpile` MCP server. For each citation key found in the `.tex` files:

1. Call `mcp__paperpile__search_library` with the citation key as query
2. Match on the citekey field in results
3. For entries with issues, call `mcp__paperpile__get_item` for full metadata
4. Use `mcp__paperpile__export_bib` to generate correct BibTeX for missing/outdated entries

**Additional checks:**
- Call `mcp__paperpile__get_labels` to verify folder organisation matches project themes
- For projects with a known Paperpile label, call `mcp__paperpile__get_items_by_label` to find papers in the folder but not cited (potential missing citations)

## Combined Status Categories

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
