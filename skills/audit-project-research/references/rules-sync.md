# Phase 2.7: Rules Hygiene (Read-Only)

> Detailed check for `/audit-project-research` Phase 2.7. **This phase is read-only.** It never copies global rules into projects.

## Philosophy

Global rules in `~/.claude/rules/` already apply to every session, regardless of project. **Never copy them into `<project>/.claude/rules/`** — duplication causes:

- **Drift**: project copies silently diverge from global source
- **Context bloat**: every duplicated rule loads twice per session
- **No added value**: globals are already loaded by the harness

`<project>/.claude/rules/` should contain **only genuinely project-specific rules** (e.g. project-unique LaTeX conventions, data handling quirks).

## Source of truth

The global rules in `~/.claude/rules/`. List them at runtime:

```bash
ls ~/.claude/rules/*.md
```

## Comparison logic (read-only)

1. If `<project>/.claude/rules/` does not exist → no action, report `not present (OK)`
2. If it exists, compare each file against the global version:

| Condition | Classification | Reported action |
|-----------|---------------|-----------------|
| In project, byte-identical to global | **Redundant** | Flag for removal |
| In project, differs from global | **Fork** | Flag — project may be overriding global intentionally |
| In project only (no global counterpart) | **Project-specific** | Leave alone, no action |

## Detection script

```bash
if [ ! -d "<project>/.claude/rules" ]; then
  echo "No .claude/rules/ — OK"
  exit 0
fi

redundant=()
forks=()
specific=()

for rule in "<project>/.claude/rules/"*.md; do
  name=$(basename "$rule")
  global="$HOME/.claude/rules/$name"
  if [ ! -f "$global" ]; then
    specific+=("$name")
  elif diff -q "$rule" "$global" > /dev/null 2>&1; then
    redundant+=("$name")
  else
    forks+=("$name")
  fi
done
```

## Report format

For the Phase 9 report, add a `Rules Hygiene:` section:

```
Rules Hygiene:
  .claude/rules/             9 files (5 redundant, 0 forks, 4 project-specific)
  check-hostname.md          REDUNDANT — identical to ~/.claude/rules/ — safe to delete
  dropbox-paths.md           REDUNDANT — identical to ~/.claude/rules/ — safe to delete
  latex-outdir.md            project-specific — keep
  ignore-agents-md.md        project-specific — keep
```

## Action

The audit **flags** findings. It does **not** modify the project. Removing redundant rules is a separate, explicit user decision — not an auto-sync.

If the user wants to clean up, offer:

```bash
# Batch-clean byte-identical duplicates across all projects
for proj_rules in $(find "$RESEARCH_ROOT" -maxdepth 4 -type d -name rules -path "*/.claude/rules"); do
  for rule in "$proj_rules"/*.md; do
    name=$(basename "$rule")
    global="$HOME/.claude/rules/$name"
    if [ -f "$global" ] && diff -q "$rule" "$global" > /dev/null 2>&1; then
      rm "$rule"
    fi
  done
done
```

## Edge cases

- **No `.claude/rules/` directory:** Report OK. Do not create it.
- **Empty `.claude/rules/` directory:** Report OK. Do not flag as Missing or Degraded. An empty directory means the project relies entirely on global rules, which is the default and correct state. Never recommend deleting the empty directory either — it's harmless and may get populated later.
- **Symlinked `.claude/rules/`:** Skip entirely. Report as Info.
- **Forks:** Always report, never modify. A fork may be intentional (project overrides a global rule for local reasons) or accidental (project copy is stale). Only the user can decide.
