#!/usr/bin/env python3
"""
Biblio MCP Server

Multi-source scholarly search: OpenAlex + Semantic Scholar + Crossref (always) + Scopus + Web of Science (when API keys provided).
Exposes source-specific openalex_*/crossref_* tools and cross-source scholarly_* tools.
Imports the shared clients from biblio-sources package — single source of truth.
"""

import asyncio
import os
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from biblio_sources import (
    AltmetricClient,
    CoreSource,
    CrossrefSource,
    DblpSource,
    OpenCitationsClient,
    OpenReviewClient,
    UnpaywallClient,
    ZenodoClient,
    OrcidClient,
    OpenAlexClient,
    OpenAlexSource,
    MultiSource,
    SemanticScholarSource,
    ScopusSource,
    WosSource,
)

# OpenAlex-specific helpers (raw dict API)
SCRIPTS_DIR = str(Path(__file__).parent.parent.parent / ".scripts" / "openalex")
sys.path.insert(0, SCRIPTS_DIR)

from query_helpers import (  # noqa: E402
    find_author_works,
    analyze_research_output,
    get_publication_trends,
)

from formatters import (  # noqa: E402
    format_works_table,
    format_author_profile,
    format_trends,
    format_work_detail,
)

from scholarly_formatters import (  # noqa: E402
    format_papers_table,
    format_verification_table,
    format_source_status,
)


def log(msg):
    print(f"[bibliography-mcp] {msg}", file=sys.stderr, flush=True)


# Shared client instance (polite pool)
client = OpenAlexClient(email="user@example.com")

# ---------- Multi-source initialization ----------

_all_sources = []
_source_info = []

# OpenAlex — always available
_openalex_source = OpenAlexSource(client)
_all_sources.append(_openalex_source)
_source_info.append({"name": "OpenAlex", "key": "openalex", "active": True})
log("OpenAlex source: active")

# Semantic Scholar — always available, optional API key for higher rate limits
_s2_key = os.environ.get("S2_API_KEY")
_s2_source = SemanticScholarSource(api_key=_s2_key)
_all_sources.append(_s2_source)
_source_info.append({"name": "Semantic Scholar", "key": "s2", "active": True})
log(f"Semantic Scholar source: active{' (API key)' if _s2_key else ' (no key, 1 req/sec)'}")

# Crossref — always available (no API key, polite pool via mailto)
_crossref_source = CrossrefSource(mailto="user@example.com")
_all_sources.append(_crossref_source)
_source_info.append({"name": "Crossref", "key": "crossref", "active": True})
log("Crossref source: active (authoritative DOI registry)")

# Scopus — optional, requires SCOPUS_API_KEY
_scopus_key = os.environ.get("SCOPUS_API_KEY")
if _scopus_key:
    _scopus_inst_token = os.environ.get("SCOPUS_INST_TOKEN", "")
    _scopus_source = ScopusSource(_scopus_key, inst_token=_scopus_inst_token)
    _all_sources.append(_scopus_source)
    _source_info.append({"name": "Scopus", "key": "scopus", "active": True})
    log(f"Scopus source: active{' (InstToken)' if _scopus_inst_token else ''}")
else:
    _source_info.append({"name": "Scopus", "key": "scopus", "active": False})
    log("Scopus source: no API key")

# Web of Science — optional, requires WOS_API_KEY
_wos_key = os.environ.get("WOS_API_KEY")
_wos_tier = os.environ.get("WOS_API_TIER", "starter").lower()
if _wos_key:
    _wos_source = WosSource(_wos_key, tier=_wos_tier)
    _all_sources.append(_wos_source)
    _source_info.append({"name": f"Web of Science ({_wos_tier})", "key": "wos", "active": True})
    log(f"WoS source: active (tier={_wos_tier})")
else:
    _source_info.append({"name": "Web of Science", "key": "wos", "active": False})
    log("WoS source: no API key")

# Composite source for cross-source queries
_multi_source = MultiSource(_all_sources) if len(_all_sources) > 1 else _openalex_source
log(f"Multi-source: {len(_all_sources)} source(s) active")

# CORE — open access full text, optional API key
_core_key = os.environ.get("CORE_API_KEY", "")
if _core_key:
    _core_source = CoreSource(api_key=_core_key)
    _all_sources.append(_core_source)
    _source_info.append({"name": "CORE", "key": "core", "active": True})
    log("CORE source: active (431M+ records, full-text access)")
else:
    _core_source = None
    _source_info.append({"name": "CORE", "key": "core", "active": False})
    log("CORE source: no API key (set CORE_API_KEY)")

