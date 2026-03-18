"""Markdown formatting functions for OpenAlex API results."""

from typing import Any


def _get_authors_str(work: dict[str, Any], max_authors: int = 3) -> str:
    """Extract author names from a work, truncating if needed."""
    authorships = work.get("authorships", [])
    names = [a["author"]["display_name"] for a in authorships if a.get("author")]
    if len(names) > max_authors:
        return ", ".join(names[:max_authors]) + " et al."
    return ", ".join(names) if names else "Unknown"


def _get_journal(work: dict[str, Any]) -> str:
    """Extract journal/source name from a work."""
    loc = work.get("primary_location") or {}
    source = loc.get("source") or {}
    return source.get("display_name", "")


def _clean_doi(doi: str | None) -> str:
    """Strip https://doi.org/ prefix from DOI."""
    if not doi:
        return ""
    return doi.replace("https://doi.org/", "")


def format_works_table(works: list[dict[str, Any]], title: str = "Results") -> str:
    """Format a list of works as a markdown table."""
    if not works:
        return f"## {title}\n\nNo results found."

    lines = [
        f"## {title}\n",
        f"**{len(works)} works**\n",
        "| # | Title | Authors | Year | Journal | Cites | DOI |",
        "|---|-------|---------|------|---------|-------|-----|",
    ]

    for i, w in enumerate(works, 1):
        title_text = (w.get("title") or "Untitled")[:80]
        authors = _get_authors_str(w)
        year = w.get("publication_year", "")
        journal = _get_journal(w)[:30]
        cites = w.get("cited_by_count", 0)
        doi = _clean_doi(w.get("doi"))
        lines.append(f"| {i} | {title_text} | {authors} | {year} | {journal} | {cites} | {doi} |")

    return "\n".join(lines)


def format_author_profile(analysis: dict[str, Any]) -> str:
    """Format research output analysis as markdown."""
    if "error" in analysis:
        return f"**Error:** {analysis['error']}"

    lines = [
        f"## {analysis['entity_name']}",
        "",
        f"- **Total works:** {analysis['total_works']}",
        f"- **Open access:** {analysis['open_access_works']} ({analysis['open_access_percentage']}%)",
        "",
        "### Publications by Year",
        "",
        "| Year | Count |",
        "|------|-------|",
    ]

    for entry in sorted(analysis.get("publications_by_year", []),
                        key=lambda x: x.get("key", ""), reverse=True):
        lines.append(f"| {entry.get('key', '')} | {entry.get('count', 0)} |")

    topics = analysis.get("top_topics", [])
    if topics:
        lines.extend(["", "### Top Topics", "", "| Topic | Count |", "|-------|-------|"])
        for t in topics[:10]:
            name = t.get("key_display_name", t.get("key", ""))
            lines.append(f"| {name} | {t.get('count', 0)} |")

    return "\n".join(lines)


def format_trends(trends: list[dict[str, Any]], search_term: str = "") -> str:
    """Format publication trends as markdown."""
    if not trends:
        return "No trend data found."

    header = f"## Publication Trends"
    if search_term:
        header += f": {search_term}"

    sorted_trends = sorted(trends, key=lambda x: x.get("key", ""), reverse=True)

    lines = [
        header,
        "",
        "| Year | Publications |",
        "|------|-------------|",
    ]

    for entry in sorted_trends[:20]:
        lines.append(f"| {entry.get('key', '')} | {entry.get('count', 0)} |")

    return "\n".join(lines)


def format_work_detail(work: dict[str, Any]) -> str:
    """Format a single work with full metadata."""
    title = work.get("title") or "Untitled"
    authors = _get_authors_str(work, max_authors=10)
    year = work.get("publication_year", "")
    journal = _get_journal(work)
    doi = _clean_doi(work.get("doi"))
    cites = work.get("cited_by_count", 0)
    oa = work.get("open_access", {})
    oa_status = oa.get("oa_status", "unknown")
    oa_url = oa.get("oa_url", "")

    # Reconstruct abstract from inverted index
    abstract = ""
    inv_index = work.get("abstract_inverted_index")
    if inv_index:
        word_positions: list[tuple[int, str]] = []
        for word, positions in inv_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join(w for _, w in word_positions)

    lines = [
        f"## {title}",
        "",
        f"**Authors:** {authors}",
        f"**Year:** {year}",
        f"**Journal:** {journal}",
        f"**DOI:** {doi}",
        f"**Citations:** {cites}",
        f"**Open Access:** {oa_status}",
    ]

    if oa_url:
        lines.append(f"**OA URL:** {oa_url}")

    work_type = work.get("type", "")
    if work_type:
        lines.append(f"**Type:** {work_type}")

    if abstract:
        lines.extend(["", "### Abstract", "", abstract])

    # Concepts/topics
    topics = work.get("topics", [])
    if topics:
        topic_names = [t.get("display_name", "") for t in topics[:5]]
        lines.extend(["", f"**Topics:** {', '.join(topic_names)}"])

    return "\n".join(lines)
