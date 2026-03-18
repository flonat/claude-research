#!/usr/bin/env python3
"""
Skill Log Miner — Extracts skill invocation data from session logs.

Fallback observation method when the Skill tool doesn't emit hook events.
Scans log/*.md files for `/skill-name` references, extracts structured
invocation records, and writes to ~/.claude/ecc/observations-*.jsonl.

Idempotent: tracks which log files have been mined in a watermark file.
Re-running only processes new logs.

Usage:
    uv run python .scripts/skill-log-miner.py              # mine new logs
    uv run python .scripts/skill-log-miner.py --backfill    # re-mine all logs
    uv run python .scripts/skill-log-miner.py --dry-run     # show what would be mined
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
ECC_DIR = Path.home() / ".claude" / "ecc"
WATERMARK_FILE = ECC_DIR / "miner-watermark.json"

# Where to find session logs — resolve from config
def get_task_mgmt() -> Path | None:
    cfg = Path.home() / ".config" / "task-mgmt" / "path"
    if cfg.exists():
        p = Path(cfg.read_text().strip())
        if p.is_dir():
            return p
    return None

# Also check project-specific log directories
def find_log_dirs() -> list[Path]:
    dirs = []
    tm = get_task_mgmt()
    if tm:
        log_dir = tm / "log"
        if log_dir.is_dir():
            dirs.append(log_dir)
    return dirs

# Skill name pattern: `/skill-name` in backticks or at line start
# Matches: `/proofread`, `/latex-autofix`, `/bib-validate`
# Excludes: `/path/to/file`, `/dev/null`, `/usr/bin`, `/tmp/`
SKILL_PATTERN = re.compile(
    r'`/([a-z][a-z0-9-]+)`'          # backtick-quoted: `/proofread`
    r'|(?:^|\s)/([a-z][a-z0-9-]+)'   # bare: /proofread at line start or after space
    , re.MULTILINE
)

# Known non-skill patterns to exclude
NON_SKILLS = {
    "dev", "tmp", "usr", "bin", "etc", "var", "opt", "home",
    "Users", "Library", "Applications", "System", "Volumes",
    "clear", "help", "compact", "cost", "doctor", "init",
    "login", "logout", "status", "version", "model",
}

# Date pattern from log filenames: YYYY-MM-DD-HHMM.md or YYYY-MM-DD-HHMM-compact.md
LOG_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})")

# Project header in session logs
PROJECT_RE = re.compile(r"^## Project:\s*(.+)", re.MULTILINE)


def sha256_prefix(value: str, length: int = 12) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:length]


def load_known_skills() -> set[str]:
    """Load valid skill names from ~/.claude/skills/."""
    skills_dir = Path.home() / ".claude" / "skills"
    if not skills_dir.is_dir():
        return set()
    return {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}


def extract_skills_from_log(filepath: Path, known_skills: set[str]) -> list[dict]:
    """Extract skill invocations from a session log file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    # Skip compact logs (auto-generated, minimal skill data)
    if "-compact" in filepath.name:
        return []

    # Extract date from filename
    date_match = LOG_DATE_RE.search(filepath.stem)
    if not date_match:
        return []

    date_str = date_match.group(1)
    hour = date_match.group(2)
    minute = date_match.group(3)
    try:
        log_date = datetime.strptime(f"{date_str}T{hour}:{minute}:00", "%Y-%m-%dT%H:%M:%S")
        log_date = log_date.replace(tzinfo=timezone.utc)
    except ValueError:
        return []

    # Extract project name
    project_match = PROJECT_RE.search(content)
    project_label = project_match.group(1).strip() if project_match else "unknown"

    # Find all skill references
    found_skills: dict[str, int] = {}
    for match in SKILL_PATTERN.finditer(content):
        skill_name = match.group(1) or match.group(2)
        if not skill_name:
            continue

        # Filter out non-skills
        if skill_name in NON_SKILLS:
            continue
        if len(skill_name) < 2:
            continue

        # Prefer known skills, but also accept plausible names
        # (handles renamed/deleted skills in historical logs)
        if skill_name in known_skills or len(skill_name) >= 3:
            found_skills[skill_name] = found_skills.get(skill_name, 0) + 1

    # Create events
    events = []
    for skill_name, mention_count in found_skills.items():
        # Validate against known skills (strict mode for non-obvious names)
        if skill_name not in known_skills and len(skill_name) < 5:
            continue

        event = {
            "schema": "skill-event.v1",
            "phase": "mined",
            "skill": skill_name,
            "session_hash": sha256_prefix(filepath.name),
            "timestamp": log_date.isoformat(),
            "project_label": project_label,
            "project_hash": sha256_prefix(project_label),
            "source_file": str(filepath.name),
            "mention_count": mention_count,
            "agent_context": "direct",
        }
        events.append(event)

    return events


