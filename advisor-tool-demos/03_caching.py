#!/usr/bin/env python3
"""03 — Advisor-side prompt caching.

Enables ephemeral caching on the advisor tool so repeated advisor calls
within a conversation share cached context.  The first call pays a cache-
write premium; subsequent calls within the TTL window read from the cache.

Caching breaks even at roughly 3 advisor calls and improves from there.
"""

from helpers import (
    BETA, EXECUTOR_MODEL, ADVISOR_MODEL,
    create_client, process_response,
)


def main():
    client = create_client()

    # Advisor tool with 5-minute cache
    advisor_cached = {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": ADVISOR_MODEL,
        "caching": {"type": "ephemeral", "ttl": "5m"},
    }

    tools = [advisor_cached]
    messages = []

    prompts = [
        "Outline a production-ready observability stack for a Kubernetes "
        "cluster running 50 microservices.",
        "Now add distributed tracing.  Which vendor-neutral standards "
        "should I adopt, and how do they integrate with the stack above?",
        "Finally, how should I set up alerting thresholds to reduce noise "
        "while catching real incidents?",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"Turn {i}")
        print(f"{'='*60}")

        messages.append({"role": "user", "content": prompt})

        response = client.beta.messages.create(
            model=EXECUTOR_MODEL,
            max_tokens=4096,
            betas=[BETA],
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})
        process_response(response)

        # Show caching metrics per iteration
        iterations = getattr(response.usage, "iterations", [])
        for j, it in enumerate(iterations):
            it_type = getattr(it, "type", "?")
            cache_create = getattr(it, "cache_creation_input_tokens", 0)
            cache_read = getattr(it, "cache_read_input_tokens", 0)
            input_tok = getattr(it, "input_tokens", 0)
            print(f"  iter {j} ({it_type}): input={input_tok}  "
                  f"cache_create={cache_create}  cache_read={cache_read}")


if __name__ == "__main__":
    main()
