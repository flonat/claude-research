"""Web of Science API adapter (Starter + Expanded tiers).

Uses httpx async client. Requires WOS_API_KEY env var.
Optional WOS_API_TIER env var: "starter" (default) or "expanded".

Expanded tier provides: abstracts, higher per-page limits (100 vs 50),
full author affiliations, funding data.

SYNC: Mirrored in Topic Finder (claude_topic_finder/services/wos.py).
Changes to query construction, pagination, or record parsing must be propagated.
Topic Finder adds get_topics/get_trend_data; this version adds
verify_doi/batch_verify_dois. Core search logic should stay identical.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone

import httpx

from sources.base import ScholarlySource
from sources.models import Paper

logger = logging.getLogger(__name__)

# Common English stopwords — kept small to avoid false removals of domain terms
_STOPWORDS = frozenset(
    "a an the and or but in on of to for is it that this with by from as at be "
    "are was were been have has had do does did not no nor so if then than can "
    "will would could should may might shall its we i you he she they our my "
    "your their about into through during before after above below between"
    .split()
)

_WORD_RE = re.compile(r"[a-zA-Z][\w-]*[a-zA-Z]|[a-zA-Z]{2,}")


def _extract_search_terms(text: str, *, max_terms: int = 12) -> str:
    """Extract key terms from a long text for use in WoS TS=() queries."""
    words = _WORD_RE.findall(text)
    terms: list[str] = []
    seen: set[str] = set()
    for w in words:
        lower = w.lower()
        if lower in _STOPWORDS or len(lower) < 3:
            continue
        if lower not in seen:
            seen.add(lower)
            terms.append(w)
        if len(terms) >= max_terms:
            break
    return " ".join(terms)

_BASE_URLS = {
    "starter": "https://api.clarivate.com/apis/wos-starter/v1",
    "expanded": "https://wos-api.clarivate.com/api/wos",
}


class WosSource(ScholarlySource):
    """Web of Science implementation supporting both Starter and Expanded API tiers.

    Starter: /documents endpoint, max 50/page, no abstracts.
    Expanded: root endpoint, max 100/page, abstracts + affiliations + funding.
    """

    def __init__(self, api_key: str, tier: str = "starter") -> None:
        self._api_key = api_key
        self._tier = tier
        base_url = _BASE_URLS.get(tier, _BASE_URLS["starter"])
        self._per_page_max = 100 if tier == "expanded" else 50
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-ApiKey": api_key},
            timeout=30.0,
        )

    @property
    def source_name(self) -> str:
        tier_label = " (Expanded)" if self._tier == "expanded" else ""
        return f"Web of Science{tier_label}"

    @property
    def source_key(self) -> str:
        return "wos"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def search_works(
        self,
        query: str,
        *,
        year_from: int | None = None,
        year_to: int | None = None,
        sort_by: str = "relevance",
        limit: int = 50,
    ) -> list[Paper]:
        current_year = datetime.now(timezone.utc).year
        wos_query = f"TS=({query})"
        if year_from:
            wos_query += f" AND PY=({year_from}-{year_to or current_year})"
        elif year_to:
            wos_query += f" AND PY=(1900-{year_to})"

        if self._tier == "expanded":
            return await self._search_expanded(wos_query, sort_by, limit)
        return await self._search_starter(wos_query, sort_by, limit)

    async def verify_doi(self, doi: str) -> Paper | None:
        clean_doi = doi
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi[len("https://doi.org/"):]

        wos_query = f"DO=({clean_doi})"

        if self._tier == "expanded":
            papers = await self._search_expanded(wos_query, "relevance", 1)
        else:
            papers = await self._search_starter(wos_query, "relevance", 1)

        if papers:
            papers[0].verified_by = ["wos"]
            return papers[0]
        return None

    async def batch_verify_dois(self, dois: list[str]) -> dict[str, Paper | None]:
        results: dict[str, Paper | None] = {d: None for d in dois}

        clean_dois = []
        for d in dois:
            clean = d
            if clean.startswith("https://doi.org/"):
                clean = clean[len("https://doi.org/"):]
            clean_dois.append(clean)

        # Process in chunks of 10 (WoS query length limits)
        for i in range(0, len(clean_dois), 10):
            batch = clean_dois[i:i + 10]
            orig_batch = dois[i:i + 10]
            or_query = " OR ".join(f'"{d}"' for d in batch)
            wos_query = f"DO=({or_query})"

            try:
                if self._tier == "expanded":
                    papers = await self._search_expanded(wos_query, "relevance", 50)
                else:
                    papers = await self._search_starter(wos_query, "relevance", 50)

                for paper in papers:
                    paper.verified_by = ["wos"]
                    if paper.doi:
                        paper_doi = paper.doi.lower()
                        if paper_doi.startswith("https://doi.org/"):
                            paper_doi = paper_doi[len("https://doi.org/"):]
                        for orig in orig_batch:
                            clean_orig = orig
                            if clean_orig.startswith("https://doi.org/"):
                                clean_orig = clean_orig[len("https://doi.org/"):]
                            if paper_doi == clean_orig.lower():
                                results[orig] = paper
                                break
            except Exception:
                logger.warning("WoS batch verify failed for chunk starting at %d", i)

        return results

    async def find_similar_works(
        self,
        text: str,
        *,
        limit: int = 20,
    ) -> list[Paper]:
        query = _extract_search_terms(text, max_terms=12)
        if not query:
            return []
        return await self.search_works(query, sort_by="relevance", limit=limit)

    async def close(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Starter API implementation
    # ------------------------------------------------------------------

    async def _search_starter(
        self, wos_query: str, sort_by: str, limit: int,
    ) -> list[Paper]:
        sort_field = "relevance"
        if sort_by == "cited_by_count":
            sort_field = "TC.D"
        elif sort_by == "publication_year":
            sort_field = "PY.D"

        papers: list[Paper] = []
        page = 1
        per_page = min(limit, self._per_page_max)

        while len(papers) < limit:
            try:
                resp = await self._client.get(
                    "/documents",
                    params={
                        "q": wos_query,
                        "limit": per_page,
                        "page": page,
                        "sortField": sort_field,
                        "db": "WOS",
                    },
                )
                resp.raise_for_status()

                if not resp.content or not resp.content.strip():
                    logger.warning("WoS empty response for: %s (page %d)", wos_query, page)
                    break

                content_type = resp.headers.get("content-type", "")
                if "json" not in content_type:
                    logger.warning("WoS non-JSON response (%s) for: %s", content_type, wos_query)
                    break

                data = resp.json()
            except httpx.HTTPStatusError as exc:
                logger.error("WoS HTTP %d for: %s", exc.response.status_code, wos_query)
                break
            except Exception:
                logger.exception("WoS search failed for: %s (page %d)", wos_query, page)
                break

            hits = data.get("hits", [])
            if not hits:
                break

            for hit in hits:
                papers.append(self._starter_to_paper(hit))
                if len(papers) >= limit:
                    break

            total = data.get("metadata", {}).get("total", 0)
            if page * per_page >= total:
                break
            page += 1

        return papers[:limit]

    # ------------------------------------------------------------------
    # Expanded API implementation
    # ------------------------------------------------------------------

    async def _search_expanded(
        self, wos_query: str, sort_by: str, limit: int,
    ) -> list[Paper]:
        # Expanded uses different sort format: field+direction (e.g. PY+D)
        sort_field = "RS+D"  # relevance score descending
        if sort_by == "cited_by_count":
            sort_field = "TC+D"
        elif sort_by == "publication_year":
            sort_field = "PY+D"

        papers: list[Paper] = []
        first_record = 1
        per_page = min(limit, self._per_page_max)
        query_id: int | None = None

        while len(papers) < limit:
            try:
                if query_id is None:
                    # First request: search query
                    resp = await self._client.get(
                        "",
                        params={
                            "databaseId": "WOS",
                            "usrQuery": wos_query,
                            "count": per_page,
                            "firstRecord": first_record,
                            "sortField": sort_field,
                            "optionView": "FR",
                        },
                    )
                else:
                    # Subsequent pages: use queryId
                    resp = await self._client.get(
                        f"/query/{query_id}",
                        params={
                            "count": per_page,
                            "firstRecord": first_record,
                            "sortField": sort_field,
                            "optionView": "FR",
                        },
                    )
                resp.raise_for_status()

                if not resp.content or not resp.content.strip():
                    logger.warning("WoS Expanded empty response for: %s", wos_query)
                    break

                content_type = resp.headers.get("content-type", "")
                if "json" not in content_type:
                    logger.warning("WoS Expanded non-JSON response (%s)", content_type)
                    break

                data = resp.json()
            except httpx.HTTPStatusError as exc:
                logger.error(
                    "WoS Expanded HTTP %d for: %s. Body: %.200s",
                    exc.response.status_code, wos_query, exc.response.text,
                )
                break
            except Exception:
                logger.exception("WoS Expanded search failed for: %s", wos_query)
                break

            # Extract query metadata
            query_result = data.get("QueryResult", {})
            if query_id is None:
                query_id = query_result.get("QueryID")
            records_found = query_result.get("RecordsFound", 0)

            # Extract records
            recs = (
                data
                .get("Data", {})
                .get("Records", {})
                .get("records", {})
                .get("REC", [])
            )
            if not recs:
                break

            for rec in recs:
                papers.append(self._expanded_to_paper(rec))
                if len(papers) >= limit:
                    break

            first_record += len(recs)
            if first_record > records_found:
                break

        return papers[:limit]

    # ------------------------------------------------------------------
    # Record converters
    # ------------------------------------------------------------------

    @staticmethod
    def _starter_to_paper(hit: dict) -> Paper:
        """Convert WoS Starter API hit to Paper."""
        names = hit.get("names", {})
        authors = []
        for author_entry in names.get("authors", []):
            display_name = author_entry.get("displayName") or author_entry.get("wosStandard", "")
            if display_name:
                authors.append(display_name)

        keywords = hit.get("keywords", {}).get("authorKeywords", []) or []

        cited_by = 0
        for c in hit.get("citations", []):
            if c.get("db") == "wos":
                try:
                    cited_by = int(c.get("count", 0))
                except (ValueError, TypeError):
                    pass
                break

        pub_year = 0
        source_info = hit.get("source", {})
        pub_date = source_info.get("publishYear")
        if pub_date:
            try:
                pub_year = int(pub_date)
            except (ValueError, TypeError):
                pass

        identifiers = hit.get("identifiers", {})
        doi = identifiers.get("doi")
        if doi and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"

        uid = hit.get("uid", "")

        return Paper(
            source_id=f"wos:{uid}",
            title=hit.get("title", "") or "",
            abstract=None,  # Starter API doesn't return abstracts
            authors=authors,
            publication_year=pub_year,
            cited_by_count=cited_by,
            source_name=source_info.get("sourceTitle"),
            doi=doi,
            keywords=keywords,
            url=doi or f"https://www.webofscience.com/wos/woscc/full-record/{uid}",
            verified_by=["wos"],
        )

    @staticmethod
    def _expanded_to_paper(rec: dict) -> Paper:
        """Convert WoS Expanded API record to Paper."""
        uid = rec.get("UID", "")
        static = rec.get("static_data", {})
        dynamic = rec.get("dynamic_data", {})
        summary = static.get("summary", {})
        fullrecord = static.get("fullrecord_metadata", {})

        # Title — look for type "item" (article title)
        title = ""
        source_name = None
        for t in summary.get("titles", {}).get("title", []):
            if t.get("type") == "item":
                title = t.get("content", "")
            elif t.get("type") == "source":
                source_name = t.get("content")

        # Authors
        authors = []
        for name_entry in summary.get("names", {}).get("name", []):
            if name_entry.get("role") == "author":
                display = (
                    name_entry.get("display_name")
                    or name_entry.get("full_name")
                    or name_entry.get("wos_standard", "")
                )
                if display:
                    authors.append(display)

        # Abstract
        abstract = None
        abstracts_block = fullrecord.get("abstracts", {}).get("abstract", {})
        abstract_text = abstracts_block.get("abstract_text", {})
        if isinstance(abstract_text, dict):
            p = abstract_text.get("p")
            if isinstance(p, list):
                abstract = " ".join(str(para) for para in p)
            elif isinstance(p, str):
                abstract = p
        elif isinstance(abstract_text, str):
            abstract = abstract_text

        # Keywords
        keywords = fullrecord.get("keywords", {}).get("keyword", []) or []
        if isinstance(keywords, str):
            keywords = [keywords]

        # Publication year
        pub_year = 0
        pub_info = summary.get("pub_info", {})
        pubyear = pub_info.get("pubyear")
        if pubyear:
            try:
                pub_year = int(pubyear)
            except (ValueError, TypeError):
                pass

        # Citation count — from dynamic_data.citation_related.tc_list.silo_tc
        cited_by = 0
        tc_list = (
            dynamic
            .get("citation_related", {})
            .get("tc_list", {})
            .get("silo_tc", [])
        )
        for tc in tc_list:
            if tc.get("coll_id") == "WOS":
                try:
                    cited_by = int(tc.get("local_count", 0))
                except (ValueError, TypeError):
                    pass
                break

        # DOI — try dynamic_data path first (most reliable), then static fallbacks
        doi = None
        dyn_ids = dynamic.get("cluster_related", {}).get("identifiers", {}).get("identifier", [])
        if isinstance(dyn_ids, dict):
            dyn_ids = [dyn_ids]
        for ident in dyn_ids:
            if ident.get("type") == "doi":
                doi = ident.get("value")
                break
        if not doi:
            static_ids = summary.get("identifiers", {}).get("identifier", [])
            if isinstance(static_ids, dict):
                static_ids = [static_ids]
            for ident in static_ids:
                if ident.get("type") == "doi":
                    doi = ident.get("value")
                    break
        if not doi:
            doi = static.get("item", {}).get("ids", {}).get("doi")
        if doi and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"

        return Paper(
            source_id=f"wos:{uid}",
            title=title,
            abstract=abstract,
            authors=authors,
            publication_year=pub_year,
            cited_by_count=cited_by,
            source_name=source_name,
            doi=doi,
            keywords=keywords,
            url=doi or f"https://www.webofscience.com/wos/woscc/full-record/{uid}",
            verified_by=["wos"],
        )
