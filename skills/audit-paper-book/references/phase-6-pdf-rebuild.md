# Phase 6: Rebuild PDF companion (soft-fail; --apply only)

After Phase 5 verifies the atlas reload + smoke tests, rebuild the PDF companion if chapter content actually changed in Phase 4. The build script is shared with `/init-paper-book` — single source of truth.

## When this phase runs

- `--apply` was passed AND Phase 4 made changes to chapter files
- `mystmd` is on PATH (else: skip silently)
- `myst.yml` exists in the book dir (else: skip — audit never creates new infrastructure files)

If any of these are false, log a one-liner and continue. Audit is non-destructive by design; PDF rebuild is purely opportunistic.

## Invocation

```bash
bash ~/.claude/skills/init-paper-book/scripts/build-book-pdf.sh <slug>
```

Output: `~/vault/books/<slug>/exports/<slug>.pdf`.

The script's bootstrap logic CAN write a `myst.yml` if missing — but during audit we suppress this by checking for `myst.yml` first and only invoking the script when it exists. Reasoning: scaffolding new infrastructure is `/init-paper-book`'s job, not audit's.

## Pipeline details

See [`init-paper-book/references/phase-6-pdf-build.md`](../../init-paper-book/references/phase-6-pdf-build.md) for the full pipeline description (font swap, section→chapter promotion, title-page composition, dependencies, publication-info sourcing).

## Soft-fail contract

- Missing `mystmd` → log "Phase 6 skipped (mystmd not installed)", continue
- Missing `myst.yml` → log "Phase 6 skipped (no myst.yml; run /init-paper-book to scaffold)", continue
- `latexmk` non-zero exit → warn with log path, continue
- No chapter content changes detected in Phase 4 → log "Phase 6 skipped (no chapter changes)", continue

## Audit-time considerations

- The PDF is a derived artifact. If the audit found numeric drift in a chapter and `--apply` did NOT touch it (numeric drift is never auto-applied), the PDF will still rebuild — but it'll reflect whatever's currently in the chapter source, not whatever the audit thinks the correct values are. Numeric drift remediation is a user-driven follow-up.
- Cross-reference warnings (e.g. `#sec-foo` not found) raised by mystmd at build time should be added to the audit report under the `structural` bucket if they weren't already, so the user knows the PDF has stale section refs.
