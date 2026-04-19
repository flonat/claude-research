# Literature — Phase 6: BibTeX Format and Rules

> Standard BibTeX output format for `literature_summary.bib` and project canonical `.bib`.

## Format

```bibtex
@article{AuthorYear,
  author    = {Last, First and Last, First},
  title     = {Full Title},
  journal   = {Journal Name},
  year      = {2024},
  volume    = {XX},
  pages     = {1--20},
  doi       = {10.1000/example},
  abstract  = {Abstract text here.}
}
```

## Rules

- **Citation keys:** use Better BibTeX-format keys (e.g., `Author2016-xx`). If merging into an existing `.bib`, match the key format already in use. Never generate `AuthorYear` keys.
- **Reuse existing Paperpile citation keys** — for entries marked **ALREADY IN PAPERPILE** in Phase 1, use the Paperpile `citationKey` directly. Do not generate a new key.
- **Only VERIFIED papers** — no METADATA MISMATCH entries.
- **List ALL authors explicitly** — never "et al." in BibTeX.
- **Include abstracts when available.**
- **S2 BibTeX seed:** Call `scholarly scholarly-paper-detail` for each verified paper to get pre-formatted BibTeX via the `citationStyles` field. Use as a starting template, then enrich with missing fields (abstract, pages, volume) and correct the citation key to BBT format. This reduces manual entry errors.
- **Confidence grade:** Add a BibTeX comment above each entry with its confidence grade from Phase 4: `% Confidence: A` (or B/C). This is metadata for the literature review, not for LaTeX.
- **Working paper criteria:** For working papers, add a comment noting which inclusion criteria were met: `% WP criteria: established author + sole source for concept`
- **Connection note:** Every entry in `literature_summary.md` must include a **connection note** — a 1-sentence link to ≥1 other entry in the bibliography ("agrees with", "extends", "contradicts", "uses same data as", "applies method from"). This prevents the bibliography from reading as an isolated list. Connection notes go in the annotation/summary, not in the `.bib` file.
