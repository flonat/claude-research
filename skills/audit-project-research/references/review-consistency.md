# Phase 4.6: Review Process Consistency

> Detailed check for `/audit-project-research` Phase 4.6.

If `correspondence/referee-reviews/` exists and is non-empty, verify that review documents follow the `/strategic-revision` skill's expected structure. Also detect misplaced review files elsewhere in the project.

## Expected structure per round

The `/strategic-revision` skill outputs this structure:

```
correspondence/referee-reviews/{venue}-round{n}/
+-- reviews-original.pdf              (copy of referee reports)
+-- rebuttal.md                       (response draft -- may not exist yet)
+-- analysis/
    +-- comment-tracker.md            (atomic comment matrix)
    +-- review-analysis.md            (strategic overview)
    +-- reviewer-comments-verbatim.tex (LaTeX transcription)
```

## Step 1: Validate round directories

List directories inside `correspondence/referee-reviews/`. Each should match the pattern `{venue}-round{n}` (e.g., `ejor-round1`, `facct-2026-round2`).

| Condition | Severity |
|-----------|----------|
| Directory matches `*-round*` pattern | OK -- check contents |
| Directory does not match pattern | **Info** -- "unrecognized directory in correspondence/referee-reviews/" |
| No directories found (only `.gitkeep` or empty) | **Info** -- "correspondence/referee-reviews/ exists but has no round directories" |

## Step 2: Check required files per round

For each round directory, check:

| File | Required | Severity if absent |
|------|----------|-------------------|
| `reviews-original.pdf` | Yes | **Missing** -- "no original reviews PDF in {round}/" |
| `analysis/` | Yes | **Missing** -- "no analysis/ subdirectory in {round}/" |
| `analysis/comment-tracker.md` | Yes | **Missing** -- "no comment tracker in {round}/analysis/" |
| `analysis/review-analysis.md` | Yes | **Missing** -- "no review analysis in {round}/analysis/" |
| `analysis/reviewer-comments-verbatim.tex` | Yes | **Missing** -- "no verbatim transcription in {round}/analysis/" |
| `rebuttal.md` | No | Not flagged if absent (created when response work begins) |

## Step 3: Check for build artifacts

Scan each round directory for LaTeX build artifacts that should be in `out/` or absent:

```
*.aux, *.bbl, *.blg, *.fdb_latexmk, *.fls, *.log, *.synctex.gz, *.dvi
```

| Condition | Severity |
|-----------|----------|
| Build artifacts in `analysis/` (not inside `out/`) | **Degraded** -- "build artifacts in analysis/ -- should be in analysis/out/ or cleaned" |
| `analysis/out/` exists with artifacts | OK -- correct location |

## Step 4: Detect misplaced review files

Scan `docs/venues/` for files that look like they belong in `correspondence/referee-reviews/`:

```bash
# Patterns that suggest misplaced review documents
find "<project>/docs/venues/" -type f \( \
  -name "reviewer-comment*" -o -name "comment-tracker*" \
  -o -name "review-analysis*" -o -name "*reviewer-reports*" \
  -o -name "*referee-report*" -o -name "reviews-original*" \
\) 2>/dev/null
```

Also check for directories named `reviewer-comments/` or `reviews/` inside `docs/venues/`:

```bash
find "<project>/docs/venues/" -type d \( \
  -name "reviewer-comments" -o -name "reviews" \
\) 2>/dev/null
```

| Condition | Severity |
|-----------|----------|
| Review files found in `docs/venues/` | **Degraded** -- "review file found in docs/venues/ -- should be in correspondence/referee-reviews/{venue}-round{n}/" |
| `reviewer-comments/` directory in `docs/venues/` | **Degraded** -- "reviewer-comments/ directory found in docs/venues/ -- review documents belong in correspondence/referee-reviews/" |

## Step 5: Check for version consistency

If multiple versions of the same file exist (e.g., `comment-tracker.md` and `comment-tracker-v2.md`), report as **Info** -- "multiple versions found -- verify latest is current".

## Report format

```
Review Process Consistency:
  correspondence/referee-reviews/ejor-round1/
    reviews-original.pdf       present
    analysis/                  present
      comment-tracker.md       present
      review-analysis.md       present
      reviewer-comments-verbatim.tex  present
    rebuttal.md                not yet created

  Misplaced files:             none found in docs/venues/
```

Or when issues are found:

```
Review Process Consistency:
  correspondence/referee-reviews/ejor-round1/
    reviews-original.pdf       present
    analysis/                  missing

  Misplaced files:
    docs/venues/ejor/revision-1/reviewer-comments/comment-tracker.md
      -> should be in correspondence/referee-reviews/ejor-round1/analysis/
```

## When to skip

- If `correspondence/referee-reviews/` does not exist -- Phase 2.2 already flags this as Missing
- If the project is theoretical with no venue history
