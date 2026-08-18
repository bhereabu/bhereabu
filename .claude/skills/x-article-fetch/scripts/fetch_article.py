#!/usr/bin/env python3
"""Fetch an X (Twitter) Article as Markdown using an authenticated session.

Rather than reimplementing X's GraphQL calls — whose query IDs rotate every few
weeks and break any hardcoded client — this opens the article in a real logged-in
browser and captures the JSON the page fetches for itself. Whatever X changes
about its endpoint names, the page still has to ask for its own content, and we
read that. The Draft.js body is then reassembled into Markdown.

Usage:
    export X_USERNAME=... X_PASSWORD=...
    python fetch_article.py https://x.com/user/status/123 -o article.md

Credentials come from the environment only. See xauth.py for the full list.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draftjs_to_md import render_article, word_count  # noqa: E402
from xauth import DEFAULT_SESSION_PATH, AuthError, get_session, log  # noqa: E402

STATUS_RE = re.compile(r"(?:^|/)(?:status(?:es)?|article)/(\d{6,25})")
BARE_ID_RE = re.compile(r"^\d{6,25}$")


def parse_target(value: str) -> str:
    """Accept a full URL (any x/twitter mirror, query strings fine) or a bare ID."""
    raw = value.strip()
    if BARE_ID_RE.match(raw):
        return raw
    match = STATUS_RE.search(raw)
    if match:
        return match.group(1)
    if raw.startswith(("http://", "https://")):
        digits = re.search(r"\d{6,25}", raw)
        if digits:
            return digits.group(0)
    raise SystemExit(
        f'Could not extract a post ID from "{value}". Pass a URL like '
        "https://x.com/user/status/1234567890123456789 or the bare numeric ID."
    )


def find_article(node, depth: int = 0):
    """Recursively locate an article object inside an arbitrary JSON response.

    We look for the shape rather than a fixed path: an object carrying a
    `content.blocks` list is an article body wherever X chooses to nest it.
    """
    if depth > 25:
        return None
    if isinstance(node, dict):
        content = node.get("content")
        if isinstance(content, dict) and isinstance(content.get("blocks"), list) and content["blocks"]:
            return node
        # Some payloads wrap the body one level further down.
        for key in ("article", "article_results", "result", "data"):
            if key in node:
                found = find_article(node[key], depth + 1)
                if found:
                    return found
        for value in node.values():
            found = find_article(value, depth + 1)
            if found:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_article(item, depth + 1)
            if found:
                return found
    return None


def extract_meta(payload) -> dict:
    """Pull author handle/name out of whatever user object the payload carries."""
    meta: dict = {}

    def walk(node, depth=0):
        if depth > 25 or meta.get("author_handle"):
            return
        if isinstance(node, dict):
            legacy = node.get("legacy") if isinstance(node.get("legacy"), dict) else node
            if isinstance(legacy, dict) and legacy.get("screen_name"):
                meta["author_handle"] = legacy.get("screen_name")
                meta["author_name"] = legacy.get("name")
                return
            for value in node.values():
                walk(value, depth + 1)
        elif isinstance(node, list):
            for item in node:
                walk(item, depth + 1)

    walk(payload)
    return meta


def fetch(status_id: str, session_path: Path, headless: bool, force_login: bool, timeout_s: int):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Run:\n"
            "    pip install playwright && playwright install chromium"
        ) from exc

    url = f"https://x.com/i/status/{status_id}"
    captured: list = []

    with sync_playwright() as playwright:
        state = get_session(playwright, session_path, headless=headless, force_login=force_login)

        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=state, viewport={"width": 1280, "height": 1400}, locale="en-US")
        page = context.new_page()

        def on_response(response):
            # The article body only ever arrives as JSON from X's own API hosts.
            if "/graphql/" not in response.url and "/i/api/" not in response.url:
                return
            try:
                if "application/json" not in (response.headers.get("content-type") or ""):
                    return
                captured.append(response.json())
            except Exception:  # noqa: BLE001 - a response we cannot read is not fatal
                pass

        page.on("response", on_response)

        log(f"Opening {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_s * 1000)

        if "/login" in page.url or "/i/flow/login" in page.url:
            context.close()
            browser.close()
            raise AuthError(
                "The cached session is no longer valid. Re-run with --login to "
                "authenticate again."
            )

        # Articles lazy-load their body; give the page a chance to request it.
        page.wait_for_timeout(3000)
        for _ in range(6):
            if any(find_article(payload) for payload in captured):
                break
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1500)

        page_title = page.title()
        context.close()
        browser.close()

    for payload in captured:
        article = find_article(payload)
        if article:
            return article, extract_meta(payload), page_title

    return None, {}, page_title


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch an X Article as Markdown using an authenticated session."
    )
    parser.add_argument("target", help="Article/post URL or bare numeric ID")
    parser.add_argument("-o", "--out", help="Write to this file instead of stdout")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--no-images", action="store_true", help="Omit embedded media")
    parser.add_argument("--no-front-matter", action="store_true", help="Omit title/author header")
    parser.add_argument("--login", action="store_true", help="Force a fresh login, ignoring any cached session")
    parser.add_argument("--headful", action="store_true", help="Show the browser — use this to solve a challenge by hand")
    parser.add_argument("--session", default=str(DEFAULT_SESSION_PATH), help="Session cache path")
    parser.add_argument("--timeout", type=int, default=60, help="Page load timeout in seconds")
    args = parser.parse_args()

    status_id = parse_target(args.target)

    try:
        article, meta, page_title = fetch(
            status_id,
            Path(args.session),
            headless=not args.headful,
            force_login=args.login,
            timeout_s=args.timeout,
        )
    except AuthError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        return 2

    if not article:
        print(
            f"No Article body found for {status_id}.\n"
            f"Page title was: {page_title!r}\n"
            "This usually means the post is an ordinary tweet rather than a long-form "
            "Article, or it is deleted/protected. Nothing was written.",
            file=sys.stderr,
        )
        return 1

    meta["url"] = f"https://x.com/i/status/{status_id}"
    meta["published_at"] = article.get("created_at")

    if args.format == "json":
        output = json.dumps(article, indent=2, ensure_ascii=False)
    else:
        output = render_article(
            article,
            meta=meta,
            include_images=not args.no_images,
            include_front_matter=not args.no_front_matter,
        )

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        log(f"Wrote {args.out} ({word_count(article)} words).")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
