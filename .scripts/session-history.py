#!/usr/bin/env python3
"""Query session history from skill-outcomes.jsonl via SQLite.

Indexes the JSONL file into an in-memory SQLite database for fast queries.
The DB is rebuilt on each invocation (the source file is small).

Usage:
    uv run python .scripts/session-history.py                    # show all
    uv run python .scripts/session-history.py --skill proofread  # filter by skill
    uv run python .scripts/session-history.py --project Task-Management
    uv run python .scripts/session-history.py --since 2026-03-15
    uv run python .scripts/session-history.py --outcome error
    uv run python .scripts/session-history.py --stats            # summary stats
    uv run python .scripts/session-history.py --top-skills       # most-used skills
    uv run python .scripts/session-history.py --by-project       # breakdown by project
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


JSONL_PATH = Path.home() / ".claude" / "ecc" / "skill-outcomes.jsonl"


def load_db() -> sqlite3.Connection:
    """Load JSONL into an in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            outcome TEXT NOT NULL,
            session TEXT,
            project TEXT,
            note TEXT
        )
    """)
    conn.execute("CREATE INDEX idx_skill ON outcomes(skill)")
    conn.execute("CREATE INDEX idx_project ON outcomes(project)")
    conn.execute("CREATE INDEX idx_timestamp ON outcomes(timestamp)")
    conn.execute("CREATE INDEX idx_outcome ON outcomes(outcome)")

    if not JSONL_PATH.exists():
        print(f"No history file at {JSONL_PATH}", file=sys.stderr)
        return conn

    with open(JSONL_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                conn.execute(
                    "INSERT INTO outcomes (skill, timestamp, outcome, session, project, note) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        row.get("skill", ""),
                        row.get("timestamp", ""),
                        row.get("outcome", ""),
                        row.get("session", ""),
                        row.get("project", ""),
                        row.get("note", ""),
                    ),
                )
            except (json.JSONDecodeError, KeyError):
                continue
    conn.commit()
    return conn


def fmt_table(rows: list[sqlite3.Row], columns: list[str]) -> str:
    """Format rows as a simple table."""
    if not rows:
        return "No results."

    widths = [len(c) for c in columns]
    str_rows = []
    for row in rows:
        vals = [str(row[c] or "") for c in columns]
        str_rows.append(vals)
        for i, v in enumerate(vals):
            widths[i] = max(widths[i], len(v))

    header = "  ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    sep = "  ".join("-" * widths[i] for i in range(len(columns)))
    lines = [header, sep]
    for vals in str_rows:
        lines.append("  ".join(vals[i].ljust(widths[i]) for i in range(len(columns))))
    return "\n".join(lines)


def cmd_list(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """List outcomes with optional filters."""
    clauses = []
    params: list[str] = []

    if args.skill:
        clauses.append("skill LIKE ?")
        params.append(f"%{args.skill}%")
    if args.project:
        clauses.append("project LIKE ?")
        params.append(f"%{args.project}%")
    if args.outcome:
        clauses.append("outcome = ?")
        params.append(args.outcome)
    if args.since:
        clauses.append("timestamp >= ?")
        params.append(args.since)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT timestamp, skill, project, outcome, note FROM outcomes {where} ORDER BY timestamp DESC"

    if args.limit:
        query += f" LIMIT {args.limit}"

    rows = conn.execute(query, params).fetchall()
    print(fmt_table(rows, ["timestamp", "skill", "project", "outcome", "note"]))


def cmd_stats(conn: sqlite3.Connection, _args: argparse.Namespace) -> None:
    """Show summary statistics."""
    total = conn.execute("SELECT COUNT(*) as n FROM outcomes").fetchone()["n"]
    success = conn.execute("SELECT COUNT(*) as n FROM outcomes WHERE outcome='success'").fetchone()["n"]
    error = conn.execute("SELECT COUNT(*) as n FROM outcomes WHERE outcome='error'").fetchone()["n"]
    partial = conn.execute("SELECT COUNT(*) as n FROM outcomes WHERE outcome='partial'").fetchone()["n"]
    skills = conn.execute("SELECT COUNT(DISTINCT skill) as n FROM outcomes").fetchone()["n"]
    projects = conn.execute("SELECT COUNT(DISTINCT project) as n FROM outcomes WHERE project != ''").fetchone()["n"]

    first = conn.execute("SELECT MIN(timestamp) as t FROM outcomes").fetchone()["t"]
    last = conn.execute("SELECT MAX(timestamp) as t FROM outcomes").fetchone()["t"]

    print(f"Total invocations:  {total}")
    print(f"Unique skills:      {skills}")
    print(f"Unique projects:    {projects}")
    print(f"Success:            {success} ({100*success//max(total,1)}%)")
    print(f"Error:              {error} ({100*error//max(total,1)}%)")
    print(f"Partial:            {partial} ({100*partial//max(total,1)}%)")
    print(f"First recorded:     {first or 'N/A'}")
    print(f"Last recorded:      {last or 'N/A'}")


def cmd_top_skills(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    """Show most-used skills."""
    limit = args.limit or 20
    rows = conn.execute(
        """SELECT skill,
                  COUNT(*) as invocations,
                  SUM(CASE WHEN outcome='success' THEN 1 ELSE 0 END) as ok,
                  SUM(CASE WHEN outcome='error' THEN 1 ELSE 0 END) as err
           FROM outcomes GROUP BY skill ORDER BY invocations DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    print(fmt_table(rows, ["skill", "invocations", "ok", "err"]))


def cmd_by_project(conn: sqlite3.Connection, _args: argparse.Namespace) -> None:
    """Show breakdown by project."""
    rows = conn.execute(
        """SELECT project,
                  COUNT(*) as invocations,
                  COUNT(DISTINCT skill) as skills_used,
                  MAX(timestamp) as last_activity
           FROM outcomes WHERE project != '' GROUP BY project ORDER BY invocations DESC""",
    ).fetchall()
    print(fmt_table(rows, ["project", "invocations", "skills_used", "last_activity"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Query session history")
    parser.add_argument("--skill", help="Filter by skill name (substring match)")
    parser.add_argument("--project", help="Filter by project name (substring match)")
    parser.add_argument("--outcome", choices=["success", "error", "partial"], help="Filter by outcome")
    parser.add_argument("--since", help="Show entries since date (ISO format, e.g. 2026-03-15)")
    parser.add_argument("--limit", type=int, help="Max rows to show")
    parser.add_argument("--stats", action="store_true", help="Show summary statistics")
    parser.add_argument("--top-skills", action="store_true", help="Show most-used skills")
    parser.add_argument("--by-project", action="store_true", help="Show breakdown by project")
    args = parser.parse_args()

    conn = load_db()

    if args.stats:
        cmd_stats(conn, args)
    elif args.top_skills:
        cmd_top_skills(conn, args)
    elif args.by_project:
        cmd_by_project(conn, args)
    else:
        cmd_list(conn, args)


if __name__ == "__main__":
    main()
