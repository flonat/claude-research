"""CLI entry point for running council deliberations.

Usage:
    python -m llm_council \\
        --system-prompt "You are a paper reviewer..." \\
        --user-message "Review this paper: ..." \\
        --models "anthropic/claude-sonnet-4.5,openai/gpt-4.1,google/gemini-2.5-pro" \\
        --chairman "anthropic/claude-sonnet-4.5" \\
        --output result.json

    # Or read prompts from files:
    python -m llm_council \\
        --system-prompt-file system.txt \\
        --user-message-file user.txt \\
        --models "anthropic/claude-sonnet-4.5,openai/gpt-4.1,google/gemini-2.5-pro"

Environment:
    OPENROUTER_API_KEY  Required. Your OpenRouter API key.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from llm_council.client import LLMClient
from llm_council.config import COUNCIL_DEFAULT_CHAIRMAN, COUNCIL_DEFAULT_MODELS
from llm_council.council import CouncilService


async def _run(args: argparse.Namespace) -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    # Resolve prompts
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
        description="Run a multi-model LLM council deliberation via OpenRouter.",
    )
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
        default=",".join(COUNCIL_DEFAULT_MODELS),
        help="Comma-separated list of OpenRouter model IDs.",
    )
    parser.add_argument(
        "--chairman", type=str,
        default=COUNCIL_DEFAULT_CHAIRMAN,
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
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
