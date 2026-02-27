"""Multi-source composite adapter with DOI-based deduplication.

Queries all enabled sources concurrently and merges results.
Ported from ZZ Topic Finder with improvements.
"""

from __future__ import annotations

import asyncio
import logging
import re
from contextvars import ContextVar
from typing import Any

from sources.base import ScholarlySource
from sources.models import Paper

logger = logging.getLogger(__name__)


class MultiSource(ScholarlySource):
    """Composite data source that queries multiple APIs and deduplicates results.

    All methods query sources concurrently. Failed sources are skipped gracefully.
    Papers are deduplicated by normalized DOI; papers without DOIs are kept as-is.
    """

    def __init__(self, sources: list[ScholarlySource]) -> None:
        if not sources:
            raise ValueError("MultiSource requires at least one source")
        self._sources = sources
        self._diagnostics_ctx: ContextVar[dict[str, Any] | None] = ContextVar(
            f"multi_source_diagnostics_{id(self)}", default=None
        )

    @property
    def source_name(self) -> str:
        names = [s.source_name for s in self._sources]
        return " + ".join(names)

    @property
    def source_key(self) -> str:
        return "multi"

    def reset_diagnostics(self) -> None:
        self._diagnostics_ctx.set(
            {
                "attempted": [s.source_name for s in self._sources],
                "failed": set(),
                "warnings": [],
            }
        )

    def consume_diagnostics(self) -> dict[str, Any] | None:
        diag = self._diagnostics_ctx.get()
        if diag is None:
            return None

        attempted = list(diag["attempted"])
        failed = sorted(diag["failed"])
        succeeded = [name for name in attempted if name not in failed]
        warnings = list(diag["warnings"])
        self._diagnostics_ctx.set(None)
        return {
            "attempted": attempted,
            "succeeded": succeeded,
            "failed": failed,
            "warnings": warnings,
        }

    async def search_works(
        self,
        query: str,
        *,
        year_from: int | None = None,
        year_to: int | None = None,
        sort_by: str = "relevance",
        limit: int = 50,
    ) -> list[Paper]:
        coros = [
            s.search_works(query, year_from=year_from, year_to=year_to, sort_by=sort_by, limit=limit)
            for s in self._sources
        ]
        all_papers = await self._gather_flat(coros)
        deduped = deduplicate_papers(all_papers)

        if sort_by == "cited_by_count":
            deduped.sort(key=lambda p: p.cited_by_count, reverse=True)
        elif sort_by == "publication_year":
            deduped.sort(key=lambda p: p.publication_year, reverse=True)

        return deduped[:limit]

    async def verify_doi(self, doi: str) -> Paper | None:
        coros = [s.verify_doi(doi) for s in self._sources]
        results = await asyncio.gather(*coros, return_exceptions=True)

        papers = []
        verified_by: list[str] = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.debug("Source %s failed DOI verify: %s", self._sources[i].source_name, result)
                continue
            if result is not None:
                papers.append(result)
                verified_by.append(self._sources[i].source_key)

        if not papers:
            return None

        # Merge all found papers into one
        merged = papers[0]
        for p in papers[1:]:
            merged = _merge_papers(merged, p)
        merged.verified_by = verified_by
        return merged

    async def batch_verify_dois(self, dois: list[str]) -> dict[str, Paper | None]:
        coros = [s.batch_verify_dois(dois) for s in self._sources]
        results = await asyncio.gather(*coros, return_exceptions=True)

        # Merge results from all sources
        merged: dict[str, Paper | None] = {d: None for d in dois}

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.warning("Source %s failed batch verify: %s", self._sources[i].source_name, result)
                continue

            for doi, paper in result.items():
                if paper is None:
                    continue
                if merged[doi] is None:
                    merged[doi] = paper
                    merged[doi].verified_by = [self._sources[i].source_key]
                else:
                    merged[doi] = _merge_papers(merged[doi], paper)
                    if self._sources[i].source_key not in merged[doi].verified_by:
                        merged[doi].verified_by.append(self._sources[i].source_key)

        return merged

    async def find_similar_works(
        self,
        text: str,
        *,
        limit: int = 20,
    ) -> list[Paper]:
        coros = [s.find_similar_works(text, limit=limit) for s in self._sources]
        all_papers = await self._gather_flat(coros)
        return deduplicate_papers(all_papers)[:limit]

    async def close(self) -> None:
        for s in self._sources:
            try:
                await s.close()
            except Exception:
                pass

    async def _gather_flat(self, coros: list) -> list:
        """Run coroutines concurrently, flatten results, skip failures."""
        diag = self._diagnostics_ctx.get()
        results = await asyncio.gather(*coros, return_exceptions=True)
        flat: list = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                source_name = self._sources[i].source_name
                logger.warning("Source %s failed: %s", source_name, result)
                if diag is not None:
                    diag["failed"].add(source_name)
                    diag["warnings"].append(f"{source_name} failed: {result}")
                continue
            flat.extend(result)
        return flat


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

_DOI_PATTERN = re.compile(r"10\.\d{4,}/[^\s]+", re.IGNORECASE)


def _normalize_doi(doi: str | None) -> str | None:
    """Extract and normalize a DOI string for comparison."""
    if not doi:
        return None
    match = _DOI_PATTERN.search(doi)
    if not match:
        return None
    return match.group(0).lower().rstrip(".")


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Deduplicate papers by normalized DOI.

    For duplicates: keep the longest abstract, max citation count, union keywords.
    Papers without DOIs are kept as-is.
    """
    by_doi: dict[str, Paper] = {}
    no_doi: list[Paper] = []

    for p in papers:
        ndoi = _normalize_doi(p.doi)
        if ndoi is None:
            no_doi.append(p)
            continue

        if ndoi not in by_doi:
            by_doi[ndoi] = p
        else:
            existing = by_doi[ndoi]
            by_doi[ndoi] = _merge_papers(existing, p)

    return list(by_doi.values()) + no_doi


def _merge_papers(a: Paper, b: Paper) -> Paper:
    """Merge two Paper records representing the same work."""
    # Pick the longer abstract
    abstract = a.abstract
    if b.abstract and (not abstract or len(b.abstract) > len(abstract)):
        abstract = b.abstract

    # Union keywords, preserving order
    keywords = list(dict.fromkeys(a.keywords + b.keywords))

    # Union verified_by
    verified_by = list(dict.fromkeys(a.verified_by + b.verified_by))

    return Paper(
        source_id=a.source_id,
        title=a.title or b.title,
        abstract=abstract,
        authors=a.authors or b.authors,
        publication_year=a.publication_year or b.publication_year,
        cited_by_count=max(a.cited_by_count, b.cited_by_count),
        source_name=a.source_name or b.source_name,
        doi=a.doi or b.doi,
        keywords=keywords,
        url=a.url or b.url,
        verified_by=verified_by,
    )
