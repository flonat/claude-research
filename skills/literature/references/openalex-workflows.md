# OpenAlex Structured Query Workflows

> Extracted from the former `/openalex-search` skill. These workflows use the shared Python client in `.scripts/openalex/openalex_client.py` and helpers in `.scripts/openalex/query_helpers.py`.

## Setup

```python
import sys
sys.path.insert(0, ".scripts/openalex")
from openalex_client import OpenAlexClient
from query_helpers import find_highly_cited_recent_papers, get_open_access_papers, \
    find_author_works, find_institution_works, analyze_research_output, get_publication_trends

client = OpenAlexClient(email="user@example.edu")
```

Install dependency: `uv pip install requests`

---

## When to Use OpenAlex Queries

| Scenario | OpenAlex workflow | Full `/literature` instead? |
|----------|-------------------|----------------------------|
| Find highly-cited papers on a topic | Workflow 1 | No — quick structured query |
| Build a full literature review with narrative | — | Yes — use full 7-phase pipeline |
| Citation count / trend analysis | Workflow 4 | No — API-only |
| Verify a specific citation exists | Workflow 7 | Or Phase 4 of `/literature` |
| Author or institution research output | Workflows 2–3 | No — API-only |
| Find open-access versions of papers | Workflow 5 | No — API-only |
| Comprehensive lit search + .bib assembly | — | Yes — calls OpenAlex as Phase 2 agent |
| Bibliometric analysis for a paper | Workflow 6 | No — API-only |

**Rule of thumb:** Use these workflows directly when you need *structured data* (counts, rankings, trends, metadata). Use the full `/literature` pipeline when you need a *complete workflow* (search, verify, download, synthesize).

---

## Core Workflows

### 1. Find Highly-Cited Papers on a Topic

```python
papers = find_highly_cited_recent_papers(
    topic="multi-criteria decision making",
    years=">2018",
    client=client,
    limit=50
)

for p in papers[:10]:
    print(f"[{p['cited_by_count']}] {p['title']} ({p['publication_year']})")
```

### 2. Author Publication Record

```python
works = find_author_works("Salvatore Greco", client=client, limit=100)
```

Uses the two-step pattern: search author -> get ID -> filter works by ID.

### 3. Institution Research Output

```python
analysis = analyze_research_output(
    entity_type='institution',
    entity_name='University of Example',
    client=client,
    years='>2020'
)

print(f"Total works: {analysis['total_works']}")
print(f"Open access: {analysis['open_access_percentage']}%")
```

### 4. Publication Trends

```python
trends = get_publication_trends(
    search_term="human-AI collaboration",
    client=client
)

for t in sorted(trends, key=lambda x: x['key'])[-10:]:
    print(f"{t['key']}: {t['count']} publications")
```

### 5. Open-Access Paper Discovery

```python
papers = get_open_access_papers(
    search_term="staggered difference-in-differences",
    client=client,
    oa_status="any",
    limit=50
)
```

### 6. Citation Network (Who Cites This Paper?)

```python
import requests

work = client.get_entity('works', 'https://doi.org/10.1016/j.ejor.2023.01.001')
citing = requests.get(
    work['cited_by_api_url'],
    params={'mailto': client.email, 'per-page': 200}
).json()['results']
```

### 7. Batch DOI Lookup

For verifying multiple papers at once — useful for feeding into `/validate-bib`:

```python
dois = [
    "https://doi.org/10.1016/j.ejor.2023.01.001",
    "https://doi.org/10.1287/mnsc.2022.4321",
]

works = client.batch_lookup('works', dois, 'doi')
```

---

## Key API Patterns

### Filters

```python
# Single year
filter_params={"publication_year": "2023"}

# Range
filter_params={"publication_year": "2020-2025"}

# Multiple conditions (AND)
filter_params={"publication_year": ">2020", "is_oa": "true", "cited_by_count": ">50"}

# Multiple values (OR)
filter_params={"authorships.institutions.id": "I123|I456"}

# Collaboration (AND within attribute)
filter_params={"authorships.institutions.id": "I123+I456"}

# Negation
filter_params={"type": "!paratext"}
```

