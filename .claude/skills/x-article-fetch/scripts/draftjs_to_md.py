"""Convert X Article bodies (Draft.js block format) to Markdown.

X stores long-form Articles as Draft.js blocks rather than plain text, and the
post's own `text` field is empty, so a generic scraper recovers nothing. This
module reassembles the block structure.

Real-world shape notes, which differ from classic Draft.js:
  - `entityMap` may arrive as an ARRAY of {key, value} rather than an object.
  - Inline styles are capitalised ("Bold"), not Draft's usual "BOLD".
  - `atomic` blocks carry a single-space `text` plus one entityRange pointing at
    a MEDIA entity, whose mediaId resolves against the article's media entities.

Offsets are UTF-16 code units. Python strings index by code point, so any text
containing astral characters (emoji, some CJK) would shift every offset after it
if we indexed naively. We therefore splice in UTF-16 space and decode at the end.
"""

from __future__ import annotations

from typing import Any, Iterable

STYLE_WRAPPERS: dict[str, tuple[str, str]] = {
    "bold": ("**", "**"),
    "italic": ("_", "_"),
    "underline": ("<u>", "</u>"),
    "strikethrough": ("~~", "~~"),
    "code": ("`", "`"),
}

HEADER_LEVELS: dict[str, int] = {
    "header-one": 1,
    "header-two": 2,
    "header-three": 3,
    "header-four": 4,
    "header-five": 5,
    "header-six": 6,
}


def normalize_entity_map(entity_map: Any) -> dict[str, dict]:
    """Accept both the array form X returns and the classic Draft.js object."""
    out: dict[str, dict] = {}
    if not entity_map:
        return out
    if isinstance(entity_map, list):
        for item in entity_map:
            if isinstance(item, dict) and item.get("key") is not None:
                out[str(item["key"])] = item.get("value") or {}
    elif isinstance(entity_map, dict):
        for key, value in entity_map.items():
            out[str(key)] = value or {}
    return out


def index_media(article: dict) -> dict[str, dict]:
    """Map every id a media entity might be referenced by to that entity."""
    out: dict[str, dict] = {}

    def push(media: Any) -> None:
        if not isinstance(media, dict):
            return
        for key in ("media_id", "media_key", "id"):
            if media.get(key):
                out[str(media[key])] = media

    for media in article.get("media_entities") or []:
        push(media)
    push(article.get("cover_media"))
    return out


def _media_url(media: dict) -> str | None:
    info = media.get("media_info") or {}
    return (
        info.get("original_img_url")
        or media.get("original_img_url")
        or media.get("media_url_https")
        or media.get("url")
    )


def render_inline(block: dict, entities: dict[str, dict]) -> str:
    """Apply inline styles and LINK entities to one block's text.

    Insertions are collected and applied right-to-left so that earlier offsets
    stay valid as we splice, with closing markers ordered before opening markers
    at the same offset so nested ranges don't interleave incorrectly.
    """
    text = block.get("text") or ""
    if not text:
        return ""

    units = bytearray(text.encode("utf-16-le"))
    length_u16 = len(units) // 2

    # (offset, kind, tiebreak, marker) where kind 0 opens and 1 closes.
    #
    # Insertions are applied right-to-left, and each insertion at a given offset
    # pushes previously-inserted text rightwards — so whatever is applied *last*
    # ends up leftmost. Two consequences drive the sort:
    #   - At one offset, a closing marker must sit left of an opening one, so that
    #     "**bold**_italic_" does not come out as "**bold_**italic_". Opens are
    #     therefore applied first, closes last.
    #   - Among markers of the same kind at one offset, the outer (longer) range
    #     must sit outside the inner one: longer opens applied last, longer closes
    #     applied first.
    insertions: list[tuple[int, int, int, str]] = []

    for rng in block.get("inlineStyleRanges") or []:
        wrapper = STYLE_WRAPPERS.get(str(rng.get("style", "")).lower())
        if not wrapper:
            continue
        start = max(0, int(rng.get("offset", 0)))
        end = min(length_u16, start + int(rng.get("length", 0)))
        if end <= start:
            continue
        span = end - start
        insertions.append((start, 0, span, wrapper[0]))
        insertions.append((end, 1, -span, wrapper[1]))

    for rng in block.get("entityRanges") or []:
        entity = entities.get(str(rng.get("key")))
        if not entity:
            continue
        if str(entity.get("type", "")).upper() != "LINK":
            continue
        url = (entity.get("data") or {}).get("url")
        if not url:
            continue
        start = max(0, int(rng.get("offset", 0)))
        end = min(length_u16, start + int(rng.get("length", 0)))
        if end <= start:
            continue
        span = end - start
        insertions.append((start, 0, span, "["))
        insertions.append((end, 1, -span, f"]({url})"))

    if not insertions:
        return text

    insertions.sort(key=lambda item: (-item[0], item[1], item[2]))
    for offset, _kind, _tiebreak, marker in insertions:
        units[offset * 2 : offset * 2] = marker.encode("utf-16-le")

    return units.decode("utf-16-le")


