<!-- Governed by: skills/shared/project-documentation.md -->

# Scholarly search and bibliography setup

The public framework treats scholarly search as a capability, not as a
Claude-only MCP tool. Shell-capable Claude Code and Codex sessions use the
`scholarly` CLI. Claude Desktop may use the same package through its optional
MCP server. Personal-library tools such as Paperpile or RefPile are separate
optional services and are not installed or configured by this repository.

## 1. Install a compatible scholarly CLI (optional)

The CLI is not bundled by `flonat-research`. Obtain a compatible package from
its publisher or use ordinary web/library search, then follow that package’s
README with `uv`. Do not infer a download URL from examples in this framework.

Verify the CLI before configuring any client adapter:

```bash
scholarly --help
scholarly scholarly-search "your topic" --json
scholarly scholarly-verify-dois --dois 10.0000/example --json
```

Provider coverage and credential requirements are package-owned. Verify them
against the installed CLI’s current help.

## 2. Claude Code and Codex

Use the CLI from either shell-capable client. Shared skills must call or
describe the CLI route rather than assuming that an MCP tool exists:

```bash
scholarly scholarly-search "difference-in-differences spillovers" --json
scholarly scholarly-verify-dois --dois 10.1257/aer.20181103 --json
```

The exact subcommand list is package-owned; run `scholarly --help` instead of
copying an old tool list into this repository.

## 3. Optional Claude Desktop MCP adapter

Claude Desktop cannot run arbitrary shell commands, so it may register the
package's MCP server in its normal configuration. Use the command and arguments
from the installed scholarly package's current README. Keep credentials in the
client's environment or a secret manager—never in this repository—and verify
the registration independently after every path or runtime change.

Codex does not need this registration and this guide does not present MCP tools
as callable from Codex.

## 4. Optional personal-library services

- **Paperpile** is a reference manager and citekey source. If you use it,
  install the separate `paperpile` CLI/package and verify `paperpile --help`.
- **RefPile** provides semantic search over a configured Paperpile library. It
  requires its own service or network endpoint; verify `refpile --help` and the
  endpoint before using it.

Neither service, its credentials, nor its registrations are bundled here.

## 5. Skill behavior

The `literature`, `bib-validate`, `bib-parse`, and related skills should:

1. discover which CLIs are actually installed;
2. use the CLI route in shell-capable clients;
3. use an MCP adapter only on a surface where it is explicitly registered;
4. state a manual fallback when a personal library is absent; and
5. verify every DOI or bibliographic claim before writing it.

See [`availability.md`](availability.md) for client targeting and
[`skills.md`](skills.md) for the shipped workflows.
