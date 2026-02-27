# Metadata Verification

> Reference file for `/validate-bib`. Use when missing entries or suspicious metadata are found.

## Preferred: Biblio MCP Tools

**Always prefer MCP tools over the Python client** — they're faster, require no boilerplate, and query multiple sources.

| Tool | Use for |
|------|---------|
| `scholarly_verify_dois` | Batch-verify DOIs across OpenAlex + Scopus + WoS (up to 50 per call) |
| `scholarly_search` | Find a paper by title across all sources — useful when a cited key is missing |
| `openalex_lookup_doi` | Look up full metadata for a single DOI |
| `scholarly_similar_works` | Find related papers when a title search doesn't match exactly |

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
- Batch DOI verification (use `scholarly_verify_dois` first)

Do NOT use this by default — only when the report flags issues worth verifying.
