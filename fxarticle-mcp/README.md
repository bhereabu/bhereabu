# fxarticle-mcp

An MCP server that reads **X (Twitter) Articles** and posts through the [FxEmbed/FxTwitter](https://github.com/FxEmbed/FxEmbed) public API.

No API key. No X account. No cookies. No headless browser. No ban risk — every request is a logged-out public read, so there is no account to suspend.

It exists because `x.com` refuses automated fetchers, and long-form **X Articles** are the worst case: the post's own `text` field is empty, and the entire body lives in a Draft.js block structure that no generic scraper reassembles correctly. This server does that reassembly and hands back clean Markdown.

## Install

```bash
npm install
npm run build
```

Requires Node 18+ (uses native `fetch`).

## Connect it

Add to your MCP client config — for Claude Desktop, `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fxarticle": {
      "command": "node",
      "args": ["/absolute/path/to/fxarticle-mcp/dist/index.js"]
    }
  }
}
```

For Claude Code:

```bash
claude mcp add fxarticle -- node /absolute/path/to/fxarticle-mcp/dist/index.js
```

Test it standalone first:

```bash
npm run inspect   # opens MCP Inspector
```

## Tools

### `x_fetch_article`
The main event. Give it a post URL or bare ID; get the full Article as Markdown.

| Param | Type | Default | Notes |
|---|---|---|---|
| `url_or_id` | string | — | Full URL (any of x.com / twitter.com / fxtwitter.com / vxtwitter.com, query strings fine) or bare numeric ID |
| `format` | `markdown` \| `json` | `markdown` | `json` returns the raw article object |
| `include_images` | boolean | `true` | Emit `![](…)` for embedded media |
| `include_front_matter` | boolean | `true` | Title, author, date, source URL header |

If the target turns out to be an ordinary post rather than an Article, it returns the post text with a note instead of erroring.

Structured output includes `title`, `author_handle`, `published_at`, `word_count`, `block_count`, and the `markdown`.

### `x_list_articles`
Lists an account's Articles, newest first, with pagination.

`handle` accepts `startupideaspod`, `@startupideaspod`, or a profile URL. Pass `next_cursor` from a previous call to page.

**Upstream limitation:** this endpoint returns metadata only — `content.blocks` is empty. Use it for discovery, then call `x_fetch_article` per URL for bodies.

### `x_fetch_post`
Regular posts, with `mode: single | thread | conversation`. `thread` unrolls the author's self-reply chain; `conversation` adds replies from other accounts (capped by `max_replies`).

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `FXTWITTER_BASE_URL` | `https://api.fxtwitter.com` | Point at your own self-hosted instance |
| `FXTWITTER_TIMEOUT_MS` | `20000` | Per-request timeout |

### Self-hosting the upstream (recommended for anything production)

The public instance is volunteer-run and shares a ~1000 req/min per-IP limit. FxEmbed runs on Cloudflare Workers, free to 100k requests/day:

```bash
git clone https://github.com/FxEmbed/FxEmbed && cd FxEmbed
npm install
cp wrangler.example.toml wrangler.toml   # add your CF account ID
npx wrangler login && npm run deploy
```

Then set `FXTWITTER_BASE_URL=https://your-worker.workers.dev`. This also sidesteps the fact that X blocks many cloud egress IPs — Cloudflare's edge does the fetching, not your VM.

## Implementation notes / gotchas

These were verified against live API responses, not documentation — the published docs are wrong in places:

- **The documented thread endpoints 404.** The docs say `/2/threadid/:id` and `/2/conversationid/:id`; the working paths are `/2/thread/:id` and `/2/conversation/:id`.
- **`entityMap` is an array**, `[{key, value}, …]`, not the object that classic Draft.js uses. Both shapes are handled.
- **Inline styles are capitalised** (`"Bold"`), not Draft's usual `"BOLD"`. Matching is case-insensitive.
- **`atomic` blocks** carry a single-space `text` plus one entity range pointing at a `MEDIA` entity, whose `mediaId` must be resolved against `article.media_entities` to recover the image URL. Unresolvable media degrades to `*[embedded media]*` rather than vanishing.
- **Offsets are UTF-16 code units**, which happens to match JS string indexing — so styles land correctly even across emoji and CJK. A Python port would need `utf-16-le` handling here.
- **Style and link insertions are applied right-to-left** so earlier offsets stay valid, with closing markers ordered before opening markers at the same offset.
- **`article.created_at` from the listing endpoint is intermittently epoch-0.** Any timestamp at/near 0 is discarded and the post's own `created_at` is used instead; all dates are normalised to ISO 8601.
- Consecutive list items are merged so Markdown renders them as one list rather than several.

## Limits

- Protected (private) accounts return a clear 401 — FxTwitter only reads logged-out public content, and no configuration changes that.
- Deleted or suspended content returns 404 with a hint.
- The public instance can be down or degraded; self-host to remove that dependency.

## Legal

Reading logged-out public posts is on reasonably solid ground in the US after *hiQ v. LinkedIn* and *Meta v. Bright Data*, but this still contravenes X's Terms of Service, which prohibit automated access without written consent. If you are in the EU and store what you retrieve, GDPR applies to any personal data in it — have a lawful basis and a retention policy. Not legal advice.

## Licence

MIT. The upstream FxEmbed project is also MIT.
