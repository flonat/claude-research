#!/usr/bin/env bash
# build-book-pdf.sh — compile a vault book to a PDF companion.
#
# Pipeline:
#   1. `myst build --tex` writes raw LaTeX to <book>/_build/tex/
#   2. Patch fontenc/inputenc/lmodern → fontspec (xelatex unicode glyphs)
#   3. Patch \section → \chapter (and bump subsection/subsubsection down) so the
#      book class produces proper chapter numbering
#   4. Insert a publication block after \maketitle
#   5. `latexmk -xelatex` → copy to <book>/exports/<slug>.pdf
#
# Usage: build-book-pdf.sh <slug>
#   <slug> must match a directory under ~/vault/books/ containing a
#   myst.yml with a `format: tex` export.
#
# Exit codes: 0 success, 1 usage/precondition, 2 build error.

set -euo pipefail

SLUG="${1:-}"
if [[ -z "$SLUG" ]]; then
  echo "usage: build-book-pdf.sh <slug>" >&2
  exit 1
fi

BOOK_DIR="$HOME/vault/books/$SLUG"
if [[ ! -d "$BOOK_DIR" ]]; then
  echo "error: book directory not found: $BOOK_DIR" >&2
  exit 1
fi
if [[ ! -f "$BOOK_DIR/myst.yml" ]]; then
  echo "[0/5] myst.yml not found — bootstrapping from books/index.yaml"
  python3 - "$SLUG" "$BOOK_DIR" <<'PY'
import re, sys, pathlib
slug, book_dir = sys.argv[1], pathlib.Path(sys.argv[2])
idx = (pathlib.Path.home() / "vault" / "books" / "index.yaml").read_text()
# Find the slug's block; collect title + chapters
title, bib, chapters = None, "references.bib", []
in_block, in_chapters = False, False
for line in idx.splitlines():
    if line.startswith(f"{slug}:"):
        in_block = True; continue
    if in_block:
        if line and not line.startswith((" ", "\t", "#")):
            break
        m = re.match(r'\s*title:\s*"?([^"]+)"?\s*$', line)
        if m: title = m.group(1).strip()
        m = re.match(r'\s*bibliography:\s*(\S+)\s*$', line)
        if m: bib = m.group(1).strip()
        if re.match(r'\s*chapters:\s*$', line):
            in_chapters = True; continue
        if in_chapters:
            m = re.match(r'\s*-\s*(\S+)\s*$', line)
            if m: chapters.append(m.group(1).strip())
            elif line.strip() and not line.startswith(" " * 4):
                in_chapters = False
if not title or not chapters:
    sys.exit("error: could not find title or chapters in books/index.yaml")
articles = "\n".join(f"        - file: {c}.md" for c in chapters)
(book_dir / "myst.yml").write_text(
    "# Bootstrapped by build-book-pdf.sh; safe to extend.\n"
    "version: 1\n"
    "project:\n"
    f'  title: "{title}"\n'
    "  bibliography:\n"
    f"    - {bib}\n"
    "  exports:\n"
    "    - format: tex\n"
    "      template: plain_latex_book\n"
    "      output: _build/tex/\n"
    "      articles:\n"
    f"{articles}\n"
)
print(f"  wrote {book_dir}/myst.yml")
PY
fi

command -v myst    >/dev/null || { echo "error: mystmd not installed (npm install -g mystmd)" >&2; exit 1; }
command -v latexmk >/dev/null || { echo "error: latexmk not on PATH" >&2; exit 1; }
command -v xelatex >/dev/null || { echo "error: xelatex not on PATH" >&2; exit 1; }

cd "$BOOK_DIR"

echo "[1/5] cleaning prior build artefacts"
rm -rf _build exports

echo "[2/5] myst build --tex"
myst build --tex 2>&1 | tail -5

