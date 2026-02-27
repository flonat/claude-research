#!/usr/bin/env python3
"""context-monitor.py
PostToolUse hook — tracks tool call count as a heuristic for context usage.

Fires on Bash|Task tool calls. Uses tool-call counting as a proxy for context
window consumption (150 tool calls ~ 100% context).

Three thresholds:
- 60% (~90 calls): Info — suggest saving key state
- 80% (~120 calls): Warning — auto-compact approaching
- 90% (~135 calls): Critical — complete current task

Each warning fires once per session. 60s throttle below warning level.
Outputs as systemMessage (non-blocking).
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

# --- Configuration ---
MAX_TOOL_CALLS = 150  # Conservative: 150 calls ~ 100% context
THRESHOLDS = [
    (0.90, "critical", "Context at ~90%. Complete current task. Run `/context-status` to review preservation state."),
    (0.80, "warning", "Context at ~80%. Auto-compact approaching. Ensure plan + session log are current."),
    (0.60, "info", "Context at ~60%. Consider saving key state with `/update-focus` or `/session-log`."),
]
THROTTLE_SECONDS = 60  # Minimum seconds between info-level messages

# --- Paths ---
SESSIONS_BASE = Path.home() / ".claude" / "sessions"


def project_hash() -> str:
    """Deterministic hash of the project directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    return hashlib.sha256(project_dir.encode()).hexdigest()[:12]


def session_dir() -> Path:
    """Get or create the session state directory."""
    d = SESSIONS_BASE / project_hash()
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_state(sdir: Path) -> dict:
    """Load the monitor state file, or return defaults."""
    state_file = sdir / "context-monitor-state.json"
    if state_file.is_file():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"tool_calls": 0, "fired": [], "last_message_time": 0}


def save_state(sdir: Path, state: dict) -> None:
    """Persist monitor state."""
    state_file = sdir / "context-monitor-state.json"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    hook_input = json.loads(sys.stdin.read())

    sdir = session_dir()
    state = load_state(sdir)

    # Increment call count
    state["tool_calls"] = state.get("tool_calls", 0) + 1
    count = state["tool_calls"]
    pct = count / MAX_TOOL_CALLS

    fired = set(state.get("fired", []))
    now = time.time()
    last_msg = state.get("last_message_time", 0)

    message = None

    for threshold, level, msg in THRESHOLDS:
        if pct >= threshold and level not in fired:
            message = msg
            fired.add(level)
            state["last_message_time"] = now
            break

    # Throttle: don't emit info-level messages more than once per THROTTLE_SECONDS
    if message and "info" in fired and len(fired) == 1:
        if (now - last_msg) < THROTTLE_SECONDS and last_msg > 0:
            message = None

    state["fired"] = list(fired)
    save_state(sdir, state)

    if message:
        output = {"systemMessage": f"[Context Monitor] {message}"}
        print(json.dumps(output))
        sys.exit(2)  # Exit code 2 = message visible in transcript
    else:
        # Silent — no output needed
        print(json.dumps({}))
        sys.exit(0)


if __name__ == "__main__":
    main()
