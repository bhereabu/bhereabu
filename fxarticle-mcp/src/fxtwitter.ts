/**
 * Thin client for the FxEmbed / FxTwitter public API.
 * https://github.com/FxEmbed/FxEmbed
 *
 * No API key, no account, no cookies. Public rate limit is ~1000 req/min per IP.
 * Set FXTWITTER_BASE_URL to point at your own self-hosted Cloudflare Worker.
 */

export const DEFAULT_BASE_URL = "https://api.fxtwitter.com";

export interface DraftBlock {
  key: string;
  text: string;
  type: string;
  depth?: number;
  data?: Record<string, unknown>;
  entityRanges: Array<{ key: number | string; length: number; offset: number }>;
  inlineStyleRanges: Array<{ length: number; offset: number; style: string }>;
}

export interface DraftEntity {
  type: string; // "MEDIA" | "LINK" | "TWEET" | ...
  mutability?: string;
  data?: {
    url?: string;
    mediaItems?: Array<{ mediaId?: string; localMediaId?: string; mediaCategory?: string }>;
    [k: string]: unknown;
  };
}

/** X returns entityMap as an ARRAY of {key,value}; classic Draft.js uses an object. Support both. */
export type EntityMap = Array<{ key: string; value: DraftEntity }> | Record<string, DraftEntity>;

export interface MediaEntity {
  id?: string;
  media_id?: string;
  media_key?: string;
  media_info?: {
    __typename?: string;
    original_img_url?: string;
    original_img_width?: number;
    original_img_height?: number;
    [k: string]: unknown;
  };
}

export interface FxArticle {
  id: string;
  title: string;
  preview_text?: string;
  created_at?: string;
  modified_at?: string;
  cover_media?: MediaEntity;
  media_entities?: MediaEntity[];
  content?: { blocks: DraftBlock[]; entityMap?: EntityMap };
}

export interface FxAuthor {
  screen_name?: string;
  name?: string;
  url?: string;
  followers?: number;
  description?: string;
}

export interface FxStatus {
  id: string;
  url: string;
  text: string;
  created_at?: string;
  created_timestamp?: number;
  author?: FxAuthor;
  likes?: number;
  reposts?: number;
  replies?: number;
  bookmarks?: number;
  quotes?: number;
  views?: number | null;
  lang?: string | null;
  is_note_tweet?: boolean;
  replying_to?: string | null;
  article?: FxArticle | null;
  media?: Record<string, unknown>;
}

export interface FxStatusResponse {
  code: number;
  message?: string;
  status?: FxStatus | null;
  thread?: FxStatus[] | null;
  replies?: FxStatus[] | null;
  author?: FxAuthor | null;
  cursor?: unknown;
}

export interface FxProfileFeedResponse {
  code: number;
  message?: string;
  results?: FxStatus[];
  cursor?: { top?: string; bottom?: string } | null;
}

export class FxTwitterError extends Error {
  constructor(
    message: string,
    readonly code: number,
    readonly hint?: string,
  ) {
    super(message);
    this.name = "FxTwitterError";
  }
}

/**
 * Accepts a full x.com/twitter.com/fxtwitter.com/vxtwitter.com status URL,
 * a bare numeric status ID, or an id with surrounding whitespace/query string.
 */
export function parseStatusId(input: string): string {
  const raw = input.trim();
  if (/^\d{6,25}$/.test(raw)) return raw;

  const m = raw.match(/(?:^|\/)status(?:es)?\/(\d{6,25})/);
  if (m) return m[1];

  // Last resort: any long digit run in a URL-looking string.
  if (/^https?:\/\//i.test(raw)) {
    const digits = raw.match(/\d{6,25}/);
    if (digits) return digits[0];
  }

  throw new FxTwitterError(
    `Could not extract a post ID from "${input}".`,
    400,
    'Pass a full post URL such as "https://x.com/user/status/1234567890123456789" or the bare numeric ID.',
  );
}