# ORCID — researcher profiles, always available if credentials set
_orcid_client_id = os.environ.get("ORCID_CLIENT_ID", "")
_orcid_client_secret = os.environ.get("ORCID_CLIENT_SECRET", "")
_orcid_client = None
if _orcid_client_id and _orcid_client_secret:
    _orcid_client = OrcidClient(
        client_id=_orcid_client_id,
        client_secret=_orcid_client_secret,
    )
    log("ORCID client: active")
else:
    log("ORCID client: no credentials (set ORCID_CLIENT_ID + ORCID_CLIENT_SECRET)")

# Altmetric Explorer — research attention metrics, optional
_altmetric_key = os.environ.get("ALTMETRIC_API_KEY", "")
_altmetric_secret = os.environ.get("ALTMETRIC_API_PASSWORD", "")
_altmetric_client = None
if _altmetric_key and _altmetric_secret:
    _altmetric_client = AltmetricClient(api_key=_altmetric_key, api_secret=_altmetric_secret)
    log("Altmetric Explorer client: active")
else:
    log("Altmetric Explorer client: no credentials (set ALTMETRIC_API_KEY + ALTMETRIC_API_PASSWORD)")

# Zenodo — research data repository, always available (no auth)
_zenodo_client = ZenodoClient()
log("Zenodo client: active (no auth required)")

# Unpaywall — OA PDF resolver, always available (no auth, just email)
_unpaywall_client = UnpaywallClient(email="user@example.com")
log("Unpaywall client: active (no auth required)")

# OpenCitations — open citation graph, always available (no auth)
_opencitations_client = OpenCitationsClient()
log("OpenCitations client: active (no auth required)")

# DBLP — CS publications, always available (no auth)
_dblp_source = DblpSource()
log("DBLP source: active (no auth required)")

# OpenReview — conference submissions and reviews, always available (no auth)
_openreview_client = OpenReviewClient()
log("OpenReview client: active (no auth required)")

server = Server("bibliography")
log("Server initialized")


# ---------- Tool definitions ----------

TOOLS = [
    Tool(
        name="openalex_search_works",
        description=(
            "Search OpenAlex for scholarly papers by topic. Supports filters for "
            "year range, minimum citations, open access, and sort order. "
            "Returns a markdown table of results."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (topic, keywords, title fragment)",
                },
                "year": {
                    "type": "string",
                    "description": "Year filter: e.g. '2023', '>2020', '2020-2024'",
                },
                "min_citations": {
                    "type": "integer",
                    "description": "Minimum citation count",
                },
                "open_access": {
                    "type": "boolean",
                    "description": "Only return open access papers",
                },
                "sort": {
                    "type": "string",
                    "description": "Sort order: 'cited_by_count:desc' (default), 'publication_date:desc', 'relevance_score:desc'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="openalex_author_works",
        description=(
            "Find publications by a specific author. Searches by name, "
            "resolves to OpenAlex author ID, returns their works."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Author name to search for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 50, max 100)",
                },
            },
            "required": ["author_name"],
        },
    ),
    Tool(
        name="openalex_author_profile",
        description=(
            "Analyze an author's research output: total works, open access %, "
            "publications by year, and top topics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Author name to analyze",
                },
                "years": {
                    "type": "string",
                    "description": "Year filter (default: '>2020')",
                },
            },
            "required": ["author_name"],
        },
    ),
    Tool(
        name="openalex_institution_output",
        description=(
            "Analyze an institution's research output: total works, open access %, "
            "publications by year, and top topics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "institution_name": {
                    "type": "string",
                    "description": "Institution name to analyze",
                },
                "years": {
                    "type": "string",
                    "description": "Year filter (default: '>2020')",
                },
            },
            "required": ["institution_name"],
        },
    ),
    Tool(
        name="openalex_trends",
        description=(
            "Get publication count trends over time for a search term. "
            "Returns yearly publication counts."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to track trends for",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="openalex_lookup_doi",
        description=(
            "Look up a work by DOI. Returns full metadata including title, "
            "authors, abstract, citations, and open access status."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI (with or without https://doi.org/ prefix)",
                },
            },
            "required": ["doi"],
        },
    ),
    Tool(
        name="openalex_citing_works",
        description=(
            "Find papers that cite a given work (forward citation tracking). "
            "Provide a DOI and get back the citing papers."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI of the work to find citations for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["doi"],
        },
    ),
    Tool(
        name="crossref_lookup_doi",
        description=(
            "Look up a DOI in Crossref, the authoritative DOI registry. Returns "
            "verified metadata: title, authors, journal, date, abstract, citation count. "
            "Use this to verify a DOI exists and get canonical metadata. More authoritative "
            "than OpenAlex for DOI verification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI to look up (with or without https://doi.org/ prefix)",
                },
            },
            "required": ["doi"],
        },
    ),
]


# ---------- Scholarly tool definitions (cross-source) ----------

