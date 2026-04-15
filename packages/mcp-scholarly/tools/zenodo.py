"""Zenodo tools (2 tools, always available)."""

from mcp.types import Tool, TextContent

from _app import _zenodo_client
from tools._registry import register


# ---------- Handlers ----------


async def _handle_zenodo_search(args: dict) -> list[TextContent]:
    query = args["query"]
    resource_type = args.get("resource_type")
    limit = min(args.get("limit", 25), 100)

    records = await _zenodo_client.search(query, resource_type=resource_type, limit=limit)

    if not records:
        return [TextContent(type="text", text=f"No Zenodo results for: {query}")]

    lines = [f"## Zenodo: {query}\n"]
    if resource_type:
        lines[0] = f"## Zenodo ({resource_type}): {query}\n"

    lines.append("| # | Title | Type | DOI | Files | Access |")
    lines.append("|---|-------|------|-----|-------|--------|")

    for i, r in enumerate(records, 1):
        title = r.title[:50] + ("..." if len(r.title) > 50 else "")
        doi_link = f"[{r.doi}](https://doi.org/{r.doi})" if r.doi else "—"
        file_count = len(r.files)
        file_names = ", ".join(f.filename for f in r.files[:2])
        if len(r.files) > 2:
            file_names += f"... (+{len(r.files)-2})"
        rtype = r.resource_type or "—"
        access = r.access_right or "—"
        lines.append(f"| {i} | [{title}]({r.zenodo_url}) | {rtype} | {doi_link} | {file_count}: {file_names} | {access} |")

    lines.append(f"\n*{len(records)} results from Zenodo*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_zenodo_get_record(args: dict) -> list[TextContent]:
    record_id = args["record_id"]

    record = await _zenodo_client.get_record(record_id)

    if not record:
        return [TextContent(type="text", text=f"Zenodo record not found: {record_id}")]

    lines = [f"## {record.title}\n"]
    lines.append(f"**Zenodo:** [{record.zenodo_url}]({record.zenodo_url})")
    if record.doi:
        lines.append(f"**DOI:** [{record.doi}](https://doi.org/{record.doi})")
    if record.creators:
        lines.append(f"**Authors:** {', '.join(record.creators[:10])}")
    if record.publication_date:
        lines.append(f"**Date:** {record.publication_date}")
    if record.resource_type:
        lines.append(f"**Type:** {record.resource_type}")
    if record.access_right:
        lines.append(f"**Access:** {record.access_right}")
    if record.license:
        lines.append(f"**License:** {record.license}")
    if record.keywords:
        lines.append(f"**Keywords:** {', '.join(record.keywords)}")
    if record.description:
        lines.append(f"\n**Description:** {record.description}")

    if record.files:
        lines.append(f"\n### Files ({len(record.files)})\n")
        for f in record.files:
            size_mb = f.size / (1024 * 1024) if f.size else 0
            size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{f.size:,} bytes"
            dl = f" — [download]({f.download_url})" if f.download_url else ""
            lines.append(f"- `{f.filename}` ({size_str}){dl}")

    lines.append(f"\n*Source: Zenodo (CERN Open Repository)*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Registration ----------

_TOOLS = [
    (
        Tool(
            name="zenodo_search",
            description=(
                "Search Zenodo for research datasets, software, publications, and other outputs. "
                "Filter by type: 'dataset', 'software', 'publication', 'poster', 'presentation'. "
                "Use to find replication data, code repositories, and supplementary materials."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (keywords, topic, author name)"},
                    "resource_type": {"type": "string", "description": "Filter: 'dataset', 'software', 'publication', 'poster', 'presentation'"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 100)"},
                },
                "required": ["query"],
            },
        ),
        _handle_zenodo_search,
    ),
    (
        Tool(
            name="zenodo_get_record",
            description="Get a specific Zenodo record by ID. Returns full metadata including files (with download URLs), description, license, and DOI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "integer", "description": "Zenodo record ID (numeric)"},
                },
                "required": ["record_id"],
            },
        ),
        _handle_zenodo_get_record,
    ),
]

for tool, handler in _TOOLS:
    register(tool, handler)
