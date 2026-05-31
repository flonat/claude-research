---
paths:
  - "**/*.bib"
  - "**/*.tex"
  - "**/literature-review/**"
  - "**/references.*"
---

# Rule: Verify Every Reference Before Writing

## Principle

**Never write any paper reference to any output file without verifying the paper exists.** This applies to every format — markdown literature reviews, `.bib` entries, inline citations in `.tex`, reference lists in reports. The sequence is always: find → verify existence → verify DOI → write.

Hallucinated papers are worse than missing papers. A missing citation is an honest gap; a fabricated citation undermines the entire document's credibility.

## Paper Existence Protocol

### Before writing any paper reference (markdown, .bib, .tex, any file)

1. **Verify the paper exists** in at least one academic database — run `scholarly scholarly-search "author title" --json` or `scholarly scholarly-paper-detail <id> --json` (if you have a DOI or S2 ID). A paper that returns zero hits across all sources does not exist.
2. **Collect the DOI** from the search result. If no DOI is returned, look up via `scholarly crossref-lookup-doi --query "author title" --json`.
3. **Batch-verify DOIs** via `scholarly scholarly-verify-dois --dois ... --json` (up to 50 at once).
4. **Only write verified references** — never record a reference to a paper you cannot find in any database, regardless of how confident you are it exists.

> **Tooling note:** Use the `scholarly` CLI (and `refpile` / `paperpile` for owned-library checks) — never `mcp__scholarly__*`. CLIs work in main context AND inside sub-agents; MCP tools don't propagate. See `bibliography-routing.md`.

### Hallucination Red Flags

Drop the paper immediately (do not write, do not flag as "unverified") if ANY of these are true:

- **Publication date is in the future** or the current year with no database record
- **Zero hits** across `scholarly scholarly-search`, `scholarly crossref-lookup-doi`, and `scholarly scholarly-paper-detail`
- **Title is suspiciously tailored** to the exact research question (real papers have broader or tangential titles)
- **Authors cannot be found** via `scholarly scholarly-search` with their name + field
- **Venue does not exist** or the paper is not in the venue's proceedings/issue

When a paper is dropped, do not include it with a caveat — omit it entirely.

### DOI Verification Statuses

| Status | Action |
|--------|--------|
| VERIFIED (2+ sources) | Safe to write |
| SINGLE_SOURCE | Write, but flag as low-confidence |
| NOT_FOUND | Do NOT write the DOI. Look up correct DOI via `scholarly crossref-lookup-doi` or `scholarly scholarly-paper-detail`. If still not found, write "DOI: not available" explicitly |

### Every reference must have a DOI

When writing a reference list, every entry must include a DOI. If a paper genuinely has no DOI (pre-digital, working paper, book chapter), state this explicitly (e.g., "arXiv:XXXX.XXXXX" or "No DOI — working paper") rather than leaving the field silently blank.

## When This Applies

- Writing `docs/literature-review/` files
- Adding entries to `.bib` files
- Running `/literature` (pipeline mode) or `/bib-validate`
- Any task that produces a list of references
- **Any ad-hoc literature summary** — including during `/init-project-research`, project recaps, or when asked to "list relevant papers"
- **Any context where you are about to cite a paper from memory** — if you haven't verified it in this session, verify before writing

## When to Skip

- Reading or summarising papers the user has provided (existence already confirmed)
- Informal conversation about papers ("have you seen X?") where no file is being written
- Discussing well-known foundational works in conversation (not writing to files)

## Why This Matters

Six hallucinated papers were written to a literature review in this project — all had plausible authors, titles, and venues but did not exist in any academic database. Three DOIs in another project pointed to wrong papers. Verification takes seconds per paper and prevents silent corruption of research outputs.
