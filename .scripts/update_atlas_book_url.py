#!/usr/bin/env python3
"""Idempotently set `book_url:` in an atlas topic file's YAML frontmatter.

Used by /paper-book Phase 4.4 after a successful deploy to wire the
`books.user.com/<slug>/` link into the atlas topic so that
`atlas.user.com` topic pages can render it.

Usage:
    python3 update_atlas_book_url.py --slug quiver-ea --url https://books.user.com/quiver-ea/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

VAULT = Path.home() / "Research-Vault" / "atlas"


def find_topic(slug: str) -> Path:
    matches = list(VAULT.rglob(f"{slug}.md"))
    if not matches:
        sys.exit(f"No atlas topic found for slug: {slug}")
    if len(matches) > 1:
        sys.exit(f"Ambiguous slug — multiple atlas topics: {matches}")
    return matches[0]


def upsert_book_url(path: Path, url: str) -> bool:
    text = path.read_text()
    if not text.startswith("---\n"):
        sys.exit(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        sys.exit(f"{path}: malformed frontmatter (no closing ---)")

    fm = text[4:end]
    body = text[end + 5 :]

    lines = fm.splitlines()
    new_line = f"book_url: {url}"
    out: list[str] = []
    found = False
    for line in lines:
        if line.startswith("book_url:"):
            if line == new_line:
                return False  # already correct, no write
            out.append(new_line)
            found = True
        else:
            out.append(line)
    if not found:
        out.append(new_line)

    new_fm = "\n".join(out)
    path.write_text(f"---\n{new_fm}\n---\n{body}")
    return True


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--url", required=True)
    args = p.parse_args()

    topic = find_topic(args.slug)
    changed = upsert_book_url(topic, args.url)
    print(f"{'updated' if changed else 'unchanged'}: {topic}")


if __name__ == "__main__":
    main()
