"""OpenAlex adapter wrapping the shared client from .scripts/openalex/."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from sources.base import ScholarlySource
from sources.models import Paper

logger = logging.getLogger(__name__)

# Import the shared OpenAlex client
SCRIPTS_DIR = str(Path(__file__).parent.parent.parent / ".scripts" / "openalex")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from openalex_client import OpenAlexClient  # noqa: E402


class OpenAlexSource(ScholarlySource):
    """OpenAlex implementation using the shared client.

    Always available (no API key needed). Uses polite pool with email.
    """

    def __init__(self, client: OpenAlexClient) -> None:
        self._client = client

    @property
    def source_name(self) -> str:
        return "OpenAlex"

    @property
    def source_key(self) -> str:
        return "openalex"

    async def search_works(
        self,
        query: str,
        *,
        year_from: int | None = None,
        year_to: int | None = None,
        sort_by: str = "relevance",
        limit: int = 50,
    ) -> list[Paper]:
        filter_params: dict[str, str] = {}
        if year_from and year_to:
            filter_params["publication_year"] = f"{year_from}-{year_to}"
        elif year_from:
            filter_params["publication_year"] = f">{year_from - 1}"
        elif year_to:
            filter_params["publication_year"] = f"<{year_to + 1}"

        sort_param = "cited_by_count:desc"
        if sort_by == "relevance":
            sort_param = "relevance_score:desc"
        elif sort_by == "publication_year":
            sort_param = "publication_date:desc"

        def _search() -> dict[str, Any]:
            return self._client.search_works(
                search=query,
                filter_params=filter_params if filter_params else None,
                per_page=min(limit, 200),
                sort=sort_param,
            )

        response = await asyncio.to_thread(_search)
        works = response.get("results", [])
        return [self._to_paper(w) for w in works[:limit]]

    async def verify_doi(self, doi: str) -> Paper | None:
        if not doi.startswith("https://doi.org/"):
            doi = f"https://doi.org/{doi}"

        try:
            work = await asyncio.to_thread(self._client.get_entity, "works", doi)
            if work and work.get("id"):
                return self._to_paper(work)
        except Exception:
            logger.debug("OpenAlex DOI lookup failed for: %s", doi)
        return None

    async def batch_verify_dois(self, dois: list[str]) -> dict[str, Paper | None]:
        # Normalize DOIs
        normalized = []
        for d in dois:
            if not d.startswith("https://doi.org/"):
                d = f"https://doi.org/{d}"
            normalized.append(d)

        results: dict[str, Paper | None] = {d: None for d in dois}

        try:
            works = await asyncio.to_thread(
                self._client.batch_lookup, "works", normalized, "doi"
            )
            for w in works:
                doi_val = w.get("doi", "")
                if doi_val:
                    # Match back to original DOI
                    for orig in dois:
                        norm_orig = orig if orig.startswith("https://doi.org/") else f"https://doi.org/{orig}"
                        if doi_val.lower() == norm_orig.lower():
                            results[orig] = self._to_paper(w)
                            break
        except Exception:
            logger.warning("OpenAlex batch DOI lookup failed")

        return results

    async def find_similar_works(
        self,
        text: str,
        *,
        limit: int = 20,
    ) -> list[Paper]:
        return await self.search_works(text, sort_by="relevance", limit=limit)

    @staticmethod
    def _to_paper(work: dict[str, Any]) -> Paper:
        """Convert OpenAlex work dict to Paper."""
        # Authors
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                authors.append(name)

        # Keywords
        keywords = []
        for kw in work.get("keywords", []):
            if isinstance(kw, dict):
                keywords.append(kw.get("keyword", ""))
            elif isinstance(kw, str):
                keywords.append(kw)

        # Abstract
        abstract = None
        inv_abstract = work.get("abstract_inverted_index")
        if inv_abstract:
            try:
                word_positions = []
                for word, positions in inv_abstract.items():
                    for pos in positions:
                        word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join(w for _, w in word_positions)
            except Exception:
                pass

        # DOI
        doi = work.get("doi")
        if doi and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"

        # Publication year
        pub_year = work.get("publication_year", 0) or 0

        # Source / journal
        source_name = None
        primary_location = work.get("primary_location") or {}
        source_info = primary_location.get("source") or {}
        source_name = source_info.get("display_name")

        return Paper(
            source_id=f"openalex:{work.get('id', '')}",
            title=work.get("title", "") or "",
            abstract=abstract,
            authors=authors,
            publication_year=pub_year,
            cited_by_count=work.get("cited_by_count", 0) or 0,
            source_name=source_name,
            doi=doi,
            keywords=keywords,
            url=doi or work.get("id", ""),
            verified_by=["openalex"],
        )
