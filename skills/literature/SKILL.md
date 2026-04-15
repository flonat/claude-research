---
name: literature
description: "Use when you need academic literature discovery, synthesis, or bibliography management. Supports standalone searches and end-to-end project pipelines with vault sync and auto-commit."
allowed-tools: Bash(curl*), Bash(wget*), Bash(mkdir*), Bash(ls*), Bash(uv*), Bash(cd*), Bash(git*), Bash(cat*), Bash(date*), Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Task, Agent, Skill, mcp__bibliography__scholarly_search, mcp__bibliography__scholarly_verify_dois, mcp__bibliography__scholarly_paper_detail, mcp__bibliography__crossref_lookup_doi, mcp__bibliography__openalex_lookup_doi, mcp__bibliography__unpaywall_find_pdf, mcp__bibliography__arxiv_search, mcp__bibliography__arxiv_get_paper, mcp__bibliography__arxiv_search_category, mcp__bibliography__exa_search, mcp__bibliography__exa_search_papers, mcp__bibliography__exa_get_contents, mcp__bibliography__dblp_search, mcp__bibliography__scholarly_similar_works, mcp__bibliography__scholarly_citations, mcp__bibliography__scholarly_references, mcp__bibliography__scholarly_author_papers, mcp__bibliography__scholarly_source_status, mcp__paperpile__search_library, mcp__paperpile__get_items_by_label, mcp__paperpile__get_labels, mcp__paperpile__write_bib, mcp__paperpile__get_item, mcp__taskflow__search_tasks, mcp__taskflow__list_tasks, mcp__taskflow__update_task
argument-hint: "[topic-query] or <topic-slug> for full pipeline"
---

# Literature Skill

**CRITICAL RULE: Every citation must be verified to exist before inclusion.** Never include a paper you cannot find via web search. Hallucinated citations are worse than no citations.

**DOI INTEGRITY RULE: Every DOI must be programmatically verified before entering any `.bib` file.** Sub-agents hallucinate plausible-looking DOIs that resolve to wrong papers (e.g., correct journal prefix, wrong suffix). The ONLY reliable verification is `scholarly_verify_dois` with title-matching (see Phase 4). A DOI that resolves to a different title than expected is WRONG — treat it the same as a missing DOI.

**CITATION KEY RULE: ALWAYS use Better BibTeX-format keys (e.g., `Author2016-xx`).** When merging into an existing `.bib`, match existing keys. Never generate custom keys (`AuthorYear`, `AuthorKamenica2017`, etc.) or retain non-standard keys unless the user explicitly says otherwise.

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

**LIBRARY-FIRST RULE: ALWAYS check Paperpile (paperpile MCP) BEFORE any external search.** Call `mcp__paperpile__search_library` and `mcp__paperpile__search_library` for the topic in Phase 1. Do not skip this even if no `.bib` file exists yet. Papers already in either library should be reused, not re-discovered.

**PREPRINT RULE: Always prefer the published version.** If a paper is found on arXiv, SSRN, NBER, or any working paper series, search for a published journal/conference version using `scholarly_search`. Only cite a preprint if no published version can be found. This applies at every phase: Phase 2 (discovery), Phase 4 (verification), and Phase 6b (bib-validate runs the full preprint staleness check from `bib-validate/references/preprint-check.md`).

**CAUSAL LANGUAGE RULE: Match the strength of language to the study design.** Reserve causal verbs ("causes", "increases", "reduces", "leads to") for findings from designs that warrant causal inference (experiments, RCTs, credible quasi-experiments with clear identification). For observational/correlational work, use: "is associated with", "predicts", "correlates with". When summarising a paper in the narrative or bibliography annotations, match the language to the design — not to the authors' own claims. State disagreements precisely: who claims what, on what evidence. Do not flatten into "the literature is mixed."

> Comprehensive academic literature workflow: discover, verify, organize, synthesize.
> Uses parallel sub-agents to search multiple sources, verify citations, and fetch PDFs concurrently.
> Supports two modes: **standalone** (free-form query) and **pipeline** (topic-slug for full project-aware cycle with vault sync and auto-commit).

## Modes