TEX_DIR="_build/tex"
MAIN_TEX="$TEX_DIR/intro.tex"
if [[ ! -f "$MAIN_TEX" ]]; then
  # mystmd names the main file after the first article; fall back to a glob
  MAIN_TEX=$(find "$TEX_DIR" -maxdepth 1 -name "*.tex" -not -name "*-*" | head -1)
fi
if [[ -z "${MAIN_TEX:-}" || ! -f "$MAIN_TEX" ]]; then
  echo "error: could not locate main tex file under $TEX_DIR" >&2
  exit 2
fi

PREFIX=$(basename "$MAIN_TEX" .tex)  # e.g. "intro"

echo "[3/5] patching main tex ($MAIN_TEX)"
# Swap 8-bit font setup for fontspec (xelatex needs this for unicode glyphs
# like ↗ ∈ ─ ├ that mystmd emits in callouts, code blocks, tree diagrams).
# Also compose a custom title page from atlas metadata + myst.yml overrides.
python3 - "$MAIN_TEX" "$BOOK_DIR" "$SLUG" <<'PY'
import re, sys, pathlib

main_tex   = pathlib.Path(sys.argv[1])
book_dir   = pathlib.Path(sys.argv[2])
slug       = sys.argv[3]
vault_root = pathlib.Path.home() / "vault"

# ---- read atlas topic for canonical publication metadata --------------------
def read_book_index_atlas_topic(slug):
    idx = (vault_root / "books" / "index.yaml").read_text()
    # Find the slug's block and its atlas_topic line
    in_block = False
    for line in idx.splitlines():
        if line.startswith(f"{slug}:"):
            in_block = True
            continue
        if in_block:
            if line and not line.startswith((" ", "\t", "#")):
                break  # next top-level slug
            m = re.match(r'\s*atlas_topic:\s*"?([^"]+)"?\s*$', line)
            if m:
                return m.group(1).strip()
    return None

def read_atlas_meta(atlas_topic):
    """Return dict with paper_title, venue, status, institution from the atlas
    topic (venue/status/paper_title from the first outputs entry; institution
    is a top-level field used for the cover affiliation line)."""
    if not atlas_topic:
        return {}
    path = vault_root / "atlas" / f"{atlas_topic}.md"
    if not path.exists():
        return {}
    txt = path.read_text()
    meta = {}
    # outputs: is a list; first entry runs until the next top-level key.
    m = re.search(r"^outputs:\s*\n((?:[ -].*\n)+)", txt, re.M)
    if m:
        first = m.group(1)
        for field in ("venue", "status", "paper_title", "format",
                      "camera_ready_submitted"):
            # First field of a YAML list entry starts with "- ", others with
            # leading spaces. Allow either.
            fm = re.search(rf"^[ \-]+{field}:\s*['\"]?([^'\"\n]+?)['\"]?\s*$",
                           first, re.M)
            if fm:
                v = fm.group(1).strip()
                # strip wiki brackets, taking the alias side of a pipe-form link
                v = re.sub(r"^\[\[(?:.*\|)?(.+?)\]\]$", r"\1", v)
                meta[field] = v
    # institution is a top-level field (drop any trailing `# comment`).
    im = re.search(r"^institution:\s*['\"]?([^'\"#\n]+?)['\"]?\s*(?:#.*)?$", txt, re.M)
    if im:
        meta["institution"] = im.group(1).strip()
    return meta

def read_myst_overrides(book_dir):
    """Pick up optional doi/arxiv/repo/conference_date/license fields."""
    p = book_dir / "myst.yml"
    if not p.exists():
        return {}
    txt = p.read_text()
    out = {}
    for field in ("doi", "arxiv", "repo", "conference_date", "license",
                  "subtitle"):
        fm = re.search(rf"^\s+{field}:\s*['\"]?([^'\"\n]+?)['\"]?\s*$",
                       txt, re.M)
        if fm:
            out[field] = fm.group(1).strip()
    return out

