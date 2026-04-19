"""OpenCitations tools (2 tools, always available)."""

from tools._registry import Tool, ToolResult, register

from _app import _opencitations_client


# ---------- Handlers ----------


async def _handle_opencitations_citations(args: dict) -> ToolResult:
    doi = args["doi"]
    limit = args.get("limit")

    citations = await _opencitations_client.get_citations(doi, limit=limit)

    if not citations:
        return ToolResult(text=f"No citations found in OpenCitations for: {doi}")

    count = await _opencitations_client.get_citation_count(doi)

    lines = [f"## OpenCitations: Papers citing {doi}\n"]
    lines.append(f"**Total citations:** {count}\n")
    lines.append("| # | Citing DOI | Date |")
    lines.append("|---|-----------|------|")

    for i, c in enumerate(citations[:50], 1):
        citing_doi = c.citing
        date = c.creation or "—"
        lines.append(f"| {i} | [{citing_doi}](https://doi.org/{citing_doi}) | {date} |")

    if len(citations) > 50:
        lines.append(f"\n*Showing 50 of {len(citations)} citations*")

    lines.append(f"\n*Source: OpenCitations COCI (fully open citation index)*")
    return ToolResult(text="\n".join(lines))


async def _handle_opencitations_references(args: dict) -> ToolResult:
    doi = args["doi"]
    limit = args.get("limit")

    references = await _opencitations_client.get_references(doi, limit=limit)

    if not references:
        return ToolResult(text=f"No references found in OpenCitations for: {doi}")

    lines = [f"## OpenCitations: References of {doi}\n"]
    lines.append("| # | Referenced DOI | Date |")
    lines.append("|---|--------------|------|")

    for i, r in enumerate(references, 1):
        cited_doi = r.cited
        date = r.creation or "—"
        lines.append(f"| {i} | [{cited_doi}](https://doi.org/{cited_doi}) | {date} |")

    lines.append(f"\n*{len(references)} references (Source: OpenCitations COCI)*")
    return ToolResult(text="\n".join(lines))


# ---------- Registration ----------

_TOOLS = [
    (
        Tool(
            name="opencitations_citations",
            description=(
                "Get papers that cite a given DOI using the fully open COCI citation index. "
                "Returns citing DOIs with dates. Complements Semantic Scholar citations with "
                "a fully open, non-proprietary citation graph."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI to find citations for (with or without prefix)"},
                    "limit": {"type": "integer", "description": "Max results (default: all citations)"},
                },
                "required": ["doi"],
            },
        ),
        _handle_opencitations_citations,
    ),
    (
        Tool(
            name="opencitations_references",
            description="Get papers referenced by a given DOI (backward citations / bibliography). Returns cited DOIs. Use for tracing intellectual lineage.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI to find references for"},
                    "limit": {"type": "integer", "description": "Max results (default: all references)"},
                },
                "required": ["doi"],
            },
        ),
        _handle_opencitations_references,
    ),
]

for tool, handler in _TOOLS:
    register(tool, handler)
