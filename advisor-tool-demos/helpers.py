"""Shared utilities for Anthropic Advisor Tool demos."""

import os
import sys

import anthropic

BETA = "advisor-tool-2026-03-01"
EXECUTOR_MODEL = "claude-sonnet-4-6"
ADVISOR_MODEL = "claude-opus-4-6"

ADVISOR_TOOL = {
    "type": "advisor_20260301",
    "name": "advisor",
    "model": ADVISOR_MODEL,
}


def create_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def process_response(response):
    """Walk response content blocks, printing each type."""
    for block in response.content:
        block_type = getattr(block, "type", None)

        if block_type == "text":
            print(f"\n[Executor]\n{block.text}")

        elif block_type == "server_tool_use":
            name = getattr(block, "name", "unknown")
            print(f"\n--- Executor invoked server tool: {name} ---")

        elif block_type == "advisor_tool_result":
            _handle_advisor_result(block)

        elif block_type == "tool_use":
            name = getattr(block, "name", "?")
            print(f"\n[Tool call: {name}] input={getattr(block, 'input', {})}")

        else:
            print(f"\n[Block type={block_type}]")


def _handle_advisor_result(block):
    """Dispatch on the advisor_tool_result content variant."""
    content = getattr(block, "content", None)
    if content is None:
        print("\n[Advisor] (no content)")
        return

    result_type = getattr(content, "type", None)

    if result_type == "advisor_result":
        text = getattr(content, "text", "")
        print(f"\n[Advisor guidance]\n{text}")

    elif result_type == "advisor_redacted_result":
        print("\n[Advisor] (encrypted/redacted result — opaque to client, "
              "visible to executor on next turn)")

    elif result_type == "advisor_tool_result_error":
        code = getattr(content, "error_code", "unknown")
        print(f"\n[Advisor error] code={code}")

    else:
        print(f"\n[Advisor] unknown result type: {result_type}")


def print_usage(response):
    """Print top-level token usage."""
    u = response.usage
    print(f"\n{'='*50}")
    print(f"Usage  — input: {u.input_tokens}  output: {u.output_tokens}")

    iterations = getattr(u, "iterations", None)
    if iterations:
        print(f"         {len(iterations)} iteration(s) reported")
    print(f"{'='*50}")
