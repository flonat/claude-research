# LLM Council

A Python package for multi-model LLM deliberation. Orchestrates independent assessments from multiple AI models, conducts anonymous peer review, and synthesises consensus through a chairman model.

Routes across **OpenRouter, OpenAI, Anthropic, Gemini, and Mistral** via OpenAI-compatible endpoints — use a single OpenRouter key for everything, or mix native provider keys.

## The 3-Stage Protocol

```
Stage 1: Individual Assessments (parallel)
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Claude   │  │ GPT-5   │  │ Gemini  │
│ Sonnet   │  │         │  │ 2.5 Pro │
└────┬─────┘  └────┬────┘  └────┬────┘
     │             │             │
     ▼             ▼             ▼
  Result A      Result B      Result C
  (JSON)        (JSON)        (JSON)

Stage 2: Peer Review (parallel)
Each model reviews ALL assessments anonymously
┌────────────────────────────────────────┐
│  "Assessment A is comprehensive but    │
│   misses X. Assessment C handles Y     │
│   better than B..."                    │
│                                        │
│  FINAL RANKING:                        │
│  1. Assessment C                       │
│  2. Assessment A                       │
│  3. Assessment B                       │
└────────────────────────────────────────┘
Rankings are aggregated across all reviewers

Stage 3: Chairman Synthesis (single model)
┌────────────────────────────────────────┐
│  Chairman reviews all assessments +    │
│  all peer reviews, then produces a     │
│  single synthesised result in the      │
│  same JSON schema as Stage 1           │
└────────────────────────────────────────┘
```

**Why this works:**
- Multiple models catch each other's blind spots
- Anonymous peer review prevents model-name bias
- Aggregate rankings surface the best reasoning regardless of source
- Chairman synthesis resolves disagreements using the full deliberation record

## Installation

```bash
pip install "llm-council @ git+https://github.com/user/llm-council.git"
```

Requires Python 3.11+.

## Quick Start

```python
import asyncio
from llm_council import LLMClient, CouncilService

async def main():
    client = LLMClient(
        api_key="sk-or-...",  # OpenRouter API key
        model="anthropic/claude-sonnet-4.5",
    )
    council = CouncilService(llm=client)

    result = await council.run_council(
        system_prompt="You are a research paper reviewer. Return JSON with: overall_score (1-10), strengths (list), weaknesses (list), recommendation (string).",
        user_msg="Review this paper abstract: ...",
        council_models=[
            "anthropic/claude-sonnet-4.5",
            "openai/gpt-5",
            "google/gemini-2.5-pro",
        ],
        chairman_model="anthropic/claude-sonnet-4.5",
    )

    print(f"Consensus score: {result.final_result['overall_score']}")
    print(f"Council ranked: {[r['model_name'] for r in result.meta.aggregate_rankings]}")
    print(f"Total time: {result.meta.total_ms}ms")

    await client.close()

asyncio.run(main())
```

## API Reference

### LLMClient

Generic async LLM client supporting multiple providers.

```python
client = LLMClient(
    api_key: str | None = None,
    model: str = "anthropic/claude-sonnet-4.5",
    max_tokens: int = 4096,
    json_retry_attempts: int = 2,
    *,
    provider: str | None = None,     # "openrouter"|"openai"|"anthropic"|"gemini"|"mistral"
    base_url: str | None = None,     # Override the provider's base URL
)
```

**Provider resolution** (when `provider` is not set explicitly):

1. Model-prefix match — `anthropic/claude-*` → Anthropic if `ANTHROPIC_API_KEY` set
2. Priority fallback — OpenRouter > OpenAI > Anthropic > Gemini > Mistral (first available key)

Or use the `from_env()` factory for pure environment-driven auto-detection:

