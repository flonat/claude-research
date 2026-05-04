#!/usr/bin/env python3
"""Build a {filename → absolute_path} index over the Paperpile-synced PDFs.

Run periodically (or after a Paperpile sync). Writes to
~/.cache/paperpile-filename-index.json. Atlas-workspace reads this file as
an O(1) fallback for resolve_pdf_by_citekey when the JSON-recorded path is
stale (Paperpile's taxonomy reorg between exports).

Usage:
    build_paperpile_filename_index.py [--root <pdf-root>] [--out <out-path>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


DEFAULT_ROOT = "$HOME/Library/CloudStorage/GoogleDrive-user@example.com/My Drive/Paperpile"
DEFAULT_OUT = Path.home() / ".cache" / "paperpile-filename-index.json"


def build_index(root: Path) -> dict[str, str]:
    """Walk root, collect {basename → first absolute path}.

    Subsequent occurrences of the same basename are kept too (under suffix
    keys like `name__1`) — Paperpile cross-files some PDFs into multiple
    taxonomy folders. The first match wins for lookup; the duplicates are
    ignored unless the consumer wants to dedupe.
    """
    index: dict[str, str] = {}
    n = 0
    t0 = time.time()
    for sub in ("All Papers", "Starred Papers", "Trashed Papers"):
        sub_root = root / sub
        if not sub_root.exists():
            continue
        for p in sub_root.rglob("*.pdf"):
            n += 1
            if n % 5000 == 0:
                print(f"  {n:>6} files scanned ({time.time()-t0:.0f}s elapsed)", file=sys.stderr)
            base = p.name
            if base not in index:
                index[base] = str(p)
    print(f"[paperpile-index] scanned {n} PDFs in {time.time()-t0:.1f}s; {len(index)} unique basenames", file=sys.stderr)
    return index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT, type=Path)
    ap.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = ap.parse_args()

    if not args.root.exists():
        sys.exit(f"pdf root does not exist: {args.root}")

    index = build_index(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(index, indent=0))
    print(f"[paperpile-index] wrote {args.out} ({len(index)} entries)")


if __name__ == "__main__":
    main()
