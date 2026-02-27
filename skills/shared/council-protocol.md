# Council Protocol

> Shared protocol for multi-model council mode. Any review agent or skill can opt into this by providing domain-specific system prompts and output formatting. This file defines the generic orchestration flow.
>
> **Included backend:** `cli-council` (local CLI tools, free with existing subscriptions). An optional API backend (`llm-council` via OpenRouter) is available separately — see below.

## What Council Mode Is

Instead of a single reviewer, council mode runs a 3-stage deliberation across **multiple LLM providers** (Claude, GPT, Gemini):

1. **Stage 1: Independent Assessments** — N models (typically 3, each from a different provider) independently evaluate the same artifact using the same instructions
2. **Stage 2: Anonymised Peer Review** — each model evaluates the others' assessments without knowing which model produced which
3. **Stage 3: Chairman Synthesis** — a chairman model reads everything and produces the final report

The key insight: genuine model diversity (different architectures, training data, biases) surfaces issues that any single model — or even multiple instances of the same model — would miss.

## Infrastructure

### CLI Backend: `cli-council` (Included)

Package: `packages/cli-council/`

- `CouncilRunner` — orchestrator that calls `gemini -p`, `codex exec`, and `claude -p` via subprocess
- `GeminiBackend`, `CodexBackend`, `ClaudeBackend` — thin async wrappers around CLI tools
- `CouncilResult` — Pydantic models for text-based results
- CLI — `python -m cli_council` for standalone use
- Uses existing subscriptions (ChatGPT Plus, Gemini, Claude Pro) — no per-token API costs
- **Best for:** Ad-hoc reviews, research tasks, quick multi-perspective opinions

### API Backend: `llm-council` (Optional, Separate Install)

> Not included in this repo. Install separately: `pip install llm-council` or clone from GitHub.

- `LLMClient` — generic async OpenRouter client with JSON/text chat and retry logic
- `CouncilService` — 3-stage orchestration engine with customisable Stage 2/3 prompts
- `CouncilResult` — Pydantic models for structured JSON results
- CLI — `python -m llm_council` for standalone use
- Requires `OPENROUTER_API_KEY` in the environment
- **Best for:** Automated pipelines, structured JSON output, programmatic integration

### Choosing a Backend

| Factor | `cli-council` (included) | `llm-council` (separate) |
|--------|--------------------------|--------------------------|
| Cost | Subscription-included | Per-token (OpenRouter) |
| Output format | Free-form text | Structured JSON |
| Reliability | Variable (CLI output parsing) | High (API contracts) |
| Speed | Slower (subprocess overhead) | Fast (parallel async HTTP) |
| Model control | Whatever CLIs support | Full OpenRouter catalogue |
| Offline | Partially (Claude -p works offline) | No |

**Default:** Use `cli-council` (included and free). Use `llm-council` only if you need structured JSON output or are running in an automated pipeline.

## When to Use

- Pre-submission quality checks (high stakes)
- When thoroughness matters more than speed
- When the user explicitly requests "council mode", "council review", or "thorough review"
- Never the default — standard single-reviewer mode remains the default for all consumers

## Prerequisites for a Consumer

An agent or skill that supports council mode must provide:

| What | Where | Purpose |
|------|-------|---------|
| **System prompt builder** | Consumer's `references/council-personas.md` | How to construct the system prompt sent to all models |
| **Output formatter** | Consumer's `references/council-prompts.md` | Stage 3 chairman prompt template + output format |
| **Council mode section** | Consumer's agent/skill body | Short section noting support + pointer to reference files |
| **Trigger phrases** | Consumer's frontmatter description/examples | How the user activates council mode |

## Orchestration Protocol

The **main session** orchestrates council mode. Review agents cannot orchestrate themselves (they lack Bash). When council mode is triggered:

### Pre-flight

1. Run the consumer's standard pre-checks and hard gates
2. If any gate fails, report immediately — do not invoke the council (save cost)
3. Collect all source material (file contents, logs, rubrics) into a system prompt and user message
4. Read the consumer's reference files for prompt construction guidance

### Stage 1: Independent Assessments

The main session invokes the `llm-council` package (via CLI or Python script). The library:

1. Sends the system prompt + user message to N different LLM models via OpenRouter
2. Each model independently produces a JSON assessment
3. All calls are parallel (async)
4. Failed models are logged and skipped — the council proceeds with available responses

**Default models:** `anthropic/claude-sonnet-4.5`, `openai/gpt-5`, `google/gemini-2.5-pro`

### Stage 2: Anonymised Peer Review

The library automatically:

1. Labels Stage 1 assessments as "Assessment A", "Assessment B", etc. (anonymised)
2. Sends all assessments to each model for cross-evaluation
3. Each model evaluates the others' work, identifies agreements/disagreements, and provides a ranking
4. Rankings are parsed and aggregated

