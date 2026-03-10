---
name: literature
description: "Academic literature discovery, synthesis, and bibliography management. Find papers, verify citations, create .bib files, download PDFs, and synthesize literature narratives. Includes OpenAlex, Scopus, and Web of Science API integration for structured scholarly queries."
allowed-tools: Bash(curl*), Bash(wget*), Bash(mkdir*), Bash(ls*), Bash(uv*), Bash(cd*), Read, Write, Edit, WebSearch, WebFetch, Task
argument-hint: [topic-or-paper-query]
---

# Literature Skill

**CRITICAL RULE: Every citation must be verified to exist before inclusion.** Never include a paper you cannot find via web search. Hallucinated citations are worse than no citations.

**DOI INTEGRITY RULE: Every DOI must be programmatically verified before entering any `.bib` file.** Sub-agents hallucinate plausible-looking DOIs that resolve to wrong papers (e.g., correct journal prefix, wrong suffix). The ONLY reliable verification is `scholarly_verify_dois` with title-matching (see Phase 4). A DOI that resolves to a different title than expected is WRONG — treat it the same as a missing DOI.

**CITATION KEY RULE: ALWAYS use Better BibTeX-format keys (e.g., `Author2016-xx`).** When merging into an existing `.bib`, match existing keys. Never generate custom keys (`AuthorYear`, `AuthorKamenica2017`, etc.) or retain non-standard keys unless the user explicitly says otherwise.

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

**PREPRINT RULE: Always prefer the published version.** If a paper is found on arXiv, SSRN, NBER, or any working paper series, search for a published journal/conference version. Only cite a preprint if no published version can be found.

> Comprehensive academic literature workflow: discover, verify, organize, synthesize.
> Uses parallel sub-agents to search multiple sources, verify citations, and fetch PDFs concurrently.

## When to Use

- Starting a new research project
- Writing a literature review section
- Building a reading list on a topic
- Finding specific citations
- Creating annotated bibliographies

---

## Architecture: Orchestrator + Sub-Agents

```
You (orchestrator)
├── Phase 0: Session log & compact (mandatory — /session-log)
├── Phase 1: Pre-search check (direct — no sub-agent)
├── Phase 2: Parallel search (2-3 Explore agents)
├── Phase 2b: CLI Council search (optional — multi-model recall via cli-council)
├── Phase 3: Deduplicate + rank (direct — no sub-agent)
├── Phase 4: Parallel verification (general-purpose agents, batches of 5)
├── Phase 5: Parallel PDF download (Bash agents)
├── Phase 6: Assemble .bib (direct — no sub-agent)
├── Phase 6c: Sync to reference managers (Paperpile + Zotero via MCP)
└── Phase 7: Synthesize narrative (direct, or cli-council for multi-model synthesis)
```

**Key principle:** Sub-agents handle independent, parallelizable work. Merging, deduplication, and synthesis stay with you because they need the full picture.

**Full agent prompt templates for all phases:** [references/agent-templates.md](references/agent-templates.md)

---

## Phase 0: Session Log & Compact (Mandatory)

Literature searches are context-heavy. **Always** run `/session-log` before starting to create a recovery checkpoint.

---

## Phase 1: Pre-Search Check (Direct)

Check for existing `.bib` files in project root, `/references`, `/bib`, `/bibliography`:

1. Parse existing entries to avoid duplicates and understand context
2. Identify gaps — note if bibliography skews toward certain years/methods
3. Compile list of existing citation keys to pass to sub-agents
4. **Check Paperpile library** — call `mcp__paperpile__search_library` for the search topic. This finds papers the user already has, preventing re-discovery of known work. Mark these as **ALREADY IN LIBRARY** and skip them in Phase 2. Also call `mcp__paperpile__get_items_by_label` if a relevant folder exists to get the full reading list for this topic.
5. **Check Zotero library** (legacy) — call `search_library` (refpile MCP) for the search topic. Same purpose as above. If refpile MCP is unavailable, log a warning and continue.
6. **Check source availability** — call `scholarly_source_status` (bibliography MCP) to see which sources are active (OpenAlex always; Scopus and WoS if API keys are set). Report this so search agents know what coverage to expect.