SCHOLARLY_TOOLS = [
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
                "query": {
                    "type": "string",
                    "description": "Search query (topic, keywords, title fragment)",
                },
                "year_from": {
                    "type": "integer",
                    "description": "Start year filter (inclusive)",
                },
                "year_to": {
                    "type": "integer",
                    "description": "End year filter (inclusive)",
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort: 'relevance' (default), 'cited_by_count', 'publication_year'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 50)",
                },
            },
            "required": ["query"],
        },
    ),
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
    Tool(
        name="scholarly_similar_works",
        description=(
            "Find papers similar to a given text (title or abstract) across all enabled sources. "
            "Results are deduplicated by DOI."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to find similar papers for (title, abstract, or topic description)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 20, max 50)",
                },
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="scholarly_source_status",
        description=(
            "Show which scholarly data sources are configured and active. "
            "Reports OpenAlex (always), Scopus (if SCOPUS_API_KEY set), "
            "WoS (if WOS_API_KEY set)."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
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
                "paper_id": {
                    "type": "string",
                    "description": "Paper identifier: DOI (with DOI: prefix, e.g. 'DOI:10.1234/example'), arXiv ID (ARXIV:2106.15928), or S2 paper ID",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 50, max 1000)",
                },
            },
            "required": ["paper_id"],
        },
    ),
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
                "paper_id": {
                    "type": "string",
                    "description": "Paper identifier: DOI (with DOI: prefix, e.g. 'DOI:10.1234/example'), arXiv ID (ARXIV:2106.15928), or S2 paper ID",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 50, max 1000)",
                },
            },
            "required": ["paper_id"],
        },
    ),
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
                "paper_id": {
                    "type": "string",
                    "description": "Paper identifier: DOI (with DOI: prefix), arXiv ID (ARXIV:xxx), or S2 paper ID",
                },
            },
            "required": ["paper_id"],
        },
    ),
    Tool(
        name="scholarly_author_papers",
        description=(
            "Find all papers by an author. First searches for the author by name, "
            "then retrieves their publications. Powered by Semantic Scholar Graph API."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Author name to search for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max papers to return (default 50, max 100)",
                },
            },
            "required": ["author_name"],
        },
    ),
]

# Conditional source-specific tools
if _scopus_key:
    SCHOLARLY_TOOLS.append(
        Tool(
            name="scholarly_search_scopus",
            description=(
                "Search Scopus directly using Scopus query syntax (TITLE-ABS-KEY). "
                "Useful for ASJC subject codes and Scopus-specific features."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Scopus (TITLE-ABS-KEY syntax)",
                    },
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        )
    )

if _wos_key:
    SCHOLARLY_TOOLS.append(
        Tool(
            name="scholarly_search_wos",
            description=(
                "Search Web of Science directly using WoS query syntax (TS=). "
                "Useful for WoS-specific features and citation tracking."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for WoS (TS= syntax)",
                    },
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {"type": "integer", "description": "Max results (default 25)"},
                },
                "required": ["query"],
            },
        )
    )


# ---------- ORCID tool definitions (researcher-centric) ----------

ORCID_TOOLS = []
if _orcid_client:
    ORCID_TOOLS = [
        Tool(
            name="orcid_search_researchers",
            description=(
                "Search the ORCID registry for researchers by name, affiliation, or keyword. "
                "Returns ORCID iDs with names and institutional affiliations. "
                "Query syntax: family-name:Smith, given-names:John, affiliation-org-name:Warwick, keyword:MCDM. "
                "Combine with AND/OR. Use this to find a researcher's ORCID iD for disambiguation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "ORCID search query (Lucene syntax: family-name:X AND affiliation-org-name:Y)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 10, max 100)",
                    },
                },
                "required": ["query"],
            },
        ),
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
                    "orcid_id": {
                        "type": "string",
                        "description": "ORCID identifier (e.g. 0000-0001-2345-6789 or https://orcid.org/0000-0001-2345-6789)",
                    },
                    "include_works": {
                        "type": "boolean",
                        "description": "Include publication list (default true)",
                    },
                    "max_works": {
                        "type": "integer",
                        "description": "Max works to return (default 50)",
                    },
                },
                "required": ["orcid_id"],
            },
        ),
    ]


# ---------- CORE tool definitions ----------

CORE_TOOLS = []
if _core_source:
    CORE_TOOLS = [
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
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, title fragment)",
                    },
                    "year_from": {"type": "integer", "description": "Start year"},
                    "year_to": {"type": "integer", "description": "End year"},
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 25, max 100)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="core_get_fulltext",
            description=(
                "Get the full text of a paper by CORE ID. Returns the complete paper text. "
                "Use core_search_fulltext first to find the CORE ID (source_id field, format: core:12345)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "core_id": {
                        "type": "integer",
                        "description": "CORE work ID (numeric, from source_id field)",
                    },
                },
                "required": ["core_id"],
            },
        ),
    ]

