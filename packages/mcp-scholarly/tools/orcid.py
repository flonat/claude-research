"""ORCID tools (2 tools, conditional on credentials)."""

from mcp.types import Tool, TextContent

from _app import _orcid_client
from tools._registry import register


# ---------- Handlers ----------


async def _handle_orcid_search(args: dict) -> list[TextContent]:
    if not _orcid_client:
        return [TextContent(type="text", text="**Error:** ORCID not configured (set ORCID_CLIENT_ID + ORCID_CLIENT_SECRET)")]

    query = args["query"]
    limit = min(args.get("limit", 10), 100)

    results = await _orcid_client.search(query, limit=limit)

    if not results:
        return [TextContent(type="text", text=f"No ORCID profiles found for: {query}")]

    lines = [f"## ORCID Search: {query}\n"]
    lines.append(f"| # | ORCID iD | Name | Affiliations |")
    lines.append(f"|---|----------|------|-------------|")

    for i, r in enumerate(results, 1):
        name = r.credit_name or f"{r.given_names} {r.family_name}"
        institutions = ", ".join(r.institutions[:3]) if r.institutions else "—"
        lines.append(f"| {i} | [{r.orcid_id}](https://orcid.org/{r.orcid_id}) | {name} | {institutions} |")

    lines.append(f"\n*{len(results)} result(s) from ORCID registry*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_orcid_get_researcher(args: dict) -> list[TextContent]:
    if not _orcid_client:
        return [TextContent(type="text", text="**Error:** ORCID not configured (set ORCID_CLIENT_ID + ORCID_CLIENT_SECRET)")]

    orcid_id = args["orcid_id"]
    include_works = args.get("include_works", True)
    max_works = min(args.get("max_works", 50), 200)

    researcher = await _orcid_client.get_researcher(
        orcid_id,
        include_works=include_works,
        max_works=max_works,
    )

    if not researcher:
        return [TextContent(type="text", text=f"ORCID profile not found: {orcid_id}")]

    lines = [f"## {researcher.display_name}\n"]
    lines.append(f"**ORCID:** [{researcher.orcid_id}]({researcher.profile_url})")

    if researcher.affiliations:
        lines.append(f"**Affiliations:** {', '.join(researcher.affiliations)}")

    if researcher.biography:
        bio = researcher.biography[:500]
        if len(researcher.biography) > 500:
            bio += "..."
        lines.append(f"\n**Biography:** {bio}")

    if researcher.keywords:
        lines.append(f"**Keywords:** {', '.join(researcher.keywords)}")

    if researcher.urls:
        url_parts = [f"[{name}]({url})" for name, url in list(researcher.urls.items())[:5]]
        lines.append(f"**Links:** {' · '.join(url_parts)}")

    if researcher.works:
        lines.append(f"\n### Publications ({researcher.works_count} total, showing {len(researcher.works)})\n")
        lines.append("| Year | Title | DOI | Type |")
        lines.append("|------|-------|-----|------|")

        for w in sorted(researcher.works, key=lambda x: x.year or 0, reverse=True):
            year = str(w.year) if w.year else "—"
            title = w.title[:80] + ("..." if len(w.title) > 80 else "")
            doi_link = f"[{w.doi}](https://doi.org/{w.doi})" if w.doi else "—"
            wtype = (w.work_type or "—").replace("-", " ")
            lines.append(f"| {year} | {title} | {doi_link} | {wtype} |")

    lines.append(f"\n*Source: ORCID Public API v3.0*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Registration (conditional) ----------

if _orcid_client:
    register(
        Tool(
            name="orcid_search_researchers",
            description=(
                "Search the ORCID registry for researchers by name, affiliation, or keyword. "
                "Returns ORCID iDs with names and institutional affiliations. "
                "Query syntax: family-name:Smith, given-names:John, affiliation-org-name:Example, keyword:MCDM. "
                "Combine with AND/OR. Use this to find a researcher's ORCID iD for disambiguation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "ORCID search query (Lucene syntax: family-name:X AND affiliation-org-name:Y)"},
                    "limit": {"type": "integer", "description": "Max results (default 10, max 100)"},
                },
                "required": ["query"],
            },
        ),
        _handle_orcid_search,
    )
    register(
        Tool(
            name="orcid_get_researcher",
            description=(
                "Get a researcher's full ORCID profile: name, biography, affiliations, keywords, "
                "URLs, and publication list with DOIs. Provide an ORCID iD (e.g. 0000-0001-2345-6789). "
                "Use orcid_search_researchers first to find the iD if you only have a name."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "orcid_id": {"type": "string", "description": "ORCID identifier (e.g. 0000-0001-2345-6789 or https://orcid.org/0000-0001-2345-6789)"},
                    "include_works": {"type": "boolean", "description": "Include publication list (default true)"},
                    "max_works": {"type": "integer", "description": "Max works to return (default 50)"},
                },
                "required": ["orcid_id"],
            },
        ),
        _handle_orcid_get_researcher,
    )
