# CLI dispatch policy

Use this policy when a skill makes several independent calls to an installed
CLI integration. The CLI is an optional external capability: if it is not
configured, use the fallback documented by the calling skill.

## Thresholds

- One to three calls: run directly.
- Four or five calls: run directly only when the output is small and the calls
  complete quickly.
- Six or more calls: divide the inputs into bounded batches and delegate them.
- Prefer one native batch command over many single-item calls whenever the CLI
  provides one.

Each delegated batch has one purpose, writes structured output to a temporary
file, and returns only a compact summary. The orchestrator verifies the files,
merges the structured results, and removes temporary artifacts after successful
consumption unless the user asked to retain them.

Do not dispatch more workers than the active client supports, and do not assume
that an MCP registration exists merely because a CLI-shaped integration is
mentioned in a skill.
