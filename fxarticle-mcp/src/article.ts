/**
 * Converts X Article bodies (Draft.js block format, as returned by FxTwitter)
 * into clean Markdown.
 *
 * Notes on the real-world shape, verified against live API responses:
 *  - `entityMap` arrives as an ARRAY of {key, value}, not the classic Draft.js object.
 *  - Inline styles are capitalised ("Bold"), not Draft's usual "BOLD".
 *  - `atomic` blocks carry a single-space `text` and one entityRange pointing at a
 *    MEDIA entity, whose mediaId must be resolved against `article.media_entities`.
 *  - Offsets/lengths are UTF-16 code units, which matches JS string indexing.
 */

import type { DraftBlock, DraftEntity, EntityMap, FxArticle, MediaEntity } from "./fxtwitter.js";

export interface RenderOptions {
  /** Emit `![alt](url)` for embedded media. Default true. */
  includeImages?: boolean;
  /** Prepend an H1 title and a byline/date metadata block. Default true. */
  includeFrontMatter?: boolean;
}

function normalizeEntityMap(entityMap?: EntityMap): Map<string, DraftEntity> {
  const out = new Map<string, DraftEntity>();
  if (!entityMap) return out;
  if (Array.isArray(entityMap)) {
    for (const item of entityMap) {
      if (item && item.key != null) out.set(String(item.key), item.value);
    }
  } else {
    for (const [k, v] of Object.entries(entityMap)) out.set(String(k), v);
  }
  return out;
}

function indexMedia(article: FxArticle): Map<string, MediaEntity> {
  const out = new Map<string, MediaEntity>();
  const push = (m?: MediaEntity) => {
    if (!m) return;
    if (m.media_id) out.set(String(m.media_id), m);
    if (m.media_key) out.set(String(m.media_key), m);
    if (m.id) out.set(String(m.id), m);
  };
  (article.media_entities ?? []).forEach(push);
  push(article.cover_media);
  return out;
}

const STYLE_WRAPPERS: Record<string, [string, string]> = {
  bold: ["**", "**"],
  italic: ["_", "_"],
  underline: ["<u>", "</u>"],
  strikethrough: ["~~", "~~"],
  code: ["`", "`"],
};

interface Insertion {
  offset: number;
  text: string;
  /** Closing markers must be applied before opening markers at the same offset. */
  priority: number;
}

/**
 * Applies inline styles and LINK entities to a block's text.
 * Insertions are collected then applied right-to-left so earlier offsets stay valid.
 */
function renderInline(block: DraftBlock, entities: Map<string, DraftEntity>): string {
  const text = block.text ?? "";
  if (!text) return "";

  const insertions: Insertion[] = [];

  for (const range of block.inlineStyleRanges ?? []) {
    const wrapper = STYLE_WRAPPERS[String(range.style).toLowerCase()];
    if (!wrapper) continue;
    const start = Math.max(0, range.offset);
    const end = Math.min(text.length, range.offset + range.length);
    if (end <= start) continue;
    insertions.push({ offset: start, text: wrapper[0], priority: 1 });
    insertions.push({ offset: end, text: wrapper[1], priority: 0 });
  }

  for (const range of block.entityRanges ?? []) {
    const entity = entities.get(String(range.key));
    if (!entity) continue;
    const url = entity.data?.url;
    if (String(entity.type).toUpperCase() !== "LINK" || !url) continue;
    const start = Math.max(0, range.offset);
    const end = Math.min(text.length, range.offset + range.length);
    if (end <= start) continue;
    insertions.push({ offset: start, text: "[", priority: 1 });
    insertions.push({ offset: end, text: `](${url})`, priority: 0 });
  }

  if (insertions.length === 0) return text;

  insertions.sort((a, b) => b.offset - a.offset || a.priority - b.priority);

  let out = text;
  for (const ins of insertions) {
    out = out.slice(0, ins.offset) + ins.text + out.slice(ins.offset);
  }
  return out;
}

function mediaMarkdown(
  block: DraftBlock,
  entities: Map<string, DraftEntity>,
  media: Map<string, MediaEntity>,
): string | null {
  for (const range of block.entityRanges ?? []) {
    const entity = entities.get(String(range.key));
    if (!entity) continue;
    const type = String(entity.type).toUpperCase();

    if (type === "MEDIA") {
      const urls: string[] = [];
      for (const item of entity.data?.mediaItems ?? []) {
        const found = item.mediaId ? media.get(String(item.mediaId)) : undefined;
        const url = found?.media_info?.original_img_url;
        if (url) urls.push(`![](${url})`);
      }
      if (urls.length) return urls.join("\n\n");
      return "*[embedded media]*";
    }

    if (type === "TWEET" || type === "LINK") {
      const url = entity.data?.url;
      if (url) return `> [${url}](${url})`;
    }
  }
  return null;
}

