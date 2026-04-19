"""DBLP tools (1 tool, always available)."""

from tools._registry import Tool, ToolResult, register

from _app import _dblp_source, format_papers_table


# ---------- Handler ----------


async def _handle_dblp_search(args: dict) -> ToolResult:
    query = args["query"]
    limit = min(args.get("limit", 25), 1000)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _dblp_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit
    )

    if not papers:
        return ToolResult(text=f"No DBLP results for: {query}")

    text = format_papers_table(papers, title=f"DBLP: {query}")
    text += f"\n\n*{len(papers)} results from DBLP*"
    return ToolResult(text=text)


# ---------- Registration ----------

register(
    Tool(
        name="dblp_search",
        description=(
            "Search DBLP for computer science publications. Covers conferences, journals, "
            "books, and theses comprehensively. Free, no auth. Returns title, authors, venue, "
            "year, DOI. Use for CS venue metadata and author publication lists."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (keywords, title, author name)"},
                "year_from": {"type": "integer", "description": "Start year filter"},
                "year_to": {"type": "integer", "description": "End year filter"},
                "limit": {"type": "integer", "description": "Max results (default 25, max 1000)"},
            },
            "required": ["query"],
        },
    ),
    _handle_dblp_search,
)
