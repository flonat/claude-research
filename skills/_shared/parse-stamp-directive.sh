#!/usr/bin/env bash
# parse-stamp-directive.sh — extract a review-state-stamp directive from an
# agent's response (markdown) and print it as `--key "value"` args ready to
# pipe into review-state-log.sh.
#
# Input: a markdown file or stdin containing the agent's final response.
# Output: a single line of arguments suitable for
#         `eval bash review-state-log.sh $(parse-stamp-directive.sh ...) --project X`.
#
# Directive format (YAML inside a fenced markdown block, the last thing in
# the agent's response):
#
#     ```review-state-stamp
#     check: paper-critic
#     paper: paper-eaamo
#     verdict: NEEDS REVISION
#     score: 78/100
#     open_issues: 8/8
#     report: reviews/paper-critic/2026-05-19-1437.md
#     notes: M3 framing weak; 4 minors trivial
#     ```
#
# Required keys: check, paper, verdict, open_issues, report, notes
# Optional keys: score (defaults to —), trigger (defaults to direct),
#                source (defaults to agent)
#
# Exit codes:
#   0   directive parsed and printed
#   1   no directive block found
#   2   malformed directive (missing required key, multi-line value, etc.)
#   3   bad invocation
#
# Usage:
#   bash parse-stamp-directive.sh agent-return.md
#   cat agent-return.md | bash parse-stamp-directive.sh -
#
# Note: the helper does NOT run review-state-log.sh itself. The orchestrator
# combines the parsed args with its own --trigger/--source/--project overrides
# and runs the helper. This keeps the parser deterministic and reusable.

set -uo pipefail

input="${1:-}"
if [[ -z "$input" ]]; then
    echo "usage: $0 <markdown-file>|-" >&2
    exit 3
fi

# Read the input into a temp file (handles both file arg and stdin "-")
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

if [[ "$input" == "-" ]]; then
    cat > "$tmp"
else
    if [[ ! -f "$input" ]]; then
        echo "parse-stamp-directive: file not found: $input" >&2
        exit 3
    fi
    cat "$input" > "$tmp"
fi

# Extract the directive block. Accept three forms (in order of preference):
#   1. ```review-state-stamp ... ```           (canonical fence info string)
#   2. ```yaml / ```yml with review-state-stamp: or review_stamp: at top level
#   3. ```yaml / ```yml with flat key: value lines (last resort, accept if all
#       required keys present)
# The first matching block in the file wins.

# Try form 1 first (canonical)
block=$(awk '
    /^```review-state-stamp$/ { in_block = 1; next }
    in_block && /^```$/        { exit }
    in_block                   { print }
' "$tmp")

# Try forms 2 + 3 — scan ```yaml / ```yml fences
if [[ -z "$block" ]]; then
    yaml_block=$(awk '
        /^```(yaml|yml)$/    { in_block = 1; next }
        in_block && /^```$/   { exit }
        in_block              { print }
    ' "$tmp")
    if [[ -n "$yaml_block" ]]; then
        # Form 2: top-level key is review-state-stamp: or review_stamp: (underscore or dash variants)
        if echo "$yaml_block" | grep -qE "^(review-state-stamp|review_stamp|review_state_stamp):"; then
            # Unwrap: drop the top-level key line and de-indent the children (strip leading whitespace).
            # Use sed -E (ERE) — BSD sed on macOS doesn't support \| BRE alternation.
            block=$(echo "$yaml_block" | sed -nE '/^(review-state-stamp|review_stamp|review_state_stamp):/,$p' \
                | tail -n +2 \
                | sed -E 's/^[[:space:]]+//')
        else
            # Form 3: flat key:value lines directly
            block="$yaml_block"
        fi
    fi
fi

if [[ -z "$block" ]]; then
    echo "parse-stamp-directive: no review-state-stamp directive found (tried fence-info-string, yaml/yml fence with review-state-stamp: top key, and flat yaml/yml fence)" >&2
    exit 1
fi

# Parse key: value lines. Each line must be "key: value" with optional spaces.
# Values cannot contain newlines (single-line directive). Refuse multi-line.

declare -A vals

while IFS= read -r line; do
    # Skip empty lines and comment lines
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue

    # Match key: value
    if [[ "$line" =~ ^[[:space:]]*([a-zA-Z_][a-zA-Z0-9_-]*)[[:space:]]*:[[:space:]]*(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        val="${BASH_REMATCH[2]}"
        # Strip surrounding double or single quotes if present (defensive against
        # agents that quote string values like score: "78/100")
        val="${val#\"}"; val="${val%\"}"
        val="${val#\'}"; val="${val%\'}"
        # Trim trailing whitespace
        val="${val%"${val##*[![:space:]]}"}"
        # Normalize underscore → dash for arg style (open_issues → open-issues)
        key_dash="${key//_/-}"
        # Refuse if value contains a newline (shouldn't happen given line-by-line, but defensive)
        if [[ "$val" == *$'\n'* ]]; then
            echo "parse-stamp-directive: multi-line value forbidden in key=$key" >&2
            exit 2
        fi
        vals["$key_dash"]="$val"
    else
        echo "parse-stamp-directive: unparseable line: $line" >&2
        exit 2
    fi
done <<< "$block"

# Soft-translate common agent-emitted aliases for required keys
[[ -z "${vals[open-issues]:-}" && -n "${vals[open]:-}" ]]  && vals[open-issues]="${vals[open]}"
[[ -z "${vals[report]:-}"      && -n "${vals[report-path]:-}" ]] && vals[report]="${vals[report-path]}"
[[ -z "${vals[report]:-}"      && -n "${vals[report_path]:-}" ]] && vals[report]="${vals[report_path]}"

# Check required keys
required=(check paper verdict open-issues report notes)
for k in "${required[@]}"; do
    if [[ -z "${vals[$k]:-}" ]]; then
        echo "parse-stamp-directive: missing required key: ${k/-/_}" >&2
        exit 2
    fi
done

# Apply defaults
[[ -z "${vals[score]:-}" ]]   && vals[score]="—"
[[ -z "${vals[trigger]:-}" ]] && vals[trigger]="direct"
[[ -z "${vals[source]:-}" ]]  && vals[source]="agent"

# Print as --key "value" args. Order matches review-state-log.sh's expected
# arg list for readability.
printf -- '--check %q --paper %q --verdict %q --score %q --open-issues %q --report %q --notes %q --trigger %q --source %q\n' \
    "${vals[check]}" \
    "${vals[paper]}" \
    "${vals[verdict]}" \
    "${vals[score]}" \
    "${vals[open-issues]}" \
    "${vals[report]}" \
    "${vals[notes]}" \
    "${vals[trigger]}" \
    "${vals[source]}"
