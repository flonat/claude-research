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
[[ -d ~/Research-Vault/books/"$SLUG" ]] || die "No book at vault. Use /init-paper-book."

# 2. Registry entry must exist
grep -q "^${SLUG}:" ~/Research-Vault/books/index.yaml \
    || die "${SLUG} not in books/index.yaml. Add a registry entry first."

# 3. Atlas topic + project_path must resolve
ATLAS_TOPIC=$(find ~/Research-Vault/atlas -name "${SLUG}.md" -type f | head -1)
[[ -n "$ATLAS_TOPIC" ]] || die "No atlas topic for ${SLUG}."
PROJECT_PATH=$(grep -E "^project_path:" "$ATLAS_TOPIC" | cut -d' ' -f2- | tr -d "'\"")
RR=$(cat ~/.config/task-mgmt/research-root)
[[ -d "$RR/$PROJECT_PATH" ]] || die "project_path in atlas does not resolve."

# 4. Paper tex + bib must exist
PAPER_DIR=$(ls -d "$RR/$PROJECT_PATH"/paper-* 2>/dev/null | head -1)
PAPER_TEX="$PAPER_DIR/paper/main.tex"; [[ -f "$PAPER_TEX" ]] || PAPER_TEX="$PAPER_DIR/backup/main.tex"
PAPER_BIB=$(find "$PAPER_DIR" -maxdepth 3 -name "*.bib" | head -1)
[[ -f "$PAPER_TEX" ]] || die "No main.tex in paper dir."
[[ -f "$PAPER_BIB" ]] || warn "No bib in paper dir."
```

## Phases

```
Phase 1: Diff inventory   (compare paper assets to book vault)
Phase 2: Classify         (mechanical / numeric / structural / new-content)
Phase 3: Apply or report  (--apply: mechanical fixes; otherwise report-only)
Phase 4: Verify           (atlas reload + chapter smoke test if --apply ran)
```

### Phase 1: Diff inventory

Build four diffs.

**Bibliography diff:**
```bash
PAPER_BIB="$PAPER_DIR/.../references.bib"
BOOK_BIB=~/Research-Vault/books/"$SLUG"/references.bib
diff <(grep -oE "@\w+\{[^,]+," "$PAPER_BIB" | sort) \
     <(grep -oE "@\w+\{[^,]+," "$BOOK_BIB" | sort)
# Capture: bib_added, bib_removed, bib_unchanged
```

**Figures diff:**
- Walk `\includegraphics{...}` paths in paper tex.
- Resolve to `<project>/figures/...png` or `<project>/output/figures/...png`.
- Compare against `~/Research-Vault/books/<slug>/figures/`.
- Capture: figs_paper_only, figs_book_only, figs_changed (mtime / size differs).

**Numeric drift:**
- Extract numeric claims from paper abstract + result tables (regex: ranges like `0.85`, `2.82 ± 1.4`, `93.7%`).
- Grep each book chapter for the same numeric strings.
- Capture: numbers_in_book_not_paper, numbers_in_paper_not_book.

**Section structure drift:**
- Extract `\section{...}` and `\subsection{...}` from paper tex.
- Compare against the chapter outline declared in `~/Research-Vault/books/index.yaml` for this slug.
- Capture: paper_sections_added, paper_sections_renamed, book_chapters_orphaned.

**Overleaf-link drift (status transitions):**
- Read the atlas topic's `outputs[].status` for the paper-path that matches this book.
- Read the book's `intro.md` masthead — does it currently contain a `https://www.overleaf.com/...` link?
- Capture cases:
  - Status is `{Accepted, Camera-ready, Published, Withdrawn}` AND book intro has Overleaf link → **propose removal** (paper accepted; Overleaf source is no longer the canonical artefact).
  - Status is in-flight (`{Idea, Drafting, Submitted, Under Review, R&R, Revising}`) AND atlas has `overleaf_link:` AND book intro lacks the link → **propose addition**.
  - Atlas `overleaf_link:` URL has changed AND book intro shows the old URL → **propose update**.

### Phase 2: Classify

Each drift item lands in one of four buckets:

| Bucket | What it means | --apply behaviour |
|---|---|---|
| **Mechanical** | New bib entries; new figure files; identical-name figures with different content | Auto-applied |
| **Overleaf-link** | Add / remove / update the masthead Overleaf-source line per status | Auto-applied (one-line edit to `intro.md`) |
| **Numeric** | A number in the book no longer appears in the paper, or vice versa | Reported, never auto-applied |
| **Structural** | Section heading renamed; new section added in paper; old section removed | Reported with suggested action ("Update `method.md` to mention §4.5 on the new selection rule") |
| **New content** | Paper has a new theorem, definition, or claim with no echo in any book chapter | Reported with suggested chapter target |

