# Literature — Phase 1.5: Search Plan & Confirmation Gate

> Both standalone and pipeline modes. Present plan before launching any searches and wait for confirmation.

## Steps

1. **Restate the research question / topic** — confirm you understood the query correctly
2. **List search queries** — 3-6 keyword queries you plan to run across sources, grouped by:
   - **Track A (Substantive):** theory and empirical findings on the core phenomenon
   - **Track B (Empirical comparanda):** work using comparable data, cases, or designs
   - **Track C (Methodological precedents):** papers establishing or applying the methods
3. **List seed authors/venues** (if known) — key scholars or journals to target
4. **Note scope boundaries** — what you will and will NOT search for
5. **Propose filters (optional)** — `year_min` and `year_max` apply globally to every Phase 2 search call. Leave unset for no restriction. Propose defaults only when the topic has an obvious temporal boundary (e.g., post-2015 for transformer-era NLP); otherwise leave blank and let the user add them.

## Presentation

```
Search plan:
- Topic: <restated RQ/topic>
- Track A queries: [list]
- Track B queries: [list]
- Track C queries: [list]
- Seed authors: [list or "none identified"]
- Scope: [boundaries]
- Filters: year_min=<YYYY or blank>, year_max=<YYYY or blank>
```

**Wait for confirmation or corrections before proceeding to Phase 2.** One word ("yes", "go") is enough. If the user corrects a query, scope, or filter, adjust before searching.

## Filter Propagation

Confirmed `year_min` / `year_max` values propagate to every Phase 2 and Phase 4.5 search call as `--year-from <year_min> --year-to <year_max>`. Supported natively on:
- `scholarly scholarly-search` (multi-source)
- `scholarly scholarly-search-scopus`
- `scholarly scholarly-search-wos`
- `scholarly openalex-search-works` (via `--year "<year_min>-<year_max>"`)

If a value is blank, omit the flag rather than passing an empty string.

## Book Coverage Check

If the topic plausibly has major book-length treatments (common in comparative politics, political theory, area studies, organisational behaviour), flag this in the search plan: "This topic likely has significant book-length work — I'll supplement API results with publisher catalogue and handbook searches."

API-based search (OpenAlex, Crossref, S2) systematically underrepresents books and edited volumes.