# ---------- Altmetric tool definitions ----------

ALTMETRIC_TOOLS = []
if _altmetric_client:
    ALTMETRIC_TOOLS = [
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
                    "query": {
                        "type": "string",
                        "description": "Search query (topic, keywords)",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time filter: 'all' (default), '1d', '1w', '1m', '3m', '6m', '1y'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 25, max 100)",
                    },
                },
                "required": ["query"],
            },
        ),
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
                    "query": {
                        "type": "string",
                        "description": "Topic to analyze",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Time filter: 'all' (default), '1d', '1w', '1m', '3m', '6m', '1y'",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


# ---------- OpenReview tool definitions (always available) ----------

OPENREVIEW_TOOLS = [
    Tool(
        name="openreview_venue_submissions",
        description=(
            "Get submissions for an AI/ML conference from OpenReview. Returns titles, abstracts, "
            "authors, keywords, and primary areas. Supports: NeurIPS, ICLR, ICML, ACL, EMNLP, "
            "AISTATS, UAI, CoRL, AAAI. Use shorthand like 'neurips/2024' or full ID."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "venue_id": {
                    "type": "string",
                    "description": "Venue ID: shorthand (neurips/2024, iclr/2025) or full (NeurIPS.cc/2024/Conference)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 1000)",
                },
            },
            "required": ["venue_id"],
        },
    ),
    Tool(
        name="openreview_paper_reviews",
        description=(
            "Get a paper and all its reviews from OpenReview. Returns the submission plus "
            "reviewer ratings, soundness, strengths, weaknesses, and questions. "
            "Provide the forum ID (from openreview_venue_submissions results)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "forum_id": {
                    "type": "string",
                    "description": "OpenReview forum ID for the paper",
                },
            },
            "required": ["forum_id"],
        },
    ),
    Tool(
        name="openreview_search",
        description=(
            "Search OpenReview for papers by text query. Optionally filter by venue. "
            "Returns submissions matching the query. Use for finding specific papers "
            "or exploring what's been submitted to a conference on a topic."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, title fragment)",
                },
                "venue_id": {
                    "type": "string",
                    "description": "Optional venue filter (e.g. neurips/2024)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25)",
                },
            },
            "required": ["query"],
        },
    ),
]


# ---------- DBLP tool definitions (always available) ----------

DBLP_TOOLS = [
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
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, title, author name)",
                },
                "year_from": {"type": "integer", "description": "Start year filter"},
                "year_to": {"type": "integer", "description": "End year filter"},
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 1000)",
                },
            },
            "required": ["query"],
        },
    ),
]


# ---------- OpenCitations tool definitions (always available) ----------

OPENCITATIONS_TOOLS = [
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
                "doi": {
                    "type": "string",
                    "description": "DOI to find citations for (with or without prefix)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default: all citations)",
                },
            },
            "required": ["doi"],
        },
    ),
    Tool(
        name="opencitations_references",
        description=(
            "Get papers referenced by a given DOI (backward citations / bibliography). "
            "Returns cited DOIs. Use for tracing intellectual lineage."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "doi": {
                    "type": "string",
                    "description": "DOI to find references for",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default: all references)",
                },
            },
            "required": ["doi"],
        },
    ),
]


# ---------- Unpaywall tool definition (always available) ----------

UNPAYWALL_TOOLS = [
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
                "doi": {
                    "type": "string",
                    "description": "DOI to find OA PDF for (with or without prefix)",
                },
            },
            "required": ["doi"],
        },
    ),
]


# ---------- Zenodo tool definitions (always available) ----------

