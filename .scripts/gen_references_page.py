#!/usr/bin/env python3
"""Generate references.md from a .bib file in Harvard style.

Usage:
    gen_references_page.py <bib-path> <out-path> {public|private} [--paper-pdf <link>]

Output: a Markdown page with Harvard-style entries, one per bib record.
Each entry has an anchor `(ref-<citekey>)=` so chapters can cross-reference
with `{cite}` (mystmd's native cite, which resolves citekey → anchor) or with
plain Markdown links `[Author Year](#ref-citekey)`.

Public variant: just the bibliographic entry + DOI.
Private variant: same + RefPile and Paperpile links per entry.

Harvard format used (UK academic style, Cite Them Right):
    Author, A.B. and Author, C.D. (Year) 'Title of article', Journal Title,
    Volume(Issue), pp. start-end. Available at: <doi-link>.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENTRY_RE = re.compile(
    r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}\s*",
    re.DOTALL | re.IGNORECASE,
)
FIELD_RE = re.compile(
    r"\s*(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)\s*,?",
    re.DOTALL,
)


def clean_braces(s: str) -> str:
    """Strip BibTeX brace-protection (e.g., '{I}' → 'I')."""
    return re.sub(r"\{([^{}]*)\}", r"\1", s)


def parse_bib(text: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for m in ENTRY_RE.finditer(text):
        entry_type, key, body = m.group(1), m.group(2), m.group(3)
        fields: dict[str, str] = {"_type": entry_type.lower(), "_key": key}
        for fm in FIELD_RE.finditer(body):
            name = fm.group(1).lower()
            value = fm.group(2).strip()
            if value.startswith("{") and value.endswith("}"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            value = re.sub(r"\s+", " ", value).strip()
            fields[name] = value
        out.append(fields)
    return out


def format_author_harvard(name: str) -> str:
    """One author → '**Surname**, F.M.' Harvard style with bolded surname.

    Accepts both 'Last, First Middle' and 'First Middle Last' input forms.
    Bold surname makes the bibliography much faster to scan.
    """
    name = clean_braces(name).strip()
    if not name:
        return ""
    if "," in name:
        last, rest = (s.strip() for s in name.split(",", 1))
        first_parts = rest.split()
    else:
        parts = name.split()
        if len(parts) < 2:
            return f"**{name}**"
        last = parts[-1]
        first_parts = parts[:-1]
    initials = ".".join(p[0].upper() for p in first_parts if p) + "." if first_parts else ""
    if initials:
        return f"**{last}**, {initials}"
    return f"**{last}**"


def format_authors_harvard(raw: str) -> str:
    """Bibtex 'and'-separated → 'Surname, F.M., Surname, F. and Surname, F.'."""
    if not raw:
        return ""
    parts = re.split(r"\s+and\s+", raw)
    formatted = [format_author_harvard(p) for p in parts if p.strip()]
    if not formatted:
        return ""
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    return ", ".join(formatted[:-1]) + " and " + formatted[-1]


def format_authors_short(raw: str) -> str:
    """Heading-friendly: 'Surname et al.' / 'Surname & Surname2' / 'Surname'."""
    if not raw:
        return ""
    parts = re.split(r"\s+and\s+", raw)
    surnames: list[str] = []
    for p in parts:
        n = clean_braces(p).strip()
        if "," in n:
            last = n.split(",", 1)[0].strip()
        else:
            last = n.split()[-1] if n else ""
        if last:
            surnames.append(last)
    if not surnames:
        return ""
    if len(surnames) == 1:
        return surnames[0]
    if len(surnames) == 2:
        return f"{surnames[0]} and {surnames[1]}"
    return f"{surnames[0]} et al."


def format_pages(p: str) -> str:
    if not p:
        return ""
    p = p.replace("--", "–").replace("---", "—")
    return f"pp. {p}" if "–" in p or "—" in p or "-" in p or "," in p else f"p. {p}"


def format_volume_issue(e: dict[str, str]) -> str:
    vol = e.get("volume", "")
    issue = e.get("number", "") or e.get("issue", "")
    if vol and issue:
        return f"{vol}({issue})"
    return vol


def format_entry_harvard(e: dict[str, str], variant: str) -> str:
    """Single Harvard-style paragraph per entry — no heading repetition.

    Layout:
        (anchor — invisible)
        Harvard citation line (paragraph).
        — `citekey` · RefPile↗ · Paperpile↗   (private only adds the last two)
    """
    key = e["_key"]
    etype = e.get("_type", "")
    title = clean_braces(e.get("title", "").strip()).rstrip(".")
    authors_full = format_authors_harvard(e.get("author", ""))
    venue = clean_braces(e.get("journal") or e.get("booktitle") or e.get("publisher") or "")
    year = e.get("year", "")
    doi = e.get("doi", "")
    volissue = format_volume_issue(e)
    pages = format_pages(e.get("pages", ""))
    place = clean_braces(e.get("address", ""))
    publisher = clean_braces(e.get("publisher", ""))

    cite_parts: list[str] = []
    if authors_full:
        cite_parts.append(f"{authors_full} ({year})." if year else f"{authors_full}.")
    elif year:
        cite_parts.append(f"({year}).")

    # Title formatting depends on entry type
    if etype in ("book", "phdthesis", "mastersthesis", "techreport", "manual", "misc"):
        cite_parts.append(f"*{title}*.")
    else:
        cite_parts.append(f"'{title}'.")

    if venue and etype not in ("book", "phdthesis", "mastersthesis", "techreport"):
        venue_str = f"*{venue}*"
        if volissue:
            venue_str += f", {volissue}"
        if pages:
            venue_str += f", {pages}"
        cite_parts.append(f"{venue_str}.")

    if place and publisher and etype in ("book", "inbook", "incollection"):
        cite_parts.append(f"{place}: {publisher}.")
    elif publisher and etype in ("book", "inbook", "incollection"):
        cite_parts.append(f"{publisher}.")

    # DOI: full URL as visible link text (Cite Them Right Harvard style).
    # Explicit Markdown link (not <URL> autolink) to avoid mystmd's autolink-
    # as-citation rewriting that previously turned the URL into "Bradley &
    # Terry (1952)" because the URL was also in the bib.
    if doi:
        cite_parts.append(
            f"Available at: [https://doi.org/{doi}](https://doi.org/{doi})."
        )

    cite_line = " ".join(cite_parts)

    # Footer: only the private-side link.
    # Deployed RefPile is a Zotero-backed React SPA mounted at /. The Search
    # tab reads the `?q=` query string param (URLSearchParams in App.jsx),
    # so /?q=<citekey> lands on Search with the citekey pre-filled — the
    # paper appears as the top result. Direct /?item=<zotero_key> deep-link
    # would need a citekey→zotero_key resolver added to refpile's API
    # (TODO for a future session).
    # Paperpile dropped — closed-source SaaS with no public deeplink that
    # works by citekey. The DOI link in the Harvard cite line above is
    # the canonical publisher URL.
    if variant == "private":
        foot_line = (
            f"<small>[Look up in RefPile↗](https://refpile.com/?q={key})</small>\n"
        )
    else:
        foot_line = ""

    return f"(ref-{key})=\n{cite_line}\n\n{foot_line}"


def render_page(entries: list[dict[str, str]], variant: str, paper_pdf_link: str | None) -> str:
    sorted_entries = sorted(entries, key=lambda e: (
        format_authors_short(e.get("author", "")) or e["_key"]
    ).lower())
    head = [
        "---",
        "title: References",
        "short_title: References",
        "---",
        "",
        "# References",
        "",
        "Citations are formatted in Harvard style (Cite Them Right). " + (
            "Each entry links to the corresponding RefPile and Paperpile-search entries."
            if variant == "private"
            else "Each DOI links to the publisher page."
        ),
        "",
    ]
    if paper_pdf_link:
        head.append(f"For the original .bib file, see the [paper PDF]({paper_pdf_link}) bibliography.")
        head.append("")
    # Subtle thin horizontal rule between entries for visual separation
    body = []
    for i, e in enumerate(sorted_entries):
        if i > 0:
            body.append("\n---\n\n")
        body.append(format_entry_harvard(e, variant))
    return "".join(["\n".join(head)] + body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bib", type=Path, help="path to .bib file")
    ap.add_argument("out", type=Path, help="path to references.md to write")
    ap.add_argument("variant", choices=["public", "private"])
    ap.add_argument("--paper-pdf", default=None, help="optional link to paper PDF")
    args = ap.parse_args()

    if not args.bib.exists():
        sys.exit(f"bib not found: {args.bib}")
    text = args.bib.read_text()
    entries = parse_bib(text)
    print(f"[paper-book/refs] {args.bib.name}: parsed {len(entries)} entries → {args.out}")

    page = render_page(entries, args.variant, args.paper_pdf)
    args.out.write_text(page)


if __name__ == "__main__":
    main()
