---
name: init-paper-book
description: "Use when you need to scaffold a NEW educational companion book for a LaTeX paper. Reads the paper, drafts 8 substantive chapters into the vault at ~/Research-Vault/books/<slug>/, copies bib + figures, registers the book, and verifies atlas serves it. Source-of-truth is the paper PDF/tex; the book is a reading companion, never a re-statement of new claims. For syncing an existing book to a paper revision, use /audit-paper-book."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, Task
argument-hint: "<project-path-or-slug> [--dry-run]"
---

# Init Paper Book

Scaffold a runnable, browsable companion to a LaTeX paper. The book lives in the vault, atlas renders it, and direct URLs at `books.user.com/<slug>/<chapter>` make it shareable. There is **no separate build pipeline** — atlas is the renderer.

For syncing an existing book to a paper revision, use `/audit-paper-book` instead.

## Hard rules

### Existential — block writing

1. **No new claims.** The book may rephrase, scaffold, and explain, but never introduce results not in the paper. Numbers and theorems trace to the paper.
2. **Numeric invariant.** Every numeric claim in the book must match the paper. Mismatches block.
3. **Paper is canonical.** Source-of-truth is the paper PDF/tex. Edits to the book do not edit the paper. Edits to the paper require `/audit-paper-book` to propagate.
4. **Atlas slug match.** Book slug = atlas topic filename (lowercase, hyphenated). If project dir and atlas filename disagree, stop and prompt — alignment is required at the source, not a workaround in the book.

### Format — catch in review

5. **Vault location.** Book chapters live at `~/Research-Vault/books/<slug>/`. Never in the project tree (atlas runs under launchd and File Provider paths hang).
6. **Registry entry.** `~/Research-Vault/books/index.yaml` must list the slug, title, atlas-topic pointer, bibliography file, and explicit chapter order.
7. **Eight chapters.** Default skeleton: `intro · background · setup · method · results · limitations · extend · appendix`. The `references` chapter is auto-appended when `bibliography:` is set.
8. **No-index by default.** atlas's base.html injects `noindex,nofollow` for book chapters. Books are direct-link-only — no discovery surface.
9. **Section headings descriptive, never numbered.** Use `## The selection rule`, not `## 4.5 The selection rule`. Cross-references to the paper carry the paper's own numbering inline.
10. **Mystmd-style callouts.** Use `` ```{important} ``, `` ```{tip} ``, `` ```{note} ``, `` ```{warning} ``, `` ```{caution} ``, `` ```{seealso} ``. Atlas's directive converter handles these. Pandoc-style `::: {.callout-X}` does NOT render — convert if you find it in source material.
11. **Figure paths are vault-relative.** `figures/<filename>` resolves to `~/Research-Vault/books/<slug>/figures/<filename>` served by atlas's `/book/<slug>/figures/{filename:path}` route.
12. **Citations as atlas links.** Mystmd `{cite:t}\`Key\`` converts to `[Key](/paper/Key)` automatically. Don't construct paper-detail URLs by hand.
13. **Affiliations from atlas.** Author affiliations come from the atlas topic's `institution:` field. Never hardcode.

## When to use

- Paper submitted, results stable, accepted or under review (no churn)
- Methods/benchmark/theory papers where reuse depends on understanding
- Papers with policy or practitioner audiences who don't read the venue proceedings
- the user explicitly asks for a "book" or "companion" for a paper

## When NOT to use

- Paper still in heavy revision (results moving) — wait or accept that you'll need `/audit-paper-book` immediately after submission
- Slide decks (`/beamer-deck`, `/quarto-deck`)
- Compilation only (`/latex`)
- Generic literature reviews (`/literature`)

## Inputs accepted

```
/init-paper-book <project-path>     # full path to project dir, e.g. /Volumes/SSD/Dropbox/Research/ASG/audit-gaming-benchmark
/init-paper-book <slug>             # atlas slug; resolved via atlas topic file's project_path
/init-paper-book <slug> --dry-run   # plan only, no writes
```

## Pre-flight (block-on-fail)

```bash
SLUG="<resolved-slug>"

# 1. Atlas topic exists
find ~/Research-Vault/atlas -name "${SLUG}.md" -type f | head -1
[[ $? == 0 ]] || die "No atlas topic for ${SLUG}. Run /init-project-research first."

# 2. Project directory exists
PROJECT_PATH=$(grep -E "^project_path:" "$ATLAS_TOPIC" | cut -d' ' -f2- | tr -d "'\"")
RR=$(cat ~/.config/task-mgmt/research-root)
[[ -d "$RR/$PROJECT_PATH" ]] || die "project_path in atlas does not resolve."

# 3. Paper directory + tex file exist
PAPER_DIR=$(ls -d "$RR/$PROJECT_PATH"/paper-* 2>/dev/null | head -1)
PAPER_TEX="$PAPER_DIR/paper/main.tex"
[[ -f "$PAPER_TEX" ]] || PAPER_TEX="$PAPER_DIR/backup/main.tex"
[[ -f "$PAPER_TEX" ]] || die "No main.tex in $PAPER_DIR/{paper,backup}/."

# 4. Bibliography exists
BIB=$(find "$PAPER_DIR" -maxdepth 3 -name "*.bib" | head -1)
[[ -f "$BIB" ]] || warn "No .bib found — references chapter will be empty."

# 5. Vault book dir doesn't already exist
[[ -d ~/Research-Vault/books/"$SLUG" ]] && die "Book already exists. Use /audit-paper-book to sync."
```

