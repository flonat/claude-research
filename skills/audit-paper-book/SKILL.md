---
name: audit-paper-book
description: "Use when you need to detect drift between an existing paper-book companion and a revised version of its source paper, then sync the mechanical pieces (new bib entries, new/changed figures) and report the substantive drift (renamed sections, changed numbers, new theorems, new contributions) for the user to triage. Counterpart to /init-paper-book. Read-only by default; --apply flag opts in to mechanical fixes."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: "<slug> [--apply] [--dry-run]"
---

# Audit Paper Book

A book companion goes stale the moment its source paper revises. This skill walks the gap between the paper and the book, classifies each drift item by mechanical-vs-substantive, and produces a single report. With `--apply`, the mechanical drift (new bib entries, new figures) is fixed in place; substantive drift always requires user judgement.

For NEW books, use `/init-paper-book`. This skill never creates a book that doesn't already exist.

## Hard rules

1. **Never edit chapter prose without explicit user approval.** Mechanical fixes touch `references.bib` and `figures/*` only. Section content drift is reported, not fixed.
2. **Numeric changes always block.** If the paper changed a result number (mean gap, accuracy, theorem constant), the book reports it but does NOT auto-update. The user verifies the new number is intentional.
3. **Atlas slug match.** The book's slug must equal the atlas topic filename. Drift in either is a `/init-project-research`-level concern, not this skill's job.
4. **Read-only is the default.** `--apply` is opt-in; without it, this skill produces a report and changes nothing.
5. **Accessibility floor.** The book must remain readable by someone with an undergraduate degree in a quantitative field (linear algebra, probability, basic optimisation/statistics — not necessarily Bayesian methods or domain-specific machinery). Concretely:
    - Every acronym must be expanded at first use within each chapter (e.g. "expected hypervolume improvement (EHVI)").
    - Every display equation gets a one-line plain reading within 2 sentences.
    - No jargon-on-jargon sentences (≥3 specialised terms without inline definition).
    - Intuition before formal definition.

    The audit runs an accessibility check on every chapter (see Phase 2) and reports violations alongside other drift. Violations are reported in the `accessibility` drift bucket (see Phase 3), never auto-fixed. The user decides whether to revise prose or accept the violation.

## When to use

- Camera-ready version of a submitted paper (post-acceptance revisions)
- After a major revision in response to reviewer comments
- When you've added or removed figures from the paper
- When you've added or replaced bib entries
- Before sharing the book URL externally — sanity check that it still matches the paper

## When NOT to use

- The book doesn't exist yet (`/init-paper-book`)
- The paper hasn't actually changed (no point)
- You want a full re-write, not a sync (delete the book + `/init-paper-book` is faster)

## Inputs accepted

```
/audit-paper-book <slug>              # report only, no writes (default)
/audit-paper-book <slug> --apply      # apply mechanical fixes (bib + figures); report substantive drift
/audit-paper-book <slug> --dry-run    # alias for default; explicit no-write
```

## Pre-flight (block-on-fail)

```bash
SLUG="<resolved-slug>"

# 1. Book must exist in vault
[[ -d ~/vault/books/"$SLUG" ]] || die "No book at vault. Use /init-paper-book."

# 2. Registry entry must exist
grep -q "^${SLUG}:" ~/vault/books/index.yaml \
    || die "${SLUG} not in books/index.yaml. Add a registry entry first."

# 3. Atlas topic + project_path must resolve.
#    Hard Rule 4 (from /init-paper-book): book slug MUST equal atlas topic
#    filename. The registry's `atlas_topic:` field is the source of truth — its
#    leaf must match the book slug exactly. Drift here is an existential
#    failure; the book and atlas are no longer the same artefact.
ATLAS_TOPIC_REF=$(awk -v slug="$SLUG" '
    $0 ~ "^"slug":" {in_block=1; next}
    in_block && /^[a-z]/ {in_block=0}
    in_block && /^[[:space:]]+atlas_topic:/ {gsub(/[",'\'']/, ""); print $2; exit}
' ~/vault/books/index.yaml)
ATLAS_TOPIC_LEAF="${ATLAS_TOPIC_REF##*/}"
[[ "$ATLAS_TOPIC_LEAF" == "$SLUG" ]] \
    || die "SLUG DRIFT: book '${SLUG}' points at atlas topic '${ATLAS_TOPIC_LEAF}'. Rename one side so they match (Hard Rule 4). See /init-paper-book SKILL.md."

ATLAS_TOPIC=$(find ~/vault/atlas -name "${SLUG}.md" -type f | head -1)
[[ -n "$ATLAS_TOPIC" ]] \
    || die "No atlas topic file at ~/vault/atlas/*/${SLUG}.md. Either rename the book to match an existing atlas topic, or create the missing topic via /init-project-research."
PROJECT_PATH=$(grep -E "^project_path:" "$ATLAS_TOPIC" | cut -d' ' -f2- | tr -d "'\"")
RR=$(cat ~/.config/task-mgmt/research-root)
[[ -d "$RR/$PROJECT_PATH" ]] || die "project_path in atlas does not resolve."

# 3a. Project-path leaf should also match the slug (warn, don't block — some
#     projects have been renamed historically and only the book + atlas leaf
#     are required to match).
PROJECT_LEAF=$(basename "$PROJECT_PATH")
[[ "$PROJECT_LEAF" == "$SLUG" ]] \
    || warn "PROJECT-DIR DRIFT: project_path leaf '${PROJECT_LEAF}' differs from book slug '${SLUG}'. Not a hard violation but worth aligning if the book is being actively maintained."

# 4. Paper tex + bib must exist
PAPER_DIR=$(ls -d "$RR/$PROJECT_PATH"/paper-* 2>/dev/null | head -1)
PAPER_TEX="$PAPER_DIR/paper/main.tex"; [[ -f "$PAPER_TEX" ]] || PAPER_TEX="$PAPER_DIR/backup/main.tex"
PAPER_BIB=$(find "$PAPER_DIR" -maxdepth 3 -name "*.bib" | head -1)
[[ -f "$PAPER_TEX" ]] || die "No main.tex in paper dir."
[[ -f "$PAPER_BIB" ]] || warn "No bib in paper dir."
```

