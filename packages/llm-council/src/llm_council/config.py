"""Model registry and council defaults."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

ALLOWED_PROVIDERS = {"anthropic", "openai", "google"}

AVAILABLE_MODELS: list[dict[str, str]] = [
    # Anthropic
    {"id": "anthropic/claude-haiku-4.5", "name": "Claude Haiku 4.5", "tier": "fast, cheap"},
    {"id": "anthropic/claude-sonnet-4.5", "name": "Claude Sonnet 4.5", "tier": "balanced"},
    {"id": "anthropic/claude-sonnet-4.6", "name": "Claude Sonnet 4.6", "tier": "balanced, latest"},
    {"id": "anthropic/claude-opus-4.5", "name": "Claude Opus 4.5", "tier": "most capable"},
    {"id": "anthropic/claude-opus-4.6", "name": "Claude Opus 4.6", "tier": "most capable, latest"},
    # OpenAI
    {"id": "openai/gpt-4.1-mini", "name": "GPT-4.1 Mini", "tier": "fast, cheap"},
    {"id": "openai/gpt-4.1", "name": "GPT-4.1", "tier": "balanced"},
    {"id": "openai/gpt-5-mini", "name": "GPT-5 Mini", "tier": "fast"},
    {"id": "openai/gpt-5", "name": "GPT-5", "tier": "balanced, latest"},
    {"id": "openai/gpt-5.2", "name": "GPT-5.2", "tier": "most capable, latest"},
    {"id": "openai/o3", "name": "o3", "tier": "reasoning"},
    {"id": "openai/o4-mini", "name": "o4 Mini", "tier": "reasoning, cheap"},
    # Google
    {"id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash", "tier": "fast, cheap"},
    {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tier": "balanced"},
    {"id": "google/gemini-3-flash-preview", "name": "Gemini 3 Flash", "tier": "fast, latest"},
    {"id": "google/gemini-3-pro-preview", "name": "Gemini 3 Pro", "tier": "balanced, latest"},
    {"id": "google/gemini-3.1-pro-preview", "name": "Gemini 3.1 Pro", "tier": "most capable, latest"},
]

# Built-in defaults (used when no user config exists)
_BUILTIN_DEFAULT_MODELS: list[str] = [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-5",
    "google/gemini-2.5-pro",
]

_BUILTIN_DEFAULT_CHAIRMAN: str = "anthropic/claude-sonnet-4.5"

# User config file
USER_CONFIG_PATH = Path.home() / ".config" / "llm-council" / "config.json"


def _load_user_config() -> dict | None:
    """Load user config from ~/.config/llm-council/config.json."""
    if not USER_CONFIG_PATH.exists():
        return None
    try:
        return json.loads(USER_CONFIG_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        logger.warning("Could not parse %s — using built-in defaults", USER_CONFIG_PATH)
        return None


def get_council_defaults() -> list[str]:
    """Return council default models (user config > built-in)."""
    cfg = _load_user_config()
    if cfg and "council_models" in cfg:
        return cfg["council_models"]
    return list(_BUILTIN_DEFAULT_MODELS)


def get_chairman_default() -> str:
    """Return chairman default model (user config > built-in)."""
    cfg = _load_user_config()
    if cfg and "chairman" in cfg:
        return cfg["chairman"]
    return _BUILTIN_DEFAULT_CHAIRMAN


def set_council_defaults(
    models: list[str] | None = None,
    chairman: str | None = None,
) -> dict:
    """Persist council defaults to user config. Returns the saved config."""
    cfg = _load_user_config() or {}
    if models is not None:
        cfg["council_models"] = models
    if chairman is not None:
        cfg["chairman"] = chairman
    USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
    return cfg


def reset_council_defaults() -> None:
    """Remove user config, reverting to built-in defaults."""
    if USER_CONFIG_PATH.exists():
        USER_CONFIG_PATH.unlink()


# Public constants that resolve user config automatically
COUNCIL_DEFAULT_MODELS: list[str] = get_council_defaults()
COUNCIL_DEFAULT_CHAIRMAN: str = get_chairman_default()

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def model_display_name(model_id: str) -> str:
    """Human-readable name for a model ID."""
    names = {m["id"]: m["name"] for m in AVAILABLE_MODELS}
    return names.get(model_id, model_id.split("/")[-1])


def _auto_tier(input_price_per_m: float) -> str:
    if input_price_per_m < 0.5:
        return "fast, cheap"
    if input_price_per_m < 3.0:
        return "balanced"
    return "most capable"


def load_models(path: str | Path) -> list[dict[str, str]] | None:
    """Load saved models from a JSON file. Returns None if file missing."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        return data.get("models", [])
    except (json.JSONDecodeError, KeyError):
        logger.warning("Could not parse %s — falling back to defaults", path)
        return None


