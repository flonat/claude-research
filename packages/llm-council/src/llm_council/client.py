"""Multi-provider async LLM client.

OpenAI-compatible wrapper supporting OpenRouter, OpenAI, Anthropic, Gemini,
and Mistral. Provides structured JSON and raw text chat methods with retry
logic, reasoning-param unification, and empty-response handling.

Default behavior is OpenRouter (backward compatible with earlier versions).
To use a native provider, pass ``provider="anthropic"`` (or similar) or call
``LLMClient.from_env()`` for auto-detection.
"""

from __future__ import annotations

import json
import logging
import os
import re

import openai
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CREDITS_URL = "https://openrouter.ai/credits"

# Provider configs: env_var, base_url (None = OpenAI default), model-prefix-to-strip
PROVIDERS: dict[str, tuple[str, str | None, str | None]] = {
    "openrouter": ("OPENROUTER_API_KEY", OPENROUTER_BASE_URL, None),
    "openai": ("OPENAI_API_KEY", None, None),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/", "anthropic/"),
    "gemini": ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/", "google/"),
    "mistral": ("MISTRAL_API_KEY", "https://api.mistral.ai/v1", "mistralai/"),
}

# Auto-detection priority — OpenRouter first (broadest model access)
PROVIDER_PRIORITY = ["openrouter", "openai", "anthropic", "gemini", "mistral"]

# Model prefix → native provider (for model-aware auto-routing)
MODEL_VENDOR_TO_PROVIDER = {
    "anthropic/": "anthropic",
    "google/": "gemini",
    "mistralai/": "mistral",
    "openai/": "openai",
}

REASONING_EFFORT_RATIO = {
    "none": 0,
    "low": 0.1,
    "medium": 0.5,
    "high": 0.8,
}

EMPTY_RESPONSE_MAX_RETRIES = 3
EMPTY_RESPONSE_TOKEN_MULTIPLIER = 2


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


def _handle_openai_error(exc: Exception, provider: str = "openrouter") -> LLMServiceError:
    """Convert openai SDK exceptions into user-friendly LLMServiceError."""
    help_url = OPENROUTER_CREDITS_URL if provider == "openrouter" else None
    provider_display = provider.replace("_", " ").title()

    if isinstance(exc, openai.AuthenticationError):
        env_var = PROVIDERS.get(provider, (None,))[0] or "API_KEY"
        return LLMServiceError(
            f"Invalid {provider_display} API key. Please check your {env_var}.",
            help_url=help_url,
            detail=str(exc),
        )
    if isinstance(exc, openai.RateLimitError):
        return LLMServiceError(
            f"{provider_display} rate limit reached. Please wait a moment and try again.",
            help_url=help_url,
            detail=str(exc),
        )
    if isinstance(exc, openai.APIStatusError):
        status = getattr(exc, "status_code", None)
        if status == 402:
            return LLMServiceError(
                f"Insufficient {provider_display} credits. Please top up your account.",
                help_url=help_url,
                detail=str(exc),
            )
        if status == 503:
            return LLMServiceError(
                "The selected LLM model is temporarily unavailable. Try a different model.",
                detail=str(exc),
            )
        return LLMServiceError(
            f"{provider_display} API error (HTTP {status}). Please try again.",
            help_url=help_url,
            detail=str(exc),
        )
    if isinstance(exc, openai.APIConnectionError):
        return LLMServiceError(
            f"Could not connect to {provider_display}. Please check your internet connection.",
            detail=str(exc),
        )
    return LLMServiceError(
        "LLM request failed unexpectedly. Please try again.",
        detail=str(exc),
    )


def _resolve_provider(
    provider: str | None,
    model: str | None,
    api_key: str | None,
) -> tuple[str, str]:
    """Return (provider_name, api_key) by resolving explicit → env → model-prefix → priority."""
    if provider:
        name = provider.lower().strip()
        if name not in PROVIDERS:
            raise ValueError(f"Unknown provider '{provider}'. Available: {', '.join(PROVIDERS)}")
        env_var = PROVIDERS[name][0]
        key = api_key or os.environ.get(env_var)
        if not key:
            raise ValueError(f"Provider '{name}' selected but {env_var} is not set")
        return name, key

    # No explicit provider — model-aware auto-detect
    if model:
        for prefix, prov_name in MODEL_VENDOR_TO_PROVIDER.items():
            if model.startswith(prefix):
                env_var = PROVIDERS[prov_name][0]
                key = os.environ.get(env_var)
                if key:
                    return prov_name, key
                break  # prefix matched but key missing — fall through to priority

    # Priority fallback
    for name in PROVIDER_PRIORITY:
        env_var = PROVIDERS[name][0]
        key = os.environ.get(env_var)
        if key:
            return name, key

    raise ValueError(
        "No API key found. Set one of: "
        + ", ".join(PROVIDERS[p][0] for p in PROVIDER_PRIORITY)
    )


def _apply_reasoning(
    kwargs: dict,
    provider: str,
    reasoning_effort: str,
    max_tokens: int,
) -> None:
    """Add provider-specific reasoning/thinking parameters in place."""
    ratio = REASONING_EFFORT_RATIO.get(reasoning_effort, 0.5)
    budget = max(int(max_tokens * ratio), 1024)

    if provider == "openrouter":
        kwargs["extra_body"] = {"reasoning": {"max_tokens": budget}}
    elif provider == "anthropic":
        kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": budget}}
    elif provider == "openai":
        kwargs["reasoning_effort"] = reasoning_effort
    elif provider == "gemini":
        kwargs["extra_body"] = {"thinking": {"type": "enabled", "budget_tokens": budget}}
    # Mistral: no reasoning token support


