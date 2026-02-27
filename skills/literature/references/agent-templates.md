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

### Agent 2 (recommended): Cross-Source Search via Biblio MCP

**This is the primary structured search agent.** It queries all enabled sources (OpenAlex + Scopus + WoS) in a single call with automatic DOI-based deduplication.

```
subagent_type: Explore
prompt: |
  Search for academic papers on: [TOPIC]

  Use the biblio MCP tools (these are available as MCP tools, call them directly):

  1. Call `scholarly_search` with:
     - query: "[TOPIC]"
     - year_from: [YEAR] (if specified)
     - year_to: [YEAR] (if specified)
     - sort_by: "cited_by_count" for foundational papers, "relevance" for topical search
     - limit: 50

  2. If the topic has sub-themes, run `scholarly_search` again with narrower queries
     to capture papers the broad search might miss.

  3. For finding papers related to a specific known paper, use `scholarly_similar_works`
     with the paper's title or abstract as the text argument.

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

Before spawning verification agents, collect all DOIs from Phase 3 candidates and call the biblio MCP tool directly:

```
Call `scholarly_verify_dois` with:
  dois: ["10.1016/j.ejor.2024.01.001", "10.1287/mnsc.2022.4321", ...]

Results: each DOI gets a status:
  - VERIFIED (2+ sources confirm) → skip manual verification
  - SINGLE_SOURCE (1 source only) → still needs manual check
  - NOT_FOUND → needs full manual verification or may be hallucinated
```

Papers without DOIs always go to manual verification.

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
  3. Find the DOI and **resolve it** by visiting https://doi.org/[DOI] — confirm the
     landing page shows the SAME title and authors. If the DOI resolves to a
     different paper, the metadata is wrong. Search for the correct DOI.
  4. Find the abstract
  5. Note the URL where you found/confirmed it (publisher page preferred)
  6. **Preprint check:** If the paper was found on arXiv, SSRN, NBER, or any
     working paper series, search for a published journal or conference version.
     Check Google Scholar, the DOI, and the author's publication page.
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

  **DOI verification is mandatory.** If the DOI does not resolve to the claimed
  paper, the entry FAILS verification — do not mark it as VERIFIED.

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
cd "packages/cli-council"
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
cd "packages/cli-council"
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
