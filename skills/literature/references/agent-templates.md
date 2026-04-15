# Literature Skill: Agent Templates

> Sub-agent prompt templates used in Phases 2, 4, and 5 of the `/literature` skill. Read this when dispatching agents.

---

## Phase 2: Search Agent Templates

### Agent 1: Google Scholar Search

```
subagent_type: Explore
prompt: |
  Search Google Scholar for academic papers on: [TOPIC]

  Focus on: [JOURNALS/FIELDS if specified]
  Time period: [YEARS if specified]

  Search strategy:
  1. Start with broad terms capturing the core concept
  2. Narrow progressively — add specificity based on results
  3. Try 3-5 different query variations

  Prioritize:
  - Recent work (past 3 years) first
  - Highly-cited foundational papers regardless of age
  - Peer-reviewed over preprints

  Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]

  Return a structured list with for each paper:
  - Title, authors, year, journal/venue
  - DOI or URL if found
  - Brief note on relevance (1 sentence)

  Target: [N] papers. Cast a wide net — duplicates will be removed later.
```

### Agent 2: Semantic Scholar / arXiv Search

```
subagent_type: Explore
prompt: |
  Search Semantic Scholar and arXiv for academic papers on: [TOPIC]

  [Same structure as Agent 1, but targeting these specific sources]
  Use WebSearch with site:semanticscholar.org and site:arxiv.org queries.

  Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]

  Return the same structured list format as above.
  Target: [N] papers.
```

### Agent 2 (recommended): Cross-Source Search via Pre-Fetched Biblio Data

**This is the primary structured search agent.** The orchestrator (main context) calls `scholarly_search` via the bibliography MCP before spawning this agent, and writes results to a temp file.

**MCP tools are NOT available in sub-agents.** The orchestrator must pre-fetch search results.

**Orchestrator pre-fetch step (run in main context before spawning Agent 2):**
1. Call `scholarly_search` with query, year_from, year_to, sort_by, limit: 50
2. If sub-themes exist, run additional `scholarly_search` calls
3. Optionally call `scholarly_similar_works` for related papers
4. Write all results to `/tmp/lit-search/bibliography-results.json`

```
subagent_type: Explore
prompt: |
  Read pre-fetched bibliography search results from:
    /tmp/lit-search/bibliography-results.json

  This file contains structured results from OpenAlex, Scopus, and WoS
  for papers on: [TOPIC]

  Your tasks:
  1. Parse the results and extract: title, authors, year, journal, DOI, citation count
  2. Supplement with WebSearch for papers that may be missing from bibliometric databases
     (very recent papers, working papers, interdisciplinary work)
  3. Search Semantic Scholar (site:semanticscholar.org) for additional coverage

  Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]

  Return for each paper: title, authors, year, journal, DOI, citation count, sources found in.
  Target: [N] papers. Cast a wide net — duplicates will be removed later.
```

### Agent 3 (optional): Semantic Scholar / arXiv or Domain-Specific

Use when the topic has strong CS/ML overlap (Semantic Scholar) or needs working paper coverage (SSRN, NBER):

```
subagent_type: Explore
prompt: |
  Search Semantic Scholar and arXiv for academic papers on: [TOPIC]

  [Same structure as Agent 1, but targeting these specific sources]
  Use WebSearch with site:semanticscholar.org and site:arxiv.org queries.

  Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]

  Return the same structured list format as above.
  Target: [N] papers.
```

---

## Phase 4: Verification

### Step 1: Batch DOI Pre-Verification via MCP (Direct — No Sub-Agent)

Before spawning verification agents, collect all DOIs from Phase 3 candidates and call the bibliography MCP tool directly:

```
Call `scholarly_verify_dois` with:
  dois: ["10.1016/j.ejor.2024.01.001", "10.1287/mnsc.2022.4321", ...]

Results: each DOI gets a status AND a resolved title:
  - VERIFIED (2+ sources confirm) → CHECK TITLE MATCH before accepting
  - SINGLE_SOURCE (1 source only) → still needs manual check
  - NOT_FOUND → needs full manual verification or may be fabricated
```

**CRITICAL — Title-matching gate:** For every VERIFIED DOI, compare the returned title against the expected title. If they don't match, the DOI is WRONG even though it resolves. This is the most common error pattern — lookup tools return DOIs that are structurally valid (correct journal prefix, plausible suffix) but point to a different paper in the same journal. Example: `10.1111/j.1468-0297.2010.02387.x` vs `02366.x` — both resolve, but to different papers.

