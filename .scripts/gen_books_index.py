#!/usr/bin/env python3
"""Generate the root index.html for books.user.com.

Walks the atlas, finds every topic with a `book_url:` field set, and renders
a minimal index page styled with the shared `user-theme.css`.

Run after each `paper-book --deploy` so the root index reflects what's live.
The skill's Phase 4.4 invokes this after the per-book rsync.

Usage:
    python3 gen_books_index.py [--out OUT_PATH] [--rsync]

    --out     write index.html to this path (default: ./index.html)
    --rsync   after writing, rsync to vps:/opt/user/data/books/index.html
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path.home() / "Research-Vault" / "atlas"


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse YAML-ish frontmatter — handles only flat string fields we need."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm = text[4:end]
    out: dict[str, str] = {}
    for line in fm.splitlines():
        m = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            out[key] = value
    return out


def collect_books() -> list[dict[str, str]]:
    books: list[dict[str, str]] = []
    for md in VAULT.rglob("*.md"):
        try:
            text = md.read_text()
        except Exception:
            continue
        fm = parse_frontmatter(text)
        url = fm.get("book_url")
        if not url:
            continue
        books.append(
            {
                "slug": md.stem,
                "title": fm.get("title") or md.stem,
                "url": url,
                "theme": fm.get("theme", "").strip("[]"),
                "status": fm.get("status", ""),
            }
        )
    books.sort(key=lambda b: b["title"].lower())
    return books


def render(books: list[dict[str, str]]) -> str:
    now = datetime.now(timezone.utc).strftime("%d %b %Y")
    cards = "\n".join(render_card(b) for b in books) or render_empty()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>books.user.com — paper companions</title>
<link rel="stylesheet" href="/shared/user-theme.css">
<style>
  body {{ margin: 0; }}
  .fn-app {{ min-height: 100vh; display: flex; flex-direction: column; }}
  .page-main {{ flex: 1; padding: var(--fn-space-8) var(--fn-space-4); }}
  .page-title {{
    font-size: var(--fn-text-2xl);
    font-weight: 700;
    color: var(--fn-color-text);
    margin: 0 0 var(--fn-space-2) 0;
    letter-spacing: -0.01em;
  }}
  .page-lede {{
    font-size: var(--fn-text-base);
    color: var(--fn-color-text-secondary);
    margin: 0 0 var(--fn-space-8) 0;
    max-width: 640px;
  }}
  .book-grid {{
    display: grid;
    gap: var(--fn-space-4);
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }}
  .book-card {{
    display: flex;
    flex-direction: column;
    gap: var(--fn-space-2);
    padding: var(--fn-space-6);
    text-decoration: none;
    color: inherit;
  }}
  .book-card-title {{
    font-size: var(--fn-text-lg);
    font-weight: 600;
    color: var(--fn-color-text);
    margin: 0;
    letter-spacing: -0.005em;
  }}
  .book-card-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: var(--fn-space-2);
    align-items: center;
    margin-top: var(--fn-space-2);
  }}
  .book-card-slug {{
    font-family: var(--fn-font-mono);
    font-size: var(--fn-text-xs);
    color: var(--fn-color-text-muted);
  }}
  .book-card-arrow {{
    margin-left: auto;
    font-size: var(--fn-text-sm);
    color: var(--fn-color-text-muted);
    transition: transform var(--fn-transition);
  }}
  .book-card:hover .book-card-arrow {{
    transform: translateX(2px);
    color: var(--fn-color-primary);
  }}
  .empty-state {{
    padding: var(--fn-space-8);
    text-align: center;
    color: var(--fn-color-text-secondary);
    font-size: var(--fn-text-sm);
  }}
</style>
</head>
<body>
<div class="fn-app">

  <header class="fn-header">
    <a class="fn-header-brand" href="/">
      <span style="font-weight:600;letter-spacing:-0.01em;">📖 books.user.com</span>
    </a>
    <nav class="fn-header-nav">
      <a class="fn-header-link" href="https://atlas.user.com/" target="_blank" rel="noopener">Atlas ↗</a>
      <a class="fn-header-link" href="https://vault.user.com/" target="_blank" rel="noopener">Vault ↗</a>
    </nav>
  </header>

  <main class="fn-container page-main">
    <h1 class="page-title">Paper companions</h1>
    <p class="page-lede">
      Educational MyST/Jupyter Book v2 walkthroughs of papers in the portfolio.
      Each book is a runnable, browsable explainer alongside the canonical paper PDF.
    </p>

    <div class="book-grid">
{cards}
    </div>
  </main>

  <footer class="fn-footer">
    <span>Generated {now} UTC · {len(books)} {"book" if len(books) == 1 else "books"} live</span>
    <a href="https://atlas.user.com/">atlas.user.com</a>
  </footer>

</div>
</body>
</html>
"""


def render_card(b: dict[str, str]) -> str:
    title = html.escape(b["title"])
    slug = html.escape(b["slug"])
    url = html.escape(b["url"])
    theme = html.escape(b["theme"]) if b["theme"] else ""
    status = html.escape(b["status"]) if b["status"] else ""

    badges = []
    if status:
        cls = badge_class(status)
        badges.append(f'<span class="fn-badge {cls}">{status}</span>')
    if theme:
        badges.append(f'<span class="fn-badge fn-badge-gray">{theme}</span>')
    badges_html = "\n        ".join(badges)

    return f"""      <a class="fn-card book-card" href="{url}">
        <h2 class="book-card-title">{title}</h2>
        <div class="book-card-meta">
        {badges_html}
          <span class="book-card-slug">/{slug}</span>
          <span class="book-card-arrow">↗</span>
        </div>
      </a>"""


def render_empty() -> str:
    return """      <div class="fn-card empty-state">
        No books deployed yet. Run <code>/paper-book &lt;project&gt; --deploy</code> to publish one.
      </div>"""


def badge_class(status: str) -> str:
    s = status.lower()
    if "accepted" in s or "published" in s:
        return "fn-badge-green"
    if "drafting" in s or "submitted" in s or "active" in s:
        return "fn-badge-blue"
    if "exploring" in s or "idea" in s:
        return "fn-badge-amber"
    if "abandoned" in s or "archived" in s:
        return "fn-badge-gray"
    return "fn-badge-gray"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="index.html", type=Path)
    p.add_argument("--rsync", action="store_true")
    args = p.parse_args()

    books = collect_books()
    args.out.write_text(render(books))
    print(f"Wrote {args.out} — {len(books)} book(s) listed")

    if args.rsync:
        cmd = ["rsync", "-avz", str(args.out), "vps:/opt/user/data/books/index.html"]
        print("$", " ".join(cmd))
        subprocess.run(cmd, check=True)
        print("Synced to books.user.com")


if __name__ == "__main__":
    main()
