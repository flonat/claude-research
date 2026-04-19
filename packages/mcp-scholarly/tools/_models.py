"""Neutral tool models shared by the MCP and CLI adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolSpec:
    """Provider-neutral description of a callable scholarly tool."""

    name: str
    description: str
    input_schema: dict[str, Any]

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any] | None = None,
        inputSchema: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.input_schema = input_schema if input_schema is not None else (inputSchema or {})

    @property
    def inputSchema(self) -> dict[str, Any]:
        """Compatibility alias for the MCP field name."""
        return self.input_schema


@dataclass(slots=True)
class ToolResult:
    """Provider-neutral tool execution result."""

    text: str
    data: Any = None
    ok: bool = True
    error: str | None = None

    def envelope(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Return the stable JSON envelope used by the CLI."""
        payload = {
            "tool": tool,
            "arguments": arguments,
            "text": self.text,
            "data": self.data,
            "ok": self.ok,
        }
        if self.error:
            payload["error"] = self.error
        return payload
