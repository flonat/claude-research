# LLM Council

A Python package for multi-model LLM deliberation via OpenRouter. Orchestrates independent assessments from multiple AI models, conducts anonymous peer review, and synthesises consensus through a chairman model.

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

Generic async LLM client for OpenRouter.

```python
client = LLMClient(
    api_key: str,                    # OpenRouter API key
    model: str = "anthropic/claude-sonnet-4.5",  # Default model
    max_tokens: int = 4096,          # Max completion tokens
    json_retry_attempts: int = 2,    # Retries on JSON parse failure
)
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `chat_json(system, user_msg, *, model=None)` | `dict` | Send message, parse JSON response (with retries) |
| `chat_text(system, user_msg, *, model=None)` | `str` | Send message, return raw text |
| `close()` | `None` | Close the async HTTP client |

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

The `config` module provides model registry management and pricing.

```python
from llm_council.config import (
    AVAILABLE_MODELS,          # Default model list (18 models)
    ALLOWED_PROVIDERS,         # {"anthropic", "openai", "google"}
    COUNCIL_DEFAULT_MODELS,    # Default 3 council members
    COUNCIL_DEFAULT_CHAIRMAN,  # Default chairman model
    model_display_name,        # model_id -> human name
    fetch_model_pricing,       # Enrich models with live OpenRouter pricing
    fetch_all_provider_models, # Discover all models from allowed providers
    load_models,               # Load saved model list from JSON file
    save_models,               # Persist model list to JSON file
)
```

### Default Models (18 total)

| Provider | Models |
|----------|--------|
| **Anthropic** (5) | Claude Haiku 4.5, Sonnet 4.5, Sonnet 4.6, Opus 4.5, Opus 4.6 |
| **OpenAI** (7) | GPT-4.1 Mini, GPT-4.1, GPT-5 Mini, GPT-5, GPT-5.2, o3, o4 Mini |
| **Google** (6) | Gemini 2.5 Flash, 2.5 Pro, 3 Flash, 3 Pro, 3.1 Pro |

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

```bash
python -m llm_council \
    --system-prompt "You are a reviewer. Return JSON: {score: int, summary: str}" \
    --user-message "Review: ..." \
    --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
    --chairman "anthropic/claude-sonnet-4.5" \
    --output result.json
```

Or from files:

```bash
python -m llm_council \
    --system-prompt-file system.txt \
    --user-message-file user.txt \
    --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
    --chairman "anthropic/claude-sonnet-4.5"
```

**Environment:** Requires `OPENROUTER_API_KEY`.

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

- **OpenRouter, not direct APIs** — single API key accesses Anthropic, OpenAI, and Google models. No need for 3 separate accounts.
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

- [Claude Topic Finder](https://github.com/user/claude-topic-finder) — research topic discovery app that uses this package for multi-model council deliberation