## Phases

```
Phase 1: Read paper + plan        (direct read of paper tex + atlas topic)
Phase 2: Scaffold vault           (mkdir, copy bib + figures)
Phase 3: Draft chapters           (mixed — sub-agents for content-heavy chapters)
Phase 4: Register + verify        (registry entry, atlas reload, screenshot probe)
```

### Phase 1: Read + plan

Read in this order:

1. **Atlas topic frontmatter** — title, theme, status, paper title, paper-path, co-authors, institution, **`overleaf_link:`** (top-level or per-output), **`outputs[].status`** (per-venue submission status). These set the book's metadata.
2. **Paper tex** — title, abstract, section structure, headline numerical claims, figure list, theorem statements.
3. **Project README + CLAUDE.md** if they exist — context for the spine.

#### Overleaf-link handling

The book's intro chapter typically includes an Overleaf source link in the masthead blockquote when the paper is **still in flight** (under review, in revision, drafting). Once the paper is **accepted or published**, the Overleaf source becomes irrelevant for sharing (the canonical artefact is the published PDF / DOI), so the link is dropped.

Decision rule:

- If atlas topic has `overleaf_link:` AND the relevant `outputs[].status` is in `{Idea, Drafting, Submitted, Under Review, R&R, Revising}` → **include** the link in the intro masthead with the format:
  > `[📝 Overleaf source ↗](<url>)`
- If `outputs[].status` is in `{Accepted, Camera-ready, Published, Withdrawn}` → **omit** the link.
- If no `overleaf_link:` is present → omit (and flag once at Phase 4 verification: "No Overleaf link in atlas — add it under outputs/top-level if you want it surfaced in the book").

Pick the relevant `outputs[]` entry by matching `paper_path` to the project's actual paper directory (e.g., `paper-neurips/`, `paper-acm-ccs/`).

