#!/bin/bash
# resume-context-loader.sh
# SessionStart hook (resume) — surfaces current focus and latest session log
# so Claude picks up where things left off.

TASK_MGMT="$HOME/Library/CloudStorage/YOUR-CLOUD/Task Management"
FOCUS_FILE="$TASK_MGMT/.context/current-focus.md"
LOG_DIR="$TASK_MGMT/log"

CONTEXT=""

# Read current focus
if [ -f "$FOCUS_FILE" ]; then
  FOCUS=$(head -20 "$FOCUS_FILE")
  CONTEXT="## Current Focus\n$FOCUS"
fi

# Find latest session log (not plans, not compact saves)
if [ -d "$LOG_DIR" ]; then
  LATEST_LOG=$(find "$LOG_DIR" -maxdepth 1 -name "*.md" -type f | sort -r | head -1)
  if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
    LOG_SUMMARY=$(head -30 "$LATEST_LOG")
    CONTEXT="$CONTEXT\n\n## Latest Session Log ($(basename "$LATEST_LOG"))\n$LOG_SUMMARY"
  fi
fi

if [ -z "$CONTEXT" ]; then
  exit 0
fi

# Escape for JSON
CONTEXT_ESCAPED=$(echo -e "$CONTEXT" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": $CONTEXT_ESCAPED
  }
}
EOF

exit 0
