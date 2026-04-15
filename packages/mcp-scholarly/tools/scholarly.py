"""Cross-source scholarly tools (9+ tools, core always available)."""

import asyncio
import re
import time
import unicodedata

from _app import (
    _crossref_source,
    _multi_source,
    _orcid_client,
    _s2_source,
    _source_info,
    _scopus_key,
    _scopus_source,
    _wos_key,
    _wos_source,
    generate_bibtex_key,
    log,
    MultiSource,
    format_papers_table,
    format_verification_table,
    format_source_status,
)
from mcp.types import Tool, TextContent
from tools._registry import register


# ---------- Search cascade helpers ----------

CASCADE_TIMEOUT = 60  # seconds total budget for all strategies

_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "not", "no", "nor",
    "so", "if", "then", "than", "that", "this", "these", "those", "it",
    "its", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "over", "about", "such", "each", "which",
    "their", "we", "our", "how", "what", "when", "where", "who", "whom",
})


def _ascii_normalize(text: str) -> str:
    """Strip diacritics and normalize to ASCII."""
    nfkd = unicodedata.normalize("NFKD", text)
    return nfkd.encode("ascii", "ignore").decode("ascii")


def _generate_variants(query: str) -> list[str]:
    """Generate query variants for cascade search. Returns unique non-empty variants."""
    variants = []
    seen = {query.strip().lower()}

    # Variant 1: ASCII-normalized (removes diacritics)
    ascii_q = _ascii_normalize(query).strip()
    if ascii_q.lower() not in seen and ascii_q:
        variants.append(ascii_q)
        seen.add(ascii_q.lower())

    # Variant 2: dashes/hyphens to spaces
    dashed = query.replace("-", " ").replace("–", " ").replace("—", " ")
    dashed = re.sub(r"\s+", " ", dashed).strip()
    if dashed.lower() not in seen and dashed:
        variants.append(dashed)
        seen.add(dashed.lower())

    # Variant 3: remove quotes and special characters
    cleaned = re.sub(r'["""\'`():\[\]{}]', " ", query)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned.lower() not in seen and cleaned:
        variants.append(cleaned)
        seen.add(cleaned.lower())

    return variants


def _simplify_query(query: str) -> str | None:
    """Extract significant keywords from query (drop stopwords, keep first 5)."""
    words = re.findall(r"[a-zA-Z0-9]+", _ascii_normalize(query).lower())
    keywords = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    if len(keywords) < 2:
        return None
    return " ".join(keywords[:5])


def _collect_dois(papers) -> set[str]:
    """Extract DOI set from papers for deduplication."""
    return {p.doi.lower() for p in papers if p.doi}


def _dedup_papers(all_papers: list, seen_dois: set) -> list:
    """Remove papers whose DOI is already in seen_dois. Updates seen_dois in place."""
    unique = []
    for p in all_papers:
        doi_key = p.doi.lower() if p.doi else None
        if doi_key and doi_key in seen_dois:
            continue
        if doi_key:
            seen_dois.add(doi_key)
        unique.append(p)
    return unique


# ---------- Handlers ----------


