#!/usr/bin/env bash
# Wrapper to launch the bibliography MCP server with API keys from Scout's .env
set -euo pipefail

ENV_FILE="$(dirname "$0")/../../research/scout/.env"

if [[ -f "$ENV_FILE" ]]; then
  while IFS='=' read -r key value; do
    # Skip comments and blank lines
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    # Only export the keys the server needs
    case "$key" in
      WOS_API_KEY|WOS_API_TIER|SCOPUS_API_KEY|SCOPUS_INST_TOKEN|S2_API_KEY|ORCID_CLIENT_ID|ORCID_CLIENT_SECRET|CORE_API_KEY|ALTMETRIC_API_KEY|ALTMETRIC_API_PASSWORD)
        export "$key"="$value"
        ;;
    esac
  done < "$ENV_FILE"
fi

exec uv run --directory "$(dirname "$0")" python server.py