| Mode | Invocation | What it does |
|------|-----------|-------------|
| **Standalone** | `/literature [topic query]` | Search + verify + bib + synthesis. No project context needed. |
| **Pipeline** | `/literature <topic-slug>` | Full cycle: resolve project → search → verify → bib → bib-validate gate → vault sync → auto-commit |
| **Deep** | `/literature --deep [query]` | Standalone or pipeline + iterative gap-filling loop (Phase 4.5). Also triggered by "deep", "thorough", or "comprehensive review" in the query. |

**How to detect mode:** If the argument matches an atlas topic slug (check `~/Research-Vault/atlas/` for a matching `.md` file), run in Pipeline mode. Otherwise, run in Standalone mode. When in doubt, ask.

## Shared References

- Concept validation gate: `shared/concept-validation-gate.md` — validate concept before synthesis
- Method-fitness gate: `shared/method-fitness-gate.md` — validate RQ-method alignment before search (pipeline mode only)
- Integrity gates: `shared/integrity-gates.md` — pipeline-blocking verification checkpoints
- Material passport: `shared/material-passport.md` — artifact provenance and staleness tracking
- Checkpoint resumability: `shared/checkpoint-resumability.md` — save/resume on crash (pipeline mode)
- LEARN tag routing: `shared/learn-tag-routing.md` — auto-inject corrections at invocation
- Escalation protocol: `shared/escalation-protocol.md` — escalate when research question is vague

## When to Use

- Starting a new research project
- Writing a literature review section
- Building a reading list on a topic
- Finding specific citations
- Creating annotated bibliographies
- End-to-end literature pipeline for a research topic (pipeline mode)

---

## Pipeline Mode: Project Context Resolution

**Only in pipeline mode** (when argument is a topic slug). Skip this section entirely in standalone mode.

1. **Find atlas topic file:**
   ```bash
   find ~/Research-Vault/atlas/ -name "<topic-slug>.md"
   ```

2. **Read topic frontmatter** — extract: `title`, `project_path`, `outputs`, `connected_topics`

3. **Resolve project directory:**
   ```bash
   RESEARCH_ROOT="$(cat ~/.config/task-mgmt/research-root)"
   PROJECT="$RESEARCH_ROOT/<project_path>"
   ```

4. **Locate the .bib file** — search for `references.bib`, `refs.bib`, or any `.bib` in the project and its `paper*/paper/` directories. If multiple, ask which one.

5. **Report context and wait for confirmation:**
   ```
   Topic: <title>
   Project: <project_path>
   Bib file: <path>
   Search query: <derived from title + keywords>
   ```

Then proceed to Phase 0 as normal. The project context informs Phase 1 (where to look for existing .bib) and Phase 6 (where to write output).

---

## Architecture: Orchestrator + Sub-Agents

