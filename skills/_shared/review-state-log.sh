#!/usr/bin/env bash
# review-state-log.sh — append a row to the project's review-state log file.
#
# Schema: docs/reference/review-state-schema.md (10-column canonical form)
# Routing: rules/review-artefact-routing.md (paper-*/** path-scoped)
# Used by: 20 review skills/agents (see schema doc for the locked list).
#
# Target-file resolution (forward-only, post 2026-05-17 reroute):
#   1. <project>/reviews/INDEX.md is ALWAYS the destination. Create with the
#      canonical header if absent. Never write to <project>/REVIEW-STATE.md
#      going forward.
#   2. If <project>/REVIEW-STATE.md ALSO exists (legacy state), print a
#      one-line warning suggesting the `tidy-project-reviews` workflow to migrate.
#      The legacy file is left untouched — this helper does not migrate it;
#      that is tidy-project-reviews' job.
#
# CHANGELOG:
#   2026-05-17 (dcbcd9fb): added 3-way resolution preferring INDEX.md but
#       falling back to REVIEW-STATE.md if it existed. This proved insufficient
#       — projects that had REVIEW-STATE.md alone continued to accrete legacy
#       rows under the legacy path, causing divergence from the canonical
#       INDEX.md once tidy-project-reviews ran.
#   2026-05-17 (this fix): forward-only — always write to reviews/INDEX.md,
#       warn on dual-file existence, leave legacy REVIEW-STATE.md for tidy.
#       Also: refuse newlines in --notes (would break the table row).
#
# Append-only semantics. Existing rows are never overwritten or rewritten.
#
# Usage:
#   source "<skills-root>/_shared/review-state-log.sh"
#   log_review_state \
#     --check paper-critic \
#     --paper paper-eaamo \
#     --verdict APPROVED \
#     --score "87/100" \
#     --open-issues "0/8" \
#     --report reviews/paper-eaamo/paper-critic/2026-05-14-1400.md \
#     --notes "M1-M6 fixed" \
#     [--trigger pre-submission-report] \
#     [--project /path/to/project]
#
# Defaults:
#   --paper       "—"        (project-level review)
#   --verdict     "RAN"      (action-only, no verdict semantics)
#   --score       "—"
#   --open-issues "—"
#   --report      "—"
#   --notes       "—"
#   --trigger     "direct"
#   --source      "skill"    (one of: skill | agent | manual | recap-inferred)
#   --project     auto       (walk up from cwd looking for .git or CLAUDE.md)
#
# Always sets:
#   Last Run = current local time, YYYY-MM-DD HH:MM
#
# Exit codes:
#   0   row appended
#   1   missing required arg (--check)
#   2   could not resolve project root
#   3   could not write to REVIEW-STATE.md
#   4   report path does not match canonical convention

