#!/usr/bin/env bash
# Wrapper to launch the mcp-scholarly server with API keys.
#
# Keys arrive via two mechanisms (belt-and-suspenders):
#   1. The `env` dict in ~/.claude.json / claude_desktop_config.json
#      (set by sync-credentials.sh — primary mechanism)
#   2. Sourcing credentials.env directly below
#      (fallback for terminal launches and cron)
set -euo pipefail

CREDS_FILE="$HOME/.config/task-mgmt/credentials.env"
if [[ -f "$CREDS_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CREDS_FILE"
fi

exec uv run --directory "$(dirname "$0")" python server.py