**Overleaf-link is mechanical** because the rule is deterministic: status ∈ accepted-set → remove; status in-flight + link in atlas → ensure present; URL changed → propagate. No editorial judgement.

### Phase 3: Apply (only with --apply) or report

Without `--apply`, write the report to `~/Research-Vault/books/<slug>/.audit-report-YYYY-MM-DD.md` and stop.

With `--apply`:

```bash
# Bib: copy new entries from paper to book
cp "$PAPER_BIB" ~/Research-Vault/books/"$SLUG"/references.bib

# Figures: copy added figures + replace changed ones
for fig in $figs_paper_only $figs_changed; do
    cp "$fig" ~/Research-Vault/books/"$SLUG"/figures/
done

# Overleaf-link masthead: add / remove / update the Overleaf-source line in intro.md.
# Status set decides direction:
#   in-flight = {Idea, Drafting, Submitted, Under Review, R&R, Revising}
#   terminal  = {Accepted, Camera-ready, Published, Withdrawn}
# Pseudocode (the actual edit is a one-line sed/Edit in intro.md):
#   if status ∈ terminal AND intro has Overleaf line     → strip it
#   if status ∈ in-flight AND atlas has overleaf_link
#       AND intro lacks Overleaf line                    → insert it
#   if status ∈ in-flight AND URL drifted                → replace it
```

Write the same audit report so the user has a record of what was applied + what's still pending.

### Phase 4: Verify (if --apply ran)

```bash
# Reload atlas (Mac Mini only)
launchctl bootout gui/$(id -u)/com.user.atlas
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.atlas.plist
sleep 4

# Smoke-test the references chapter (catches bib parse errors)
curl -s --max-time 8 -o /dev/null -w "references: %{http_code}\n" \
    "http://localhost:8770/book/${SLUG}/references"

# Spot-check that any new figure URL serves
for fig in $figs_paper_only; do
    name=$(basename "$fig")
    curl -s --max-time 5 -o /dev/null -w "figures/${name}: %{http_code}\n" \
        "http://localhost:8770/book/${SLUG}/figures/${name}"
done
```

## Report format

`~/Research-Vault/books/<slug>/.audit-report-YYYY-MM-DD.md`:

```markdown
# Audit report — <slug>

**Date:** YYYY-MM-DD
**Mode:** report-only | applied
**Paper revision:** <git-sha-or-mtime of paper tex>
**Book last touched:** <git-sha-or-mtime of book vault dir>

## Summary

| Bucket | Count | Status |
|---|---:|---|
| Mechanical (bib + figures) | N | applied / pending |
| Overleaf-link (masthead) | N | applied / pending |
| Numeric | N | pending — user triage |
| Structural | N | pending — user triage |
| New content | N | pending — user triage |

## Mechanical fixes

### New bib entries (N)
- `Smith2026-xx` — Smith, J. (2026). Title. *Journal*, 12(3). doi:10.xxxx
- ...

### New / changed figures (N)
- `figures/new_plot.png` — added (paper §5)
- `figures/budget_vs_harm.png` — content changed (mtime newer)
- ...

## Numeric drift

| Where in book | Old number | New paper number | Action |
|---|---|---|---|
| `results.md` line 42 | 2.82 ± 1.4 | 2.78 ± 1.2 | Update `results.md` to match paper §5.1 |
| ... |

## Structural drift

| Paper change | Affected chapter | Suggested action |
|---|---|---|
| §4.5 added "Cost-aware selection" | `method.md` | Add a section after the VOI rule |
| §6 renamed to "Limitations and ethics" | `limitations.md` | Update chapter title + opening |

## New content (no echo in book)

| Paper element | Book gap | Suggested action |
|---|---|---|
| Theorem 3 (paper §3.4) | No mention in `method.md` | Add a callout/short subsection summarising the result |

## Next actions

1. (optional) Re-run with `--apply` to take the mechanical fixes.
2. Triage numeric drift in `results.md`.
3. Add a sub-section in `method.md` for Theorem 3.
4. (optional) Run `/init-paper-book <slug>` only if the paper has restructured drastically — usually `audit` is faster.
```

## Anti-patterns

- **Auto-applying numeric changes.** If a number changed, the user must decide whether the book's old explanation still applies. Auto-update silently corrupts the book.
- **Auto-renaming chapters.** Chapter renames cascade through the registry, atlas, and any external links. Always user-triaged.
- **Skipping the report when applying.** Even if `--apply` succeeds, the report logs what was changed (audit trail).

## Logging

Append outcome to `~/.claude/ecc/skill-outcomes.jsonl`:

```bash
mkdir -p ~/.claude/ecc && echo '{"skill":"audit-paper-book","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","outcome":"success","session":"'"${CLAUDE_SESSION_ID:-}"'","project":"'"$(basename "$PWD")"'","note":""}' >> ~/.claude/ecc/skill-outcomes.jsonl
```
