# Canonical CLI Recipes — literature

> Copy-paste reference for the `scholarly` and `paperpile` CLI invocations used across `literature`. New skills that do academic search or reference sync should mirror this pattern.

## Environment

Credentials for each provider (OpenAlex, Scopus, WoS, S2, CORE, ORCID, Altmetric) come from the host shell (Code) or `/etc/credentials.env` (container). The CLI shim sources them automatically.

```bash
# Check which sources are enabled (credentials present)
scholarly scholarly-source-status --json
```

## Multi-source keyword search (Phase 2 pre-fetch)

```bash
scholarly scholarly-search "diffusion models in economics" --limit 20 --json
```

Queries all enabled sources in parallel, dedupes by DOI, returns combined result list. Use `--from-year 2020` and `--to-year 2025` to filter.

## Author-based search

```bash
scholarly scholarly-author-papers --author-name "Susan Athey" --limit 50 --json
```

## ML-based recommendations

```bash
scholarly scholarly-similar-works --doi "10.xxxx/yyyy" --limit 20 --json
```

Backed by the S2 Recommendations API. Useful to surface papers beyond keyword matches.

## Forward / backward citation graphs (snowball)

```bash
# Papers citing a given DOI
scholarly scholarly-citations --doi "10.xxxx/yyyy" --limit 50 --json

# Papers referenced by a given DOI
scholarly scholarly-references --doi "10.xxxx/yyyy" --limit 50 --json
```

## Full paper metadata

```bash
scholarly scholarly-paper-detail --doi "10.xxxx/yyyy" --json
```

Returns abstract, TLDR, BibTeX, OA PDF link where available. Use in Phase 3 (screening) and Phase 6 (BibTeX assembly).

## Batch DOI verification

```bash
scholarly scholarly-verify-dois --dois "10.aaaa/bbbb,10.cccc/dddd" --json
```

Phase 4: after the `.bib` is assembled, verify every DOI resolves. Batch reduces API calls dramatically vs. per-paper lookups.

## Paperpile sync after assembly (Phase 6c)

Stage genuinely-new entries under `.paperpile-import/` for manual import — the Paperpile CLI is read-only for the library (no import command). Write each entry's BibTeX into a `.bib` there and use a `\CiteTodo{...}` placeholder for any draft cite until imported. See `rules/paperpile-citations.md`.

`paperpile write-bib` only **exports** entries already in the library, by citekey:

```bash
paperpile write-bib --citekeys Key1-ab,Key2-cd --output-path exported.bib
```

Then report the staged path and remind the user to import into Paperpile.

For entries already in Paperpile with richer metadata:

```bash
paperpile export-bib --ids <id1>,<id2> --json | jq -r .bibtex > merged.bib
```

## JSON contract

Every command supports `--json` and returns structured output. Always pass `--json` in skill scripts.

## Sub-agent pattern

Both `scholarly` and `paperpile` have CLI frontends — sub-agents can call them directly (no MCP pre-fetch needed). See `rules/subagent-prompt-discipline.md`.

## Provider notes (known issues)

- **CORE** may return 500 on `scholarly-search` — skip with warning
- **Web of Science** has a long-standing `'int' object has no attribute 'get'` bug — skip with warning

These are tracked in `log/plans/2026-04-16_mcp-consolidation-plan.md` under "Open Issues".
