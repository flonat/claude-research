"""Unpaywall tools (1 tool, always available)."""

from mcp.types import Tool, TextContent

from _app import _unpaywall_client
from tools._registry import register


# ---------- Handler ----------


async def _handle_unpaywall(args: dict) -> list[TextContent]:
    doi = args["doi"]

    result = await _unpaywall_client.lookup(doi)

    if not result:
        return [TextContent(type="text", text=f"DOI not found in Unpaywall: {doi}")]

    lines = [f"## Unpaywall: {doi}\n"]

    if result.title:
        lines.append(f"**Title:** {result.title}")
    if result.journal:
        lines.append(f"**Journal:** {result.journal}")
    if result.publisher:
        lines.append(f"**Publisher:** {result.publisher}")

    oa_emoji = "Yes" if result.is_oa else "No"
    lines.append(f"**Open Access:** {oa_emoji}")
    if result.oa_status:
        lines.append(f"**OA Status:** {result.oa_status}")

    if result.pdf_url:
        lines.append(f"\n**PDF:** [{result.pdf_url}]({result.pdf_url})")
    elif result.best_oa_url:
        lines.append(f"\n**Best OA Link:** [{result.best_oa_url}]({result.best_oa_url})")
    else:
        lines.append("\n*No open access version found.*")

    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Registration ----------

register(
    Tool(
        name="unpaywall_find_pdf",
        description=(
            "Find an open access PDF for a DOI via Unpaywall. Returns the best available "
            "OA link, PDF URL, OA status (gold/green/hybrid/bronze/closed), journal, and publisher. "
            "Use after finding a paper to check if a free PDF is available."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {"type": "string", "description": "DOI to find OA PDF for (with or without prefix)"},
            },
            "required": ["doi"],
        },
    ),
    _handle_unpaywall,
)
