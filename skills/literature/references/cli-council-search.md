# CLI Council Search & arXiv Full-Text Reading

> Phase 2b multi-model literature search and arXiv source reading.
> Referenced from `SKILL.md` — the parent file has a summary + pointer.

## Phase 2b: CLI Council Search (Optional)

**When to use:** Broad literature reviews (20+ papers), interdisciplinary topics, or when maximum recall matters. Each model has different training data and recall — running the same search query through Gemini, Codex, and Claude surfaces papers that any single model would miss. Gemini additionally has live web search.

**How it works:** Run `cli-council` from the `packages/cli-council/` package. The council sends the same search prompt to all three CLI backends in parallel, collects their independent paper lists, then synthesises a merged list.

**Invocation:**

```bash
cd "packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/lit-council-prompt.txt \
    --output /tmp/lit-council-result.json \
    --output-md /tmp/lit-council-report.md \
    --timeout 180
```

**Prompt template** (write to `/tmp/lit-council-prompt.txt`):

```
Search for academic papers on: [TOPIC]

Focus: [JOURNALS/FIELDS if specified]
Time period: [YEARS if specified]

For each paper, provide:
- Full title
- ALL authors (never "et al.")
- Year
- Journal/venue
- DOI if known

Prioritize:
- Highly-cited foundational papers
- Recent work (past 3-5 years)
- Peer-reviewed over preprints

Target: [N] papers. Cast a wide net — duplicates will be removed.

Skip these already-known papers: [LIST OF EXISTING CITATION KEYS]
```

**After the council returns:**
1. Parse the synthesis and individual assessments from the JSON output
2. Extract paper lists from each backend's response (Gemini often finds more recent papers via web search; Codex and Claude recall different foundational works)
3. Feed ALL discovered papers into Phase 3 alongside the Phase 2 results for deduplication

**When to skip:** Small requests (< 10 papers), narrow/well-defined topics, or when Phase 2 already returns sufficient coverage. The standard Phase 2 agents (Scholar + biblio MCP) remain the primary search mechanism; Phase 2b supplements with model-diversity recall.

---

## Reading Full Paper Text from arXiv

When you need to read the full text of a paper (not just the abstract) — to verify claims, understand methodology, or extract exact phrasing — download the arXiv LaTeX source:

```bash
# Download source tarball
curl -L -o /tmp/ARXIV_ID.tar.gz "https://arxiv.org/src/ARXIV_ID"

# Extract
mkdir -p /tmp/ARXIV_ID && cd /tmp/ARXIV_ID && tar -xzf /tmp/ARXIV_ID.tar.gz

# Find and read the main .tex file
ls *.tex
```

This gives you:
- Full paper text with equations, methodology details, and exact author phrasing
- The paper's `.bib` or `.bbl` file for cross-referencing their citations
- Supplementary materials and appendices

**When to use:** Deep verification of a specific paper's claims, extracting precise definitions or theorems, understanding methodology details that abstracts omit, or finding papers cited by the target paper.

**Limitation:** Only works for arXiv papers with source available. For journal-only papers, use `/split-pdf` instead.
