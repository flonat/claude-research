# mcp-scholarly

Multi-source scholarly search — dual frontend (MCP server + `scholarly` CLI) over 15 providers: OpenAlex, Semantic Scholar, Crossref, Scopus, Web of Science, CORE, ORCID, Altmetric, Zenodo, Unpaywall, OpenCitations, DBLP, OpenReview, arXiv, Exa.

39 tools total (35 without an Exa API key). Both frontends call the same neutral handlers — see [`EXPLAINER.md`](EXPLAINER.md) for architecture.

## Install

```bash
# From Task-Management root
cd packages/mcp-scholarly
uv sync
```

### Credentials

Provider keys live in `~/.config/task-mgmt/credentials.env` (sourced automatically by both `run.sh` and the CLI):

| Provider | Env var(s) | Required? |
|----------|-----------|-----------|
| Scopus | `SCOPUS_API_KEY`, `SCOPUS_INST_TOKEN` | For Scopus |
| Web of Science | `WOS_LITE_KEY` | For WoS |
| CORE | `CORE_API_KEY` | For CORE |
| ORCID | `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET` | For ORCID |
| Altmetric | `ALTMETRIC_API_KEY`, `ALTMETRIC_API_PASSWORD` | For Altmetric |
| Exa | `EXA_API_KEY` | For Exa tools |

OpenAlex, S2, Crossref, Zenodo, Unpaywall, OpenCitations, DBLP, OpenReview, arXiv need no auth.

Check which are active:

```bash
uv run scholarly source-status
```

### CLI on PATH (recommended)

Put a shim at `~/.local/bin/scholarly`:

```bash
#!/usr/bin/env bash
exec uv run --project "$HOME/Task-Management/packages/mcp-scholarly" scholarly "$@"
```

Then `scholarly source-status` works from anywhere. The shim always reflects the latest source (no reinstall on refactors).

## CLI usage

```bash
scholarly scholarly-search "human AI collaboration" --limit 5
scholarly crossref-lookup-doi 10.1145/3359313
scholarly arxiv-search "multi-agent systems" --limit 3

# JSON envelope for scripted use
scholarly scholarly-search "query" --limit 5 --json
```

`--help` on any subcommand shows schema-derived flags. Exact-name escape hatch:

```bash
scholarly call scholarly_search --json-args '{"query":"q","limit":3}'
```

## MCP usage

Launch the server directly:

```bash
./run.sh
```

Or register in `~/.claude.json` (user-scope) so Claude Code loads it automatically. The MCP frontend is the only option in Claude Desktop, which cannot shell out to `uv`.

## Tool catalog

Grouped by provider. Full schemas via `scholarly <cmd> --help`.

**Multi-source** (fanout across all active providers):
`scholarly_search`, `scholarly_verify_dois`, `scholarly_similar_works`, `scholarly_source_status`, `scholarly_citations`, `scholarly_references`, `scholarly_paper_detail`, `scholarly_author_papers`, `scholarly_search_scopus`, `scholarly_search_wos`

**OpenAlex:** `openalex_search_works`, `openalex_author_works`, `openalex_author_profile`, `openalex_institution_output`, `openalex_trends`, `openalex_lookup_doi`, `openalex_citing_works`

**Crossref:** `crossref_lookup_doi`

**OpenReview:** `openreview_venue_submissions`, `openreview_paper_reviews`, `openreview_search`

**DBLP:** `dblp_search`

**OpenCitations:** `opencitations_citations`, `opencitations_references`

**Unpaywall:** `unpaywall_find_pdf`

**Zenodo:** `zenodo_search`, `zenodo_get_record`

**arXiv:** `arxiv_search`, `arxiv_get_paper`, `arxiv_search_category`

**Exa** (if `EXA_API_KEY` set): `exa_search`, `exa_get_contents`, plus 2 more

**ORCID, Altmetric**: registered when credentials present.

## Testing

```bash
uv run --with pytest pytest -q
```

## Architecture

See [`EXPLAINER.md`](EXPLAINER.md). Short version:

```
biblio-sources provider clients
        │
        ▼
_app.py shared runtime
        │
        ▼
tools/*.py neutral handlers → ToolResult
        │
tools/_registry.py
  ├─ mcp_adapter.py → server.py  (MCP frontend)
  └─ cli.py                       (CLI frontend)
```

The CLI lets the same stack stay available without globally loading 39 MCP schemas into every Claude Code session.

## Known provider issues

Tracked in [`MEMORY.md`](MEMORY.md). Highlights:

- **S2 `scholarly_paper_detail`** — wrong journal names for some management journals (e.g., "Southern Medical Journal" ← Strategic Management Journal). Cross-check via Crossref DOI lookup.
- **`scholarly_search`** — noisy for known-paper lookups; use Crossref directly for targeted queries.
- **CORE** — occasional 500s from upstream.
- **Web of Science** — intermittent `'int' object has no attribute 'get'` client errors.

## Rollout status

Moving skills from MCP tool calls to CLI invocations is tracked in [`log/plans/2026-04-15_mcp-scholarly-cli-rollout.md`](../../log/plans/2026-04-15_mcp-scholarly-cli-rollout.md).