log_review_state() {
    local check="" paper="—" verdict="RAN" score="—" open_issues="—"
    local report="—" notes="—" trigger="direct" project="" source="skill"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check)        check="$2";        shift 2 ;;
            --paper)        paper="$2";        shift 2 ;;
            --verdict)      verdict="$2";      shift 2 ;;
            --score)        score="$2";        shift 2 ;;
            --open-issues)  open_issues="$2";  shift 2 ;;
            --report)       report="$2";       shift 2 ;;
            --notes)        notes="$2";        shift 2 ;;
            --trigger)      trigger="$2";      shift 2 ;;
            --project)      project="$2";      shift 2 ;;
            --source)       source="$2";       shift 2 ;;
            *)
                printf 'review-state-log: unknown arg: %s\n' "$1" >&2
                return 1
                ;;
        esac
    done

    if [[ -z "$check" ]]; then
        printf 'review-state-log: --check is required\n' >&2
        return 1
    fi

    # Validate --source against the closed allow-list. Trigger is left open
    # (it names the invoking orchestrator — review-cluster / pre-submission-report
    # / direct / etc. — and new ones legitimately appear over time).
    case "$source" in
        skill|agent|manual|recap-inferred) ;;
        *)
            printf 'review-state-log: --source must be one of: skill, agent, manual, recap-inferred (got: %q)\n' "$source" >&2
            return 1
            ;;
    esac

    # Refuse newlines in --notes (would break the table row). Same check for
    # any user-supplied single-line field to be safe.
    local fld
    for fld in check paper verdict score open_issues report notes trigger source; do
        if [[ "${!fld}" == *$'\n'* ]]; then
            printf 'review-state-log: --%s contains a newline — single-line only\n' "${fld//_/-}" >&2
            return 1
        fi
    done

    # Validate --report path follows canonical convention: reviews/<scope>/<check>/YYYY-MM-DD-HHMM.md
    # where <scope> is the paper slug (e.g. paper-jtp) or "_project" if paper == "—".
    # Skip if report is "—" (no report artifact) or source is "recap-inferred" (legacy backfill).
    if [[ "$report" != "—" && "$source" != "recap-inferred" ]]; then
        local expected_prefix
        if [[ "$paper" == "—" ]]; then
            expected_prefix="reviews/_project/$check/"
        else
            expected_prefix="reviews/$paper/$check/"
        fi
        if [[ "$report" != "$expected_prefix"* ]]; then
            printf 'review-state-log: --report path does not match canonical convention\n' >&2
            printf '  expected prefix: %s\n' "$expected_prefix" >&2
            printf '  got: %s\n' "$report" >&2
            return 4
        fi
    fi

    # Resolve project root: walk up from cwd looking for .git or CLAUDE.md
    if [[ -z "$project" ]]; then
        local d
        d="$(pwd)"
        while [[ "$d" != "/" ]]; do
            if [[ -d "$d/.git" || -f "$d/CLAUDE.md" ]]; then
                project="$d"
                break
            fi
            d="$(dirname "$d")"
        done
    fi

    if [[ -z "$project" || ! -d "$project" ]]; then
        printf 'review-state-log: could not resolve project root from %s\n' "$(pwd)" >&2
        return 2
    fi

    # Target-file resolution per rules/review-artefact-routing.md (forward-only).
    # Always write to reviews/INDEX.md. Warn if legacy REVIEW-STATE.md exists too.
    local state_file="$project/reviews/INDEX.md"
    if [[ -f "$project/REVIEW-STATE.md" ]]; then
        printf 'review-state-log: legacy %s/REVIEW-STATE.md detected alongside canonical reviews/INDEX.md — use the tidy-project-reviews workflow to merge legacy rows (this stamp lands at reviews/INDEX.md only).\n' \
            "$project" >&2
    fi

    local project_name
    project_name="$(basename "$project")"
    local now
    now="$(date '+%Y-%m-%d %H:%M')"

    # Sanitise pipe characters in user-supplied fields (would break the table).
    # Keep this conservative — only strip the one character that breaks parsing.
    local f
    for f in check paper verdict score open_issues report notes trigger; do
        # shellcheck disable=SC2086
        printf -v "$f" '%s' "${!f//|/\\|}"
    done

    # Create file with header if missing. Only ever the CANONICAL path
    # (reviews/INDEX.md) — the legacy REVIEW-STATE.md is never created fresh;
    # we'd have selected it above only if it existed.
    if [[ ! -f "$state_file" ]]; then
        mkdir -p "$(dirname "$state_file")"
        cat > "$state_file" <<EOF
# Review State — $project_name

> Per-project review log. One row per (skill/agent run). Append-only by convention.
> See the installed shared `review-state-schema.md` resource for the schema.
> Routing: \`rules/review-artefact-routing.md\` (canonical home: \`reviews/INDEX.md\`).
> \`review-recap\` renders this file. Hand-edits welcome (set Source=manual).

| Paper | Check | Last Run | Verdict | Score | Open Issues | Source | Trigger | Report | Notes |
|-------|-------|----------|---------|-------|-------------|--------|---------|--------|-------|
EOF
        if [[ ! -f "$state_file" ]]; then
            printf 'review-state-log: failed to create %s\n' "$state_file" >&2
            return 3
        fi
    fi

    # Append row. Always >> — never > — preserves prior rows.
    # Source column accepts: skill (default), agent, manual, recap-inferred.
    if ! printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
        "$paper" "$check" "$now" "$verdict" "$score" "$open_issues" \
        "$source" "$trigger" "$report" "$notes" \
        >> "$state_file"; then
        printf 'review-state-log: failed to append row to %s\n' "$state_file" >&2
        return 3
    fi

    return 0
}

# If invoked directly (not sourced), run with passed args.
# This lets non-bash skills call it as: bash review-state-log.sh --check ... --paper ...
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    log_review_state "$@"
    exit $?
fi
