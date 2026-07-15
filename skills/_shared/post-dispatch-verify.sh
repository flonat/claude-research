#!/usr/bin/env bash
# post-dispatch-verify.sh — ensure the .md report file claimed by a sub-agent's
# `review-state-stamp` directive actually exists on disk.
#
# Background: as of the 2026-05-19 architecture, review sub-agents emit a
# `review-state-stamp` YAML directive naming the report path. The orchestrator
# parses the directive and calls review-state-log.sh to append a row to
# reviews/INDEX.md. But agents can emit a directive claiming the file exists
# without actually calling Write — the blindspot incident on 2026-05-21
# (see log/2026-05-21-blindspot-write-fix.md). The orchestrator was then
# stamping rows that pointed at non-existent files.
#
# This helper closes the loop: between parse-stamp-directive.sh and
# review-state-log.sh, the orchestrator invokes this helper to verify
# the report file exists. If missing, reconstruct it from the agent's
# return-value content (the prose + directive block) so the stamp row
# still points at a real file. The reconstructed file is tagged
# `reconstructed: true` in its front-matter so downstream consumers
# (synthesise-reviews, anchor tooling) can degrade gracefully.
#
# Usage:
#   bash post-dispatch-verify.sh \
#       --return-file /tmp/agent-return-<agent>.md \
#       --project <project-root> \
#       [--agent <expected-agent-name>]
#
# Output: prints one of these to stdout:
#   OK <abs-path>                 — file exists, no action
#   RECONSTRUCTED <abs-path>      — file was missing, reconstructed from return
#   MISSING-DIRECTIVE             — no review-state-stamp block in return file
#   ERROR <message>               — parse / write failure
#
# Exit codes:
#   0   file exists, no action needed
#   10  file was missing, reconstruction succeeded
#   1   bad invocation
#   2   directive parse failed (missing block or required fields)
#   3   write / mkdir failed
#
# Designed to be called by:
#   - skills/review-cluster/SKILL.md (per sub-agent)
#   - skills/pre-submission-report/SKILL.md (per sub-agent)
#   - skills/code-suite/SKILL.md (per sub-agent)
#   - rules/stamp-after-review-dispatch.md (main session, per direct dispatch)

set -uo pipefail

return_file=""
project=""
agent=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --return-file) return_file="$2"; shift 2 ;;
        --project)     project="$2";     shift 2 ;;
        --agent)       agent="$2";       shift 2 ;;
        *)
            echo "post-dispatch-verify: unknown arg: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$return_file" || -z "$project" ]]; then
    echo "usage: $0 --return-file <path> --project <root> [--agent <name>]" >&2
    exit 1
fi
if [[ ! -f "$return_file" ]]; then
    echo "ERROR return-file not found: $return_file" >&2
    exit 1
fi
if [[ ! -d "$project" ]]; then
    echo "ERROR project root not a directory: $project" >&2
    exit 1
fi

# Resolve the parser path. Try several common locations.
PARSER=""
for cand in \
    "$(dirname "${BASH_SOURCE[0]}")/parse-stamp-directive.sh" \
    "<skills-root>/_shared/parse-stamp-directive.sh" \
    [[ -f "$cand" ]] && { PARSER="$cand"; break; }
done
if [[ -z "$PARSER" ]]; then
    echo "ERROR parse-stamp-directive.sh not found" >&2
    exit 2
fi

# Parse the directive. Capture stderr separately so we can distinguish
# "no block" from real parse failures.
ARGS=$("$PARSER" "$return_file" 2>/tmp/post-dispatch-parse-err.$$)
parse_rc=$?
parse_stderr=$(cat /tmp/post-dispatch-parse-err.$$ 2>/dev/null || true)
rm -f /tmp/post-dispatch-parse-err.$$

if [[ $parse_rc -ne 0 ]]; then
    if echo "$parse_stderr" | grep -q "no review-state-stamp directive"; then
        echo "MISSING-DIRECTIVE"
        exit 2
    fi
    echo "ERROR parse failed (rc=$parse_rc): $parse_stderr" >&2
    exit 2
fi

# Extract the --report value (the canonical .md path).
# Use a simple regex; ARGS is shell-quoted output from the parser.
report_path=""
# parser emits: ... --report <value> --notes ...
# Use eval to get a parseable array, then walk it
declare -a parsed
eval "parsed=($ARGS)"
i=0
while [[ $i -lt ${#parsed[@]} ]]; do
    if [[ "${parsed[$i]}" == "--report" ]]; then
        report_path="${parsed[$((i+1))]}"
        break
    fi
    i=$((i+1))
done

if [[ -z "$report_path" ]]; then
    echo "ERROR no --report field in parsed directive" >&2
    exit 2
fi

# Resolve absolute path
case "$report_path" in
    /*) abs_path="$report_path" ;;
    *)  abs_path="$project/$report_path" ;;
esac

# Check if file exists
if [[ -f "$abs_path" ]]; then
    echo "OK $abs_path"
    exit 0
fi

# File missing — reconstruct from the agent's return content.
parent_dir="$(dirname "$abs_path")"
if ! mkdir -p "$parent_dir" 2>/dev/null; then
    echo "ERROR could not mkdir $parent_dir" >&2
    exit 3
fi

# Extract a label for the reconstructed file from the agent name (passed in
# via --agent) or from the --check field in the parsed directive
agent_label="$agent"
if [[ -z "$agent_label" ]]; then
    i=0
    while [[ $i -lt ${#parsed[@]} ]]; do
        if [[ "${parsed[$i]}" == "--check" ]]; then
            agent_label="${parsed[$((i+1))]}"
            break
        fi
        i=$((i+1))
    done
fi
[[ -z "$agent_label" ]] && agent_label="unknown-agent"

timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

# Write the reconstructed file. Front-matter tags it for downstream consumers.
{
    cat <<EOF
---
reconstructed: true
reconstructed_at: $timestamp
agent: $agent_label
reason: agent emitted a review-state-stamp directive naming this path but did not call Write
docs: log/2026-05-21-blindspot-write-fix.md
---

# $agent_label Report (reconstructed by orchestrator)

> **Note:** the \`$agent_label\` sub-agent emitted a stamp directive referencing
> this path but did not actually call \`Write\` to create the file. The
> orchestrator reconstructed the report from the agent's return-value
> content (below). Downstream consumers (\`synthesise-reviews\`, anchor
> tooling) should check the \`reconstructed: true\` front-matter field and
> degrade gracefully — the prose below is unstructured and may lack the
> per-tier issue tables, hard-gate sections, or findings.json sidecars that
> a real run would emit.
>
> See \`log/2026-05-21-blindspot-write-fix.md\` for the failure mode this
> guards against.

## Agent return content (verbatim)

EOF
    cat "$return_file"
} > "$abs_path"

if [[ ! -f "$abs_path" ]]; then
    echo "ERROR write succeeded but file does not exist: $abs_path" >&2
    exit 3
fi

echo "RECONSTRUCTED $abs_path"
exit 10
