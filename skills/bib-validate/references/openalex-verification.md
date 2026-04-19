# Metadata Verification

> Reference file for `/bib-validate`. Use when missing entries or suspicious metadata are found.

## Preferred: `scholarly` CLI

**Always prefer the `scholarly` CLI over the Python client** — it's faster, requires no boilerplate, queries multiple sources, and works in both the main context and sub-agents.

| Command | Use for |
|---------|---------|
| `scholarly scholarly-verify-dois --dois D1,D2 --json` | Batch-verify DOIs across OpenAlex + Scopus + WoS (up to 50 per call) |
| `scholarly scholarly-search "<title>" --json` | Find a paper by title across all sources — useful when a cited key is missing |
| `scholarly openalex-lookup-doi <doi> --json` | Look up full metadata for a single DOI |
| `scholarly scholarly-similar-works <paper_id> --json` | Find related papers when a title search doesn't match exactly |

## Fallback: Python Client

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

Use the Python client only for workflows not exposed via MCP (citation networks, institution analysis):

```bash
uv run python -c "
import sys
sys.path.insert(0, '.scripts/openalex')
from openalex_client import OpenAlexClient

client = OpenAlexClient(email='user@example.edu')

# Look up a specific DOI
result = client.get_entity('works', 'doi:10.1016/j.ejor.2024.01.001')

# Search by title to find the correct entry
results = client.search_works(search='decision making under uncertainty', per_page=5)
"
```

## When to use:

- A cited key is missing and you want to confirm whether the paper exists
- Year or author formatting looks suspicious and you want to cross-check
- The user asks to enrich `.bib` entries with verified metadata
- Batch DOI verification (use `scholarly scholarly-verify-dois` first)

Do NOT use this by default — only when the report flags issues worth verifying.
