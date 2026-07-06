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

# All counts derived from the filesystem — no hardcoded constants.


def get_ground_truth(root: Path) -> dict[str, int]:
    """Derive infrastructure counts from the filesystem."""
    skills = len(list((root / "skills").glob("**/SKILL.md")))
    # Also count skill.md (lowercase) to avoid missing any
    skills += len([p for p in (root / "skills").glob("**/skill.md")
                   if not any(s.name == "SKILL.md" for s in p.parent.iterdir())])
    agents = len(list((root / ".claude" / "agents").glob("*.md")))
    rules = len(list((root / "rules").glob("*.md")))
    hooks_sh = len(list((root / "hooks").glob("*.sh")))
    hooks_py = len(list((root / "hooks").glob("*.py")))
    hooks_mjs = len(list((root / "hooks").glob("*.mjs")))
    hooks = hooks_sh + hooks_py + hooks_mjs

    # Resource repos: count top-level .git per category, not nested submodules.
    # academics/<author>/<repo>/.git → depth 4
    # general/<author>/<repo>/.git → depth 4
    # bibliography/<author>/<repo>/.git → depth 4
    # artifacts/<repo>/.git → depth 3
    resource_repos = 0
    resources_root = root / "resources"
    if resources_root.is_dir():
        # Two-level-deep categories
        for sub in ("academics", "general", "bibliography"):
            base = resources_root / sub
            if base.is_dir():
                resource_repos += sum(1 for p in base.glob("*/*/.git"))
        # One-level-deep category
        artifacts = resources_root / "artifacts"
        if artifacts.is_dir():
            resource_repos += sum(1 for p in artifacts.glob("*/.git"))

    # Packages: immediate subdirectories of packages/ (each is a package,
    # whether a nested git repo or a local-only dir).
    packages = 0
    packages_root = root / "packages"
    if packages_root.is_dir():
        packages = sum(
            1 for p in packages_root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )

    return {
        "skills": skills,
        "agents": agents,
        "rules": rules,
        "hooks": hooks,
        "resource_repos": resource_repos,
        "packages": packages,
    }


def list_packages(root: Path) -> list[str]:
    """Return the names of all package directories under packages/."""
    packages_root = root / "packages"
    if not packages_root.is_dir():
        return []
    return sorted(
        p.name for p in packages_root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def check_package_coverage(root: Path) -> list[str]:
    """Return package dirs that are NOT mentioned in docs/components/packages.md.

    Coverage is name-presence only (the package appears somewhere in the doc),
    which catches the common drift: a new package added under packages/ that
    nobody added to the catalogue.
    """
    doc = root / "docs" / "components" / "packages.md"
    if not doc.exists():
        return []
    text = doc.read_text(encoding="utf-8")
    missing = []
    for name in list_packages(root):
        # Word-boundary match so e.g. `pdf-clean` isn't matched by `pdf-cleaner`.
        if not re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text):
            missing.append(name)
    return missing


# ── Scan configuration ──────────────────────────────────────────────────

# Files to scan (relative to repo root)
SCAN_FILES = [
    "CLAUDE.md",
    "README.md",
    "docs/components/skills.md",
    "docs/components/rules.md",
    "docs/components/hooks.md",
    "docs/components/agents.md",
    "docs/components/packages.md",
    "docs/system.md",
    "docs/architecture.md",
    "docs/guides/installation.md",
    ".context/projects/_index.md",
    "skills/shared/skill-index.md",
    "docs/reference/user-manual/user-manual.tex",
    "docs/setup/setup-overview/setup-overview.tex",
]

