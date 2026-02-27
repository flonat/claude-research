# karpathy/llm-council — Review

> Reviewed 2026-02-25. Repo: https://github.com/karpathy/llm-council (Karpathy "Saturday hack")

## What It Does

Multi-model council that answers questions in 3 stages:
1. **Stage 1 — Individual responses**: Query all council members (4 models) in parallel via OpenRouter
2. **Stage 2 — Peer review**: Each model ranks all other responses (anonymised as "Response A/B/C/D"), parses `FINAL RANKING:` section
3. **Stage 3 — Chairman synthesis**: A designated chairman model synthesises all responses + rankings into a final answer

## Architecture

- **Backend**: FastAPI + httpx (async OpenRouter calls) + JSON file storage
- **Frontend**: React + Vite (separate app)
- **API**: OpenRouter only (same as our Topic Finder migration)
- **Config**: `COUNCIL_MODELS` list + `CHAIRMAN_MODEL` in `config.py`
- **Streaming**: SSE endpoint streams stage completions to frontend
- Dependencies: `fastapi`, `httpx`, `pydantic`, `uvicorn`, `python-dotenv`

## Key Design Choices

- Anonymous peer review: models see "Response A/B/C" not model names — prevents brand-bias
- Parallel queries via `asyncio.gather` — all models queried simultaneously
- Aggregate rankings: Borda-count-style average position across all reviewers
- Chairman can be any model (default: Gemini 3 Pro)
- Regex parsing of `FINAL RANKING:` section — fragile but works

## What's Good

- Clean separation: `openrouter.py` (API client) → `council.py` (orchestration) → `main.py` (routes)
- Parallel execution throughout — fast despite 4+ model calls per stage
- SSE streaming so frontend shows progressive results
- Anonymisation prevents model-name bias in peer review

## Weaknesses

- No system prompts — all queries are bare user messages
- JSON file storage — no DB, no caching
- `FINAL RANKING:` parsing is fragile (regex on free-form text)
- No retry logic on model failures
- No cost tracking or token counting
- Fixed council membership — no per-query model selection
- No conversation context (each turn is independent, no history passed)

## Relevance for Topic Finder

Core 3-stage pattern is directly reusable:
1. Query N models with the same prompt (research idea to evaluate)
2. Each model reviews/ranks the other responses (anonymised)
3. Chairman synthesises into a consensus evaluation

Key adaptations needed:
- Domain-specific system prompts (research novelty/framing context, not general Q&A)
- Use structured JSON output (Pydantic models) instead of free-form markdown
- Integrate with existing OpenRouter client (`LLMService`) rather than raw httpx
- Store results in SQLite (existing pattern) not JSON files
- HTMX partial rendering, not React SPA
