# Literature — Phase 4: Parallel Verification

> Hard DOI gate. Every DOI entering a `.bib` must pass title-matching verification via `scholarly scholarly-verify-dois`.

## Step 1 — Batch DOI Pre-Verification via CLI

Collect all DOIs from Phase 3 candidates and run:

```bash
scholarly scholarly-verify-dois --dois D1,D2,... --json
```

This checks each DOI against all enabled sources (OpenAlex, Scopus, WoS). For each result:

- **VERIFIED (2+ sources):** Check that the **returned title matches** the expected paper. If the title doesn't match, the DOI is wrong — flag as DOI MISMATCH and find the correct DOI in Step 2.
- **SINGLE_SOURCE:** Needs manual verification — the DOI may be real but unconfirmed.
- **NOT_FOUND:** DOI is likely hallucinated. Find the correct DOI in Step 2.

**Title-matching is mandatory.** `scholarly scholarly-verify-dois` returns the title each DOI actually resolves to. Compare this against the title you expect. DOIs that are off by one character in the suffix (e.g., `02387` vs `02366`, `2014.01.014` vs `2014.03.013`) are the most common hallucination pattern — they resolve to real papers in the same journal but with different content.

## Step 2 — Find Correct DOIs for Flagged Papers

For any paper where the DOI was wrong, missing, or single-source, use these methods **in order of reliability**:

1. **Crossref API** (most reliable): `curl -sL "https://api.crossref.org/works?query.bibliographic=[URL-encoded title+author]&rows=3"` — returns the actual DOI from publisher metadata.
2. **`scholarly scholarly-search`** with exact title — searches OpenAlex/Scopus/WoS for the paper.
3. **Web search as last resort** — but DOIs from web search must still be verified via `scholarly scholarly-verify-dois` before use.

## Step 3 — Manual Verification for Remaining Papers

Spawn **multiple general-purpose agents in parallel**, each verifying ~5 papers. Read the full verification template from [agent-templates.md](agent-templates.md#phase-4-verification-agent-template). **Include the Crossref instruction** in the agent prompt — agents must use Crossref API (`curl`) for DOI lookup, not reconstruct DOIs from memory. Sub-agents can also call `scholarly` CLI directly (e.g., `scholarly scholarly-search "<title>" --json` for preprint upgrades).

Key rules enforced by the template:

- DOI verification is mandatory (resolve and confirm)
- ALL authors must be listed (never "et al." in metadata)
- Preprint check: always search for published version; use `scholarly scholarly-search` CLI to find published versions of preprints
- Results: VERIFIED / NOT FOUND / METADATA MISMATCH

## Step 4 — Final DOI Gate

Before proceeding to Phase 5/6, run `scholarly scholarly-verify-dois` one final time on ALL DOIs that will enter the `.bib`. This is the hard gate — no DOI enters a bibliography without passing this check with a matching title. Papers without DOIs (working papers, book chapters, old pre-DOI articles) are acceptable but must be explicitly flagged as `% NO DOI` in the `.bib`.

After all return: collect VERIFIED, drop NOT FOUND, check for remaining duplicates.

## Step 5 — Assign Metadata Confidence Grades

Every verified paper gets a confidence grade:

| Grade | Criteria |
|-------|----------|
| **A** | DOI resolves correctly; metadata matches trusted source (publisher, Crossref, OpenAlex). Full metadata available. |
| **B** | Stable identifier; metadata consistent across ≥2 sources. No verified DOI, or minor metadata gaps. |
| **C** | Single non-canonical source or incomplete metadata. Include only if the item is the sole source for a needed concept/method/dataset; state what is unverified. |

When sources disagree on metadata, use publisher-of-record version and note the discrepancy. Carry the grade forward into Phase 6 (bibliography) and Phase 7 (synthesis output).

## Step 6 — Working Paper Inclusion Test

For any paper that remains a preprint/working paper after the preprint check, apply this structured gate. Include only if the paper meets **≥2** of these criteria:

1. High citations or downloads relative to age
2. Established author(s) with track record in the field
3. Presented at a top venue (note venue and year)
4. Sole source for a needed dataset, method, or concept
5. Verifiable forthcoming/accepted status

For each included working paper, **state which ≥2 criteria it meets** in the bibliography annotation. Label as "Working paper / preprint." No Confidence C working papers in the must-read shortlist without explicit justification.

## Breadcrumb

Append to `.planning/state.md` (if exists) or `.context/current-focus.md`:

```
### [/literature] Phase 4 complete [YYYY-MM-DD HH:MM]
- **Done:** [N verified, N dropped (not found), N DOI mismatches corrected]
- **Outputs:** [verified paper list ready for bib assembly]
- **Next:** PDF download → bib assembly → validation
```
