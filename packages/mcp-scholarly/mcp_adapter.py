"""MCP adapter for the neutral scholarly tool registry."""

from __future__ import annotations

from collections.abc import Callable

from mcp.types import TextContent, Tool

from tools._models import ToolResult, ToolSpec
from tools._registry import TOOL_DEFINITIONS, TOOL_REGISTRY


def to_mcp_tool(spec: ToolSpec) -> Tool:
    """Convert a neutral tool specification into an MCP Tool."""
    return Tool(
        name=spec.name,
        description=spec.description,
        inputSchema=spec.input_schema,
    )


def list_mcp_tools() -> list[Tool]:
    """Return all registered tools in MCP schema form."""
    return [to_mcp_tool(spec) for spec in TOOL_DEFINITIONS]


def to_text_content(result: ToolResult) -> list[TextContent]:
    """Convert a neutral result into MCP text content."""
    return [TextContent(type="text", text=result.text)]


async def call_mcp_tool(
    name: str,
    arguments: dict | None,
    log: Callable[[str], None] | None = None,
) -> list[TextContent]:
    """Call a registered neutral tool and return MCP text content."""
    handler = TOOL_REGISTRY.get(name)
    if handler is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    args = arguments or {}
    try:
        result = await handler(args)
    except Exception as e:
        if log:
            log(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"**Error:** {e}")]

    return to_text_content(result)