def media_markdown(block: dict, entities: dict[str, dict], media: dict[str, dict]) -> str | None:
    """Resolve an atomic block to an image, a quoted link, or a placeholder.

    Media that cannot be resolved degrades to a visible marker rather than
    disappearing, so a reader can tell something was there.
    """
    for rng in block.get("entityRanges") or []:
        entity = entities.get(str(rng.get("key")))
        if not entity:
            continue
        etype = str(entity.get("type", "")).upper()
        data = entity.get("data") or {}

        if etype == "MEDIA":
            urls = []
            for item in data.get("mediaItems") or []:
                found = media.get(str(item.get("mediaId"))) if item.get("mediaId") else None
                url = _media_url(found) if found else None
                if url:
                    urls.append(f"![]({url})")
            if urls:
                return "\n\n".join(urls)
            return "*[embedded media]*"

        if etype in ("TWEET", "LINK"):
            url = data.get("url")
            if url:
                return f"> [{url}]({url})"
    return None


def _merge_lists(parts: Iterable[str]) -> list[str]:
    """Join consecutive list items so Markdown renders one list, not several."""
    merged: list[str] = []
    for part in parts:
        is_item = part.lstrip().startswith(("- ", "1. ")) or (
            part.lstrip()[:3].rstrip(". ").isdigit() and ". " in part[:6]
        )
        if is_item and merged:
            prev_last_line = merged[-1].split("\n")[-1].lstrip()
            prev_is_item = prev_last_line.startswith("- ") or (
                prev_last_line[:3].rstrip(". ").isdigit() and ". " in prev_last_line[:6]
            )
            if prev_is_item:
                merged[-1] = f"{merged[-1]}\n{part}"
                continue
        merged.append(part)
    return merged


def render_blocks(article: dict, include_images: bool = True) -> str:
    """Render the article body to Markdown, without title or metadata."""
    content = article.get("content") or {}
    blocks = content.get("blocks") or []
    entities = normalize_entity_map(content.get("entityMap"))
    media = index_media(article)

    parts: list[str] = []
    ordered_counter = 0

    for block in blocks:
        btype = block.get("type") or "unstyled"

        if btype != "ordered-list-item":
            ordered_counter = 0

        if btype == "atomic":
            if not include_images:
                continue
            rendered = media_markdown(block, entities, media)
            if rendered:
                parts.append(rendered)
            continue

        inline = render_inline(block, entities)
        indent = "  " * max(0, int(block.get("depth") or 0))

        if not inline.strip() and btype != "unstyled":
            continue

        level = HEADER_LEVELS.get(btype)
        if level:
            parts.append(f"{'#' * level} {inline.strip()}")
            continue

        if btype == "unordered-list-item":
            parts.append(f"{indent}- {inline.strip()}")
        elif btype == "ordered-list-item":
            ordered_counter += 1
            parts.append(f"{indent}{ordered_counter}. {inline.strip()}")
        elif btype == "blockquote":
            parts.append("\n".join(f"> {line}" for line in inline.split("\n")))
        elif btype == "code-block":
            parts.append(f"```\n{inline}\n```")
        elif inline.strip():
            parts.append(inline)

    body = "\n\n".join(_merge_lists(parts))
    while "\n\n\n" in body:
        body = body.replace("\n\n\n", "\n\n")
    return body.strip()


def render_article(
    article: dict,
    meta: dict | None = None,
    include_images: bool = True,
    include_front_matter: bool = True,
) -> str:
    """Full Markdown document: title, byline, cover image, then body."""
    meta = meta or {}
    sections: list[str] = []

    if include_front_matter:
        sections.append(f"# {article.get('title') or '(untitled article)'}")
        bits = []
        author_name = meta.get("author_name")
        author_handle = meta.get("author_handle")
        if author_name or author_handle:
            who = author_name or ""
            if author_handle:
                who = f"{who} (@{author_handle})".strip()
            bits.append(f"**Author:** {who}")
        published = meta.get("published_at") or article.get("created_at")
        if published:
            bits.append(f"**Published:** {published}")
        if meta.get("url"):
            bits.append(f"**Source:** {meta['url']}")
        if bits:
            sections.append("  \n".join(bits))

    cover = article.get("cover_media")
    cover_url = _media_url(cover) if isinstance(cover, dict) else None
    if include_images and cover_url:
        sections.append(f"![cover]({cover_url})")

    body = render_blocks(article, include_images=include_images)
    sections.append(body or "*(This article has no readable body blocks.)*")

    return "\n\n".join(sections).strip()


def word_count(article: dict) -> int:
    blocks = (article.get("content") or {}).get("blocks") or []
    text = " ".join(b.get("text") or "" for b in blocks if b.get("type") != "atomic")
    return len(text.split())