Produce a one-paragraph plan in your reasoning trace covering:
- Exactly which 8 chapter titles you will write (default skeleton is fine; deviate if the paper structure demands).
- Which figures to copy (paper-cited figures only — don't copy the entire `output/figures/` dir).
- Audience tier (students / practitioners / adjacent-researchers / the user-future-self).
- Whether the paper has executable artefacts to reference, or it's a pure-theory book where chapters cite paper sections.

### Phase 2: Scaffold

```bash
mkdir -p ~/Research-Vault/books/"$SLUG"/figures
cp "$BIB" ~/Research-Vault/books/"$SLUG"/references.bib

# Copy ONLY paper-cited figures. Inspect tex for \includegraphics{...} paths,
# resolve them, then copy or convert as needed:
# - if a .png exists at that path, copy directly
# - if only a .pdf exists (common in NeurIPS/ACM submissions), convert to
#   .png via pdftoppm so atlas can serve to browsers (PNG/SVG/WebP only)
grep -oE '\\includegraphics(\[[^]]*\])?\{[^}]+\}' "$PAPER_TEX" \
  | grep -oE '\{[^}]+\}' | tr -d '{}' \
  | while read -r fig; do
      # Resolve to absolute path (project_path-relative or absolute)
      [[ "$fig" == /* ]] && src="$fig" || src="$PROJECT_PATH/$fig"
      base=$(basename "$fig" | sed 's/\.[^.]*$//')  # strip extension
      out=~/Research-Vault/books/"$SLUG"/figures/"$base"
      # Search for png anywhere — paper tex includes might omit extension or
      # point to PDF while a PNG twin lives elsewhere in the project tree.
      png_src=$(find "$PROJECT_PATH" -name "${base}.png" -type f 2>/dev/null | head -1)
      if [[ -n "$png_src" ]]; then
          cp "$png_src" "${out}.png"
          continue
      fi
      # Fall back to PDF → PNG conversion via pdftoppm (poppler)
      pdf_src=$(find "$PROJECT_PATH" -name "${base}.pdf" -type f 2>/dev/null | head -1)
      if [[ -n "$pdf_src" ]] && command -v pdftoppm >/dev/null; then
          pdftoppm -png -r 150 "$pdf_src" "$out" 2>/dev/null
          # pdftoppm appends `-1` (or `-01` for ≥10-page docs) per page; flatten
          mv "${out}-1.png" "${out}.png" 2>/dev/null \
            || mv "${out}-01.png" "${out}.png" 2>/dev/null
      fi
    done
```

**Note on PNG vs PDF.** Atlas serves files as-is via FileResponse, but browsers can't render PDF inline as a `<figure>` image — only PNG/SVG/WebP/JPG. Always end with `.png` files in the vault `figures/` dir; never publish a `.pdf` figure expecting it to render.

### Phase 3: Draft chapters

Eight chapters. For each, you write substantive prose grounded in the paper, **not placeholders**. Chapter responsibilities:

| Chapter | Role | Length | Key sources from paper |
|---|---|---|---|
| `intro.md` | One-chapter version: headline + 3-bullet result + why it matters | ~600 words | abstract, intro §1, contributions list |
| `background.md` | What the reader needs to know before §3 of the paper | ~800 words | related work, setup primitives |
| `setup.md` | Notation table, threat model / problem statement, worked example if applicable | ~700 words | §2 / setup section, notation table |
| `method.md` | Definitions → propositions → theorems with proof sketches and intuition | ~1200 words | §3 / method section, §4 / theorem statements |
| `results.md` | Headline result, deterministic case study, stress test, figures, comparison tables | ~1000 words | §5 / experiments, figures, tables |
| `limitations.md` | What's NOT claimed, where the framework cracks, what's next | ~600 words | §6 / discussion, §7 / limitations |
| `extend.md` | Worked steps for adopting the framework — code skeletons, extension paths, reproducibility checklist | ~900 words | §8 / instructions, reproducibility manifest |
| `appendix.md` | Notation glossary (consolidated), theorem summary table, reproducibility manifest, links | ~500 words | full paper + atlas topic |

For each chapter:
- Start with a frontmatter block: `title:` (long) and `short_title:` (~1 word for sidebar).
- **`intro.md` masthead.** Pull the paper title, authors (with affiliations from the atlas topic's `institution:` field), and venue from atlas `outputs[]`. Add the Overleaf-source line per the decision rule above (omit if accepted/published).
- Use mystmd-style callouts for asides: `` ```{important} `` for headline statements, `` ```{tip} `` for reading-order hints, `` ```{warning} `` for caveats, `` ```{caution} `` for hazards.
- Use markdown tables for notation + comparison + result tables. Atlas styles tables with hairline dividers + tabular nums.
- Use $...$ and $$...$$ for math. Atlas's arithmatex extension preserves these for MathJax.
- Cross-reference paper sections inline ("paper §4.2") rather than via book chapter numbers.
- For citations, use mystmd-style `{cite:t}\`Key\`` — atlas converts to `/paper/<key>` links automatically.

### Phase 4: Register + verify

```bash
# Append to registry
cat >> ~/Research-Vault/books/index.yaml <<EOF

${SLUG}:
  title: "<book title — paper title or descriptive variant>"
  atlas_topic: "<theme>/<slug>"
  bibliography: references.bib
  chapters:
    - intro
    - background
    - setup
    - method
    - results
    - limitations
    - extend
    - appendix
EOF

# Reload atlas (Mac Mini only — see multi-machine rule)
launchctl bootout gui/$(id -u)/com.user.atlas
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.atlas.plist
sleep 4

# Smoke test every chapter
for ch in intro background setup method results limitations extend appendix references; do
    code=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" \
        "http://localhost:8770/book/${SLUG}/${ch}")
    echo "  ${ch}: ${code}"
done

# Update atlas topic frontmatter with book_url
python3 ~/Task-Management/.scripts/update_atlas_book_url.py \
  --slug "$SLUG" \
  --url "https://books.user.com/${SLUG}/"
```

Acceptance: every chapter returns 200; references chapter shows ≥1 ref-card.

## Anti-patterns

- **Copy-pasting paper text verbatim.** The book is a reading companion, not a transcription. Paraphrase + scaffold; don't duplicate the proof prose.
- **Inventing numbers.** If the paper says "mean gap 0.884", the book says exactly that — never round, never re-derive, never average across runs not in the paper.
- **Adding new theorems or results.** Even an obvious corollary that the paper doesn't state must NOT appear. The book is a reading guide, not a sequel.
- **Pandoc `::: {.callout-X}` callouts.** Atlas's converter handles `` ```{X} `` only. If the paper or notes are in Pandoc, convert before drafting.
- **Hardcoded affiliations.** Pull from atlas topic `institution:` field; never type the institution name inline.
- **Section numbering on book headings.** Book sidebar provides ordinal; the heading itself stays descriptive.

## After-flight

If anything looks visually wrong (callouts not rendering, math not rendering, figures missing), the most common causes are:
- `:::` callout syntax not converted → grep, replace with `` ```{X} ``
- Math wasn't wrapped because of underscores in body — atlas's arithmatex handles this
- Figure path wrong — should be `figures/<filename>` relative to chapter
- Bib file missing or in wrong format — references chapter shows "No references" if `_parse_bib` returns []

When the rendered output is ready, suggest committing the vault changes (`git add ~/Research-Vault/books/<slug>` from the vault repo if it's tracked) and announce: "Live at https://books.user.com/<slug>/intro".

## Logging

Append outcome to `~/.claude/ecc/skill-outcomes.jsonl` per `skill-outcome-logging` rule:

```bash
mkdir -p ~/.claude/ecc && echo '{"skill":"init-paper-book","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","outcome":"success","session":"'"${CLAUDE_SESSION_ID:-}"'","project":"'"$(basename "$PWD")"'","note":""}' >> ~/.claude/ecc/skill-outcomes.jsonl
```
