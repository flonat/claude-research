#!/usr/bin/env python3
"""postcompact-restore.py
SessionStart hook (compact matcher) — restores state after context compression.

Reads the pre-compact-state.json saved by precompact-autosave.py, re-scans
disk for active plan state, and outputs a formatted restoration message as
additionalContext so Claude immediately knows where things stand.

Deletes the state file after reading to avoid stale restores.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

TASK_MGMT = Path.home() / "Library" / "CloudStorage" / "YOUR-CLOUD" / "Task Management"
LOG_DIR = TASK_MGMT / "log"
PLANS_DIR = LOG_DIR / "plans"
FOCUS_FILE = TASK_MGMT / ".context" / "current-focus.md"
SESSIONS_BASE = Path.home() / ".claude" / "sessions"


def project_hash() -> str:
    """Deterministic hash of the project directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return hashlib.sha256(project_dir.encode()).hexdigest()[:12]


def latest_file(directory: Path, pattern: str = "*.md") -> Path | None:
    """Return the most recently modified file matching pattern, or None."""
    if not directory.is_dir():
        return None
    files = sorted(directory.glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0] if files else None


def rescan_active_plan() -> dict | None:
    """Re-scan disk for the active plan (may have been updated since pre-compact save)."""
    plan_file = latest_file(PLANS_DIR)
    if not plan_file:
        return None

    text = plan_file.read_text(encoding="utf-8", errors="replace")
    text_lower = text.lower()

    if "completed" in text_lower or "done" in text_lower:
        return None

    status = "DRAFT"
    if "approved" in text_lower:
        status = "APPROVED"

    first_unchecked = None
    for line in text.splitlines():
        if re.match(r"\s*-\s*\[\s*\]", line):
            first_unchecked = line.strip()
            break

    return {
        "file": plan_file.name,
        "status": status,
        "first_unchecked": first_unchecked,
    }


def format_restoration(state: dict, live_plan: dict | None) -> str:
    """Build the formatted restoration message."""
    lines = ["## Post-Compaction State Restoration", ""]

    # Pre-compaction timestamp
    lines.append(f"**Compacted at:** {state.get('timestamp', 'unknown')}")
    lines.append(f"**Working directory:** {state.get('cwd', 'unknown')}")
    lines.append("")

    # Current focus
    focus = state.get("current_focus_headline")
    if focus:
        lines.append("### Current Focus")
        lines.append(focus)
        lines.append("")

    # Active plan
    plan = live_plan or state.get("active_plan")
    if plan:
        lines.append("### Active Plan")
        lines.append(f"- **File:** `log/plans/{plan['file']}`")
        lines.append(f"- **Status:** {plan['status']}")
        if plan.get("first_unchecked"):
            lines.append(f"- **Next step:** {plan['first_unchecked']}")
        lines.append("")

    # Latest session log
    log_name = state.get("latest_session_log")
    if log_name:
        lines.append(f"### Latest Session Log")
        lines.append(f"- **File:** `log/{log_name}`")
        lines.append("")

    # Recent decisions
    decisions = state.get("recent_decisions", [])
    if decisions:
        lines.append("### Recent Decisions (pre-compaction)")
        for d in decisions:
            lines.append(f"- {d}")
        lines.append("")

    # Recovery actions
    lines.append("### Recovery Actions")
    lines.append("1. Read the active plan file to restore full implementation context")
    lines.append("2. Read the latest session log to understand recent progress")
    lines.append("3. Continue from the next unchecked step in the plan")

    return "\n".join(lines)


def main():
    # Read hook input (unused but consumed from stdin)
    sys.stdin.read()

    phash = project_hash()
    state_file = SESSIONS_BASE / phash / "pre-compact-state.json"

    if not state_file.is_file():
        # No pre-compact state found — nothing to restore
        sys.exit(0)

    state = json.loads(state_file.read_text(encoding="utf-8"))

    # Re-scan disk for live plan state
    live_plan = rescan_active_plan()

    # Build restoration message
    message = format_restoration(state, live_plan)

    # Delete state file after reading
    state_file.unlink()

    # Output as additionalContext
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