class LLMClient:
    """Generic async LLM client supporting multiple providers.

    Default behavior matches the earlier OpenRouter-only client: passing only
    ``api_key`` and ``model`` works unchanged. Pass ``provider="anthropic"``
    (or similar) to route to a native API; model prefixes like
    ``"anthropic/"`` are stripped automatically for native endpoints.

    Use ``LLMClient.from_env()`` to auto-detect a provider from available
    environment variables.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "anthropic/claude-sonnet-4.5",
        max_tokens: int = 4096,
        json_retry_attempts: int = 2,
        *,
        provider: str | None = None,
        base_url: str | None = None,
    ) -> None:
        # Backward-compat default: if nothing is specified, assume OpenRouter
        if provider is None and base_url is None and api_key is not None:
            provider = "openrouter"

        resolved_provider, resolved_key = _resolve_provider(provider, model, api_key)

        env_var, default_base_url, prefix = PROVIDERS[resolved_provider]
        effective_base_url = base_url or default_base_url

        client_kwargs: dict = {"api_key": resolved_key}
        if effective_base_url:
            client_kwargs["base_url"] = effective_base_url

        self.client = AsyncOpenAI(**client_kwargs)
        self.provider = resolved_provider
        self.model = model
        self.max_tokens = max_tokens
        self.json_retry_attempts = max(1, json_retry_attempts)
        self._model_prefix = prefix

    @classmethod
    def from_env(
        cls,
        *,
        model: str | None = None,
        max_tokens: int = 4096,
        json_retry_attempts: int = 2,
        provider: str | None = None,
    ) -> LLMClient:
        """Build a client by auto-detecting provider + key from the environment.

        Resolution order:
          1. ``provider`` argument
          2. ``LLM_PROVIDER`` env var (falls back to ``REVIEW_PROVIDER``)
          3. Model-prefix match (e.g. ``anthropic/claude-*`` → Anthropic)
          4. First available key in priority order
        """
        resolved_provider = (
            provider
            or os.environ.get("LLM_PROVIDER")
            or os.environ.get("REVIEW_PROVIDER")
        )
        effective_model = model or "anthropic/claude-opus-4-7"
        return cls(
            api_key=None,
            model=effective_model,
            max_tokens=max_tokens,
            json_retry_attempts=json_retry_attempts,
            provider=resolved_provider,
        )

    def _api_model(self, model: str) -> str:
        """Strip vendor prefix for native-provider calls."""
        if self._model_prefix and model.startswith(self._model_prefix):
            return model[len(self._model_prefix):]
        return model

    async def _complete(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: list[dict],
        reasoning_effort: str | None,
    ) -> str:
        """Single completion call with empty-response retry on reasoning-consumed tokens."""
        current_max_tokens = max_tokens
        for _attempt in range(EMPTY_RESPONSE_MAX_RETRIES):
            kwargs: dict = {
                "model": self._api_model(model),
                "max_tokens": current_max_tokens,
                "messages": messages,
            }
            if reasoning_effort and reasoning_effort != "none":
                _apply_reasoning(kwargs, self.provider, reasoning_effort, current_max_tokens)

            try:
                response = await self.client.chat.completions.create(**kwargs)
            except (openai.APIError, openai.APIConnectionError) as api_exc:
                raise _handle_openai_error(api_exc, self.provider) from api_exc

            content = (response.choices[0].message.content or "").strip()
            if content:
                return content

            logger.warning(
                "Empty response from %s (reasoning may have consumed all tokens). "
                "Retrying with max_tokens=%d...",
                model, current_max_tokens * EMPTY_RESPONSE_TOKEN_MULTIPLIER,
            )
            current_max_tokens *= EMPTY_RESPONSE_TOKEN_MULTIPLIER

        logger.warning(
            "Empty response from %s after %d retries (max_tokens=%d)",
            model, EMPTY_RESPONSE_MAX_RETRIES, current_max_tokens,
        )
        return ""

    async def chat_json(
        self,
        system: str,
        user_msg: str,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        reasoning_effort: str | None = None,
    ) -> dict:
        """Send a message and parse a JSON-object response with retries.

        Parameters
        ----------
        max_tokens:
            Override the client's default ``max_tokens`` for this call.
        reasoning_effort:
            ``"low"``, ``"medium"``, ``"high"``, or ``None`` (default, no
            reasoning). Provider-specific mapping handled automatically.
        """
        effective_model = model or self.model
        effective_max_tokens = max_tokens or self.max_tokens
        prompt = user_msg + "\n\nRespond ONLY with valid JSON."
        raw_text = ""
        parse_error: Exception | None = None

        for attempt in range(1, self.json_retry_attempts + 1):
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ]
            raw_text = await self._complete(
                model=effective_model,
                max_tokens=effective_max_tokens,
                messages=messages,
                reasoning_effort=reasoning_effort,
            )

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
        reasoning_effort: str | None = None,
    ) -> str:
        """Query the LLM and return the raw text response (no JSON parsing)."""
        effective_model = model or self.model
        effective_max_tokens = max_tokens or self.max_tokens
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]
        return await self._complete(
            model=effective_model,
            max_tokens=effective_max_tokens,
            messages=messages,
            reasoning_effort=reasoning_effort,
        )

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
