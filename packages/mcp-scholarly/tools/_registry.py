"""Tool registry — maps tool names to handler functions."""

from __future__ import annotations

from typing import Callable, Awaitable

from mcp.types import Tool, TextContent

# All registered Tool definitions (populated by tool modules at import time)
TOOL_DEFINITIONS: list[Tool] = []

# name → async handler(args) mapping
TOOL_REGISTRY: dict[str, Callable[[dict], Awaitable[list[TextContent]]]] = {}


def register(tool: Tool, handler: Callable[[dict], Awaitable[list[TextContent]]]) -> None:
    """Register a tool definition and its handler."""
    TOOL_DEFINITIONS.append(tool)
    TOOL_REGISTRY[tool.name] = handler