def read_book_index_title(slug):
    """Return the book's registry title from books/index.yaml, or None."""
    idx = (vault_root / "books" / "index.yaml").read_text()
    in_block = False
    for line in idx.splitlines():
        if line.startswith(f"{slug}:"):
            in_block = True
            continue
        if in_block:
            if line and not line.startswith((" ", "\t", "#")):
                break
            m = re.match(r'\s*title:\s*["\']?(.+?)["\']?\s*$', line)
            if m:
                return m.group(1).strip()
    return None

# "Last updated" date = most recent chapter-file edit, formatted exactly like
# the web cover at books.example.com/<slug> ("5 Jun 2026"), so the PDF
# frontispiece and the web cover never show different dates.
import datetime as _dt
# Chapter files only — exclude hidden dotfiles (e.g. .audit-report-*.md that
# /audit-paper-book leaves behind); pathlib.glob matches them but the web
# cover's registered-chapter set does not, so including them would desync the
# two dates.
_mtimes = [p.stat().st_mtime for p in book_dir.glob("*.md") if not p.name.startswith(".")]
last_updated = None
if _mtimes:
    _d = _dt.date.fromtimestamp(max(_mtimes))
    last_updated = f"{_d.day} {_d.strftime('%b %Y')}"

atlas_topic = read_book_index_atlas_topic(slug)
atlas_meta  = read_atlas_meta(atlas_topic)
overrides   = read_myst_overrides(book_dir)

# myst.yml overrides win over atlas
meta = {**atlas_meta, **{k: v for k, v in overrides.items() if v}}

s = main_tex.read_text()

# Swap the 8-bit font stack for fontspec so xelatex can render the unicode
# glyphs mystmd emits (callout arrows, set membership, box-drawing chars).
# Use Latin Modern via its .otf files (kpsewhich-resolvable on TeX Live)
# plus a small \newunicodechar map for the glyphs lmodern doesn't carry.
font_block = (
    "\\usepackage{fontspec}\n"
    # Latin Modern via the explicit .otf basenames shipped with TeX Live —
    # fontspec resolves via kpathsea so we don't need fontconfig registration.
    "\\setmainfont{lmroman10-regular.otf}[\n"
    "  Path=, BoldFont=lmroman10-bold.otf,\n"
    "  ItalicFont=lmroman10-italic.otf,\n"
    "  BoldItalicFont=lmroman10-bolditalic.otf]\n"
    "\\setsansfont{lmsans10-regular.otf}[\n"
    "  Path=, BoldFont=lmsans10-bold.otf,\n"
    "  ItalicFont=lmsans10-oblique.otf,\n"
    "  BoldItalicFont=lmsans10-boldoblique.otf]\n"
    "\\setmonofont{lmmono10-regular.otf}[\n"
    "  Path=, BoldFont=lmmonolt10-bold.otf,\n"
    "  ItalicFont=lmmono10-italic.otf]\n"
    "\\usepackage{newunicodechar}\n"
    "\\newunicodechar{↗}{$\\nearrow$}\n"
    "\\newunicodechar{∈}{$\\in$}\n"
    "\\newunicodechar{─}{-}\n"
    "\\newunicodechar{├}{|-}\n"
    "\\newunicodechar{└}{`-}\n"
    "\\newunicodechar{│}{|}\n"
    # mystmd emits \rightarrow, \leftarrow, etc. in text mode when the source
    # markdown contains unicode arrows — wrap them in \ensuremath so they work
    # outside of explicit $...$.
    "\\let\\origrightarrow\\rightarrow\n"
    "\\renewcommand{\\rightarrow}{\\ensuremath{\\origrightarrow}}\n"
    "\\let\\origleftarrow\\leftarrow\n"
    "\\renewcommand{\\leftarrow}{\\ensuremath{\\origleftarrow}}\n"
    "\\let\\origRightarrow\\Rightarrow\n"
    "\\renewcommand{\\Rightarrow}{\\ensuremath{\\origRightarrow}}\n"
    "\\let\\origLeftarrow\\Leftarrow\n"
    "\\renewcommand{\\Leftarrow}{\\ensuremath{\\origLeftarrow}}\n"
    # Standard research math macros that mirror the source papers' preambles
    # and the web book's MathJax macro set (atlas prose-assets.html). Use
    # \providecommand so a book-specific myst.yml `math:` definition — which
    # mystmd expands inline before this preamble runs — always wins; this is
    # just the default net so every book's PDF resolves the common shorthand
    # without per-book config. \ensuremath wraps each so they also survive in
    # text mode (mystmd can emit them outside $...$, like the arrows above).
    # \1 = the double-stroke indicator 𝟙 via dsfont's \mathds.
    "\\usepackage{dsfont}\n"
    "\\providecommand{\\Prob}{\\ensuremath{\\mathbb{P}}}\n"
    "\\providecommand{\\E}{\\ensuremath{\\mathbb{E}}}\n"
    "\\providecommand{\\Var}{\\ensuremath{\\operatorname{Var}}}\n"
    "\\providecommand{\\1}{\\ensuremath{\\mathds{1}}}\n"
)
s = re.sub(
    r"\\usepackage\[T1\]\{fontenc\}\s*\n"
    r"\\usepackage\[utf8\]\{inputenc\}\s*\n"
    r"\\usepackage\{lmodern\}\s*\n",
    lambda _m: font_block,
    s,
)