## Phases

```
Phase 1: Diff inventory    (compare paper assets to book vault)
Phase 2: Accessibility     (acronyms, equation-prose pairing, jargon density)
Phase 3: Classify          (mechanical / numeric / structural / accessibility / new-content)
Phase 4: Apply or report   (--apply: mechanical fixes; otherwise report-only)
Phase 5: Verify            (atlas reload + chapter smoke test if --apply ran)
Phase 6: Rebuild PDF       (mystmd → patched xelatex; soft-fail, --apply only)
```

### Phase 1: Diff inventory

See [`references/phase-1-diff-inventory.md`](references/phase-1-diff-inventory.md) for detailed diff protocols (bibliography, figures, numeric drift, section structure, Overleaf-link transitions, masthead format drift, citation-URL drift).

### Phase 2: Accessibility check

See [`references/phase-2-accessibility.md`](references/phase-2-accessibility.md) for detailed accessibility floor checks (acronym expansion, equation-prose pairing, jargon density, sentence length). This phase always runs (regardless of `--apply`).

### Deterministic implementation — `scripts/batch_audit.py`

Phase 1 + Phase 2's deterministic checks are implemented in `scripts/batch_audit.py`. It reads the book registry, resolves each book's `paper_tex` via the atlas topic's `project_path`, and produces a per-book report at `~/vault/books/<slug>/.audit-report-<date>.md`.

```bash
# Audit all 9 books
~/Task-Management/packages/atlas-workspace/.venv/bin/python \
    ~/.claude/skills/audit-paper-book/scripts/batch_audit.py

# Audit one book
~/Task-Management/packages/atlas-workspace/.venv/bin/python \
    ~/.claude/skills/audit-paper-book/scripts/batch_audit.py <slug>
```

What the script gets right:
- **Bib drift** is computed from `\cite{}` keys in `main.tex` (and any `\input{}`-expanded section files), not from a guessed `.bib` filename. Avoids the common "wrong scratch bib" false positive.
- **Numeric drift** normalises Unicode `±` ↔ LaTeX `\pm`, `%` ↔ `\%`, leading-zero variants (`.91` ↔ `0.91`), and whitespace around `±` before declaring a mismatch. Also skips tokens preceded by `§`, `Section`, `Eq.`, `Fig.`, `Table` (those are cross-references, not numeric claims).
- **Structural drift** parses paper section numbering by walking `\section{}` / `\subsection{}` linearly (handles `\appendix` reset). Extracts `§X.Y` refs from book chapters and flags any that don't resolve.
- **Accessibility** accepts both `Full Form (ACRONYM)` and `ACRONYM (Full Form)` expansion forms, and skips all-caps tokens that only appear inside markdown table rows (column headers).

What still needs human judgement:
- Numeric drift hits may still include formatting edge cases (e.g. paper uses `$\mathbf{2.82 \pm 1.4}$` vs book bare-text version).
- Accessibility allow-list is global; per-domain acronyms (e.g. MOO, MOEA, RVEA, SBX for evolutionary-algorithm books) may need extension. Edit `ACRONYM_ALLOW` at the top of the script.
- Semantic claim-scope check (paper §X.Y says something the book misstates) is **not** implemented here — that's a Phase 3.5-style LLM sub-agent call, not a regex pass.

