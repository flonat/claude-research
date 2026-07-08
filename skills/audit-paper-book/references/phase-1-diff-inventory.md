# Phase 1: Diff Inventory

**Paper-tex resolution.** The audit needs to know which `.tex` file is the canonical paper. Resolution order:

1. **Registry override.** If the book's entry in `~/vault/books/index.yaml` has a `paper_tex:` field, it's used as a path relative to the project root (e.g. `paper-acm-gecco/paper/gecco2026.tex`). Set this once at `/init-paper-book` setup when the paper's tex isn't named `main.tex` (common with ACM templates that name files after the venue).
2. **Canonical layout.** First `paper-*/paper/main.tex` under the project (the Overleaf symlink convention).
3. **Backup fallback.** First `paper-*/backup/main.tex` (for when the Overleaf symlink is temporarily down).

If none resolve, the book is surfaced in the JSON summary as `{"slug": ..., "error": "no paper tex found"}` rather than silently skipped — fix by adding `paper_tex:` to the registry.

Build four diffs.

**Bibliography diff:**
```bash
PAPER_BIB="$PAPER_DIR/.../references.bib"
BOOK_BIB=~/vault/books/"$SLUG"/references.bib
diff <(grep -oE "@\w+\{[^,]+," "$PAPER_BIB" | sort) \
     <(grep -oE "@\w+\{[^,]+," "$BOOK_BIB" | sort)
# Capture: bib_added, bib_removed, bib_unchanged
```

**Figures diff:**
- Walk `\includegraphics{...}` paths in paper tex.
- Resolve to `<project>/figures/...png` or `<project>/output/figures/...png`.
- Compare against `~/vault/books/<slug>/figures/`.
- Capture: figs_paper_only, figs_book_only, figs_changed (mtime / size differs).

**Numeric drift:**
- Extract numeric claims from paper abstract + result tables (regex: ranges like `0.85`, `2.82 ± 1.4`, `93.7%`).
- Grep each book chapter for the same numeric strings.
- Capture: numbers_in_book_not_paper, numbers_in_paper_not_book.

**Section structure drift:**
- Extract `\section{...}` and `\subsection{...}` from paper tex.
- Compare against the chapter outline declared in `~/vault/books/index.yaml` for this slug.
- Capture: paper_sections_added, paper_sections_renamed, book_chapters_orphaned.

**Overleaf-link drift (status transitions):**
- Read the atlas topic's `outputs[].status` for the paper-path that matches this book.
- Read the book's `intro.md` masthead — does it currently contain a `https://www.overleaf.com/...` link?
- Capture cases:
  - Status is `{Accepted, In Press, Camera-ready, Published, Withdrawn}` AND book intro has Overleaf link → **propose removal** (paper accepted; Overleaf source is no longer the canonical artefact).
  - Status is in-flight (`{Idea, Drafting, Submitted, Under Review, R&R, Revising}`) AND atlas has `overleaf_link:` AND book intro lacks the link → **propose addition**.
  - Atlas `overleaf_link:` URL has changed AND book intro shows the old URL → **propose update**.

**Published-masthead drift (status = Published):**

When `outputs[0].status` starts with `Published`, the intro masthead must reflect the published state. The audit checks two things:

- **DOI Source line.** Atlas `outputs[0].doi` should appear somewhere in `intro.md`. If atlas has a DOI but the intro doesn't reference it (e.g. the Source line still points at Overleaf, or was dropped without a replacement), **propose addition** of `Source\n: [📄 DOI: <doi> ↗](https://doi.org/<doi>)`.
- **Venue line freshness.** If `intro.md` has a Venue line that contains stale status markers (`R&R`, `Major Revision`, `In Press`, `Accepted`, `under review`, `under revision`, `In preparation`, `Submitted`, `Drafting`) and does NOT contain the word `Published`, **propose rewrite** to `*<venue>* (<year>) — Published online <publication_date>`.

Both fixes are deterministic and pull from the same atlas fields (`outputs[0].venue`, `.doi`, `.publication_date`). The canonical fix is to invoke `regenerate_intro.py --apply` — see the next paragraph.

**Regenerate via the shared script.** When format-convention drift is found, the canonical fix is to invoke the regenerate script — same one `/init-paper-book` uses, so the format stays in lockstep:

```bash
~/Task-Management/packages/atlas-workspace/.venv/bin/python \
    ~/.claude/skills/init-paper-book/scripts/regenerate_intro.py \
    <slug> --apply
```

This rebuilds `intro.md` from the atlas topic and re-appends anything below the preserve marker. Use it instead of hand-editing format drift — it's the only way to guarantee identity across books.

