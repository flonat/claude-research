---
name: gather-readings
description: "Use when you need to gather PDFs from Paperpile into a project's articles/ folder."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls*), Bash(cp*), Bash(mkdir*), Bash(python*), Bash(uv*), Bash(paperpile*)
argument-hint: "[.bib file, Paperpile label name, or search queries]"
---

# Gather Readings

> Copy PDFs from your Paperpile library (Google Drive) into a project's `articles/` folder with clean filenames. Bridges the gap between "papers in Paperpile" and "corpus ready for analysis."

## When to Use

- Before running corpus skills (`/theory-mapper`, `/method-audit`, `/weakness-scanner`, `/quote-mining`, `/replication-audit`, `/evolution-timeline`, `/future-research-agenda`, `/interdisciplinary-bridge`)
- When starting a literature review and want all relevant PDFs in one place
- When a `.bib` file exists but the PDFs are scattered across Paperpile's Google Drive folder

## When NOT to Use

- **Finding new papers** — use `/literature` first, stage as BibTeX for Paperpile import, then gather
- **Reading a single paper** — use `/split-pdf` directly or `paperpile get-pdf-text`
- **Papers not in Paperpile** — download manually or via `/split-pdf`, which handles acquisition

## Input

The user provides one of:

1. **A `.bib` file** — match each entry to a Paperpile item by DOI, title, or author+year
2. **A Paperpile label name** — gather all items in that label
3. **A list of search queries** — search Paperpile for each and gather matches
4. **"All cited papers"** — parse `.tex` files for `\cite{}` keys, match against `.bib`, then gather

If ambiguous, ask: "Which papers should I gather? Point me to a .bib file, name a Paperpile label, or list search terms."

## Workflow

### Phase 1: Identify Target Papers

**From a `.bib` file:**
1. Parse the `.bib` to extract entries (DOI, title, author, year)
2. For each entry, search Paperpile:
   - First try DOI via `paperpile lookup-by-doi` (most reliable match)
   - Fallback to `paperpile search-library` by title
   - Fallback to author + year search
3. Record matches and misses

**Dispatch rule for ≥5 entries.** Per [`_shared/cli-dispatch-policy.md`](../_shared/cli-dispatch-policy.md): if the `.bib` has 5 or more entries, DO NOT loop in main context. Batch entries into groups of 5 and dispatch each group to a Bash sub-agent. Each sub-agent runs the lookup loop for its batch and writes matches to `/tmp/gather-readings-<n>.json`. Main context merges. For <5 entries, sequential lookup in main context is fine.

**From a Paperpile label:**
1. Call `paperpile get-labels` to find the label
2. Use `paperpile get-items-by-label` to get items in that label
3. All items in the label are targets

**From search queries:**
1. For each query, call `paperpile search-library`
2. Present results and ask user to confirm which items to gather

**From cited papers:**
1. Find `.tex` files in the project, extract `\cite{key}` commands
2. Match keys against the project's `.bib` file
3. Proceed as "from a .bib file" with the matched entries

### Phase 2: Locate PDFs

PDFs live in the local rclone mirror of the Paperpile library (path from `~/.config/task-mgmt/paperpile-pdfs`, currently `/Volumes/SSD/paperpile-pdfs`). This is the same canonical mirror RefPile ingests — kept fresh by the `sync-paperpile` cron (4×/day) and more complete than the Google Drive Desktop copy. The mirror has the `All Papers/` level stripped, so attachment filenames like `All Papers/Other/Foo.pdf` resolve to `<paperpile-pdfs>/Other/Foo.pdf`.

For each matched Paperpile item:

1. Call `paperpile get-item` with the citekey to get full metadata, including `attachments[].filename`
2. Resolve the PDF path from the attachment filename under `<paperpile-pdfs>/` (strip the leading `All Papers/` prefix Paperpile uses). This is the authoritative source of the path.
3. If the item has no attachment, fall back to searching `<paperpile-pdfs>/All Papers/` subdirectories by author + year pattern
4. `paperpile get-pdf-text` returns the **cleaned Markdown text**, NOT a path — use it only to confirm a PDF is extractable, never to locate the file
5. If no PDF exists, record as "no PDF available"

