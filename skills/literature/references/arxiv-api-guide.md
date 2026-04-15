# arXiv API Reference

> For use by the `/literature` skill — Phase 2 pre-fetch and Phase 4.5 deep loop.
> arXiv is now available as an MCP tool (`arxiv_search`, `arxiv_get_paper`, `arxiv_search_category`).

## MCP Tools (Preferred)

Use these instead of raw WebFetch — they handle XML parsing and return Paper objects.

| Tool | Use case |
|------|----------|
| `arxiv_search` | General search with optional category filter |
| `arxiv_get_paper` | Fetch by arXiv ID (e.g., `2301.07041`) |
| `arxiv_search_category` | Search within a specific category |

## Category Codes (Common)

| Category | Domain |
|----------|--------|
| `econ.GN` | General Economics |
| `econ.TH` | Theoretical Economics |
| `econ.EM` | Econometrics |
| `cs.AI` | Artificial Intelligence |
| `cs.GT` | Computer Science and Game Theory |
| `cs.MA` | Multi-Agent Systems |
| `cs.CL` | Computation and Language (NLP) |
| `cs.HC` | Human-Computer Interaction |
| `cs.LG` | Machine Learning |
| `stat.ML` | Machine Learning (Statistics) |
| `stat.ME` | Methodology |
| `q-fin.GN` | General Finance |
| `q-fin.TR` | Trading and Market Microstructure |

## Query Syntax (for MCP tool `query` parameter)

The `arxiv_search` tool accepts natural language queries. For advanced use, arXiv operators are passed through:

```
ti:keyword        — title search
au:author         — author search
abs:keyword       — abstract search
cat:cs.AI         — category filter
AND, OR, ANDNOT   — boolean operators
```

Examples:
```
"mechanism design auctions"                           → searches title + abstract
ti:"multi-agent" AND cat:cs.MA                        → title search within category
au:smith AND abs:"reinforcement learning"             → author + abstract
(ti:auction OR ti:"mechanism design") AND cat:econ.GN → complex query
```

## Rate Limits

- No authentication required
- Polite rate: 1 concurrent request (enforced by the adapter)
- Max 200 results per query
- Results are Atom XML, parsed automatically by the adapter

## When to Use arXiv vs Other Sources

| Need | Source |
|------|--------|
| Latest preprints (not yet peer-reviewed) | arXiv |
| CS/AI conference papers | DBLP (better venue metadata) |
| Peer-reviewed publications | `scholarly_search` (multi-source) |
| Specific arXiv paper by ID | `arxiv_get_paper` |
| Category-specific preprint scan | `arxiv_search_category` |
