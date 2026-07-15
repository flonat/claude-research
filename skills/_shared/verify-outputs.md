# Shared: Verify Claimed Outputs (Output Guard)

## Purpose

Prevent the "hallucinated outputs" failure class where a skill commits a log
claiming files were written but the files never existed. Specifically triggered
by the `literature --deep` run on `example-project-a`
(2026-04-18), where `references.bib`, `main.tex`, and `synthesis.md` were
reported as written but only the log was committed.

## How a skill uses this

Every file-producing skill must, just before its auto-commit step:

1. **Emit a manifest** listing the files it believes it wrote:

   ```bash
   MANIFEST="$PROJECT_ROOT/.claude/state/outputs-manifest-$(date -u +%Y%m%dT%H%M%SZ).json"
   mkdir -p "$(dirname "$MANIFEST")"
   cat > "$MANIFEST" <<'EOF'
   {
     "skill": "literature",
     "session": "<CLAUDE_SESSION_ID>",
     "project": "<project-slug>",
     "claimed_outputs": [
       "docs/literature-review/literature_summary.bib",
       "docs/literature-review/literature_summary.md",
       "paper-neurips/paper/references.bib"
     ]
   }
   EOF
   ```

2. **Invoke the verifier** before `git commit`:

   ```bash
   uv run python "<skills-root>/_shared/verify_outputs.py" \
       --manifest "$MANIFEST" \
       --project-root "$PROJECT_ROOT"
   ```

3. **Abort on non-zero exit** — do not commit. The verifier already appended an
   `error` entry to `~/.local/state/ai-workflows/skill-outcomes.jsonl`, so the
   shared skill-health dashboard will surface the failure.

## Skills that must integrate this

| Skill | Phase to emit manifest |
|---|---|
| `literature` | End of Phase 6d, before commit in Phase 6e |
| `latex` / `latex-health-check` | After compile passes |
| `replication-package` | After archive creation |
| `bib-filter` / `bib-parse` / `bib-coverage` | After writing the curated .bib |
| `figure` | After figure file written |

Skills that are read-only or emit no files (`proofread`, `bib-validate`, most
audit skills, `review`) do **not** need this.

## What counts as a "claimed output"

- Only files that the skill itself wrote in this invocation.
- Paths relative to `$PROJECT_ROOT` (not absolute).
- Include derived outputs (e.g., the compiled PDF if the skill is responsible
  for producing it), but not pre-existing inputs.

## Testing the guard

```bash
# Deliberately break one claimed output mid-run:
rm -f "$PROJECT_ROOT/docs/literature-review/literature_summary.bib"

# Then run the guard:
uv run python <skills-root>/_shared/verify_outputs.py \
    --manifest "$MANIFEST" --project-root "$PROJECT_ROOT"
# Expect exit 1 and a clear "missing" message.
```