```python
client = LLMClient.from_env(model="anthropic/claude-opus-4-7")
# Honours LLM_PROVIDER (with REVIEW_PROVIDER fallback for back-compat)
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `chat_json(system, user_msg, *, model=None, max_tokens=None, reasoning_effort=None)` | `dict` | Send message, parse JSON response (with retries) |
| `chat_text(system, user_msg, *, model=None, max_tokens=None, reasoning_effort=None)` | `str` | Send message, return raw text |
| `close()` | `None` | Close the async HTTP client |

**Reasoning tokens** (`reasoning_effort` = `"low"` | `"medium"` | `"high"`) are mapped to each provider's native parameter:

| Provider | Parameter |
|----------|-----------|
| OpenRouter | `extra_body.reasoning.max_tokens` (budget computed from ratio) |
| Anthropic | `extra_body.thinking.budget_tokens` |
| OpenAI | `reasoning_effort` string |
| Gemini | `extra_body.thinking.budget_tokens` |
| Mistral | not supported (silently ignored) |

If reasoning consumes all output tokens (empty response), the client auto-retries up to 3 times with doubled `max_tokens`.

**JSON parsing** is robust — it tries three extraction strategies in order:
1. Parse the full response as JSON
2. Extract from markdown code fences (`` ```json ... ``` ``)
3. Extract the first `{...}` block

If all fail after retries, raises `LLMResponseFormatError`.

**Error handling** converts OpenRouter/OpenAI SDK errors into `LLMServiceError` with user-friendly messages:

| HTTP Status | Meaning | `LLMServiceError` message |
|-------------|---------|--------------------------|
| 401 | Bad API key | "Authentication failed" |
| 402 | No credits | "Insufficient credits" + help URL |
| 429 | Rate limited | "Rate limited — try again" |
| 503 | Model unavailable | "Model temporarily unavailable" |

### CouncilService

Orchestrates the 3-stage deliberation protocol.

```python
council = CouncilService(llm: LLMClient)

result = await council.run_council(
    system_prompt: str,          # System prompt for Stage 1 assessments
    user_msg: str,               # User message for Stage 1
    council_models: list[str],   # 3+ OpenRouter model IDs
    chairman_model: str,         # Model for Stage 3 synthesis
    *,
    # Optional:
    existing_result: dict | None = None,      # Reuse a prior result as one assessment
    existing_model: str | None = None,        # Which model produced existing_result
    stage2_system: str | None = None,         # Custom peer review prompt
    stage3_prompt_builder: Callable | None = None,  # Custom chairman prompt builder
)
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `system_prompt` | Yes | Defines the task and expected JSON output schema |
| `user_msg` | Yes | The content to evaluate (abstract, topic, code, etc.) |
| `council_models` | Yes | List of OpenRouter model IDs (minimum 3 recommended) |
| `chairman_model` | Yes | Model ID for final synthesis |
| `existing_result` | No | Skip Stage 1 for one model by reusing a prior JSON result |
| `existing_model` | No | Model ID that produced `existing_result` |
| `stage2_system` | No | Override the default peer review system prompt |
| `stage3_prompt_builder` | No | Callable `(assessments, peer_reviews, user_msg) -> str` |