### Phase 3: Copy with Clean Filenames

1. Create `articles/` in the project directory if it doesn't exist
2. For each PDF found, copy (NOT move) to `articles/` with a clean filename:

**Filename convention:** `author_year_shorttitle.pdf`
- `author`: first author's surname, lowercase, no accents (e.g., `santanna`)
- `year`: 4-digit year
- `shorttitle`: first 3-4 meaningful words of the title, lowercase, joined with hyphens (e.g., `doubly-robust-did`)
- Example: `santanna_2020_doubly-robust-did.pdf`

**If the `.bib` key is available**, prefer using it as the filename (e.g., `santanna2020doubly.pdf`) for consistency with citations. Ask the user which convention they prefer on first run.

**Collision handling:** If a file with the same name already exists in `articles/`:
- Compare file sizes — if identical, skip (already gathered)
- If different, append `-v2` to the new file

### Phase 4: Report

Print a summary table:

```markdown
## Gather Report

**Target:** [source — .bib file / label / queries]
**Found:** X/Y papers with PDFs
**Copied:** Z new PDFs to articles/
**Skipped:** W (already in articles/)

| # | Author (Year) | Title | Status | Filename |
|---|--------------|-------|--------|----------|
| 1 | Smith (2020) | Paper Title | Copied | smith_2020_paper-title.pdf |
| 2 | Jones (2019) | Another Paper | Already exists | jones_2019_another-paper.pdf |
| 3 | Lee (2021) | Missing Paper | No PDF in Paperpile | — |

### Missing PDFs
These papers are in Paperpile but have no PDF:
- Lee (2021) — "Missing Paper" — DOI: 10.xxxx/yyyy
  → Try: `scholarly unpaywall-find-pdf` or download manually

### Not Found in Paperpile
These .bib entries had no Paperpile match:
- `bibkey2023` — "Unmatched Paper" — DOI: 10.xxxx/zzzz
  → Stage as BibTeX for Paperpile import, or download via `/split-pdf`
```

Write the report to `articles/GATHER-REPORT.md` for reference.

### Phase 5: Ready for Analysis

After gathering, suggest next steps:

> "articles/ now has [N] PDFs ready for analysis. You can run:
> - `/theory-mapper articles/` — map the theoretical landscape
> - `/method-audit articles/` — compare empirical methods
> - `/weakness-scanner articles/` — find vulnerable arguments
> - `/split-pdf articles/<file>.pdf` — deep-read a specific paper"

## Important Notes

- **Never move or delete** the original PDF in Paperpile's Google Drive folder — always copy
- **Never modify** Google Drive's Paperpile directory structure
- PDFs in `articles/` are working copies — Paperpile remains the source of truth
- If `articles/` is inside `paper/` (Overleaf symlink), flag the Overleaf separation rule and suggest moving to project root

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/split-pdf` | To deep-read individual papers after gathering |
| `/literature` | To find NEW papers (this skill gathers papers already in Paperpile) |
| `/bib-coverage` | To compare .bib against Paperpile labels (audit, not gather) |
| `/theory-mapper` | Run on `articles/` after gathering |
| `/method-audit` | Run on `articles/` after gathering |
| `/weakness-scanner` | Run on `articles/` after gathering |

## Citation Contract

<!-- paperpile-citation-contract -->
1. Paperpile is the only source of truth for committed citation keys and BibTeX metadata.
2. Before writing `\cite{key}`, verify with `paperpile get-item key` and `paperpile export-bib key`.
3. Resolve unknowns in order: DOI lookup → Paperpile substring search → `refpile` semantic search → Paperpile verify.
4. A DOI miss is **not** non-membership; continue with title/author search and refpile.
5. If unresolved, write `\CiteTodo{slug}{title/author/year/DOI hint}` — never a guessed key.
6. Drafting sub-agents must not write/edit the active `.bib`; only the orchestrator regenerates it from Paperpile exports.
7. Stage genuine new refs under `.paperpile-import/` for manual Paperpile import; don't cite until Paperpile mints the key.
8. Run `scripts/bib/citation_lint.py` before commit; zero placeholders, zero non-Paperpile keys, zero hand-authored metadata.

See `rules/paperpile-citations.md` for the full workflow.
