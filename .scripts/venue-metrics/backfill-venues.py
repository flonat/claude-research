#!/usr/bin/env -S uv run --with pyyaml python3
"""Backfill `scimago:` and `impact_factor:` on vault venue files from SJR CSV.

SJR CSV schema (semicolon-delimited, European decimal):
  Issn (space-separated, no hyphens) | SJR Best Quartile | Citations / Doc. (2years)

Matching order: ISSN (exact, normalised) → normalised title.
Idempotent: skip if both fields already non-empty, unless --force.
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
from pathlib import Path
import yaml

ROOT = Path.home() / "Research-Vault"
VENUES = ROOT / "venues"
SJR_CSV = Path.home() / "Task-Management/.context/resources/venue-rankings/scimagojr-2025.csv"


def norm_issn(s: str) -> str:
    return re.sub(r"[^0-9Xx]", "", s or "").upper()


def norm_title(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def parse_eu_float(s: str) -> float | None:
    if not s or s.strip() == "":
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def load_sjr(csv_path: Path) -> tuple[dict, dict]:
    """Return (by_issn, by_title) → {'quartile': 'Q1', 'cites2y': 5.2, 'title': ..., 'sjr': float}."""
    by_issn: dict[str, dict] = {}
    by_title: dict[str, dict] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            title = row.get("Title", "").strip().strip('"')
            quartile = row.get("SJR Best Quartile", "").strip()
            cites2y = parse_eu_float(row.get("Citations / Doc. (2years)", ""))
            sjr_score = parse_eu_float(row.get("SJR", ""))
            if not quartile or quartile == "-":
                continue
            rec = {"quartile": quartile, "cites2y": cites2y, "sjr": sjr_score, "title": title}
            issn_field = row.get("Issn", "").strip().strip('"')
            for issn in re.split(r"[\s,]+", issn_field):
                n = norm_issn(issn)
                if len(n) == 8:  # ISSN is 8 chars
                    by_issn.setdefault(n, rec)
            if title:
                by_title.setdefault(norm_title(title), rec)
    return by_issn, by_title


def parse_frontmatter(text: str) -> tuple[dict | None, str, str]:
    """Return (frontmatter_dict, raw_yaml, body). None if no frontmatter."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, "", text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None, m.group(1), m.group(2)
    return fm, m.group(1), m.group(2)


def dump_frontmatter(fm: dict) -> str:
    # Preserve insertion order; yaml.safe_dump sorts by default — disable that.
    return yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)


def lookup(fm: dict, by_issn: dict, by_title: dict) -> dict | None:
    # 1) ISSN
    issn = fm.get("issn")
    if issn:
        rec = by_issn.get(norm_issn(str(issn)))
        if rec:
            return rec
    # 2) Title (and aliases)
    candidates = []
    for k in ("full_name", "title"):
        if fm.get(k):
            candidates.append(str(fm[k]))
    for a in fm.get("aliases") or []:
        if a:
            candidates.append(str(a))
    for c in candidates:
        rec = by_title.get(norm_title(c))
        if rec:
            return rec
    return None


def format_if(cites2y: float | None) -> str:
    if cites2y is None:
        return ""
    return f"~{cites2y:.1f}" if cites2y < 10 else f"~{cites2y:.0f}"


def update_venue(path: Path, by_issn: dict, by_title: dict, force: bool) -> tuple[str, str]:
    """Return (status, note). Status ∈ {updated, skipped-nonjournal, skipped-filled, nomatch}."""
    text = path.read_text(encoding="utf-8")
    fm, _, body = parse_frontmatter(text)
    if fm is None:
        return "nomatch", "no frontmatter"
    if fm.get("venue_type") != "Journal":
        return "skipped-nonjournal", ""

    has_scimago = fm.get("scimago") not in (None, "", "null")
    has_if = fm.get("impact_factor") not in (None, "", "null")
    if has_scimago and has_if and not force:
        return "skipped-filled", f"{fm.get('scimago')} / {fm.get('impact_factor')}"

    # Drop acceptance_rate if present (schema change)
    dropped_ar = fm.pop("acceptance_rate", None) is not None

    rec = lookup(fm, by_issn, by_title)
    if not rec:
        if dropped_ar:
            # Write back just to remove acceptance_rate
            new_fm = dump_frontmatter(fm)
            path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")
            return "nomatch", "no SJR match; dropped acceptance_rate"
        return "nomatch", "no SJR match"

    if force or not has_scimago:
        fm["scimago"] = rec["quartile"]
    if force or not has_if:
        fm["impact_factor"] = format_if(rec["cites2y"])

    new_fm = dump_frontmatter(fm)
    path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")
    return "updated", f"{rec['quartile']} / {format_if(rec['cites2y'])} ← {rec['title']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing values")
    ap.add_argument("--only", help="glob of slugs to process (e.g., 'management-science')")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not SJR_CSV.exists():
        print(f"error: SJR CSV not found at {SJR_CSV}", file=sys.stderr)
        return 2
    by_issn, by_title = load_sjr(SJR_CSV)
    print(f"SJR: {len(by_issn)} ISSNs, {len(by_title)} titles indexed")

    files = sorted(VENUES.glob("*.md"))
    if args.only:
        files = [f for f in files if args.only in f.name]

    counts = {"updated": 0, "skipped-nonjournal": 0, "skipped-filled": 0, "nomatch": 0}
    nomatch_names = []
    for f in files:
        if args.dry_run:
            text = f.read_text(encoding="utf-8")
            fm, _, _ = parse_frontmatter(text)
            if fm and fm.get("venue_type") == "Journal":
                rec = lookup(fm, by_issn, by_title)
                status = "would-update" if rec else "nomatch"
                note = f"{rec['quartile']} ← {rec['title']}" if rec else "no SJR match"
                print(f"  [{status}] {f.stem}: {note}")
                if not rec:
                    nomatch_names.append(f.stem)
            continue
        status, note = update_venue(f, by_issn, by_title, args.force)
        counts[status] = counts.get(status, 0) + 1
        if status == "updated":
            print(f"  [updated] {f.stem}: {note}")
        elif status == "nomatch":
            nomatch_names.append(f.stem)

    print("\nSummary:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    if nomatch_names:
        print(f"\nNo match ({len(nomatch_names)}):")
        for n in nomatch_names:
            print(f"  - {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