```
You (orchestrator)
├── Phase 0: Session log & compact (mandatory — /session-log)
├── Phase 1: Pre-search check (direct — no sub-agent)
├── Phase 2: Parallel search (2-3 Explore agents + MCP pre-fetch incl. arXiv, Exa)
├── Phase 2b: CLI Council search (optional — multi-model recall via cli-council)
├── Phase 3: Deduplicate + rank (direct — no sub-agent)
├── Phase 3b: SciSciNet enrichment (direct — optional, adds disruption/novelty scores)
├── Phase 4: Parallel verification (general-purpose agents, batches of 5)
├── Phase 4.5: Iterative deep loop (optional — --deep flag, max 3 iterations)
│   ├── Gap analysis (direct)
│   ├── Query refinement (direct)
│   ├── Targeted search (MCP pre-fetch + sub-agents)
│   ├── Merge + dedup (direct)
│   └── Verify new papers (direct)
├── Phase 5: Parallel PDF download (Bash agents)
├── Phase 6: Assemble .bib (direct — no sub-agent)
├── Phase 6c: Sync to Paperpile via MCP
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
4. **MANDATORY: Check Paperpile library** — call `mcp__paperpile__search_library` for the search topic. Also call `mcp__paperpile__get_items_by_label` if a relevant label exists. This finds papers the user already has, preventing re-discovery of known work. Mark these as **ALREADY IN PAPERPILE** and reuse their citation keys. If Paperpile MCP is unavailable, log a warning and continue — but always attempt the call.
5. **Resolve topic label** — call `mcp__paperpile__get_labels` to find the label for the current topic. This label is used in Phase 6c for reporting.
7. **Check source availability** — call `scholarly_source_status` (bibliography MCP) to see which sources are active (OpenAlex always; Scopus and WoS if API keys are set). Report this so search agents know what coverage to expect.

**Steps 4 and 5 are NOT optional.** Every literature search must check both reference managers before external discovery. This prevents re-discovering papers already in the library and identifies migration candidates early.

---

## Phase 1.5: Search Plan & Confirmation Gate (Both Modes)

Before launching any searches, present a search plan and wait for confirmation. This applies to **both standalone and pipeline modes**.

1. **Restate the research question / topic** — confirm you understood the query correctly
2. **List search queries** — 3-6 keyword queries you plan to run across sources, grouped by:
   - **Track A (Substantive):** theory and empirical findings on the core phenomenon
   - **Track B (Empirical comparanda):** work using comparable data, cases, or designs
   - **Track C (Methodological precedents):** papers establishing or applying the methods
3. **List seed authors/venues** (if known) — key scholars or journals to target
4. **Note scope boundaries** — what you will and will NOT search for

Present to the user:
```
Search plan:
- Topic: <restated RQ/topic>
- Track A queries: [list]
- Track B queries: [list]
- Track C queries: [list]
- Seed authors: [list or "none identified"]
- Scope: [boundaries]
```

**Wait for confirmation or corrections before proceeding to Phase 2.** One word ("yes", "go") is enough. If the user corrects a query or scope, adjust before searching.

**Book coverage check:** If the topic plausibly has major book-length treatments (common in comparative politics, political theory, area studies, organisational behaviour), flag this in the search plan: "This topic likely has significant book-length work — I'll supplement API results with publisher catalogue and handbook searches." API-based search (OpenAlex, Crossref, S2) systematically underrepresents books and edited volumes.

---

## Phase 2: Parallel Search (Sub-Agents)

**MCP pre-fetch (main context, before spawning agents):** Call these bibliography MCP tools from the main context before spawning agents. MCP tools are not available inside sub-agents — they are permission-scoped to the main conversation context only. Write results to `/tmp/lit-search/`.

1. **`scholarly_search`** — cross-source keyword search (OpenAlex + S2 + Scopus + WoS). Write to `/tmp/lit-search/bibliography-results.json`.
2. **`scholarly_similar_works`** — ML-based recommendations (powered by S2 Recommendations API). Pass the topic description as text to find semantically related papers beyond keyword matches. Write to `/tmp/lit-search/similar-results.json`.
3. **`scholarly_author_papers`** — if key authors are known, fetch their publication lists. Write to `/tmp/lit-search/author-results.json`.
4. **`arxiv_search`** — preprints in physics, maths, CS, econ, stats. Use `arxiv_search_category` for targeted subdomain search (e.g., `econ.GN`, `cs.AI`). Write to `/tmp/lit-search/arxiv-results.json`. Best for: latest working papers, CS/ML overlap, preprint-heavy fields. See [references/arxiv-api-guide.md](references/arxiv-api-guide.md).
5. **`exa_search_papers`** (if EXA_API_KEY set) — semantic search for research papers via Exa. Finds grey literature, working papers, and papers not indexed by traditional databases. Write to `/tmp/lit-search/exa-results.json`. Best for: interdisciplinary work, reports, non-traditional academic outputs.

Spawn **2-3 Explore agents in parallel** in a single message, one per source. Read the full prompt templates from [references/agent-templates.md](references/agent-templates.md#phase-2-search-agent-templates).

Available search agents:
1. **Google Scholar** — broad academic search via web (no MCP needed)
2. **Cross-Source via pre-fetched biblio data** (recommended) — reads `/tmp/lit-search/bibliography-results.json` and `/tmp/lit-search/similar-results.json` (pre-fetched by the orchestrator) and supplements with WebSearch
3. **Semantic Scholar / arXiv** (optional) — CS/ML focused, useful when topic has strong CS overlap (no MCP needed)
4. **Domain-specific** (optional) — SSRN, NBER, specific journals (no MCP needed)

**The MCP calls happen in the main context (Phase 2 pre-fetch), not inside sub-agents.** Sub-agents read the pre-fetched results and supplement with web search.

---

## Phase 2b: CLI Council Search (Optional)

Multi-model literature search via `cli-council` — runs the same query through Gemini, Codex, and Claude for maximum recall. Use for broad reviews (20+ papers) or interdisciplinary topics.

**Full invocation, prompt template, and post-processing:** [references/cli-council-search.md](references/cli-council-search.md#phase-2b-cli-council-search-optional)

---

## Phase 2.5: Snowball Search (Optional — Main Context)

After Phase 2 results are merged, use S2's citation graph to expand the candidate pool via snowballing. This finds seminal papers (backward) and recent follow-ups (forward) that keyword search misses.

1. **Identify seed papers** — pick the 3-5 most relevant papers from Phase 2 results (highest citation count + relevance)
2. **Forward snowball** — call `scholarly_citations` for each seed to find papers that cite it. Useful for finding recent work building on foundational papers.
3. **Backward snowball** — call `scholarly_references` for each seed to find papers it cites. Useful for finding seminal/foundational works.
4. **Filter** — deduplicate against Phase 2 results, keep only papers with ≥5 citations (avoid noise)
5. **Add to candidate pool** — merge into the main list before Phase 3 ranking

**When to use:** Literature reviews, broad topic surveys, or when Phase 2 returned <15 unique papers. Skip for narrow/targeted searches where the initial results are sufficient.

**Paper detail enrichment:** For top candidates, call `scholarly_paper_detail` to get TLDR summaries (one-line AI-generated descriptions) — useful for rapid screening without reading abstracts.

---

## Phase 3: Deduplicate, Classify, and Rank (Direct)

1. **Merge** results from all search agents (Phase 2 + Phase 2b if used)
2. **Remove duplicates** — match on title similarity and DOI
3. **Field-framework extraction** — for each candidate, extract structured fields (see below)
4. **Rank** by relevance, citation count, and recency
5. **Select top N** to verify (typically 25-30 candidates for 20-25 verified)
6. **Assign batches** of ~5 for verification

### Field-Framework Definitions

For each paper entering the candidate pool, extract these structured fields from the abstract and metadata. This transforms raw search results into a structured database that enables systematic comparison, gap detection, and synthesis.

| Field | Description | Example |
|-------|-------------|---------|
| **Setting** | Country, sector, time period | "US healthcare, 2010-2020" |
| **Population** | Unit of analysis, sample characteristics | "Fortune 500 firms", "MTurk workers (N=400)" |
| **Method** | Identification strategy or research design | "DiD around ACA rollout", "3-study experiment" |
| **Data** | Dataset name and type | "COMPUSTAT + CRSP", "Custom survey" |
| **DV** | Dependent variable(s) | "Firm profitability (ROA)", "Decision accuracy" |
| **IV/Treatment** | Independent variable, treatment, or intervention | "AI adoption", "Algorithmic recommendation" |
| **Key finding** | Direction and magnitude of main result | "AI adoption → +12% productivity (p<.01)" |
| **Mechanism** | Proposed causal channel (if stated) | "Information processing capacity" |
| **Boundary** | Stated limitations or scope conditions | "Only large firms", "Lab setting" |

**When to extract:** Always. Even partial extraction (3-4 fields from abstract alone) is valuable for ranking and gap analysis. Full extraction happens after Phase 4 verification for the final verified set.

**How this helps downstream:**
- **Phase 3 ranking:** Papers with methods/settings similar to the user's project rank higher
- **Phase 4.5 gap analysis:** Systematic gaps become visible (e.g., "no experimental evidence", "all US samples")
- **Phase 7 synthesis:** Enables structured comparison tables and evidence maps
- **Hypothesis generation:** Feeds directly into `/hypothesis-generation` Phase 2

**Breadcrumb:** Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:
```
### [/literature] Phase 3 complete [YYYY-MM-DD HH:MM]
- **Done:** [N papers found, deduplicated from N sources, top N selected for verification]
- **Outputs:** [candidate list at /tmp/lit-search/]
- **Next:** SciSciNet enrichment → Parallel verification (DOI + metadata)
```

---

## Phase 3b: SciSciNet Enrichment (Direct — Optional)

**Skip if:** SciSciNet API is not reachable (`curl -sf http://localhost:8500/health` fails). This phase is purely additive — the pipeline works without it.

