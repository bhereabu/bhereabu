#!/usr/bin/env python3
"""01 — Basic advisor tool usage.

A Sonnet executor consults an Opus advisor for strategic guidance on a
complex architecture question.  The advisor runs server-side; no extra
round-trips are needed on the client.
"""

from helpers import (
    ADVISOR_TOOL, BETA, EXECUTOR_MODEL,
    create_client, process_response, print_usage,
)


def main():
    client = create_client()

    response = client.beta.messages.create(
        model=EXECUTOR_MODEL,
        max_tokens=4096,
        betas=[BETA],
        tools=[ADVISOR_TOOL],
        messages=[{
            "role": "user",
            "content": (
                "Design a microservices migration strategy for a monolithic "
                "e-commerce platform that processes 10,000 orders per day. "
                "The monolith is a Django app backed by PostgreSQL. "
                "Cover service decomposition, data migration, and rollback."
            ),
        }],
    )

    print("Stop reason:", response.stop_reason)
    process_response(response)
    print_usage(response)


if __name__ == "__main__":
    main()
