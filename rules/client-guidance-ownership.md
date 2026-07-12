---
paths:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
  - "**/GEMINI.md"
---

# Rule: Respect Client Guidance Ownership

## Policy

Use the active client's guidance file as authoritative instructions. Do not
silently import a sibling client's guidance file as a second instruction set:

- Codex uses `AGENTS.md`;
- Claude Code uses `CLAUDE.md`;
- Gemini uses `GEMINI.md`.

Shared project facts belong in neutral files such as `AI.md`, `README.md`,
`docs/`, and `.context/`; client files should point to those sources.

## What To Do

- Read and follow the active client's guidance file normally.
- During broad documentation scans, skip sibling client guidance files unless
  comparison, migration, or parity review is the task.
- If explicitly asked to compare or edit another client's guidance, do so and
  report which file is authoritative for the current client.
- Never ignore `AGENTS.md` in Codex or `CLAUDE.md` in Claude Code.

## Why

This prevents duplicated or contradictory instructions without disabling the
active client's actual configuration.
