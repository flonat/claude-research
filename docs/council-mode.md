<!-- Governed by: skills/shared/project-documentation.md -->

# Council Mode

Two multi-model council backends run the same 3-stage protocol: independent assessments from 3 different LLM providers, anonymised cross-review, then chairman synthesis. Used by the `paper-critic` agent and optionally by `/proofread`, `/devils-advocate`, `/code-review`, and `/multi-perspective`.

See `skills/shared/council-protocol.md` for the full orchestration protocol.

## CLI Council (`packages/cli-council/`) — Free

Uses local CLI tools with existing subscriptions (no per-token cost):

```bash
cd packages/cli-council
pip install -e .
python -m cli_council --check  # verify CLI tools are installed
```

Requires [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Codex CLI](https://github.com/openai/codex), and [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed locally.

## LLM Council (`packages/llm-council/`) — API

Uses OpenRouter for structured JSON output and programmatic integration:

```bash
cd packages/llm-council
pip install -e .
export OPENROUTER_API_KEY="sk-or-..."  # get one at https://openrouter.ai/keys
```

Requires an [OpenRouter](https://openrouter.ai/) account. One API key accesses Anthropic, OpenAI, and Google models. A council run (3 models) costs ~7 API calls. See the package's `README.md` for the full Python API reference.
