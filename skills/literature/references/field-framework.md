# Literature — Phase 3: Field-Framework Extraction

> Transforms raw search results into a structured database for systematic comparison, gap detection, and synthesis.

For each paper entering the candidate pool, extract these structured fields from the abstract and metadata.

## Fields

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

## When to Extract

**Always.** Even partial extraction (3-4 fields from abstract alone) is valuable for ranking and gap analysis. Full extraction happens after Phase 4 verification for the final verified set.

## How This Helps Downstream

- **Phase 3 ranking:** Papers with methods/settings similar to the user's project rank higher
- **Phase 4.5 gap analysis:** Systematic gaps become visible (e.g., "no experimental evidence", "all US samples")
- **Phase 7 synthesis:** Enables structured comparison tables and evidence maps
- **Hypothesis generation:** Feeds directly into `/hypothesis-generation` Phase 2

## Breadcrumb

Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:

```
### [/literature] Phase 3 complete [YYYY-MM-DD HH:MM]
- **Done:** [N papers found, deduplicated from N sources, top N selected for verification]
- **Outputs:** [candidate list at /tmp/lit-search/]
- **Next:** SciSciNet enrichment → Parallel verification (DOI + metadata)
```
