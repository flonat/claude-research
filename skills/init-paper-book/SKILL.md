---
name: init-paper-book
description: "Use when you need to scaffold a NEW educational companion book for a LaTeX paper. Reads the paper, drafts 8 substantive chapters into the vault at ~/vault/books/{slug}/, copies bib + figures, registers the book, and verifies atlas serves it. Source-of-truth is the paper PDF/tex; the book is a reading companion, never a re-statement of new claims. For syncing an existing book to a paper revision, use /audit-paper-book."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, Task
argument-hint: "<project-path-or-slug> [--dry-run]"
---

# Init Paper Book

Scaffold a runnable, browsable companion to a LaTeX paper. The book lives in the vault, atlas renders it, and direct URLs at `books.example.com/<slug>/<chapter>` make it shareable. There is **no separate build pipeline** — atlas is the renderer.

For syncing an existing book to a paper revision, use `/audit-paper-book` instead.

## Hard rules

### Existential — block writing

1. **No new claims.** The book may rephrase, scaffold, and explain, but never introduce results not in the paper. Numbers and theorems trace to the paper.
2. **Numeric invariant.** Every numeric claim in the book must match the paper. Mismatches block.
3. **Paper is canonical.** Source-of-truth is the paper PDF/tex. Edits to the book do not edit the paper. Edits to the paper require `/audit-paper-book` to propagate.
4. **Atlas slug match.** Book slug must equal atlas topic filename (lowercase, hyphenated). The project directory leaf under the research root should also match (warn, don't block). If any of these three disagree, stop and prompt — alignment is required at the source, not a workaround in the book. `/audit-paper-book` pre-flight aborts on book-slug ⇄ atlas-filename drift; the regenerate script aborts at runtime with "SLUG DRIFT".

### Format — catch in review

5. **Vault location.** Book chapters live at `~/vault/books/<slug>/`. Never in the project tree (atlas runs under launchd and File Provider paths hang).
6. **Registry entry.** `~/vault/books/index.yaml` must list the slug, title, atlas-topic pointer, bibliography file, and explicit chapter order.
7. **Eight chapters.** Default skeleton: `intro · background · setup · method · results · limitations · extend · appendix`. The `references` chapter is auto-appended when `bibliography:` is set.
8. **No-index by default.** atlas's base.html injects `noindex,nofollow` for book chapters. Books are direct-link-only — no discovery surface.
9. **Section headings descriptive, never numbered.** Use `## The selection rule`, not `## 4.5 The selection rule`. Cross-references to the paper carry the paper's own numbering inline.
10. **Mystmd-style callouts.** Use `` ```{important} ``, `` ```{tip} ``, `` ```{note} ``, `` ```{warning} ``, `` ```{caution} ``, `` ```{seealso} ``. Atlas's directive converter handles these. Pandoc-style `::: {.callout-X}` does NOT render — convert if you find it in source material.
11. **Figure paths are vault-relative.** `figures/<filename>` resolves to `~/vault/books/<slug>/figures/<filename>` served by atlas's `/book/<slug>/figures/{filename:path}` route.
12. **Citations resolve in-book first.** Mystmd `{cite:t}\`Key\`` converts to `[Key](/book/<slug>/references#ref-Key)` when `Key` is present in the book's local `references.bib` (anchors to the matching `<li id="ref-Key">` card in the auto-rendered `references` chapter). For keys not in the local bib, the converter falls back to `https://atlas.example.com/paper/Key` (the global Paperpile-backed route, behind CF Access). Don't construct citation URLs by hand.
13. **Affiliations from atlas.** Author affiliations come from the atlas topic's `institution:` field. Never hardcode.
14. **Accessibility floor.** Chapters must be readable by someone with an undergraduate degree in a quantitative field (linear algebra, probability, basic optimisation/statistics — not necessarily Bayesian methods or domain-specific machinery). Concretely:
    - Introduce every non-elementary notation/term inline at first use (e.g. "Gaussian process (GP) — a distribution over functions where any finite set of evaluations is jointly Gaussian").
    - State the intuition before the formal definition.
    - Avoid acronyms without expansion at first use within each chapter (e.g. "expected hypervolume improvement (EHVI)", not just "EHVI").
    - Math is allowed but never carries the whole load — every display equation gets a one-line plain reading.
    - Avoid jargon-on-jargon: don't define one undergraduate-opaque term using two others.

    The Phase 4 verifier checks this floor (see below). Each drafting sub-agent prompt in Phase 3 MUST include the accessibility floor verbatim.

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
/init-paper-book <project-path>          # full path to project dir, e.g. ~/Research/<theme>/<project-slug>
/init-paper-book <slug>                  # atlas slug; resolved via atlas topic file's project_path
/init-paper-book <slug> --dry-run        # plan only, no writes
/init-paper-book <slug> --autonomous     # or -y: 4 phases end-to-end, no inter-phase pauses (see Autonomy below)
```

## Autonomy

Per the global `--autonomous` / `-y` convention in `~/.claude/rules/phased-work.md` § "Autonomy flag convention". When set:

- **No mid-run `AskUserQuestion`** — every choice point uses the recommended default and logs the decision (chapter scope decisions, screenshot mode, atlas-reload trigger).
- **No inter-phase confirmation** — Phases 1 → 5 chain without stopping for `continue`, EXCEPT Phase 4 (verification) which can hard-block Phase 5 on any verifier failure (see "Hard correctness gates" below).
- **Phase 3 sub-agents still fire in parallel** (chapter drafting); they each carry the standard forbid-list (no git, no build outside the chapter file).
- **Phase 4 verifier runs mandatorily** — even in autonomous mode, the verifier dispatch and report are not skipped. Any verifier failure (numeric drift, missing citation key, claim outside paper scope, accessibility violation) BLOCKS Phase 5 and exits with a clear remediation list.
- **Pre-flight block-on-fail still applies** — missing atlas topic / project dir / `main.tex` aborts the run with a clear error (this is a correctness gate, not a phase pause).
- **Phase 5 register + smoke-test still runs** if and only if Phase 4 passed — registry entry, atlas reload, smoke probe; failures are reported at end, not blocked mid-run.
- **Single end-of-run report** as the only mandatory user-facing output — lists chapters created, verifier findings, registry registration, smoke-test results, any non-fatal warnings.

Hard correctness gates that still fire even with `--autonomous` (any of these aborts the run):

- Pre-flight checks 1–5 (atlas, project, paper-tex, bib, vault-not-already-present)
- Sub-agent forbid-list (Phase 3 drafters can't touch git, can't run latexmk, can't edit outside `~/vault/books/<slug>/`)
- **Phase 4 verifier failure** — any one of: numeric drift, missing citation key, claim outside paper scope, accessibility-floor violation (see Phase 4)
- After-flight verifier (registry entry exists, atlas serves the book URL)

Recommended invocations:

```
/init-paper-book article40-access-as-mechanism --autonomous
/init-paper-book -y article40-access-as-mechanism
```

Use `--dry-run` first if you want to see the chapter plan before letting it run.

## Pre-flight (block-on-fail)

```bash
SLUG="<resolved-slug>"

# 1. Atlas topic exists
find ~/vault/atlas -name "${SLUG}.md" -type f | head -1
[[ $? == 0 ]] || die "No atlas topic for ${SLUG}. Run /init-project-research first."

# 2. Project directory exists
PROJECT_PATH=$(grep -E "^project_path:" "$ATLAS_TOPIC" | cut -d' ' -f2- | tr -d "'\"")
RR=$(cat ~/.config/task-mgmt/research-root)
[[ -d "$RR/$PROJECT_PATH" ]] || die "project_path in atlas does not resolve."

# 3. Paper directory + tex file exist
PAPER_DIR=$(ls -d "$RR/$PROJECT_PATH"/paper-* 2>/dev/null | head -1)
PAPER_TEX="$PAPER_DIR/paper/main.tex"
[[ -f "$PAPER_TEX" ]] || PAPER_TEX="$PAPER_DIR/backup/main.tex"
# If neither default exists, ask the user once at setup what the canonical
# .tex filename is. Some papers (ACM templates etc.) name the file after the
# venue (e.g. `gecco2026.tex`) rather than main.tex. Record the answer as
# `paper_tex: <path-relative-to-project-root>` in the registry entry — the
# audit script reads it from there on every subsequent run. Do NOT try to
# auto-guess; ambiguity is a setup-time question, not a runtime one.
if [[ ! -f "$PAPER_TEX" ]]; then
    # AskUserQuestion: "What's the canonical .tex filename for this paper?"
    # Example answer: paper-acm-gecco/paper/gecco2026.tex
    # On answer → write `paper_tex: <answer>` into the registry entry below.
    die "No main.tex in $PAPER_DIR/{paper,backup}/. Ask the user for the paper_tex path and store it in the registry."
fi

# 4. Bibliography exists
BIB=$(find "$PAPER_DIR" -maxdepth 3 -name "*.bib" | head -1)
[[ -f "$BIB" ]] || warn "No .bib found — references chapter will be empty."

# 5. Vault book dir doesn't already exist
[[ -d ~/vault/books/"$SLUG" ]] && die "Book already exists. Use /audit-paper-book to sync."
```

## Phases

```
Phase 1: Read paper + plan        (direct read of paper tex + atlas topic)
Phase 2: Scaffold vault           (mkdir, copy bib + figures)
Phase 3: Draft chapters           (mixed — sub-agents for content-heavy chapters)
Phase 4: Verify chapters          (read-only sub-agent; HARD GATES Phase 5)
Phase 5: Register + smoke-test    (registry entry, atlas reload, smoke probe)
Phase 6: Build PDF companion      (mystmd → patched xelatex; soft-fail)
```

### Phase 1: Read + plan

See [`references/phase-1-read-plan.md`](references/phase-1-read-plan.md).

### Phase 2: Scaffold

See [`references/phase-2-scaffold.md`](references/phase-2-scaffold.md).

### Phase 3: Draft chapters

See [`references/phase-3-chapter-scaffolding.md`](references/phase-3-chapter-scaffolding.md) for chapter table and requirements.

**Intro masthead format.** See [`references/intro-masthead-format.md`](references/intro-masthead-format.md) for definition-list pattern, preserve marker, regenerate commands, and Overleaf-link handling.

### Phase 4: Verify chapters (MANDATORY; hard-gates Phase 5)

See [`references/phase-4-verify-chapters.md`](references/phase-4-verify-chapters.md) for deterministic checks, semantic checks, and hard-gate rules.

### Phase 5: Register + smoke-test

See [`references/phase-5-register.md`](references/phase-5-register.md) for registry append, atlas reload, HTTP smoke test, and Playwright visual check.

### Phase 6: Build PDF companion (soft-fail)

See [`references/phase-6-pdf-build.md`](references/phase-6-pdf-build.md). Runs `bash scripts/build-book-pdf.sh <slug>` to produce `~/vault/books/<slug>/exports/<slug>.pdf` via a `myst build --tex` → patch → `latexmk -xelatex` pipeline. Skips silently if `mystmd` is not on PATH; warns on build error but does not block — atlas HTML rendering remains the canonical surface.

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

When the rendered output is ready, suggest committing the vault changes (`git add ~/vault/books/<slug>` from the vault repo if it's tracked) and announce: "Live at https://books.example.com/<slug>" — the landing URL renders an **editorial cover/frontispiece**: an accent spine, the title, "Companion to <paper>", authors + venue/status/institution **chips**, a numbered contents list with **per-chapter and total reading time** (auto-computed from word count in `book.get_book`, no authoring action needed), and an action row — **Start reading →** · **⤓ Download PDF** · **View atlas topic ↗**. Chapters render running prose at a serif reading measure with a scroll-progress bar and prev/next cards (all in the atlas `--fn-*` tokens, so dark mode holds). The **⤓ Download PDF** action serves the Phase-6 build at `~/vault/books/<slug>/exports/<slug>.pdf` (one-click, real xelatex typesetting), and falls back to a browser-printable `/book/<slug>/print` view when no PDF has been built — so keep Phase 6 in the loop to keep the download fresh.

## Logging

Append outcome to `~/.claude/ecc/skill-outcomes.jsonl` per `skill-outcome-logging` rule:

```bash
mkdir -p ~/.claude/ecc && echo '{"skill":"init-paper-book","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","outcome":"success","session":"'"${CLAUDE_SESSION_ID:-}"'","project":"'"$(basename "$PWD")"'","note":""}' >> ~/.claude/ecc/skill-outcomes.jsonl
```
