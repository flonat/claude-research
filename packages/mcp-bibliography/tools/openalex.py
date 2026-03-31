"""OpenAlex + Crossref tools (8 tools, always available)."""

import asyncio

from mcp.types import Tool, TextContent

from _app import (
    client,
    _crossref_source,
    log,
    find_author_works,
    analyze_research_output,
    get_publication_trends,
    format_works_table,
    format_author_profile,
    format_trends,
    format_work_detail,
)
from tools._registry import register


# ---------- Handlers ----------


async def _handle_search_works(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    sort = args.get("sort", "cited_by_count:desc")

    filter_params: dict[str, str] = {}
    if args.get("year"):
        filter_params["publication_year"] = args["year"]
    if args.get("min_citations"):
        filter_params["cited_by_count"] = f">{args['min_citations']}"
    if args.get("open_access"):
        filter_params["is_oa"] = "true"

    def _search():
        return client.search_works(
            search=query,
            filter_params=filter_params if filter_params else None,
            per_page=limit,
            sort=sort,
        )

    response = await asyncio.to_thread(_search)
    works = response.get("results", [])
    total = response.get("meta", {}).get("count", 0)

    text = format_works_table(works, title=f"Search: {query}")
    text += f"\n\n*{total:,} total results in OpenAlex (showing top {len(works)})*"
    return [TextContent(type="text", text=text)]


async def _handle_author_works(args: dict) -> list[TextContent]:
    author_name = args["author_name"]
    limit = min(args.get("limit", 50), 100)

    works = await asyncio.to_thread(find_author_works, author_name, client, limit)
    text = format_works_table(works, title=f"Works by {author_name}")
    return [TextContent(type="text", text=text)]


async def _handle_author_profile(args: dict) -> list[TextContent]:
    author_name = args["author_name"]
    years = args.get("years", ">2020")

    analysis = await asyncio.to_thread(
        analyze_research_output, "author", author_name, client, years
    )
    text = format_author_profile(analysis)
    return [TextContent(type="text", text=text)]


async def _handle_institution_output(args: dict) -> list[TextContent]:
    institution_name = args["institution_name"]
    years = args.get("years", ">2020")

    analysis = await asyncio.to_thread(
        analyze_research_output, "institution", institution_name, client, years
    )
    text = format_author_profile(analysis)
    return [TextContent(type="text", text=text)]


async def _handle_trends(args: dict) -> list[TextContent]:
    query = args["query"]

    trends = await asyncio.to_thread(get_publication_trends, query, None, client)
    text = format_trends(trends, search_term=query)
    return [TextContent(type="text", text=text)]


async def _handle_lookup_doi(args: dict) -> list[TextContent]:
    doi = args["doi"]
    if not doi.startswith("https://doi.org/"):
        doi = f"https://doi.org/{doi}"

    work = await asyncio.to_thread(client.get_entity, "works", doi)
    text = format_work_detail(work)
    return [TextContent(type="text", text=text)]


async def _handle_citing_works(args: dict) -> list[TextContent]:
    doi = args["doi"]
    limit = min(args.get("limit", 25), 50)

    if not doi.startswith("https://doi.org/"):
        doi = f"https://doi.org/{doi}"

    work = await asyncio.to_thread(client.get_entity, "works", doi)
    cited_by_url = work.get("cited_by_api_url")

    if not cited_by_url:
        return [TextContent(type="text", text="No citation data available for this work.")]

    import requests

    def _fetch_citing():
        resp = requests.get(
            cited_by_url,
            params={"mailto": client.email, "per-page": limit},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    data = await asyncio.to_thread(_fetch_citing)
    citing_works = data.get("results", [])
    total = data.get("meta", {}).get("count", 0)

    title_text = (work.get("title") or "this work")[:60]
    text = format_works_table(citing_works, title=f"Papers citing: {title_text}")
    text += f"\n\n*{total:,} total citing works (showing {len(citing_works)})*"
    return [TextContent(type="text", text=text)]


async def _handle_crossref_lookup_doi(args: dict) -> list[TextContent]:
    doi = args["doi"]
    paper = await _crossref_source.verify_doi(doi)

    if not paper:
        return [TextContent(type="text", text=f"DOI not found in Crossref: {doi}")]

    lines = [f"## {paper.title}\n"]
    lines.append(f"**Authors:** {', '.join(paper.authors)}")
    lines.append(f"**Year:** {paper.publication_year}")
    lines.append(f"**Citations:** {paper.cited_by_count:,}")
    if paper.source_name:
        lines.append(f"**Journal:** {paper.source_name}")
    if paper.doi:
        lines.append(f"**DOI:** {paper.doi}")
    if paper.abstract:
        lines.append(f"\n**Abstract:** {paper.abstract}")

    lines.append(f"\n*Source: Crossref (authoritative DOI registry) | Verified: Yes*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Tool definitions + registration ----------

_TOOLS = [
    (
        Tool(
            name="openalex_search_works",
            description=(
                "Search OpenAlex for scholarly papers by topic. Supports filters for "
                "year range, minimum citations, open access, and sort order. "
                "Returns a markdown table of results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (topic, keywords, title fragment)"},
                    "year": {"type": "string", "description": "Year filter: e.g. '2023', '>2020', '2020-2024'"},
                    "min_citations": {"type": "integer", "description": "Minimum citation count"},
                    "open_access": {"type": "boolean", "description": "Only return open access papers"},
                    "sort": {"type": "string", "description": "Sort order: 'cited_by_count:desc' (default), 'publication_date:desc', 'relevance_score:desc'"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 50)"},
                },
                "required": ["query"],
            },
        ),
        _handle_search_works,
    ),
    (
        Tool(
            name="openalex_author_works",
            description="Find publications by a specific author. Searches by name, resolves to OpenAlex author ID, returns their works.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_name": {"type": "string", "description": "Author name to search for"},
                    "limit": {"type": "integer", "description": "Max results (default 50, max 100)"},
                },
                "required": ["author_name"],
            },
        ),
        _handle_author_works,
    ),
    (
        Tool(
            name="openalex_author_profile",
            description="Analyze an author's research output: total works, open access %, publications by year, and top topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_name": {"type": "string", "description": "Author name to analyze"},
                    "years": {"type": "string", "description": "Year filter (default: '>2020')"},
                },
                "required": ["author_name"],
            },
        ),
        _handle_author_profile,
    ),
    (
        Tool(
            name="openalex_institution_output",
            description="Analyze an institution's research output: total works, open access %, publications by year, and top topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "institution_name": {"type": "string", "description": "Institution name to analyze"},
                    "years": {"type": "string", "description": "Year filter (default: '>2020')"},
                },
                "required": ["institution_name"],
            },
        ),
        _handle_institution_output,
    ),
    (
        Tool(
            name="openalex_trends",
            description="Get publication count trends over time for a search term. Returns yearly publication counts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term to track trends for"},
                },
                "required": ["query"],
            },
        ),
        _handle_trends,
    ),
    (
        Tool(
            name="openalex_lookup_doi",
            description="Look up a work by DOI. Returns full metadata including title, authors, abstract, citations, and open access status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI (with or without https://doi.org/ prefix)"},
                },
                "required": ["doi"],
            },
        ),
        _handle_lookup_doi,
    ),
    (
        Tool(
            name="openalex_citing_works",
            description="Find papers that cite a given work (forward citation tracking). Provide a DOI and get back the citing papers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI of the work to find citations for"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 50)"},
                },
                "required": ["doi"],
            },
        ),
        _handle_citing_works,
    ),
    (
        Tool(
            name="crossref_lookup_doi",
            description=(
                "Look up a DOI in Crossref, the authoritative DOI registry. Returns "
                "verified metadata: title, authors, journal, date, abstract, citation count. "
                "Use this to verify a DOI exists and get canonical metadata. More authoritative "
                "than OpenAlex for DOI verification."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI to look up (with or without https://doi.org/ prefix)"},
                },
                "required": ["doi"],
            },
        ),
        _handle_crossref_lookup_doi,
    ),
]

for tool, handler in _TOOLS:
    register(tool, handler)
