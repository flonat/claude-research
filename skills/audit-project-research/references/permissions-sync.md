# Phase 2.5: Permissions Audit (Read-Only)

> Detailed check for `/audit-project-research` Phase 2.5. **This phase is read-only.** It flags missing permissions and recommends `/sync-permissions` for the actual merge.

Compares the project's `.claude/settings.local.json` against the global `~/.claude/settings.json` to find permissions that are present globally but missing locally.

## Source of truth

The global permissions in `~/.claude/settings.json` under `permissions.allow` and `permissions.deny`.

## Comparison logic

1. Read global settings: `jq '.permissions.allow // []' ~/.claude/settings.json`.
2. Check if `<project>/.claude/settings.local.json` exists.
3. If it doesn't exist → flag as Missing with remediation: *"Run `/sync-permissions` to seed local settings from global."*
4. If it exists → classify each global permission:

| Condition | Classification | Severity |
|-----------|---------------|----------|
| In global, not in local | **Missing** | Degraded |
| In both | **Synced** | — |
| In local, not in global | **Project-specific** | Info |

## Read-only check

```bash
# Read-only diff — never writes
diff <(jq -r '.permissions.allow[]?' ~/.claude/settings.json | sort) \
     <(jq -r '.permissions.allow[]?' "<project>/.claude/settings.local.json" 2>/dev/null | sort)
```

The audit reports the diff. The user runs `/sync-permissions` separately to apply it.

## Report format

```
Permissions Audit:
  .claude/settings.local.json   synced (64/64 allow, 4/4 deny)
```

Or when missing entries are detected:

```
Permissions Audit:
  .claude/settings.local.json   3 allow permissions missing (WebFetch, Skill(literature), Bash(jq*))
  .claude/settings.local.json   1 deny permission missing (Bash(pip*))
  Remediation: run /sync-permissions to merge.
```

Or when the file is missing entirely:

```
Permissions Audit:
  .claude/settings.local.json   MISSING — run /sync-permissions to seed from global (25 allow, 4 deny would be added).
```

## Edge cases

- **No `.claude/` directory at all:** flag at Phase 2.1 (pre-template detection); audit notes that `/sync-permissions` will create the directory along with the settings file.
- **`settings.local.json` has non-permissions keys (hooks, model):** report them under Info — they're preserved by `/sync-permissions`, which only touches the `permissions` object.
- **Pre-template projects:** Phase 2.1 already flags these. Permissions audit can still run independently — having permissions without the rest of the scaffold is harmless.

## What this phase does NOT do

- Never modifies the project (read-only — see Critical Rule 1 in `SKILL.md`).
- Never modifies `~/.claude/settings.json` (read-only globally).
- Never auto-runs `/sync-permissions` — that's a separate user-triggered action.
