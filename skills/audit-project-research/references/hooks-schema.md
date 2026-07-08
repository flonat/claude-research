# Phase 2.6: Hooks Schema Validation (Read-Only)

> Detailed check for `/audit-project-research` Phase 2.6. **This phase is read-only.** It flags bare-string hooks and provides the patch — the user applies the fix manually or via `/update-config`.

If `.claude/settings.local.json` contains a `hooks` key, validate every hook entry against the required schema. **Invalid hooks cause the entire settings file to be skipped at session start** — permissions, model overrides, and all other settings are silently lost.

## Required schema

Each hook event (`PreToolUse`, `PostToolUse`, `Notification`, `Stop`) maps to an array of matcher objects. Each matcher object has:

```json
{
  "matcher": "ToolName",
  "hooks": [
    {"type": "command", "command": "path/to/script.sh"}
  ]
}
```

The `hooks` array inside each matcher must contain **objects** with `type` and `command` keys.

## Common error

Bare strings instead of objects:

```json
// WRONG — causes entire settings file to be skipped
"hooks": [".claude/hooks/copy-paper-pdf.sh"]

// CORRECT
"hooks": [{"type": "command", "command": ".claude/hooks/copy-paper-pdf.sh"}]
```

## How to check

```bash
# Extract all hooks array values and check for bare strings
jq -e '
  .hooks // {} | to_entries[] |
  .value[] | .hooks[] |
  if type == "string" then error("bare string hook found: \(.)") else empty end
' "<project>/.claude/settings.local.json" 2>&1
```

If `jq` exits non-zero with "bare string hook found", the file has the bug.

## Severity

| Condition | Severity |
|-----------|----------|
| `hooks` key absent | OK — no hooks configured |
| All hook entries are objects | OK |
| Any hook entry is a bare string | **Missing** — "hooks entry is a bare string — entire settings file is skipped at session start. Fix patch shown below." |
| `hooks` key present but malformed JSON | **Missing** — "hooks section has invalid JSON — entire settings file is skipped" |

## Suggested patch (do not auto-apply)

The audit reports the patch but does not run it. The user applies via `/update-config` or by hand:

```bash
# Replace bare string hooks with object format
jq '
  .hooks |= (if . then
    to_entries | map(
      .value |= map(
        .hooks |= map(
          if type == "string" then {"type": "command", "command": .} else . end
        )
      )
    ) | from_entries
  else . end)
' "<project>/.claude/settings.local.json" > tmp.$$ && mv tmp.$$ "<project>/.claude/settings.local.json"
```

This is consistent with Phase 2.5 (permissions) and Phase 2.7 (rules hygiene), which are also read-only.

## Report format

```
Hooks Schema:
  .claude/settings.local.json   OK (1 PostToolUse hook, all valid objects)
```

Or when issues are detected:

```
Hooks Schema:
  .claude/settings.local.json   1 bare string hook detected — entire settings file is skipped
    PostToolUse[0].hooks[0]: ".claude/hooks/copy-paper-pdf.sh"
    Suggested patch: wrap as {"type":"command","command":".claude/hooks/copy-paper-pdf.sh"}
    Apply with: /update-config (or run the jq snippet above manually)
```
