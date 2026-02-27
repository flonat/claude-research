#!/usr/bin/env python3
"""
Biblio MCP Server

Multi-source scholarly search: OpenAlex (always) + Scopus + Web of Science (when API keys provided).
Exposes both source-specific openalex_* tools and cross-source scholarly_* tools.
Imports the shared OpenAlex client from .scripts/openalex/ — single source of truth.
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import existing OpenAlex client and helpers
SCRIPTS_DIR = str(
    Path(__file__).parent.parent / ".scripts" / "openalex"
)
sys.path.insert(0, SCRIPTS_DIR)

# Add sources/ to path for multi-source adapters
SOURCES_DIR = str(Path(__file__).parent)
if SOURCES_DIR not in sys.path:
    sys.path.insert(0, SOURCES_DIR)

from openalex_client import OpenAlexClient  # noqa: E402
from query_helpers import (  # noqa: E402
    find_author_works,
    analyze_research_output,
    get_publication_trends,
)

from formatters import (  # noqa: E402
    format_works_table,
    format_author_profile,
    format_trends,
    format_work_detail,
)

# Multi-source imports
from sources.openalex_source import OpenAlexSource  # noqa: E402
from sources.multi_source import MultiSource  # noqa: E402
from sources.formatters import (  # noqa: E402
    format_papers_table,
    format_verification_table,
    format_source_status,
)


def log(msg):
    print(f"[biblio-mcp] {msg}", file=sys.stderr, flush=True)


# Shared client instance (polite pool)
client = OpenAlexClient(email="user@example.com")

# ---------- Multi-source initialization ----------

_all_sources = []
_source_info = []

# OpenAlex — always available
_openalex_source = OpenAlexSource(client)
_all_sources.append(_openalex_source)
_source_info.append({"name": "OpenAlex", "key": "openalex", "active": True})
log("OpenAlex source: active")

# Scopus — optional, requires SCOPUS_API_KEY
_scopus_key = os.environ.get("SCOPUS_API_KEY")
if _scopus_key:
    from sources.scopus_source import ScopusSource
    _scopus_inst_token = os.environ.get("SCOPUS_INST_TOKEN", "")
    _scopus_source = ScopusSource(_scopus_key, inst_token=_scopus_inst_token)
    _all_sources.append(_scopus_source)
    _source_info.append({"name": "Scopus", "key": "scopus", "active": True})
    log(f"Scopus source: active{' (InstToken)' if _scopus_inst_token else ''}")
else:
    _source_info.append({"name": "Scopus", "key": "scopus", "active": False})
    log("Scopus source: no API key")

# Web of Science — optional, requires WOS_API_KEY
_wos_key = os.environ.get("WOS_API_KEY")
_wos_tier = os.environ.get("WOS_API_TIER", "starter").lower()
if _wos_key:
    from sources.wos_source import WosSource
    _wos_source = WosSource(_wos_key, tier=_wos_tier)
    _all_sources.append(_wos_source)
    _source_info.append({"name": f"Web of Science ({_wos_tier})", "key": "wos", "active": True})
    log(f"WoS source: active (tier={_wos_tier})")
else:
    _source_info.append({"name": "Web of Science", "key": "wos", "active": False})
    log("WoS source: no API key")

# Composite source for cross-source queries
_multi_source = MultiSource(_all_sources) if len(_all_sources) > 1 else _openalex_source
log(f"Multi-source: {len(_all_sources)} source(s) active")

server = Server("biblio")
log("Server initialized")


# ---------- Tool definitions ----------

TOOLS = [
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
                "query": {
                    "type": "string",
                    "description": "Search query (topic, keywords, title fragment)",
                },
                "year": {
                    "type": "string",
                    "description": "Year filter: e.g. '2023', '>2020', '2020-2024'",
                },
                "min_citations": {
                    "type": "integer",
                    "description": "Minimum citation count",
                },
                "open_access": {
                    "type": "boolean",
                    "description": "Only return open access papers",
                },
                "sort": {
                    "type": "string",
                    "description": "Sort order: 'cited_by_count:desc' (default), 'publication_date:desc', 'relevance_score:desc'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="openalex_author_works",
        description=(
            "Find publications by a specific author. Searches by name, "
            "resolves to OpenAlex author ID, returns their works."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Author name to search for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 50, max 100)",
                },
            },
            "required": ["author_name"],
        },
    ),
    Tool(
        name="openalex_author_profile",
        description=(
            "Analyze an author's research output: total works, open access %, "
            "publications by year, and top topics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Author name to analyze",
                },
                "years": {
                    "type": "string",
                    "description": "Year filter (default: '>2020')",
                },
            },
            "required": ["author_name"],
        },
    ),
    Tool(
        name="openalex_institution_output",
        description=(
            "Analyze an institution's research output: total works, open access %, "
            "publications by year, and top topics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "institution_name": {
                    "type": "string",
                    "description": "Institution name to analyze",
                },
                "years": {
                    "type": "string",
                    "description": "Year filter (default: '>2020')",
                },
            },
            "required": ["institution_name"],
        },
    ),
    Tool(
        name="openalex_trends",
        description=(
            "Get publication count trends over time for a search term. "
            "Returns yearly publication counts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to track trends for",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="openalex_lookup_doi",
        description=(
            "Look up a work by DOI. Returns full metadata including title, "
            "authors, abstract, citations, and open access status."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI (with or without https://doi.org/ prefix)",
                },
            },
            "required": ["doi"],
        },
    ),
    Tool(
        name="openalex_citing_works",
        description=(
            "Find papers that cite a given work (forward citation tracking). "
            "Provide a DOI and get back the citing papers."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI of the work to find citations for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["doi"],
        },
    ),
]


# ---------- Scholarly tool definitions (cross-source) ----------

SCHOLARLY_TOOLS = [
    Tool(
        name="scholarly_search",
        description=(
            "Search for scholarly papers across ALL enabled sources (OpenAlex, Scopus, WoS) "
            "with automatic DOI-based deduplication. Returns merged results with the best "
            "metadata from each source."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (topic, keywords, title fragment)",
                },
                "year_from": {
                    "type": "integer",
                    "description": "Start year filter (inclusive)",
                },
                "year_to": {
                    "type": "integer",
                    "description": "End year filter (inclusive)",
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort: 'relevance' (default), 'cited_by_count', 'publication_year'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="scholarly_verify_dois",
        description=(
            "Batch-verify DOIs across all enabled sources. For each DOI, checks if it exists "
            "in OpenAlex, Scopus, and/or WoS. Returns verification status: VERIFIED (2+ sources), "
            "SINGLE_SOURCE (1 source), or NOT_FOUND. The killer tool for /literature Phase 4."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "dois": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of DOIs to verify (up to 50). With or without https://doi.org/ prefix.",
                },
            },
            "required": ["dois"],
        },
    ),
    Tool(
        name="scholarly_similar_works",
        description=(
            "Find papers similar to a given text (title or abstract) across all enabled sources. "
            "Results are deduplicated by DOI."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to find similar papers for (title, abstract, or topic description)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20, max 50)",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="scholarly_source_status",
        description=(
            "Show which scholarly data sources are configured and active. "
            "Reports OpenAlex (always), Scopus (if SCOPUS_API_KEY set), "
            "WoS (if WOS_API_KEY set)."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]

# Conditional source-specific tools
if _scopus_key:
    SCHOLARLY_TOOLS.append(
        Tool(
            name="scholarly_search_scopus",
            description=(
                "Search Scopus directly using Scopus query syntax (TITLE-ABS-KEY). "
                "Useful for ASJC subject codes and Scopus-specific features."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Scopus (TITLE-ABS-KEY syntax)",
                    },
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        )
    )

if _wos_key:
    SCHOLARLY_TOOLS.append(
        Tool(
            name="scholarly_search_wos",
            description=(
                "Search Web of Science directly using WoS query syntax (TS=). "
                "Useful for WoS-specific features and citation tracking."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for WoS (TS= syntax)",
                    },
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        )
    )


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS + SCHOLARLY_TOOLS


# ---------- Tool handlers ----------


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log(f"call_tool: {name} {arguments}")

    try:
        if name == "openalex_search_works":
            return await _handle_search_works(arguments)
        elif name == "openalex_author_works":
            return await _handle_author_works(arguments)
        elif name == "openalex_author_profile":
            return await _handle_author_profile(arguments)
        elif name == "openalex_institution_output":
            return await _handle_institution_output(arguments)
        elif name == "openalex_trends":
            return await _handle_trends(arguments)
        elif name == "openalex_lookup_doi":
            return await _handle_lookup_doi(arguments)
        elif name == "openalex_citing_works":
            return await _handle_citing_works(arguments)
        # Scholarly (cross-source) tools
        elif name == "scholarly_search":
            return await _handle_scholarly_search(arguments)
        elif name == "scholarly_verify_dois":
            return await _handle_scholarly_verify_dois(arguments)
        elif name == "scholarly_similar_works":
            return await _handle_scholarly_similar_works(arguments)
        elif name == "scholarly_source_status":
            return await _handle_scholarly_source_status(arguments)
        elif name == "scholarly_search_scopus":
            return await _handle_scholarly_search_scopus(arguments)
        elif name == "scholarly_search_wos":
            return await _handle_scholarly_search_wos(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"**Error:** {e}")]


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


# ---------- Scholarly tool handlers ----------


async def _handle_scholarly_search(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    year_from = args.get("year_from")
    year_to = args.get("year_to")
    sort_by = args.get("sort_by", "relevance")

    if isinstance(_multi_source, MultiSource):
        _multi_source.reset_diagnostics()

    papers = await _multi_source.search_works(
        query, year_from=year_from, year_to=year_to, sort_by=sort_by, limit=limit,
    )
    text = format_papers_table(papers, title=f"Scholarly Search: {query}")

    if isinstance(_multi_source, MultiSource):
        diag = _multi_source.consume_diagnostics()
        if diag:
            text += f"\n\n*Sources queried: {', '.join(diag['succeeded'])}"
            if diag["failed"]:
                text += f" | Failed: {', '.join(diag['failed'])}"
            text += f" | {len(papers)} results after dedup*"
    else:
        text += f"\n\n*Source: OpenAlex | {len(papers)} results*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_verify_dois(args: dict) -> list[TextContent]:
    dois = args["dois"]
    if len(dois) > 50:
        return [TextContent(type="text", text="**Error:** Maximum 50 DOIs per request.")]

    results = await _multi_source.batch_verify_dois(dois)
    text = format_verification_table(results)

    # Add source summary
    active_names = [s["name"] for s in _source_info if s["active"]]
    text += f"\n\n*Checked against: {', '.join(active_names)}*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_similar_works(args: dict) -> list[TextContent]:
    text_query = args["text"]
    limit = min(args.get("limit", 20), 50)

    papers = await _multi_source.find_similar_works(text_query, limit=limit)
    preview = text_query[:80] + "..." if len(text_query) > 80 else text_query
    text = format_papers_table(papers, title=f"Similar to: {preview}")
    text += f"\n\n*{len(papers)} results*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_source_status(args: dict) -> list[TextContent]:
    text = format_source_status(_source_info)
    active_count = sum(1 for s in _source_info if s["active"])
    text += f"\n\n*{active_count}/{len(_source_info)} sources active*"
    return [TextContent(type="text", text=text)]


async def _handle_scholarly_search_scopus(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _scopus_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit,
    )
    text = format_papers_table(papers, title=f"Scopus: {query}")
    text += f"\n\n*{len(papers)} results from Scopus*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_search_wos(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _wos_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit,
    )
    text = format_papers_table(papers, title=f"Web of Science: {query}")
    text += f"\n\n*{len(papers)} results from WoS*"

    return [TextContent(type="text", text=text)]


# ---------- Main ----------

async def main():
    log("Starting MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        log("stdio_server ready, running server...")
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )
    log("Server stopped")


if __name__ == "__main__":
    log("Main entry point")
    asyncio.run(main())
