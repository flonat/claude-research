#!/bin/bash
# protect-source-files.sh
# PreToolUse hook for Edit|Write — prompts confirmation for files outside
# the current project, ~/.claude/, and the Task Management directory.
# Soft block (permissionDecision: "ask"), not hard block.

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

# If no file path, allow (shouldn't happen but be safe)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Resolve to absolute paths
FILE_PATH=$(cd "$(dirname "$FILE_PATH")" 2>/dev/null && echo "$(pwd)/$(basename "$FILE_PATH")" || echo "$FILE_PATH")
CWD=$(cd "$CWD" 2>/dev/null && pwd || echo "$CWD")

TASK_MGMT="$HOME/Library/CloudStorage/YOUR-CLOUD/Task Management"
CLAUDE_DIR="$HOME/.claude"

# Allow: file is inside CWD (logical path)
if [[ "$FILE_PATH" == "$CWD"/* ]]; then
  exit 0
fi

# Allow: file is inside CWD (resolved/physical path, handles symlinks)
RESOLVED_CWD=$(cd "$CWD" 2>/dev/null && pwd -P || echo "$CWD")
if [[ "$FILE_PATH" == "$RESOLVED_CWD"/* ]]; then
  exit 0
fi

# Allow: file is inside any symlink target reachable from CWD (one level deep)
# This handles e.g. paper/ -> Overleaf/ where resolved paths differ from CWD
for LINK in "$CWD"/*/; do
  if [ -L "${LINK%/}" ]; then
    LINK_TARGET=$(cd "${LINK%/}" 2>/dev/null && pwd -P || continue)
    if [[ -n "$LINK_TARGET" ]] && [[ "$FILE_PATH" == "$LINK_TARGET"/* ]]; then
      exit 0
    fi
  fi
done

# Allow: file is under ~/.claude/ (settings, memory, skills)
if [[ "$FILE_PATH" == "$CLAUDE_DIR"/* ]]; then
  exit 0
fi

# Allow: file is under Task Management directory (context library)
if [[ "$FILE_PATH" == "$TASK_MGMT"/* ]]; then
  exit 0
fi

# Block: skill files outside Task Management (skills are global only)
if [[ "$FILE_PATH" == */skills/*/SKILL.md ]] && [[ "$FILE_PATH" != "$TASK_MGMT"/skills/* ]]; then
  cat <<BLOCK
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Skills must be created in Task Management/skills/, not locally. This file would be created at: $FILE_PATH"
  }
}
BLOCK
  exit 0
fi

# Outside all known safe zones — ask for confirmation
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "File is outside current project: $FILE_PATH — confirm?"
  }
}
EOF

exit 0
