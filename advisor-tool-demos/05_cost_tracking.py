#!/usr/bin/env python3
"""05 — Iteration-level cost tracking.

Parses `usage.iterations[]` to break down executor vs. advisor token
usage and compute estimated costs per iteration.

Pricing (per 1M tokens):
  Sonnet 4.6  — $3.00 input, $15.00 output
  Opus   4.6  — $15.00 input, $75.00 output
"""

from helpers import (
    ADVISOR_TOOL, BETA, EXECUTOR_MODEL,
    create_client, process_response,
)

# Dollars per million tokens
PRICING = {
    "message": {"input": 3.00, "output": 15.00, "label": "Executor (Sonnet)"},
    "advisor_message": {"input": 15.00, "output": 75.00, "label": "Advisor (Opus)"},
}


def analyze_costs(response):
    """Print a detailed cost breakdown from usage.iterations."""
    iterations = getattr(response.usage, "iterations", None)
    if not iterations:
        print("No iterations data available.")
        return

    total_cost = 0.0
    advisor_cost = 0.0

    header = f"{'#':>3}  {'Type':<22} {'Input':>8} {'Output':>8}  {'Cost':>10}"
    print(f"\n{header}")
    print("-" * len(header))

    for i, it in enumerate(iterations):
        it_type = getattr(it, "type", "unknown")
        input_tok = getattr(it, "input_tokens", 0)
        output_tok = getattr(it, "output_tokens", 0)
        cache_read = getattr(it, "cache_read_input_tokens", 0)

        rates = PRICING.get(it_type, PRICING["message"])
        label = rates["label"]

        # Cache reads are cheaper (typically 90% off), but we use full
        # rate here for a conservative estimate.
        cost_in = (input_tok + cache_read) / 1_000_000 * rates["input"]
        cost_out = output_tok / 1_000_000 * rates["output"]
        cost = cost_in + cost_out
        total_cost += cost

        if it_type == "advisor_message":
            advisor_cost += cost

        print(f"{i:>3}  {label:<22} {input_tok:>8,} {output_tok:>8,}  ${cost:>9.6f}")

    print("-" * len(header))
    print(f"{'Total cost':<36} ${total_cost:>9.6f}")
    if total_cost > 0:
        pct = advisor_cost / total_cost * 100
        print(f"{'Advisor portion':<36} ${advisor_cost:>9.6f}  ({pct:.1f}%)")


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
                "Compare event-driven vs. request-driven architectures for "
                "a real-time fraud detection pipeline processing 50K "
                "transactions per second.  Recommend one with justification."
            ),
        }],
    )

    process_response(response)
    analyze_costs(response)


if __name__ == "__main__":
    main()
