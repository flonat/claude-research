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

from mcp.server import Server

from _app import log  # noqa: F401 — triggers client initialization

server = Server("scholarly")
log("MCP server initialized")

# Importing `tools` triggers side-effect registration of all tool modules
import tools  # noqa: F401
from mcp_adapter import call_mcp_tool, list_mcp_tools


@server.list_tools()
async def list_tools():
    return list_mcp_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"call_tool: {name} {arguments}")

    return await call_mcp_tool(name, arguments, log=log)


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
