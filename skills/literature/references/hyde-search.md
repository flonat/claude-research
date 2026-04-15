# HyDE: Hypothetical Document Embeddings for Literature Search

> Pre-retrieval query expansion technique adapted from SciSciGPT (Nature Computational Science 2025, arXiv:2504.05559).
> Source: `resources/academics/northwestern-cssi/SciSciGPT/backend/tools/literature.py`

## What Is HyDE?

Standard keyword search misses papers that use different terminology for the same concepts. HyDE fixes this by:

1. Asking the LLM to **generate hypothetical paper abstracts** that would answer the research question
2. Using these hypothetical texts as **additional search queries** alongside the original query
3. The hypothetical abstracts capture synonyms, related concepts, and discipline-specific vocabulary that keyword search misses

## When to Use

- **Broad topic searches** where terminology varies across subfields (e.g., "human-AI collaboration" vs "human-machine teaming" vs "AI-augmented decision making")
- **Interdisciplinary queries** where the same concept has different names in different fields
- **Deep mode** (`--deep`) — always use HyDE for comprehensive literature reviews
- **Pipeline mode** — use HyDE when the topic spans multiple fields (check `connected_topics` in the atlas file)

## When to Skip

- **Narrow/targeted searches** for a specific paper or author
- **Known-item searches** (looking for a paper by title or DOI)
- **Time-constrained searches** where the extra LLM call isn't worth the latency

## Protocol

### Step 1: Generate Hypothetical Papers (Main Context)

Before the Phase 2 MCP pre-fetch, generate 3-5 hypothetical paper descriptions:

```
Given this research question:
[QUERY]

Generate 3-5 hypothetical paper abstracts (each 2-3 sentences) that would 
directly address this question. Each abstract should:
- Use different terminology and framing than the others
- Come from a different disciplinary perspective (e.g., economics, psychology, computer science, management)
- Include realistic but fictional author names and journal names
- Focus on methodology and findings, not just the question

Format each as:
<hypothetical>
[Abstract text — 2-3 sentences capturing the core finding and method]
</hypothetical>
```

### Step 2: Extract Search Queries

From each `<hypothetical>` block, extract:
- 2-3 key phrases that differ from the original query
- Any discipline-specific terms not in the original

### Step 3: Augment MCP Pre-Fetch

Add the hypothetical-derived queries to the existing Phase 2 MCP calls:

1. Call `scholarly_search` with the **original query** (as before)
2. Call `scholarly_search` with each **hypothetical-derived query** (2-3 additional calls)
3. Call `scholarly_similar_works` with the best hypothetical abstract as `text` input
4. Merge all results before deduplication

### Step 4: Pass to Sub-Agents

Include the hypothetical abstracts in the sub-agent prompts as "concept expansions" — the agents use them as additional search variations for WebSearch.

## Example

**Query:** "How do teams make decisions when AI recommends one option but human intuition suggests another?"

**Hypothetical 1 (Management):**
> "We study algorithm aversion in team settings using a randomized experiment with 400 managers. Teams that received AI recommendations but discussed them collectively were 34% more likely to override the AI than individual decision-makers, suggesting that group deliberation amplifies skepticism toward algorithmic advice."

**Hypothetical 2 (HCI):**
> "Through a mixed-methods study of 12 surgical teams using AI diagnostic support, we find that disagreement between AI output and clinical intuition triggers a 'verification cascade' where team members sequentially evaluate the discrepancy, increasing decision time by 2.3x but improving accuracy by 18%."

**Hypothetical 3 (Economics):**
> "Using a lab experiment with 600 participants in sequential decision tasks, we estimate the causal effect of AI-human disagreement on group welfare. We find that teams with heterogeneous AI trust levels achieve Pareto-superior outcomes compared to homogeneous teams."

**Derived search queries:**
- "algorithm aversion team decision making"
- "AI disagreement verification cascade"
- "human-AI conflict group deliberation override"
- "heterogeneous AI trust team welfare"

These queries capture terminology (algorithm aversion, verification cascade, Pareto-superior) that the original question didn't use, dramatically improving recall.

## Provenance

Adapted from `pre_retrieval_processing()` in SciSciGPT's `backend/tools/literature.py`. The original uses HyDE with Pinecone vector search; our adaptation uses the hypothetical texts as query expansions for API-based search (scholarly MCP, WebSearch). The principle is identical — bridge the vocabulary gap between research questions and paper abstracts.
