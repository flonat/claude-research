"""CLI entry point: python -m cli_council."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from cli_council.config import DEFAULT_CHAIRMAN, DEFAULT_COUNCIL_BACKENDS
from cli_council.council import CouncilRunner


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cli-council",
        description="Run a multi-model council deliberation using local CLI tools.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="The question or task for the council. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Read prompt from a file instead of argument/stdin.",
    )
    parser.add_argument(
        "--context-file",
        type=Path,
        help="File with system context (project description, constraints, etc.).",
    )
    parser.add_argument(
        "--backends",
        type=str,
        default=",".join(DEFAULT_COUNCIL_BACKENDS),
        help=f"Comma-separated list of backends (default: {','.join(DEFAULT_COUNCIL_BACKENDS)}).",
    )
    parser.add_argument(
        "--chairman",
        type=str,
        default=DEFAULT_CHAIRMAN,
        help=f"Backend for Stage 3 synthesis (default: {DEFAULT_CHAIRMAN}).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout per backend call in seconds (default: 120).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON result to file (default: stdout).",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Write markdown report to file.",
    )
    parser.add_argument(
        "--cwd",
        type=str,
        help="Working directory for CLI tools (default: current directory).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check which backends are available and exit.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def _format_markdown(result) -> str:
    """Format a CouncilResult as a readable markdown report."""
    lines = ["# Council Report\n"]

    lines.append("## Synthesis\n")
    lines.append(result.synthesis)
    lines.append("")

    lines.append("## Individual Assessments\n")
    for a in result.assessments:
        lines.append(f"### {a.label} ({a.backend}, {a.model})\n")
        lines.append(a.text)
        lines.append(f"\n*Elapsed: {a.elapsed_ms}ms*\n")

    if result.peer_reviews:
        lines.append("## Peer Reviews\n")
        for r in result.peer_reviews:
            lines.append(f"### Review by {r.backend} ({r.model})\n")
            lines.append(r.review_text)
            if r.parsed_ranking:
                lines.append(f"\n**Ranking:** {' > '.join(r.parsed_ranking)}")
            lines.append(f"\n*Elapsed: {r.elapsed_ms}ms*\n")

    lines.append("## Metadata\n")
    meta = result.meta
    lines.append(f"- **Backends:** {', '.join(meta.backends_used)}")
    lines.append(f"- **Chairman:** {meta.chairman_backend}")
    lines.append(f"- **Timing:** Stage 1: {meta.stage1_ms}ms, Stage 2: {meta.stage2_ms}ms, Stage 3: {meta.stage3_ms}ms, Total: {meta.total_ms}ms")
    if meta.errors:
        lines.append(f"- **Errors:** {'; '.join(meta.errors)}")

    return "\n".join(lines)


def main() -> None:
    args = _parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    # --check mode
    if args.check:
        backends = args.backends.split(",")
        runner = CouncilRunner(backends=backends)
        available = runner.available_backends()
        print(f"Requested: {', '.join(backends)}")
        print(f"Available: {', '.join(available) or 'none'}")
        missing = set(backends) - set(available)
        if missing:
            print(f"Missing:   {', '.join(missing)}")
            sys.exit(1)
        print("All backends available.")
        sys.exit(0)

    # Resolve prompt
    prompt: str | None = args.prompt
    if args.prompt_file:
        prompt = args.prompt_file.read_text().strip()
    elif prompt is None:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print("Error: No prompt provided. Use positional arg, --prompt-file, or pipe via stdin.", file=sys.stderr)
            sys.exit(1)

    if not prompt:
        print("Error: Empty prompt.", file=sys.stderr)
        sys.exit(1)

    # Resolve context
    system_context = ""
    if args.context_file:
        system_context = args.context_file.read_text().strip()

    # Run council
    backends = [b.strip() for b in args.backends.split(",")]
    runner = CouncilRunner(
        backends=backends,
        chairman=args.chairman,
        timeout=args.timeout,
        cwd=args.cwd,
    )

    result = asyncio.run(runner.run(prompt, system_context=system_context))

    # Output JSON
    result_json = result.model_dump()
    if args.output:
        args.output.write_text(json.dumps(result_json, indent=2) + "\n")
        print(f"JSON result written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result_json, indent=2))

    # Output markdown
    if args.output_md:
        md = _format_markdown(result)
        args.output_md.write_text(md + "\n")
        print(f"Markdown report written to {args.output_md}", file=sys.stderr)


if __name__ == "__main__":
    main()
