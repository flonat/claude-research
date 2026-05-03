#!/bin/bash
# ensure-resources.sh — clone any resource repos listed in the manifest
# that are missing locally.
#
# Usage:
#   bash .scripts/ensure-resources.sh            # clone missing
#   bash .scripts/ensure-resources.sh --dry-run  # report only, no clones
#
# Reads scripts/resource-manifest.txt (committed). For each entry, if the
# target dir has no .git, clones from the origin URL. Existing repos are
# left alone — use .scripts/sync-resources.sh to pull updates.

set -uo pipefail

_CONFIG="$HOME/.config/task-mgmt/path"
[[ ! -f "$_CONFIG" ]] && { echo "Missing $_CONFIG" >&2; exit 1; }
TM="$(head -1 "$_CONFIG" | tr -d '\n')"

BASE="$TM/resources"
MANIFEST="$TM/scripts/resource-manifest.txt"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

[[ ! -f "$MANIFEST" ]] && { echo "Missing manifest: $MANIFEST" >&2; exit 1; }

# Prevent git from hanging on credential prompts (fail fast if auth missing)
export GIT_TERMINAL_PROMPT=0

missing=0
cloned=0
failed=0

while IFS='|' read -r rel origin; do
    # Skip comments and blanks
    [[ -z "$rel" || "$rel" == \#* ]] && continue
    target="$BASE/$rel"
    if [ -d "$target/.git" ] || [ -f "$target/.git" ]; then
        continue
    fi
    missing=$((missing + 1))
    echo "[missing] $rel → $origin"
    if (( DRY )); then
        continue
    fi
    mkdir -p "$(dirname "$target")"
    if git clone "$origin" "$target" 2>&1 | sed 's/^/  /'; then
        cloned=$((cloned + 1))
    else
        failed=$((failed + 1))
        echo "  ✗ clone failed"
    fi
done < "$MANIFEST"

if (( DRY )); then
    echo "[ensure-resources] dry-run: $missing missing"
else
    echo "[ensure-resources] missing=$missing cloned=$cloned failed=$failed"
fi

(( failed > 0 )) && exit 1 || exit 0
