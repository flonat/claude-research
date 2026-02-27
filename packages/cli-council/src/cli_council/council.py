"""3-stage council orchestration via local CLI tools.

Stage 1 — Independent assessments (parallel subprocess calls)
Stage 2 — Anonymised peer review (each backend reviews all assessments)
Stage 3 — Chairman synthesis (single backend reads everything, produces final)
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections import defaultdict
from time import perf_counter

from cli_council.backends.base import CLIBackend
from cli_council.config import DEFAULT_CHAIRMAN, DEFAULT_COUNCIL_BACKENDS, STAGE_TIMEOUT
from cli_council.models import Assessment, CouncilMeta, CouncilResult, PeerReview

logger = logging.getLogger(__name__)


def _get_backend(name: str) -> CLIBackend:
    """Instantiate a backend by name."""
    from cli_council.backends.claude import ClaudeBackend
    from cli_council.backends.codex import CodexBackend
    from cli_council.backends.gemini import GeminiBackend

    registry: dict[str, type[CLIBackend]] = {
        "gemini": GeminiBackend,
        "codex": CodexBackend,
        "claude": ClaudeBackend,
    }
    cls = registry.get(name)
    if cls is None:
        raise ValueError(f"Unknown backend: {name!r}. Available: {list(registry)}")
    return cls()


class CouncilRunner:
    """Orchestrates a multi-model council using local CLI tools."""

    def __init__(
        self,
        backends: list[str] | None = None,
        chairman: str | None = None,
        timeout: int = STAGE_TIMEOUT,
        cwd: str | None = None,
    ) -> None:
        self.backend_names = backends or DEFAULT_COUNCIL_BACKENDS
        self.chairman_name = chairman or DEFAULT_CHAIRMAN
        self.timeout = timeout
        self.cwd = cwd

        # Instantiate and validate backends
        self.backends: dict[str, CLIBackend] = {}
        for name in self.backend_names:
            backend = _get_backend(name)
            if not backend.is_available():
                logger.warning("Backend %s not found on PATH — skipping", name)
                continue
            self.backends[name] = backend

        if self.chairman_name not in self.backends:
            chairman_backend = _get_backend(self.chairman_name)
            if chairman_backend.is_available():
                self.backends[self.chairman_name] = chairman_backend

    async def run(
        self,
        prompt: str,
        *,
        system_context: str = "",
    ) -> CouncilResult:
        """Run the full 3-stage council process.

        Parameters
        ----------
        prompt:
            The main question or task for the council.
        system_context:
            Optional context prepended to all prompts (project description,
            file contents, constraints, etc.).
        """
        errors: list[str] = []
        t_total = perf_counter()

        full_prompt = f"{system_context}\n\n{prompt}".strip() if system_context else prompt

        # Stage 1: Independent assessments
        t1 = perf_counter()
        assessments = await self._stage1(full_prompt, errors)
        stage1_ms = int((perf_counter() - t1) * 1000)

        if len(assessments) < 2:
            errors.append(f"Only {len(assessments)} backend(s) responded — need at least 2 for peer review")
            return CouncilResult(
                synthesis=assessments[0].text if assessments else "",
                assessments=assessments,
                peer_reviews=[],
                meta=CouncilMeta(
                    backends_used=[a.backend for a in assessments],
                    stage1_ms=stage1_ms,
                    total_ms=int((perf_counter() - t_total) * 1000),
                    chairman_backend=self.chairman_name,
                    errors=errors,
                ),
            )

        # Assign anonymised labels
        for i, a in enumerate(assessments):
            a.label = f"Assessment {chr(65 + i)}"

        # Stage 2: Peer review
        t2 = perf_counter()
        peer_reviews = await self._stage2(prompt, assessments, errors)
        stage2_ms = int((perf_counter() - t2) * 1000)

        # Stage 3: Chairman synthesis
        t3 = perf_counter()
        synthesis = await self._stage3(prompt, assessments, peer_reviews, errors)
        stage3_ms = int((perf_counter() - t3) * 1000)

        total_ms = int((perf_counter() - t_total) * 1000)

        return CouncilResult(
            synthesis=synthesis,
            assessments=assessments,
            peer_reviews=peer_reviews,
            meta=CouncilMeta(
                backends_used=[a.backend for a in assessments],
                stage1_ms=stage1_ms,
                stage2_ms=stage2_ms,
                stage3_ms=stage3_ms,
                total_ms=total_ms,
                chairman_backend=self.chairman_name,
                errors=errors,
            ),
        )

    # ------------------------------------------------------------------
    # Stage 1: Independent Assessments
    # ------------------------------------------------------------------

    async def _stage1(
        self, prompt: str, errors: list[str],
    ) -> list[Assessment]:
        async def _query(name: str, backend: CLIBackend) -> Assessment | None:
            try:
                text, elapsed = await backend.run(
                    prompt, timeout=self.timeout, cwd=self.cwd,
                )
                return Assessment(
                    backend=name,
                    model=backend.default_model,
                    text=text,
                    elapsed_ms=elapsed,
                )
            except Exception as exc:
                msg = f"Stage 1: {name} failed — {exc}"
                logger.warning(msg)
                errors.append(msg)
                return None

        tasks = [_query(name, b) for name, b in self.backends.items()]
        results = await asyncio.gather(*tasks)
        assessments = [r for r in results if r is not None]

        logger.info(
            "Stage 1: %d/%d backends responded",
            len(assessments), len(self.backends),
        )
        return assessments

    # ------------------------------------------------------------------
    # Stage 2: Anonymised Peer Review
    # ------------------------------------------------------------------

    async def _stage2(
        self,
        original_prompt: str,
        assessments: list[Assessment],
        errors: list[str],
    ) -> list[PeerReview]:
        assessments_block = "\n\n---\n\n".join(
            f"**{a.label}:**\n{a.text}" for a in assessments
        )

        review_prompt = f"""You are reviewing multiple independent assessments of the same question.

