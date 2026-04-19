# Literature — Phase 2: Parallel Search (Sub-Agents)

> CLI pre-fetch from main context or sub-agents, then 2-3 Explore agents in parallel.

## CLI Pre-Fetch

Run these `scholarly` CLI commands to gather results. The CLI works inside sub-agents too — pre-fetch from main context (and pass file paths to agents) or let agents shell out directly. Write results to `/tmp/lit-search/*.json`.

**Apply confirmed Phase 1.5 filters.** If the user confirmed `year_min` / `year_max` in the search plan, append `--year-from <year_min> --year-to <year_max>` to every `scholarly-search`, `scholarly-search-scopus`, and `scholarly-search-wos` call below. For `openalex-search-works`, use `--year "<year_min>-<year_max>"`. Omit the flag if the corresponding value is blank.

1. **`scholarly scholarly-search`** — cross-source keyword search (OpenAlex + S2 + Scopus + WoS). Write to `/tmp/lit-search/bibliography-results.json`.
2. **`scholarly scholarly-similar-works`** — ML-based recommendations (powered by S2 Recommendations API). Pass the topic description as text to find semantically related papers beyond keyword matches. Write to `/tmp/lit-search/similar-results.json`.
3. **`scholarly scholarly-author-papers`** — if key authors are known, fetch their publication lists. Write to `/tmp/lit-search/author-results.json`.
4. **`scholarly arxiv-search`** — preprints in physics, maths, CS, econ, stats. Use `scholarly arxiv-search-category` for targeted subdomain search (e.g., `econ.GN`, `cs.AI`). Write to `/tmp/lit-search/arxiv-results.json`. Best for: latest working papers, CS/ML overlap, preprint-heavy fields. See [arxiv-api-guide.md](arxiv-api-guide.md).
5. **`scholarly exa-search-papers`** (if `EXA_API_KEY` set) — semantic search for research papers via Exa. Finds grey literature, working papers, and papers not indexed by traditional databases. Write to `/tmp/lit-search/exa-results.json`. Best for: interdisciplinary work, reports, non-traditional academic outputs.

## Parallel Agents

Spawn **2-3 Explore agents in parallel** in a single message, one per source. Read the full prompt templates from [agent-templates.md](agent-templates.md#phase-2-search-agent-templates).

Available search agents:
1. **Google Scholar** — broad academic search via web (no MCP needed)
2. **Cross-Source bibliometric search** (recommended) — agents call `scholarly` CLI directly or read pre-fetched results from `/tmp/lit-search/`, supplemented with WebSearch
3. **Semantic Scholar / arXiv** (optional) — CS/ML focused, useful when topic has strong CS overlap (no MCP needed)
4. **Domain-specific** (optional) — SSRN, NBER, specific journals (no MCP needed)

**Both `scholarly` and `paperpile` CLIs work inside sub-agents.** You can either pre-fetch from main context and pass file paths, or let agents shell out directly. Pre-fetching is still useful when multiple agents need the same base results.
