"""Antigravity CLI backend.

Successor to the Gemini CLI backend: on 2026-06-18 Google stopped serving
free / AI Pro / AI Ultra individual tiers through `gemini`; those tiers are
now served by the Antigravity CLI (`agy`, brew cask `antigravity-cli`).

Notes (from `agy --help`, v1.0.16):
- `-p` / `--print`: "Run a single prompt non-interactively and print the
  response" (`--prompt` is an alias). Print mode waits up to `--print-timeout`
  (default 5m); the council's own timeout should be >= that.
- `--model <name>`: model for the CLI session (list with `agy models`).
  Omitted when no model is set, so the account default applies.
- Requires a one-time interactive OAuth: run `agy` with no arguments and
  complete the browser flow. Unauthenticated, agy exits 0 with NO output in
  non-TTY contexts -- an empty response from this backend usually means
  "not logged in", not "empty answer".
"""

from __future__ import annotations

from council_cli.backends.base import CLIBackend
from council_cli.config import BACKENDS


class AntigravityBackend(CLIBackend):
    """Wrapper for Google's Antigravity CLI (agy -p)."""

    name = "agy"
    command = "agy"

    def __init__(self, model: str | None = None) -> None:
        spec = BACKENDS["agy"]
        self.default_model = model or spec.default_model

    def build_args(self, prompt: str, *, model: str | None = None) -> list[str]:
        effective_model = model or self.default_model
        args = ["agy", "-p", prompt]
        if effective_model:
            args += ["--model", effective_model]
        return args
