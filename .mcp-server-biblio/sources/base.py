"""Abstract base class for scholarly data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sources.models import Paper


class ScholarlySource(ABC):
    """Abstract interface for bibliometric data providers.

    Implement this for each data source (OpenAlex, Scopus, Web of Science).
    All methods are async to support concurrent API calls.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of this data source."""
        ...

    @property
    @abstractmethod
    def source_key(self) -> str:
        """Machine-readable slug for this source (e.g. 'openalex', 'scopus', 'wos')."""
        ...

    @abstractmethod
    async def search_works(
        self,
        query: str,
        *,
        year_from: int | None = None,
        year_to: int | None = None,
        sort_by: str = "relevance",
        limit: int = 50,
    ) -> list[Paper]:
        """Search for works matching a text query."""
        ...

    @abstractmethod
    async def verify_doi(self, doi: str) -> Paper | None:
        """Look up a single DOI and return metadata, or None if not found."""
        ...

    @abstractmethod
    async def batch_verify_dois(self, dois: list[str]) -> dict[str, Paper | None]:
        """Verify multiple DOIs at once. Returns {doi: Paper or None}."""
        ...

    @abstractmethod
    async def find_similar_works(
        self,
        text: str,
        *,
        limit: int = 20,
    ) -> list[Paper]:
        """Find works most similar to a given text (title or abstract)."""
        ...

    async def close(self) -> None:
        """Release any network/session resources held by the source."""
        return None

    def reset_diagnostics(self) -> None:
        """Reset per-request diagnostics collected by the source."""
        return None

    def consume_diagnostics(self) -> dict[str, Any] | None:
        """Return and clear diagnostics for the current request context."""
        return None
