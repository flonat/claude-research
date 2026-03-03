<!-- Governed by: skills/shared/project-documentation.md -->

# Council Mode

Claude Code can invoke other LLM providers' CLI tools as subprocess reviewers — a different model reviews work that Claude produced, providing genuine architectural diversity (different training data, reasoning patterns, and blind spots). The system is extensible: any CLI tool that accepts a prompt and returns text can be wrapped as a backend (~20 lines of Python).

Council mode coordinates this into a structured 3-stage protocol: independent assessments from multiple LLM providers, anonymised cross-review, then chairman synthesis. Used by the `paper-critic` agent and optionally by `/proofread`, `/devils-advocate`, `/code-review`, and `/multi-perspective`.

See `skills/shared/council-protocol.md` for the full orchestration protocol.

## CLI Council (`packages/cli-council/`) — Free

Uses local CLI tools with existing subscriptions (no per-token cost). Backends are pluggable — adding a new provider follows the `BackendSpec` pattern:

```bash
cd packages/cli-council
pip install -e .
python -m cli_council --check  # verify which CLI backends are available
```

Currently available backends:
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — `npm install -g @google/gemini-cli`
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — useful for fresh context (same model, different session)
- Additional backends can be added by implementing a `BackendSpec` in `config.py` and a thin async wrapper in `backends/`

## LLM Council (`packages/llm-council/`) — API

Uses OpenRouter for structured JSON output and programmatic integration:

```bash
cd packages/llm-council
pip install -e .
export OPENROUTER_API_KEY="sk-or-..."  # get one at https://openrouter.ai/keys
```

Requires an [OpenRouter](https://openrouter.ai/) account. One API key accesses Anthropic, OpenAI, and Google models. A council run (3 models) costs ~7 API calls. See the package's `README.md` for the full Python API reference.
