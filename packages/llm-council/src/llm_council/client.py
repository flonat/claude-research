"""Generic OpenRouter LLM client.

Extracted from claude-topic-finder's services/llm.py — only the generic
OpenRouter wrapper, JSON parsing, and error handling. No workflow-specific
prompts or methods.
"""

from __future__ import annotations

import json
import logging
import re

import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CREDITS_URL = "https://openrouter.ai/credits"


class LLMResponseFormatError(RuntimeError):
    """Raised when an LLM response cannot be parsed into valid JSON."""


class LLMServiceError(Exception):
    """User-friendly error from the LLM service."""

    def __init__(
        self,
        message: str,
        *,
        help_url: str | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.help_url = help_url
        self.detail = detail


def _handle_openai_error(exc: Exception) -> LLMServiceError:
    """Convert openai SDK exceptions into user-friendly LLMServiceError."""
    if isinstance(exc, openai.AuthenticationError):
        return LLMServiceError(
            "Invalid OpenRouter API key. Please check your OPENROUTER_API_KEY.",
            help_url=OPENROUTER_CREDITS_URL,
            detail=str(exc),
        )
    if isinstance(exc, openai.RateLimitError):
        return LLMServiceError(
            "OpenRouter rate limit reached. Please wait a moment and try again.",
            help_url=OPENROUTER_CREDITS_URL,
            detail=str(exc),
        )
    if isinstance(exc, openai.APIStatusError):
        status = getattr(exc, "status_code", None)
        if status == 402:
            return LLMServiceError(
                "Insufficient OpenRouter credits. Please top up your account.",
                help_url=OPENROUTER_CREDITS_URL,
                detail=str(exc),
            )
        if status == 503:
            return LLMServiceError(
                "The selected LLM model is temporarily unavailable. Try a different model.",
                detail=str(exc),
            )
        return LLMServiceError(
            f"OpenRouter API error (HTTP {status}). Please try again.",
            help_url=OPENROUTER_CREDITS_URL,
            detail=str(exc),
        )
    if isinstance(exc, openai.APIConnectionError):
        return LLMServiceError(
            "Could not connect to OpenRouter. Please check your internet connection.",
            detail=str(exc),
        )
    return LLMServiceError(
        "LLM request failed unexpectedly. Please try again.",
        detail=str(exc),
    )


class LLMClient:
    """Generic async LLM client via OpenRouter.

    Provides structured JSON and raw text chat methods with retry logic.
    Consumers extend this with domain-specific workflow methods.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-sonnet-4.5",
        max_tokens: int = 4096,
        json_retry_attempts: int = 2,
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
        )
        self.model = model
        self.max_tokens = max_tokens
        self.json_retry_attempts = max(1, json_retry_attempts)

    async def chat_json(
        self,
        system: str,
        user_msg: str,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """Send a message and parse a JSON-object response with retries.

        Parameters
        ----------
        max_tokens:
            Override the client's default ``max_tokens`` for this call.
            Useful when the expected JSON response is larger than usual
            (e.g. council synthesis of a discovery workflow).
        """
        effective_model = model or self.model
        effective_max_tokens = max_tokens or self.max_tokens
        prompt = user_msg + "\n\nRespond ONLY with valid JSON."
        raw_text = ""
        parse_error: Exception | None = None

        for attempt in range(1, self.json_retry_attempts + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=effective_model,
                    max_tokens=effective_max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                )
            except (openai.APIError, openai.APIConnectionError) as api_exc:
                raise _handle_openai_error(api_exc) from api_exc

            raw_text = (response.choices[0].message.content or "").strip()

            try:
                return self._parse_json_response(raw_text)
            except LLMResponseFormatError as exc:
                parse_error = exc
                logger.warning(
                    "LLM JSON parse failed (attempt %d/%d): %s",
                    attempt, self.json_retry_attempts, exc,
                )
                if attempt == self.json_retry_attempts:
                    break
                prompt = (
                    "Your previous response was not valid JSON.\n"
                    "Return ONLY a valid JSON object matching the schema in the system prompt.\n"
                    "Do not include markdown fences or commentary.\n\n"
                    "Previous invalid response:\n"
                    f"{raw_text[:8000]}"
                )

        snippet = raw_text[:240].replace("\n", " ")
        raise LLMResponseFormatError(
            f"Failed to parse LLM JSON response after {self.json_retry_attempts} attempts. "
            f"Last parse error: {parse_error}. Response snippet: {snippet!r}"
        )

    async def chat_text(
        self,
        system: str,
        user_msg: str,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Query the LLM and return the raw text response (no JSON parsing).

        Used for Stage 2 peer review which returns free-form text with a
        FINAL RANKING section.

        Parameters
        ----------
        max_tokens:
            Override the client's default ``max_tokens`` for this call.
        """
        effective_model = model or self.model
        effective_max_tokens = max_tokens or self.max_tokens
        try:
            response = await self.client.chat.completions.create(
                model=effective_model,
                max_tokens=effective_max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
            )
        except (openai.APIError, openai.APIConnectionError) as api_exc:
            raise _handle_openai_error(api_exc) from api_exc
        return (response.choices[0].message.content or "").strip()

    async def close(self) -> None:
        await self.client.close()

    # ------------------------------------------------------------------
    # JSON parsing utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_json_candidates(text: str) -> list[str]:
        stripped = text.strip()
        candidates: list[str] = []

        if stripped:
            candidates.append(stripped)

        fenced_blocks = re.findall(
            r"```(?:json)?\s*(.*?)```", stripped, flags=re.IGNORECASE | re.DOTALL,
        )
        for block in fenced_blocks:
            block = block.strip()
            if block:
                candidates.append(block)

        first_brace = stripped.find("{")
        last_brace = stripped.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidates.append(stripped[first_brace : last_brace + 1].strip())

        deduped: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                deduped.append(candidate)
        return deduped

    @classmethod
    def _parse_json_response(cls, text: str) -> dict:
        errors: list[str] = []
        for candidate in cls._extract_json_candidates(text):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError as exc:
                errors.append(f"{exc.msg} (line {exc.lineno}, col {exc.colno})")
                continue
            if isinstance(parsed, dict):
                return parsed
            errors.append(f"Expected JSON object, got {type(parsed).__name__}")

        snippet = text[:240].replace("\n", " ")
        raise LLMResponseFormatError(
            f"Unable to parse JSON object from response. Snippet: {snippet!r}. "
            f"Errors: {errors[:2]}"
        )
