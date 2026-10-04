#!/usr/bin/env python3
"""04 — Advisor tool combined with other tools.

The advisor coexists with server-side tools (web_search) and custom
client-side tools (analyze_codebase) in the same request.  Server-side
tools execute automatically; custom tools require the standard agentic
loop on the client.
"""

import json

from helpers import (
    ADVISOR_TOOL, BETA, EXECUTOR_MODEL,
    create_client, process_response, print_usage,
)

CUSTOM_TOOL = {
    "name": "analyze_codebase",
    "description": (
        "Analyze a codebase and return metrics: lines of code, number of "
        "modules, test coverage percentage, and dependency count."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "Path or URL of the repository to analyze.",
            },
        },
        "required": ["repo_path"],
    },
}

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}


def handle_custom_tool(name, tool_input):
    """Return mock results for custom tools."""
    if name == "analyze_codebase":
        return json.dumps({
            "repo": tool_input.get("repo_path", "unknown"),
            "lines_of_code": 124_500,
            "modules": 38,
            "test_coverage_pct": 67.3,
            "dependencies": 152,
        })
    return json.dumps({"error": f"Unknown tool: {name}"})


def main():
    client = create_client()

    tools = [ADVISOR_TOOL, WEB_SEARCH_TOOL, CUSTOM_TOOL]

    messages = [{
        "role": "user",
        "content": (
            "I have a Python monorepo at github.com/example/platform.  "
            "Analyze its codebase, then recommend a strategy to improve "
            "test coverage from the current level to 85%.  Factor in "
            "current best practices for Python testing."
        ),
    }]

    # Agentic loop: server-side tools (advisor, web_search) resolve
    # automatically.  Only custom tool_use blocks need client handling.
    for turn in range(10):
        response = client.beta.messages.create(
            model=EXECUTOR_MODEL,
            max_tokens=4096,
            betas=[BETA],
            tools=tools,
            messages=messages,
        )

        print(f"\n--- Turn {turn + 1}  (stop_reason={response.stop_reason}) ---")
        process_response(response)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    result = handle_custom_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            if tool_results:
                messages.append({"role": "user", "content": tool_results})
            else:
                break
        else:
            break

    print_usage(response)


if __name__ == "__main__":
    main()