ORIGINAL QUESTION:
{original_prompt}

ASSESSMENTS:

{assessments_block}

YOUR TASK:
1. Evaluate each assessment: strengths, weaknesses, gaps.
2. Identify areas of AGREEMENT across assessments.
3. Identify areas of DISAGREEMENT — which position is more convincing and why.
4. Provide a final ranking from best to worst.

IMPORTANT: End your review with "FINAL RANKING:" followed by a numbered list.
Each line: number, period, space, then the assessment label (e.g. "1. Assessment A")."""

        async def _review(name: str, backend: CLIBackend) -> PeerReview | None:
            try:
                text, elapsed = await backend.run(
                    review_prompt, timeout=self.timeout, cwd=self.cwd,
                )
                ranking = self._parse_ranking(text)
                return PeerReview(
                    backend=name,
                    model=backend.default_model,
                    review_text=text,
                    parsed_ranking=ranking,
                    elapsed_ms=elapsed,
                )
            except Exception as exc:
                msg = f"Stage 2: {name} failed — {exc}"
                logger.warning(msg)
                errors.append(msg)
                return None

        tasks = [_review(name, b) for name, b in self.backends.items()]
        results = await asyncio.gather(*tasks)
        reviews = [r for r in results if r is not None]

        logger.info(
            "Stage 2: %d/%d backends reviewed",
            len(reviews), len(self.backends),
        )
        return reviews

    # ------------------------------------------------------------------
    # Stage 3: Chairman Synthesis
    # ------------------------------------------------------------------

    async def _stage3(
        self,
        original_prompt: str,
        assessments: list[Assessment],
        peer_reviews: list[PeerReview],
        errors: list[str],
    ) -> str:
        assessments_block = "\n\n".join(
            f"**{a.label}** (by {a.backend}):\n{a.text}" for a in assessments
        )
        reviews_block = "\n\n".join(
            f"**Review by {r.backend}:**\n{r.review_text}" for r in peer_reviews
        )

        chairman_prompt = f"""You are the Chairman of a multi-model council. Multiple AI systems have independently assessed the same question, then peer-reviewed each other's assessments.

ORIGINAL QUESTION:
{original_prompt}

STAGE 1 — Individual Assessments:
{assessments_block}

STAGE 2 — Peer Reviews:
{reviews_block}

YOUR TASK AS CHAIRMAN:
1. Consider all individual assessments and their insights.
2. Consider the peer reviews and what they reveal about quality and disagreements.
3. Identify areas of strong consensus vs. genuine disagreement.
4. Synthesise a SINGLE, comprehensive answer that represents the council's collective wisdom.

Where the council agrees, reflect that consensus. Where they disagree, use your judgement to select the most well-reasoned position and explain why."""

        chairman_backend = self.backends.get(self.chairman_name)
        if chairman_backend is None:
            errors.append(f"Chairman backend {self.chairman_name!r} not available")
            return assessments[0].text if assessments else ""

        try:
            text, _ = await chairman_backend.run(
                chairman_prompt, timeout=self.timeout * 2, cwd=self.cwd,
            )
            return text
        except Exception as exc:
            msg = f"Stage 3: chairman ({self.chairman_name}) failed — {exc}"
            logger.warning(msg)
            errors.append(msg)
            return assessments[0].text if assessments else ""

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ranking(text: str) -> list[str]:
        """Extract assessment ranking from review text."""
        if "FINAL RANKING:" in text:
            section = text.split("FINAL RANKING:", 1)[1]
            numbered = re.findall(r"\d+\.\s*Assessment [A-Z]", section)
            if numbered:
                return [
                    re.search(r"Assessment [A-Z]", m).group()
                    for m in numbered
                ]
            return re.findall(r"Assessment [A-Z]", section)
        return re.findall(r"Assessment [A-Z]", text)

    def available_backends(self) -> list[str]:
        """Return names of backends that are installed and available."""
        return list(self.backends.keys())
