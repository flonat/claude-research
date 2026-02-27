#!/bin/bash
# promise-checker.sh
# Stop hook — catches "performative compliance": Claude says it remembered/noted/saved
# something but never actually called Edit or Write.
#
# Scans the last assistant turn for promise patterns.
# If promises found without corresponding Edit/Write tool calls → blocks.

INPUT=$(cat)

# Prevent infinite loops
STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_ACTIVE" = "true" ]; then
  exit 0
fi

TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# --- Extract the last assistant turn ---
# Read transcript from the end, collect all lines until we hit a user message.
# This captures the full turn (multiple assistant messages + tool results).
LAST_TURN=$(tac "$TRANSCRIPT_PATH" 2>/dev/null | while IFS= read -r line; do
  MSG_TYPE=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
  if [ "$MSG_TYPE" = "user_message" ]; then
    break
  fi
  echo "$line"
done)

if [ -z "$LAST_TURN" ]; then
  exit 0
fi

# --- Check for Edit/Write tool calls in this turn ---
HAS_WRITE=$(echo "$LAST_TURN" | \
  jq -r '.content[]? | select(.type == "tool_use") | .name' 2>/dev/null | \
  grep -qiE '^(Edit|Write|NotebookEdit)$' && echo "yes" || echo "no")

# --- Extract all text content from assistant messages in this turn ---
TEXT_CONTENT=$(echo "$LAST_TURN" | \
  jq -r 'select(.type == "assistant_message") | .content[]? | select(.type == "text") | .text' 2>/dev/null)

if [ -z "$TEXT_CONTENT" ]; then
  exit 0
fi

# --- Promise patterns ---
# Phrases where Claude claims to have stored/remembered/noted something,
# or promises to do so. Case-insensitive matching applied later.

PROMISE_PATTERNS=(
  # Future promises to store
  "I'll remember"
  "I'll note that"
  "I'll write that down"
  "I'll save that"
  "I'll record"
  "I'll store"
  "I'll make a note"
  "I'll add that to"
  "I'll put that in"
  "I'll log that"
  "I'll update.*memory"
  "I'll update.*context"
  "I'll update.*MEMORY"
  "I'll keep that in mind"
  "let me note that"
  "let me save"
  "let me record"
  "let me write that"
  # Past claims of having stored
  "I've noted"
  "I've recorded"
  "I've saved that"
  "I've stored"
  "I've memorized"
  "I've written that down"
  "I've added that"
  "I've updated.*memory"
  "I've updated.*MEMORY"
  "I've updated.*context"
  "I've logged"
  "I've made a note"
  "I've taken note"
  "I've put that in"
  # Short forms
  "^Noted[.!]"
  "Noted —"
  "Noted,"
  "duly noted"
)

# Build a single regex from patterns
REGEX=$(printf '%s|' "${PROMISE_PATTERNS[@]}")
REGEX="${REGEX%|}"  # Remove trailing pipe

# Check for promise patterns (case-insensitive)
MATCHED=$(echo "$TEXT_CONTENT" | grep -iE "$REGEX" | head -3)

if [ -z "$MATCHED" ]; then
  # No promises found — all clear
  exit 0
fi

# --- Verdict ---
if [ "$HAS_WRITE" = "no" ]; then
  # Promises found but no write actions — block!
  SNIPPET=$(echo "$MATCHED" | head -1 | cut -c1-80)
  cat <<EOF
{
  "decision": "block",
  "reason": "Promise without action: you said \"${SNIPPET}\" but no Edit/Write tool was called. Actually write it down (MEMORY.md, context file, or wherever appropriate)."
}
EOF
  exit 0
fi

# Promises found AND write actions exist — all good
exit 0
