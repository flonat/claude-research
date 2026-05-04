#!/usr/bin/env python3
"""Convert mystmd-flavoured Markdown to Quarto Markdown.

Used by the Quarto migration of the paper-book skill. Reads .md files from
a source dir and writes .qmd equivalents to a target dir, applying:

    {cite:t}`Key`              →  @Key
    {cite:p}`Key`              →  [@Key]
    ```{note} ... ```          →  ::: {.callout-note} ... :::
    ```{tip}/{important}/{warning}/{caution}/{seealso} ... ```
                               →  ::: {.callout-tip|important|warning|caution|note} ... :::
    ```{figure} path ...```    →  ![caption](path){#fig-id width=...}
    ```{code-cell} lang        →  ```{lang}     (no execution; we present, don't run)
    <!-- private:start -->     →  ::: {.content-visible when-profile="private"}
    <!-- private:end -->       →  :::

Frontmatter `short_title` is preserved (Quarto doesn't use it but ignores
unknown keys). Anything else is passed through unchanged.

Usage:
    myst_to_quarto.py <src-dir> <dst-dir> [--manifest manifest.txt]

If --manifest is given, only the listed files (one per line, basenames) are
converted. Otherwise every *.md in src-dir is converted (skipping PLAN.md
and any file starting with _ or .).
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# ── Citations ────────────────────────────────────────────────────────────
RE_CITE_T = re.compile(r"\{cite:t\}`([^`]+)`")
RE_CITE_P = re.compile(r"\{cite:p\}`([^`]+)`")
RE_CITE_BARE = re.compile(r"\{cite\}`([^`]+)`")  # treat as parenthetical

# ── Directive callouts ──────────────────────────────────────────────────
# Maps mystmd directive name → Quarto callout class
CALLOUT_MAP = {
    "note":      "callout-note",
    "tip":       "callout-tip",
    "important": "callout-important",
    "warning":   "callout-warning",
    "caution":   "callout-caution",
    "seealso":   "callout-tip",  # no native Quarto equivalent; tip is closest
}

# Match a fenced directive opening line:  ```{name}
RE_DIRECTIVE_OPEN = re.compile(r"^(\s*)```\{([a-z-]+)\}\s*(.*)$")

# Match private blocks
RE_PRIVATE_START = re.compile(r"<!--\s*private:start\s*-->")
RE_PRIVATE_END = re.compile(r"<!--\s*private:end\s*-->")


def convert_citations(text: str) -> str:
    text = RE_CITE_T.sub(r"@\1", text)
    text = RE_CITE_P.sub(r"[@\1]", text)
    text = RE_CITE_BARE.sub(r"[@\1]", text)
    return text


def convert_directives(text: str) -> str:
    """Walk the text line-by-line, converting fenced directives.

    Handles nested code blocks by tracking fence depth — a ```{python}
    inside a ```{note} ... ``` block needs to NOT close the outer note
    block. We use a stack of (kind, fence) where kind is "directive" or
    "code".
    """
    lines = text.split("\n")
    out: list[str] = []
    stack: list[tuple[str, str]] = []  # (kind, expected-closing-fence)

    for line in lines:
        # Already-converted directive close: a closing ``` from a directive
        # converts to ::: ; closing ``` from a code block stays as ```.
        stripped = line.rstrip()

        # Detect opening of a directive: ```{name}
        m = RE_DIRECTIVE_OPEN.match(line)
        if m and not (stack and stack[-1][0] == "code"):
            indent, name, args = m.group(1), m.group(2), m.group(3).strip()

            # {figure} path → image markdown (single-line conversion)
            if name == "figure":
                # We'll buffer figure content separately; for now emit a
                # placeholder marker and process figure body specially.
                # Simpler approach: keep ```{figure} as a verbatim mystmd
                # block and let Quarto's pandoc treat it as a code block.
                # Better approach: parse out path, caption, attrs.
                stack.append(("figure", "```"))
                out.append(f"{indent}<!-- figure-block-start: {args} -->")
                continue

            # {code-cell} lang → ```lang
            if name == "code-cell":
                lang = args or "text"
                stack.append(("code", "```"))
                out.append(f"{indent}```{lang}")
                continue

            # {<callout>} → ::: {.callout-X}
            if name in CALLOUT_MAP:
                cls = CALLOUT_MAP[name]
                stack.append(("directive", "```"))
                out.append(f"{indent}::: {{.{cls}}}")
                # If there's a `:title: ...` line right after, we'll catch it
                # below; for now emit the open marker. Quarto callouts use
                # the first heading inside the block as the title.
                continue

            # Unknown directive — leave verbatim, treat as code block
            stack.append(("code", "```"))
            out.append(line)
            continue

        # Detect closing fence ```
        if stripped == "```" or stripped == "```":
            if stack:
                kind, _ = stack.pop()
                if kind == "directive":
                    out.append(":::")
                    continue
                if kind == "figure":
                    # Close the figure-block; the caller will post-process.
                    out.append("<!-- figure-block-end -->")
                    continue
                # code: keep as-is
                out.append(line)
                continue
            out.append(line)
            continue

        # Track entering a code block from plain ```lang
        if stripped.startswith("```") and not stack:
            # Opening of a plain code fence (not a directive)
            stack.append(("code", "```"))
            out.append(line)
            continue

        out.append(line)

    return "\n".join(out)