# Compose a custom frontispiece title page from atlas meta + myst overrides.
# Mirrors the web cover at books.example.com/<slug>: a "Reading Companion"
# eyebrow, the book title, a "Companion to <paper>" line, author, the
# venue/status/institution row, and publication IDs at the foot — all on
# page 1 (the book-class default \maketitle would otherwise be bare).
def _texesc(t):
    # Escape the three characters that are almost always literal text in these
    # metadata fields. Leave $ { } alone so any inline math/grouping survives.
    return (t.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
            if isinstance(t, str) else t)

# Prefer a display title with the "— A Reading Companion" suffix stripped so it
# doesn't echo the "Reading Companion" eyebrow; fall back to \@title otherwise.
_book_title = read_book_index_title(slug)
if _book_title:
    _disp = re.sub(r"\s*[—–-]\s*An?\s+.*\bCompanion\s*$", "", _book_title,
                   flags=re.I).strip()
    title_tex = "{\\Huge\\bfseries " + _texesc(_disp or _book_title) + " \\par}"
else:
    title_tex = "{\\Huge\\bfseries \\@title \\par}"

companion = _texesc(meta.get("paper_title"))

venue_bits = []
for k in ("venue", "status", "institution"):
    if meta.get(k):
        venue_bits.append(_texesc(meta[k]))
if meta.get("conference_date"):
    venue_bits.append(_texesc(meta["conference_date"]))

id_bits = []
if meta.get("doi"):
    id_bits.append(f"DOI: \\href{{https://doi.org/{meta['doi']}}}"
                   f"{{{meta['doi']}}}")
if meta.get("arxiv"):
    id_bits.append(f"arXiv: \\href{{https://arxiv.org/abs/{meta['arxiv']}}}"
                   f"{{{meta['arxiv']}}}")
if meta.get("repo"):
    id_bits.append(f"Code: \\href{{{meta['repo']}}}{{{meta['repo']}}}")

# Build the titlepage body line by line. Always applied — even with no
# publication metadata the eyebrow + title + author + date beats the default.
tp = [
    "    \\centering",
    "    \\vspace*{\\fill}",
    "    {\\large\\scshape Reading Companion\\par}",
    "    \\vskip 0.7em",
    "    \\rule{3cm}{0.4pt}\\par",
    "    \\vskip 2.2em",
    "    " + title_tex,
]
if companion:
    tp += [
        "    \\vskip 1.6em",
        "    {\\large\\itshape Companion to\\par}",
        "    \\vskip 0.35em",
        f"    {{\\large {companion}\\par}}",
    ]
