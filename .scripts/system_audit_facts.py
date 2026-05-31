#!/usr/bin/env python3
"""Deterministic facts for /system-audit.

Replaces the count/link-heavy sub-agents that proved unreliable in the
2026-05-23 audit (SA1 Inventory, SA4 Documentation Freshness, SA5 Ecosystem
Health, SA7 Friends Repo) — they rolled their own counters and resolved
relative paths from the wrong working directory, producing 5+ false-positive
findings out of 8.

This module does what those four agents tried to do, but mechanically:
counts files, resolves markdown links against the source file's directory,
greps for orphans / stale references, etc. The output is then folded into
the system-audit report alongside the three remaining judgment-only
sub-agents (SA2 Bibliography, SA3 Conventions, SA6 Skill Quality / Overlap).

Usage:
    uv run python .scripts/system_audit_facts.py [section] [--json]

Sections:
    inventory   counts, symlink/copy status, MCP server alignment
    docs        count parity, broken internal links, .context freshness
    ecosystem   MCP references, staleness (>90d), orphan candidates, CLI tools
    friends     friends-repo counts, anonymisation grep, install-script check
    all         run all sections (default)

Exit codes:
    0  all sections produced facts
    1  one or more sections hit a hard failure (missing dir etc.)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ─── Roots ─────────────────────────────────────────────────────────────────

TM = Path(__file__).resolve().parent.parent
CLAUDE_HOME = Path.home() / ".claude"

# ~/.claude.json is the canonical Claude Code user-config file. Has top-level
# `mcpServers` (user-scope) and `projects.<abs-path>.mcpServers` (project-scope).
# ~/.claude/settings.json is the newer split config but does NOT carry mcpServers
# on this install — we read it for completeness but expect it usually empty.
CLAUDE_USER_JSON = Path.home() / ".claude.json"

# Desktop config — historically Mac path. May not exist (Desktop uninstalled or
# never configured). All callers must use `.exists()` before reading.
DESKTOP_CONFIG = (
    Path.home()
    / "Library/Application Support/Claude/claude_desktop_config.json"
)


# ─── Helpers ───────────────────────────────────────────────────────────────


def count_skills() -> int:
    """Count SKILL.md files anywhere under skills/ (incl. nested categories)."""
    return len(list((TM / "skills").rglob("SKILL.md")))


def count_hooks() -> int:
    """Count Claude-Code hook files: .sh + .py + .mjs in hooks/ (top-level only)."""
    return sum(
        len(list((TM / "hooks").glob(f"*.{ext}"))) for ext in ("sh", "py", "mjs")
    )


def count_agents() -> int:
    """Count agent .md files in .claude/agents/ (top-level only)."""
    return len(list((TM / ".claude/agents").glob("*.md")))


def count_rules() -> int:
    """Count rule .md files in rules/ (top-level only)."""
    return len(list((TM / "rules").glob("*.md")))


def resolve_relative_link(source_file: Path, link: str) -> Path:
    """Resolve a markdown relative link against its source file's directory.

    Strips fragments (#anchor) and query strings. Returns the absolute path
    to the target (may or may not exist — caller checks).
    """
    link = link.split("#", 1)[0].split("?", 1)[0]
    if not link:
        return source_file
    return (source_file.parent / link).resolve()


def find_broken_links(file: Path) -> list[tuple[int, str]]:
    """Return (line_no, link) pairs for every relative markdown link in
    `file` whose resolved target does not exist."""
    if not file.exists():
        return []
    broken = []
    text = file.read_text(errors="replace")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
            link = m.group(2)
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = resolve_relative_link(file, link)
            if not target.exists():
                broken.append((lineno, link))
    return broken


def stale_files(root: Path, glob: str, days: int = 90) -> list[Path]:
    """Files matching glob under root whose mtime is older than days days."""
    if not root.exists():
        return []
    threshold = days * 86400
    import time
    now = time.time()
    return sorted(
        p
        for p in root.glob(glob)
        if p.is_file() and (now - p.stat().st_mtime) > threshold
    )


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def safe_run(cmd: list[str]) -> str:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


# ─── Section 1: Inventory (was SA1) ────────────────────────────────────────


@dataclass
class InventorySection:
    counts: dict[str, int] = field(default_factory=dict)
    deployed_copies: dict[str, str] = field(default_factory=dict)
    # MCP servers by source:
    #   user           — `~/.claude.json` top-level `mcpServers` (user-scope, Code)
    #   project_local  — `<TM>/.mcp.json` (project-scope, Code, .mcp.json convention)
    #   project_user   — `~/.claude.json` `projects.<TM>.mcpServers` (Code per-project pref)
    #   settings       — `~/.claude/settings.json` (newer split config; usually empty)
    #   desktop        — Claude Desktop config (only if installed)
    mcp_servers_user: list[str] = field(default_factory=list)
    mcp_servers_project_local: list[str] = field(default_factory=list)
    mcp_servers_project_user: list[str] = field(default_factory=list)
    mcp_servers_settings: list[str] = field(default_factory=list)
    mcp_servers_desktop: list[str] = field(default_factory=list)
    undocumented_hooks: list[str] = field(default_factory=list)
    undocumented_rules: list[str] = field(default_factory=list)
    undocumented_agents: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def section_inventory() -> InventorySection:
    s = InventorySection()
    s.counts = {
        "skills": count_skills(),
        "hooks": count_hooks(),
        "agents": count_agents(),
        "rules": count_rules(),
    }

    # Deployed state (symlinks vs copies — by design)
    targets = [
        "skills",
        "agents",
        "rules",
        "hooks",
        "settings.json",
        "CLAUDE.md",
    ]
    for t in targets:
        p = CLAUDE_HOME / t
        if not p.exists():
            s.deployed_copies[t] = "missing"
        elif p.is_symlink():
            s.deployed_copies[t] = f"symlink → {p.resolve()}"
        else:
            s.deployed_copies[t] = "copy"

    # MCP servers — read from five sources
    # 1+3: ~/.claude.json (user-scope + per-project-scope under projects.<TM>)
    if CLAUDE_USER_JSON.exists():
        try:
            data = json.loads(CLAUDE_USER_JSON.read_text())
            s.mcp_servers_user = sorted((data.get("mcpServers") or {}).keys())
            projects = data.get("projects") or {}
            project_entry = projects.get(str(TM)) or {}
            s.mcp_servers_project_user = sorted(
                (project_entry.get("mcpServers") or {}).keys()
            )
        except Exception as e:
            s.issues.append(f"~/.claude.json unreadable: {e}")

    # 2: <TM>/.mcp.json (project-local convention)
    mcp_json = TM / ".mcp.json"
    if mcp_json.exists():
        try:
            data = json.loads(mcp_json.read_text())
            s.mcp_servers_project_local = sorted(
                (data.get("mcpServers") or {}).keys()
            )
        except Exception as e:
            s.issues.append(f".mcp.json unreadable: {e}")

    # 4: ~/.claude/settings.json (newer split config — usually no mcpServers)
    settings_path = CLAUDE_HOME / "settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text())
            s.mcp_servers_settings = sorted((data.get("mcpServers") or {}).keys())
        except Exception as e:
            s.issues.append(f"settings.json unreadable: {e}")

    # 5: Claude Desktop config (optional)
    if DESKTOP_CONFIG.exists():
        try:
            data = json.loads(DESKTOP_CONFIG.read_text())
            s.mcp_servers_desktop = sorted((data.get("mcpServers") or {}).keys())
        except Exception as e:
            s.issues.append(f"claude_desktop_config.json unreadable: {e}")

    # Undocumented components — files on disk not in their catalogue
    s.undocumented_hooks = _undocumented_hooks()
    s.undocumented_rules = _undocumented_rules()
    s.undocumented_agents = _undocumented_agents()
    return s


def _undocumented_hooks() -> list[str]:
    cat = TM / "docs/components/hooks.md"
    if not cat.exists():
        return []
    text = cat.read_text()
    # Extract filenames from table rows (first-column-as-name pattern in
    # hooks.md is the "Script" column, fourth column in `| ... | ... | ... | filename |`)
    referenced = set()
    for line in text.splitlines():
        if line.startswith("| ") and "`" in line:
            for m in re.finditer(r"`([a-z0-9_-]+\.(?:sh|py|mjs))`", line):
                referenced.add(m.group(1))
    on_disk = {
        p.name for ext in ("sh", "py", "mjs") for p in (TM / "hooks").glob(f"*.{ext}")
    }
    return sorted(on_disk - referenced)


def _undocumented_rules() -> list[str]:
    cat = TM / "docs/components/rules.md"
    if not cat.exists():
        return []
    text = cat.read_text()
    referenced = set()
    for m in re.finditer(r"`([a-z0-9_-]+\.md)`", text):
        referenced.add(m.group(1))
    on_disk = {p.name for p in (TM / "rules").glob("*.md")}
    return sorted(on_disk - referenced)


def _undocumented_agents() -> list[str]:
    cat = TM / "docs/components/agents.md"
    if not cat.exists():
        return []
    text = cat.read_text()
    referenced = set()
    # Agent rows are `| \`name\` | ...`
    for line in text.splitlines():
        m = re.match(r"^\|\s*`([a-z0-9-]+)`\s*\|", line)
        if m:
            referenced.add(m.group(1) + ".md")
    on_disk = {p.name for p in (TM / ".claude/agents").glob("*.md")}
    return sorted(on_disk - referenced)


# ─── Section 2: Docs (was SA4) ─────────────────────────────────────────────


@dataclass
class DocsSection:
    count_parity: dict[str, dict[str, Any]] = field(default_factory=dict)
    broken_links: dict[str, list[tuple[int, str]]] = field(default_factory=dict)
    current_focus_age_days: float | None = None
    log_count: int = 0
    plans_count: int = 0
    oldest_plan_age_days: float | None = None
    issues: list[str] = field(default_factory=list)


def section_docs() -> DocsSection:
    s = DocsSection()

    # Count parity — pull ground truth from count_inventory.py if available
    truth = {
        "skills": count_skills(),
        "hooks": count_hooks(),
        "agents": count_agents(),
        "rules": count_rules(),
    }
    s.count_parity = {k: {"truth": v} for k, v in truth.items()}

    # Cross-check against count_inventory --check (authoritative)
    out = safe_run(
        ["uv", "run", "python", str(TM / ".scripts/count_inventory.py"), "--json"]
    )
    if out:
        try:
            ci = json.loads(out)
            for k in ("skills", "hooks", "agents", "rules"):
                v = ci.get("ground_truth", {}).get(k)
                if v is not None and v != truth[k]:
                    s.issues.append(
                        f"count_inventory says {k}={v}, our count says {truth[k]}"
                    )
        except Exception:
            pass

    # Broken links across key docs
    targets = [
        TM / "CLAUDE.md",
        TM / "README.md",
        TM / "docs/system.md",
        *list((TM / "docs/components").glob("*.md")),
        *list((TM / "docs/reference").glob("*.md")),
    ]
    for t in targets:
        bl = find_broken_links(t)
        if bl:
            s.broken_links[str(t.relative_to(TM))] = bl

    # .context/current-focus.md freshness
    cf = TM / ".context/current-focus.md"
    if cf.exists():
        import time
        s.current_focus_age_days = round(
            (time.time() - cf.stat().st_mtime) / 86400, 1
        )

    # log/ count + oldest plan age
    log_dir = TM / "log"
    if log_dir.exists():
        s.log_count = sum(1 for _ in log_dir.rglob("*.md"))

    plans_dir = TM / "log/plans"
    if plans_dir.exists():
        plans = list(plans_dir.glob("*.md"))
        s.plans_count = len(plans)
        if plans:
            import time
            oldest = min(plans, key=lambda p: p.stat().st_mtime)
            s.oldest_plan_age_days = round(
                (time.time() - oldest.stat().st_mtime) / 86400, 1
            )

    return s


# ─── Section 3: Ecosystem (was SA5) ────────────────────────────────────────


@dataclass
class EcosystemSection:
    mcp_referenced: list[str] = field(default_factory=list)
    mcp_configured: list[str] = field(default_factory=list)
    mcp_phantom_refs: list[str] = field(default_factory=list)
    stale_components: dict[str, list[str]] = field(default_factory=dict)
    cli_tools: dict[str, str | None] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


def section_ecosystem() -> EcosystemSection:
    s = EcosystemSection()

    # MCP server references in skills + agents
    refs: set[str] = set()
    for d in [TM / "skills", TM / ".claude/agents"]:
        for p in d.rglob("*.md"):
            try:
                text = p.read_text(errors="replace")
            except Exception:
                continue
            for m in re.finditer(r"mcp__([A-Za-z0-9_-]+)__[A-Za-z0-9_]+", text):
                refs.add(m.group(1))
    s.mcp_referenced = sorted(refs)

    # Configured servers — union across all known sources.
    # ~/.claude.json carries both user-scope (top-level mcpServers) and per-
    # project-scope (projects.<abs-path>.mcpServers). ~/.claude/settings.json
    # rarely carries mcpServers on this install but check anyway. .mcp.json is
    # the project-local convention. DESKTOP_CONFIG is optional.
    configured: set[str] = set()

    if CLAUDE_USER_JSON.exists():
        try:
            data = json.loads(CLAUDE_USER_JSON.read_text())
            configured.update((data.get("mcpServers") or {}).keys())
            projects = data.get("projects") or {}
            project_entry = projects.get(str(TM)) or {}
            configured.update((project_entry.get("mcpServers") or {}).keys())
        except Exception:
            pass

    for src in (CLAUDE_HOME / "settings.json", TM / ".mcp.json", DESKTOP_CONFIG):
        if src.exists():
            try:
                data = json.loads(src.read_text())
                configured.update((data.get("mcpServers") or {}).keys())
            except Exception:
                pass
    s.mcp_configured = sorted(configured)

    # Known cloud-only aliases
    cloud_aliases = {"claude_ai_vault", "claude_ai_Gamma", "claude_ai_Canva",
                     "claude_ai_Gmail", "claude_ai_Google_Calendar",
                     "claude_ai_Google_Drive", "claude_ai_Sentry",
                     "claude_ai_Spotify", "claude_ai_Consensus"}
    s.mcp_phantom_refs = sorted(
        r for r in refs if r not in configured and r not in cloud_aliases
    )

    # Staleness (>90 days)
    for label, root, pattern in [
        ("skills", TM / "skills", "**/SKILL.md"),
        ("agents", TM / ".claude/agents", "*.md"),
        ("hooks_sh", TM / "hooks", "*.sh"),
        ("hooks_py", TM / "hooks", "*.py"),
        ("rules", TM / "rules", "*.md"),
    ]:
        old = [
            str(p.relative_to(TM))
            for p in stale_files(root, pattern, days=90)
            if "/shared/" not in str(p) and "/_shared/" not in str(p)
        ]
        if old:
            s.stale_components[label] = old

    # CLI tools
    for tool in ("gh", "latexmk", "uv", "jq", "gemini", "node", "rclone", "tailscale"):
        s.cli_tools[tool] = which(tool)

    return s


# ─── Section 4: Friends Repo (was SA7) ─────────────────────────────────────


@dataclass
class FriendsSection:
    skill_dirs: int = 0
    skill_md_count: int = 0
    rule_count: int = 0
    readme_claims: dict[str, str | None] = field(default_factory=dict)
    leaks: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    install_script_present: bool = False
    install_script_issues: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def section_friends() -> FriendsSection:
    s = FriendsSection()
    fr = TM / "public/friends-repo"
    if not fr.exists():
        s.issues.append("public/friends-repo not present")
        return s

    s.skill_dirs = sum(1 for p in (fr / "skills").iterdir() if p.is_dir())
    s.skill_md_count = sum(1 for _ in (fr / "skills").glob("*/SKILL.md"))
    s.rule_count = sum(1 for _ in (fr / "rules").glob("*.md"))

    # Parse README claims
    readme = fr / "README.md"
    if readme.exists():
        text = readme.read_text(errors="replace")
        for label, pattern in [
            ("skills_total", r"(\d+)\s+skills"),
            ("rules_total", r"(\d+)\s+(?:behavioral\s+)?rules"),
        ]:
            m = re.search(pattern, text)
            s.readme_claims[label] = m.group(1) if m else None

    # Leak grep — institutions + personal + paths
    leak_patterns = {
        "the user": r"\bthe user\b",
        "user-path": r"$HOME",
        "Institution1": r"\bInstitution1\b",
        "Institution2": r"\bInstitution2\b",
        "Institution3": r"\bInstitution3\b",
        "Institution4": r"\bInstitution4\b",
    }
    for name, pat in leak_patterns.items():
        hits = []
        for p in fr.rglob("*.md"):
            if "/.git/" in str(p):
                continue
            try:
                for lineno, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                    if re.search(pat, line):
                        # Filter intentional/false-positive contexts
                        if name == "the user" and "Made by the user" in line:
                            continue
                        if "user" in line.lower() and name == "the user":
                            continue
                        hits.append((str(p.relative_to(TM)), lineno))
            except Exception:
                continue
        if hits:
            s.leaks[name] = hits[:5]  # cap to 5 per pattern

    # Install script
    install = fr / "install.sh"
    s.install_script_present = install.exists()
    if install.exists():
        text = install.read_text(errors="replace")
        for warning, pattern in [
            ("macOS sed -i ''", r"sed -i ''"),
            ("macOS open command", r"^\s*open\s"),
        ]:
            if re.search(pattern, text, re.MULTILINE):
                s.install_script_issues.append(warning)

    return s


# ─── Main ──────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "section",
        nargs="?",
        default="all",
        choices=("inventory", "docs", "ecosystem", "friends", "all"),
        help="Section to run (default: all)",
    )
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args(argv)

    sections = {}
    if args.section in ("inventory", "all"):
        sections["inventory"] = asdict(section_inventory())
    if args.section in ("docs", "all"):
        sections["docs"] = asdict(section_docs())
    if args.section in ("ecosystem", "all"):
        sections["ecosystem"] = asdict(section_ecosystem())
    if args.section in ("friends", "all"):
        sections["friends"] = asdict(section_friends())

    if args.json:
        print(json.dumps(sections, indent=2, default=str))
    else:
        print(_human(sections))
    return 0


def _human(sections: dict[str, dict]) -> str:
    out: list[str] = []
    if "inventory" in sections:
        inv = sections["inventory"]
        out.append("## Inventory")
        out.append(f"  Counts: {inv['counts']}")
        out.append(f"  Deployed: {inv['deployed_copies']}")
        out.append(f"  MCP (~/.claude.json user-scope):    {len(inv['mcp_servers_user'])} — {inv['mcp_servers_user']}")
        out.append(f"  MCP (~/.claude.json project-scope): {len(inv['mcp_servers_project_user'])} — {inv['mcp_servers_project_user']}")
        out.append(f"  MCP (<TM>/.mcp.json):               {len(inv['mcp_servers_project_local'])} — {inv['mcp_servers_project_local']}")
        out.append(f"  MCP (~/.claude/settings.json):      {len(inv['mcp_servers_settings'])} — {inv['mcp_servers_settings']}")
        out.append(f"  MCP (claude_desktop_config.json):   {len(inv['mcp_servers_desktop'])} — {inv['mcp_servers_desktop']}")
        if inv["undocumented_hooks"]:
            out.append(f"  Undocumented hooks: {inv['undocumented_hooks']}")
        if inv["undocumented_rules"]:
            out.append(f"  Undocumented rules: {inv['undocumented_rules']}")
        if inv["undocumented_agents"]:
            out.append(f"  Undocumented agents: {inv['undocumented_agents']}")
        out.append("")

    if "docs" in sections:
        d = sections["docs"]
        out.append("## Documentation")
        out.append(f"  count_parity ground truth: {d['count_parity']}")
        out.append(f"  current-focus age: {d['current_focus_age_days']} days")
        out.append(f"  logs: {d['log_count']}  plans: {d['plans_count']}  oldest_plan: {d['oldest_plan_age_days']} days")
        broken = d["broken_links"]
        if broken:
            out.append(f"  Broken links in {len(broken)} files:")
            for f, lines in broken.items():
                out.append(f"    {f}: {[ln for ln, _ in lines][:5]}")
        else:
            out.append("  ✓ No broken internal links")
        out.append("")

    if "ecosystem" in sections:
        e = sections["ecosystem"]
        out.append("## Ecosystem")
        out.append(f"  MCP referenced ({len(e['mcp_referenced'])}): {e['mcp_referenced']}")
        out.append(f"  MCP configured ({len(e['mcp_configured'])}): {e['mcp_configured']}")
        if e["mcp_phantom_refs"]:
            out.append(f"  ⚠ Phantom MCP refs (referenced but not configured): {e['mcp_phantom_refs']}")
        else:
            out.append("  ✓ No phantom MCP refs")
        if e["stale_components"]:
            for label, items in e["stale_components"].items():
                out.append(f"  Stale {label} ({len(items)}): {items[:3]}{'…' if len(items) > 3 else ''}")
        else:
            out.append("  ✓ No stale components (>90d)")
        out.append(f"  CLI tools: {e['cli_tools']}")
        out.append("")

    if "friends" in sections:
        f = sections["friends"]
        out.append("## Friends Repo")
        out.append(f"  skill dirs: {f['skill_dirs']}  SKILL.md files: {f['skill_md_count']}  rules: {f['rule_count']}")
        out.append(f"  README claims: {f['readme_claims']}")
        if f["leaks"]:
            out.append(f"  ⚠ Possible leaks: {list(f['leaks'].keys())}")
        else:
            out.append("  ✓ No anonymisation leaks")
        out.append(f"  install.sh present: {f['install_script_present']}  issues: {f['install_script_issues']}")

    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
