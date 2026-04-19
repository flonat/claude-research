"""CORE tools (2 tools, conditional on API key)."""

from tools._registry import Tool, ToolResult, register

from _app import _core_source, format_papers_table


# ---------- Handlers ----------


async def _handle_core_search(args: dict) -> ToolResult:
    if not _core_source:
        return ToolResult(text="**Error:** CORE not configured (set CORE_API_KEY)")

    query = args["query"]
    limit = min(args.get("limit", 25), 100)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _core_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit
    )

    if not papers:
        return ToolResult(text=f"No CORE results for: {query}")

    text = format_papers_table(papers, title=f"CORE Search: {query}")

    with_text = sum(1 for p in papers if p.open_access_url)
    text += f"\n\n*{len(papers)} results from CORE ({with_text} with full text available)*"
    text += "\n*Use `core_get_fulltext` with the CORE ID to retrieve full paper text.*"
    return ToolResult(text=text)


async def _handle_core_get_fulltext(args: dict) -> ToolResult:
    if not _core_source:
        return ToolResult(text="**Error:** CORE not configured (set CORE_API_KEY)")

    core_id = args["core_id"]
    full_text = await _core_source.get_full_text(core_id)

    if not full_text:
        return ToolResult(text=f"No full text available for CORE ID: {core_id}")

    if len(full_text) > 50000:
        full_text = full_text[:50000] + f"\n\n... [truncated, {len(full_text)} chars total]"

    return ToolResult(text=f"## Full Text (CORE ID: {core_id})\n\n{full_text}")


# ---------- Registration (conditional) ----------

if _core_source:
    register(
        Tool(
            name="core_search_fulltext",
            description=(
                "Search CORE's 431M+ open access records. Unique: returns papers with "
                "full-text content available. Use when you need actual paper text, not just metadata. "
                "Supports year filtering."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (keywords, title fragment)"},
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 100)"},
                },
                "required": ["query"],
            },
        ),
        _handle_core_search,
    )
    register(
        Tool(
            name="core_get_fulltext",
            description=(
                "Get the full text of a paper by CORE ID. Returns the complete paper text. "
                "Use core_search_fulltext first to find the CORE ID (source_id field, format: core:12345)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "core_id": {"type": "integer", "description": "CORE work ID (numeric, from source_id field)"},
                },
                "required": ["core_id"],
            },
        ),
        _handle_core_get_fulltext,
    )
