"""
Biblio MCP Server — shared state

Server instance, client initialization, formatters, and helpers.
Imported by tool modules in tools/.
"""

import asyncio
import os
import re
import sys
import unicodedata
from pathlib import Path

from biblio_sources import (
    AltmetricClient,
    ArxivSource,
    CoreSource,
    CrossrefSource,
    DblpSource,
    ExaClient,
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
    print(f"[mcp-scholarly] {msg}", file=sys.stderr, flush=True)


# ---------- Client / source initialization ----------

# Shared client instance (polite pool)
client = OpenAlexClient(email="user@example.com")

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
_scopus_source = None
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
_wos_source = None
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
_core_source = None
if _core_key:
    _core_source = CoreSource(api_key=_core_key)
    _all_sources.append(_core_source)
    _source_info.append({"name": "CORE", "key": "core", "active": True})
    log("CORE source: active (431M+ records, full-text access)")
else:
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

# arXiv — preprints, always available (no auth)
_arxiv_source = ArxivSource()
log("arXiv source: active (no auth required)")

# Exa — semantic web search, optional API key
_exa_key = os.environ.get("EXA_API_KEY", "")
_exa_client = None
if _exa_key:
    _exa_client = ExaClient(api_key=_exa_key)
    log("Exa client: active (semantic search + research papers)")
else:
    log("Exa client: no API key (set EXA_API_KEY)")

# ---------- Utility: BibTeX key generation ----------

_KEY_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "of", "in", "on", "for", "to", "with", "by",
    "from", "at", "is", "are", "do", "does", "how", "what", "when", "where",
})


def generate_bibtex_key(authors: list[str], year: int | None, title: str | None) -> str:
    """Generate a BibTeX key following Google Scholar convention: surnameYearFirstword.

    Examples:
        ["Albert Einstein"], 1905, "On the Electrodynamics..." -> einstein1905electrodynamics
        ["María García-López"], 2023, "A Study..." -> garcialopez2023study
    """
    # Surname: last token of first author, ASCII-normalized, lowercase
    surname = ""
    if authors:
        name = authors[0].strip()
        # Handle "Last, First" format
        if "," in name:
            surname = name.split(",")[0].strip()
        else:
            surname = name.split()[-1] if name.split() else ""
    surname = unicodedata.normalize("NFKD", surname).encode("ascii", "ignore").decode("ascii")
    surname = re.sub(r"[^a-zA-Z]", "", surname).lower()
    if not surname:
        surname = "unknown"

    # Year
    year_str = str(year) if year else ""

    # First significant word of title
    first_word = ""
    if title:
        title_ascii = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
        words = re.findall(r"[a-zA-Z]+", title_ascii.lower())
        for w in words:
            if w not in _KEY_STOPWORDS and len(w) > 2:
                first_word = w
                break
        if not first_word and words:
            first_word = words[0]

    return f"{surname}{year_str}{first_word}"


log("Shared scholarly runtime initialized")