**Masthead format drift (definition-list convention):**

The canonical intro masthead is a definition list (atlas has `def_list` enabled). The old blockquote pattern (`> **Paper.** ...\n> **Authors.** ...`) is deprecated because it duplicates the H1 the template already supplies and wraps awkwardly on narrow screens. For each book under audit, check:

- **Blockquote masthead present.** If `intro.md` starts with a `> **Paper.**` (or `> **Authors.**` / `> **Venue.**`) block, **propose migration** to the definition-list pattern below. This is the deprecation flagged in `/init-paper-book` Rule 12 + Intro-masthead-format section — Phase 3 `--apply` auto-migrates by regenerating via the shared script.
- **Redundant H1 in chapter body.** If any chapter file `~/vault/books/<slug>/<ch>.md` contains a top-level `^# ` heading anywhere in the body (the template already renders `<h1 class="page-title">` from `index.yaml`), **propose stripping** that line. This catches both legacy books and chapters that were hand-edited.
- **Required masthead fields.** Verify `intro.md` masthead has at minimum `Authors`, `Venue`, and `Topic`. Optional fields: `Preprint`, `Source` (Overleaf — handled by the Overleaf-link rule above), `Status`. Missing required field → **report**, not auto-applied.
- **Missing `Topic` field.** If `intro.md` masthead lacks a `Topic` definition linking to `https://atlas.example.com/topic/<slug>`, **propose addition**. This is the canonical bridge between book and atlas portfolio.
- **Intro body drift from atlas Description.** The intro chapter's prose under `## About this paper` (and *above* the `<!-- preserve-below ... -->` marker if present) should mirror the atlas topic's `## Description` body. If they have drifted, **report** and offer regeneration. Atlas is the source of truth — book intros are derived above the marker, hand-written below it.
- **Preserve marker integrity.** The canonical preserve-marker string is exactly (one line, no leading/trailing whitespace):

  ```
  <!-- preserve-below: hand-written content survives regeneration -->
  ```

  If `intro.md` contains this marker, the regenerate script captures everything beneath verbatim. The audit should:
  - Confirm the marker line matches the canonical string **exactly** (typos = silent loss on next regenerate — e.g., `preserve_below` vs `preserve-below`, missing the `: hand-written content survives regeneration` suffix, or extra whitespace inside the comment).
  - Confirm no atlas-derived content sits *below* the marker (any `## About this paper` or masthead `dl` below the marker is a structural error and will be duplicated on next regenerate).
  - Confirm no hand-written content sits *above* the marker (it will be overwritten on next regenerate).
  Marker drift is reported, not auto-fixed (a malformed marker could indicate intentional restructuring).
- **Status normalised to a fixed enum.** Book mastheads use atlas `outputs[0].status` **verbatim** — including curated terms like `Curating` or `Curating (Route A — 12-week plan)`. If a book has normalised the status to a fixed enum (e.g. atlas says `Major Revision` but book says `R&R`), **report** and regenerate.

Canonical masthead template (mirrors `/init-paper-book` SKILL.md §"Intro masthead format"):

```markdown
---
title: "<Book Title> — A Reading Companion"
short_title: "Intro"
---

<one-sentence lede: what the paper is, in plain language>

Authors
: <First Last>, <First Last> (<Institution from atlas topic's `institution:` field>)

Venue
: <Venue> — <status> · <City> · <Dates>

Preprint
: [arXiv:NNNN.NNNNN ↗](<url>) (vN)

Status
: <In press · Camera-ready submitted DD Mmm YYYY>  *(omit if not yet accepted)*

---
```

**Citation-URL drift:**

Inline citations must use `{cite:t}\`Key\`` and let atlas's converter route them. The converter prefers `/book/<slug>/references#ref-Key` for keys in the local `references.bib` and falls back to `https://atlas.example.com/paper/Key` for keys only in the global library — so hand-constructed citation URLs bypass the fallback and may 404 for grey-literature entries.

- **Hand-constructed `/paper/<key>` link present in chapter.** Regex `\]\(https?://[^)]*atlas\.user\.com/paper/[A-Za-z0-9_-]+\)` or `\]\(/paper/[A-Za-z0-9_-]+\)` in any non-references chapter → **propose conversion** to `{cite:t}\`Key\``.
- **Hand-constructed `[Key](Key)` self-link.** Markdown citations that point at the key as a non-URL → **report**, suggest `{cite:t}\`Key\``.

These two are reported, not auto-applied (rewriting prose in context requires user judgement on cite-t vs cite-p form).