/** Normalize an @handle / profile URL to a bare screen_name. */
export function parseHandle(input: string): string {
  let h = input.trim();
  const urlMatch = h.match(/^https?:\/\/(?:www\.)?(?:x|twitter|fxtwitter|vxtwitter)\.com\/([A-Za-z0-9_]{1,15})/i);
  if (urlMatch) h = urlMatch[1];
  h = h.replace(/^@/, "").split(/[/?#]/)[0];
  if (!/^[A-Za-z0-9_]{1,15}$/.test(h)) {
    throw new FxTwitterError(
      `"${input}" is not a valid X handle.`,
      400,
      'Pass a handle like "startupideaspod", "@startupideaspod", or a profile URL.',
    );
  }
  return h;
}

export interface ClientOptions {
  baseUrl?: string;
  timeoutMs?: number;
  userAgent?: string;
}

export class FxTwitterClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly userAgent: string;

  constructor(opts: ClientOptions = {}) {
    this.baseUrl = (opts.baseUrl ?? process.env.FXTWITTER_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.timeoutMs = opts.timeoutMs ?? Number(process.env.FXTWITTER_TIMEOUT_MS ?? 20000);
    this.userAgent = opts.userAgent ?? "fxarticle-mcp/1.0 (+https://github.com/FxEmbed/FxEmbed)";
  }

  private async get<T>(path: string): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    let res: Response;
    try {
      res = await fetch(url, {
        headers: { "User-Agent": this.userAgent, Accept: "application/json" },
        signal: controller.signal,
      });
    } catch (err) {
      const aborted = err instanceof Error && err.name === "AbortError";
      throw new FxTwitterError(
        aborted
          ? `Request to ${this.baseUrl} timed out after ${this.timeoutMs}ms.`
          : `Network error contacting ${this.baseUrl}: ${(err as Error).message}`,
        504,
        "Check connectivity. If the public instance is degraded, self-host FxEmbed on Cloudflare Workers and set FXTWITTER_BASE_URL.",
      );
    } finally {
      clearTimeout(timer);
    }

    if (res.status === 429) {
      throw new FxTwitterError(
        "Rate limited by the FxTwitter instance (HTTP 429).",
        429,
        "The public API allows ~1000 requests/minute per IP. Back off, or self-host FxEmbed and set FXTWITTER_BASE_URL.",
      );
    }

    let body: unknown;
    const raw = await res.text();
    try {
      body = JSON.parse(raw);
    } catch {
      throw new FxTwitterError(
        `Non-JSON response (HTTP ${res.status}) from ${url}.`,
        res.status,
        "The instance may be down or returning an HTML error page.",
      );
    }

    const payload = body as { code?: number; message?: string };
    const code = payload.code ?? res.status;

    if (code === 401) {
      throw new FxTwitterError(
        "Post is from a protected (private) account.",
        401,
        "FxTwitter reads only logged-out public content, so protected accounts cannot be fetched.",
      );
    }
    if (code === 404) {
      throw new FxTwitterError(
        payload.message ?? "Not found.",
        404,
        "The post may be deleted, the account suspended or protected, or the ID may be wrong.",
      );
    }
    if (code >= 400) {
      throw new FxTwitterError(payload.message ?? `Upstream error (code ${code}).`, code);
    }

    return body as T;
  }

  /** Single post, including the full `article` body when the post is an X Article. */
  status(id: string): Promise<FxStatusResponse> {
    return this.get<FxStatusResponse>(`/2/status/${encodeURIComponent(id)}`);
  }

  /** Post plus the author's self-reply chain. */
  thread(id: string): Promise<FxStatusResponse> {
    return this.get<FxStatusResponse>(`/2/thread/${encodeURIComponent(id)}`);
  }

  /** Post plus thread plus replies from other accounts. */
  conversation(id: string): Promise<FxStatusResponse> {
    return this.get<FxStatusResponse>(`/2/conversation/${encodeURIComponent(id)}`);
  }

  /** An account's Articles. NOTE: returns metadata only — `content.blocks` is empty. */
  profileArticles(handle: string, cursor?: string): Promise<FxProfileFeedResponse> {
    const q = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
    return this.get<FxProfileFeedResponse>(`/2/profile/${encodeURIComponent(handle)}/articles${q}`);
  }

  /** An account's recent posts. */
  profileStatuses(handle: string, cursor?: string): Promise<FxProfileFeedResponse> {
    const q = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
    return this.get<FxProfileFeedResponse>(`/2/profile/${encodeURIComponent(handle)}/statuses${q}`);
  }
}
