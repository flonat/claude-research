"""Validate a skill directory against conventions.

Checks frontmatter, naming, description quality, body length,
referenced files, and allowed_tools format.

Usage:
    uv run python validate_skill.py <skill-directory> [--strict] [--all]

Exit codes: 0 = valid, 1 = errors found, 2 = warnings promoted by --strict.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml not installed. Run: uv pip install pyyaml", file=sys.stderr)
    sys.exit(1)

_NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")
_PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
)
_KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "Bash",
    "AskUserQuestion", "Task", "WebFetch", "WebSearch",
    "NotebookEdit", "EnterPlanMode", "ExitPlanMode", "Skill",
}


def _split_frontmatter(content: str) -> tuple[str, str]:
    """Split SKILL.md into frontmatter string and body."""
    lines = content.split("\n")
    start = 0
    while start < len(lines) and lines[start].strip() == "":
        start += 1
    if start >= len(lines) or lines[start].strip() != "---":
        return "", ""
    close = None
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return "", ""
    frontmatter_str = "\n".join(lines[start + 1 : close])
    body = "\n".join(lines[close + 1 :]).strip()
    return frontmatter_str, body


def _parse_yaml(frontmatter_str: str) -> dict | None:
    """Parse YAML frontmatter."""
    try:
        data = yaml.safe_load(frontmatter_str)
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def _has_placeholder(text: str) -> bool:
    return any(p.search(text) for p in _PLACEHOLDER_PATTERNS)


def _count_body_lines(body: str) -> int:
    return len([line for line in body.split("\n") if line.strip()])


def validate_skill(path: Path, strict: bool = False) -> tuple[bool, list[str], list[str]]:
    """Validate a skill directory.

    Returns (is_valid, errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []
    skill_dir = Path(path)

    # --- SKILL.md exists ---
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found.")
        return (False, errors, warnings)

    content = skill_md.read_text()

    # --- Valid frontmatter ---
    frontmatter_str, body = _split_frontmatter(content)
    if not frontmatter_str:
        errors.append("Missing or invalid YAML frontmatter (needs --- delimiters).")
        return (False, errors, warnings)

    data = _parse_yaml(frontmatter_str)
    if data is None:
        errors.append("Frontmatter is not valid YAML.")
        return (False, errors, warnings)

    # --- Body non-empty ---
    if not body:
        errors.append("Body (system prompt) is empty.")

    # --- Name present and valid ---
    name = data.get("name")
    if not name or not isinstance(name, str):
        errors.append("Required field 'name' is missing.")
    elif not _NAME_PATTERN.match(name):
        errors.append(f"Invalid name '{name}': must be lowercase alphanumeric + hyphens, 1-64 chars.")
    else:
        if name != skill_dir.name:
            errors.append(f"Name '{name}' does not match directory '{skill_dir.name}'.")

    if isinstance(name, str) and _has_placeholder(name):
        errors.append(f"Name '{name}' contains placeholder text.")

    # --- Description present and useful ---
    description = data.get("description")
    if not description or not isinstance(description, str):
        errors.append("Required field 'description' is missing.")
    else:
        desc_clean = description.replace("\n", " ").strip()
        if len(desc_clean) > 1024:
            errors.append(f"Description too long ({len(desc_clean)} chars, max 1024).")
        if _has_placeholder(desc_clean):
            errors.append("Description contains placeholder text.")
        if len(desc_clean) < 20:
            warnings.append(f"Description very short ({len(desc_clean)} chars) — may not trigger correctly.")
        if not any(kw in desc_clean.lower() for kw in ("use when", "use for", "use this", "when ")):
            warnings.append("Description lacks activation hint (e.g., 'Use when...'). May not trigger reliably.")

    # --- Body quality ---
    if body:
        line_count = _count_body_lines(body)
        if line_count < 5:
            warnings.append(f"Body is very short ({line_count} non-empty lines).")
        if line_count > 300:
            warnings.append(f"Body is long ({line_count} lines). Consider moving detail to references/.")

    # --- allowed_tools / allowed-tools ---
    tools = data.get("allowed_tools") or data.get("allowed-tools")
    if tools and isinstance(tools, list):
        for tool in tools:
            if isinstance(tool, str):
                # Strip Bash(pattern) to just Bash for the check
                base = tool.split("(")[0]
                if base not in _KNOWN_TOOLS:
                    warnings.append(f"Unknown tool '{tool}' in allowed_tools.")

    # --- Referenced files exist ---
    refs_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    # Check for broken relative links in body (strip #anchors before checking)
    for match in re.finditer(r'\[.*?\]\(((?!http)[^)]+)\)', body):
        rel_path = match.group(1)
        file_path_str = rel_path.split("#")[0]  # strip fragment
        if not file_path_str or file_path_str.startswith("<"):  # skip placeholders like <name>.md
            continue
        full_path = skill_dir / file_path_str
        if not full_path.exists():
            errors.append(f"Broken link: '{rel_path}' — file '{file_path_str}' does not exist.")

    # Check that references/ and scripts/ dirs, if linked to, actually exist
    # Only flag when there's a markdown link pointing into these dirs
    refs_link = re.search(r'\]\(references/', body)
    scripts_link = re.search(r'\]\(scripts/', body)
    if refs_link and not refs_dir.exists():
        warnings.append("Body links to 'references/' but directory does not exist.")
    if scripts_link and not scripts_dir.exists():
        warnings.append("Body links to 'scripts/' but directory does not exist.")

    # --- Determine validity ---
    if strict:
        is_valid = len(errors) + len(warnings) == 0
    else:
        is_valid = len(errors) == 0

    return (is_valid, errors, warnings)


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def print_report(skill_path: Path, errors: list[str], warnings: list[str], strict: bool) -> None:
    print(f"\n  Validating: {skill_path.name}")

    if not errors and not warnings:
        print(f"  {_color('PASS', '32')}  All checks passed.\n")
        return

    for err in errors:
        print(f"  {_color('ERROR', '31')}  {err}")

    for warn in warnings:
        label = "ERROR" if strict else "WARN "
        color = "31" if strict else "33"
        print(f"  {_color(label, color)}  {warn}")

    total = len(errors) + (len(warnings) if strict else 0)
    if total > 0:
        print(f"  {_color(f'{total} issue(s)', '31')}\n")
    else:
        print(f"  {_color('PASS', '32')}  {len(warnings)} warning(s)\n")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate skill directories.")
    parser.add_argument("skill_directory", nargs="?", type=Path, help="Path to skill directory")
    parser.add_argument("--strict", action="store_true", help="Promote warnings to errors")
    parser.add_argument("--all", action="store_true", help="Validate all skills in the parent directory")
    args = parser.parse_args()

    if args.all:
        # Find skills root: if inside a skill dir, go up; otherwise use cwd
        if args.skill_directory:
            skills_root = args.skill_directory.resolve()
        else:
            skills_root = Path.cwd()

        total_errors = 0
        total_warnings = 0
        total_pass = 0
        total_fail = 0

        for child in sorted(skills_root.iterdir()):
            if not child.is_dir() or child.name == "shared" or child.name.startswith("."):
                continue
            skill_md = child / "SKILL.md"
            if not skill_md.exists():
                continue

            is_valid, errors, warnings = validate_skill(child, strict=args.strict)
            print_report(child, errors, warnings, strict=args.strict)
            total_errors += len(errors)
            total_warnings += len(warnings)
            if is_valid:
                total_pass += 1
            else:
                total_fail += 1

        print(f"  Summary: {total_pass} passed, {total_fail} failed, {total_warnings} warnings\n")
        return 1 if total_fail > 0 else 0

    if not args.skill_directory:
        parser.error("skill_directory is required unless --all is used")

    skill_path = args.skill_directory.resolve()
    if not skill_path.is_dir():
        print(f"Error: '{skill_path}' is not a directory.", file=sys.stderr)
        return 1

    is_valid, errors, warnings = validate_skill(skill_path, strict=args.strict)
    print_report(skill_path, errors, warnings, strict=args.strict)

    if not is_valid:
        return 2 if (not errors and args.strict) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