async def _handle_scholarly_search(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    year_from = args.get("year_from")
    year_to = args.get("year_to")
    sort_by = args.get("sort_by", "relevance")

    start_time = time.monotonic()
    search_kwargs = dict(year_from=year_from, year_to=year_to, sort_by=sort_by, limit=limit)
    strategies_used = []
    all_diag_succeeded = set()
    all_diag_failed = set()

    if isinstance(_multi_source, MultiSource):
        _multi_source.reset_diagnostics()

    # --- Strategy 1: Original query ---
    papers = await _multi_source.search_works(query, **search_kwargs)
    strategies_used.append("original")
    seen_dois = _collect_dois(papers)

    if isinstance(_multi_source, MultiSource):
        diag = _multi_source.consume_diagnostics()
        if diag:
            all_diag_succeeded.update(diag.get("succeeded", []))
            all_diag_failed.update(diag.get("failed", []))

    # --- Strategy 2: Query variants (ASCII, dashes, cleaned) ---
    if len(papers) < 3:
        variants = _generate_variants(query)
        for variant in variants:
            elapsed = time.monotonic() - start_time
            if elapsed > CASCADE_TIMEOUT:
                log(f"Cascade timeout after {elapsed:.1f}s, stopping variants")
                break
            if len(papers) >= limit:
                break

            log(f"Cascade: trying variant '{variant}'")
            if isinstance(_multi_source, MultiSource):
                _multi_source.reset_diagnostics()

            try:
                variant_papers = await _multi_source.search_works(variant, **search_kwargs)
                new_papers = _dedup_papers(variant_papers, seen_dois)
                if new_papers:
                    papers.extend(new_papers)
                    strategies_used.append("variant")
                    log(f"Cascade variant added {len(new_papers)} new papers")
            except Exception as e:
                log(f"Cascade variant failed: {e}")

            if isinstance(_multi_source, MultiSource):
                diag = _multi_source.consume_diagnostics()
                if diag:
                    all_diag_succeeded.update(diag.get("succeeded", []))
                    all_diag_failed.update(diag.get("failed", []))

    # --- Strategy 3: Simplified query (keywords only) ---
    if len(papers) < 3:
        elapsed = time.monotonic() - start_time
        simplified = _simplify_query(query)
        if simplified and elapsed < CASCADE_TIMEOUT and simplified.lower() != query.strip().lower():
            log(f"Cascade: trying simplified '{simplified}'")
            if isinstance(_multi_source, MultiSource):
                _multi_source.reset_diagnostics()

            try:
                simp_papers = await _multi_source.search_works(simplified, **search_kwargs)
                new_papers = _dedup_papers(simp_papers, seen_dois)
                if new_papers:
                    papers.extend(new_papers)
                    strategies_used.append("simplified")
                    log(f"Cascade simplified added {len(new_papers)} new papers")
            except Exception as e:
                log(f"Cascade simplified failed: {e}")

            if isinstance(_multi_source, MultiSource):
                diag = _multi_source.consume_diagnostics()
                if diag:
                    all_diag_succeeded.update(diag.get("succeeded", []))
                    all_diag_failed.update(diag.get("failed", []))

    # --- Strategy 4: Individual source fallback (S2 directly) ---
    if len(papers) < 3:
        elapsed = time.monotonic() - start_time
        if elapsed < CASCADE_TIMEOUT:
            log("Cascade: trying S2 direct search")
            try:
                s2_results = await _s2_source.search_works(query, limit=limit)
                new_papers = _dedup_papers(s2_results, seen_dois)
                if new_papers:
                    papers.extend(new_papers)
                    strategies_used.append("s2_direct")
                    log(f"Cascade S2 direct added {len(new_papers)} new papers")
            except Exception as e:
                log(f"Cascade S2 direct failed: {e}")

    # Trim to limit
    papers = papers[:limit]
    elapsed = time.monotonic() - start_time

    # --- Format output ---
    text = format_papers_table(papers, title=f"Scholarly Search: {query}")

    # Source diagnostics
    if isinstance(_multi_source, MultiSource):
        source_parts = []
        if all_diag_succeeded:
            source_parts.append(f"Sources: {', '.join(sorted(all_diag_succeeded))}")
        if all_diag_failed:
            source_parts.append(f"Failed: {', '.join(sorted(all_diag_failed))}")
        source_parts.append(f"{len(papers)} results after dedup")
        text += f"\n\n*{' | '.join(source_parts)}*"
    else:
        text += f"\n\n*Source: OpenAlex | {len(papers)} results*"

    # Cascade notes
    if len(strategies_used) > 1:
        text += f"\n*Cascade: {len(strategies_used)} strategies used ({', '.join(strategies_used)}) in {elapsed:.1f}s*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_verify_dois(args: dict) -> list[TextContent]:
    dois = args["dois"]
    if len(dois) > 50:
        return [TextContent(type="text", text="**Error:** Maximum 50 DOIs per request.")]

    results = await _multi_source.batch_verify_dois(dois)
    text = format_verification_table(results)

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


async def _handle_scholarly_citations(args: dict) -> list[TextContent]:
    paper_id = args["paper_id"]
    limit = min(args.get("limit", 50), 1000)

    papers = await _s2_source.get_paper_citations(paper_id, limit=limit)
    text = format_papers_table(papers, title=f"Papers citing: {paper_id}")
    text += f"\n\n*{len(papers)} citing papers (via Semantic Scholar Graph API)*"
    return [TextContent(type="text", text=text)]


async def _handle_scholarly_references(args: dict) -> list[TextContent]:
    paper_id = args["paper_id"]
    limit = min(args.get("limit", 50), 1000)

    papers = await _s2_source.get_paper_references(paper_id, limit=limit)
    text = format_papers_table(papers, title=f"References of: {paper_id}")
    text += f"\n\n*{len(papers)} references (via Semantic Scholar Graph API)*"
    return [TextContent(type="text", text=text)]


async def _handle_scholarly_paper_detail(args: dict) -> list[TextContent]:
    paper_id = args["paper_id"]

    paper = await _s2_source.get_paper_detail(paper_id)
    if not paper:
        return [TextContent(type="text", text=f"Paper not found: {paper_id}")]

    # Generate standardised BibTeX key
    bib_key = generate_bibtex_key(paper.authors, paper.publication_year, paper.title)

    lines = [f"## {paper.title}\n"]
    lines.append(f"**Suggested BibTeX key:** `{bib_key}`")
    lines.append(f"**Authors:** {', '.join(paper.authors)}")
    lines.append(f"**Year:** {paper.publication_year}")
    lines.append(f"**Citations:** {paper.cited_by_count:,}")
    if paper.source_name:
        lines.append(f"**Venue:** {paper.source_name}")
    if paper.doi:
        lines.append(f"**DOI:** {paper.doi}")
    if paper.open_access_url:
        lines.append(f"**Open Access PDF:** {paper.open_access_url}")
    if paper.keywords:
        lines.append(f"**Fields:** {', '.join(paper.keywords)}")

    # ORCID enrichment: look up author ORCIDs when client available
    if _orcid_client and paper.authors:
        orcid_lines = []
        for author_name in paper.authors[:10]:  # cap at 10 to avoid rate-limit issues
            try:
                results = await asyncio.get_event_loop().run_in_executor(
                    None, lambda name=author_name: _orcid_client.search(name=name, limit=1)
                )
                if results:
                    orcid_lines.append(f"  - {author_name}: `{results[0].orcid_id}`")
            except Exception:
                pass  # best-effort — skip on any error
        if orcid_lines:
            lines.append("\n**Author ORCIDs:**")
            lines.extend(orcid_lines)

    if paper.tldr:
        lines.append(f"\n**TLDR:** {paper.tldr}")
    if paper.abstract:
        lines.append(f"\n**Abstract:** {paper.abstract}")
    if paper.bibtex:
        lines.append(f"\n**BibTeX:**\n```bibtex\n{paper.bibtex}\n```")

    lines.append(f"\n*Source: Semantic Scholar ({paper.source_id})*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_scholarly_author_papers(args: dict) -> list[TextContent]:
    author_name = args["author_name"]
    limit = min(args.get("limit", 50), 100)

    authors = await _s2_source.search_author(author_name, limit=5)
    if not authors:
        return [TextContent(type="text", text=f"Author not found: {author_name}")]

    author = authors[0]
    author_id = author.get("authorId", "")
    display_name = author.get("name", author_name)

    papers = await _s2_source.get_author_papers(author_id, limit=limit)
    text = format_papers_table(papers, title=f"Papers by {display_name}")

    if len(authors) > 1:
        text += "\n\n**Other matching authors:**\n"
        for a in authors[1:5]:
            text += f"- {a.get('name', '?')} (S2 ID: {a.get('authorId', '?')})\n"

    text += f"\n*{len(papers)} papers (via Semantic Scholar Graph API)*"
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


# ---------- Tool definitions + registration ----------

_TOOLS = [
    (
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
                    "query": {"type": "string", "description": "Search query (topic, keywords, title fragment)"},
                    "year_from": {"type": "integer", "description": "Start year filter (inclusive)"},
                    "year_to": {"type": "integer", "description": "End year filter (inclusive)"},
                    "sort_by": {"type": "string", "description": "Sort: 'relevance' (default), 'cited_by_count', 'publication_year'"},
                    "limit": {"type": "integer", "description": "Max results (default 25, max 50)"},
                },
                "required": ["query"],
            },
        ),
        _handle_scholarly_search,
    ),
    (
        Tool(
            name="scholarly_verify_dois",
            description=(
                "Batch-verify DOIs across all enabled sources. For each DOI, checks if it exists "
                "in Crossref (authoritative), OpenAlex, Semantic Scholar, Scopus, and/or WoS. "
                "Returns verification status: VERIFIED (2+ sources), SINGLE_SOURCE (1 source), "
                "or NOT_FOUND. The killer tool for /literature Phase 4."
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
        _handle_scholarly_verify_dois,
    ),
    (
        Tool(
            name="scholarly_similar_works",
            description="Find papers similar to a given text (title or abstract) across all enabled sources. Results are deduplicated by DOI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to find similar papers for (title, abstract, or topic description)"},
                    "limit": {"type": "integer", "description": "Max results (default 20, max 50)"},
                },
                "required": ["text"],
            },
        ),
        _handle_scholarly_similar_works,
    ),
    (
        Tool(
            name="scholarly_source_status",
            description="Show which scholarly data sources are configured and active. Reports OpenAlex (always), Scopus (if SCOPUS_API_KEY set), WoS (if WOS_API_KEY set).",
            inputSchema={"type": "object", "properties": {}},
        ),
        _handle_scholarly_source_status,
    ),
    (
        Tool(
            name="scholarly_citations",
            description=(
                "Get papers that CITE a given paper (forward citation tracking). "
                "Powered by Semantic Scholar Graph API. Accepts DOI, arXiv ID, or S2 paper ID. "
                "Use for snowball searches, impact analysis, and finding follow-up work."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper identifier: DOI (with DOI: prefix, e.g. 'DOI:10.1234/example'), arXiv ID (ARXIV:2106.15928), or S2 paper ID"},
                    "limit": {"type": "integer", "description": "Max results (default 50, max 1000)"},
                },
                "required": ["paper_id"],
            },
        ),
        _handle_scholarly_citations,
    ),
    (
        Tool(
            name="scholarly_references",
            description=(
                "Get papers REFERENCED BY a given paper (backward citation / bibliography). "
                "Powered by Semantic Scholar Graph API. Accepts DOI, arXiv ID, or S2 paper ID. "
                "Use for snowball searches, finding foundational works, and tracing intellectual lineage."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper identifier: DOI (with DOI: prefix, e.g. 'DOI:10.1234/example'), arXiv ID (ARXIV:2106.15928), or S2 paper ID"},
                    "limit": {"type": "integer", "description": "Max results (default 50, max 1000)"},
                },
                "required": ["paper_id"],
            },
        ),
        _handle_scholarly_references,
    ),
    (
        Tool(
            name="scholarly_paper_detail",
            description=(
                "Get full metadata for a single paper including TLDR (AI summary), "
                "BibTeX citation, open access PDF link, abstract, and citation count. "
                "Powered by Semantic Scholar. Accepts DOI, arXiv ID, or S2 paper ID."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper identifier: DOI (with DOI: prefix), arXiv ID (ARXIV:xxx), or S2 paper ID"},
                },
                "required": ["paper_id"],
            },
        ),
        _handle_scholarly_paper_detail,
    ),
    (
        Tool(
            name="scholarly_author_papers",
            description="Find all papers by an author. First searches for the author by name, then retrieves their publications. Powered by Semantic Scholar Graph API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_name": {"type": "string", "description": "Author name to search for"},
                    "limit": {"type": "integer", "description": "Max papers to return (default 50, max 100)"},
                },
                "required": ["author_name"],
            },
        ),
        _handle_scholarly_author_papers,
    ),
]

for tool, handler in _TOOLS:
    register(tool, handler)

# Conditional source-specific tools
if _scopus_key:
    register(
        Tool(
            name="scholarly_search_scopus",
            description="Search Scopus directly using Scopus query syntax (TITLE-ABS-KEY). Useful for ASJC subject codes and Scopus-specific features.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for Scopus (TITLE-ABS-KEY syntax)"},
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        ),
        _handle_scholarly_search_scopus,
    )

if _wos_key:
    register(
        Tool(
            name="scholarly_search_wos",
            description="Search Web of Science directly using WoS query syntax (TS=). Useful for WoS-specific features and citation tracking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for WoS (TS= syntax)"},
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        ),
        _handle_scholarly_search_wos,
    )