---

## Phase 2: Parallel Search (Sub-Agents)

Spawn **2-3 Explore agents in parallel** in a single message, one per source. Read the full prompt templates from [references/agent-templates.md](references/agent-templates.md#phase-2-search-agent-templates).

Available search agents:
1. **Google Scholar** — broad academic search via web
2. **Cross-Source via bibliography MCP** (recommended) — call `scholarly_search` to query all enabled sources (OpenAlex + Scopus + WoS) with automatic DOI-based deduplication. Returns structured metadata, citation counts, and DOIs — reducing Phase 4 verification work significantly
3. **Semantic Scholar / arXiv** (optional) — CS/ML focused, useful when topic has strong CS overlap
4. **Domain-specific** (optional) — SSRN, NBER, specific journals

**Prefer the bibliography MCP `scholarly_search` tool over the raw Python client** — it queries all configured sources in one call and deduplicates automatically. Use it as Agent 2 alongside Google Scholar for maximum coverage.

---

## Phase 2b: CLI Council Search (Optional)

Multi-model literature search via `cli-council` — runs the same query through Gemini, Codex, and Claude for maximum recall. Use for broad reviews (20+ papers) or interdisciplinary topics.

**Full invocation, prompt template, and post-processing:** [references/cli-council-search.md](references/cli-council-search.md#phase-2b-cli-council-search-optional)

---

## Phase 3: Deduplicate and Rank (Direct)

1. **Merge** results from all search agents (Phase 2 + Phase 2b if used)
2. **Remove duplicates** — match on title similarity and DOI
3. **Rank** by relevance, citation count, and recency
4. **Select top N** to verify (typically 25-30 candidates for 20-25 verified)
5. **Assign batches** of ~5 for verification

---

## Phase 4: Parallel Verification (Sub-Agents)

**Step 1 — Batch DOI pre-verification via MCP:** Collect all DOIs from Phase 3 candidates and call `scholarly_verify_dois` (bibliography MCP). This checks each DOI against all enabled sources (OpenAlex, Scopus, WoS). For each result:
- **VERIFIED (2+ sources):** Check that the **returned title matches** the expected paper. If the title doesn't match, the DOI is wrong — flag as DOI MISMATCH and find the correct DOI in Step 2.
- **SINGLE_SOURCE:** Needs manual verification — the DOI may be real but unconfirmed.
- **NOT_FOUND:** DOI is likely hallucinated. Find the correct DOI in Step 2.

**Title-matching is mandatory.** `scholarly_verify_dois` returns the title each DOI actually resolves to. Compare this against the title you expect. DOIs that are off by one character in the suffix (e.g., `02387` vs `02366`, `2014.01.014` vs `2014.03.013`) are the most common hallucination pattern — they resolve to real papers in the same journal but with different content.

**Step 2 — Find correct DOIs for flagged papers:** For any paper where the DOI was wrong, missing, or single-source, use these methods **in order of reliability**:
1. **Crossref API** (most reliable): `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` — returns the actual DOI from publisher metadata.
2. **`scholarly_search`** with exact title — searches OpenAlex/Scopus/WoS for the paper.
3. **Web search as last resort** — but DOIs from web search must still be verified via `scholarly_verify_dois` before use.

**Step 3 — Manual verification for remaining papers:** Spawn **multiple general-purpose agents in parallel**, each verifying ~5 papers. Read the full verification template from [references/agent-templates.md](references/agent-templates.md#phase-4-verification-agent-template). **Include the Crossref instruction** in the agent prompt — agents must use Crossref API for DOI lookup, not reconstruct DOIs from memory.

Key rules enforced by the template:
- DOI verification is mandatory (resolve and confirm)
- ALL authors must be listed (never "et al." in metadata)
- Preprint check: always search for published version; use `scholarly_search` MCP tool to find published versions of preprints
- Results: VERIFIED / NOT FOUND / METADATA MISMATCH

**Step 4 — Final DOI gate:** Before proceeding to Phase 5/6, run `scholarly_verify_dois` one final time on ALL DOIs that will enter the `.bib`. This is the hard gate — no DOI enters a bibliography without passing this check with a matching title. Papers without DOIs (working papers, book chapters, old pre-DOI articles) are acceptable but must be explicitly flagged as `% NO DOI` in the `.bib`.

After all return: collect VERIFIED, drop NOT FOUND, check for remaining duplicates.

---

## Phase 5: Parallel PDF Download (Sub-Agents)

Spawn Bash agents in parallel, 3-5 papers each. Read template from [references/agent-templates.md](references/agent-templates.md#phase-5-pdf-download-agent-template). Best-effort — many papers are behind paywalls.

---

## Phase 6: Assemble Bibliography (Direct)

**Two outputs required:**

1. **`docs/literature-review/literature_summary.bib`** — always created, standalone, self-contained
2. **Project canonical bib** (e.g. `paper/references.bib`) — merge into it if it exists

### BibTeX Format

```bibtex
@article{AuthorYear,
  author    = {Last, First and Last, First},
  title     = {Full Title},
  journal   = {Journal Name},
  year      = {2024},
  volume    = {XX},
  pages     = {1--20},
  doi       = {10.1000/example},
  abstract  = {Abstract text here.}
}
```

Rules:
- Citation keys: use **Better BibTeX-format keys** (e.g., `Author2016-xx`). If merging into an existing `.bib`, match the key format already in use. Never generate `AuthorYear` keys.
- Only VERIFIED papers — no METADATA MISMATCH entries
- **List ALL authors explicitly** — never "et al." in BibTeX
- Include abstracts when available

---

## Phase 6b: Validate Bibliography (Mandatory)

**After assembling the `.bib`, always run `/bib-validate`.** The Phase 4 verification checks that papers exist, but `/bib-validate` catches a different class of issues:

- Missing required BibTeX fields (journal, volume, pages)
- Preprint staleness (arXiv paper now published in a journal)
- Missing or incorrect DOIs
- Author formatting problems ("et al." in author field, corporate names needing braces)
- Unused entries and possible typos

This is **not optional** — every time new entries are added to a `.bib` file, run the validation before considering the bibliography complete.

---

## Phase 6c: Sync to Reference Managers

After assembling and validating the `.bib`, sync new references to the user's reference libraries.

### Paperpile (Primary)

For each new entry not marked **ALREADY IN LIBRARY** from Phase 1:

1. **Check if already in Paperpile** — call `mcp__paperpile__search_library` by title to avoid duplicates
2. **Report additions needed** — list entries that need manual import into Paperpile (Paperpile MCP is read-only; the user adds via the Paperpile app or browser extension)
3. **Export BibTeX** — if Paperpile has entries with better metadata than what was assembled, call `mcp__paperpile__export_bib` and use those entries instead

### Zotero (Legacy)

For each new entry not already in Zotero:

1. **Auto-add to Zotero** — call `add_item` (refpile MCP) for each new reference with full metadata (title, authors, year, journal, DOI).
2. **Tag for review** — call `add_to_collection` with the `_Needs Review` collection so the user can verify entries in the Zotero app.
3. **Report results** — show a summary table of what was added and remind the user to check `_Needs Review` in Zotero.

**Graceful degradation:** If either MCP is unavailable, skip that source with a warning. The `.bib` file on disk is still the primary output.

---

## Phase 7: Synthesize Narrative (Direct or CLI Council)

1. **Identify themes** — group papers by approach, finding, or debate
2. **Map intellectual lineage** — how did thinking evolve?
3. **Note current debates** — where do researchers disagree?
4. **Find gaps** — what's missing?

Output types: narrative summary (LaTeX), literature deck, annotated bibliography.

### Multi-Model Synthesis (Optional)

For comprehensive literature reviews, run the synthesis through `cli-council` to get three independent interpretations of the literature landscape. Different models identify different themes, debates, and gaps.

```bash
cd "packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/lit-synthesis-prompt.txt \
    --context-file /tmp/lit-papers.txt \
    --output-md /tmp/lit-synthesis-report.md \
    --chairman claude \
    --timeout 180
```

Where `--context-file` contains the verified paper list with titles, abstracts, and metadata, and the prompt asks for thematic grouping, intellectual lineage, and gap identification. The chairman synthesises three independent narratives into one.

---

## Output Structure

```
project/
├── docs/
│   ├── literature-review/
│   │   ├── literature_summary.md      # Thematic narrative (always)
│   │   └── literature_summary.bib     # Standalone .bib (always)
│   └── readings/
│       ├── Smith2024.pdf              # Downloaded PDFs
│       └── ...
└── paper/
    └── references.bib                  # Canonical bib (merge if exists)
```

---

## Sub-Agent Guidelines

0. **Python: ALWAYS use `uv run python`.** Include this in every sub-agent prompt.
1. **Launch independent agents in a single message** for parallelism
2. **Be explicit in prompts** — sub-agents have no context
3. **Include skip lists** of existing citation keys
4. **Batch sizes:** 5 papers per verification agent, 3-5 per PDF agent
5. **Maximum 3 parallel agents at a time** — spawn in waves, write results to disk between waves. Each agent should write to a temp file (e.g., `/tmp/lit-search/agent-N.json`) rather than returning large payloads in-context. Summarise from files to avoid context overflow.
6. **Right agent type:** `Explore` for search, `general-purpose` for verification, `Bash` for downloads
7. **Tolerate partial failures** — continue with what you have

---

## Bibliometric API Structured Queries

Three bibliometric sources are available. The **bibliography MCP server** (`.mcp-server-bibliography/`) is the preferred interface — `scholarly_search` queries all enabled sources in one call with automatic DOI-based dedup; `scholarly_verify_dois` batch-verifies DOIs across all sources. Use the Python clients only for source-specific workflows not yet exposed via MCP (e.g., citation networks, institution analysis).

### OpenAlex (always available)

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

**Full recipes:** [references/openalex-workflows.md](references/openalex-workflows.md) | **API guide:** [references/openalex-api-guide.md](references/openalex-api-guide.md)

### Scopus (requires `SCOPUS_API_KEY` + `SCOPUS_INST_TOKEN`)

Query syntax: `TITLE-ABS-KEY("quoted phrases" OR terms)`, subject areas via `SUBJAREA(CODE)`, year filters via `PUBYEAR > N` / `PUBYEAR < N`. Elsevier REST API with `X-ELS-APIKey` + `X-ELS-Insttoken` headers. Provides abstracts, author keywords, and citation counts in COMPLETE view. Pagination via `start`/`count` params (max 25 per page).

**API guide:** [references/scopus-api-guide.md](references/scopus-api-guide.md)

### Web of Science (requires `WOS_API_KEY`)

Query syntax: `TS=(topic search)`, year filter via `PY=(YYYY-YYYY)`. Two API tiers: **Starter** (`/documents` endpoint, page-based, max 50/page) and **Expanded** (root endpoint, `firstRecord`-based, max 100/page, includes abstracts). Auth via `X-ApiKey` header. Tier set via `WOS_API_TIER` env var (default: `starter`).

**API guide:** [references/wos-api-guide.md](references/wos-api-guide.md)

---

## Reading Full Paper Text from arXiv

Download arXiv LaTeX source for full-text reading (equations, methodology, exact phrasing). Only works for arXiv papers with source available — for journal-only papers, use `/split-pdf`.

**Full instructions:** [references/cli-council-search.md](references/cli-council-search.md#reading-full-paper-text-from-arxiv)

---

## Cross-References

| Skill / Package | When to use instead/alongside |
|-------|-------------------------------|
| `/scout generate` | Generate research questions first |
| `/interview-me` | Develop a specific idea before searching |
| `/bib-validate` | **Mandatory** after assembling `.bib` (Phase 6b) — metadata quality, preprint staleness, DOI checks |
| `/split-pdf` | Deep-read a paper found during search |
| `cli-council` | Multi-model search (Phase 2b) and synthesis (Phase 7) — `packages/cli-council/` |
| `refpile` MCP | Search personal Zotero library, extract PDF text/annotations, export BibTeX. Use in Phase 1 to check what's already in the library before searching externally |
