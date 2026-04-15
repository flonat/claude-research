"""Exa tools (3 tools, conditional — requires EXA_API_KEY)."""

from mcp.types import Tool, TextContent

from _app import _exa_client, format_papers_table, log
from tools._registry import register


if _exa_client is None:
    log("Exa tools: skipped (no API key)")
else:

    # ---------- Handlers ----------

    async def _handle_exa_search(args: dict) -> list[TextContent]:
        query = args["query"]
        num_results = min(args.get("num_results", 10), 50)
        search_type = args.get("search_type", "deep")
        category = args.get("category")
        include_domains = args.get("include_domains")
        exclude_domains = args.get("exclude_domains")
        include_text = args.get("include_text", True)

        results = await _exa_client.search(
            query,
            num_results=num_results,
            search_type=search_type,
            category=category,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_text=include_text,
        )

        if not results:
            return [TextContent(type="text", text=f"No Exa results for: {query}")]

        lines = [f"# Exa Search: {query}", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"## {i}. {r.title}")
            lines.append(f"**URL:** {r.url}")
            if r.published_date:
                lines.append(f"**Date:** {r.published_date}")
            if r.author:
                lines.append(f"**Author:** {r.author}")
            lines.append(f"**Score:** {r.score:.3f}")
            if r.text:
                # Show first 500 chars of content
                preview = r.text[:500] + ("..." if len(r.text) > 500 else "")
                lines.append(f"\n{preview}")
            if r.highlights:
                lines.append(f"\n**Highlights:** {'; '.join(r.highlights[:3])}")
            lines.append("")

        lines.append(f"*{len(results)} results from Exa ({search_type} search)*")
        return [TextContent(type="text", text="\n".join(lines))]

    async def _handle_exa_search_papers(args: dict) -> list[TextContent]:
        query = args["query"]
        num_results = min(args.get("num_results", 10), 50)

        papers = await _exa_client.search_papers(
            query, num_results=num_results,
        )

        if not papers:
            return [TextContent(type="text", text=f"No Exa paper results for: {query}")]

        text = format_papers_table(papers, title=f"Exa Papers: {query}")
        text += f"\n\n*{len(papers)} papers from Exa (deep search, research paper category)*"
        return [TextContent(type="text", text=text)]

    async def _handle_exa_get_contents(args: dict) -> list[TextContent]:
        urls = args["urls"]
        max_characters = args.get("max_characters", 20000)

        results = await _exa_client.get_contents(urls, max_characters=max_characters)

        if not results:
            return [TextContent(type="text", text="No content retrieved for the given URLs.")]

        lines = [f"# Exa Content Retrieval ({len(results)} URLs)", ""]
        for r in results:
            lines.append(f"## {r.title}")
            lines.append(f"**URL:** {r.url}")
            if r.text:
                lines.append(f"\n{r.text[:max_characters]}")
            lines.append("")

        return [TextContent(type="text", text="\n".join(lines))]

    # ---------- Registration ----------

    register(
        Tool(
            name="exa_search",
            description=(
                "Semantic web search via Exa. Understands meaning, not just keywords. "
                "Search types: 'deep' (multi-query, 4-12s, best quality), 'auto' (balanced), "
                "'fast' (real-time). Optional category filter: 'research paper', 'news', "
                "'company', 'people'. Can filter by domain."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"},
                    "num_results": {"type": "integer", "description": "Number of results (1-50, default 10)"},
                    "search_type": {
                        "type": "string",
                        "enum": ["auto", "deep", "fast"],
                        "description": "Search type (default: deep)",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["research paper", "news", "company", "people"],
                        "description": "Optional content category filter",
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Only return results from these domains",
                    },
                    "exclude_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Exclude results from these domains",
                    },
                    "include_text": {"type": "boolean", "description": "Fetch full text content (default: true)"},
                },
                "required": ["query"],
            },
        ),
        _handle_exa_search,
    )

    register(
        Tool(
            name="exa_search_papers",
            description=(
                "Search for research papers via Exa's semantic engine. Uses 'research paper' "
                "category filter and deep search. Returns Paper objects compatible with other "
                "scholarly tools. Good for finding grey literature, working papers, and preprints "
                "not indexed by traditional academic databases."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research topic or question"},
                    "num_results": {"type": "integer", "description": "Number of results (1-50, default 10)"},
                },
                "required": ["query"],
            },
        ),
        _handle_exa_search_papers,
    )

    register(
        Tool(
            name="exa_get_contents",
            description=(
                "Fetch full text content for known URLs via Exa. Use when you have URLs "
                "and need their text content (e.g., reading a blog post, working paper, "
                "or report that isn't in academic databases)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to fetch content from",
                    },
                    "max_characters": {"type": "integer", "description": "Max characters per result (default 20000)"},
                },
                "required": ["urls"],
            },
        ),
        _handle_exa_get_contents,
    )

    log("Exa tools: 3 registered (search, search_papers, get_contents)")
