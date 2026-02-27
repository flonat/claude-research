# Preprint Staleness Check

> Reference file for `/validate-bib`. Protocol for checking whether preprints have been published.

## Detection — identify preprint entries by any of:

| Signal | Examples |
|--------|----------|
| URL/DOI contains preprint host | `arxiv.org`, `ssrn.com`, `nber.org`, `repec.org`, `econpapers`, `ideas.repec` |
| Journal/howpublished field | "arXiv preprint", "SSRN", "NBER Working Paper", "Working Paper", "mimeo" |
| Entry type | `@techreport`, `@unpublished`, `@misc` with working-paper-like metadata |
| Note field | Contains "preprint", "working paper", "wp", "discussion paper" |

## Lookup — find the published version:

1. **Biblio MCP `scholarly_search` first** (preferred — queries OpenAlex + Scopus + WoS with dedup):
   Call `scholarly_search` with the paper title as query. Check if any result has a journal/venue and is not itself a preprint. Cross-source search increases the chance of finding the published version.
2. **DOI resolution fallback**: If the preprint has a DOI, check if it redirects to or links to a published version.
3. **Web search last resort**: Search for the paper title + "published" or "journal" if MCP returns nothing.

## Classification:

| Finding | Severity | Message |
|---------|----------|---------|
| Published version exists | **Warning** | "Preprint `key` appears published in *Journal Name* (Year). Consider updating the .bib entry." |
| Published version exists with different title/authors | **Warning** | "Preprint `key` may have been published as '*new title*' in *Journal*. Verify and update." |
| No published version found | **Info** | "Preprint `key` — no published version found (checked YYYY-MM-DD)." |

## Report section:

Add a `## Warning: Stale Preprints` section to the report listing all preprints where a published version was found, with the suggested replacement metadata (journal, year, DOI).
