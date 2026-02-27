"""Pydantic models for CLI council results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Assessment(BaseModel):
    """One council member's individual assessment (Stage 1)."""

    backend: str        # "gemini", "codex", "claude"
    model: str          # model name/ID used by the backend
    text: str           # raw text response
    label: str = ""     # anonymised label, e.g. "Assessment A"
    elapsed_ms: int = 0


class PeerReview(BaseModel):
    """One council member's peer review of all assessments (Stage 2)."""

    backend: str
    model: str
    review_text: str
    parsed_ranking: list[str] = Field(default_factory=list)
    elapsed_ms: int = 0


class CouncilMeta(BaseModel):
    """Metadata for a council run."""

    backends_used: list[str]
    stage1_ms: int = 0
    stage2_ms: int = 0
    stage3_ms: int = 0
    total_ms: int = 0
    chairman_backend: str = "claude"
    errors: list[str] = Field(default_factory=list)


class CouncilResult(BaseModel):
    """Full council deliberation result."""

    synthesis: str
    assessments: list[Assessment]
    peer_reviews: list[PeerReview]
    meta: CouncilMeta