def load_watermark() -> dict:
    """Load the watermark file tracking which logs have been mined."""
    if WATERMARK_FILE.exists():
        try:
            return json.loads(WATERMARK_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"mined_files": [], "last_run": None}


def save_watermark(watermark: dict):
    """Save the watermark file."""
    ECC_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(ECC_DIR, 0o700)
    old_umask = os.umask(0o077)
    try:
        WATERMARK_FILE.write_text(json.dumps(watermark, indent=2))
    finally:
        os.umask(old_umask)


def write_events(events: list[dict]):
    """Write events to daily JSONL files."""
    if not events:
        return

    ECC_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(ECC_DIR, 0o700)

    # Group events by date (from their timestamp)
    by_date: dict[str, list[dict]] = {}
    for event in events:
        try:
            ts = datetime.fromisoformat(event["timestamp"])
            date_key = ts.strftime("%Y-%m-%d")
        except (KeyError, ValueError):
            date_key = datetime.now().strftime("%Y-%m-%d")
        by_date.setdefault(date_key, []).append(event)

    old_umask = os.umask(0o077)
    try:
        for date_key, date_events in by_date.items():
            filepath = ECC_DIR / f"observations-{date_key}.jsonl"
            with open(filepath, "a") as f:
                for event in date_events:
                    f.write(json.dumps(event, separators=(",", ":")) + "\n")
    finally:
        os.umask(old_umask)


def main():
    parser = argparse.ArgumentParser(description="Mine session logs for skill invocations")
    parser.add_argument("--backfill", action="store_true", help="Re-mine all logs (ignore watermark)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be mined without writing")
    args = parser.parse_args()

    known_skills = load_known_skills()
    if not known_skills:
        print("Warning: no skills found in ~/.claude/skills/", file=sys.stderr)

    log_dirs = find_log_dirs()
    if not log_dirs:
        print("No log directories found.", file=sys.stderr)
        sys.exit(1)

    watermark = load_watermark()
    mined_set = set(watermark.get("mined_files", [])) if not args.backfill else set()

    # Collect all log files
    all_logs = []
    for log_dir in log_dirs:
        for filepath in sorted(log_dir.glob("*.md")):
            if filepath.name not in mined_set:
                all_logs.append(filepath)

    if not all_logs:
        print("No new session logs to mine.")
        return

    # Mine each log
    total_events = 0
    total_skills = set()
    all_events = []
    newly_mined = []

    for filepath in all_logs:
        events = extract_skills_from_log(filepath, known_skills)
        if events:
            all_events.extend(events)
            total_events += len(events)
            for e in events:
                total_skills.add(e["skill"])
            if args.dry_run:
                skills_in_log = [e["skill"] for e in events]
                print(f"  {filepath.name}: {', '.join(skills_in_log)}")
        newly_mined.append(filepath.name)

    if args.dry_run:
        print(f"\nDry run: {total_events} events from {len(newly_mined)} logs, "
              f"{len(total_skills)} unique skills")
        return

    # Write events
    write_events(all_events)

    # Update watermark
    mined_set.update(newly_mined)
    watermark["mined_files"] = sorted(mined_set)
    watermark["last_run"] = datetime.now(timezone.utc).isoformat()
    save_watermark(watermark)

    print(f"Mined {total_events} skill references from {len(newly_mined)} logs "
          f"({len(total_skills)} unique skills)")


if __name__ == "__main__":
    main()