Papers with title mismatches go to Step 2. Papers without DOIs always go to manual verification.

### Step 2: Manual Verification for Remaining Papers

Spawn multiple agents in parallel, each verifying a batch of ~5 papers:

```
subagent_type: general-purpose
prompt: |
  Verify that each of the following academic papers exists and has correct metadata.
  This is for a bibliography — accuracy is critical. Do NOT guess or fabricate details.

  Papers to verify:
  1. [Title] by [Authors] ([Year]) — [Journal/venue if known]
  2. [Title] by [Authors] ([Year]) — [Journal/venue if known]
  3. ...
  4. ...
  5. ...

  For EACH paper:
  1. Search the web to confirm the paper exists
  2. Verify: authors (ALL authors — full list, exact names and order), title, year, journal, volume, pages
  3. **Find the correct DOI using these methods IN ORDER of reliability:**
     a. **Crossref API (most reliable — ALWAYS try this first):** Run:
        `curl -sL "https://api.crossref.org/works?query.bibliographic=TITLE+AUTHOR&rows=3"`
        Parse the JSON response — the first result's `DOI` field is the correct DOI.
        This uses publisher metadata and is far more reliable than web search or MCP tools.
        **Do NOT use MCP `scholarly_search` for specific known papers** — it returns
        noisy, irrelevant results. Crossref is the gold standard for targeted lookups.
     b. **Publisher page:** Visit the journal's website and search for the paper.
     c. **Web search (last resort):** Search for the paper + "DOI". But DOIs from
        web search MUST still be verified in step 4.
  4. **Resolve the DOI** by visiting https://doi.org/[DOI] — confirm the landing
     page shows the SAME title and authors. If the DOI resolves to a different
     paper, the metadata is WRONG. Go back to step 3.
     **NEVER reconstruct DOIs from memory or by guessing suffixes** — this is the
     most common hallucination pattern (correct journal prefix, wrong suffix).
  5. Find the abstract
  6. Note the URL where you found/confirmed it (publisher page preferred)
  7. **Preprint check:** If the paper was found on arXiv, SSRN, NBER, or any
     working paper series, search for a published journal or conference version.
     Check Google Scholar, the DOI, and the author's publication page.
     Use Crossref API or WebSearch — do NOT call MCP tools (scholarly_search,
     scholarly_verify_dois, etc.) as MCP tools are not available in sub-agents.
     - If a published version exists: use that version's metadata instead
       (journal, year, volume, pages, DOI)
     - If no published version exists: keep the preprint, but note it as
       a working paper in the venue field

  **Author accuracy rules:**
  - List ALL authors — never use "and others" or "et al." in the metadata.
    Every author must be named.
  - Beware of author conflation: researchers in the same subfield may share
    surnames or topics. Confirm authors from the publisher page, not from
    secondary aggregators.
  - If you find the paper attributed to different authors on different sources,
    trust the publisher/DOI landing page over Google Scholar snippets.
  - **Verify author order and initials** against the publisher page. Common
    errors: swapped first/last names, wrong middle initials, missing co-authors,
    or extra authors from a different paper with a similar title.

  **DOI verification is mandatory.** If the DOI does not resolve to the claimed
  paper, the entry FAILS verification — do not mark it as VERIFIED.
  Use Crossref API for DOI lookup — never guess or reconstruct DOIs.

  Return for each paper one of:
  - VERIFIED: [full corrected metadata including DOI and abstract]
    — include the URL of the publisher page where you confirmed the metadata
    — if upgraded from preprint, add: "UPGRADED from [preprint source]"
  - NOT FOUND: [title] — could not confirm existence, do not include
  - METADATA MISMATCH: [title] — paper exists but DOI/authors don't match
    search results. Include what you found and flag the discrepancy.

  Be strict. If you cannot find a paper or its details don't match, mark it NOT FOUND
  or METADATA MISMATCH. Never guess metadata.
```

---

## Phase 5: PDF Download Agent Template

```
subagent_type: Bash
prompt: |
  Download PDFs for these academic papers. Save each to [PROJECT]/docs/readings/
  with filename matching the citation key.

  Papers:
  1. Key: Smith2024 — DOI: 10.1000/example — URL: https://...
  2. Key: Jones2023 — DOI: 10.1000/example2 — URL: https://...
  3. ...

  For each paper, try in order:
  1. Direct PDF link if known
  2. DOI redirect (https://doi.org/[DOI])
  3. Search for open access version on author website, SSRN, arXiv, NBER

  Use curl or wget. Create the output directory if needed.
  Report which downloads succeeded and which failed.
```

