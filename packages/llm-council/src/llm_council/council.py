"""3-stage LLM Council orchestration.

Adapted from karpathy/llm-council:
  Stage 1 -- Individual assessments (parallel, structured JSON or text)
  Stage 2 -- Peer review (parallel, free-form text with FINAL RANKING)
  Stage 3 -- Chairman synthesis (single model, structured JSON or text)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections import defaultdict
from time import perf_counter

from llm_council.client import LLMClient
from llm_council.config import AVAILABLE_MODELS, model_display_name
from llm_council.models import (
    CouncilAssessment,
    CouncilMeta,
    CouncilPeerReview,
    CouncilResult,
)

logger = logging.getLogger(__name__)


class CouncilService:
    """Orchestrates a multi-model council review."""

    def __init__(self, llm: LLMClient, *, max_tokens: int | None = None) -> None:
        self.llm = llm
        self._max_tokens = max_tokens

    async def run_council(
        self,
        system_prompt: str,
        user_msg: str,
        council_models: list[str],
        chairman_model: str,
        *,
        existing_result: dict | None = None,
        existing_model: str | None = None,
        stage2_system: str | None = None,
        stage3_prompt_builder: object | None = None,
    ) -> CouncilResult:
        """Run the full 3-stage council process.

        Parameters
        ----------
        system_prompt:
            The system prompt for Stage 1 assessments.
        user_msg:
            The user message for Stage 1 assessments.
        council_models:
            List of OpenRouter model IDs to query (3+ models).
        chairman_model:
            Model to use for the final synthesis.
        existing_result:
            If provided, reuse this as one of the Stage 1 assessments.
        existing_model:
            The model ID that produced ``existing_result``.
        stage2_system:
            Optional custom system prompt for Stage 2 peer review.
            Defaults to a generic meta-reviewer prompt.
        stage3_prompt_builder:
            Optional callable(assessments, peer_reviews, user_msg) -> str
            that builds a custom Stage 3 chairman prompt. If None, uses
            the default synthesis prompt.
        """
        t_total = perf_counter()

        # Stage 1
        t1 = perf_counter()
        assessments = await self._stage1_collect(
            system_prompt, user_msg, council_models,
            existing_result=existing_result,
            existing_model=existing_model,
        )
        stage1_ms = int((perf_counter() - t1) * 1000)

        if not assessments:
            return CouncilResult(
                final_result={},
                assessments=[],
                peer_reviews=[],
                meta=CouncilMeta(
                    council_models=council_models,
                    chairman_model=chairman_model,
                    stage1_ms=stage1_ms,
                    total_ms=int((perf_counter() - t_total) * 1000),
                    reused_model=existing_model,
                ),
            )

        for i, a in enumerate(assessments):
            a.label = f"Assessment {chr(65 + i)}"

        # Stage 2
        t2 = perf_counter()
        peer_reviews, label_to_model = await self._stage2_peer_review(
            system_prompt, user_msg, assessments, council_models,
            custom_system=stage2_system,
        )
        stage2_ms = int((perf_counter() - t2) * 1000)

        aggregate_rankings = self._calculate_aggregate_rankings(
            peer_reviews, label_to_model,
        )

        # Stage 3
        t3 = perf_counter()
        final_result, stage3_fallback = await self._stage3_synthesise(
            system_prompt, user_msg, assessments, peer_reviews,
            chairman_model,
            custom_prompt_builder=stage3_prompt_builder,
        )
        stage3_ms = int((perf_counter() - t3) * 1000)

        total_ms = int((perf_counter() - t_total) * 1000)

        return CouncilResult(
            final_result=final_result,
            assessments=assessments,
            peer_reviews=peer_reviews,
            meta=CouncilMeta(
                council_models=council_models,
                chairman_model=chairman_model,
                stage1_ms=stage1_ms,
                stage2_ms=stage2_ms,
                stage3_ms=stage3_ms,
                total_ms=total_ms,
                reused_model=existing_model,
                aggregate_rankings=aggregate_rankings,
                stage3_fallback=stage3_fallback,
            ),
        )

    # ------------------------------------------------------------------
    # Stage 1
    # ------------------------------------------------------------------

    async def _stage1_collect(
        self,
        system_prompt: str,
        user_msg: str,
        council_models: list[str],
        *,
        existing_result: dict | None = None,
        existing_model: str | None = None,
    ) -> list[CouncilAssessment]:
        assessments: list[CouncilAssessment] = []

        if existing_result and existing_model:
            assessments.append(CouncilAssessment(
                model=existing_model,
                model_name=model_display_name(existing_model),
                result_json=existing_result,
            ))

        models_to_query = [
            m for m in council_models
            if m != existing_model or existing_result is None
        ]

        if not models_to_query:
            return assessments

        async def _query_one(model_id: str) -> CouncilAssessment | None:
            try:
                result = await self.llm.chat_json(
                    system_prompt, user_msg,
                    model=model_id, max_tokens=self._max_tokens,
                )
                return CouncilAssessment(
                    model=model_id,
                    model_name=model_display_name(model_id),
                    result_json=result,
                )
            except Exception:
                logger.exception("Council Stage 1: model %s failed", model_id)
                return None

        tasks = [_query_one(m) for m in models_to_query]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r is not None:
                assessments.append(r)

        logger.info(
            "Council Stage 1: %d/%d models responded",
            len(assessments), len(council_models),
        )
        return assessments

    # ------------------------------------------------------------------
    # Stage 2
    # ------------------------------------------------------------------

    async def _stage2_peer_review(
        self,
        system_prompt: str,
        user_msg: str,
        assessments: list[CouncilAssessment],
        council_models: list[str],
        *,
        custom_system: str | None = None,
    ) -> tuple[list[CouncilPeerReview], dict[str, str]]:
        assessments_text = "\n\n---\n\n".join(
            f"**{a.label}:**\n```json\n{json.dumps(a.result_json, indent=2)}\n```"
            for a in assessments
        )

        label_to_model = {a.label: a.model for a in assessments}

        review_prompt = f"""You are reviewing multiple assessments of the same question/task.

