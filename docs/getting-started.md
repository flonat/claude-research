# Getting started

`flonat-research` supports Claude Code, Codex, or both from one checkout. The
shared source is client-neutral; installation creates managed copies for the
selected clients and records their hashes in a receipt.

Use this repository *or* `flonat-research-friends` as the managed distribution
on a machine, not both. Their installers intentionally target some of the same
client-home paths.

## Prerequisites

- Git
- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- Claude Code, Codex, or both
- Optional: a TeX distribution with `latexmk` for LaTeX workflows

Use uv for every Python command. Hooks are a Claude-only convenience; Codex does
not need them to read the shared file context.

## Install

The repository is still reachable through its transition alias:

```bash
git clone https://github.com/flonat/flonat-research.git flonat-research
cd flonat-research
./scripts/setup.sh --client both
```

Choose `claude` or `codex` instead of `both` for a single-client installation.
On Windows PowerShell:

```powershell
git clone https://github.com/flonat/flonat-research.git flonat-research
cd flonat-research
.\scripts\setup.ps1 -Client both
```

The installer:

1. reads `config/install-manifest.json`;
2. copies only assets declared compatible with the selected client;
3. puts shared Claude skill bodies in `~/.claude/shared-skills/` and short
   command adapters in `~/.claude/commands/`;
4. puts Codex-compatible skills in `~/.agents/skills/` and agents in
   `~/.codex/agents/`;
5. preserves existing Claude settings and unmanaged files; and
6. writes `~/.config/flonat-research/install-receipt.json`.

It also installs shared skill resources beside each client’s skill tree,
agent reference files beside both agent adapters, and reviewed rules under
`~/.codex/rules/` for Codex. `AGENTS.md` tells Codex when to read those rules.

No home-directory symlinks or junctions are created.

## Verify and update

```bash
./scripts/setup.sh --client both --check
git pull --ff-only
./scripts/setup.sh --client both
./scripts/setup.sh --client both --check
```

The second install is a no-op when source and receipt are current. The former
`--update` spelling remains accepted for compatibility, but every normal install
already reconciles managed copies. A divergent
managed file is preserved under `~/.config/flonat-research/backups/` before it
is reconciled. An unmanaged conflicting file stops installation.

A first successful installation ends with `--check` reporting `PASS`. Restart
the selected clients, invoke one simple bundled skill such as `proofread`, and
confirm that it appears only once. Optional CLIs, MCP registrations, and
credentials are separate checks and do not form part of the base receipt.

For an existing Claude-only symlink installation, follow
[the transition guide](transitioning-to-flonat-research.md) and use
`--migrate-legacy` only after inspecting the reported links.

## Shared context

Customise these repository files:

- `.context/profile.md`
- `.context/current-focus.md`
- `.context/projects/_index.md`
- `MEMORY.md`
- `.context/ai-handoff.md` when handing work between sessions or clients

`AI.md` is the neutral root guidance. `CLAUDE.md` and `AGENTS.md` are generated
entry points for Claude and Codex. Put project-specific durable context in the
files above rather than relying on a client transcript.

## Capability boundaries

The public contract is `config/ai-contracts.yaml`; the installation plan is
`config/install-manifest.json`.

The generated [`availability.md`](availability.md) inventory accounts for
skills, agents, rules, hooks, MCP registrations, and CLIs. Read it when an item
is missing from a client: an explicit `No` is a reviewed boundary, not an
installer discovery error.

| Capability | Claude Code | Codex |
|---|---:|---:|
| Shared file context and handoff | Yes | Yes |
| Compatible skills | Yes | Yes |
| Compatible custom agents | Markdown adapter | TOML adapter |
| Claude hooks and settings | Yes | No; not presented as active |
| Claude MCP workflows | When configured | Use documented CLI fallback |
| Shared skill name appears twice in Codex Desktop | No | No |

## Start a project

Open a research project containing `CLAUDE.md`, `AGENTS.md`, or both. Both files
should point at the same project context rather than duplicate it. Ask
naturally for a workflow, use `/skill-name` in Claude, or `$skill-name` in
Codex.

For a project with role-specific agents and repeatable workflows, use the
shared `init-project-orchestration` skill. It writes neutral sources under
`.ai/orchestration/` and renders both clients' project adapters from those
sources.

When adding a new skill or agent, declare its clients and required capabilities
before rendering. See [Contributing](../CONTRIBUTING.md) when available; missing
client metadata is a hard validation failure.
