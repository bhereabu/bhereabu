#!/usr/bin/env python3
"""06 — Capping advisor calls with max_uses.

Compares unlimited advisor access vs. max_uses=1.  When the cap is hit,
further advisor calls return advisor_tool_result_error with error_code
"max_uses_exceeded" and the executor continues without advice.
"""

from helpers import (
    BETA, EXECUTOR_MODEL, ADVISOR_MODEL,
    create_client, process_response, print_usage,
)

PROMPT = (
    "Design a complete CI/CD pipeline for a polyglot monorepo (Python, Go, "
    "TypeScript) with the following requirements: build caching, parallel "
    "test execution, canary deployments, automatic rollback on error-rate "
    "spikes, and secrets management.  Provide concrete tool choices."
)


def count_advisor_blocks(response):
    """Count advisor_tool_result blocks in the response."""
    return sum(
        1 for b in response.content
        if getattr(b, "type", None) == "advisor_tool_result"
    )


def main():
    client = create_client()

    # --- Run 1: unlimited advisor calls ---
    print("=" * 60)
    print("Run 1: Unlimited advisor calls")
    print("=" * 60)

    advisor_unlimited = {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": ADVISOR_MODEL,
    }

    r1 = client.beta.messages.create(
        model=EXECUTOR_MODEL,
        max_tokens=4096,
        betas=[BETA],
        tools=[advisor_unlimited],
        messages=[{"role": "user", "content": PROMPT}],
    )

    process_response(r1)
    print_usage(r1)
    a1 = count_advisor_blocks(r1)
    print(f"Advisor consultations: {a1}")

    # --- Run 2: max_uses=1 ---
    print("\n" + "=" * 60)
    print("Run 2: max_uses=1")
    print("=" * 60)

    advisor_capped = {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": ADVISOR_MODEL,
        "max_uses": 1,
    }

    r2 = client.beta.messages.create(
        model=EXECUTOR_MODEL,
        max_tokens=4096,
        betas=[BETA],
        tools=[advisor_capped],
        messages=[{"role": "user", "content": PROMPT}],
    )

    process_response(r2)
    print_usage(r2)
    a2 = count_advisor_blocks(r2)
    print(f"Advisor consultations: {a2}")

    # --- Comparison ---
    print("\n" + "=" * 60)
    print("Comparison")
    print(f"  Unlimited: {a1} advisor call(s), "
          f"{r1.usage.output_tokens} output tokens")
    print(f"  Capped:    {a2} advisor call(s), "
          f"{r2.usage.output_tokens} output tokens")
    print("=" * 60)


if __name__ == "__main__":
    main()
