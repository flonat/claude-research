#!/usr/bin/env python3
"""
Biblio MCP Server

Multi-source scholarly search: OpenAlex + Semantic Scholar + Crossref (always)
+ Scopus + WoS + CORE + arXiv + ORCID + Altmetric + Exa (when API keys provided).

Architecture:
  _app.py      — shared state: client/source init, formatters, helpers
  tools/*.py   — tool definitions + handlers (registered via tools/_registry.py)
  server.py    — this file: wires the registry to the MCP server
"""

import asyncio

from _app import server, log  # noqa: F401 — triggers client initialization

# Importing `tools` triggers side-effect registration of all tool modules
import tools  # noqa: F401
from tools._registry import TOOL_DEFINITIONS, TOOL_REGISTRY


@server.list_tools()
async def list_tools():
    return TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"call_tool: {name} {arguments}")

    handler = TOOL_REGISTRY.get(name)
    if handler is None:
        from mcp.types import TextContent
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        return await handler(arguments)
    except Exception as e:
        log(f"Error in {name}: {e}")
        from mcp.types import TextContent
        return [TextContent(type="text", text=f"**Error:** {e}")]


async def main():
    from mcp.server.stdio import stdio_server

    log("Starting MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        log("stdio_server ready, running server...")
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )
    log("Server stopped")


if __name__ == "__main__":
    log("Main entry point")
    asyncio.run(main())
