"""Pydantic models for council deliberation results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CouncilAssessment(BaseModel):
    """One council member's individual assessment (Stage 1)."""

    model: str          # OpenRouter model ID
    model_name: str     # human-readable name
    result_json: dict   # raw JSON response (schema depends on consumer)
    label: str = ""     # anonymised label, e.g. "Assessment A"


class CouncilPeerReview(BaseModel):
    """One council member's peer review of all assessments (Stage 2)."""

    model: str
    model_name: str
    review_text: str    # free-form evaluation + disagreement analysis
    parsed_ranking: list[str] = Field(default_factory=list)


class CouncilMeta(BaseModel):
    """Metadata for a council run."""

    council_models: list[str]
    chairman_model: str
    stage1_ms: int = 0
    stage2_ms: int = 0
    stage3_ms: int = 0
    total_ms: int = 0
    reused_model: str | None = None
    aggregate_rankings: list[dict] = Field(default_factory=list)
    stage3_fallback: bool = False


class CouncilResult(BaseModel):
    """Full council deliberation result."""

    final_result: dict  # synthesised response (schema depends on consumer)
    assessments: list[CouncilAssessment]
    peer_reviews: list[CouncilPeerReview]
    meta: CouncilMeta
