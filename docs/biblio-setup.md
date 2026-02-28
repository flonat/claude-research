<!-- Governed by: skills/shared/project-documentation.md -->

# Biblio MCP Server Setup

The Biblio MCP server (`.mcp-server-biblio/`) provides scholarly search across up to 3 sources. OpenAlex is always available (free, no key required). Scopus and Web of Science are optional — add API keys to unlock them.

## 1. Update the Email Address

In `.mcp-server-biblio/server.py`:

```python
client = OpenAlexClient(email="your.email@university.edu")
```

OpenAlex uses this for its [polite pool](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication#the-polite-pool) — faster rate limits, no registration needed.

## 2. Add the Server to Your Claude Code MCP Config

In `.mcp.json` (project root) or `~/.claude.json` (global access):

```json
{
  "mcpServers": {
    "biblio": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--frozen", "--directory", "/path/to/claude-code-flonat/.mcp-server-biblio", "python", "server.py"],
      "env": {}
    }
  }
}
```

## 3. (Optional) Add API Keys for Additional Sources

| Source | Env var | How to get it |
|--------|---------|---------------|
| OpenAlex | None needed | Free — just set your email in step 1 |
| Scopus | `SCOPUS_API_KEY` | [Elsevier Developer Portal](https://dev.elsevier.com/) — free for academic institutions |
| Web of Science | `WOS_API_KEY` | [Clarivate Developer Portal](https://developer.clarivate.com/) — requires institutional subscription |

Add keys to the `env` block:

```json
"env": {
  "SCOPUS_API_KEY": "your-scopus-key",
  "WOS_API_KEY": "your-wos-key",
  "WOS_API_TIER": "expanded"
}
```

The server auto-detects available keys at startup. With all 3 sources enabled, the `scholarly_*` tools deduplicate across sources and the `scholarly_verify_dois` tool cross-validates references.

## 4. Use `/literature`

Search for papers — the skill uses the biblio server automatically.
