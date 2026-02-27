"""Scopus adapter using httpx (Elsevier REST API).

Uses async httpx client. Requires SCOPUS_API_KEY env var.
Optional SCOPUS_INST_TOKEN for non-institutional IP access.

SYNC: Mirrored in Topic Finder (claude_topic_finder/services/scopus.py).
Changes to query construction, pagination, or record parsing must be propagated.
Topic Finder adds get_topics/get_trend_data; this version adds
verify_doi/batch_verify_dois. Core search logic should stay identical.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from sources.base import ScholarlySource
from sources.models import Paper

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"

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
    """Extract key terms from a long text for use in Scopus TITLE-ABS-KEY() queries."""
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


class ScopusSource(ScholarlySource):
    """Scopus implementation using the Elsevier REST API directly.

    Uses httpx async client — no pybliometrics dependency.
    Supports API key only (institutional IP) or API key + InstToken (any IP).
    """

    def __init__(self, api_key: str, inst_token: str = "") -> None:
        self._api_key = api_key
        self._inst_token = inst_token
        headers: dict[str, str] = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json",
        }
        if inst_token:
            headers["X-ELS-Insttoken"] = inst_token
        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
        )

    @property
    def source_name(self) -> str:
        return "Scopus"

    @property
    def source_key(self) -> str:
        return "scopus"

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
        scopus_query = f"TITLE-ABS-KEY({query})"
        if year_from:
            scopus_query += f" AND PUBYEAR > {year_from - 1}"
        if year_to:
            scopus_query += f" AND PUBYEAR < {year_to + 1}"

        sort_param = "relevancy"
        if sort_by == "cited_by_count":
            sort_param = "-citedby-count"
        elif sort_by == "publication_year":
            sort_param = "-coverDate"

        papers: list[Paper] = []
        start = 0
        per_page = min(limit, 25)

        while len(papers) < limit:
            params: dict[str, Any] = {
                "query": scopus_query,
                "start": start,
                "count": per_page,
                "sort": sort_param,
                "view": "COMPLETE",
            }
            try:
                resp = await self._client.get(_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "Scopus HTTP %d for: %s. Body: %.200s",
                    exc.response.status_code, scopus_query, exc.response.text,
                )
                break
            except Exception:
                logger.warning("Scopus search failed for: %s", scopus_query, exc_info=True)
                break

            results = data.get("search-results", {})
            entries = results.get("entry", [])
            if not entries or (len(entries) == 1 and "error" in entries[0]):
                break

            for entry in entries:
                papers.append(self._to_paper(entry))
                if len(papers) >= limit:
                    break

            total = int(results.get("opensearch:totalResults", 0) or 0)
            start += per_page
            if start >= total:
                break

        return papers[:limit]

    async def verify_doi(self, doi: str) -> Paper | None:
        clean_doi = doi
        if clean_doi.startswith("https://doi.org/"):
            clean_doi = clean_doi[len("https://doi.org/"):]

        scopus_query = f"DOI({clean_doi})"
        params: dict[str, Any] = {
            "query": scopus_query,
            "start": 0,
            "count": 1,
            "view": "COMPLETE",
        }
        try:
            resp = await self._client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.debug("Scopus DOI verify failed for: %s", doi)
            return None

        entries = data.get("search-results", {}).get("entry", [])
        if not entries or (len(entries) == 1 and "error" in entries[0]):
            return None

        paper = self._to_paper(entries[0])
        paper.verified_by = ["scopus"]
        return paper

    async def batch_verify_dois(self, dois: list[str]) -> dict[str, Paper | None]:
        results: dict[str, Paper | None] = {d: None for d in dois}

        clean_dois = []
        for d in dois:
            clean = d
            if clean.startswith("https://doi.org/"):
                clean = clean[len("https://doi.org/"):]
            clean_dois.append(clean)

        # Process in chunks of 10 (Scopus query length limits)
        for i in range(0, len(clean_dois), 10):
            batch = clean_dois[i:i + 10]
            orig_batch = dois[i:i + 10]
            or_query = " OR ".join(f"DOI({d})" for d in batch)

            try:
                resp = await self._client.get(
                    _SEARCH_URL,
                    params={
                        "query": or_query,
                        "start": 0,
                        "count": 25,
                        "view": "COMPLETE",
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                entries = data.get("search-results", {}).get("entry", [])
                if not entries or (len(entries) == 1 and "error" in entries[0]):
                    continue

                for entry in entries:
                    paper = self._to_paper(entry)
                    paper.verified_by = ["scopus"]
                    entry_doi = entry.get("prism:doi", "")
                    if entry_doi:
                        entry_doi_lower = entry_doi.lower()
                        for orig in orig_batch:
                            clean_orig = orig
                            if clean_orig.startswith("https://doi.org/"):
                                clean_orig = clean_orig[len("https://doi.org/"):]
                            if entry_doi_lower == clean_orig.lower():
                                results[orig] = paper
                                break
            except Exception:
                logger.warning("Scopus batch verify failed for chunk starting at %d", i)

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
    # Paper mapping
    # ------------------------------------------------------------------

    @staticmethod
    def _to_paper(entry: dict) -> Paper:
        """Convert Scopus JSON entry to Paper."""
        # Authors — dc:creator is first author, author array has all
        authors: list[str] = []
        author_list = entry.get("author", [])
        if author_list:
            for a in author_list:
                name = a.get("authname") or a.get("given-name", "") + " " + a.get("surname", "")
                if name and name.strip():
                    authors.append(name.strip())
        elif entry.get("dc:creator"):
            authors = [entry["dc:creator"]]

        # Keywords
        keywords: list[str] = []
        authkeywords = entry.get("authkeywords")
        if authkeywords:
            keywords = [k.strip() for k in authkeywords.split("|") if k.strip()]

        # Citation count
        cited_by = 0
        try:
            cited_by = int(entry.get("citedby-count", 0) or 0)
        except (ValueError, TypeError):
            pass

        # Publication year from coverDate (YYYY-MM-DD)
        pub_year = 0
        cover_date = entry.get("prism:coverDate", "")
        if cover_date:
            try:
                pub_year = int(str(cover_date)[:4])
            except (ValueError, TypeError):
                pass

        # DOI
        doi = entry.get("prism:doi")
        if doi and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"

        # EID
        eid = entry.get("eid", "")

        # Abstract (available in COMPLETE view)
        abstract = entry.get("dc:description")

        return Paper(
            source_id=f"scopus:{eid}",
            title=entry.get("dc:title", "") or "",
            abstract=abstract,
            authors=authors,
            publication_year=pub_year,
            cited_by_count=cited_by,
            source_name=entry.get("prism:publicationName"),
            doi=doi,
            keywords=keywords,
            url=doi or f"https://www.scopus.com/record/display.uri?eid={eid}",
            verified_by=["scopus"],
        )
