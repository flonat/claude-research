"""Altmetric tools (2 tools, conditional on API key)."""

import json

from tools._registry import Tool, ToolResult, register

from _app import _altmetric_client


# ---------- Handlers ----------


async def _handle_altmetric_search(args: dict) -> ToolResult:
    if not _altmetric_client:
        return ToolResult(text="**Error:** Altmetric not configured (set ALTMETRIC_API_KEY + ALTMETRIC_API_PASSWORD)")

    query = args["query"]
    timeframe = args.get("timeframe", "all")
    limit = min(args.get("limit", 25), 100)

    outputs = await _altmetric_client.search(query, timeframe=timeframe, limit=limit)

    if not outputs:
        return ToolResult(text=f"No Altmetric results for: {query}")

    lines = [f"## Altmetric Search: {query}\n"]
    lines.append("| Score | Title | Tweets | News | Policy | Blogs | Wikipedia | Readers |")
    lines.append("|-------|-------|--------|------|--------|-------|-----------|---------|")

    for o in outputs:
        title = o.title[:50] + ("..." if len(o.title) > 50 else "")
        m = o.mentions
        tweets = m.get("tweet", 0)
        news = m.get("msm", 0)
        policy = m.get("policy", 0)
        blogs = m.get("blog", 0)
        wiki = m.get("wikipedia", 0)
        readers = o.readers.get("mendeley", 0)
        score = f"**{o.altmetric_score:.0f}**" if o.altmetric_score else "—"
        lines.append(f"| {score} | {title} | {tweets} | {news} | {policy} | {blogs} | {wiki} | {readers} |")

    lines.append(f"\n*{len(outputs)} results from Altmetric Explorer (timeframe: {timeframe})*")
    return ToolResult(text="\n".join(lines))


async def _handle_altmetric_attention_summary(args: dict) -> ToolResult:
    if not _altmetric_client:
        return ToolResult(text="**Error:** Altmetric not configured")

    query = args["query"]
    timeframe = args.get("timeframe", "all")

    data = await _altmetric_client.get_attention_summary(query, timeframe=timeframe)

    if not data:
        return ToolResult(text=f"No attention data for: {query}")

    lines = [f"## Attention Summary: {query}\n"]
    lines.append(f"```json\n{json.dumps(data, indent=2)[:2000]}\n```")
    lines.append(f"\n*Source: Altmetric Explorer (timeframe: {timeframe})*")
    return ToolResult(text="\n".join(lines))


# ---------- Registration (conditional) ----------

if _altmetric_client:
    register(
        Tool(
            name="altmetric_search",
            description=(
                "Search for research outputs with altmetric attention data. Returns papers "
                "with their altmetric score and mention breakdown (tweets, news, blogs, policy docs, "
                "Wikipedia, Reddit, Bluesky). Use to discover which papers on a topic get the most "
                "real-world attention beyond citations."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (topic, keywords)"},
                    "timeframe": {"type": "string", "description": "Time filter: 'all' (default), '1d', '1w', '1m', '3m', '6m', '1y'"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 100)"},
                },
                "required": ["query"],
            },
        ),
        _handle_altmetric_search,
    )
    register(
        Tool(
            name="altmetric_attention_summary",
            description=(
                "Get aggregate attention summary for a research topic. Returns total mentions, "
                "score distribution, and top sources. Use to understand the overall attention "
                "landscape for a field or topic."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Topic to analyze"},
                    "timeframe": {"type": "string", "description": "Time filter: 'all' (default), '1d', '1w', '1m', '3m', '6m', '1y'"},
                },
                "required": ["query"],
            },
        ),
        _handle_altmetric_attention_summary,
    )
