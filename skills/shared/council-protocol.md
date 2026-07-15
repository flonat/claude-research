# Portable Council Protocol

Council mode is an optional multi-model review workflow. The public distribution
does not assume access to any private package, local model subscription, or
machine-specific checkout.

## Supported backend

The repository includes the source of `council-api`. Install it explicitly with
`uv tool install ./packages/council-api`, then verify the command with
`council-api --help`. A council run requires `OPENROUTER_API_KEY`; treat it as a
paid external call and obtain the user's approval before running it.

Provider CLIs may be used only when the user has separately installed and
authenticated them. They are optional integrations, never implicit fallbacks.

## Protocol

1. Run the consumer's local hard gates before spending on model calls.
2. Build one system prompt and one artifact/context file for every reviewer.
3. Obtain independent assessments from at least two distinct models.
4. Ask each model to review the anonymised assessments.
5. Ask a chairman model to synthesise agreements, disputes, and priorities.
6. Preserve the consumer's normal report format and append council metadata.

Example:

```bash
council-api \
  --system-prompt-file /tmp/council-system.txt \
  --user-message-file /tmp/council-context.txt \
  --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
  --chairman "anthropic/claude-sonnet-4.5" \
  --output /tmp/council-result.json
```

If fewer than two independent assessments succeed, stop and report a degraded
run. Never substitute a paid backend silently.
