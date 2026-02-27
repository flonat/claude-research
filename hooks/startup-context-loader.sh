#!/bin/bash
# startup-context-loader.sh
# SessionStart hook (startup) — auto-detects and surfaces project documentation
# on fresh sessions in any project, so Claude doesn't waste tokens searching.

TASK_MGMT="$HOME/Library/CloudStorage/YOUR-CLOUD/Task Management"
CWD="$(pwd)"
CONTEXT=""
MAX_LINES=30

add_section() {
  local title="$1"
  local file="$2"
  local lines="${3:-$MAX_LINES}"

  if [ -f "$file" ]; then
    local content
    content=$(head -"$lines" "$file")
    if [ -n "$content" ]; then
      if [ -n "$CONTEXT" ]; then
        CONTEXT="$CONTEXT\n\n"
      fi
      CONTEXT="${CONTEXT}## ${title}\n${content}"
    fi
  fi
}

# --- Current focus (Task Management context) ---
add_section "Current Focus" "$TASK_MGMT/.context/current-focus.md" 25

# --- Project index (Task Management context) ---
add_section "Project Index" "$TASK_MGMT/.context/projects/_index.md" 40

# --- MEMORY.md (structured knowledge tables and [LEARN] corrections) ---
if [ "$CWD" = "$TASK_MGMT" ]; then
  add_section "MEMORY.md" "$TASK_MGMT/MEMORY.md" 30
else
  # For other projects, load project-level MEMORY.md
  add_section "Project MEMORY" "$CWD/MEMORY.md" 30
fi

# --- Project-specific docs (if not in Task Management itself) ---
if [ "$CWD" != "$TASK_MGMT" ]; then
  add_section "Project README" "$CWD/README.md" 40

  # Check for project-specific context files
  add_section "Project Focus" "$CWD/.context/current-focus.md" 25
fi

# --- Latest session log ---
if [ -d "$TASK_MGMT/log" ]; then
  LATEST_LOG=$(find "$TASK_MGMT/log" -maxdepth 1 -name "*.md" -type f | sort -r | head -1)
  add_section "Latest Session Log ($(basename "$LATEST_LOG" 2>/dev/null))" "$LATEST_LOG" 30
fi

# --- Latest plan (if any) ---
if [ -d "$TASK_MGMT/log/plans" ]; then
  LATEST_PLAN=$(find "$TASK_MGMT/log/plans" -maxdepth 1 -name "*.md" -type f | sort -r | head -1)
  add_section "Latest Plan ($(basename "$LATEST_PLAN" 2>/dev/null))" "$LATEST_PLAN" 25
fi

if [ -z "$CONTEXT" ]; then
  exit 0
fi

# Add a header
CONTEXT="# Session Context (auto-loaded)\nRead these docs — do NOT re-search for this information.\n\n${CONTEXT}"

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
