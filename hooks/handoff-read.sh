#!/bin/bash
# handoff-read.sh
# SessionStart hook — if handoff.md exists in cwd, read it into additionalContext
# and delete it (one-shot scratch).
#
# Companion to the /handoff skill. Zero cost when no handoff.md present.

HANDOFF="$(pwd)/handoff.md"

[ -f "$HANDOFF" ] || exit 0

CONTENT=$(cat "$HANDOFF")
[ -z "$CONTENT" ] && { rm -f "$HANDOFF"; exit 0; }

# Delete immediately — one-shot semantics even if JSON emission fails
rm -f "$HANDOFF"

WRAPPED="# Handoff from previous session

(Auto-injected from handoff.md in cwd, then deleted.)

$CONTENT"

CONTEXT_ESCAPED=$(printf '%s' "$WRAPPED" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": $CONTEXT_ESCAPED
  }
}
EOF

exit 0
