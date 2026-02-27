"""Backend registry and defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendSpec:
    """Specification for a CLI backend."""

    name: str
    command: str            # binary name
    headless_flag: str      # flag for non-interactive mode
    model_flag: str         # flag to select model (empty if not supported)
    default_model: str      # default model name
    output_flag: str        # flag for output format (empty if not needed)


BACKENDS: dict[str, BackendSpec] = {
    "gemini": BackendSpec(
        name="gemini",
        command="gemini",
        headless_flag="-p",
        model_flag="-m",
        default_model="gemini-2.5-pro",
        output_flag="-o text",
    ),
    "codex": BackendSpec(
        name="codex",
        command="codex",
        headless_flag="exec",
        model_flag="-m",
        default_model="default",
        output_flag="",
    ),
    "claude": BackendSpec(
        name="claude",
        command="claude",
        headless_flag="-p",
        model_flag="--model",
        default_model="claude-sonnet-4-6",
        output_flag="",
    ),
}

DEFAULT_COUNCIL_BACKENDS: list[str] = ["gemini", "codex", "claude"]
DEFAULT_CHAIRMAN: str = "claude"

# Subprocess timeout in seconds per stage
STAGE_TIMEOUT: int = 120
