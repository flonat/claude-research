"""Neutral tool registry — maps tool names to handler functions."""

from __future__ import annotations

from typing import Callable, Awaitable

from tools._models import ToolResult, ToolSpec

Tool = ToolSpec

# All registered Tool definitions (populated by tool modules at import time)
TOOL_DEFINITIONS: list[ToolSpec] = []

# name → async handler(args) mapping
TOOL_REGISTRY: dict[str, Callable[[dict], Awaitable[ToolResult]]] = {}


def register(tool: ToolSpec, handler: Callable[[dict], Awaitable[ToolResult]]) -> None:
    """Register a tool definition and its handler."""
    TOOL_DEFINITIONS.append(tool)
    TOOL_REGISTRY[tool.name] = handler
