# Phase 6: Build PDF companion (soft-fail)

After Phase 5 lands the registry entry, atlas reload, and smoke test, build a PDF companion alongside the HTML book. Atlas remains the canonical reader surface; the PDF is a shareable, paginated artifact for those who want one.

## Invocation

```bash
bash ~/.claude/skills/init-paper-book/scripts/build-book-pdf.sh <slug>
```

Output: `~/vault/books/<slug>/exports/<slug>.pdf`.

The script is generic — any vault book with an `index.yaml` registry entry can be built. No per-book code needed.

## What the script does

1. `myst build --tex` → writes raw LaTeX to `<book>/_build/tex/`
2. Patches the main `.tex`:
   - Swaps 8-bit `fontenc+inputenc+lmodern` for `fontspec` with explicit `.otf` paths (xelatex unicode glyph support)
   - Adds a `\newunicodechar` map for box-drawing / arrow glyphs mystmd emits
   - Adds `\ensuremath` wrappers for bare `\rightarrow` / `\leftarrow` / etc. so they survive text mode
   - Replaces book-class `\maketitle` with a custom titlepage that folds publication info onto page 1
3. Patches each chapter `.tex`:
   - `\section{...}` → `\chapter{...}` (so chapter counter advances; 0.x → 1.x numbering)
   - Bumps `\subsection` → `\section`, `\subsubsection` → `\subsection`, `\paragraph` → `\subsubsection`
   - Inserts `{}` after `\rightarrow`-family commands followed by letters (TeX gobble-bug)
4. `latexmk -xelatex` → copies result to `exports/<slug>.pdf`

## Dependencies

| Tool | Install |
|------|---------|
| `mystmd` v1.10+ | `npm install -g mystmd` |
| `xelatex` | MacTeX / TeX Live |
| `latexmk` | bundled with MacTeX |
| `python3` | system |

If `mystmd` is missing, the script exits with a one-line error and the overall init pipeline continues (PDF is non-blocking).

## Soft-fail contract

- Missing `mystmd` → log warning, continue
- Missing `myst.yml` → script auto-bootstraps one from `~/vault/books/index.yaml`
- `latexmk` non-zero exit → warn, point at the build log, continue (a partial PDF may have been written)
- Missing or unresolved cross-references (e.g. `#sec-foo` not found) → mystmd warns at build time, doesn't block

The init pipeline never blocks on PDF errors. Atlas HTML rendering is canonical; the PDF is a derived artifact.

## Frontispiece title page

The script replaces the book-class `\maketitle` with a **frontispiece** that mirrors
the web cover at `books.example.com/<slug>`: a "Reading Companion" eyebrow, the book
title (with any trailing "— A Reading Companion" suffix stripped so it doesn't echo
the eyebrow), a "Companion to <paper>" line, the author, the
venue · status · institution row, and publication IDs (DOI / arXiv / Code) at the
foot. Always applied — even with no publication metadata the eyebrow + title +
author + date beats the bare default.

Metadata reads from two sources:

| Source | Fields |
|--------|--------|
| Atlas topic (`~/vault/atlas/<theme>/<slug>.md`) | `paper_title`, `venue`, `status` from `outputs[0]`; `institution` from the top level |
| `<book>/myst.yml` | `subtitle`, `conference_date`, `doi`, `arxiv`, `repo`, `license` (overrides win) |

The atlas topic is the canonical record. Per-book overrides in `myst.yml` fill fields atlas doesn't carry (conference dates, repo URLs, license).

## Standard math macros

The preamble patch injects a default set of research-notation macros via
`\providecommand`, mirroring the source papers' preambles and the web book's
MathJax macro set (atlas `prose-assets.html`):

| Macro | Expansion |
|-------|-----------|
| `\Prob` | `\mathbb{P}` |
| `\E` | `\mathbb{E}` |
| `\Var` | `\operatorname{Var}` |
| `\1` | `\mathds{1}` — double-stroke indicator 𝟙 (via `dsfont`) |

Each is `\ensuremath`-wrapped so it also survives in text mode (mystmd can
emit these outside `$...$`, like the arrow glyphs). The preamble loads
`dsfont` for `\mathds`; the web book uses `\mathbb{1}` for the same glyph
(MathJax's double-struck digit).

Because it's `\providecommand`, a book that defines the same macro itself —
either in its chapter source or via a `math:` block in `<book>/myst.yml`
(mystmd expands those inline before this preamble runs) — always wins; the
injected defaults are just a net so common shorthand resolves without
per-book config. Add more here (and in `prose-assets.html` for the web) as
conventions recur.

## When to skip

- The user passes `--no-pdf` to `/init-paper-book` (future flag; not yet wired)
- The book has no `index.yaml` registry entry (means Phase 5 didn't run — Phase 6 has nothing to do)