**Returns:** `CouncilResult` (see [Data Models](#data-models)).

### Data Models

```python
from llm_council import (
    CouncilResult,
    CouncilAssessment,
    CouncilPeerReview,
    CouncilMeta,
)
```

#### CouncilResult

The complete output of a council deliberation.

```python
class CouncilResult(BaseModel):
    final_result: dict                      # Synthesised consensus (same schema as Stage 1)
    assessments: list[CouncilAssessment]    # All Stage 1 responses
    peer_reviews: list[CouncilPeerReview]   # All Stage 2 reviews
    meta: CouncilMeta                       # Timing, rankings, diagnostics
```

#### CouncilAssessment

A single model's Stage 1 response.

```python
class CouncilAssessment(BaseModel):
    model: str           # OpenRouter model ID (e.g., "anthropic/claude-sonnet-4.5")
    model_name: str      # Human-readable name (e.g., "Claude Sonnet 4.5")
    result_json: dict    # The structured JSON response
    label: str = ""      # Anonymised label ("Assessment A", "Assessment B", etc.)
```

#### CouncilPeerReview

A single model's Stage 2 peer review.

```python
class CouncilPeerReview(BaseModel):
    model: str                                   # Reviewer's model ID
    model_name: str                              # Human-readable name
    review_text: str                             # Free-form evaluation text
    parsed_ranking: list[str] = Field(default_factory=list)  # ["Assessment C", "Assessment A", ...]
```

#### CouncilMeta

Metadata and diagnostics.

```python
class CouncilMeta(BaseModel):
    council_models: list[str]                    # All participating model IDs
    chairman_model: str                          # Chairman model ID
    stage1_ms: int = 0                           # Stage 1 wall-clock time
    stage2_ms: int = 0                           # Stage 2 wall-clock time
    stage3_ms: int = 0                           # Stage 3 wall-clock time
    total_ms: int = 0                            # Total wall-clock time
    reused_model: str | None = None              # Model whose result was reused (if any)
    aggregate_rankings: list[dict] = Field(...)  # Sorted by average_rank
    stage3_fallback: bool = False                # True if chairman failed → used top assessment
```

**`aggregate_rankings`** — computed from all peer reviews:

```python
[
    {"label": "Assessment C", "model": "google/gemini-2.5-pro", "model_name": "Gemini 2.5 Pro", "average_rank": 1.0, "rankings_count": 3},
    {"label": "Assessment A", "model": "anthropic/claude-sonnet-4.5", "model_name": "Claude Sonnet 4.5", "average_rank": 2.0, "rankings_count": 3},
    {"label": "Assessment B", "model": "openai/gpt-5", "model_name": "GPT-5", "average_rank": 3.0, "rankings_count": 3},
]
```

## Configuration Module

The `config` module provides model registry management, user defaults, and pricing.

```python
from llm_council.config import (
    AVAILABLE_MODELS,          # Default model list (17 models)
    ALLOWED_PROVIDERS,         # {"anthropic", "openai", "google"}
    COUNCIL_DEFAULT_MODELS,    # Default 3 council members (resolves user config)
    COUNCIL_DEFAULT_CHAIRMAN,  # Default chairman model (resolves user config)
    model_display_name,        # model_id -> human name
    get_council_defaults,      # Get council models (user config > built-in)
    get_chairman_default,      # Get chairman model (user config > built-in)
    set_council_defaults,      # Persist council defaults to ~/.config/llm-council/
    reset_council_defaults,    # Revert to built-in defaults
    fetch_model_pricing,       # Enrich models with live OpenRouter pricing
    fetch_all_provider_models, # Discover all models from allowed providers
    load_models,               # Load saved model list from JSON file
    save_models,               # Persist model list to JSON file
)
```

### User Defaults

Council defaults are resolved in order: **user config** > **built-in defaults**.

```python
# Get current defaults (resolves user config automatically)
models = get_council_defaults()    # e.g., ["anthropic/claude-sonnet-4.6", ...]
chairman = get_chairman_default()  # e.g., "anthropic/claude-opus-4.5"

# Set and persist defaults
set_council_defaults(
    models=["anthropic/claude-sonnet-4.6", "openai/gpt-5", "google/gemini-3-pro-preview"],
    chairman="anthropic/claude-opus-4.5",
)
# Saved to ~/.config/llm-council/config.json

# Revert to built-in defaults
reset_council_defaults()
```

**Built-in defaults** (used when no user config exists):
- Models: `anthropic/claude-sonnet-4.5`, `openai/gpt-5`, `google/gemini-2.5-pro`
- Chairman: `anthropic/claude-sonnet-4.5`

### Available Models (17 total)

| Provider | Models |
|----------|--------|
| **Anthropic** (5) | Claude Haiku 4.5, Sonnet 4.5, Sonnet 4.6, Opus 4.5, Opus 4.6 |
| **OpenAI** (7) | GPT-4.1 Mini, GPT-4.1, GPT-5 Mini, GPT-5, GPT-5.2, o3, o4 Mini |
| **Google** (5) | Gemini 2.5 Flash, 2.5 Pro, 3 Flash, 3 Pro, 3.1 Pro |

### Live Pricing

```python
# Enrich the default model list with live pricing from OpenRouter
models = await fetch_model_pricing()
# Returns: [{"id": "...", "name": "...", "tier": "...", "input_price": "$3.00", "output_price": "$15.00", "provider": "anthropic"}, ...]

# Or discover ALL available models from allowed providers
all_models = await fetch_all_provider_models()
```

### Model Persistence

```python
# Save the current model selection to disk
save_models("models.json", models)

# Load it back (returns None if file missing)
loaded = load_models("models.json")
```

## Advanced Usage

### Reusing a Prior Result

If you already have a result from a single model and want to run a council review around it:

```python
# First, run a single-model analysis
single_result = await client.chat_json(system_prompt, user_msg)

# Then, run a council that reuses this result as one assessment
council_result = await council.run_council(
    system_prompt=system_prompt,
    user_msg=user_msg,
    council_models=["anthropic/claude-sonnet-4.5", "openai/gpt-5", "google/gemini-2.5-pro"],
    chairman_model="anthropic/claude-sonnet-4.5",
    existing_result=single_result,
    existing_model="anthropic/claude-sonnet-4.5",
)
# Stage 1 runs only for gpt-5 and gemini — claude's result is reused
# meta.reused_model == "anthropic/claude-sonnet-4.5"
```

### Custom Peer Review Prompt

```python
result = await council.run_council(
    ...,
    stage2_system="You are a domain expert reviewing research assessments. Focus on methodological rigour and citation accuracy. End with FINAL RANKING.",
)
```

### Custom Chairman Prompt Builder

```python
def my_chairman_prompt(assessments, peer_reviews, user_msg):
    return f"""
    Given these {len(assessments)} assessments and {len(peer_reviews)} peer reviews,
    synthesise a consensus. Prioritise methodological soundness.
    Original question: {user_msg}
    ...
    """

result = await council.run_council(
    ...,
    stage3_prompt_builder=my_chairman_prompt,
)
```

### Fallback Handling

If the chairman model fails (network error, malformed response), the council falls back to the top-ranked assessment from Stage 2:

```python
if result.meta.stage3_fallback:
    print("Warning: Chairman synthesis failed — using top-ranked assessment")
```

## CLI

### Run a Council

```bash
llm-council \
    --system-prompt "You are a reviewer. Return JSON: {score: int, summary: str}" \
    --user-message "Review: ..." \
    --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
    --chairman "anthropic/claude-sonnet-4.5" \
    --output result.json
```

Or from files:

```bash
llm-council \
    --system-prompt-file system.txt \
    --user-message-file user.txt
```

When `--models` and `--chairman` are omitted, the CLI uses your configured defaults (see below).

**Environment:** Requires `OPENROUTER_API_KEY`.

### Manage Models

```bash
# List available models and current defaults
llm-council models

# Include live OpenRouter pricing
llm-council models --pricing

# Set default council models
llm-council models --set-defaults "anthropic/claude-sonnet-4.6,openai/gpt-5,google/gemini-3-pro-preview"

# Set default chairman
llm-council models --set-chairman "anthropic/claude-opus-4.5"

# Reset to built-in defaults
llm-council models --reset
```

Defaults are persisted to `~/.config/llm-council/config.json` and used automatically when `--models`/`--chairman` are omitted.

## Dependencies

| Package | Purpose |
|---------|---------|
| `httpx>=0.27` | Async HTTP for OpenRouter pricing API |
| `openai>=1.0` | OpenAI SDK (used as OpenRouter client) |
| `pydantic>=2.0` | Data models and validation |

## Package Structure

```
llm_council/
├── __init__.py      # Public API exports
├── __main__.py      # CLI entry point
├── client.py        # LLMClient + error classes
├── models.py        # Pydantic models (CouncilResult, etc.)
├── config.py        # Model registry, pricing, defaults
└── council.py       # CouncilService (3-stage orchestration)
```

## Design Decisions

- **OpenRouter default, native providers available** — one `OPENROUTER_API_KEY` accesses all models. Pass `provider="anthropic"` (or set `LLM_PROVIDER=anthropic`) to route to native APIs when you want lower latency, larger context windows, or direct billing.
- **Schema-agnostic** — the council doesn't know what JSON schema you're using. It passes through whatever Stage 1 returns. Your application defines the schema via the system prompt.
- **Anonymous peer review** — assessments are labeled "Assessment A/B/C" during Stage 2. Model identities are only revealed in metadata.
- **Parallel execution** — Stage 1 and Stage 2 queries run concurrently via `asyncio.gather`. Wall-clock time is limited by the slowest model, not the sum.
- **Graceful degradation** — if a Stage 1 model fails, the council continues with the remaining assessments. If the chairman fails, it falls back to the top-ranked assessment.

## Cost Estimate

A council run with 3 models costs approximately **6-7x** a single-model call:
- Stage 1: 3 parallel calls (3x)
- Stage 2: 3 parallel reviews, each reviewing all assessments (3x, but shorter prompts)
- Stage 3: 1 chairman synthesis (1x)

## Related

- Used by downstream applications for multi-model council deliberation
