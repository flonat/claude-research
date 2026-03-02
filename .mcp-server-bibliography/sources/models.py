"""Paper dataclass for multi-source scholarly search."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Paper:
    """Unified paper representation across all sources."""

    source_id: str
    title: str
    authors: list[str]
    publication_year: int
    cited_by_count: int
    doi: str | None
    abstract: str | None = None
    source_name: str | None = None  # journal / venue
    keywords: list[str] = field(default_factory=list)
    url: str | None = None
    verified_by: list[str] = field(default_factory=list)  # which sources confirmed this DOI
