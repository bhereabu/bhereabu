#!/usr/bin/env python3
"""02 — Multi-turn conversation with the advisor tool.

Shows how to preserve advisor_tool_result blocks in the message history
so the executor and advisor retain full context across turns.

CRITICAL: always append the raw `response.content` (not just extracted
text) as the assistant message.  Stripping advisor blocks breaks the
conversation.
"""

from helpers import (
    ADVISOR_TOOL, BETA, EXECUTOR_MODEL,
    create_client, process_response, print_usage,
)


def main():
    client = create_client()
    tools = [ADVISOR_TOOL]
    messages = []

    def chat(user_text):
        print(f"\n{'#'*60}")
        print(f"USER: {user_text}")
        print(f"{'#'*60}")

        messages.append({"role": "user", "content": user_text})

        response = client.beta.messages.create(
            model=EXECUTOR_MODEL,
            max_tokens=4096,
            betas=[BETA],
            tools=tools,
            messages=messages,
        )

        # Preserve ALL content blocks (text + advisor results) verbatim
        messages.append({"role": "assistant", "content": response.content})

        process_response(response)
        print_usage(response)
        return response

    chat(
        "I need to design a database schema for a multi-tenant SaaS "
        "application.  Tenants range from 10 to 100,000 users."
    )

    chat("How should I handle tenant data isolation — shared schema, "
         "separate schemas, or separate databases?")

    chat("What migration strategy would you recommend to move from our "
         "current single-tenant PostgreSQL setup?")


if __name__ == "__main__":
    main()
