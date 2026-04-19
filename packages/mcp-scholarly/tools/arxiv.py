"""arXiv tools (3 tools, always available — no auth required)."""

from tools._registry import Tool, ToolResult, register

from _app import _arxiv_source, format_papers_table


# ---------- Handlers ----------


async def _handle_arxiv_search(args: dict) -> ToolResult:
    query = args["query"]
    limit = min(args.get("limit", 25), 200)
    year_from = args.get("year_from")
    year_to = args.get("year_to")
    category = args.get("category")

    if category:
        papers = await _arxiv_source.search_by_category(
            query, category, limit=limit
        )
    else:
        papers = await _arxiv_source.search_works(
            query, year_from=year_from, year_to=year_to, limit=limit
        )

    if not papers:
        return ToolResult(text=f"No arXiv results for: {query}")

    text = format_papers_table(papers, title=f"arXiv: {query}")
    text += f"\n\n*{len(papers)} results from arXiv*"
    return ToolResult(text=text)


async def _handle_arxiv_get_paper(args: dict) -> ToolResult:
    arxiv_id = args["arxiv_id"]
    paper = await _arxiv_source.get_paper(arxiv_id)

    if not paper:
        return ToolResult(text=f"arXiv paper not found: {arxiv_id}")

    lines = [
        f"# {paper.title}",
        f"**Authors:** {', '.join(paper.authors)}",
        f"**Year:** {paper.publication_year}",
        f"**arXiv ID:** {arxiv_id}",
    ]
    if paper.doi:
        lines.append(f"**DOI:** {paper.doi}")
    if paper.url:
        lines.append(f"**URL:** {paper.url}")
    if paper.open_access_url:
        lines.append(f"**PDF:** {paper.open_access_url}")
    if paper.keywords:
        lines.append(f"**Categories:** {', '.join(paper.keywords)}")
    if paper.abstract:
        lines.append(f"\n**Abstract:**\n{paper.abstract}")

    return ToolResult(text="\n".join(lines))


async def _handle_arxiv_search_category(args: dict) -> ToolResult:
    query = args["query"]
    category = args["category"]
    limit = min(args.get("limit", 25), 200)

    papers = await _arxiv_source.search_by_category(query, category, limit=limit)

    if not papers:
        return ToolResult(text=f"No arXiv results for '{query}' in category {category}")

    text = format_papers_table(papers, title=f"arXiv [{category}]: {query}")
    text += f"\n\n*{len(papers)} results from arXiv [{category}]*"
    return ToolResult(text=text)


# ---------- Registration ----------

register(
    Tool(
        name="arxiv_search",
        description=(
            "Search arXiv preprints. Covers physics, maths, CS, econ, "
            "quantitative biology/finance, statistics, and EE. Free, no auth. "
            "Optionally filter by arXiv category (e.g., econ.GN, cs.AI)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (keywords, title, author)"},
                "category": {"type": "string", "description": "arXiv category filter (e.g., econ.GN, cs.AI, cs.GT)"},
                "year_from": {"type": "integer", "description": "Start year filter"},
                "year_to": {"type": "integer", "description": "End year filter"},
                "limit": {"type": "integer", "description": "Max results (default 25, max 200)"},
            },
            "required": ["query"],
        },
    ),
    _handle_arxiv_search,
)

register(
    Tool(
        name="arxiv_get_paper",
        description=(
            "Fetch a single arXiv paper by its ID (e.g., '2301.07041'). "
            "Returns full metadata: title, authors, abstract, categories, PDF link, DOI if available."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "arxiv_id": {"type": "string", "description": "arXiv paper ID (e.g., '2301.07041' or 'math.GT/0309136')"},
            },
            "required": ["arxiv_id"],
        },
    ),
    _handle_arxiv_get_paper,
)

register(
    Tool(
        name="arxiv_search_category",
        description=(
            "Search within a specific arXiv category. Useful for targeted preprint discovery "
            "in a subdomain. Common categories: econ.GN (general economics), econ.TH (theory), "
            "cs.AI, cs.GT (game theory), cs.MA (multi-agent), stat.ML, q-fin.GN."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "category": {"type": "string", "description": "arXiv category (e.g., econ.GN, cs.AI)"},
                "limit": {"type": "integer", "description": "Max results (default 25, max 200)"},
            },
            "required": ["query", "category"],
        },
    ),
    _handle_arxiv_search_category,
)
