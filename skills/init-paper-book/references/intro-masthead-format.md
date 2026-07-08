# Intro Masthead Format

The intro chapter uses a **definition-list masthead** under a one-sentence lede, followed by the atlas Description body as the chapter's prose content. The template page supplies the H1 from `chapter.title` in frontmatter (always `Intro`), so chapter files must **not** include a `# Heading` of their own.

```markdown
---
title: Intro
short_title: Intro
---

<lede: first paragraph of atlas `## Description` (use first sentence if the paragraph is >320 chars)>

Authors
: <Full author list with per-author institutions inline>

Venue
: <Venue> — <atlas outputs[0].status, used verbatim>

Topic
: [<Atlas topic title> ↗](https://atlas.example.com/topic/<atlas-slug>)

Source
: [📝 Overleaf ↗](<overleaf-link from atlas>)   ← omit when status starts with Accepted / In Press / Camera-ready / Published / Withdrawn

## About this paper

<remaining paragraphs of atlas `## Description`, with `[[wikilinks]]` flattened to plain text>
```

**Required masthead fields:** `Authors`, `Venue`, `Topic`. Optional: `Preprint`, `Source` (Overleaf, dropped on terminal status), `Status` (only when needed beyond what's in Venue).

**Status vocabulary.** Atlas status is canonical and used verbatim — including curated terms (e.g. `Curating`, `Curating (Route A — 12-week plan)`). Do not normalise atlas's status to a fixed enum.

**Topic field convention.** Every intro must link to the atlas topic via the `Topic` definition. This grounds the book in the portfolio and gives readers a one-click path to the topic's full context (status history, connected topics, key references, follow-up directions).

**Body content sourced from atlas Description.** The intro chapter's prose comes from the atlas topic's `## Description` section. This keeps the book and atlas synchronised at the source — when the atlas description is updated, re-running the migration regenerates the intro automatically. Do not hand-write distinct prose in `intro.md` *above* the preserve marker; instead, edit the atlas topic's Description and re-run.

**Regenerate command.** When the atlas Description changes (or a book's `intro.md` drifts from the convention), regenerate via:

```bash
~/Task-Management/packages/atlas-workspace/.venv/bin/python \
    ~/.claude/skills/init-paper-book/scripts/regenerate_intro.py \
    <slug> --apply    # omit slug or pass 'all' to do every book

# Dry-run (prints to stdout, no writes):
~/Task-Management/packages/atlas-workspace/.venv/bin/python \
    ~/.claude/skills/init-paper-book/scripts/regenerate_intro.py <slug>
```

The script reads the book registry, resolves the atlas topic (aborting if Hard Rule 4 is violated), rebuilds the masthead + `## About this paper` body from the atlas Description, and preserves anything below the preserve marker.

**Preserve marker for hand-written content.** Anything below this HTML comment marker survives regeneration verbatim:

```markdown
## About this paper

<atlas-derived prose — regenerated on every run>

<!-- preserve-below: hand-written content survives regeneration -->

## Reading guide for this companion

This book is organised around three claims …
<your hand-written prose lives here and is never overwritten>
```

The marker is matched as an exact string. The regenerate script (`scripts/regenerate_intro.py`) captures every line beneath the marker (including blank lines, headings, callouts, tables) and re-appends it after regenerating the masthead + `## About this paper` block. Common uses for the preserved region: a "How to read this companion" guide, "Three claims" framing, reading-group focus pointers, table of headline numbers, FAQ. Place anything that's specifically *companion editorial* — not in the paper, not in the atlas description — below the marker.

Books without the marker are fully regenerated (atlas-only). Adding the marker mid-life is safe: place it where you want hand-written content to start, write below it, and the next regeneration will preserve everything below.

Atlas's markdown filter has the `def_list` extension enabled, so `Term\n: definition` renders as `<dl><dt>...</dt><dd>...</dd></dl>`. The older blockquote masthead pattern (`> **Paper.** ...`) is deprecated and must be migrated via `/audit-paper-book --apply`.

## Overleaf-link handling

The intro's `Source` field includes an Overleaf link when the paper is **still in flight** (under review, in revision, drafting). Once **accepted or published**, the link is dropped (canonical artefact is the published PDF / DOI).

Decision rule:

- If atlas topic has `overleaf_link:` AND the relevant `outputs[].status` is in `{Idea, Drafting, Submitted, Under Review, R&R, Revising}` → **include** an additional `Source` field in the masthead `dl`:
  ```
  Source
  : [📝 Overleaf ↗](<url>)
  ```
- If `outputs[].status` is in `{Accepted, In Press, Camera-ready, Published, Withdrawn}` → **omit** the Source field.
- If no `overleaf_link:` is present → omit (and flag once at Phase 5 verification: "No Overleaf link in atlas — add it under outputs/top-level if you want it surfaced in the book").

Pick the relevant `outputs[]` entry by matching `paper_path` to the project's actual paper directory (e.g., `paper-neurips/`, `paper-acm-ccs/`).
