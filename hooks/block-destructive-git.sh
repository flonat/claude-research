#!/bin/bash
# block-destructive-git.sh
# PreToolUse hook for Bash — catches dangerous git/shell commands
# and surfaces a permission prompt. Soft block via permissionDecision: "ask".

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# No command — allow
if [ -z "$COMMAND" ]; then
  exit 0
fi

REASON=""

# Check destructive patterns
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  REASON="git reset --hard will discard all uncommitted changes"
fi

if echo "$COMMAND" | grep -qE 'git\s+push\s+(-f|--force)(\s|$)' && \
   ! echo "$COMMAND" | grep -q '\-\-force-with-lease'; then
  REASON="git push --force can overwrite remote history (use --force-with-lease instead?)"
fi

if echo "$COMMAND" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f' && \
   ! echo "$COMMAND" | grep -qE 'git\s+clean\s+-[a-zA-Z]*n'; then
  REASON="git clean -f will permanently delete untracked files"
fi

if echo "$COMMAND" | grep -qE 'git\s+checkout\s+\.\s*$'; then
  REASON="git checkout . will discard all unstaged changes"
fi

if echo "$COMMAND" | grep -qE 'git\s+restore\s+\.\s*$'; then
  REASON="git restore . will discard all unstaged changes"
fi

if echo "$COMMAND" | grep -qE 'git\s+branch\s+-D\s'; then
  REASON="git branch -D force-deletes a branch (use -d for safe delete)"
fi

if echo "$COMMAND" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f|rm\s+-[a-zA-Z]*f[a-zA-Z]*r'; then
  REASON="rm -rf is a destructive operation"
fi

# If no dangerous pattern matched, allow silently
if [ -z "$REASON" ]; then
  exit 0
fi

# Dangerous pattern found — ask for confirmation
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "$REASON"
  }
}
EOF

exit 0
