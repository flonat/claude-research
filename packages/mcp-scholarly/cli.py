#!/usr/bin/env python3
"""CLI adapter for the neutral scholarly tool registry."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

from tools._models import ToolResult, ToolSpec


class CliUsageError(Exception):
    """Raised when parsed CLI arguments cannot form a valid tool call."""


def _load_credentials_env() -> None:
    """Load API credentials for direct CLI launches.

    The MCP wrapper sources this file in `run.sh`; the CLI has to do the same
    before importing tool modules because source clients are initialized at import
    time.
    """
    creds_file = Path.home() / ".config" / "task-mgmt" / "credentials.env"
    if not creds_file.exists():
        return

    for raw_line in creds_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip()
        try:
            parsed = shlex.split(value, comments=True, posix=True)
            os.environ[key] = parsed[0] if parsed else ""
        except ValueError:
            os.environ[key] = value.strip("'\"")


def ensure_registry_loaded() -> None:
    """Import tool modules for side-effect registration."""
    _load_credentials_env()
    import tools  # noqa: F401


def cli_command_name(tool_name: str) -> str:
    """Convert an MCP tool name into its mirrored CLI command name."""
    return tool_name.replace("_", "-")


def _flag_name(property_name: str) -> str:
    return "--" + property_name.replace("_", "-")


def _argparse_help(text: str) -> str:
    """Escape argparse %-formatting placeholders in user-facing help text."""
    return text.replace("%", "%%")


def _schema_type(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type", "string")
    return schema_type[0] if isinstance(schema_type, list) else schema_type


def _convert_scalar(value: Any, schema: dict[str, Any]) -> Any:
    if value is None:
        return None
    schema_type = _schema_type(schema)
    if schema_type == "integer":
        return int(value)
    if schema_type == "number":
        return float(value)
    if schema_type == "boolean":
        if isinstance(value, bool):
            return value
        lowered = str(value).strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
        raise CliUsageError(f"Invalid boolean value: {value}")
    return str(value)


def _convert_array(value: Any, schema: dict[str, Any]) -> list[Any]:
    item_schema = schema.get("items", {"type": "string"})
    raw_values: list[Any] = []

    if value is None:
        return raw_values
    if isinstance(value, list):
        source_values = value
    else:
        source_values = [value]

    for item in source_values:
        if isinstance(item, list):
            raw_values.extend(item)
            continue
        text = str(item)
        if "," in text:
            raw_values.extend(part for part in text.split(",") if part)
        elif text:
            raw_values.append(text)

    return [_convert_scalar(item, item_schema) for item in raw_values]


def _convert_value(value: Any, schema: dict[str, Any]) -> Any:
    if _schema_type(schema) == "array":
        return _convert_array(value, schema)
    return _convert_scalar(value, schema)


def _add_common_tool_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Emit a stable JSON envelope instead of markdown.",
    )
    parser.add_argument(
        "--json-args",
        help="Pass the exact tool argument dictionary as JSON and bypass schema flags.",
    )


def _add_schema_args(parser: argparse.ArgumentParser, spec: ToolSpec) -> None:
    schema = spec.input_schema or {}
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    for name, prop_schema in properties.items():
        if name in required and _schema_type(prop_schema) != "boolean":
            nargs = "*" if _schema_type(prop_schema) == "array" else "?"
            parser.add_argument(
                f"_pos_{name}",
                nargs=nargs,
                metavar=name,
                help=argparse.SUPPRESS,
            )

    for name, prop_schema in properties.items():
        kwargs: dict[str, Any] = {
            "dest": name,
            "default": argparse.SUPPRESS,
            "help": _argparse_help(prop_schema.get("description", "")),
        }
        choices = prop_schema.get("enum")
        if choices:
            kwargs["choices"] = choices

        schema_type = _schema_type(prop_schema)
        if schema_type == "boolean":
            parser.add_argument(
                _flag_name(name),
                action=argparse.BooleanOptionalAction,
                **kwargs,
            )
        elif schema_type == "array":
            parser.add_argument(
                _flag_name(name),
                action="append",
                metavar=name.upper(),
                **kwargs,
            )
        else:
            parser.add_argument(
                _flag_name(name),
                metavar=name.upper(),
                **kwargs,
            )


def build_parser() -> argparse.ArgumentParser:
    ensure_registry_loaded()
    from tools._registry import TOOL_DEFINITIONS

    parser = argparse.ArgumentParser(
        prog="scholarly",
        description="Search and inspect scholarly sources via the shared scholarly tool registry.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-tools", help="List registered scholarly tools.")
    list_parser.add_argument("--json", action="store_true", dest="output_json")
    list_parser.set_defaults(action="list_tools")

    status_parser = subparsers.add_parser(
        "source-status",
        help="Show configured scholarly data sources.",
    )
    status_parser.add_argument("--json", action="store_true", dest="output_json")
    status_parser.set_defaults(action="tool", tool_name="scholarly_source_status", spec=None)

    call_parser = subparsers.add_parser("call", help="Call a tool by exact registry name.")
    call_parser.add_argument("tool_name", help="Exact tool name, e.g. scholarly_search.")
    call_parser.add_argument(
        "--json-args",
        required=True,
        help="Exact tool argument dictionary as JSON.",
    )
    call_parser.add_argument("--json", action="store_true", dest="output_json")
    call_parser.set_defaults(action="call")

    for spec in TOOL_DEFINITIONS:
        command = cli_command_name(spec.name)
        tool_parser = subparsers.add_parser(
            command,
            description=_argparse_help(spec.description),
            help=_argparse_help(spec.description.split(".")[0]),
        )
        _add_common_tool_args(tool_parser)
        _add_schema_args(tool_parser, spec)
        tool_parser.set_defaults(action="tool", tool_name=spec.name, spec=spec)

    return parser


def _decode_json_args(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as e:
        raise CliUsageError(f"Invalid --json-args: {e}") from e
    if not isinstance(decoded, dict):
        raise CliUsageError("--json-args must decode to a JSON object")
    return decoded


def _namespace_has(namespace: argparse.Namespace, name: str) -> bool:
    return hasattr(namespace, name)


def _parse_tool_arguments(namespace: argparse.Namespace, spec: ToolSpec | None) -> dict[str, Any]:
    if _namespace_has(namespace, "json_args") and namespace.json_args:
        return _decode_json_args(namespace.json_args)
    if spec is None:
        return {}

    schema = spec.input_schema or {}
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    parsed: dict[str, Any] = {}

    for name, prop_schema in properties.items():
        value = None
        has_value = False
        if _namespace_has(namespace, name):
            value = getattr(namespace, name)
            has_value = True

        pos_name = f"_pos_{name}"
        if not has_value and _namespace_has(namespace, pos_name):
            pos_value = getattr(namespace, pos_name)
            if pos_value not in (None, [], ""):
                value = pos_value
                has_value = True

        if has_value:
            try:
                converted = _convert_value(value, prop_schema)
            except (TypeError, ValueError) as e:
                raise CliUsageError(f"Invalid value for {name}: {value}") from e
            if converted not in (None, [], ""):
                parsed[name] = converted

    missing = [name for name in required if name not in parsed]
    if missing:
        missing_flags = ", ".join(_flag_name(name) for name in missing)
        raise CliUsageError(f"Missing required argument(s): {missing_flags}")

    return parsed


async def _invoke(tool_name: str, arguments: dict[str, Any]) -> ToolResult:
    from tools._registry import TOOL_REGISTRY

    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        return ToolResult(text=f"Unknown tool: {tool_name}", ok=False, error="unknown_tool")
    try:
        return await handler(arguments)
    except Exception as e:
        return ToolResult(text=f"**Error:** {e}", ok=False, error=str(e))


def _format_tool_list(output_json: bool) -> str:
    from tools._registry import TOOL_DEFINITIONS

    tools_payload = [
        {
            "name": spec.name,
            "command": cli_command_name(spec.name),
            "description": spec.description,
            "input_schema": spec.input_schema,
        }
        for spec in TOOL_DEFINITIONS
    ]
    if output_json:
        return json.dumps({"tools": tools_payload, "count": len(tools_payload)}, indent=2)

    lines = ["## Scholarly CLI Tools", "", "| Command | Tool | Required |", "|---|---|---|"]
    for item in tools_payload:
        required = item["input_schema"].get("required", [])
        required_text = ", ".join(required) if required else "-"
        lines.append(f"| `{item['command']}` | `{item['name']}` | {required_text} |")
    lines.append("")
    lines.append(f"*{len(tools_payload)} tools registered*")
    return "\n".join(lines)


def _emit_result(
    tool_name: str,
    arguments: dict[str, Any],
    result: ToolResult,
    output_json: bool,
) -> None:
    if output_json:
        print(json.dumps(result.envelope(tool_name, arguments), indent=2, ensure_ascii=False))
    else:
        print(result.text)


async def _run(namespace: argparse.Namespace) -> int:
    if namespace.action == "list_tools":
        print(_format_tool_list(namespace.output_json))
        return 0

    if namespace.action == "call":
        arguments = _decode_json_args(namespace.json_args)
        result = await _invoke(namespace.tool_name, arguments)
        _emit_result(namespace.tool_name, arguments, result, namespace.output_json)
        return 0 if result.ok else 1

    arguments = _parse_tool_arguments(namespace, namespace.spec)
    result = await _invoke(namespace.tool_name, arguments)
    _emit_result(namespace.tool_name, arguments, result, namespace.output_json)
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)
    try:
        return asyncio.run(_run(namespace))
    except CliUsageError as e:
        if getattr(namespace, "output_json", False):
            tool_name = getattr(namespace, "tool_name", namespace.command)
            result = ToolResult(text=f"**Error:** {e}", ok=False, error=str(e))
            _emit_result(tool_name, {}, result, output_json=True)
        else:
            print(f"scholarly: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