### Phase 3: Classify

Each drift item lands in one of six buckets:

| Bucket | What it means | --apply behaviour |
|---|---|---|
| **Mechanical** | New bib entries; new figure files; identical-name figures with different content | Auto-applied |
| **Overleaf-link** | Add / remove / update the masthead Overleaf-source line per status | Auto-applied (one-line edit to `intro.md`) |
| **Published-masthead** | Status=Published but intro lacks DOI Source line OR Venue line carries stale marker (R&R, In Press, Accepted, …) | Auto-applied via `regenerate_intro.py --apply` (pulls `doi:` + `publication_date:` from atlas) |
| **Format-convention** | Blockquote masthead → definition-list migration; redundant body H1 stripped; missing required field reported | Migration + H1 strip auto-applied; missing field reported |
| **Citation-URL** | Hand-constructed `/paper/<key>` link inside chapter prose | Reported with chapter+line; never auto-applied (replacement requires choosing cite-t vs cite-p form) |
| **Numeric** | A number in the book no longer appears in the paper, or vice versa | Reported, never auto-applied |
| **Structural** | Section heading renamed; new section added in paper; old section removed | Reported with suggested action ("Update `method.md` to mention §4.5 on the new selection rule") |
| **Accessibility** | Acronym not expanded; display equation with no prose reading; jargon-dense sentence | Reported with chapter+line; never auto-applied (prose edits require user judgement) |
| **New content** | Paper has a new theorem, definition, or claim with no echo in any book chapter | Reported with suggested chapter target |

**Overleaf-link is mechanical** because the rule is deterministic: status ∈ accepted-set → remove; status in-flight + link in atlas → ensure present; URL changed → propagate. No editorial judgement.

**Published-masthead is mechanical** because the transformation is fully driven by atlas data: when `outputs[0].status` starts with `Published`, `regenerate_intro.py` pulls `doi:` and `publication_date:` from the same atlas entry and emits (a) a Venue line `*<venue>* (<year>) — Published online <date>` and (b) a Source line `[📄 DOI: <doi> ↗](https://doi.org/<doi>)` in place of the Overleaf line. No editorial judgement — the canonical form is determined by the atlas state.

**Format-convention items are mechanical** because the transformations are deterministic: blockquote masthead → definition-list (preserving field values), body H1 → strip the line. They never touch claims or numbers, only structural markup.

### Phase 4: Apply (only with --apply) or report

See [`references/phase-4-apply-logic.md`](references/phase-4-apply-logic.md) for apply logic (bib copy, figure replacement, masthead updates, format-convention migrations). Write the audit report to `~/vault/books/<slug>/.audit-report-YYYY-MM-DD.md` so the user has a record of what was applied + what's still pending.

### Phase 5: Verify (if --apply ran OR --visual-check passed in)

See [`references/phase-5-verify-smoke-tests.md`](references/phase-5-verify-smoke-tests.md) for HTTP smoke-test and mandatory Playwright visual verification logic.

### Phase 6: Rebuild PDF companion (soft-fail; --apply only)

See [`references/phase-6-pdf-rebuild.md`](references/phase-6-pdf-rebuild.md). Runs `bash ~/.claude/skills/init-paper-book/scripts/build-book-pdf.sh <slug>` if `--apply` was passed and Phase 4 actually changed chapter files. Skips silently if `mystmd` is not on PATH or `myst.yml` is missing (no audit-time file creation beyond the build pipeline's own bootstrap). Warns on build error.

## Report format

See [`references/report-format-template.md`](references/report-format-template.md) for canonical audit report structure (summary table, mechanical fixes, drift buckets, next actions).

## Anti-patterns

- **Auto-applying numeric changes.** If a number changed, the user must decide whether the book's old explanation still applies. Auto-update silently corrupts the book.
- **Auto-renaming chapters.** Chapter renames cascade through the registry, atlas, and any external links. Always user-triaged.
- **Skipping the report when applying.** Even if `--apply` succeeds, the report logs what was changed (audit trail).

## Logging

Append outcome to `~/.claude/ecc/skill-outcomes.jsonl`:

```bash
mkdir -p ~/.claude/ecc && echo '{"skill":"audit-paper-book","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","outcome":"success","session":"'"${CLAUDE_SESSION_ID:-}"'","project":"'"$(basename "$PWD")"'","note":""}' >> ~/.claude/ecc/skill-outcomes.jsonl
```