### Two-Step Pattern (Always for Entity Lookups)

Never filter by entity names directly — always get the ID first:

```python
# Step 1: Search -> get ID
author_resp = client._make_request('/authors', params={'search': 'Name', 'per-page': 1})
author_id = author_resp['results'][0]['id'].split('/')[-1]

# Step 2: Filter by ID
works = client.search_works(filter_params={"authorships.author.id": author_id})
```

### External IDs

```python
# DOI
client.get_entity('works', 'https://doi.org/10.1016/j.ejor.2023.01.001')

# ORCID
client.get_entity('authors', 'https://orcid.org/0000-0003-1613-5981')

# ROR (institution)
client.get_entity('institutions', 'https://ror.org/02y3ad647')

# ISSN (journal)
client.get_entity('sources', 'issn:0377-2217')  # [Journal]
```

---

## Output Formats

When presenting results, format as a markdown table:

```markdown
| # | Title | Authors | Year | Journal | Citations | DOI |
|---|-------|---------|------|---------|-----------|-----|
| 1 | ... | ... | 2024 | [Journal] | 42 | 10.1016/... |
```

For BibTeX export (to feed into project `.bib`):

```python
for work in papers:
    authors = " and ".join(
        a['author']['display_name']
        for a in work.get('authorships', [])
    )
    last_name = work['authorships'][0]['author']['display_name'].split()[-1]
    key = last_name + str(work['publication_year'])
    print(f"@article{{{key},")
    print(f"  author = {{{authors}}},")
    print(f"  title = {{{work['title']}}},")
    print(f"  year = {{{work['publication_year']}}},")
    if work.get('doi'):
        print(f"  doi = {{{work['doi'].replace('https://doi.org/', '')}}},")
    print("}")
```

---

## Rate Limits

| Pool | Rate | How to access |
|------|------|---------------|
| Default | 1 req/sec, 100k/day | No email |
| Polite | 10 req/sec, 100k/day | Pass email to client |

Always use the polite pool.

---

## MCP Server (Preferred Over Python Client)

**Always prefer MCP tools when available.** The biblio MCP server (`.mcp-server-biblio/`) exposes all OpenAlex functionality plus cross-source search — no Python boilerplate needed.

| Task | MCP tool (preferred) | Python client (fallback) |
|------|---------------------|-------------------------|
| Search papers by topic | `scholarly_search` (all sources) | `find_highly_cited_recent_papers()` |
| Look up a DOI | `openalex_lookup_doi` | `client.get_entity()` |
| Batch DOI verification | `scholarly_verify_dois` | Manual loop |
| Find similar papers | `scholarly_similar_works` | N/A |
| Author publications | `openalex_author_works` | `find_author_works()` |
| Author profile | `openalex_author_profile` | `analyze_research_output()` |
| Institution output | `openalex_institution_output` | `analyze_research_output()` |
| Publication trends | `openalex_trends` | `get_publication_trends()` |
| Forward citations | `openalex_citing_works` | Manual `cited_by_api_url` fetch |
| Check active sources | `scholarly_source_status` | N/A |

Use the Python client below only for workflows not yet exposed via MCP (custom filter combinations, batch entity lookups by non-DOI IDs). See [`docs/mcp-server.md`](../../../docs/mcp-server.md) for full MCP documentation.

---

## Complementary Skills

- **`/literature`** (parent skill) — OpenAlex serves as Phase 2 Agent 3 alongside Google Scholar and Semantic Scholar. Its API returns structured metadata that web scraping often misses.
- **`/validate-bib`** — Use batch DOI lookup (Workflow 7) to verify metadata for flagged entries.
- **`/split-pdf`** — Use OA discovery (Workflow 5) to find downloadable PDFs before split-reading.
