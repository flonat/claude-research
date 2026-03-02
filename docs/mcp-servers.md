# MCP Servers

MCP (Model Context Protocol) servers extend Claude with external tools and data sources. This infrastructure uses several MCP servers across Claude Code and Claude Desktop.

## Server Inventory

| Server | Claude Code | Claude Desktop | Type | Purpose |
|--------|:-----------:|:--------------:|------|---------|
| **bibliography** | `.mcp.json` | `claude_desktop_config.json` | Self-hosted | Multi-source scholarly search (OpenAlex + Scopus + WoS) |
| **user-papers** | `.mcp.json` | `claude_desktop_config.json` | Self-hosted | Zotero library management (search, PDF, semantic, BibTeX) |
| **context7** | `.mcp.json` | `claude_desktop_config.json` | npm | Up-to-date library/API documentation lookup |
| **github** | `~/.claude.json` (user) | `claude_desktop_config.json` | HTTP remote | GitHub repos, PRs, issues, code search |
| **filesystem** | -- | `claude_desktop_config.json` | npm | Read/write access to project folder (Desktop only) |
| **skills-server** | -- | `claude_desktop_config.json` | Self-hosted | Exposes skills, agents, and context library to Desktop |
| **cloudflare** | `.mcp.json` | `claude_desktop_config.json` | npm | Cloudflare Workers, KV, R2, D1 (optional) |
| **gcloud** | `.mcp.json` | `claude_desktop_config.json` | npm | Google Cloud Platform via gcloud CLI (optional) |

**Config locations:**

| Config | Scope | Servers |
|--------|-------|---------|
| `.mcp.json` | Project-level | bibliography, user-papers, context7, cloudflare, gcloud |
| `~/.claude.json` (user scope) | Global (all projects) | github |
| `claude_desktop_config.json` | Claude Desktop | All servers above |

## Custom Servers

### Bibliography MCP Server

Multi-source scholarly search across OpenAlex (free, always available), Scopus, and Web of Science.

**Setup guide:** [`bibliography-setup.md`](bibliography-setup.md)

### Flonat-Papers MCP Server (Zotero)

Zotero library management with 14 tools: search, PDF text extraction, semantic retrieval (ChromaDB), BibTeX export, and write operations.

**Location:** `packages/user-papers/`

**Skills bundled:** `bib-validate`, `bib-parse` (symlinked to `skills/`)

### Skills Server (Desktop only)

Exposes skills, agents, and the context library to Claude Desktop. Claude Code loads these directly from `~/.claude/skills/` and `.claude/agents/`.

**Location:** `.mcp-server-desktop/` (or `.mcp-server-biblio/` in the public repo)

## Third-Party Servers

### Context7

Fetches up-to-date documentation for any library or framework. Useful because Claude's training data has a knowledge cutoff.

- `resolve-library-id` — finds the library's documentation source
- `query-docs` — fetches relevant documentation pages and code examples

**Install:** `npx -y @upstash/context7-mcp` (add to `.mcp.json`)

### GitHub

GitHub integration via Copilot MCP endpoint. Provides repos, PRs, issues, commits, and code search.

**Type:** HTTP remote at `api.githubcopilot.com/mcp` with OAuth token

### Filesystem (Desktop only)

Standard `@modelcontextprotocol/server-filesystem` — gives Claude Desktop read/write access to the project folder. Not needed in Claude Code (which has direct file access).

### Cloudflare (optional)

Cloudflare developer platform — Workers, KV, R2, D1, routes, zones, secrets, cron triggers. Only needed if you deploy web applications on Cloudflare.

### gcloud (optional)

Google Cloud Platform via the gcloud CLI. Only needed if you use GCP services.

## Adding a New MCP Server

1. **Stdio servers** (self-hosted or npm): add to `.mcp.json` (project-level)
2. **HTTP remote servers**: add to `~/.claude.json` with user scope
3. **Claude Desktop**: add to `~/Library/Application Support/Claude/claude_desktop_config.json`
4. Always configure both clients if the server should be available everywhere
