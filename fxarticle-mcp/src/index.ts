#!/usr/bin/env node
/**
 * fxarticle-mcp — an MCP server that reads X (Twitter) Articles and posts
 * through the FxEmbed/FxTwitter public API.
 *
 * Transport is stdio, so nothing may be written to stdout except JSON-RPC.
 * Diagnostics go to stderr.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { renderArticleMarkdown, wordCount } from "./article.js";
import {
  FxTwitterClient,
  FxTwitterError,
  parseHandle,
  parseStatusId,
  type FxArticle,
  type FxStatus,
} from "./fxtwitter.js";

const VERSION = "1.0.0";

const client = new FxTwitterClient();

/* ------------------------------------------------------------------ dates */

/**
 * Normalises an upstream date to ISO 8601.
 *
 * The listing endpoint intermittently reports `article.created_at` as epoch 0,
 * so anything at or near the epoch is treated as missing rather than as 1970.
 */
function toIso(value: string | number | null | undefined): string | null {
  if (value === null || value === undefined || value === "") return null;

  let ms: number;
  if (typeof value === "number") {
    // FxTwitter reports `created_timestamp` in seconds.
    ms = value < 1e12 ? value * 1000 : value;
  } else {
    ms = Date.parse(value);
  }

  if (!Number.isFinite(ms)) return null;
  // Within a day of the epoch means "unset", not a real 1970 publication date.
  if (Math.abs(ms) < 86_400_000) return null;

  return new Date(ms).toISOString();
}

/** Best available publication date: the article's own, else the post's. */
function publishedAt(status: FxStatus, article?: FxArticle | null): string | null {
  return toIso(article?.created_at) ?? toIso(status.created_at) ?? toIso(status.created_timestamp) ?? null;
}

/* ----------------------------------------------------------------- errors */

interface TextResult {
  [key: string]: unknown;
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
  structuredContent?: Record<string, unknown>;
}

function textResult(text: string, structuredContent?: Record<string, unknown>): TextResult {
  const result: TextResult = { content: [{ type: "text", text }] };
  if (structuredContent) result.structuredContent = structuredContent;
  return result;
}

/**
 * Tool errors are reported as `isError` results rather than thrown, so the
 * model sees the message and hint instead of a transport-level failure.
 */
function errorResult(err: unknown): TextResult {
  if (err instanceof FxTwitterError) {
    const lines = [`${err.message} (code ${err.code})`];
    if (err.hint) lines.push(err.hint);
    return { content: [{ type: "text", text: lines.join("\n") }], isError: true };
  }
  const message = err instanceof Error ? err.message : String(err);
  return { content: [{ type: "text", text: `Unexpected error: ${message}` }], isError: true };
}

/* -------------------------------------------------------------- rendering */

function statusHeader(status: FxStatus): string {
  const handle = status.author?.screen_name;
  const name = status.author?.name;
  const who = name ? `${name}${handle ? ` (@${handle})` : ""}` : handle ? `@${handle}` : "(unknown author)";
  const date = publishedAt(status);
  return `**${who}**${date ? ` · ${date}` : ""}${status.url ? ` · ${status.url}` : ""}`;
}

function statusMetrics(status: FxStatus): string | null {
  const bits: string[] = [];
  if (status.likes != null) bits.push(`${status.likes} likes`);
  if (status.reposts != null) bits.push(`${status.reposts} reposts`);
  if (status.replies != null) bits.push(`${status.replies} replies`);
  if (status.views != null) bits.push(`${status.views} views`);
  return bits.length ? `_${bits.join(" · ")}_` : null;
}

function renderStatus(status: FxStatus): string {
  const parts = [statusHeader(status)];
  const body = (status.text ?? "").trim();
  parts.push(body || "_(no text)_");
  const metrics = statusMetrics(status);
  if (metrics) parts.push(metrics);
  return parts.join("\n\n");
}

/* ------------------------------------------------------------------ server */

const server = new McpServer(
  { name: "fxarticle-mcp", version: VERSION },
  {
    capabilities: { tools: {} },
    instructions:
      "Reads X (Twitter) Articles and posts via the FxEmbed/FxTwitter public API — no API key or account. " +
      "Use x_fetch_article for long-form Articles (it reassembles the Draft.js body into Markdown), " +
      "x_list_articles to discover an account's Articles, and x_fetch_post for ordinary posts and threads.",
  },
);

/* --------------------------------------------------------- x_fetch_article */