**Model:** Same models as Stage 1 (each reviews the others' work).

### Stage 3: Chairman Synthesis

The library:

1. Sends all assessments and peer reviews to the chairman model
2. The chairman considers all inputs and produces a single synthesised response
3. The response follows the consumer's required output schema

**Default chairman:** `anthropic/claude-sonnet-4.5`

### Write Output

The main session receives the `CouncilResult` JSON and formats it into the consumer's standard output (e.g., `CRITIC-REPORT.md` for paper-critic). The report uses the consumer's standard format with two sections appended:

```markdown
## Council Notes

### Agreement Summary
- [N] issues confirmed by all reviewers
- [N] issues confirmed by majority
- [N] issues from single reviewer (validated in cross-review)
- [N] disputed issues (marked [DISPUTED])

### Aggregate Rankings
| Assessment | Model | Avg Rank | Rankings Count |
|------------|-------|----------|----------------|
| Assessment A | [model name] | X.X | N |
| Assessment B | [model name] | X.X | N |
| Assessment C | [model name] | X.X | N |

## Council Metadata
- **Mode:** Council ([N] models + peer review + chairman)
- **Models:** [list of model IDs used]
- **Chairman:** [chairman model ID]
- **Timing:** Stage 1: Xms, Stage 2: Xms, Stage 3: Xms, Total: Xms
- **Date:** YYYY-MM-DD
```

These sections are appended **after** the consumer's standard report content. Downstream consumers (e.g., fixer agent) that parse only the standard sections are unaffected.

## CLI Invocation

### Option A: CLI Backend (`cli-council` — Included)

For ad-hoc reviews using existing subscriptions (no API cost):

```bash
cd "packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/council-prompt.txt \
    --context-file /tmp/council-context.txt \
    --output /tmp/council-result.json \
    --output-md /tmp/council-report.md \
    --chairman claude \
    --timeout 180
```

- Write the paper content / review instructions to `--context-file`, and the specific question to `--prompt-file`
- Output is free-form text — the markdown report (`--output-md`) is usually more useful than JSON
- The chairman backend defaults to `claude` (since we're already in Claude Code)

### Option B: API Backend (`llm-council` — Separate Install)

> Requires separate installation: `pip install llm-council` and an `OPENROUTER_API_KEY`.

For structured JSON output and automated pipelines:

```bash
uv run python -m llm_council \
    --system-prompt-file /tmp/council-system.txt \
    --user-message-file /tmp/council-user.txt \
    --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
    --chairman "anthropic/claude-sonnet-4.5" \
    --output /tmp/council-result.json
```

For advanced cases (custom Stage 2/3 prompts), write a small Python script that imports `llm_council` and calls `CouncilService.run_council()` with `stage2_system` and `stage3_prompt_builder` parameters.

## Issue Resolution Rules (Chairman)

The consumer's chairman prompt should instruct the chairman to apply these rules:

| Situation | Action |
|-----------|--------|
| Issue confirmed by 2+ models | Retain at the **highest** agreed severity |
| Issue from 1 model, validated in peer review | Retain at the original severity |
| Issue from 1 model, disputed in peer review | Retain with `[DISPUTED]` tag; chairman makes final severity call |
| Issue found only in peer review (missed initially) | Add as a new finding |
| Conflicting severity assessments | Chairman decides; notes the range in the issue description |

**Scoring:** The chairman produces an independent score informed by all inputs — not a mechanical average.

## Model Configuration

| Parameter | Default | Override |
|-----------|---------|---------|
| Stage 1 models | `anthropic/claude-sonnet-4.5`, `openai/gpt-5`, `google/gemini-2.5-pro` | `--models` CLI flag |
| Chairman model | `anthropic/claude-sonnet-4.5` | `--chairman` CLI flag |
| Max tokens | 4096 | `--max-tokens` CLI flag |

The library's `config.py` contains the full model registry with tiers and pricing.

## Cost Considerations

Council mode costs significantly more than standard mode because it calls N models for Stage 1, N models for Stage 2, and 1 model for Stage 3 (total: 2N+1 API calls). With 3 models:

- **Standard mode:** 1 agent call (free — uses Claude Code context)
- **Council mode:** 7 OpenRouter API calls (3 + 3 + 1)

Pricing depends on the models chosen. Check OpenRouter for current rates. Use council mode when thoroughness justifies the cost — typically pre-submission or high-stakes reviews.

## Persona Support (Optional)

Each consumer can define **personas** in `references/council-personas.md` — distinct reviewer emphases that are prepended to the system prompt. Since council mode already uses different LLM providers (which bring natural perspective diversity), personas are optional but can add further differentiation.

Current approach: the same system prompt goes to all models. Personas are documented as reference material describing what each model *tends to focus on* based on its architecture. Future extension: per-model system prompt variants via the library's API.

## Consumers

| Consumer | CLI (`cli-council`) | API (`llm-council`) | Notes |
|----------|---------------------|---------------------|-------|
| `paper-critic` | Supported | Implemented | First consumer — Technical Rigour, Presentation, Scholarly Standards personas |
| `referee2-reviewer` | Supported | Supported | 5-audit protocol + council cross-review — highest-value consumer |
| `domain-reviewer` | Supported | — | Math/assumption checking — different models catch different derivation gaps |
| `proposal-reviewer` | Supported | — | Feasibility and novelty — different models have different domain knowledge |
| `peer-reviewer` | Supported | — | Full paper review — the canonical use case for multi-model deliberation |
| `multi-perspective` | Supported | — | Replaces Claude-only sub-agents with genuine model diversity |
| `literature` | Implemented | — | Phase 2b (search) and Phase 7 (synthesis) — see skill definition |
| `devils-advocate` | Supported | — | Round 1/2/3 played by different models for genuine adversarial tension |
| `proofread` | Supported | — | Lower value — most useful for notation consistency and citation voice balance |
| `code-review` | Supported | — | Most valuable for domain correctness and cross-language verification |
| `validate-bib` | Supported | — | Different models have different bibliographic knowledge — catches metadata mismatches |
