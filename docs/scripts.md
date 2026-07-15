# CLI and external-integration boundary

`flonat-research` does not ship the former private `.scripts/` command bundle.
A clean framework installation therefore does not create commands such as
`task`, `tasks`, `done`, `papers`, `inbox`, `week`, `conf`, or `query`.

## What is bundled

- the managed-copy installer under `scripts/`;
- client-neutral skills, agents, rules, and files-first context;
- three standalone optional Claude hooks; and
- source for `packages/council-api/`, which is installed separately when used.

The setup script installs AI assets only. It does not modify `PATH`, create a
Python environment for optional packages, register MCP servers, or install
credentials.

## Optional external capabilities

| Capability | Typical interface | Bundled? | Safe fallback |
|---|---|:---:|---|
| Task or research database | Provider UI, API, or a separately installed CLI | No | Project `.context/` files and `MEMORY.md` |
| Scholarly search | Compatible `scholarly`-style CLI | No | Web search and manual DOI verification |
| Personal reference library | Paperpile/RefPile-compatible CLI or service | No | Project `.bib` validation |
| Claude MCP adapter | Client registration plus separately stored credentials | No | CLI or manual route |
| Cross-model council | Installed provider CLIs or bundled `council-api` source | Conditional | Current client or one explicit reviewer |

Before a workflow uses an optional command, run `<command> --help` and a small
read-only probe. If it is absent, follow the workflow’s documented fallback;
do not treat installation of this repository as evidence that the command or
its credentials exist.

## Adding your own CLI

Keep a reusable CLI in its own versioned package. Provide:

1. a documented `uv` installation command;
2. `--help` and a read-only health check;
3. machine-neutral configuration discovery;
4. credentials from an environment or secret manager, never Git; and
5. a capability-contract row or skill fallback explaining where it works.

Do not place host-maintenance scripts, private repository paths, or live
workspace identifiers in this public distribution.
