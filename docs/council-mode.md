<!-- Governed by: skills/shared/project-documentation.md -->

# Council mode

Claude Code or Codex can invoke other model providers' CLI tools as subprocess
reviewers. A different model then reviews the work, providing architectural
diversity through different training data, reasoning patterns, and blind spots.
The system is extensible: any CLI tool that accepts a prompt and returns text
can be wrapped as a backend.

Council mode coordinates this into a structured three-stage protocol:
independent assessments, anonymised cross-review, then chair synthesis. It is
used by the `paper-critic` agent and can be called from skills such as
`proofread`, `devils-advocate`, `code-review`, and `multi-perspective`.

See `skills/shared/council-protocol.md` for the full orchestration protocol.

## CLI reviewers

The framework does not bundle a subscription-backed council CLI. Individual
workflows may call an installed model CLI when their availability row declares
that dependency. Treat those executables as optional external integrations:
preflight them before use, do not silently substitute a paid API, and fall back
to the current client or a single explicitly chosen reviewer when unavailable.

## Bundled API council (`packages/council-api/`)

Uses OpenRouter for structured JSON output and programmatic integration:

```bash
cd packages/council-api
uv run python -m council_api --help
```

The API package requires a compatible provider credential, commonly an
[OpenRouter](https://openrouter.ai/) key. Keep the credential in your operating
system's secret store or environment, never in this repository. See the
package's `README.md` for current providers and the Python API.