---

## Phase 4.5: Deep Loop Agent Templates

### Gap Analysis (runs in main context, not a sub-agent)

The orchestrator runs gap analysis directly — it needs access to the verified paper list and MCP tools.

```
Given these {N} verified papers on "{topic}":
{paper_list — title, authors, year, journal for each}

Identify 2-4 specific gaps in this literature set. Check each dimension:

1. **Time coverage:** Are any decades or periods underrepresented?
   (e.g., "No papers before 2018 despite the field existing since 2005")
2. **Methods:** What methodological approaches are missing?
   (e.g., "All papers use surveys — no experimental or computational studies")
3. **Theory:** What theoretical frameworks are absent?
   (e.g., "No behavioural economics perspective despite relevance")
4. **Context:** What geographic, institutional, or domain contexts are missing?
   (e.g., "All studies are US-based — no European or Asian contexts")
5. **Key works:** Check references of found papers — are seminal works missing?
   (e.g., "Smith (2015) is cited by 8 papers in the set but not included")

For each gap, provide:
- **Gap:** What is missing (be specific)
- **Why it matters:** Why this gap weakens the review
- **Search query:** A targeted query to find papers filling this gap
- **Best source:** Which MCP tool to use (scholarly_search, arxiv_search,
  exa_search_papers, dblp_search, core_search_fulltext)
```

### Refined Search Agent (targets specific gaps)

Spawned as sub-agents with pre-fetched results from MCP.

```
subagent_type: Explore
prompt: |
  I'm conducting an iterative literature review on: [TOPIC]

  The initial search found {N} papers but has this gap:
  **Gap:** [SPECIFIC GAP STATEMENT]

  Pre-fetched search results for this gap are in:
    /tmp/lit-deep-loop/gap-{N}-results.json

  Your tasks:
  1. Read the pre-fetched results
  2. Supplement with WebSearch for papers the bibliometric databases may miss:
     - Working papers, policy reports, grey literature
     - Very recent publications (last 6 months)
     - Interdisciplinary work that crosses database boundaries
  3. For each paper found, provide: title, authors, year, journal/venue, DOI if known

  Skip these already-found papers: [LIST OF EXISTING TITLES/DOIS]

  Return a structured list. Target: 5-10 papers specifically addressing the gap.
  Quality over quantity — only include papers directly relevant to the gap.
```

### arXiv-Specific Gap Search (for preprint-heavy gaps)

Used when the gap analysis identifies missing preprints or working papers.

```
subagent_type: Explore
prompt: |
  Search for arXiv preprints addressing this gap in a literature review on: [TOPIC]

  **Gap:** [SPECIFIC GAP STATEMENT]

  Pre-fetched arXiv results are in:
    /tmp/lit-deep-loop/arxiv-gap-{N}-results.json

  Also search the web for:
  - SSRN working papers (site:ssrn.com)
  - NBER working papers (site:nber.org)
  - Author working paper pages at universities

  Skip these already-found papers: [LIST OF EXISTING TITLES/DOIS]

  Return: title, authors, year, venue (arXiv category or working paper series), URL.
  Target: 5-10 papers.
```

---

## Prompt Templates (User-Facing)

### Find specific references
```
Find 5 recent papers on [TOPIC] from [JOURNALS].
Verify each citation exists and provide BibTeX entries.
```

### Build comprehensive literature
```
Help me synthesize the literature on [TOPIC].

I need:
1. Top 25 seminal papers (high citations, foundational)
2. Key themes/debates in this literature
3. Narrative "story" of how this field developed
4. Gaps or opportunities for new research
5. A .bib file with all references

Focus on: [JOURNALS/FIELDS]
Time period: [YEARS]
```

### Synthesis prompts
```
Organize these papers into themes and write a 2-paragraph summary of each theme.
```

```
Based on this literature, what research questions remain unanswered?
```

---

## Phase 2b: CLI Council Search Template

**When to use:** Broad reviews (20+ papers), interdisciplinary topics, or when Phase 2 coverage seems thin. Each model (Gemini, Codex, Claude) has different training data and recall — and Gemini has live web search.

