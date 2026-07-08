#!/usr/bin/env python3
"""Regenerate the intro.md of one or all paper-book companions.

Source of truth: each book's atlas topic frontmatter + `## Description`.
The intro masthead (`Authors`, `Venue`, `Topic`, optional `Source`) and the
prose body under `## About this paper` are derived from atlas. Anything
below the `<!-- preserve-below: ... -->` marker is captured verbatim and
re-appended after regeneration.

Used by `/init-paper-book` (initial scaffold) and `/audit-paper-book`
(format-convention drift auto-fix).

Usage
-----
    regenerate_intro.py [SLUG] [--apply]

    SLUG          — book slug (must match its directory name under
                    ~/vault/books/). Omit or pass 'all' to
                    process every registered book.
    --apply       — write changes to disk. Without this flag, prints the
                    regenerated intro to stdout (dry-run).

Conventions
-----------
* Atlas topic filename MUST equal the book slug (`/init-paper-book` Hard
  Rule 4). If the registry's `atlas_topic:` leaf differs, the script
  aborts with a clear message.
* The intro chapter's page-title H1 is "Intro" (rendered from
  `chapter.title` in frontmatter by atlas's template).
* The Source field (Overleaf) is dropped when atlas's status begins with
  one of {Accepted, In Press, Camera-ready, Published, Withdrawn}.
* When status begins with `Published` AND atlas `outputs[0]` carries a
  `doi:` field, the Venue line is templated as
  `*<venue>* (<pub-year>) — Published online <publication_date>` and a
  Source line `: [📄 DOI: <doi> ↗](https://doi.org/<doi>)` is emitted
  in place of the dropped Overleaf line. Falls back to the plain
  `<venue> — Published` form if `publication_date` / `doi` are absent.
* Author-line format is per-book (per-author affiliations may differ).
  Override via AUTHORS dict below; falls back to a single-institution
  default derived from atlas `institution:` and `co_authors:`.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

VAULT = Path.home() / "vault"
BOOKS_ROOT = VAULT / "books"
ATLAS_ROOT = VAULT / "atlas"
REGISTRY = BOOKS_ROOT / "index.yaml"

PRESERVE_MARKER = "<!-- preserve-below: hand-written content survives regeneration -->"

# ── Per-book author line overrides ────────────────────────────────────────
# Atlas tracks `institution:` for the lead author and `co_authors:` as
# wikilinks, but not per-author affiliation. For multi-institution papers
# the line must be hand-curated here. For single-institution papers, the
# default derivation (lead + co_authors, all attributed to `institution:`)
# is usually correct.
#
# Add a new entry whenever a new book is scaffolded, especially if any
# co-author sits at a different institution from the lead.
AUTHORS: dict[str, str] = {
    # Map a project slug to a hand-curated author line (example only).
    "example-project": "First Author, Second Author (Institution)",
}

# Explicit Source-field suppression (e.g. when a paper has a self-hosted
# PDF instead of an Overleaf link and we don't want a Source row).
DROP_SOURCE: set[str] = set()

# Status prefixes that count as terminal (drop the Source/Overleaf row).
TERMINAL_STATUS_PREFIXES = ("Accepted", "In Press", "Camera-ready", "Published", "Withdrawn")


# ── Helpers ──────────────────────────────────────────────────────────────

def _read_registry() -> dict[str, dict]:
    if not REGISTRY.exists():
        return {}
    data = yaml.safe_load(REGISTRY.read_text()) or {}
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def _resolve_atlas_path(slug: str, entry: dict) -> Path:
    """Hard Rule 4: book slug must equal atlas topic leaf."""
    topic_ref = (entry.get("atlas_topic") or "").strip()
    if "/" not in topic_ref:
        raise SystemExit(f"{slug}: registry atlas_topic '{topic_ref}' is malformed (expected 'theme/slug').")
    leaf = topic_ref.rsplit("/", 1)[1]
    if leaf != slug:
        raise SystemExit(
            f"{slug}: SLUG DRIFT — registry points at atlas topic '{leaf}'. "
            "Book slug MUST equal atlas topic filename (Hard Rule 4). Rename one side."
        )
    path = ATLAS_ROOT / f"{topic_ref}.md"
    if not path.exists():
        raise SystemExit(f"{slug}: atlas topic file not found at {path}.")
    return path


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def _clean_wikilinks(text: str) -> str:
    return re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)


def _extract_description(atlas_body: str) -> str:
    """Body of the atlas `## Description` section, excluding the header."""
    m = re.search(r"^## Description\s*\n+(.+?)(?=\n## |\Z)", atlas_body,
                  re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def _first_sentence(paragraph: str) -> str:
    t = paragraph.strip()
    m = re.search(r"\.(\s+[A-Z]|$)", t)
    s = t[: m.start() + 1] if m else t
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _parse_pub_date(raw: str) -> tuple[str, str]:
    """Return (year, pretty-formatted date) from an ISO-date string.
    Pretty form is 'D Month YYYY' (e.g. '15 June 2026'). Returns ('','')
    if raw is not a parseable ISO date; falls back to (year-prefix, raw)
    if only a year prefix is present."""
    if not raw:
        return "", ""
    try:
        d = datetime.strptime(raw[:10], "%Y-%m-%d")
        return f"{d.year}", d.strftime("%-d %B %Y")
    except ValueError:
        m = re.match(r"^(\d{4})", raw)
        return (m.group(1) if m else "", raw)


def _default_authors(meta: dict) -> str:
    """Fallback author line when no override is in the AUTHORS dict.
    Uses the atlas `institution:` field for the lead and all co_authors —
    correct for single-institution papers, possibly wrong for multi."""
    institution = _clean_wikilinks(str(meta.get("institution") or "")).strip()
    co_authors = [_clean_wikilinks(str(a)) for a in (meta.get("co_authors") or [])]
    names = ["the user"] + co_authors
    line = ", ".join(names)
    return f"{line} ({institution})" if institution else line


# ── Core build ───────────────────────────────────────────────────────────

def build_intro(slug: str, entry: dict) -> str:
    atlas_path = _resolve_atlas_path(slug, entry)
    meta, body = _parse_frontmatter(atlas_path.read_text())

    outputs = meta.get("outputs") or []
    out0 = outputs[0] if outputs else {}
    venue = _clean_wikilinks(str(out0.get("venue") or ""))
    status = out0.get("status") or meta.get("status") or "Drafting"
    paper_title = out0.get("paper_title") or meta.get("paper_title") or meta.get("title", "")
    overleaf = out0.get("overleaf_link") or meta.get("overleaf_link") or ""
    doi = (out0.get("doi") or meta.get("doi") or "").strip()
    publication_date = str(out0.get("publication_date") or "").strip()
    topic_title = meta.get("title", slug)

    desc_full = _extract_description(body)
    paras = re.split(r"\n\s*\n", desc_full, maxsplit=1)
    lede_para = paras[0] if paras else ""
    rest = _clean_wikilinks(paras[1]) if len(paras) > 1 else ""
    lede = lede_para if 0 < len(lede_para) <= 320 else _first_sentence(lede_para)
    lede = _clean_wikilinks(lede) or f"A reading guide to {paper_title}."

    authors_line = AUTHORS.get(slug) or _default_authors(meta)

    # Venue + Source emission. Status=Published with DOI promotes both:
    # the Venue line carries a "Published online <date>" suffix, and the
    # Source line points at the DOI rather than the (now-dropped) Overleaf
    # working copy. Falls back gracefully if metadata is partial.
    is_published = str(status).startswith("Published")
    if is_published and venue:
        pub_year, pub_date_pretty = _parse_pub_date(publication_date)
        if pub_date_pretty:
            venue_line = (
                f"*{venue}* ({pub_year}) — Published online {pub_date_pretty}"
                if pub_year
                else f"*{venue}* — Published online {pub_date_pretty}"
            )
        else:
            venue_line = f"*{venue}* — Published"
    else:
        venue_line = f"{venue} — {status}" if venue else str(status)

    lines = [
        "Authors", f": {authors_line}", "",
        "Venue", f": {venue_line}", "",
        "Topic", f": [{topic_title} ↗](https://atlas.example.com/topic/{slug})",
    ]

    is_terminal = any(str(status).startswith(p) for p in TERMINAL_STATUS_PREFIXES)
    if is_published and doi and slug not in DROP_SOURCE:
        # Published + DOI → Source points at the version of record.
        lines += ["", "Source", f": [📄 DOI: {doi} ↗](https://doi.org/{doi})"]
    elif not is_terminal and slug not in DROP_SOURCE and overleaf:
        # In-flight → Source points at the Overleaf working copy.
        lines += ["", "Source", f": [📝 Overleaf ↗]({overleaf})"]

    out = [
        "---",
        "title: Intro",
        "short_title: Intro",
        "---",
        "",
        lede,
        "",
    ] + lines + [""]
    if rest:
        out += ["", "## About this paper", "", rest, ""]
    return "\n".join(out).rstrip() + "\n"


def merge_preserved(out_path: Path, new_text: str) -> str:
    """If the existing intro carries a preserve marker, re-append everything
    beneath it after the regenerated content."""
    if not out_path.exists():
        return new_text
    existing = out_path.read_text()
    if PRESERVE_MARKER not in existing:
        return new_text
    preserved = existing.split(PRESERVE_MARKER, 1)[1].lstrip("\n").rstrip()
    return new_text.rstrip() + "\n\n" + PRESERVE_MARKER + "\n\n" + preserved + "\n"


# ── CLI ──────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("slug", nargs="?", default="all",
                        help="Book slug; 'all' (default) processes every registered book.")
    parser.add_argument("--apply", action="store_true",
                        help="Write changes to disk; otherwise dry-run to stdout.")
    args = parser.parse_args(argv)

    registry = _read_registry()
    if not registry:
        print("No book registry found at", REGISTRY, file=sys.stderr)
        return 1

    slugs = list(registry) if args.slug == "all" else [args.slug]
    for slug in slugs:
        if slug not in registry:
            print(f"  {slug}: not in registry — skipping", file=sys.stderr)
            continue
        out_path = BOOKS_ROOT / slug / "intro.md"
        try:
            new_text = merge_preserved(out_path, build_intro(slug, registry[slug]))
        except SystemExit as e:
            print(str(e), file=sys.stderr)
            continue
        if args.apply:
            out_path.write_text(new_text)
            print(f"  wrote {slug}/intro.md")
        else:
            print(f"=== {slug} ===\n{new_text}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