def convert_figures(text: str) -> str:
    """Post-process figure blocks: <!-- figure-block-start: PATH --> CONTENT
    <!-- figure-block-end --> → ![caption](path){attrs}.

    Mystmd figure block:
        ```{figure} path
        :name: fig-id
        :width: 80%
        :align: center

        Caption text here.
        ```

    Quarto figure (markdown image):
        ![Caption text here.](path){#fig-id width=80% fig-align=center}
    """
    pattern = re.compile(
        r"<!-- figure-block-start: (?P<path>[^\n]+) -->\n"
        r"(?P<body>.*?)\n"
        r"<!-- figure-block-end -->",
        re.DOTALL,
    )

    def replace(m: re.Match) -> str:
        path = m.group("path").strip()
        body = m.group("body")
        attrs: dict[str, str] = {}
        caption_lines: list[str] = []
        for line in body.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(":") and ":" in stripped[1:]:
                # :name: value  or  :width: 80%
                key, _, val = stripped[1:].partition(":")
                attrs[key.strip()] = val.strip()
                continue
            caption_lines.append(line)
        caption = " ".join(l.strip() for l in caption_lines).strip()

        attr_parts: list[str] = []
        if "name" in attrs:
            attr_parts.append(f"#{attrs['name']}")
        if "width" in attrs:
            attr_parts.append(f"width={attrs['width']}")
        if "align" in attrs:
            attr_parts.append(f"fig-align={attrs['align']}")
        attr_str = (" {" + " ".join(attr_parts) + "}") if attr_parts else ""

        return f"![{caption}]({path}){attr_str}"

    return pattern.sub(replace, text)


def convert_private_markers(text: str) -> str:
    """Replace HTML-comment markers with Quarto profile div blocks."""
    text = RE_PRIVATE_START.sub(
        '::: {.content-visible when-profile="private"}',
        text,
    )
    text = RE_PRIVATE_END.sub(":::", text)
    return text


def convert(text: str) -> str:
    text = convert_directives(text)
    text = convert_figures(text)
    text = convert_citations(text)
    text = convert_private_markers(text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir", type=Path)
    ap.add_argument("dst_dir", type=Path)
    ap.add_argument("--manifest", type=Path, default=None,
                    help="File listing basenames (one per line) to convert; "
                         "defaults to all *.md files except PLAN.md / dot/under-files")
    args = ap.parse_args()

    if not args.src_dir.is_dir():
        sys.exit(f"src-dir not found: {args.src_dir}")
    args.dst_dir.mkdir(parents=True, exist_ok=True)

    if args.manifest:
        names = [n.strip() for n in args.manifest.read_text().splitlines() if n.strip()]
        files = [args.src_dir / n for n in names]
    else:
        files = [
            f for f in args.src_dir.glob("*.md")
            if f.name != "PLAN.md" and not f.name.startswith((".", "_"))
        ]

    n = 0
    for f in files:
        if not f.exists():
            print(f"  skip (missing): {f.name}", file=sys.stderr)
            continue
        text = f.read_text()
        out_text = convert(text)
        out_path = args.dst_dir / (f.stem + ".qmd")
        out_path.write_text(out_text)
        n += 1
    print(f"[myst-to-quarto] converted {n} file(s) → {args.dst_dir}")


if __name__ == "__main__":
    main()