const HEADER_LEVELS: Record<string, number> = {
  "header-one": 1,
  "header-two": 2,
  "header-three": 3,
  "header-four": 4,
  "header-five": 5,
  "header-six": 6,
};

/** Renders the article body blocks to Markdown (no title/metadata). */
export function renderBlocks(article: FxArticle, opts: RenderOptions = {}): string {
  const includeImages = opts.includeImages ?? true;
  const blocks = article.content?.blocks ?? [];
  const entities = normalizeEntityMap(article.content?.entityMap);
  const media = indexMedia(article);

  const parts: string[] = [];
  let orderedCounter = 0;

  for (const block of blocks) {
    const type = block.type ?? "unstyled";

    if (type !== "ordered-list-item") orderedCounter = 0;

    if (type === "atomic") {
      if (!includeImages) continue;
      const md = mediaMarkdown(block, entities, media);
      if (md) parts.push(md);
      continue;
    }

    const inline = renderInline(block, entities);
    const indent = "  ".repeat(Math.max(0, block.depth ?? 0));

    if (!inline.trim() && type !== "unstyled") continue;

    const headerLevel = HEADER_LEVELS[type];
    if (headerLevel) {
      parts.push(`${"#".repeat(headerLevel)} ${inline.trim()}`);
      continue;
    }

    switch (type) {
      case "unordered-list-item":
        parts.push(`${indent}- ${inline.trim()}`);
        break;
      case "ordered-list-item":
        orderedCounter += 1;
        parts.push(`${indent}${orderedCounter}. ${inline.trim()}`);
        break;
      case "blockquote":
        parts.push(
          inline
            .split("\n")
            .map((l) => `> ${l}`)
            .join("\n"),
        );
        break;
      case "code-block":
        parts.push("```\n" + inline + "\n```");
        break;
      default:
        if (inline.trim()) parts.push(inline);
        break;
    }
  }

  // Merge consecutive list items into single blocks so Markdown renders them as one list.
  const merged: string[] = [];
  for (const part of parts) {
    const isListItem = /^\s*(?:-|\d+\.)\s/.test(part);
    const prev = merged[merged.length - 1];
    if (isListItem && prev && /^\s*(?:-|\d+\.)\s/.test(prev.split("\n").pop() ?? "")) {
      merged[merged.length - 1] = `${prev}\n${part}`;
    } else {
      merged.push(part);
    }
  }

  return merged.join("\n\n").replace(/\n{3,}/g, "\n\n").trim();
}

/** Full Markdown document: title, byline, cover image, then body. */
export function renderArticleMarkdown(
  article: FxArticle,
  meta: { authorName?: string; authorHandle?: string; url?: string; createdAt?: string; publishedAt?: string },
  opts: RenderOptions = {},
): string {
  const includeFrontMatter = opts.includeFrontMatter ?? true;
  const includeImages = opts.includeImages ?? true;
  const sections: string[] = [];

  if (includeFrontMatter) {
    sections.push(`# ${article.title ?? "(untitled article)"}`);
    const bits: string[] = [];
    if (meta.authorName || meta.authorHandle) {
      bits.push(`**Author:** ${meta.authorName ?? ""}${meta.authorHandle ? ` (@${meta.authorHandle})` : ""}`.trim());
    }
    const date = meta.publishedAt ?? article.created_at ?? meta.createdAt;
    if (date) bits.push(`**Published:** ${date}`);
    if (meta.url) bits.push(`**Source:** ${meta.url}`);
    if (bits.length) sections.push(bits.join("  \n"));
  }

  const cover = article.cover_media?.media_info?.original_img_url;
  if (includeImages && cover) sections.push(`![cover](${cover})`);

  const body = renderBlocks(article, opts);
  sections.push(body || "*(This article has no readable body blocks.)*");

  return sections.join("\n\n").trim();
}

/** Rough word count of the rendered body, useful for previews. */
export function wordCount(article: FxArticle): number {
  const text = (article.content?.blocks ?? [])
    .filter((b) => b.type !== "atomic")
    .map((b) => b.text ?? "")
    .join(" ");
  return text.split(/\s+/).filter(Boolean).length;
}
