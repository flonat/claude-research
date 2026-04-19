# Deep Loop Protocol

> Iterative deepening for `/literature` Phase 4.5. Activated by `--deep` flag or keywords: "deep", "thorough", "comprehensive review".

## Entry Conditions

The deep loop runs **after** Phase 4 (verification) and **before** Phase 5 (PDF download). It only activates when:

1. User explicitly requests deep search (flag or keyword)
2. At least 5 verified papers exist from the initial search (enough to identify gaps)
3. Context budget allows (not near compression)

## Loop Structure (max 3 iterations)

```
For each iteration:

  1. GAP ANALYSIS (main context, ~200 tokens output)
     - Read current verified paper list
     - Identify gaps:
       • Missing time periods (e.g., nothing before 2018)
       • Missing methodologies (e.g., no experimental studies)
       • Missing geographic/institutional contexts
       • Missing theoretical perspectives
       • Underrepresented authors or schools of thought
       • Key papers cited by found papers but not in the set
     - Produce 2-4 specific gap statements

  2. QUERY REFINEMENT (main context)
     - Convert each gap into 1-2 targeted search queries
     - Include negative terms to avoid re-finding existing papers
     - Choose appropriate source per query:
       • `scholarly scholarly-search` — general academic
       • `scholarly arxiv-search` — preprints, CS/econ working papers
       • `scholarly exa-search-papers` — grey literature, working papers, reports
       • `scholarly dblp-search` — CS conferences/venues
       • `scholarly core-search-fulltext` — OA full-text search

  3. TARGETED SEARCH (sub-agents, parallel)
     - Sub-agents shell out to `scholarly` CLI directly (works inside sub-agents), OR orchestrator pre-fetches and writes results to /tmp/
     - Sub-agents filter for relevance
     - Each sub-agent targets 1-2 gaps

  4. MERGE + DEDUP (main context)
     - Merge new results with existing verified pool
     - Deduplicate by DOI and title similarity (normalize_doi + fuzzy match)
     - Count genuinely new papers

  5. VERIFY NEW PAPERS (main context)
     - Same Phase 4 protocol but only for new papers
     - Batch DOI verification via `scholarly scholarly-verify-dois --dois D1,D2 --json`
```

## Convergence Criteria (any triggers exit)

| Trigger | Action |
|---------|--------|
| 3 iterations completed | Exit with full results |
| <3 genuinely new papers in an iteration | Exit — diminishing returns |
| User says "enough" or "stop" | Exit immediately |
| Context budget warning | Exit gracefully, note remaining gaps |

## Source Selection per Gap Type

| Gap type | Primary source | Secondary |
|----------|---------------|-----------|
| Missing time period | `scholarly scholarly-search` with year filter | `scholarly arxiv-search` |
| Missing methodology | `scholarly exa-search-papers` (semantic) | `scholarly scholarly-search` |
| Missing geography/context | `scholarly scholarly-search` with context terms | `scholarly exa-search` |
| Missing theoretical lens | `scholarly exa-search-papers` (semantic) | `scholarly scholarly-search` |
| Key cited papers not in set | `scholarly scholarly-paper-detail` (by DOI) | `scholarly crossref-lookup-doi` |
| Preprints / working papers | `scholarly arxiv-search` | `scholarly exa-search-papers` |
| Grey literature / reports | `scholarly exa-search` (no category filter) | `scholarly core-search-fulltext` |

## Gap Analysis Prompt Template

```
Given these {N} verified papers on "{topic}":
{paper_list}

Identify 2-4 specific gaps in this literature set:
1. Time coverage: Are any decades/periods underrepresented?
2. Methods: What methodological approaches are missing?
3. Theory: What theoretical frameworks are absent?
4. Context: What geographic/institutional contexts are missing?
5. Key works: What seminal papers are cited by these works but not in the set?

For each gap, state:
- What is missing (specific, not vague)
- Why it matters for a comprehensive review
- A search query that would find papers filling this gap
```

## Token Budget

| Component | Estimated tokens |
|-----------|-----------------|
| Gap analysis per iteration | ~200 output |
| Query refinement per iteration | ~100 output |
| New search results per iteration | ~500-1000 (depends on result count) |
| Verification per iteration | ~200 |
| **Total per iteration** | ~1000-1500 |
| **Max total (3 iterations)** | ~3000-4500 |

## Reporting

After the deep loop completes, append to the synthesis section:

```markdown
## Deep Search Summary

| Metric | Value |
|--------|-------|
| Iterations | {N} |
| Gaps identified | {count} |
| Gaps filled | {count} |
| New papers found | {count} |
| Exit reason | {convergence / max iterations / user stop} |

### Remaining Gaps
{List any gaps that could not be filled, with suggested manual search strategies}
```
