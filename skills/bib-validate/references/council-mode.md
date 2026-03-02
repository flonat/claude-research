# Council Mode for Bibliography Validation

> For high-stakes submissions, run bibliography validation in council mode. Different models have different knowledge of the academic literature -- one model may know a paper's correct DOI while another catches a metadata mismatch that the first misses.

## When to Trigger

- "Council bib-validate"
- "Thorough bib check"

## How It Works

1. The main session collects all `\cite{}` keys and `.bib` entries
2. The prompt is sent to 3 models via `cli-council`
3. Each model independently cross-references keys, checks for typos, and verifies metadata
4. Cross-review catches false positives (flagged entries that are actually correct) and surfaces additional issues
5. Chairman synthesis produces a single `VALIDATION-REPORT.md`

## Invocation (CLI backend -- free)

```bash
cd packages/cli-council
uv run python -m cli_council \
    --prompt-file /tmp/bib-validate-prompt.txt \
    --context-file /tmp/bib-and-tex-content.txt \
    --output-md /tmp/bib-validate-council.md \
    --chairman claude \
    --timeout 180
```

See the shared council protocol documentation for the full orchestration protocol.

## Value

Moderate to high -- most valuable in deep verification mode where DOI/metadata accuracy matters. Different models have genuinely different bibliographic knowledge.
