"""Codex CLI backend."""

from __future__ import annotations

from cli_council.backends.base import CLIBackend
from cli_council.config import BACKENDS


class CodexBackend(CLIBackend):
    """Wrapper for OpenAI's Codex CLI (codex exec)."""

    name = "codex"
    command = "codex"

    def __init__(self, model: str | None = None) -> None:
        spec = BACKENDS["codex"]
        self.default_model = model or spec.default_model

    def build_args(self, prompt: str, *, model: str | None = None) -> list[str]:
        effective_model = model or self.default_model
        args = ["codex", "exec"]
        # Skip -m flag when using default — ChatGPT accounts don't support
        # explicit model selection but use the best available (GPT-5).
        if effective_model != "default":
            args.extend(["-m", effective_model])
        args.extend(["--full-auto", prompt])
        return args
