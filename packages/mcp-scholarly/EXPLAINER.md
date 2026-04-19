# Dual Scholarly CLI + MCP Explainer

## What Changed

This package now supports two frontends over the same scholarly tool implementation:

- The existing MCP server, still launched through `run.sh` / `server.py`.
- A new `scholarly` CLI, launched with `uv run scholarly ...`.

The core design change is that scholarly tools no longer return MCP-specific
objects directly. They now return neutral `ToolResult` objects. The MCP server
wraps those neutral results into MCP `TextContent`, while the CLI prints either
markdown or a JSON envelope.

In short:

```text
biblio-sources clients
        |
        v
_app.py shared runtime and provider clients
        |
        v
tools/*.py neutral handlers returning ToolResult
        |
        v
tools/_registry.py neutral tool registry
        |
        +--> mcp_adapter.py --> server.py MCP frontend
        |
        +--> cli.py ---------> scholarly CLI frontend
```

## Why This Was Done

The MCP was globally enabled and exposed 39 tools. That means every session paid
the context cost of the full scholarly tool schema, even for unrelated work.

The CLI lets the same scholarly stack remain available without globally loading
all MCP schemas into every conversation. The MCP remains available as a fallback
or for sessions where direct MCP tool calling is more convenient.

## Main Files

### `tools/_models.py`

Defines the neutral data models:

- `ToolSpec`: the provider-neutral equivalent of an MCP tool definition.
- `ToolResult`: the provider-neutral result returned by all handlers.

`ToolResult` includes:

- `text`: markdown output shown to humans and returned to MCP clients.
- `data`: optional structured data, currently `None` for most tools.
- `ok`: success/failure flag used by the CLI for exit codes.
- `error`: optional error text.

It also exposes `envelope(tool, arguments)`, which powers CLI `--json` output.

### `tools/_registry.py`

The registry is now neutral. It stores:

- `TOOL_DEFINITIONS: list[ToolSpec]`
- `TOOL_REGISTRY: dict[str, Callable[[dict], Awaitable[ToolResult]]]`

For compatibility with the existing tool modules, it aliases:

```python
Tool = ToolSpec
```

That allowed the tool registration blocks to keep their existing shape:

```python
register(
    Tool(
        name="scholarly_search",
        description="...",
        inputSchema={...},
    ),
    _handle_scholarly_search,
)
```

### `tools/*.py`

All tool modules were converted from MCP-specific handlers to neutral handlers.

Before:

```python
from mcp.types import Tool, TextContent

async def _handle_example(args: dict) -> list[TextContent]:
    return [TextContent(type="text", text=text)]
```

After:

```python
from tools._registry import Tool, ToolResult, register

async def _handle_example(args: dict) -> ToolResult:
    return ToolResult(text=text)
```

The provider logic was intentionally left unchanged. This was not a rewrite of
OpenAlex, Semantic Scholar, Crossref, Scopus, Web of Science, CORE, ORCID,
Altmetric, Zenodo, Unpaywall, OpenCitations, DBLP, OpenReview, arXiv, or Exa
behavior.

### `mcp_adapter.py`

This is the only place, apart from `server.py`, that imports MCP types.

It provides:

- `to_mcp_tool(spec)`: converts `ToolSpec` to `mcp.types.Tool`.
- `list_mcp_tools()`: returns all registered tools as MCP tools.
- `to_text_content(result)`: converts `ToolResult` to MCP `TextContent`.
- `call_mcp_tool(name, arguments, log=None)`: calls a neutral handler and returns
  MCP-compatible output.

Unknown tools and exceptions keep the previous MCP behavior:

- Unknown tool: `Unknown tool: <name>`
- Exception: `**Error:** <message>`

### `server.py`

The MCP entrypoint is still `server.py`, but it is now thin:

- Creates the MCP `Server("scholarly")`.
- Imports `tools` for side-effect registration.
- Uses `mcp_adapter.list_mcp_tools()` for `list_tools`.
- Uses `mcp_adapter.call_mcp_tool()` for `call_tool`.

This preserves MCP compatibility while removing tool-specific MCP logic from
the provider modules.

### `_app.py`

`_app.py` now acts as shared runtime/provider initialization rather than owning
the MCP server object.

It still initializes:

- OpenAlex
- Semantic Scholar
- Crossref
- Scopus
- Web of Science
- CORE
- ORCID
- Altmetric
- Zenodo
- Unpaywall
- OpenCitations
- DBLP
- OpenReview
- arXiv
- Exa

The final MCP-specific `Server("scholarly")` object was moved into
`server.py`.

### `cli.py`

Adds the new CLI frontend.

The CLI dynamically loads the same registry as MCP and exposes every registered
tool as a dashed command:

```text
MCP name: scholarly_search
CLI name: scholarly-search
```

Examples:

```bash
uv run scholarly scholarly-search "human AI collaboration" --limit 3
uv run scholarly crossref-lookup-doi 10.1145/3359313
uv run scholarly arxiv-search "multi-agent systems" --limit 3
```

