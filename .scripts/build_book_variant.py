#!/usr/bin/env python3
"""Build one variant (public or private) of a paper-book.

Usage:
    build_book_variant.py <book-dir> <variant>

    book-dir: path to a paper-book directory (e.g. paper-acm-gecco/book/)
    variant:  "public" | "private"

The variant works as follows:

    - For "public": copies <book-dir>/* into <book-dir>/.build-src-public/,
      strips every block delimited by `<!-- private:start --> ... <!-- private:end -->`
      from each .md file, sets BASE_URL=/<slug> and runs `myst build --html`,
      producing output at <book-dir>/_build-public/html/.

    - For "private": copies <book-dir>/* into <book-dir>/.build-src-private/
      WITHOUT stripping anything, sets BASE_URL=/private/<slug>, runs the build,
      producing output at <book-dir>/_build-private/html/.

The two variants share the same source markdown; the difference is whether
private blocks are kept and what the base URL prefix is. A myst.yml override
adjusts site.options.base_url accordingly.

Slug is derived from the book directory's atlas topic; pass --slug to override.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PRIVATE_BLOCK = re.compile(r"<!-- private:start -->.*?<!-- private:end -->\n?", re.DOTALL)


def strip_private(text: str) -> str:
    """Remove private:start / private:end blocks (used for the public variant)."""
    return PRIVATE_BLOCK.sub("", text)


def find_slug(book_dir: Path) -> str:
    """Resolve the deploy slug: project directory name (e.g., quiver-ea)."""
    # book_dir is paper-<venue>/book/, parent of parent is project dir
    return book_dir.parent.parent.name


def patch_myst_yml(yml_path: Path, base_url: str) -> None:
    """Rewrite site.options.base_url and the package.json build script BASE_URL."""
    text = yml_path.read_text()
    text = re.sub(
        r"(\s+base_url:\s*)[^\n]+",
        rf"\1{base_url}",
        text,
        count=1,
    )
    yml_path.write_text(text)


def patch_package_json(pj_path: Path, base_url: str) -> None:
    """Update the BASE_URL env in the package.json build script."""
    text = pj_path.read_text()
    text = re.sub(
        r'"build":\s*"BASE_URL=[^\s"]+\s+myst',
        f'"build": "BASE_URL={base_url} myst',
        text,
        count=1,
    )
    pj_path.write_text(text)


def run_build(src_dir: Path, base_url: str) -> Path:
    """Run `npm install && npm run build` in src_dir; returns _build/html path."""
    subprocess.run(["npm", "install", "--silent"], cwd=src_dir, check=True)
    env = {"BASE_URL": base_url}
    import os
    full_env = {**os.environ, **env}
    subprocess.run(["npx", "myst", "build", "--html"], cwd=src_dir, check=True, env=full_env)
    return src_dir / "_build" / "html"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("book_dir", type=Path)
    ap.add_argument("variant", choices=["public", "private"])
    ap.add_argument("--slug", default=None, help="Deploy slug (default: project dir name)")
    args = ap.parse_args()

    book_dir = args.book_dir.resolve()
    if not book_dir.is_dir():
        sys.exit(f"book-dir not found: {book_dir}")

    slug = args.slug or find_slug(book_dir)
    base_url = f"/{slug}" if args.variant == "public" else f"/private/{slug}"
    src_dir = book_dir / f".build-src-{args.variant}"
    out_dir = book_dir / f"_build-{args.variant}"

    print(f"[paper-book] variant={args.variant}  slug={slug}  base_url={base_url}")
    print(f"[paper-book] src={src_dir}  out={out_dir}")

    # Clean + copy source
    if src_dir.exists():
        shutil.rmtree(src_dir)
    shutil.copytree(
        book_dir,
        src_dir,
        ignore=shutil.ignore_patterns(
            "_build*", "node_modules", ".build-src-*", "package-lock.json"
        ),
    )

    # Strip private blocks for public variant
    if args.variant == "public":
        n_stripped = 0
        for md in src_dir.glob("*.md"):
            orig = md.read_text()
            new = strip_private(orig)
            if new != orig:
                md.write_text(new)
                n_stripped += 1
        print(f"[paper-book] stripped private blocks from {n_stripped} file(s)")

    # Bibliography: copy the paper's .bib into the build src as references.bib
    # so mystmd can resolve {cite} directives in body chapters (myst.yml has
    # project.bibliography pointing to ./references.bib). Also generate a
    # Harvard-formatted references.md page via gen_references_page.py — this
    # OVERRIDES mystmd's auto-bibliography so we control the visual format
    # and inject RefPile/Paperpile links per variant.
    paper_dir = book_dir.parent / "paper"
    bibs = list(paper_dir.glob("*.bib")) if paper_dir.exists() else []
    if bibs and not (src_dir / "references.bib").exists():
        # If the source book had a symlink, shutil.copytree would have copied
        # the symlink itself; resolve and copy real bytes for build isolation.
        shutil.copy(bibs[0], src_dir / "references.bib")
    if bibs:
        gen_refs = Path(__file__).parent / "gen_references_page.py"
        pdf_links = list(book_dir.glob("*.pdf"))
        pdf_link = f"./{pdf_links[0].name}" if pdf_links else None
        cmd = [
            "python3", str(gen_refs),
            str(bibs[0]),
            str(src_dir / "references.md"),
            args.variant,
        ]
        if pdf_link:
            cmd.extend(["--paper-pdf", pdf_link])
        subprocess.run(cmd, check=True)
        # Append references.md to the toc in myst.yml if not already there
        yml_path = src_dir / "myst.yml"
        yml_text = yml_path.read_text()
        if "references.md" not in yml_text:
            yml_text = yml_text.replace(
                "    - file: appendix.md",
                "    - file: appendix.md\n    - file: references.md",
                1,
            )
            yml_path.write_text(yml_text)

    # Patch myst.yml + package.json with this variant's BASE_URL
    patch_myst_yml(src_dir / "myst.yml", base_url)
    patch_package_json(src_dir / "package.json", base_url)

    # Build
    html_dir = run_build(src_dir, base_url)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.move(str(html_dir.parent), str(out_dir))

    # Copy PDF if it exists in source
    for pdf in book_dir.glob("*.pdf"):
        shutil.copy(pdf, out_dir / "html" / pdf.name)

    # Force light mode: inject a small script into every HTML file that strips
    # mystmd's `dark` class on <html>, sets data-theme="light", clears any
    # cached preference, and reapplies via MutationObserver in case React
    # hydration tries to flip back. Runs synchronously before paint.
    # Marker `<!--force-light-v1-->` is unique to this injection (mystmd's own
    # output uses `myst:theme` for its localStorage key, so don't use that).
    INJECT_MARKER = "<!--force-light-v1-->"
    force_light = (
        f'{INJECT_MARKER}<script>(function(){{var r=document.documentElement;'
        'r.classList.remove("dark");r.setAttribute("data-theme","light");'
        'try{localStorage.setItem("myst:theme","light");}catch(e){}'
        'new MutationObserver(function(){'
        'if(r.classList.contains("dark"))r.classList.remove("dark");'
        'if(r.getAttribute("data-theme")!=="light")r.setAttribute("data-theme","light");'
        '}).observe(r,{attributes:true,attributeFilter:["class","data-theme"]});'
        '})();</script>'
    )
    n_patched = 0
    for html_file in (out_dir / "html").rglob("*.html"):
        text = html_file.read_text()
        if "</head>" in text and INJECT_MARKER not in text:
            html_file.write_text(text.replace("</head>", f"{force_light}</head>", 1))
            n_patched += 1
    print(f"[paper-book] injected force-light script into {n_patched} HTML file(s)")

    print(f"[paper-book] OK — output at {out_dir}/html/")


if __name__ == "__main__":
    main()