**Step 1 — Collect DOIs:** Gather all DOIs from the Phase 3 candidate list.

**Step 2 — Call paper-enrich:** Send DOIs in a single batch (max 100 per request):

```bash
curl -s -X POST http://localhost:8500/api/paper-enrich \
  -H "Content-Type: application/json" \
  -d '["10.1234/...", "10.5678/..."]'
```

**Step 3 — Merge scores into candidate metadata:** For each matched paper, add:

| Field | Source | Use in pipeline |
|-------|--------|-----------------|
| `disruption_score` | SciSciNet | Ranking boost (highly disruptive papers → higher priority) |
| `novelty_score` | SciSciNet | Flag novel methodological contributions |
| `conventionality_score` | SciSciNet | Identify consolidating/survey papers (useful for background sections) |
| `fields` | SciSciNet | Cross-reference with user's field — flag interdisciplinary connections |
| `is_hit_1pct` / `is_hit_5pct` | SciSciNet | Flag top-cited papers within their field-year cohort |

**Step 4 — Re-rank with enrichment:** Adjust Phase 3 rankings:
- Papers with `is_hit_1pct = true` → boost ranking (field-defining work)
- Papers with high `disruption_score` (> 0.1) → boost if the review seeks paradigm shifts
- Papers with high `conventionality_score` → prioritize for "background" and "established literature" sections
- Papers in adjacent `fields` not in the user's core area → flag as cross-pollination candidates

