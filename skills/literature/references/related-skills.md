# Related Skills and Tools

## Cross-References

| Skill / Package | When to use instead/alongside |
|-------|-------------------------------|
| `/interview-me` | Develop a specific idea before searching |
| `/bib-validate` | **Mandatory** after assembling `.bib` (Phase 6b) — metadata quality, preprint staleness, DOI checks |
| `/bib-coverage` | Compare project `.bib` vs Paperpile label — find uncited papers and unfiled references |
| `/split-pdf` | Deep-read a paper found during search |
| `/gather-readings` | Run after literature to download PDFs for new papers |
| `/bib-coverage` | Run after literature to check uncited papers |
| `cli-council` | Multi-model search (Phase 2b) and synthesis (Phase 7) — `packages/cli-council/` |
| `paperpile` CLI | Search personal Paperpile library, extract PDF text/annotations, export BibTeX. Use in Phase 1 to check what's already in the library before searching externally. GROBID tools (`parse_pdf_metadata`, `parse_pdf_references`) extract structured metadata and bibliographies from PDFs — use after downloading to auto-extract refs without manual reading |
| `shared/reference-resolution.md` | Canonical lookup + filing sequence used by Phase 1 and Phase 6c |
| arXiv MCP tools | `scholarly arxiv-search`, `scholarly arxiv-get-paper`, `scholarly arxiv-search-category` — preprint search. See [references/arxiv-api-guide.md](arxiv-api-guide.md) |
| Exa MCP tools | `scholarly exa-search`, `scholarly exa-search-papers`, `scholarly exa-get-contents` — semantic web search, grey literature. Requires `EXA_API_KEY` |
| Deep loop protocol | [references/deep-loop-protocol.md](deep-loop-protocol.md) — iterative gap analysis + targeted search |
| `shared/worker-critic-protocol.md` | Inline review of synthesis output before reporting done |
| `shared/sources-cache.md` | Cache search results to avoid redundant API calls across sessions |

## Bibliometric Resources

Four bibliometric sources available via the `scholarly` CLI (and direct APIs as fallback). Includes CLI command table, OpenAlex workflows, Scopus query syntax, and WoS API tiers.

Full reference: [`references/bibliometric-apis.md`](bibliometric-apis.md) | API guides: [OpenAlex](openalex-api-guide.md), [Scopus](scopus-api-guide.md), [WoS](wos-api-guide.md)

## Reading Full Paper Text from arXiv

Download arXiv LaTeX source for full-text reading (equations, methodology, exact phrasing). Only works for arXiv papers with source available — for journal-only papers, use `/split-pdf`.

**Full instructions:** [references/cli-council-search.md](cli-council-search.md#reading-full-paper-text-from-arxiv)
