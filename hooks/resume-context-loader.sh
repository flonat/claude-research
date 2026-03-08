#!/bin/bash
# Skip on non-Mac environments (cloud, mobile)
source "$(dirname "$0")/resolve-task-mgmt.sh" || exit 0
# resume-context-loader.sh
# SessionStart hook (resume) — surfaces current focus and latest session log
# so Claude picks up where things left off.
FOCUS_FILE="$TASK_MGMT/.context/current-focus.md"
LOG_DIR="$TASK_MGMT/log"

CONTEXT=""

# Read current focus
if [ -f "$FOCUS_FILE" ]; then
  FOCUS=$(head -20 "$FOCUS_FILE")
  CONTEXT="## Current Focus\n$FOCUS"
fi

# Load project planning state (if in a project with orchestration)
CWD="$(pwd)"
if [ "$CWD" != "$TASK_MGMT" ]; then
  PROJECT_ROOT=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")
  if [ -f "$PROJECT_ROOT/.planning/state.md" ]; then
    STATE=$(head -30 "$PROJECT_ROOT/.planning/state.md")
    CONTEXT="$CONTEXT\n\n## Project Planning State\n$STATE"
  fi
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
