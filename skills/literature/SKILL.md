---
name: literature
description: "Use when you need academic literature discovery, synthesis, or bibliography management."
allowed-tools: Bash(curl*), Bash(wget*), Bash(mkdir*), Bash(ls*), Bash(uv*), Bash(cd*), Read, Write, Edit, WebSearch, WebFetch, Task, mcp__paperpile__search_library, mcp__paperpile__get_items_by_label, mcp__refpile__search_library, mcp__refpile__get_collections, mcp__refpile__add_item, mcp__refpile__add_to_collection, mcp__refpile__parse_pdf_metadata, mcp__refpile__parse_pdf_references
argument-hint: [topic-or-paper-query]
---

# Literature Skill

**CRITICAL RULE: Every citation must be verified to exist before inclusion.** Never include a paper you cannot find via web search. Hallucinated citations are worse than no citations.

**DOI INTEGRITY RULE: Every DOI must be programmatically verified before entering any `.bib` file.** Sub-agents hallucinate plausible-looking DOIs that resolve to wrong papers (e.g., correct journal prefix, wrong suffix). The ONLY reliable verification is `scholarly_verify_dois` with title-matching (see Phase 4). A DOI that resolves to a different title than expected is WRONG — treat it the same as a missing DOI.

**CITATION KEY RULE: ALWAYS use Better BibTeX-format keys (e.g., `Author2016-xx`).** When merging into an existing `.bib`, match existing keys. Never generate custom keys (`AuthorYear`, `AuthorKamenica2017`, etc.) or retain non-standard keys unless the user explicitly says otherwise.

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

**LIBRARY-FIRST RULE: ALWAYS check both Zotero (refpile MCP) and Paperpile (paperpile MCP) BEFORE any external search.** Call `mcp__refpile__search_library` and `mcp__paperpile__search_library` for the topic in Phase 1. Do not skip this even if no `.bib` file exists yet. Papers already in either library should be reused, not re-discovered.

**PREPRINT RULE: Always prefer the published version.** If a paper is found on arXiv, SSRN, NBER, or any working paper series, search for a published journal/conference version using `scholarly_search`. Only cite a preprint if no published version can be found. This applies at every phase: Phase 2 (discovery), Phase 4 (verification), and Phase 6b (bib-validate runs the full preprint staleness check from `bib-validate/references/preprint-check.md`).

> Comprehensive academic literature workflow: discover, verify, organize, synthesize.
> Uses parallel sub-agents to search multiple sources, verify citations, and fetch PDFs concurrently.

## Shared References

- Concept validation gate: `shared/concept-validation-gate.md` — validate concept before synthesis
- Escalation protocol: `shared/escalation-protocol.md` — escalate when research question is vague

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
4. **MANDATORY: Check Zotero library** (active write target) — call `mcp__refpile__search_library` for the search topic. This finds papers the user already has, preventing re-discovery of known work. Mark these as **ALREADY IN ZOTERO** and reuse their citation keys. If refpile MCP is unavailable, log a warning and continue — but always attempt the call.
5. **MANDATORY: Check Paperpile library** (read-only cross-reference) — call `mcp__paperpile__search_library` for the search topic. Also call `mcp__paperpile__get_items_by_label` if a relevant folder exists. Mark matches as **ALREADY IN PAPERPILE**. Items in Paperpile but not Zotero are flagged as `MIGRATE_TO_ZOTERO` candidates. If Paperpile MCP is unavailable, log a warning and continue — but always attempt the call.
6. **Resolve topic collection** — read `zotero-collections.md` to find the collection key for the current topic (see `shared/reference-resolution.md` for resolution logic). This key is used in Phase 6c for filing.
7. **Check source availability** — call `scholarly_source_status` (bibliography MCP) to see which sources are active (OpenAlex always; Scopus and WoS if API keys are set). Report this so search agents know what coverage to expect.

**Steps 4 and 5 are NOT optional.** Every literature search must check both reference managers before external discovery. This prevents re-discovering papers already in the library and identifies migration candidates early.

---

## Phase 2: Parallel Search (Sub-Agents)

**MCP pre-fetch (main context, before spawning agents):** Call these bibliography MCP tools from the main context before spawning agents. MCP tools are not available inside sub-agents — they are permission-scoped to the main conversation context only. Write results to `/tmp/lit-search/`.

1. **`scholarly_search`** — cross-source keyword search (OpenAlex + S2 + Scopus + WoS). Write to `/tmp/lit-search/bibliography-results.json`.
2. **`scholarly_similar_works`** — ML-based recommendations (powered by S2 Recommendations API). Pass the topic description as text to find semantically related papers beyond keyword matches. Write to `/tmp/lit-search/similar-results.json`.
3. **`scholarly_author_papers`** — if key authors are known, fetch their publication lists. Write to `/tmp/lit-search/author-results.json`.

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

**Step 3 — Manual verification for remaining papers:** Spawn **multiple general-purpose agents in parallel**, each verifying ~5 papers. Read the full verification template from [references/agent-templates.md](references/agent-templates.md#phase-4-verification-agent-template). **Include the Crossref instruction** in the agent prompt — agents must use Crossref API (`curl`) for DOI lookup, not reconstruct DOIs from memory. **Do NOT instruct sub-agents to call MCP tools** (`scholarly_search`, `scholarly_verify_dois`) — MCP tools are not available in sub-agents. Sub-agents should use Crossref API and WebSearch/WebFetch only.

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
- **Reuse existing Zotero citation keys** — for entries marked **ALREADY IN ZOTERO** in Phase 1, use the Zotero `citationKey` directly. Do not generate a new key.
- Only VERIFIED papers — no METADATA MISMATCH entries
- **List ALL authors explicitly** — never "et al." in BibTeX
- Include abstracts when available
- **S2 BibTeX seed:** Call `scholarly_paper_detail` for each verified paper to get pre-formatted BibTeX via the `citationStyles` field. Use as a starting template, then enrich with missing fields (abstract, pages, volume) and correct the citation key to BBT format. This reduces manual entry errors.

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

After assembling and validating the `.bib`, sync new references to Zotero (active write target) and cross-reference with Paperpile (read-only). Handles migration candidates and post-run maintenance.

Full steps: [`references/reference-manager-sync.md`](references/reference-manager-sync.md)

---

## Phase 7: Synthesize Narrative (Direct or CLI Council)

1. **Identify themes** — group papers by approach, finding, or debate
2. **Map intellectual lineage** — how did thinking evolve?
3. **Note current debates** — where do researchers disagree?
4. **Find gaps** — what's missing?

Output types: narrative summary (LaTeX), literature deck, annotated bibliography, concise field synthesis.

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
| `/bib-coverage` | Compare project `.bib` vs Zotero topic collection — find uncited papers and unfiled references |
| `/split-pdf` | Deep-read a paper found during search |
| `cli-council` | Multi-model search (Phase 2b) and synthesis (Phase 7) — `packages/cli-council/` |
| `refpile` MCP | Search personal Zotero library, extract PDF text/annotations, export BibTeX. Use in Phase 1 to check what's already in the library before searching externally. GROBID tools (`parse_pdf_metadata`, `parse_pdf_references`) extract structured metadata and bibliographies from PDFs — use after downloading to auto-extract refs without manual reading |
| `shared/reference-resolution.md` | Canonical lookup + filing sequence used by Phase 1 and Phase 6c |