def save_models(path: str | Path, models: list[dict[str, str]]) -> None:
    """Persist the active model list to a JSON file."""
    cleaned = [
        {"id": m["id"], "name": m["name"], "tier": m.get("tier", "")}
        for m in models
    ]
    Path(path).write_text(json.dumps({"models": cleaned}, indent=2) + "\n")


async def _fetch_openrouter_data() -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPENROUTER_MODELS_URL)
            resp.raise_for_status()
            return resp.json().get("data", [])
    except Exception:
        logger.warning("Could not reach OpenRouter API")
        return None


def _enrich_with_pricing(
    models: list[dict[str, str]], or_data: list[dict],
) -> list[dict[str, str]]:
    price_map: dict[str, dict[str, str]] = {}
    for entry in or_data:
        mid = entry.get("id", "")
        pricing = entry.get("pricing", {})
        try:
            inp = float(pricing.get("prompt", "0")) * 1_000_000
            out = float(pricing.get("completion", "0")) * 1_000_000
            price_map[mid] = {
                "input_price": f"${inp:.2f}",
                "output_price": f"${out:.2f}",
            }
        except (ValueError, TypeError):
            price_map[mid] = {"input_price": "N/A", "output_price": "N/A"}

    enriched = []
    for m in models:
        m2 = m.copy()
        prices = price_map.get(m2["id"], {})
        m2["input_price"] = prices.get("input_price", "N/A")
        m2["output_price"] = prices.get("output_price", "N/A")
        m2["provider"] = m2["id"].split("/")[0]
        enriched.append(m2)
    return enriched


async def fetch_model_pricing(
    base_models: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Fetch pricing from OpenRouter and merge into a model list."""
    models = [m.copy() for m in (base_models or AVAILABLE_MODELS)]
    or_data = await _fetch_openrouter_data()
    if or_data is None:
        for m in models:
            m.setdefault("input_price", "N/A")
            m.setdefault("output_price", "N/A")
            m.setdefault("provider", m["id"].split("/")[0])
        return models
    return _enrich_with_pricing(models, or_data)


async def fetch_all_provider_models() -> list[dict[str, str]]:
    """Fetch ALL models from allowed providers via OpenRouter."""
    or_data = await _fetch_openrouter_data()
    if or_data is None:
        return []

    models: list[dict[str, str]] = []
    for entry in or_data:
        mid = entry.get("id", "")
        provider = mid.split("/")[0] if "/" in mid else ""
        if provider not in ALLOWED_PROVIDERS:
            continue

        pricing = entry.get("pricing", {})
        try:
            inp = float(pricing.get("prompt", "0")) * 1_000_000
            out = float(pricing.get("completion", "0")) * 1_000_000
        except (ValueError, TypeError):
            inp, out = 0.0, 0.0

        raw_name = entry.get("name", mid)
        for prefix in ("Anthropic: ", "OpenAI: ", "Google: "):
            if raw_name.startswith(prefix):
                raw_name = raw_name[len(prefix):]
                break

        models.append({
            "id": mid,
            "name": raw_name,
            "tier": _auto_tier(inp),
            "provider": provider,
            "input_price": f"${inp:.2f}",
            "output_price": f"${out:.2f}",
        })

    models.sort(key=lambda m: (m["provider"], m["name"]))
    return models