**Coverage note:** Not all papers will match (SciSciNet covers 11M papers, biased toward STEM/social science). Papers without matches retain their Phase 3 ranking unchanged. Log the match rate (e.g., "SciSciNet matched 18/25 candidates").

**Breadcrumb:** Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:
```
### [/literature] Phase 3b complete [YYYY-MM-DD HH:MM]
- **SciSciNet:** [M/N papers matched, avg disruption X.XXX, N hit-1% papers]
- **Next:** Parallel verification (DOI + metadata)
```

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

**Step 3 — Manual verification for remaining papers:** Spawn **multiple general-purpose agents in parallel**, each verifying ~5 papers. Read the full verification template from [references/agent-templates.md](references/agent-templates.md#phase-4-verification-agent-template). **Include the Crossref instruction** in the agent prompt — agents must use Crossref API (`curl`) for DOI lookup, not reconstruct DOIs from memory. **Do NOT instruct sub-agents to call MCP tools** (`scholarly_search`, `scholarly_verify_dois`) — MCP tools are not available in sub-agents. Sub-agents should use Crossref API and WebSearch/WebFetch only.

Key rules enforced by the template:
- DOI verification is mandatory (resolve and confirm)
- ALL authors must be listed (never "et al." in metadata)
- Preprint check: always search for published version; use `scholarly_search` MCP tool to find published versions of preprints
- Results: VERIFIED / NOT FOUND / METADATA MISMATCH

**Step 4 — Final DOI gate:** Before proceeding to Phase 5/6, run `scholarly_verify_dois` one final time on ALL DOIs that will enter the `.bib`. This is the hard gate — no DOI enters a bibliography without passing this check with a matching title. Papers without DOIs (working papers, book chapters, old pre-DOI articles) are acceptable but must be explicitly flagged as `% NO DOI` in the `.bib`.

After all return: collect VERIFIED, drop NOT FOUND, check for remaining duplicates.

**Step 5 — Assign metadata confidence grades:** Every verified paper gets a confidence grade:

| Grade | Criteria |
|-------|----------|
| **A** | DOI resolves correctly; metadata matches trusted source (publisher, Crossref, OpenAlex). Full metadata available. |
| **B** | Stable identifier; metadata consistent across ≥2 sources. No verified DOI, or minor metadata gaps. |
| **C** | Single non-canonical source or incomplete metadata. Include only if the item is the sole source for a needed concept/method/dataset; state what is unverified. |

When sources disagree on metadata, use publisher-of-record version and note the discrepancy. Carry the grade forward into Phase 6 (bibliography) and Phase 7 (synthesis output).

**Step 6 — Working paper inclusion test:** For any paper that remains a preprint/working paper after the preprint check, apply this structured gate. Include only if the paper meets **≥2** of these criteria:

1. High citations or downloads relative to age
2. Established author(s) with track record in the field
3. Presented at a top venue (note venue and year)
4. Sole source for a needed dataset, method, or concept
5. Verifiable forthcoming/accepted status

For each included working paper, **state which ≥2 criteria it meets** in the bibliography annotation. Label as "Working paper / preprint." No Confidence C working papers in the must-read shortlist without explicit justification.

**Breadcrumb:** Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:
```
### [/literature] Phase 4 complete [YYYY-MM-DD HH:MM]
- **Done:** [N verified, N dropped (not found), N DOI mismatches corrected]
- **Outputs:** [verified paper list ready for bib assembly]
- **Next:** PDF download → bib assembly → validation
```

---

## Phase 4.5: Iterative Deep Loop (Optional)

**Trigger:** User says "deep", "--deep", "thorough", or "comprehensive review". Only runs after Phase 4 verification and before Phase 5 PDF download.

**Prerequisites:** At least 5 verified papers from Phase 4 (need enough to identify gaps).

**Full protocol:** [references/deep-loop-protocol.md](references/deep-loop-protocol.md)
**Agent templates:** [references/agent-templates.md](references/agent-templates.md#phase-45-deep-loop-agent-templates)

### Loop (max 3 iterations)

For each iteration:

1. **Gap analysis** (main context) — Read verified papers, identify 2-4 specific gaps:
   - Missing time periods, methodologies, geographic contexts, theoretical perspectives
   - Key papers cited by found papers but not in the set
   - Produce targeted search queries for each gap

2. **Targeted search** (MCP pre-fetch + sub-agents) — For each gap:
   - Call appropriate MCP tools from main context: `scholarly_search` (academic), `arxiv_search` (preprints), `exa_search_papers` (grey literature), `dblp_search` (CS venues)
   - Write results to `/tmp/lit-deep-loop/gap-{N}-results.json`
   - Spawn Explore sub-agents to supplement with web search

3. **Merge + dedup** (main context) — Merge new results with existing pool, deduplicate by DOI and title similarity

4. **Verify new papers** (main context) — Same Phase 4 protocol but only for newly found papers. Batch DOI verification via `scholarly_verify_dois`.

### Convergence (any triggers exit)

| Trigger | Action |
|---------|--------|
| 3 iterations completed | Exit with full results |
| <3 genuinely new papers in an iteration | Exit — diminishing returns |
| User says "enough" or "stop" | Exit immediately |

### Reporting

After the deep loop, report:
```
Deep Search: {N} iterations, {gaps_found} gaps identified, {gaps_filled} filled, {new_papers} new papers added.
Remaining gaps: {list or "none"}
```

---

## Phase 5: Parallel PDF Download (Sub-Agents)

### Step 1 — Check Paperpile for existing PDFs (main context)

Before downloading anything, check if papers are already in Paperpile with PDFs attached:

1. For each verified paper, call `mcp__paperpile__search_library` with the title or DOI
2. If the paper exists in Paperpile and has a PDF → mark as **SKIP** (already have it)
3. If the paper exists but has no PDF → mark as **DOWNLOAD** (need the PDF)
4. If the paper is not in Paperpile → mark as **DOWNLOAD**

Report: "Skipping N papers already in Paperpile with PDFs. Downloading M remaining."

### Step 2 — Download remaining PDFs

Spawn Bash agents in parallel, 3-5 papers each (only for papers marked **DOWNLOAD**). Read template from [references/agent-templates.md](references/agent-templates.md#phase-5-pdf-download-agent-template). Best-effort — many papers are behind paywalls.

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
- **Reuse existing Paperpile citation keys** — for entries marked **ALREADY IN PAPERPILE** in Phase 1, use the Paperpile `citationKey` directly. Do not generate a new key.
- Only VERIFIED papers — no METADATA MISMATCH entries
- **List ALL authors explicitly** — never "et al." in BibTeX
- Include abstracts when available
- **S2 BibTeX seed:** Call `scholarly_paper_detail` for each verified paper to get pre-formatted BibTeX via the `citationStyles` field. Use as a starting template, then enrich with missing fields (abstract, pages, volume) and correct the citation key to BBT format. This reduces manual entry errors.
- **Confidence grade:** Add a BibTeX comment above each entry with its confidence grade from Phase 4: `% Confidence: A` (or B/C). This is metadata for the literature review, not for LaTeX.
- **Working paper criteria:** For working papers, add a comment noting which inclusion criteria were met: `% WP criteria: established author + sole source for concept`
- **Connection note:** Every entry in `literature_summary.md` must include a **connection note** — a 1-sentence link to ≥1 other entry in the bibliography ("agrees with", "extends", "contradicts", "uses same data as", "applies method from"). This prevents the bibliography from reading as an isolated list. Connection notes go in the annotation/summary, not in the `.bib` file.

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

After assembling and validating the `.bib`, sync new references to Paperpile (primary reference manager) and cross-reference with Paperpile (read-only). Handles migration candidates and post-run maintenance.

Full steps: [`references/reference-manager-sync.md`](references/reference-manager-sync.md)

**Breadcrumb:** Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:
```
### [/literature] Phase 6c complete [YYYY-MM-DD HH:MM]
- **Done:** [N entries in .bib, bib-validate result, Paperpile sync status]
- **Outputs:** [.bib at <path>, lit review at <path>]
- **Next:** Pipeline completion (if pipeline mode) or synthesis
```

---

## Phase 6d: Pipeline Completion (Pipeline Mode Only)

**Skip this phase entirely in standalone mode.**

After Phase 6b passes (bib-validate clean) and Phase 6c completes:

### 1. Vault Sync

Update the vault topic entry with new paper count or related metadata. Use `mcp__taskflow__update_task` if a related task exists.

### 2. Knowledge Wiki Filing

If `knowledge/` exists in the project directory:
- For each new paper added, extract a one-line key finding
- File each finding into the relevant knowledge article
- If no matching article exists, create one for the concept
- Skip silently if no `knowledge/` directory exists

### 3. Auto-Commit (Hard Gate)

Only commit if bib-validate passed clean. Do NOT commit if issues remain.

```bash
cd "$PROJECT"
git add <bib-file> <lit-review-file>
git commit -m "literature: add N papers for <topic-slug>"
```

Do NOT push — verify remote first per git-safety rule.

### 4. Final Summary (Pipeline Mode)

```
Literature pipeline complete for <topic>

Papers added: N (M already held, K new)
Bib file: <path> — N total entries
Lit review: <path> — updated/created
Knowledge: filed N findings to knowledge/ (or: skipped — no knowledge dir)
Vault: <topic entry updated>
Bib-validate: PASS
Commit: <hash>

Next: review new entries, push when ready
```

---

## Phase 7: Synthesize Narrative (Direct or CLI Council)

1. **Identify themes** — group papers by approach, finding, or debate
2. **Map intellectual lineage** — how did thinking evolve?
3. **Note current debates** — where do researchers disagree?
4. **Find gaps** — what's missing?
5. **Negative evidence** — per cluster, include ≥1 null finding, failed replication, or measurement critique when such work exists. If none exists for a cluster, state this explicitly: "No null or replication evidence found for [cluster]." This is mandatory, not optional — negative evidence is as important as positive evidence for positioning a project.
6. **Cross-cluster synthesis** — after all clusters, write 1-2 paragraphs identifying: (a) how clusters connect or depend on each other; (b) tensions between clusters (e.g., theory in Cluster 1 predicts X, but empirical work in Cluster 3 finds the opposite); (c) what the combined landscape implies for the user's project. Do not just list clusters in isolation.

Output types: narrative summary (LaTeX), literature deck, annotated bibliography, concise field synthesis.

**After deep loop (Phase 4.5):** If the deep loop ran, include an explicit "Remaining Gaps" section in the synthesis — document what couldn't be found and suggest manual search strategies. This turns gaps into actionable next steps rather than hiding them.

### Concise Field Synthesis (~400 words)

When the user asks for a "quick synthesis", "field overview", or "what does the literature say", produce a tight ~400-word synthesis instead of a full narrative. No paper-by-paper summaries — write about the field, not individual papers.

Structure:
1. **What the field collectively believes** — established consensus (2-3 sentences)
2. **Where researchers disagree** — active debates with camps identified (2-3 sentences)
3. **What has been proven** — findings with strong, replicated evidence (2-3 sentences)
4. **The single most important unanswered question** — one question, why it matters, why it's hard (2-3 sentences)

Cite papers parenthetically (Author, Year) but never summarise individual papers. The goal is a helicopter view that a newcomer could read in 2 minutes and understand where the field stands.

### [VERIFY] Citation Tags

When synthesising, mark uncertain attributions with `[VERIFY]` tags for later resolution:

```markdown
Meraz and Papacharissi (2013) argue that gatekeeping power shifted
from institutional positions to network centrality [VERIFY: exact claim on p. 12?].
```

- **Drafting tier:** [VERIFY] tags are acceptable — resolve before finalising
- **Publication tier:** All [VERIFY] tags must be resolved (read the actual source)
- Run `/bib-validate` to catch any remaining [VERIFY] tags before submission

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

### `literature_summary.md` Structure

The narrative output must include:

1. **Thematic clusters** — grouped by approach, finding, or debate (typically 4-8 clusters)
2. **Per cluster:** intellectual lineage, current debates, negative/null evidence (or explicit statement that none exists)
3. **Cross-cluster synthesis** — 1-2 paragraphs on how clusters connect, where tensions exist, and implications for the project
4. **Annotated bibliography** — each entry includes: confidence grade (A/B/C), pillar tag (Substantive/Empirical/Methodological), connection note linking to ≥1 other entry, WP criteria if applicable, and SciSciNet metrics if Phase 3b ran (disruption/novelty scores, hit flags)
5. **Confidence breakdown** — summary count of A/B/C grades across all entries
6. **Coverage gaps** — what was searched for but not found, and where negative evidence is absent
7. **SciSciNet summary** (if Phase 3b ran) — match rate, distribution of disruption/novelty scores across the corpus, notable hit-1% papers, and cross-field connections flagged during enrichment

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

Four bibliometric sources available via the bibliography MCP server and direct APIs. Includes MCP tool table, OpenAlex workflows, Scopus query syntax, and WoS API tiers.

Full reference: [`references/bibliometric-apis.md`](references/bibliometric-apis.md) | API guides: [OpenAlex](references/openalex-api-guide.md), [Scopus](references/scopus-api-guide.md), [WoS](references/wos-api-guide.md)

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
| `/bib-coverage` | Compare project `.bib` vs Paperpile label — find uncited papers and unfiled references |
| `/split-pdf` | Deep-read a paper found during search |
| `/gather-readings` | Run after literature to download PDFs for new papers |
| `/bib-coverage` | Run after literature to check uncited papers |
| `cli-council` | Multi-model search (Phase 2b) and synthesis (Phase 7) — `packages/cli-council/` |
| Paperpile MCP | Search personal Paperpile library, extract PDF text/annotations, export BibTeX. Use in Phase 1 to check what's already in the library before searching externally. GROBID tools (`parse_pdf_metadata`, `parse_pdf_references`) extract structured metadata and bibliographies from PDFs — use after downloading to auto-extract refs without manual reading |
| `shared/reference-resolution.md` | Canonical lookup + filing sequence used by Phase 1 and Phase 6c |
| arXiv MCP tools | `arxiv_search`, `arxiv_get_paper`, `arxiv_search_category` — preprint search. See [references/arxiv-api-guide.md](references/arxiv-api-guide.md) |
| Exa MCP tools | `exa_search`, `exa_search_papers`, `exa_get_contents` — semantic web search, grey literature. Requires `EXA_API_KEY` |
| Deep loop protocol | [references/deep-loop-protocol.md](references/deep-loop-protocol.md) — iterative gap analysis + targeted search |
| `shared/worker-critic-protocol.md` | Inline review of synthesis output before reporting done |
| `shared/sources-cache.md` | Cache search results to avoid redundant API calls across sessions |
