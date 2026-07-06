# Canonical CLI Recipes — bib-validate

> Copy-paste reference for the `paperpile` CLI invocations used by `bib-validate`. New skills touching Paperpile should mirror this pattern.

## Environment

Credentials come from the host shell (Code) or `/etc/credentials.env` (container). No per-invocation keys.

```bash
# Verify the CLI is on PATH
command -v paperpile || echo "Missing — install paperpile and expose via uv tool install"
```

## Search by citation key

```bash
paperpile search-library "author2024keyword" --json
```

Returns JSON array of matches. Match on `citekey` field exactly; near-matches are suggestions only.

## Look up by DOI

Use when a `.bib` entry has a DOI but the citekey doesn't match the Paperpile side.

```bash
paperpile lookup-by-doi "10.1234/example.2024.001" --json
```

## Full metadata for one item

```bash
paperpile get-item <item-id> --json
```

Follows on from `search-library` — use the `id` field from the search hit.

## Export a single or full bibliography

```bash
# Export one item by id
paperpile export-bib --ids <id1>,<id2> --json

# Export by label
paperpile export-bib --label "project-slug" --json
```

Pipe to `jq -r .bibtex > entry.bib` to land at a file.

## Label operations

```bash
paperpile get-labels --json
paperpile get-items-by-label "project-slug" --json
```

Use `get-items-by-label` to detect papers in a Paperpile label that aren't cited in the `.tex` — flag as potential missing citations.

## Staging a genuinely-missing entry (`.paperpile-import/`)

The Paperpile CLI is read-only for the library (no import command). To stage a paper that is NOT in the library, write its BibTeX into a `.bib` under `.paperpile-import/` and mark its draft cite `\CiteTodo{slug}{title; authors; year; DOI}` (build-blocking until imported); the user imports the staged `.bib` into Paperpile manually. See `rules/paperpile-citations.md`.

`paperpile write-bib` only **exports** entries that already exist in the library, by citekey — it cannot stage a missing paper:

```bash
paperpile write-bib --citekeys Smith2020-xy,Doe2019-ab --output-path exported.bib
```

## Graceful degradation

If the CLI is unavailable, skip Paperpile checks and run disk-only validation. Do not fail the skill — Paperpile is an enrichment source, not a hard dependency.

## JSON contract

All commands support `--json` and return structured output. Always pass `--json` in skill scripts — human-readable output is for interactive debugging only.

## Sub-agent pattern

`paperpile` has a CLI frontend, so sub-agents can call it directly (no MCP pre-fetch needed). See `rules/subagent-prompt-discipline.md` for the full list of CLI-fronted packages.
