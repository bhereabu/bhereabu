"""Prompt caching, end to end.

Sends the same large system prompt twice and prints the usage numbers so you can
see the cache write on call 1 and the cache read on call 2.

    pip install anthropic
    export ANTHROPIC_API_KEY=...
    python cached_request.py
"""

import os
import sys

import anthropic

MODEL = "claude-opus-5"

# The cached prefix must clear the model's minimum or nothing caches and you get
# no error: 512 tokens on Opus 5, 1024 on Opus 4.8 / Sonnet 5.
# Stand-in for the thing you'd really cache -- a long system prompt, a reference
# document, a codebase dump.
REFERENCE_DOC = (
    "You are a support assistant for Acme Cloud. Answer strictly from the "
    "reference material below.\n\n### Reference\n"
) + "\n".join(
    f"- Policy {i:03d}: Requests under plan tier {i % 4} are retried up to "
    f"{i % 5} times with exponential backoff, then routed to region "
    f"{'us-east' if i % 2 else 'eu-west'} for manual review."
    for i in range(400)
)

QUESTIONS = [
    "What happens to a tier-2 request after its retries are exhausted?",
    "Which region handles manual review for odd-numbered policies?",
]


def ask(client: anthropic.Anthropic, question: str) -> anthropic.types.Message:
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": REFERENCE_DOC,
                # This marker is the whole feature. Everything from the start of
                # the request up to and including this block is the cached
                # prefix. Add "ttl": "1h" for the one-hour cache (2x write cost,
                # break-even at 3 requests instead of 2).
                "cache_control": {"type": "ephemeral"},
            }
        ],
        # The question changes every call, so it sits AFTER the breakpoint.
        # Putting anything volatile before it would invalidate the whole prefix.
        messages=[{"role": "user", "content": question}],
    )


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY first.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()

    print(f"{'':6} {'write':>7} {'read':>7} {'uncached':>9}")
    for n, question in enumerate(QUESTIONS, start=1):
        response = ask(client, question)
        u = response.usage
        print(
            f"call {n} {u.cache_creation_input_tokens:>7} "
            f"{u.cache_read_input_tokens:>7} {u.input_tokens:>9}"
        )

    print()
    print("Call 1 writes the cache (~1.25x on those tokens).")
    print("Call 2 reads it (~0.1x). If 'read' stayed 0, something in the prefix")
    print("changed between calls -- a timestamp, a UUID, unsorted JSON keys.")
    print()
    print("Note: 'uncached' is the remainder only, not the total prompt size.")
    print("Total = write + read + uncached.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
