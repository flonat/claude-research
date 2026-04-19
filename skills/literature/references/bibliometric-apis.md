# Bibliometric API Structured Queries

> Four bibliometric sources are available. The **`scholarly` CLI** (`packages/mcp-scholarly/`) is the preferred interface — `scholarly scholarly-search "<query>" --json` queries all enabled sources in one call with automatic DOI-based dedup; `scholarly scholarly-verify-dois --dois D1,D2 --json` batch-verifies DOIs across all sources.

## Scholarly CLI Tools (preferred)

| Tool | What it does | When to use |
|------|-------------|-------------|
| `scholarly scholarly-search` | Cross-source keyword search (OpenAlex + S2 + Scopus + WoS) with dedup | Phase 2 pre-fetch |
| `scholarly scholarly-similar-works` | ML-based recommendations (S2 Recommendations API) | Phase 2 pre-fetch — finds papers beyond keyword matches |
| `scholarly scholarly-verify-dois` | Batch DOI verification across all sources | Phase 4 verification |
| `scholarly scholarly-citations` | Forward citation graph (papers citing a given paper) | Phase 2.5 snowball — find follow-up work |
| `scholarly scholarly-references` | Backward citation graph (papers referenced by a given paper) | Phase 2.5 snowball — find foundational works |
| `scholarly scholarly-paper-detail` | Full metadata + TLDR + BibTeX + OA PDF link | Phase 3 screening, Phase 6 BibTeX assembly |
| `scholarly scholarly-author-papers` | All papers by an author | Phase 2 pre-fetch — author-based search |
| `scholarly scholarly-source-status` | Check which sources are active | Phase 1 |

## OpenAlex (always available)

**Setup:** `.scripts/openalex/openalex_client.py` + `.scripts/openalex/query_helpers.py`

| Workflow | What it does |
|----------|-------------|
| Highly-cited papers | Top-cited papers on a topic (filtered by year) |
| Author output | Full publication record for a researcher |
| Institution output | Research output analysis for a university |
| Publication trends | Year-by-year counts for a topic |
| Open-access discovery | Find freely downloadable versions |
| Citation network | Forward citations for a given paper |
| Batch DOI lookup | Verify metadata for multiple papers |

**Full recipes:** [openalex-workflows.md](openalex-workflows.md) | **API guide:** [openalex-api-guide.md](openalex-api-guide.md)

## Scopus (requires `SCOPUS_API_KEY` + `SCOPUS_INST_TOKEN`)

Query syntax: `TITLE-ABS-KEY("quoted phrases" OR terms)`, subject areas via `SUBJAREA(CODE)`, year filters via `PUBYEAR > N` / `PUBYEAR < N`. Elsevier REST API with `X-ELS-APIKey` + `X-ELS-Insttoken` headers. Provides abstracts, author keywords, and citation counts in COMPLETE view. Pagination via `start`/`count` params (max 25 per page).

**API guide:** [scopus-api-guide.md](scopus-api-guide.md)

## Web of Science (requires `WOS_API_KEY`)

Query syntax: `TS=(topic search)`, year filter via `PY=(YYYY-YYYY)`. Two API tiers: **Starter** (`/documents` endpoint, page-based, max 50/page) and **Expanded** (root endpoint, `firstRecord`-based, max 100/page, includes abstracts). Auth via `X-ApiKey` header. Tier set via `WOS_API_TIER` env var (default: `starter`).

**API guide:** [wos-api-guide.md](wos-api-guide.md)