# Lines matching these patterns are EXCLUDED from replacement.
# They are historical log entries, category subtotals, or external references.
EXCLUDE_LINE_PATTERNS = [
    re.compile(r"\b\d+ to \d+ skills"),  # "55 to 62 skills" changelog
    re.compile(r"Added \d+ new skills"),  # "Added 7 new skills" changelog
    re.compile(r"\d+ agents \+ multiple skills"),  # changelog
    re.compile(r"hugo|sant.anna|clo-author", re.IGNORECASE),  # external refs
    re.compile(r"driven by \d+ hooks", re.IGNORECASE),  # agent-memory row: "4 hooks" = agentmem hooks, NOT the global hook count (false-positive guard)
    re.compile(r"^\s*\|.*category", re.IGNORECASE),  # table rows with category subtotals
    re.compile(r"Research & Writing|Task Management & Code|Publishing & Submission|Utilities", re.IGNORECASE),  # skill category subtotal lines (literal '& Code'; an earlier greedy '.*Code' pattern matched an unrelated docs line ending in 'Code' and wrongly excluded its count line)
    # NOTE: shell-comment exclusion (lines starting with '#' inside ``` code
    # fences) is handled in scan() with fence-state tracking — NOT here — so that
    # markdown headers like '### Skills (191 total)' are scanned, not silently
    # dropped. The old blanket r"^\s*#" excluded every header and hid header counts.
    re.compile(r"Referee.2 agent performs"),  # prose about what an agent does
    re.compile(r"Referee.2 agent .+never"),  # prose about agent behavior
    re.compile(r"Referee.2 Agent", re.IGNORECASE),  # section title "The Referee~2 Agent"
    re.compile(r"Trail of Bits|linters? for agent", re.IGNORECASE),  # external tool counts
    re.compile(r"BasicTeX|TeX Live|scheme-full", re.IGNORECASE),  # "~80 packages" = TeX packages, not packages/
    re.compile(r"Absolute Dropbox path", re.IGNORECASE),  # architecture.md portability table: "8 agents / 12 skills use absolute paths" = subset metric, NOT the global total
    re.compile(r"Path-Scoped Rules|Always-Load(?:ed)? Rules", re.IGNORECASE),  # SUBSET headers: "### Path-Scoped Rules (21 rules)" is 21-of-60, NOT the total (only visible since headers became scannable)
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
    (re.compile(r"(\d+)\s+packages?\b", re.IGNORECASE), "packages"),
    # Heading format: ## Hooks (N scripts)
    (re.compile(r"\((\d+)\s+scripts?\)"), "hooks"),
    # Heading format: "### Skills (N total)" — preceded by ### + "Skills"
    # Disambiguated by the immediately-preceding "Skills"/"Agents"/etc. token,
    # not the parenthesised number alone (which is too generic).
    # `total` need not be immediately followed by `)` — the header
    # "## Rules (54 total — 34 always-load, 20 path-scoped)" continues with an
    # em-dash breakdown, so anchor on the `total` word, not the closing paren.
    (re.compile(r"Skills?\s*\((\d+)\s+total\b", re.IGNORECASE), "skills"),
    (re.compile(r"Agents?\s*\((\d+)\s+total\b", re.IGNORECASE), "agents"),
    (re.compile(r"Rules?\s*\((\d+)\s+total\b", re.IGNORECASE), "rules"),
    (re.compile(r"Hooks?\s*\((\d+)\s+total\b", re.IGNORECASE), "hooks"),
    # LaTeX longtable rows: "<Keyword> & \filepath{...} & <count> \\"
    # The Component Manifest in user-manual.tex puts the keyword in the
    # first column and the count in the last, so the standard "<num> <kw>"
    # patterns above miss them.
    (re.compile(r"^\s*Skills?\s*&[^&]*&\s*(\d+)\s*\\\\", re.IGNORECASE), "skills"),
    (re.compile(r"^\s*(?:Global\s+)?Agents?\s*&[^&]*&\s*(\d+)\s*\\\\", re.IGNORECASE), "agents"),
    (re.compile(r"^\s*Hooks?\s*&[^&]*&\s*(\d+)\s*\\\\", re.IGNORECASE), "hooks"),
    (re.compile(r"^\s*Rules?\s*&[^&]*&\s*(\d+)\s*\\\\", re.IGNORECASE), "rules"),
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
        in_fence = False
        for line_idx, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            # Shell comments inside a ``` code fence are not doc counts — skip.
            # Markdown headers ('### Skills (191 total)') are NOT in a fence, so
            # they stay scanned (that's the fix for the hidden header-count bug).
            if in_fence and stripped.startswith("#"):
                continue
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
    uncovered_packages = check_package_coverage(root)

    if args.json:
        data = {
            "ground_truth": truth,
            "mismatches": [asdict(m) for m in mismatches],
            "total_mismatches": len(mismatches),
            "uncovered_packages": uncovered_packages,
        }
        print(json.dumps(data, indent=2))
        problems = bool(mismatches or uncovered_packages)
        return 1 if problems and not args.fix else 0

    if args.fix:
        if not mismatches:
            print(f"All counts match ground truth: {truth}")
            if uncovered_packages:
                print(
                    f"NOTE: {len(uncovered_packages)} package(s) missing from "
                    f"packages.md (not auto-fixable — add a description manually): "
                    + ", ".join(uncovered_packages)
                )
                return 1
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
    if not mismatches and not uncovered_packages:
        print("All counts match.")
        return 0

    if mismatches:
        print(f"\n{len(mismatches)} stale counts found:\n")
        current_file = None
        for m in mismatches:
            if m.file != current_file:
                current_file = m.file
                print(f"  {m.file}:")
            print(f"    L{m.line_num}: {m.count_key} {m.found} → {m.expected}")
            print(f"      {m.context}")

    if uncovered_packages:
        print(
            f"\n{len(uncovered_packages)} package(s) under packages/ "
            f"missing from docs/components/packages.md:\n"
        )
        for name in uncovered_packages:
            print(f"    - {name}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
