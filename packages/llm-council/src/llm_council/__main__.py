"""CLI entry point for running council deliberations.

Usage:
    # Run a council
    llm-council \\
        --system-prompt "You are a paper reviewer..." \\
        --user-message "Review this paper: ..." \\
        --models "anthropic/claude-sonnet-4.5,openai/gpt-4.1,google/gemini-2.5-pro" \\
        --chairman "anthropic/claude-sonnet-4.5" \\
        --output result.json

    # Or read prompts from files:
    llm-council \\
        --system-prompt-file system.txt \\
        --user-message-file user.txt

    # Manage models
    llm-council models                          # show available + defaults
    llm-council models --pricing                # include OpenRouter pricing
    llm-council models --set-defaults "m1,m2"   # set default council models
    llm-council models --set-chairman "m1"      # set default chairman
    llm-council models --reset                  # revert to built-in defaults

Environment:
    OPENROUTER_API_KEY  Required for council runs and pricing lookups.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from llm_council.client import LLMClient
from llm_council.config import (
    AVAILABLE_MODELS,
    USER_CONFIG_PATH,
    _BUILTIN_DEFAULT_CHAIRMAN,
    _BUILTIN_DEFAULT_MODELS,
    get_chairman_default,
    get_council_defaults,
    reset_council_defaults,
    set_council_defaults,
)


# --- Models subcommand ---


async def _models_command(args: argparse.Namespace) -> None:
    if args.reset:
        reset_council_defaults()
        print("Reset to built-in defaults.")
        print(f"  Council: {', '.join(_BUILTIN_DEFAULT_MODELS)}")
        print(f"  Chairman: {_BUILTIN_DEFAULT_CHAIRMAN}")
        return

    if args.set_defaults:
        models = [m.strip() for m in args.set_defaults.split(",")]
        known_ids = {m["id"] for m in AVAILABLE_MODELS}
        unknown = [m for m in models if m not in known_ids]
        if unknown:
            print(f"Warning: unknown model(s): {', '.join(unknown)}", file=sys.stderr)
            print("They will be saved but may not work on OpenRouter.", file=sys.stderr)
        set_council_defaults(models=models)
        print(f"Default council models set: {', '.join(models)}")

    if args.set_chairman:
        set_council_defaults(chairman=args.set_chairman)
        print(f"Default chairman set: {args.set_chairman}")

    if args.set_defaults or args.set_chairman:
        return

    # List models
    council_defaults = get_council_defaults()
    chairman = get_chairman_default()
    is_custom = USER_CONFIG_PATH.exists()

    if args.pricing:
        from llm_council.config import fetch_model_pricing

        models = await fetch_model_pricing()
    else:
        models = [m.copy() for m in AVAILABLE_MODELS]

    # Group by provider
    providers: dict[str, list[dict]] = {}
    for m in models:
        provider = m["id"].split("/")[0]
        providers.setdefault(provider, []).append(m)

    source = "user config" if is_custom else "built-in"
    print(f"Council defaults ({source}):")
    print(f"  Models:   {', '.join(council_defaults)}")
    print(f"  Chairman: {chairman}")
    if is_custom:
        print(f"  Config:   {USER_CONFIG_PATH}")
    print()

    print(f"Available models ({len(models)}):")
    for provider in ["anthropic", "openai", "google"]:
        if provider not in providers:
            continue
        print(f"\n  {provider.title()}:")
        for m in providers[provider]:
            marker = ""
            if m["id"] in council_defaults and m["id"] == chairman:
                marker = " [default, chairman]"
            elif m["id"] in council_defaults:
                marker = " [default]"
            elif m["id"] == chairman:
                marker = " [chairman]"

            price = ""
            if args.pricing and "input_price" in m:
                price = f"  ({m['input_price']}/{m['output_price']} per 1M tok)"

            print(f"    {m['id']:45s} {m.get('tier', ''):25s}{marker}{price}")


# --- Run subcommand (existing behavior) ---


async def _run_command(args: argparse.Namespace) -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if args.system_prompt_file:
        system_prompt = open(args.system_prompt_file).read()
    else:
        system_prompt = args.system_prompt or "You are a helpful expert assistant."

    if args.user_message_file:
        user_msg = open(args.user_message_file).read()
    else:
        user_msg = args.user_message or ""

    if not user_msg:
        print("Error: --user-message or --user-message-file required.", file=sys.stderr)
        sys.exit(1)

    models = [m.strip() for m in args.models.split(",")]
    chairman = args.chairman

    from llm_council.council import CouncilService

    llm = LLMClient(api_key=api_key, max_tokens=args.max_tokens)
    council = CouncilService(llm)

    try:
        result = await council.run_council(
            system_prompt=system_prompt,
            user_msg=user_msg,
            council_models=models,
            chairman_model=chairman,
        )

        output = result.model_dump()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output, f, indent=2)
            print(f"Result written to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(output, indent=2))

    finally:
        await llm.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-model LLM council via OpenRouter.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- models subcommand ---
    models_parser = subparsers.add_parser(
        "models", help="List available models and manage defaults.",
    )
    models_parser.add_argument(
        "--pricing", action="store_true",
        help="Fetch and display OpenRouter pricing.",
    )
    models_parser.add_argument(
        "--set-defaults", type=str, metavar="MODELS",
        help="Set default council models (comma-separated model IDs).",
    )
    models_parser.add_argument(
        "--set-chairman", type=str, metavar="MODEL",
        help="Set default chairman model.",
    )
    models_parser.add_argument(
        "--reset", action="store_true",
        help="Remove user config and revert to built-in defaults.",
    )

    # --- run subcommand (also the default) ---
    run_parser = subparsers.add_parser(
        "run", help="Run a council deliberation.",
    )
    _add_run_args(run_parser)

    # Also add run args to the main parser for backwards compatibility
    _add_run_args(parser)

    args = parser.parse_args()

    if args.command == "models":
        asyncio.run(_models_command(args))
    else:
        asyncio.run(_run_command(args))


def _add_run_args(parser: argparse.ArgumentParser) -> None:
    """Add the run-command arguments to a parser."""
    parser.add_argument(
        "--system-prompt", type=str, default=None,
        help="System prompt for Stage 1 assessments.",
    )
    parser.add_argument(
        "--system-prompt-file", type=str, default=None,
        help="Read system prompt from a file.",
    )
    parser.add_argument(
        "--user-message", type=str, default=None,
        help="User message for Stage 1 assessments.",
    )
    parser.add_argument(
        "--user-message-file", type=str, default=None,
        help="Read user message from a file.",
    )
    parser.add_argument(
        "--models", type=str,
        default=",".join(get_council_defaults()),
        help="Comma-separated list of OpenRouter model IDs.",
    )
    parser.add_argument(
        "--chairman", type=str,
        default=get_chairman_default(),
        help="Model ID for the chairman synthesis.",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=4096,
        help="Max tokens per LLM response.",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write JSON result to file instead of stdout.",
    )


if __name__ == "__main__":
    main()
