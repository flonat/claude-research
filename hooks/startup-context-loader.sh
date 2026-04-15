#!/bin/bash
# Skip on non-Mac environments (cloud, mobile)
source "$(dirname "$0")/resolve-task-mgmt.sh" || exit 0
# startup-context-loader.sh
# SessionStart hook (startup) — auto-detects and surfaces project documentation
# on fresh sessions in any project, so Claude doesn't waste tokens searching.
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

# --- Path Registry (canonical roots for all data) ---
CONFIG_DIR="$HOME/.config/task-mgmt"
PATH_REGISTRY=""
for entry in path:Task-Management research-root:Research-Projects vault:Research-Vault overleaf-root:Overleaf; do
  file="${entry%%:*}"
  label="${entry#*:}"
  if [ -f "$CONFIG_DIR/$file" ]; then
    val="$(head -1 "$CONFIG_DIR/$file" | tr -d '\n')"
    if [ -n "$val" ]; then
      PATH_REGISTRY="${PATH_REGISTRY}\n- ${label}: ${val}"
    fi
  fi
done
if [ -n "$PATH_REGISTRY" ]; then
  CONTEXT="## Path Registry${PATH_REGISTRY}"
fi

# --- Current focus (Task Management context) ---
add_section "Current Focus" "$TASK_MGMT/.context/current-focus.md" 25

# --- Project index (Task Management context) ---
add_section "Project Index" "$TASK_MGMT/.context/projects/_index.md" 40

# --- Resolve project root (handles subdirectory CWDs) ---
if [ "$CWD" != "$TASK_MGMT" ]; then
  PROJECT_ROOT=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")
fi

# --- MEMORY.md (structured knowledge tables and [LEARN] corrections) ---
if [ "$CWD" = "$TASK_MGMT" ]; then
  add_section "MEMORY.md" "$TASK_MGMT/MEMORY.md" 30
else
  add_section "Project MEMORY" "$PROJECT_ROOT/MEMORY.md" 30
fi

# --- Project-specific docs (if not in Task Management itself) ---
if [ "$CWD" != "$TASK_MGMT" ]; then

  add_section "Project README" "$PROJECT_ROOT/README.md" 40

  # Check for project-specific context files
  add_section "Project Focus" "$PROJECT_ROOT/.context/current-focus.md" 25

  # Check for project planning state
  add_section "Project Planning State" "$PROJECT_ROOT/.planning/state.md" 30
fi

# --- Latest session log (skip if >7 days old) ---
if [ -d "$TASK_MGMT/log" ]; then
  LATEST_LOG=$(find "$TASK_MGMT/log" -maxdepth 1 -name "*.md" -type f | sort -r | head -1)
  if [ -n "$LATEST_LOG" ]; then
    LOG_AGE=$(( ( $(date +%s) - $(stat -f %m "$LATEST_LOG" 2>/dev/null || echo 0) ) / 86400 ))
    if [ "$LOG_AGE" -le 7 ] 2>/dev/null; then
      add_section "Latest Session Log ($(basename "$LATEST_LOG"))" "$LATEST_LOG" 30
    else
      if [ -n "$CONTEXT" ]; then CONTEXT="$CONTEXT\n\n"; fi
      CONTEXT="${CONTEXT}## Latest Session Log\nLast log is ${LOG_AGE} days old ($(basename "$LATEST_LOG")). Read it if resuming prior work."
    fi
  fi
fi

# --- Latest plan (skip if >14 days old) ---
if [ -d "$TASK_MGMT/log/plans" ]; then
  LATEST_PLAN=$(find "$TASK_MGMT/log/plans" -maxdepth 1 -name "*.md" -type f | sort -r | head -1)
  if [ -n "$LATEST_PLAN" ]; then
    PLAN_AGE=$(( ( $(date +%s) - $(stat -f %m "$LATEST_PLAN" 2>/dev/null || echo 0) ) / 86400 ))
    if [ "$PLAN_AGE" -le 14 ] 2>/dev/null; then
      add_section "Active Plan ($(basename "$LATEST_PLAN"))" "$LATEST_PLAN" 25
    fi
    # >14 days: silently skip — plan is likely completed or abandoned
  fi
fi

# --- Pending agent messages ---
AGENT_MSG_FILE="$TASK_MGMT/.context/agent-messages.md"
if [ -f "$AGENT_MSG_FILE" ]; then
  PENDING_COUNT=$(grep -c '^\## \[pending\]' "$AGENT_MSG_FILE" 2>/dev/null) || PENDING_COUNT=0
  if [ "$PENDING_COUNT" -gt 0 ] 2>/dev/null; then
    add_section "Pending Agent Messages ($PENDING_COUNT)" "$AGENT_MSG_FILE" 40
  fi
fi

# --- Skill observations: weekly review check ---
REVIEW_DATE_FILE="$HOME/.claude/skill-observations/last-review-date.txt"
if [ -f "$REVIEW_DATE_FILE" ]; then
  LAST_REVIEW=$(cat "$REVIEW_DATE_FILE" | tr -d '\n')
  DAYS_SINCE=$(( ( $(date +%s) - $(date -j -f "%Y-%m-%d" "$LAST_REVIEW" +%s 2>/dev/null || echo 0) ) / 86400 ))
  if [ "$DAYS_SINCE" -ge 7 ] 2>/dev/null; then
    if [ -n "$CONTEXT" ]; then
      CONTEXT="$CONTEXT\n\n"
    fi
    CONTEXT="${CONTEXT}## Skill Observations\nWeekly review overdue (last: ${LAST_REVIEW}, ${DAYS_SINCE} days ago). Consider running \`/skill-health\` to review."
  fi
fi

# --- Session type detection ---
SESSION_TYPE="general"
if [ "$CWD" = "$TASK_MGMT" ]; then
  SESSION_TYPE="infrastructure"
elif [ -d "$PROJECT_ROOT/paper" ] || [ -d "$PROJECT_ROOT/paper-"* ] 2>/dev/null || ls "$PROJECT_ROOT"/paper-*/paper 2>/dev/null | head -1 >/dev/null 2>&1; then
  SESSION_TYPE="research"
elif echo "$CWD" | grep -qi "teaching\|course\|module\|teaching\|workshop"; then
  SESSION_TYPE="teaching"
fi
if [ -n "$CONTEXT" ]; then CONTEXT="$CONTEXT\n\n"; fi
CONTEXT="${CONTEXT}## Session Type\nDetected: **${SESSION_TYPE}** (from CWD: $(basename "$CWD"))"

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
