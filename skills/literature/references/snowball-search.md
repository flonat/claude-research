# Literature — Phase 2.5: Snowball Search (Optional)

> Main context. Uses S2's citation graph to expand candidate pool via snowballing after Phase 2.

## Protocol

1. **Identify seed papers** — pick the 3-5 most relevant papers from Phase 2 results (highest citation count + relevance)
2. **Forward snowball** — call `scholarly scholarly-citations` for each seed to find papers that cite it. Useful for finding recent work building on foundational papers.
3. **Backward snowball** — call `scholarly scholarly-references` for each seed to find papers it cites. Useful for finding seminal/foundational works.
4. **Filter** — deduplicate against Phase 2 results, keep only papers with ≥5 citations (avoid noise)
5. **Add to candidate pool** — merge into the main list before Phase 3 ranking

## When to Use

Literature reviews, broad topic surveys, or when Phase 2 returned <15 unique papers. Skip for narrow/targeted searches where the initial results are sufficient.

## Paper Detail Enrichment

For top candidates, call `scholarly scholarly-paper-detail` to get TLDR summaries (one-line auto-generated descriptions) — useful for rapid screening without reading abstracts.
