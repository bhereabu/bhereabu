# 17. Prompt Caching — big cost reduction on repeated context (dev)

For developers building on the Claude API. If your requests carry a large repeated
context block — a long system prompt, a reference document, a codebase — you're
paying to re-process those same tokens on every call.

Prompt caching stores that content server-side. Later calls reuse the cache
instead of re-processing it: cache reads cost about **0.1x** the normal input
price, and responses come back faster.

## The one-line version

Add `cache_control` to the content block you want cached:

```json
"cache_control": {"type": "ephemeral"}
```

## Runnable examples

| File | Run |
|---|---|
| [`cached_request.py`](cached_request.py) | `pip install anthropic && python cached_request.py` |
| [`cached_request.mjs`](cached_request.mjs) | `npm i @anthropic-ai/sdk && node cached_request.mjs` |

Both need `ANTHROPIC_API_KEY` in the environment. Each sends the same large
system prompt twice and prints the `usage` numbers, so you see the cache write on
call 1 and the cache read on call 2.

Expected shape of the output:

```
call 1  write 2437  read 0     uncached 12
call 2  write 0     read 2437  uncached 14     <- 0.1x price on 2437 tokens
```

## Corrections to the source guide

The guide's dev section is a generation behind. What actually holds now:

| Guide says | Reality |
|---|---|
| `"model": "claude-opus-4-6"` | Use `claude-opus-5`. Opus 4.6 still works but is two releases back. |
| "Cache persists for 5 minutes" | 5 minutes by default, **or 1 hour** with `{"type": "ephemeral", "ttl": "1h"}`. |
| "Up to 90% cost reduction" | True of cache *reads* (~0.1x). Writes cost **1.25x** (5m TTL) or **2x** (1h TTL). |
| (not mentioned) | There's a **minimum cacheable prefix**: 512 tokens on Opus 5, 1024 on Opus 4.8 and Sonnet 5. Below that nothing caches and you get no error. |
| (not mentioned) | Max **4** cache breakpoints per request. |

## When it pays off

Because a write costs more than a plain request, caching is a loss on a single
call and a win on repetition:

- **5-minute TTL** — break-even at 2 requests (1.25x + 0.1x = 1.35x, vs 2x uncached)
- **1-hour TTL** — break-even at 3 requests (2x + 0.2x = 2.2x, vs 3x uncached)

Use the 1-hour TTL when traffic is bursty with gaps longer than five minutes. For
continuous traffic the default is cheaper.

## The rule that decides whether this works at all

**Caching is a prefix match. Any byte that changes anywhere in the prefix
invalidates everything after it.**

Render order is `tools` → `system` → `messages`, so a marker on the last system
block caches the tools and the system prompt together. Put stable content first
and volatile content after the last breakpoint.

The usual reasons a cache never hits:

| In the prefix | Effect |
|---|---|
| `datetime.now()` / `Date.now()` | Prefix differs every request |
| A UUID or request ID | Same |
| `json.dumps(d)` without `sort_keys=True` | Key order varies between runs |
| A user ID interpolated into the system prompt | One cache per user, no sharing |
| A tool list that varies per request | Tools render at position 0, so nothing after them caches |

Fix by moving the dynamic piece after the last breakpoint, making the
serialization deterministic, or deleting it.

## Verifying

Read the `usage` fields on the response. This is the only reliable check:

- `cache_creation_input_tokens` — written this call (you paid the write premium)
- `cache_read_input_tokens` — served from cache (you paid ~0.1x)
- `input_tokens` — the **uncached remainder only**, not the total

Total prompt size is the sum of all three. If `cache_read_input_tokens` stays 0
across repeated identical-prefix requests, one of the invalidators above is in
play — diff the exact rendered bytes of two requests to find it.

## Also worth knowing

- **Concurrency** — an entry is readable only once the first response starts
  streaming. Firing N identical requests in parallel means all N pay full price.
  Send one, wait for the first token, then fan out.
- **Model switch invalidates everything.** Caches are per-model.
- **Changing the tool list invalidates everything.** Tools render first. Changing
  `tool_choice` or toggling thinking does *not* invalidate tools plus system.
