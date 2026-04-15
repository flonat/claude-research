"""OpenReview tools (3 tools, always available)."""

from mcp.types import Tool, TextContent

from _app import _openreview_client, format_papers_table
from tools._registry import register


# ---------- Handlers ----------


async def _handle_openreview_venue(args: dict) -> list[TextContent]:
    venue_id = args["venue_id"]
    limit = min(args.get("limit", 25), 1000)

    papers = await _openreview_client.get_venue_submissions(venue_id, limit=limit)

    if not papers:
        return [TextContent(type="text", text=f"No submissions found for venue: {venue_id}")]

    lines = [f"## OpenReview: {venue_id}\n"]
    lines.append("| # | Title | Authors | Keywords | Area | Forum ID |")
    lines.append("|---|-------|---------|----------|------|----------|")

    for i, p in enumerate(papers, 1):
        title = p.title[:60] + ("..." if len(p.title) > 60 else "")
        authors = ", ".join(p.authors[:3]) + ("..." if len(p.authors) > 3 else "")
        kw = ", ".join(p.keywords[:3]) if p.keywords else "—"
        area = p.primary_area or "—"
        if len(area) > 30:
            area = area[:30] + "..."
        lines.append(f"| {i} | [{title}](https://openreview.net/forum?id={p.forum_id}) | {authors} | {kw} | {area} | `{p.forum_id}` |")

    lines.append(f"\n*{len(papers)} submissions from OpenReview*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_openreview_reviews(args: dict) -> list[TextContent]:
    forum_id = args["forum_id"]

    paper = await _openreview_client.get_paper_with_reviews(forum_id)

    if not paper:
        return [TextContent(type="text", text=f"Paper not found: {forum_id}")]

    lines = [f"## {paper.title}\n"]
    lines.append(f"**Forum:** [openreview.net/forum?id={forum_id}](https://openreview.net/forum?id={forum_id})")
    if paper.authors:
        lines.append(f"**Authors:** {', '.join(paper.authors[:5])}")
    if paper.venue:
        lines.append(f"**Venue:** {paper.venue}")
    if paper.primary_area:
        lines.append(f"**Area:** {paper.primary_area}")
    if paper.keywords:
        lines.append(f"**Keywords:** {', '.join(paper.keywords)}")
    if paper.tldr:
        lines.append(f"**TLDR:** {paper.tldr}")
    if paper.abstract:
        lines.append(f"\n**Abstract:** {paper.abstract[:500]}{'...' if len(paper.abstract or '') > 500 else ''}")

    if paper.reviews:
        lines.append(f"\n### Reviews ({len(paper.reviews)})\n")
        for i, r in enumerate(paper.reviews, 1):
            lines.append(f"#### Reviewer {i}")
            if r.rating:
                lines.append(f"- **Rating:** {r.rating}")
            if r.soundness:
                lines.append(f"- **Soundness:** {r.soundness}")
            if r.presentation:
                lines.append(f"- **Presentation:** {r.presentation}")
            if r.contribution:
                lines.append(f"- **Contribution:** {r.contribution}")
            if r.confidence:
                lines.append(f"- **Confidence:** {r.confidence}")
            if r.strengths:
                lines.append(f"- **Strengths:** {r.strengths}")
            if r.weaknesses:
                lines.append(f"- **Weaknesses:** {r.weaknesses}")
            lines.append("")
    else:
        lines.append("\n*No reviews available.*")

    lines.append(f"\n*Source: OpenReview API v2*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_openreview_search(args: dict) -> list[TextContent]:
    query = args["query"]
    venue_id = args.get("venue_id")
    limit = min(args.get("limit", 25), 100)

    papers = await _openreview_client.search(query, venue_id=venue_id, limit=limit)

    if not papers:
        return [TextContent(type="text", text=f"No OpenReview results for: {query}")]

    lines = [f"## OpenReview Search: {query}\n"]
    if venue_id:
        lines[0] = f"## OpenReview Search: {query} (venue: {venue_id})\n"

    lines.append("| # | Title | Authors | Venue | Forum ID |")
    lines.append("|---|-------|---------|-------|----------|")

    for i, p in enumerate(papers, 1):
        title = p.title[:60] + ("..." if len(p.title) > 60 else "")
        authors = ", ".join(p.authors[:2]) + ("..." if len(p.authors) > 2 else "")
        venue = p.venue or p.venue_id or "—"
        if len(venue) > 30:
            venue = venue[:30] + "..."
        lines.append(f"| {i} | [{title}](https://openreview.net/forum?id={p.forum_id}) | {authors} | {venue} | `{p.forum_id}` |")

    lines.append(f"\n*{len(papers)} results from OpenReview*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Tool definitions + registration ----------

_TOOLS = [
    (
        Tool(
            name="openreview_venue_submissions",
            description=(
                "Get submissions for an AI/ML conference from OpenReview. Returns titles, abstracts, "
                "authors, keywords, and primary areas. Supports: NeurIPS, ICLR, ICML, ACL, EMNLP, "
                "AISTATS, UAI, CoRL, AAAI. Use shorthand like 'neurips/2024' or full ID."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string", "description": "Venue ID: shorthand (neurips/2024, iclr/2025) or full (NeurIPS.cc/2024/Conference)"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 1000)"},
                },
                "required": ["venue_id"],
            },
        ),
        _handle_openreview_venue,
    ),
    (
        Tool(
            name="openreview_paper_reviews",
            description=(
                "Get a paper and all its reviews from OpenReview. Returns the submission plus "
                "reviewer ratings, soundness, strengths, weaknesses, and questions. "
                "Provide the forum ID (from openreview_venue_submissions results)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "forum_id": {"type": "string", "description": "OpenReview forum ID for the paper"},
                },
                "required": ["forum_id"],
            },
        ),
        _handle_openreview_reviews,
    ),
    (
        Tool(
            name="openreview_search",
            description=(
                "Search OpenReview for papers by text query. Optionally filter by venue. "
                "Returns submissions matching the query. Use for finding specific papers "
                "or exploring what's been submitted to a conference on a topic."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (keywords, title fragment)"},
                    "venue_id": {"type": "string", "description": "Optional venue filter (e.g. neurips/2024)"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        ),
        _handle_openreview_search,
    ),
]

for tool, handler in _TOOLS:
    register(tool, handler)
