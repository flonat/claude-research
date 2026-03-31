#!/usr/bin/env python3
"""Count automation: scan filesystem for ground-truth infrastructure counts
and propagate them across all documentation files.

Usage:
    uv run python .scripts/count_inventory.py [--check | --fix] [--json]

Exit codes:
    0  All counts match (--check) or fixes applied (--fix)
    1  Stale counts found (--check)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

# ── Ground truth ─────────────────────────────────────────────────────────

# Hardcoded constants (not derivable from filesystem)
NOTION_DBS = 6
RESOURCE_REPOS = 43  # 15 academics + 23 general + 5 bibliography
# Note: skill count is derived from filesystem (skills/*/SKILL.md), not hardcoded


def get_ground_truth(root: Path) -> dict[str, int]:
    """Derive infrastructure counts from the filesystem."""
    skills = len(list((root / "skills").glob("*/SKILL.md")))
    # Also count skill.md (lowercase) to avoid missing any
    skills += len([p for p in (root / "skills").glob("*/skill.md")
                   if not any(s.name == "SKILL.md" for s in p.parent.iterdir())])
    agents = len(list((root / ".claude" / "agents").glob("*.md")))
    rules = len(list((root / ".claude" / "rules").glob("*.md")))
    hooks_sh = len(list((root / "hooks").glob("*.sh")))
    hooks_py = len(list((root / "hooks").glob("*.py")))
    hooks = hooks_sh + hooks_py
    return {
        "skills": skills,
        "agents": agents,
        "rules": rules,
        "hooks": hooks,
    }


# ── Scan configuration ──────────────────────────────────────────────────

# Files to scan (relative to repo root)
SCAN_FILES = [
    "CLAUDE.md",
    "README.md",
    "docs/skills.md",
    "docs/rules.md",
    "docs/hooks.md",
    "docs/agents.md",
    "docs/system.md",
    "docs/installation.md",
    ".context/projects/_index.md",
    "skills/shared/skill-index.md",
    "docs/user-manual/user-manual.tex",
    "docs/setup-overview/setup-overview.tex",
]

# Lines matching these patterns are EXCLUDED from replacement.
# They are historical log entries, category subtotals, or external references.
EXCLUDE_LINE_PATTERNS = [
    re.compile(r"\b\d+ to \d+ skills"),  # "55 to 62 skills" changelog
    re.compile(r"Added \d+ new skills"),  # "Added 7 new skills" changelog
    re.compile(r"\d+ agents \+ multiple skills"),  # changelog
    re.compile(r"hugo|sant.anna|clo-author", re.IGNORECASE),  # external refs
    re.compile(r"shared/"),  # "shared/" references
    re.compile(r"^\s*\|.*category", re.IGNORECASE),  # table rows with category subtotals
    re.compile(r"Research & Writing|Task Management.*Code|Publishing & Submission|Utilities", re.IGNORECASE),  # skill category subtotal lines
    re.compile(r"^\s*#"),  # comment-only lines in code blocks
    re.compile(r"Referee.2 agent performs"),  # prose about what an agent does
    re.compile(r"Referee.2 agent .+never"),  # prose about agent behavior
    re.compile(r"Referee.2 Agent", re.IGNORECASE),  # section title "The Referee~2 Agent"
]


@dataclass
class Mismatch:
    file: str
    line_num: int
    found: int
    expected: int
    context: str  # the line text
    count_key: str  # skills, agents, rules, hooks


# Pattern tuples: (compiled regex, count_key)
# Each regex has a single capture group for the number.
# All patterns are case-insensitive to catch "81 Skills", "25 Hooks" etc.
SCAN_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(\d+)\s+skills?\b", re.IGNORECASE), "skills"),
    (re.compile(r"(\d+)\s+skill definitions?\b", re.IGNORECASE), "skills"),
    (re.compile(r"(\d+)\s+reusable\b", re.IGNORECASE), "skills"),
    (re.compile(r"(\d+)\s+agents?\b", re.IGNORECASE), "agents"),
    (re.compile(r"(\d+)\s+agent definitions?\b", re.IGNORECASE), "agents"),
    (re.compile(r"(\d+)\s+rules?\b", re.IGNORECASE), "rules"),
    (re.compile(r"(\d+)\s+auto-loaded\b", re.IGNORECASE), "rules"),
    (re.compile(r"(\d+)\s+hooks?\b", re.IGNORECASE), "hooks"),
    (re.compile(r"(\d+)\s+hook scripts?\b", re.IGNORECASE), "hooks"),
    # Heading format: ## Hooks (N scripts)
    (re.compile(r"\((\d+)\s+scripts?\)"), "hooks"),
]


def _is_excluded(line: str) -> bool:
    """Return True if the line should be skipped."""
    return any(p.search(line) for p in EXCLUDE_LINE_PATTERNS)


def scan(root: Path, truth: dict[str, int]) -> list[Mismatch]:
    """Scan all registered files for stale counts."""
    mismatches: list[Mismatch] = []
    seen: set[tuple[str, int, str]] = set()  # (file, line_num, count_key)

    for rel_path in SCAN_FILES:
        fpath = root / rel_path
        if not fpath.exists():
            continue

        lines = fpath.read_text(encoding="utf-8").splitlines()
        for line_idx, line in enumerate(lines, start=1):
            if _is_excluded(line):
                continue

            for pattern, key in SCAN_PATTERNS:
                for m in pattern.finditer(line):
                    dedup_key = (rel_path, line_idx, key)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    found = int(m.group(1))
                    expected = truth[key]
                    if found != expected:
                        mismatches.append(
                            Mismatch(
                                file=rel_path,
                                line_num=line_idx,
                                found=found,
                                expected=expected,
                                context=line.strip(),
                                count_key=key,
                            )
                        )

    return mismatches


def fix(root: Path, mismatches: list[Mismatch]) -> int:
    """Apply fixes for all mismatches. Returns number of fixes applied."""
    # Group mismatches by file to minimise I/O
    by_file: dict[str, list[Mismatch]] = {}
    for mm in mismatches:
        by_file.setdefault(mm.file, []).append(mm)

    total_fixed = 0

    for rel_path, file_mismatches in by_file.items():
        fpath = root / rel_path
        lines = fpath.read_text(encoding="utf-8").splitlines()

        # Sort by line number descending so index shifts don't matter
        for mm in sorted(file_mismatches, key=lambda m: m.line_num, reverse=True):
            idx = mm.line_num - 1
            old_line = lines[idx]

            # Find the specific pattern match and replace the number
            new_line = old_line
            for pattern, key in SCAN_PATTERNS:
                if key != mm.count_key:
                    continue
                for m in pattern.finditer(old_line):
                    if int(m.group(1)) == mm.found:
                        # Replace just this occurrence
                        start, end = m.span(1)
                        new_line = (
                            new_line[:start] + str(mm.expected) + new_line[end:]
                        )
                        break
                if new_line != old_line:
                    break

            if new_line != old_line:
                lines[idx] = new_line
                total_fixed += 1

        fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return total_fixed


# ── CLI ──────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Count automation for infrastructure docs"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        help="Report stale counts (default)",
    )
    group.add_argument(
        "--fix", action="store_true", help="Fix stale counts in place"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    truth = get_ground_truth(root)
    mismatches = scan(root, truth)

    if args.json:
        data = {
            "ground_truth": truth,
            "constants": {
                "notion_dbs": NOTION_DBS,
                "resource_repos": RESOURCE_REPOS,
            },
            "mismatches": [asdict(m) for m in mismatches],
            "total_mismatches": len(mismatches),
        }
        print(json.dumps(data, indent=2))
        return 1 if mismatches and not args.fix else 0

    if args.fix:
        if not mismatches:
            print(f"All counts match ground truth: {truth}")
            return 0

        n_fixed = fix(root, mismatches)

        # Re-scan to verify
        remaining = scan(root, truth)
        print(f"Ground truth: {truth}")
        print(f"Fixed {n_fixed} stale counts across {len(set(m.file for m in mismatches))} files")
        if remaining:
            print(f"WARNING: {len(remaining)} counts still stale after fix:")
            for m in remaining:
                print(f"  {m.file}:{m.line_num}: found {m.found}, expected {m.expected}")
                print(f"    {m.context}")
            return 1
        print("All counts now match.")
        return 0

    # --check (default)
    print(f"Ground truth: {truth}")
    if not mismatches:
        print("All counts match.")
        return 0

    print(f"\n{len(mismatches)} stale counts found:\n")
    current_file = None
    for m in mismatches:
        if m.file != current_file:
            current_file = m.file
            print(f"  {m.file}:")
        print(f"    L{m.line_num}: {m.count_key} {m.found} → {m.expected}")
        print(f"      {m.context}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