The original question/context given to all assessors:
{user_msg[:3000]}

Here are the anonymised assessments:

{assessments_text}

Your task:
1. Evaluate each assessment individually. What does it do well? What does it miss or get wrong?
2. Identify specific areas of AGREEMENT across assessments.
3. Identify specific areas of DISAGREEMENT and explain which position you find more convincing and why.
4. Provide a final ranking from best to worst.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the assessments from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the assessment label (e.g., "1. Assessment A")

Now provide your evaluation and ranking:"""

        review_system = custom_system or (
            "You are an expert meta-reviewer. You evaluate and compare "
            "multiple independent assessments, identifying strengths, "
            "weaknesses, agreements, and disagreements."
        )

        models_to_review = [m for m in council_models if m in {a.model for a in assessments}]
        if not models_to_review:
            models_to_review = council_models

        async def _review_one(model_id: str) -> CouncilPeerReview | None:
            try:
                text = await self.llm.chat_text(
                    review_system, review_prompt,
                    model=model_id, max_tokens=self._max_tokens,
                )
                parsed = self._parse_ranking_from_text(text)
                return CouncilPeerReview(
                    model=model_id,
                    model_name=model_display_name(model_id),
                    review_text=text,
                    parsed_ranking=parsed,
                )
            except Exception:
                logger.exception("Council Stage 2: model %s failed", model_id)
                return None

        tasks = [_review_one(m) for m in models_to_review]
        results = await asyncio.gather(*tasks)

        reviews = [r for r in results if r is not None]
        logger.info(
            "Council Stage 2: %d/%d models reviewed",
            len(reviews), len(models_to_review),
        )
        return reviews, label_to_model

    # ------------------------------------------------------------------
    # Stage 3
    # ------------------------------------------------------------------

    async def _stage3_synthesise(
        self,
        system_prompt: str,
        user_msg: str,
        assessments: list[CouncilAssessment],
        peer_reviews: list[CouncilPeerReview],
        chairman_model: str,
        *,
        custom_prompt_builder: object | None = None,
    ) -> tuple[dict, bool]:
        if custom_prompt_builder and callable(custom_prompt_builder):
            chairman_prompt = custom_prompt_builder(assessments, peer_reviews, user_msg)
        else:
            assessments_text = "\n\n".join(
                f"**{a.label}** (by {a.model_name}):\n"
                f"```json\n{json.dumps(a.result_json, indent=2)}\n```"
                for a in assessments
            )

            reviews_text = "\n\n".join(
                f"**Review by {r.model_name}:**\n{r.review_text}"
                for r in peer_reviews
            )

            chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have independently assessed the same question, and then peer-reviewed each other's assessments.

ORIGINAL CONTEXT:
{user_msg[:3000]}

STAGE 1 -- Individual Assessments:
{assessments_text}

STAGE 2 -- Peer Reviews:
{reviews_text}

Your task as Chairman:
1. Consider all individual assessments and their insights
2. Consider the peer reviews and what they reveal about quality and disagreements
3. Identify areas of strong consensus vs. genuine disagreement
4. Synthesise a SINGLE, comprehensive answer that represents the council's collective wisdom

Where the council agrees, reflect that consensus. Where they disagree, use your judgment to select the most well-reasoned position and explain why.

You MUST respond with valid JSON matching the EXACT SAME SCHEMA as the individual assessments above. Respond ONLY with valid JSON."""

        try:
            result = await self.llm.chat_json(
                system_prompt, chairman_prompt,
                model=chairman_model, max_tokens=self._max_tokens,
            )
            return result, False
        except Exception:
            logger.exception("Council Stage 3: chairman %s failed", chairman_model)
            if assessments:
                return assessments[0].result_json, True
            return {}, True

    # ------------------------------------------------------------------
    # Ranking utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ranking_from_text(text: str) -> list[str]:
        if "FINAL RANKING:" in text:
            parts = text.split("FINAL RANKING:")
            if len(parts) >= 2:
                ranking_section = parts[1]
                numbered = re.findall(
                    r"\d+\.\s*Assessment [A-Z]", ranking_section,
                )
                if numbered:
                    return [
                        re.search(r"Assessment [A-Z]", m).group()
                        for m in numbered
                    ]
                matches = re.findall(r"Assessment [A-Z]", ranking_section)
                return matches

        return re.findall(r"Assessment [A-Z]", text)

    @staticmethod
    def _calculate_aggregate_rankings(
        peer_reviews: list[CouncilPeerReview],
        label_to_model: dict[str, str],
    ) -> list[dict]:
        positions: dict[str, list[int]] = defaultdict(list)

        for review in peer_reviews:
            for pos, label in enumerate(review.parsed_ranking, start=1):
                if label in label_to_model:
                    positions[label].append(pos)

        aggregate = []
        for label, pos_list in positions.items():
            avg = sum(pos_list) / len(pos_list)
            aggregate.append({
                "label": label,
                "model": label_to_model.get(label, "unknown"),
                "model_name": model_display_name(label_to_model.get(label, "")),
                "average_rank": round(avg, 2),
                "rankings_count": len(pos_list),
            })

        aggregate.sort(key=lambda x: x["average_rank"])
        return aggregate