server.registerTool(
  "x_fetch_article",
  {
    title: "Fetch an X Article as Markdown",
    description:
      "Fetch a long-form X (Twitter) Article by post URL or ID and return its full body as Markdown. " +
      "If the target is an ordinary post rather than an Article, its text is returned with a note instead of an error.",
    inputSchema: {
      url_or_id: z
        .string()
        .describe('Post URL (x.com / twitter.com / fxtwitter.com / vxtwitter.com, query strings fine) or bare numeric ID'),
      format: z.enum(["markdown", "json"]).default("markdown").describe("markdown (default) or the raw article object as JSON"),
      include_images: z.boolean().default(true).describe("Emit ![](…) for embedded media"),
      include_front_matter: z.boolean().default(true).describe("Prepend title, author, date and source URL"),
    },
    outputSchema: {
      is_article: z.boolean(),
      id: z.string(),
      url: z.string(),
      title: z.string().nullable(),
      author_name: z.string().nullable(),
      author_handle: z.string().nullable(),
      published_at: z.string().nullable(),
      word_count: z.number(),
      block_count: z.number(),
      markdown: z.string(),
    },
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async ({ url_or_id, format, include_images, include_front_matter }) => {
    try {
      const id = parseStatusId(url_or_id);
      const response = await client.status(id);
      const status = response.status;
      if (!status) {
        throw new FxTwitterError(
          "The upstream API returned no post for that ID.",
          404,
          "The post may be deleted, the account suspended or protected, or the ID may be wrong.",
        );
      }

      const author = status.author ?? {};
      const article = status.article ?? null;
      const date = publishedAt(status, article);

      // Not an Article — hand back the post text rather than failing.
      if (!article) {
        const note =
          "_This post is not an X Article; it is an ordinary post. Returning its text. " +
          "Use `x_fetch_post` for threads and replies._";
        const markdown = `${note}\n\n${renderStatus(status)}`;
        const text = (status.text ?? "").trim();
        return textResult(markdown, {
          is_article: false,
          id: status.id,
          url: status.url,
          title: null,
          author_name: author.name ?? null,
          author_handle: author.screen_name ?? null,
          published_at: date,
          word_count: text.split(/\s+/).filter(Boolean).length,
          block_count: 0,
          markdown,
        });
      }

      const markdown = renderArticleMarkdown(
        article,
        {
          authorName: author.name,
          authorHandle: author.screen_name,
          url: status.url,
          createdAt: toIso(status.created_at) ?? undefined,
          publishedAt: date ?? undefined,
        },
        { includeImages: include_images, includeFrontMatter: include_front_matter },
      );

      // `markdown` stays populated in structured output regardless of `format`,
      // so consumers get a consistent shape; `format: json` only changes the text content.
      const text = format === "json" ? JSON.stringify(article, null, 2) : markdown;

      return textResult(text, {
        is_article: true,
        id: status.id,
        url: status.url,
        title: article.title ?? null,
        author_name: author.name ?? null,
        author_handle: author.screen_name ?? null,
        published_at: date,
        word_count: wordCount(article),
        block_count: article.content?.blocks?.length ?? 0,
        markdown,
      });
    } catch (err) {
      return errorResult(err);
    }
  },
);

/* --------------------------------------------------------- x_list_articles */

server.registerTool(
  "x_list_articles",
  {
    title: "List an account's X Articles",
    description:
      "List the X Articles published by an account, newest first, with pagination. " +
      "The upstream endpoint returns metadata only — no article bodies — so use x_fetch_article per URL to read them.",
    inputSchema: {
      handle: z.string().describe('Handle ("startupideaspod", "@startupideaspod") or a profile URL'),
      limit: z.number().int().min(1).max(50).default(10).describe("Maximum articles to return from the current page"),
      next_cursor: z.string().optional().describe("Cursor from a previous call, to fetch the next page"),
    },
    outputSchema: {
      handle: z.string(),
      returned: z.number(),
      page_size: z.number(),
      next_cursor: z.string().nullable(),
      articles: z.array(
        z.object({
          id: z.string(),
          url: z.string(),
          title: z.string().nullable(),
          preview_text: z.string().nullable(),
          published_at: z.string().nullable(),
          author_handle: z.string().nullable(),
        }),
      ),
    },
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async ({ handle, limit, next_cursor }) => {
    try {
      const screenName = parseHandle(handle);
      const response = await client.profileArticles(screenName, next_cursor);
      const results = response.results ?? [];

      const all = results
        .filter((status) => status.article)
        .map((status) => {
          const article = status.article as FxArticle;
          return {
            id: status.id,
            url: status.url,
            title: article.title ?? null,
            preview_text: article.preview_text ?? null,
            published_at: publishedAt(status, article),
            author_handle: status.author?.screen_name ?? null,
            _sort: toIso(status.created_timestamp) ?? publishedAt(status, article) ?? "",
          };
        })
        .sort((a, b) => (a._sort < b._sort ? 1 : a._sort > b._sort ? -1 : 0))
        .map(({ _sort, ...rest }) => rest);

      const articles = all.slice(0, limit);
      const cursor = response.cursor?.bottom ?? null;

      const lines: string[] = [
        `# Articles by @${screenName}`,
        `Showing ${articles.length} of ${all.length} on this page.`,
      ];

      if (articles.length === 0) {
        lines.push("_No Articles found for this account._");
      } else {
        for (const [i, a] of articles.entries()) {
          const meta = [a.published_at, a.url].filter(Boolean).join(" · ");
          lines.push(
            `${i + 1}. **${a.title ?? "(untitled)"}**` +
              (meta ? `\n   ${meta}` : "") +
              (a.preview_text ? `\n   ${a.preview_text.trim().slice(0, 200)}` : ""),
          );
        }
        lines.push(
          "_Bodies are not included by this endpoint — call `x_fetch_article` with a URL above to read one._",
        );
      }

      if (all.length > articles.length) {
        lines.push(`_Raise \`limit\` to see the remaining ${all.length - articles.length} on this page._`);
      }
      if (cursor) lines.push(`_Next page: pass \`next_cursor: "${cursor}"\`._`);

      return textResult(lines.join("\n\n"), {
        handle: screenName,
        returned: articles.length,
        page_size: all.length,
        next_cursor: cursor,
        articles,
      });
    } catch (err) {
      return errorResult(err);
    }
  },
);

/* ------------------------------------------------------------ x_fetch_post */

server.registerTool(
  "x_fetch_post",
  {
    title: "Fetch an X post, thread or conversation",
    description:
      "Fetch an ordinary X (Twitter) post. `thread` unrolls the author's self-reply chain; " +
      "`conversation` also includes replies from other accounts.",
    inputSchema: {
      url_or_id: z.string().describe("Post URL or bare numeric ID"),
      mode: z.enum(["single", "thread", "conversation"]).default("single").describe("How much of the discussion to fetch"),
      max_replies: z.number().int().min(0).max(200).default(20).describe("Cap on replies from other accounts (conversation mode)"),
    },
    outputSchema: {
      id: z.string(),
      url: z.string(),
      mode: z.string(),
      author_handle: z.string().nullable(),
      published_at: z.string().nullable(),
      is_article: z.boolean(),
      post_count: z.number(),
      reply_count: z.number(),
      markdown: z.string(),
    },
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async ({ url_or_id, mode, max_replies }) => {
    try {
      const id = parseStatusId(url_or_id);
      const response =
        mode === "thread" ? await client.thread(id) : mode === "conversation" ? await client.conversation(id) : await client.status(id);

      const status = response.status;
      if (!status) {
        throw new FxTwitterError(
          "The upstream API returned no post for that ID.",
          404,
          "The post may be deleted, the account suspended or protected, or the ID may be wrong.",
        );
      }

      const thread = mode === "single" ? [status] : response.thread?.length ? response.thread : [status];
      const replies = mode === "conversation" ? (response.replies ?? []).slice(0, max_replies) : [];

      const sections: string[] = [];
      if (status.article) {
        sections.push("_This post is an X Article — use `x_fetch_article` for the full body._");
      }

      sections.push(thread.map(renderStatus).join("\n\n---\n\n"));

      if (replies.length) {
        sections.push(`## Replies (${replies.length}${(response.replies ?? []).length > replies.length ? `, capped from ${(response.replies ?? []).length}` : ""})`);
        sections.push(replies.map(renderStatus).join("\n\n---\n\n"));
      }

      const markdown = sections.join("\n\n");

      return textResult(markdown, {
        id: status.id,
        url: status.url,
        mode,
        author_handle: status.author?.screen_name ?? null,
        published_at: publishedAt(status, status.article),
        is_article: Boolean(status.article),
        post_count: thread.length,
        reply_count: replies.length,
        markdown,
      });
    } catch (err) {
      return errorResult(err);
    }
  },
);

/* -------------------------------------------------------------------- main */

async function main(): Promise<void> {
  await server.connect(new StdioServerTransport());
  console.error(`fxarticle-mcp ${VERSION} listening on stdio`);
}

main().catch((err) => {
  console.error("fxarticle-mcp failed to start:", err);
  process.exit(1);
});
