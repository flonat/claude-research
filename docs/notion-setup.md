# Optional Notion integration

Notion is an optional external task/research system. The base framework remains
usable without it because durable context lives in `AI.md`, `MEMORY.md`, and
`.context/`. This repository does not create databases, install a Notion CLI,
register an MCP server, or store a token.

## Choose an adapter

| Surface | Route | Notes |
|---|---|---|
| Claude Code | A supported managed Notion integration or separate MCP adapter | Client-specific convenience; verify its current tool names in Claude |
| Codex | A separately installed CLI, connector, or manual browser workflow | Do not ask Codex to call a Claude-only MCP tool |
| Either client | Local `.context/` files | Always available and the continuity fallback |

Provider setup changes over time. Follow the current official client and
Notion documentation rather than copying a historical registration snippet.
Keep credentials in the operating-system secret store or environment, never in
`AI.md`, `CLAUDE.md`, `AGENTS.md`, or a committed settings file.

## Suggested database model

If you use Notion, two databases are a practical starting point:

- **Tasks** — title, status, priority, due date, project, source, and task type.
- **Research pipeline** — output title, stage, target venue, collaborators,
  priority, and a short status note.

Store database identifiers in a local ignored configuration file owned by the
adapter, not in generated client guidance. Record only the human-readable
workflow and fallback in `AI.md`.

## Verify before use

1. Confirm the adapter can list a harmless page or database.
2. Confirm it is scoped only to the intended workspace content.
3. Test a read-only query from the client that will use it.
4. Test the local-only fallback with the adapter disabled.

When the integration is unavailable, report that state explicitly and continue
with local context. Never silently claim that a task or pipeline record was
read or updated.