tp += [
    "    \\vskip 1.6em",
    "    {\\large \\@author \\par}",
]
if venue_bits:
    tp += [
        "    \\vskip 0.8em",
        "    {\\small " + " $\\cdot$ ".join(venue_bits) + "\\par}",
    ]
tp += [
    "    \\vskip 2.2em",
    "    \\rule{3cm}{0.4pt}\\par",
    "    \\vspace*{\\fill}",
]
if id_bits:
    tp += [
        "    {\\footnotesize " + " \\\\\n".join(id_bits) + "\\par}",
        "    \\vskip 1em",
    ]
if last_updated:
    tp += [f"    {{\\footnotesize Last updated {last_updated}\\par}}"]
else:
    tp += ["    {\\footnotesize \\@date \\par}"]

pub_block = (
    "\n% --- custom title page (replaces book-class \\maketitle) ---\n"
    "\\makeatletter\n"
    "\\renewcommand{\\maketitle}{%\n"
    "  \\begin{titlepage}%\n"
    + "\n".join(tp) + "\n"
    "  \\end{titlepage}%\n"
    "}\n"
    "\\makeatother\n"
    "% --- end custom title page ---\n"
)
s = s.replace("\\begin{document}", pub_block + "\n\\begin{document}", 1)

main_tex.write_text(s)
PY

echo "[4/5] patching per-chapter tex (section→chapter)"
# Per-chapter files are <PREFIX>-<chapter>.tex. Bump heading depth one level so
# the book class produces 1.x / 2.x / ... chapter numbering instead of 0.x.
# Use Python with sentinels to avoid sed's order-dependent reapplication.
python3 - "$TEX_DIR" "$PREFIX" <<'PY'
import re, sys, pathlib
tex_dir = pathlib.Path(sys.argv[1])
prefix  = sys.argv[2]
pattern = f"{prefix}-*.tex"

REPLACEMENTS = [
    (r"\\section\*?\{",       r"\chapter{"),
    (r"\\subsection\*?\{",    r"\section{"),
    (r"\\subsubsection\*?\{", r"\subsection{"),
    (r"\\paragraph\{",        r"\subsubsection{"),
]

for chap in tex_dir.glob(pattern):
    s = chap.read_text()
    # Sentinel pass to avoid re-application
    for i, (src, _) in enumerate(REPLACEMENTS):
        s = re.sub(src, f"@@H{i}@@{{", s)
    for i, (_, dst) in enumerate(REPLACEMENTS):
        s = s.replace(f"@@H{i}@@{{", dst)
    # mystmd emits unicode arrows/ellipses as bare \rightarrow, \dots etc. — TeX
    # glues them to a following letter (\rightarrowPS / \dotsmoves → undefined
    # cs). Insert {} to terminate the control sequence when followed by a letter.
    s = re.sub(r"(\\(?:right|left|up|down|Right|Left|Up|Down)arrow|\\dots|\\ldots)([A-Za-z])",
               r"\1{}\2", s)
    chap.write_text(s)
PY

echo "[5/5] latexmk -xelatex"
cd "$TEX_DIR"
latexmk -xelatex -interaction=nonstopmode -halt-on-error "$(basename "$MAIN_TEX")" >/dev/null 2>&1 || {
  echo "warning: latexmk had errors; see $BOOK_DIR/$TEX_DIR/$(basename "$MAIN_TEX" .tex).log" >&2
}

PDF_NAME="$(basename "$MAIN_TEX" .tex).pdf"
if [[ ! -f "$PDF_NAME" ]]; then
  echo "error: PDF not produced — inspect $BOOK_DIR/$TEX_DIR/$(basename "$MAIN_TEX" .tex).log" >&2
  exit 2
fi

cd "$BOOK_DIR"
mkdir -p exports
cp "$TEX_DIR/$PDF_NAME" "exports/$SLUG.pdf"
echo "done → $BOOK_DIR/exports/$SLUG.pdf"
