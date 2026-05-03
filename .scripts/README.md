# Automation Scripts

> Python utilities and shell helpers, mostly invoked by skills/agents/hooks.

The Notion-backed CLI tools that lived here previously (`task`, `tasks`,
`done`, `inbox`, `query`, `week`, `conf`, plus `daily_digest.py`,
`extract_meeting_actions.py`, `notion_helpers.py`, `config.py`,
`generate-codex-agents-md.py`) were retired in 2026-04. The Research Vault
(`~/Research-Vault`) and the `taskflow` MCP server replaced them.

## Active scripts

| Script | Purpose |
|--------|---------|
| `ai_pattern_density.py` | Scans text/LaTeX for auto-generated writing patterns (CommScribe-style density score) |
| `count_inventory.py` | Ground-truth count of skills / hooks / rules / agents; propagates corrected counts across docs |
| `ensure-resources.sh` | Idempotent setup of resource directories |
| `focus` | Quick-update wrapper for `.context/current-focus.md` (no Notion dependency) |
| `mini-unlock` | Mac Mini SSH-tunnel unlock helper |
| `regen-resource-manifest.sh` | Regenerate the resource manifest |
| `session-history.py` | Query session-outcomes JSONL via SQLite |
| `skill-health.py` | Skill health dashboard from `skill-outcomes.jsonl` |
| `skill-log-miner.py` | Mine skill outcome logs for failure patterns |
| `sync-resources.sh` | Pull latest from cloned resource repos |
| `sync-template.sh` | Sync templates between locations |
| `sync-to-codex.sh` | Sync infrastructure to the Codex CLI |
| `venue-metrics` | Pull venue-level metrics |

## Shared libraries

| Directory | Purpose |
|-----------|---------|
| `openalex/` | OpenAlex API client — shared across `/literature`, `/bib-validate`, `/split-pdf`, and the OpenAlex MCP server |

## Replacement map (for the deleted Notion CLIs)

| Deleted | Use instead |
|---------|-------------|
| `task`, `tasks`, `done`, `inbox` | `taskflow-cli` (Bash) or `taskflow` MCP tools |
| `query` | `refpile search-library` (semantic) or `paperpile search-library` (exact) |
| `week` | `/minutes-weekly` skill or vault-based weekly review |
| `conf` | `conf-timeline list` (see [`docs/guides/conf-deadlines.md`](../docs/guides/conf-deadlines.md)) |
| `daily_digest.py` | `/task-management` skill (vault-aware) |
| `extract_meeting_actions.py` | `/minutes-recap` skill |

## Conventions

These scripts are invoked from skills, agents, and hooks — they don't
talk to external APIs unless explicitly noted. All Python scripts run
under `uv` (per the `python-uv` global rule):

```bash
uv run python .scripts/<name>.py
```

Shell scripts are POSIX-compatible bash with `set -euo pipefail` headers.
