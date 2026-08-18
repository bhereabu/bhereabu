import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from draftjs_to_md import render_article, render_inline, word_count, normalize_entity_map
from xauth import totp_now

fails = []
def check(name, got, want):
    if got != want:
        fails.append(f"{name}\n   got:  {got!r}\n   want: {want!r}")
    print(("PASS " if got == want else "FAIL ") + name)

# --- UTF-16 offset handling: the documented gotcha for a Python port ---
# "Emoji 🚀 and CJK 日本語" — 🚀 is 2 UTF-16 code units but 1 Python code point.
# Bolding "and" sits at UTF-16 offset 9; a naive code-point splice would land at 8.
blk = {"text": "Emoji 🚀 and CJK 日本語 end", "type": "unstyled",
       "inlineStyleRanges": [{"offset": 9, "length": 3, "style": "Bold"}], "entityRanges": []}
check("utf16: bold lands on the right word past an emoji",
      render_inline(blk, {}), "Emoji 🚀 **and** CJK 日本語 end")

# Style after two astral chars (4 UTF-16 units of drift)
blk2 = {"text": "🚀🚀 tail", "type": "unstyled",
        "inlineStyleRanges": [{"offset": 5, "length": 4, "style": "Italic"}], "entityRanges": []}
check("utf16: offset past two emoji", render_inline(blk2, {}), "🚀🚀 _tail_")

# --- entityMap array form + capitalised styles + link ---
blk3 = {"text": "Ideas come from pain, not brainstorms. See fxembed for details.", "type": "unstyled",
        "inlineStyleRanges": [{"offset": 16, "length": 4, "style": "Bold"},
                              {"offset": 26, "length": 11, "style": "Italic"}],
        "entityRanges": [{"key": 0, "offset": 43, "length": 7}]}
ents = normalize_entity_map([{"key": "0", "value": {"type": "LINK", "data": {"url": "https://ex.com"}}}])
check("array entityMap + capitalised styles + link",
      render_inline(blk3, ents),
      "Ideas come from **pain**, not _brainstorms_. See [fxembed](https://ex.com) for details.")

# --- overlapping ranges: closing marker must precede opening at same offset ---
blk4 = {"text": "abcdef", "type": "unstyled",
        "inlineStyleRanges": [{"offset": 0, "length": 3, "style": "Bold"},
                              {"offset": 3, "length": 3, "style": "Italic"}], "entityRanges": []}
check("adjacent ranges do not interleave", render_inline(blk4, {}), "**abc**_def_")

# --- full document ---
article = {
    "title": "T", "created_at": "2026-08-10T12:00:00Z",
    "cover_media": {"media_id": "c", "media_info": {"original_img_url": "https://img/c.jpg"}},
    "media_entities": [{"media_id": "m1", "media_info": {"original_img_url": "https://img/1.jpg"}}],
    "content": {"blocks": [
        {"key": "1", "type": "header-two", "text": "H", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "2", "type": "unordered-list-item", "text": "a", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "3", "type": "unordered-list-item", "text": "b", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "4", "type": "ordered-list-item", "text": "x", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "5", "type": "ordered-list-item", "text": "y", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "6", "type": "blockquote", "text": "q", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "7", "type": "code-block", "text": "code()", "entityRanges": [], "inlineStyleRanges": []},
        {"key": "8", "type": "atomic", "text": " ",
         "entityRanges": [{"key": 1, "offset": 0, "length": 1}], "inlineStyleRanges": []},
        {"key": "9", "type": "atomic", "text": " ",
         "entityRanges": [{"key": 2, "offset": 0, "length": 1}], "inlineStyleRanges": []},
    ], "entityMap": [
        {"key": "1", "value": {"type": "MEDIA", "data": {"mediaItems": [{"mediaId": "m1"}]}}},
        {"key": "2", "value": {"type": "MEDIA", "data": {"mediaItems": [{"mediaId": "nope"}]}}},
    ]},
}
md = render_article(article, meta={"author_handle": "u", "author_name": "U", "url": "https://x.com/s/1"})
print("\n--- rendered ---\n" + md + "\n----------------")
for want in ["# T", "**Author:** U (@u)", "![cover](https://img/c.jpg)", "## H",
             "- a\n- b", "1. x\n2. y", "> q", "```\ncode()\n```",
             "![](https://img/1.jpg)", "*[embedded media]*"]:
    check(f"document contains {want!r}", want in md, True)

check("consecutive lists merged into one block", md.count("- a\n- b"), 1)
check("word_count ignores atomic blocks", word_count(article), 7)

# --- empty body ---
check("empty body degrades gracefully",
      "*(This article has no readable body blocks.)*" in render_article({"title": "E", "content": {"blocks": []}}), True)

# --- TOTP against RFC 6238 test vector (SHA1, secret "12345678901234567890") ---
import base64
secret = base64.b32encode(b"12345678901234567890").decode()
check("TOTP matches RFC 6238 vector at t=59", totp_now(secret, when=59), "287082")
check("TOTP matches RFC 6238 vector at t=1111111109", totp_now(secret, when=1111111109), "081804")

print("\n" + ("ALL PASS" if not fails else f"{len(fails)} FAILURE(S):\n" + "\n".join(fails)))
sys.exit(1 if fails else 0)
