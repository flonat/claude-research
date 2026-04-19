from __future__ import annotations

import argparse
import asyncio
import json

import cli
import mcp_adapter
import tools  # noqa: F401 - triggers registry population
from tools._models import ToolResult
from tools._registry import TOOL_DEFINITIONS, TOOL_REGISTRY


def test_registry_loads_neutral_tool_specs() -> None:
    assert len(TOOL_DEFINITIONS) >= 28
    assert len(TOOL_DEFINITIONS) == len(TOOL_REGISTRY)
    assert all(spec.name and spec.description and spec.input_schema for spec in TOOL_DEFINITIONS)


def test_mcp_adapter_preserves_tool_names_and_schemas() -> None:
    mcp_tools = mcp_adapter.list_mcp_tools()
    assert [tool.name for tool in mcp_tools] == [spec.name for spec in TOOL_DEFINITIONS]
    assert mcp_tools[0].inputSchema == TOOL_DEFINITIONS[0].input_schema


def test_cli_parser_exposes_every_registered_tool() -> None:
    parser = cli.build_parser()
    subparsers_action = next(
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    command_names = set(subparsers_action.choices)
    for spec in TOOL_DEFINITIONS:
        assert cli.cli_command_name(spec.name) in command_names


def test_cli_argument_parsing_supports_positionals_and_flags() -> None:
    parser = cli.build_parser()
    namespace = parser.parse_args([
        "scholarly-search",
        "human AI collaboration",
        "--limit",
        "3",
        "--year-from",
        "2020",
    ])

    parsed = cli._parse_tool_arguments(namespace, namespace.spec)
    assert parsed == {
        "query": "human AI collaboration",
        "limit": 3,
        "year_from": 2020,
    }


def test_cli_json_args_bypass_schema_flags() -> None:
    parser = cli.build_parser()
    namespace = parser.parse_args([
        "scholarly-search",
        "--json-args",
        '{"query":"auctions","limit":2}',
    ])

    parsed = cli._parse_tool_arguments(namespace, namespace.spec)
    assert parsed == {"query": "auctions", "limit": 2}


def test_cli_json_envelope_shape() -> None:
    result = ToolResult(text="ok text")
    payload = result.envelope("scholarly_source_status", {})
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert decoded == {
        "tool": "scholarly_source_status",
        "arguments": {},
        "text": "ok text",
        "data": None,
        "ok": True,
    }


def test_mcp_adapter_calls_neutral_handler(monkeypatch) -> None:
    async def fake_handler(args: dict) -> ToolResult:
        return ToolResult(text=f"called with {args['value']}")

    monkeypatch.setitem(TOOL_REGISTRY, "fake_tool", fake_handler)
    try:
        content = asyncio.run(mcp_adapter.call_mcp_tool("fake_tool", {"value": "x"}))
        assert len(content) == 1
        assert content[0].text == "called with x"
    finally:
        TOOL_REGISTRY.pop("fake_tool", None)