It also provides an exact-name escape hatch:

```bash
uv run scholarly call scholarly_source_status --json-args '{}'
```

This is useful when a generated command is awkward, or when a caller already has
an exact MCP-style argument dictionary.

### `pyproject.toml`

Adds package metadata so `uv` installs the CLI entrypoint:

```toml
[project.scripts]
scholarly = "cli:main"
```

It also adds minimal setuptools configuration for the existing top-level modules
and the `tools` package.

### `tests/test_dual_cli_mcp.py`

Adds smoke tests for the dual system:

- Registry loads neutral tool specs.
- MCP adapter preserves names and schemas.
- CLI parser exposes every registered tool.
- CLI argument parsing supports positional required values and flags.
- `--json-args` bypasses schema flags.
- JSON envelope shape is stable.
- MCP adapter calls neutral handlers correctly.

## CLI Behavior

### Command Generation

Every registered tool is exposed as a CLI subcommand by replacing underscores
with dashes:

```text
openalex_search_works      -> openalex-search-works
crossref_lookup_doi        -> crossref-lookup-doi
scholarly_search           -> scholarly-search
scholarly_source_status    -> scholarly-source-status
arxiv_search               -> arxiv-search
exa_get_contents           -> exa-get-contents
```

There is also a shorter convenience command:

```bash
uv run scholarly source-status
```

This calls `scholarly_source_status`.

### Required Arguments

Required non-boolean schema fields can be passed positionally:

```bash
uv run scholarly scholarly-search "human AI collaboration"
```

They can also be passed as flags:

```bash
uv run scholarly scholarly-search --query "human AI collaboration"
```

Optional fields are exposed as flags:

```bash
uv run scholarly scholarly-search "human AI collaboration" --limit 3 --year-from 2020
```

### Arrays

Array arguments accept repeated flags and comma-separated values where practical:

```bash
uv run scholarly scholarly-verify-dois --dois 10.1145/3359313 --dois 10.1038/s42256-022-00593-2
```

or:

```bash
uv run scholarly scholarly-verify-dois --dois 10.1145/3359313,10.1038/s42256-022-00593-2
```

### Booleans

Boolean schema fields use argparse's boolean optional action:

```bash
uv run scholarly openalex-search-works "AI collaboration" --open-access
uv run scholarly exa-search "AI research" --no-include-text
```

### JSON Args Escape Hatch

Every mirrored tool command supports `--json-args`:

```bash
uv run scholarly scholarly-search --json-args '{"query":"human AI collaboration","limit":3}'
```

The exact-name `call` command requires `--json-args`:

```bash
uv run scholarly call scholarly_search --json-args '{"query":"human AI collaboration","limit":3}'
```

## Output Behavior

### Markdown Default

By default the CLI prints the same markdown text that MCP clients receive:

```bash
uv run scholarly source-status
```

### JSON Envelope

Pass `--json` for structured output:

```bash
uv run scholarly scholarly-search "human AI collaboration" --limit 3 --json
```

The shape is:

```json
{
  "tool": "scholarly_search",
  "arguments": {
    "query": "human AI collaboration",
    "limit": 3
  },
  "text": "...markdown...",
  "data": null,
  "ok": true
}
```

For errors, the CLI returns a non-zero exit code and includes:

```json
{
  "ok": false,
  "error": "..."
}
```

## Credentials

`run.sh` already sources:

```text
~/.config/task-mgmt/credentials.env
```

The CLI now does the same before importing tool modules. This matters because
provider clients are initialized at import time. Without this, direct CLI calls
would miss credentials that the MCP server sees through `run.sh`.

Existing environment variables still work and take precedence over values in the
credentials file.

## How To Use

For most sessions, prefer the CLI:

```bash
uv run scholarly scholarly-search "query"
uv run scholarly crossref-lookup-doi 10.xxxx/xxxxx
uv run scholarly arxiv-search "query" --limit 5
```

Tool discovery:

```bash
uv run scholarly --help      # lists all mirrored commands
uv run scholarly <cmd> --help  # schema-derived flags per command
```

The MCP frontend remains enabled and usable for sessions where direct MCP tool calls are preferable (e.g. Claude Desktop, which cannot shell out to `uv`).

## Known Issues (upstream — not refactor regressions)

- CORE provider returns `500 Internal Server Error` during `scholarly-search`.
- Web of Science provider fails with `'int' object has no attribute 'get'`.

Both predate the CLI/MCP refactor. Track via GitHub issues on `packages/mcp-scholarly`.

## Rollout Plan

Moving the scholarly stack off the always-on MCP baseline (to save per-session context cost) is tracked as a phased plan with checkboxes:

**See:** [`log/plans/2026-04-15_mcp-scholarly-cli-rollout.md`](../../log/plans/2026-04-15_mcp-scholarly-cli-rollout.md)

Phases: install + parity → per-cluster skill migration → sub-agent integration → MCP disable → downstream surfaces (container, Desktop, public) → docs.
