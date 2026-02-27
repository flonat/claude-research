# cli-council

Local multi-model council deliberation using CLI tools. Runs Gemini CLI, Codex CLI, and Claude Code in parallel to get diverse AI perspectives on any question — using your existing subscriptions, not per-token API costs.

Part of [claude-code](https://github.com/user/claude-code-public) infrastructure.

## How It Works

Three-stage deliberation protocol (inspired by [Karpathy's llm-council](https://github.com/karpathy/llm-council)):

1. **Stage 1: Independent Assessments** — Each CLI tool independently answers the same question in parallel
2. **Stage 2: Anonymised Peer Review** — Each tool reviews all assessments (anonymised as "Assessment A/B/C") and ranks them
3. **Stage 3: Chairman Synthesis** — One tool reads everything and produces a single synthesised answer

## Prerequisites

Install the CLI tools you want to use:

| Backend | Install | Auth |
|---------|---------|------|
| **Gemini CLI** | `npm install -g @google/generative-ai-cli` | `gemini` (Google account) |
| **Codex CLI** | `npm install -g @openai/codex-cli` | `codex login` (ChatGPT Plus) |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | `claude` (Claude Pro) |

Check availability:

```bash
python -m cli_council --check
```

## Usage

### CLI

```bash
# Simple question
python -m cli_council "What are the tradeoffs between microservices and monoliths?"

# With context file and markdown output
python -m cli_council \
    --prompt-file question.txt \
    --context-file project-context.md \
    --output-md council-report.md

# Pipe from stdin
echo "Review this research design for causal identification issues" | python -m cli_council

# Select specific backends
python -m cli_council --backends gemini,claude "Best approach for time-series forecasting?"

# Change chairman
python -m cli_council --chairman codex "Evaluate this argument..."
```

### Python API

```python
import asyncio
from cli_council import CouncilRunner

runner = CouncilRunner(
    backends=["gemini", "codex", "claude"],
    chairman="claude",
)

result = asyncio.run(runner.run(
    "What are the key risks in this experimental design?",
    system_context="We're studying the effect of AI assistance on decision quality...",
))

print(result.synthesis)
for a in result.assessments:
    print(f"{a.label} ({a.backend}): {a.text[:100]}...")
print(f"Total time: {result.meta.total_ms}ms")
```

## Output

Returns a `CouncilResult` with:

- `synthesis` — Chairman's final synthesised answer
- `assessments` — List of individual Stage 1 responses
- `peer_reviews` — List of Stage 2 peer reviews with rankings
- `meta` — Timing, backends used, errors

## Relationship to claude-llm-council

| | cli-council | [claude-llm-council](https://github.com/user/claude-llm-council) |
|---|---|---|
| **Transport** | Local CLI subprocesses | OpenRouter API |
| **Cost** | Subscription-included | Per-token |
| **Output** | Free-form text | Structured JSON |
| **Best for** | Ad-hoc reviews, research, quick opinions | Automated pipelines, structured reports |
| **Models** | Whatever your CLIs support | Full OpenRouter catalogue |

Both implement the same 3-stage protocol. Use cli-council for interactive work, claude-llm-council for programmatic integration.

## License

MIT
