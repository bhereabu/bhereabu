/**
 * Prompt caching, end to end.
 *
 * Sends the same large system prompt twice and prints the usage numbers so you
 * can see the cache write on call 1 and the cache read on call 2.
 *
 *   npm i @anthropic-ai/sdk
 *   export ANTHROPIC_API_KEY=...
 *   node cached_request.mjs
 */

import Anthropic from "@anthropic-ai/sdk";

const MODEL = "claude-opus-5";

// The cached prefix must clear the model's minimum or nothing caches and you get
// no error: 512 tokens on Opus 5, 1024 on Opus 4.8 / Sonnet 5.
// Stand-in for the thing you'd really cache - a long system prompt, a reference
// document, a codebase dump.
const REFERENCE_DOC =
  "You are a support assistant for Acme Cloud. Answer strictly from the " +
  "reference material below.\n\n### Reference\n" +
  Array.from({ length: 400 }, (_, i) =>
    `- Policy ${String(i).padStart(3, "0")}: Requests under plan tier ${i % 4} ` +
    `are retried up to ${i % 5} times with exponential backoff, then routed to ` +
    `region ${i % 2 ? "us-east" : "eu-west"} for manual review.`,
  ).join("\n");

const QUESTIONS = [
  "What happens to a tier-2 request after its retries are exhausted?",
  "Which region handles manual review for odd-numbered policies?",
];

function ask(client, question) {
  return client.messages.create({
    model: MODEL,
    max_tokens: 1024,
    system: [
      {
        type: "text",
        text: REFERENCE_DOC,
        // This marker is the whole feature. Everything from the start of the
        // request up to and including this block is the cached prefix. Add
        // ttl: "1h" for the one-hour cache (2x write cost, break-even at 3
        // requests instead of 2).
        cache_control: { type: "ephemeral" },
      },
    ],
    // The question changes every call, so it sits AFTER the breakpoint. Putting
    // anything volatile before it would invalidate the whole prefix.
    messages: [{ role: "user", content: question }],
  });
}

if (!process.env.ANTHROPIC_API_KEY) {
  console.error("Set ANTHROPIC_API_KEY first.");
  process.exit(1);
}

const client = new Anthropic();
const pad = (n, w) => String(n).padStart(w);

console.log(`${"".padEnd(6)} ${pad("write", 7)} ${pad("read", 7)} ${pad("uncached", 9)}`);

for (const [i, question] of QUESTIONS.entries()) {
  const { usage: u } = await ask(client, question);
  console.log(
    `call ${i + 1} ${pad(u.cache_creation_input_tokens, 7)} ` +
      `${pad(u.cache_read_input_tokens, 7)} ${pad(u.input_tokens, 9)}`,
  );
}

console.log(`
Call 1 writes the cache (~1.25x on those tokens).
Call 2 reads it (~0.1x). If 'read' stayed 0, something in the prefix
changed between calls - a timestamp, a UUID, non-deterministic key order.

Note: 'uncached' is the remainder only, not the total prompt size.
Total = write + read + uncached.`);