**Step 1:** Write the search prompt to a temp file:

```bash
cat > /tmp/lit-council-prompt.txt << 'PROMPT'
Search for academic papers on: [TOPIC]

Focus: [JOURNALS/FIELDS if specified]
Time period: [YEARS if specified]

For each paper, provide:
- Full title
- ALL authors (full names, never "et al.")
- Year of publication
- Journal or venue name
- DOI if known
- One sentence on relevance

Prioritize:
- Highly-cited foundational papers regardless of age
- Recent work (past 3-5 years)
- Peer-reviewed over preprints
- Papers from top journals in the field

Target: [N] papers. Cast a wide net — duplicates will be removed later.

Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]
PROMPT
```

**Step 2:** Run the council:

```bash
cd "$TM/packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/lit-council-prompt.txt \
    --output /tmp/lit-council-result.json \
    --output-md /tmp/lit-council-report.md \
    --timeout 180
```

**Step 3:** Parse results. Read `/tmp/lit-council-report.md` and extract paper lists from:
- The synthesis (chairman's merged list)
- Each individual assessment (Assessment A/B/C) — these often contain papers the others missed

Feed all discovered papers into Phase 3 (deduplication) alongside Phase 2 results.

**Expected value:** Gemini finds more recent papers via web search. Codex and Claude recall different foundational works from training. Typical yield: 10-20% more unique papers vs. Phase 2 alone.

---

## Phase 7: CLI Council Synthesis Template (Optional)

For comprehensive reviews, run the narrative synthesis through cli-council to get three independent thematic interpretations.

**Step 1:** Write the paper list to a context file:

```bash
# Collect all verified paper metadata (titles, abstracts, years, journals)
# into a single file for context
cat > /tmp/lit-papers.txt << 'EOF'
[Paste the verified paper list with titles, authors, years, journals, and abstracts]
EOF
```

**Step 2:** Write the synthesis prompt:

```bash
cat > /tmp/lit-synthesis-prompt.txt << 'PROMPT'
Synthesise the following academic literature into a structured narrative review.

1. Identify major themes — group papers by approach, finding, or intellectual tradition
2. Map the intellectual lineage — how did thinking in this area evolve?
3. Note current debates — where do researchers disagree?
4. Identify gaps — what questions remain unanswered?

Structure your synthesis as numbered themes, each with:
- Theme title
- 2-3 paragraph narrative
- Key papers in that theme (cite by author and year)

End with a "Gaps and Opportunities" section identifying 3-5 directions for future research.
PROMPT
```

**Step 3:** Run the council:

```bash
cd "$TM/packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/lit-synthesis-prompt.txt \
    --context-file /tmp/lit-papers.txt \
    --output-md /tmp/lit-synthesis-report.md \
    --chairman claude \
    --timeout 180
```

**Expected value:** Different models identify different thematic groupings and gaps. The chairman synthesis produces a richer narrative than any single model.

---

## Scaling Guide

| Request size | Search agents | CLI Council (Phase 2b) | DOI pre-verify (MCP) | Verification waves | PDF waves |
|---|---|---|---|---|---|
| 5 papers | 1 (MCP cross-source) | Skip | 1 call | 1 wave (1 agent) | 1 wave |
| 10-15 papers | 2 (Scholar + MCP) | Skip | 1 call | 1 wave (2-3 agents) | 1 wave |
| 20-25 papers | 2-3 | Recommended | 1 call | 1-2 waves | 2 waves |
| 30+ papers | 3 | Recommended | 1 call (50 DOI limit) | 2+ waves | 3+ waves |

For small requests (< 5 papers), skip sub-agents entirely — call `scholarly_search` and `scholarly_verify_dois` directly, then do verification inline.

**Between waves:** write collected results to the `.bib` file or a scratch markdown file on disk, then proceed to the next wave. This prevents context overflow.

---

## Example Use

"Create a literature review on interactive approaches to multi-criteria decision making, focusing on papers from top journals in the field from 2015-2025. I need about 25 key papers with a .bib file and a narrative summary."

This would trigger:
1. Pre-search check for existing .bib
2. 3 parallel search agents (Scholar, Semantic Scholar, domain journals)
3. Deduplicate ~40 candidates down to ~30
4. 2 waves of 3 verification agents (5 papers each), results written to disk between waves
5. 2 waves of 3 PDF download agents
6. Assemble verified .bib (~25 papers)
7. Write thematic narrative summary
