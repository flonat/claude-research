"""Multi-source scholarly search adapters."""

from sources.models import Paper
from sources.base import ScholarlySource
from sources.openalex_source import OpenAlexSource
from sources.multi_source import MultiSource, deduplicate_papers

__all__ = [
    "Paper",
    "ScholarlySource",
    "OpenAlexSource",
    "MultiSource",
    "deduplicate_papers",
]
