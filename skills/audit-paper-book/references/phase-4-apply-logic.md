# Phase 4: Apply (only with --apply) or Report

Without `--apply`, write the report to `~/vault/books/<slug>/.audit-report-YYYY-MM-DD.md` and stop.

With `--apply`:

```bash
# Bib: copy new entries from paper to book
cp "$PAPER_BIB" ~/vault/books/"$SLUG"/references.bib

# Figures: copy added figures + replace changed ones
for fig in $figs_paper_only $figs_changed; do
    cp "$fig" ~/vault/books/"$SLUG"/figures/
done

# Overleaf-link masthead: add / remove / update the Overleaf-source line in intro.md.
# Status set decides direction:
#   in-flight = {Idea, Drafting, Submitted, Under Review, R&R, Revising}
#   terminal  = {Accepted, In Press, Camera-ready, Published, Withdrawn}
# Pseudocode (the actual edit is a one-line sed/Edit in intro.md):
#   if status ∈ terminal AND intro has Overleaf line     → strip it
#   if status ∈ in-flight AND atlas has overleaf_link
#       AND intro lacks Overleaf line                    → insert it
#   if status ∈ in-flight AND URL drifted                → replace it

# Format-convention migrations (deterministic, auto-applied):
#
#  (a) Blockquote masthead → definition-list. If intro.md starts with a
#      `> **Paper.** ...\n> **Authors.** ...` block, parse the field/value
#      pairs (Paper/Authors/Venue/Preprint/Source/Status), discard the
#      redundant `Paper` field (the template's H1 covers it), and emit a
#      definition-list masthead in the canonical order:
#        Authors / Venue / Preprint / Source / Status
#      Wrap the lede sentence above the dl if one exists. Preserve all
#      field values verbatim — only the markup changes.
#
#  (b) Redundant body H1 → strip. For every chapter file, if line 1 of
#      the body (post-frontmatter) is `# <something>`, delete that line
#      and any single blank line that follows. The page-title H1 from
#      index.yaml already supplies the heading; a body H1 produces a
#      duplicate.
#
# Published-masthead refresh (auto-applied via regenerate script):
#
#  (e) Published-masthead drift. When atlas `outputs[0].status` starts
#      with `Published` and either (i) atlas has a `doi:` field that's
#      not referenced anywhere in intro.md, or (ii) the Venue line
#      carries a stale status marker without "Published", regenerate
#      via:
#        ~/Task-Management/packages/atlas-workspace/.venv/bin/python \
#          ~/.claude/skills/init-paper-book/scripts/regenerate_intro.py \
#          <slug> --apply
#      This emits the canonical Published-state masthead pulling
#      `venue`, `doi`, `publication_date` from atlas `outputs[0]`. Any
#      hand-written content below the `<!-- preserve-below: ... -->`
#      marker is re-appended verbatim — only the masthead is touched.
#
# Format-convention reports (not auto-applied):
#
#  (c) Missing required masthead field. Intro masthead lacks `Authors`
#      or `Venue` → report; user must add (we don't fabricate field
#      values).
#  (d) Hand-constructed citation URL in chapter prose. Any
#      `](https?://atlas.example.com/paper/<Key>)` or `](/paper/<Key>)`
#      inside a non-references chapter → report with chapter:line and
#      the suggested replacement `{cite:t}\`<Key>\``. Not auto-applied
#      because cite:t vs cite:p selection requires context judgement.
```

Write the same audit report so the user has a record of what was applied + what's still pending.
