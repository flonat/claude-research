---
name: bib-coverage
description: "Use when you need to compare a project .bib against a Paperpile label to find uncited papers or unfiled entries."
allowed-tools: Read, Glob, Greps_by_label, Bash(paperpile*)
argument-hint: "[project-path or tex-file]"
---

# Bibliography Coverage

**LIBRARY-FIRST RULE: ALWAYS check Paperpile (`paperpile search-library`) when assessing coverage.**

Compare a project's `.bib` file against a Paperpile label to identify gaps between the project bibliography and the reference library.

## When to Use

- After a literature search, to see what % of the topic collection is cited
- Before submitting a paper, to catch references you forgot to cite
- When reviewing a Paperpile label, to find items not yet in any project's `.bib`
- After `/bib-validate`, as a complementary check (validate checks quality; coverage checks completeness)

## When NOT to Use

- **Finding new references** — use `/literature` for discovery
- **Validating .bib quality** (missing fields, DOI issues, preprint staleness) — use `/bib-validate`
- **Building a .bib from scratch** — use `/literature` or `/bib-parse`

## Inputs

1. **Project `.bib` file** — detected automatically (same logic as `/bib-validate`: look for `references.bib`, then any `.bib` in the project)
2. **Paperpile label** — resolved from:
   - Explicit `--topic <slug>` argument
   - Project's `CLAUDE.md` or Atlas topic frontmatter
   - Directory name if inside a research project
   - If no collection can be resolved, report an error and suggest specifying `--topic`

## Workflow

### 1. Load Project Bibliography

Parse the `.bib` file to extract all entry keys and titles.

### 2. Load Paperpile Label

1. Call `paperpile get-labels` to find the relevant topic label
2. Call `paperpile get-items-by-label` to get items in that label
3. Extract item keys (citekey) and titles

**Graceful degradation:** If the `paperpile` CLI is unavailable, skip with a warning — report .bib-only stats.

### 3. Compare

Produce three lists:

| Category | Description | Action |
|----------|-------------|--------|
| **Cited + In Label** | Items in both `.bib` and Paperpile label | No action — healthy |
| **Cited but Not in Label** | Items in `.bib` but not in the Paperpile label | Need labelling in Paperpile |
| **In Label but Not Cited** | Items in Paperpile label but not cited in any `.tex` | Potential references — review for inclusion |

### 4. Coverage Stats

```
## Coverage Report

**Paperpile label:** [label name] ([N] items)
**Project .bib:** [M] entries

| Metric | Count | % |
|--------|-------|---|
| Cited + In Label | X | X/N |
| Cited but Not Labelled | Y | — |
| In Label, Not Cited | Z | Z/N |
| Coverage (cited/label) | — | X/N% |
```

### 5. Recommendations

Based on the results:

- **Low coverage (<50%):** "The project cites few papers from the topic collection. Consider reviewing uncited items for relevance."
- **Many unfiled citations (>5):** "Several cited papers aren't in the topic collection. Run `/bib-validate` fix mode to file them."
- **High coverage (>80%):** "Good coverage of the topic collection."

## Report Format

```
## bib-coverage: [Project Name]

**Topic:** [slug] | **Collection:** [name] ([N] items) | **Bib:** [filename] ([M] entries)

### Coverage: X/N (XX%)

### Cited but Not in Collection (need filing)
| # | Key | Title | Year |
|---|-----|-------|------|

### In Collection but Not Cited (potential references)
| # | Key | Title | Year |
|---|-----|-------|------|
```

## Phase 6 (Optional): Gap Discovery via Recommendations

When coverage is low (<50%) or the user says "find what I'm missing", use the S2 Recommendations API to discover papers that should be in the collection but aren't.

1. **Select seed papers** — pick the 3-5 most-cited papers from the `.bib` file
2. **Get recommendations** — run `scholarly scholarly-similar-works <paper_id> --json` for each seed paper to get ML-based similar paper suggestions
3. **Filter against existing** — remove papers already in the `.bib` or Paperpile label
4. **Rank by relevance** — sort by citation count and recency
5. **Present candidates** — show a table of recommended additions with titles, years, citation counts

**Dispatch rule.** If ≥5 seed papers are selected, dispatch a single Explore sub-agent that runs `scholarly scholarly-similar-works` for each seed and writes merged candidates to `/tmp/bib-coverage-similar.json`. Main context reads only the merged result. For 3–4 seeds, inline calls are fine. See [`_shared/cli-dispatch-policy.md`](../_shared/cli-dispatch-policy.md).

This turns a passive coverage check into an active discovery tool — finding papers the researcher should know about based on what they already cite.

## Cross-References

- **`/bib-validate`** — Quality validation (missing fields, DOIs, preprints). Run alongside coverage for a complete check.
- **`/literature`** — Discovery of new references. Coverage identifies gaps in existing collections.
- **`/bib-parse`** — Extract citations from PDFs. Run coverage after parsing to see overlap with the topic collection.
- **`shared/reference-resolution.md`** — Topic collection resolution logic
