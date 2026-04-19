# Literature — Phase 3b: SciSciNet Enrichment (Optional)

> Additive enrichment. Skip silently if SciSciNet API is not reachable (`curl -sf http://localhost:8500/health` fails). The pipeline works without it.

## Step 1 — Collect DOIs

Gather all DOIs from the Phase 3 candidate list.

## Step 2 — Call paper-enrich

Send DOIs in a single batch (max 100 per request):

```bash
curl -s -X POST http://localhost:8500/api/paper-enrich \
  -H "Content-Type: application/json" \
  -d '["10.1234/...", "10.5678/..."]'
```

## Step 3 — Merge Scores into Candidate Metadata

For each matched paper, add:

| Field | Source | Use in pipeline |
|-------|--------|-----------------|
| `disruption_score` | SciSciNet | Ranking boost (highly disruptive papers → higher priority) |
| `novelty_score` | SciSciNet | Flag novel methodological contributions |
| `conventionality_score` | SciSciNet | Identify consolidating/survey papers (useful for background sections) |
| `fields` | SciSciNet | Cross-reference with user's field — flag interdisciplinary connections |
| `is_hit_1pct` / `is_hit_5pct` | SciSciNet | Flag top-cited papers within their field-year cohort |

## Step 4 — Re-rank with Enrichment

Adjust Phase 3 rankings:

- Papers with `is_hit_1pct = true` → boost ranking (field-defining work)
- Papers with high `disruption_score` (> 0.1) → boost if the review seeks paradigm shifts
- Papers with high `conventionality_score` → prioritize for "background" and "established literature" sections
- Papers in adjacent `fields` not in the user's core area → flag as cross-pollination candidates

## Coverage Note

Not all papers will match (SciSciNet covers 11M papers, biased toward STEM/social science). Papers without matches retain their Phase 3 ranking unchanged. Log the match rate (e.g., "SciSciNet matched 18/25 candidates").

## Breadcrumb

Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:

```
### [/literature] Phase 3b complete [YYYY-MM-DD HH:MM]
- **SciSciNet:** [M/N papers matched, avg disruption X.XXX, N hit-1% papers]
- **Next:** Parallel verification (DOI + metadata)
```