ZENODO_TOOLS = [
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
                "query": {
                    "type": "string",
                    "description": "Search query (keywords, topic, author name)",
                },
                "resource_type": {
                    "type": "string",
                    "description": "Filter: 'dataset', 'software', 'publication', 'poster', 'presentation'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 25, max 100)",
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="zenodo_get_record",
        description=(
            "Get a specific Zenodo record by ID. Returns full metadata including "
            "files (with download URLs), description, license, and DOI."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "record_id": {
                    "type": "integer",
                    "description": "Zenodo record ID (numeric)",
                },
            },
            "required": ["record_id"],
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS + SCHOLARLY_TOOLS + ORCID_TOOLS + CORE_TOOLS + ALTMETRIC_TOOLS + OPENREVIEW_TOOLS + DBLP_TOOLS + OPENCITATIONS_TOOLS + UNPAYWALL_TOOLS + ZENODO_TOOLS


# ---------- Tool handlers ----------


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log(f"call_tool: {name} {arguments}")

    try:
        if name == "openalex_search_works":
            return await _handle_search_works(arguments)
        elif name == "openalex_author_works":
            return await _handle_author_works(arguments)
        elif name == "openalex_author_profile":
            return await _handle_author_profile(arguments)
        elif name == "openalex_institution_output":
            return await _handle_institution_output(arguments)
        elif name == "openalex_trends":
            return await _handle_trends(arguments)
        elif name == "openalex_lookup_doi":
            return await _handle_lookup_doi(arguments)
        elif name == "openalex_citing_works":
            return await _handle_citing_works(arguments)
        elif name == "crossref_lookup_doi":
            return await _handle_crossref_lookup_doi(arguments)
        # Scholarly (cross-source) tools
        elif name == "scholarly_search":
            return await _handle_scholarly_search(arguments)
        elif name == "scholarly_verify_dois":
            return await _handle_scholarly_verify_dois(arguments)
        elif name == "scholarly_similar_works":
            return await _handle_scholarly_similar_works(arguments)
        elif name == "scholarly_source_status":
            return await _handle_scholarly_source_status(arguments)
        elif name == "scholarly_citations":
            return await _handle_scholarly_citations(arguments)
        elif name == "scholarly_references":
            return await _handle_scholarly_references(arguments)
        elif name == "scholarly_paper_detail":
            return await _handle_scholarly_paper_detail(arguments)
        elif name == "scholarly_author_papers":
            return await _handle_scholarly_author_papers(arguments)
        elif name == "scholarly_search_scopus":
            return await _handle_scholarly_search_scopus(arguments)
        elif name == "scholarly_search_wos":
            return await _handle_scholarly_search_wos(arguments)
        # CORE tools
        elif name == "core_search_fulltext":
            return await _handle_core_search(arguments)
        elif name == "core_get_fulltext":
            return await _handle_core_get_fulltext(arguments)
        # Altmetric tools
        elif name == "altmetric_search":
            return await _handle_altmetric_search(arguments)
        elif name == "altmetric_attention_summary":
            return await _handle_altmetric_attention_summary(arguments)
        # Zenodo tools
        elif name == "zenodo_search":
            return await _handle_zenodo_search(arguments)
        elif name == "zenodo_get_record":
            return await _handle_zenodo_get_record(arguments)
        # Unpaywall tools
        elif name == "unpaywall_find_pdf":
            return await _handle_unpaywall(arguments)
        # OpenCitations tools
        elif name == "opencitations_citations":
            return await _handle_opencitations_citations(arguments)
        elif name == "opencitations_references":
            return await _handle_opencitations_references(arguments)
        # DBLP tools
        elif name == "dblp_search":
            return await _handle_dblp_search(arguments)
        # OpenReview tools
        elif name == "openreview_venue_submissions":
            return await _handle_openreview_venue(arguments)
        elif name == "openreview_paper_reviews":
            return await _handle_openreview_reviews(arguments)
        elif name == "openreview_search":
            return await _handle_openreview_search(arguments)
        # ORCID tools
        elif name == "orcid_search_researchers":
            return await _handle_orcid_search(arguments)
        elif name == "orcid_get_researcher":
            return await _handle_orcid_get_researcher(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"**Error:** {e}")]


async def _handle_search_works(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    sort = args.get("sort", "cited_by_count:desc")

    filter_params: dict[str, str] = {}
    if args.get("year"):
        filter_params["publication_year"] = args["year"]
    if args.get("min_citations"):
        filter_params["cited_by_count"] = f">{args['min_citations']}"
    if args.get("open_access"):
        filter_params["is_oa"] = "true"

    def _search():
        return client.search_works(
            search=query,
            filter_params=filter_params if filter_params else None,
            per_page=limit,
            sort=sort,
        )

    response = await asyncio.to_thread(_search)
    works = response.get("results", [])
    total = response.get("meta", {}).get("count", 0)

    text = format_works_table(works, title=f"Search: {query}")
    text += f"\n\n*{total:,} total results in OpenAlex (showing top {len(works)})*"
    return [TextContent(type="text", text=text)]


async def _handle_author_works(args: dict) -> list[TextContent]:
    author_name = args["author_name"]
    limit = min(args.get("limit", 50), 100)

    works = await asyncio.to_thread(find_author_works, author_name, client, limit)
    text = format_works_table(works, title=f"Works by {author_name}")
    return [TextContent(type="text", text=text)]


async def _handle_author_profile(args: dict) -> list[TextContent]:
    author_name = args["author_name"]
    years = args.get("years", ">2020")

    analysis = await asyncio.to_thread(
        analyze_research_output, "author", author_name, client, years
    )
    text = format_author_profile(analysis)
    return [TextContent(type="text", text=text)]


async def _handle_institution_output(args: dict) -> list[TextContent]:
    institution_name = args["institution_name"]
    years = args.get("years", ">2020")

    analysis = await asyncio.to_thread(
        analyze_research_output, "institution", institution_name, client, years
    )
    text = format_author_profile(analysis)
    return [TextContent(type="text", text=text)]


async def _handle_trends(args: dict) -> list[TextContent]:
    query = args["query"]

    trends = await asyncio.to_thread(get_publication_trends, query, None, client)
    text = format_trends(trends, search_term=query)
    return [TextContent(type="text", text=text)]


async def _handle_lookup_doi(args: dict) -> list[TextContent]:
    doi = args["doi"]
    if not doi.startswith("https://doi.org/"):
        doi = f"https://doi.org/{doi}"

    work = await asyncio.to_thread(client.get_entity, "works", doi)
    text = format_work_detail(work)
    return [TextContent(type="text", text=text)]


async def _handle_citing_works(args: dict) -> list[TextContent]:
    doi = args["doi"]
    limit = min(args.get("limit", 25), 50)

    if not doi.startswith("https://doi.org/"):
        doi = f"https://doi.org/{doi}"

    work = await asyncio.to_thread(client.get_entity, "works", doi)
    cited_by_url = work.get("cited_by_api_url")

    if not cited_by_url:
        return [TextContent(type="text", text="No citation data available for this work.")]

    import requests

    def _fetch_citing():
        resp = requests.get(
            cited_by_url,
            params={"mailto": client.email, "per-page": limit},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    data = await asyncio.to_thread(_fetch_citing)
    citing_works = data.get("results", [])
    total = data.get("meta", {}).get("count", 0)

    title_text = (work.get("title") or "this work")[:60]
    text = format_works_table(citing_works, title=f"Papers citing: {title_text}")
    text += f"\n\n*{total:,} total citing works (showing {len(citing_works)})*"
    return [TextContent(type="text", text=text)]


async def _handle_crossref_lookup_doi(args: dict) -> list[TextContent]:
    doi = args["doi"]
    paper = await _crossref_source.verify_doi(doi)

    if not paper:
        return [TextContent(type="text", text=f"DOI not found in Crossref: {doi}")]

    lines = [f"## {paper.title}\n"]
    lines.append(f"**Authors:** {', '.join(paper.authors)}")
    lines.append(f"**Year:** {paper.publication_year}")
    lines.append(f"**Citations:** {paper.cited_by_count:,}")
    if paper.source_name:
        lines.append(f"**Journal:** {paper.source_name}")
    if paper.doi:
        lines.append(f"**DOI:** {paper.doi}")
    if paper.abstract:
        lines.append(f"\n**Abstract:** {paper.abstract}")

    lines.append(f"\n*Source: Crossref (authoritative DOI registry) | Verified: Yes*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Scholarly tool handlers ----------


async def _handle_scholarly_search(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 50)
    year_from = args.get("year_from")
    year_to = args.get("year_to")
    sort_by = args.get("sort_by", "relevance")

    if isinstance(_multi_source, MultiSource):
        _multi_source.reset_diagnostics()

    papers = await _multi_source.search_works(
        query, year_from=year_from, year_to=year_to, sort_by=sort_by, limit=limit,
    )
    text = format_papers_table(papers, title=f"Scholarly Search: {query}")

    if isinstance(_multi_source, MultiSource):
        diag = _multi_source.consume_diagnostics()
        if diag:
            text += f"\n\n*Sources queried: {', '.join(diag['succeeded'])}"
            if diag["failed"]:
                text += f" | Failed: {', '.join(diag['failed'])}"
            text += f" | {len(papers)} results after dedup*"
    else:
        text += f"\n\n*Source: OpenAlex | {len(papers)} results*"

    return [TextContent(type="text", text=text)]


async def _handle_scholarly_verify_dois(args: dict) -> list[TextContent]:
    dois = args["dois"]
    if len(dois) > 50:
        return [TextContent(type="text", text="**Error:** Maximum 50 DOIs per request.")]

    results = await _multi_source.batch_verify_dois(dois)
    text = format_verification_table(results)

    # Add source summary
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

    lines = [f"## {paper.title}\n"]
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

    # Step 1: search for author
    authors = await _s2_source.search_author(author_name, limit=5)
    if not authors:
        return [TextContent(type="text", text=f"Author not found: {author_name}")]

    # Pick the first match
    author = authors[0]
    author_id = author.get("authorId", "")
    display_name = author.get("name", author_name)

    # Step 2: get their papers
    papers = await _s2_source.get_author_papers(author_id, limit=limit)
    text = format_papers_table(papers, title=f"Papers by {display_name}")

    # Add author disambiguation info
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


# ---------- CORE tool handlers ----------


async def _handle_core_search(args: dict) -> list[TextContent]:
    if not _core_source:
        return [TextContent(type="text", text="**Error:** CORE not configured (set CORE_API_KEY)")]

    query = args["query"]
    limit = min(args.get("limit", 25), 100)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _core_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit
    )

    if not papers:
        return [TextContent(type="text", text=f"No CORE results for: {query}")]

    text = format_papers_table(papers, title=f"CORE Search: {query}")

    # Note which have full text available
    with_text = sum(1 for p in papers if p.open_access_url)
    text += f"\n\n*{len(papers)} results from CORE ({with_text} with full text available)*"
    text += "\n*Use `core_get_fulltext` with the CORE ID to retrieve full paper text.*"
    return [TextContent(type="text", text=text)]


async def _handle_core_get_fulltext(args: dict) -> list[TextContent]:
    if not _core_source:
        return [TextContent(type="text", text="**Error:** CORE not configured (set CORE_API_KEY)")]

    core_id = args["core_id"]
    full_text = await _core_source.get_full_text(core_id)

    if not full_text:
        return [TextContent(type="text", text=f"No full text available for CORE ID: {core_id}")]

    # Truncate if very long (context window safety)
    if len(full_text) > 50000:
        full_text = full_text[:50000] + f"\n\n... [truncated, {len(full_text)} chars total]"

    return [TextContent(type="text", text=f"## Full Text (CORE ID: {core_id})\n\n{full_text}")]


# ---------- Altmetric tool handlers ----------


async def _handle_altmetric_search(args: dict) -> list[TextContent]:
    if not _altmetric_client:
        return [TextContent(type="text", text="**Error:** Altmetric not configured (set ALTMETRIC_API_KEY + ALTMETRIC_API_PASSWORD)")]

    query = args["query"]
    timeframe = args.get("timeframe", "all")
    limit = min(args.get("limit", 25), 100)

    outputs = await _altmetric_client.search(query, timeframe=timeframe, limit=limit)

    if not outputs:
        return [TextContent(type="text", text=f"No Altmetric results for: {query}")]

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
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_altmetric_attention_summary(args: dict) -> list[TextContent]:
    if not _altmetric_client:
        return [TextContent(type="text", text="**Error:** Altmetric not configured")]

    query = args["query"]
    timeframe = args.get("timeframe", "all")

    data = await _altmetric_client.get_attention_summary(query, timeframe=timeframe)

    if not data:
        return [TextContent(type="text", text=f"No attention data for: {query}")]

    lines = [f"## Attention Summary: {query}\n"]
    lines.append(f"```json\n{__import__('json').dumps(data, indent=2)[:2000]}\n```")
    lines.append(f"\n*Source: Altmetric Explorer (timeframe: {timeframe})*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- Zenodo tool handlers ----------


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


# ---------- Unpaywall tool handlers ----------


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


# ---------- OpenCitations tool handlers ----------


async def _handle_opencitations_citations(args: dict) -> list[TextContent]:
    doi = args["doi"]
    limit = args.get("limit")

    citations = await _opencitations_client.get_citations(doi, limit=limit)

    if not citations:
        return [TextContent(type="text", text=f"No citations found in OpenCitations for: {doi}")]

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
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_opencitations_references(args: dict) -> list[TextContent]:
    doi = args["doi"]
    limit = args.get("limit")

    references = await _opencitations_client.get_references(doi, limit=limit)

    if not references:
        return [TextContent(type="text", text=f"No references found in OpenCitations for: {doi}")]

    lines = [f"## OpenCitations: References of {doi}\n"]
    lines.append("| # | Referenced DOI | Date |")
    lines.append("|---|--------------|------|")

    for i, r in enumerate(references, 1):
        cited_doi = r.cited
        date = r.creation or "—"
        lines.append(f"| {i} | [{cited_doi}](https://doi.org/{cited_doi}) | {date} |")

    lines.append(f"\n*{len(references)} references (Source: OpenCitations COCI)*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- DBLP tool handlers ----------


async def _handle_dblp_search(args: dict) -> list[TextContent]:
    query = args["query"]
    limit = min(args.get("limit", 25), 1000)
    year_from = args.get("year_from")
    year_to = args.get("year_to")

    papers = await _dblp_source.search_works(
        query, year_from=year_from, year_to=year_to, limit=limit
    )

    if not papers:
        return [TextContent(type="text", text=f"No DBLP results for: {query}")]

    text = format_papers_table(papers, title=f"DBLP: {query}")
    text += f"\n\n*{len(papers)} results from DBLP*"
    return [TextContent(type="text", text=text)]


# ---------- OpenReview tool handlers ----------


async def _handle_openreview_venue(args: dict) -> list[TextContent]:
    venue_id = args["venue_id"]
    limit = min(args.get("limit", 25), 1000)

    papers = await _openreview_client.get_venue_submissions(venue_id, limit=limit)

    if not papers:
        return [TextContent(type="text", text=f"No submissions found for venue: {venue_id}")]

    lines = [f"## OpenReview: {venue_id}\n"]
    lines.append("| # | Title | Authors | Keywords | Area | Forum ID |")
    lines.append("|---|-------|---------|----------|------|----------|")

    for i, p in enumerate(papers, 1):
        title = p.title[:60] + ("..." if len(p.title) > 60 else "")
        authors = ", ".join(p.authors[:3]) + ("..." if len(p.authors) > 3 else "")
        kw = ", ".join(p.keywords[:3]) if p.keywords else "—"
        area = p.primary_area or "—"
        if len(area) > 30:
            area = area[:30] + "..."
        lines.append(f"| {i} | [{title}](https://openreview.net/forum?id={p.forum_id}) | {authors} | {kw} | {area} | `{p.forum_id}` |")

    lines.append(f"\n*{len(papers)} submissions from OpenReview*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_openreview_reviews(args: dict) -> list[TextContent]:
    forum_id = args["forum_id"]

    paper = await _openreview_client.get_paper_with_reviews(forum_id)

    if not paper:
        return [TextContent(type="text", text=f"Paper not found: {forum_id}")]

    lines = [f"## {paper.title}\n"]
    lines.append(f"**Forum:** [openreview.net/forum?id={forum_id}](https://openreview.net/forum?id={forum_id})")
    if paper.authors:
        lines.append(f"**Authors:** {', '.join(paper.authors[:5])}")
    if paper.venue:
        lines.append(f"**Venue:** {paper.venue}")
    if paper.primary_area:
        lines.append(f"**Area:** {paper.primary_area}")
    if paper.keywords:
        lines.append(f"**Keywords:** {', '.join(paper.keywords)}")
    if paper.tldr:
        lines.append(f"**TLDR:** {paper.tldr}")
    if paper.abstract:
        lines.append(f"\n**Abstract:** {paper.abstract[:500]}{'...' if len(paper.abstract or '') > 500 else ''}")

    if paper.reviews:
        lines.append(f"\n### Reviews ({len(paper.reviews)})\n")
        for i, r in enumerate(paper.reviews, 1):
            lines.append(f"#### Reviewer {i}")
            if r.rating:
                lines.append(f"- **Rating:** {r.rating}")
            if r.soundness:
                lines.append(f"- **Soundness:** {r.soundness}")
            if r.presentation:
                lines.append(f"- **Presentation:** {r.presentation}")
            if r.contribution:
                lines.append(f"- **Contribution:** {r.contribution}")
            if r.confidence:
                lines.append(f"- **Confidence:** {r.confidence}")
            if r.strengths:
                lines.append(f"- **Strengths:** {r.strengths}")
            if r.weaknesses:
                lines.append(f"- **Weaknesses:** {r.weaknesses}")
            lines.append("")
    else:
        lines.append("\n*No reviews available.*")

    lines.append(f"\n*Source: OpenReview API v2*")
    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_openreview_search(args: dict) -> list[TextContent]:
    query = args["query"]
    venue_id = args.get("venue_id")
    limit = min(args.get("limit", 25), 100)

    papers = await _openreview_client.search(query, venue_id=venue_id, limit=limit)

    if not papers:
        return [TextContent(type="text", text=f"No OpenReview results for: {query}")]

    lines = [f"## OpenReview Search: {query}\n"]
    if venue_id:
        lines[0] = f"## OpenReview Search: {query} (venue: {venue_id})\n"

    lines.append("| # | Title | Authors | Venue | Forum ID |")
    lines.append("|---|-------|---------|-------|----------|")

    for i, p in enumerate(papers, 1):
        title = p.title[:60] + ("..." if len(p.title) > 60 else "")
        authors = ", ".join(p.authors[:2]) + ("..." if len(p.authors) > 2 else "")
        venue = p.venue or p.venue_id or "—"
        if len(venue) > 30:
            venue = venue[:30] + "..."
        lines.append(f"| {i} | [{title}](https://openreview.net/forum?id={p.forum_id}) | {authors} | {venue} | `{p.forum_id}` |")

    lines.append(f"\n*{len(papers)} results from OpenReview*")
    return [TextContent(type="text", text="\n".join(lines))]


# ---------- ORCID tool handlers ----------


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


# ---------- Main ----------

async def main():
    log("Starting MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        log("stdio_server ready, running server...")
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )
    log("Server stopped")


if __name__ == "__main__":
    log("Main entry point")
    asyncio.run(main())
