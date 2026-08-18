"""Authenticate to X and cache the resulting browser session.

Credentials are read from the environment, never from command-line arguments,
because arguments are visible to any other process via `ps`. Nothing in this
module prints a credential; failures report which step failed, not what was sent.

Logging in is the expensive and risky part of talking to X: each password login
is a fresh chance to trip an "unusual activity" challenge, and repeated logins
are what get accounts flagged. So we log in at most once and reuse the resulting
cookies until they stop working.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import struct
import sys
import time
from pathlib import Path

LOGIN_URL = "https://x.com/i/flow/login"
HOME_URL = "https://x.com/home"

DEFAULT_SESSION_PATH = Path(
    os.environ.get("X_SESSION_PATH")
    or Path.home() / ".cache" / "x-article-fetch" / "session.json"
)


class AuthError(RuntimeError):
    """Raised when authentication cannot complete. Never carries a credential."""


def log(message: str) -> None:
    """Progress goes to stderr so stdout stays clean for article output."""
    print(f"[x-article-fetch] {message}", file=sys.stderr)


# --------------------------------------------------------------------- TOTP


def totp_now(secret: str, when: int | None = None) -> str:
    """RFC 6238 TOTP, implemented here to avoid a dependency for ~15 lines.

    `secret` is the base32 string X shows when you enable an authenticator app.
    """
    cleaned = secret.strip().replace(" ", "").upper()
    padding = "=" * (-len(cleaned) % 8)
    try:
        key = base64.b32decode(cleaned + padding)
    except Exception as exc:  # noqa: BLE001 - surface a clear message, not a stack
        raise AuthError("X_TOTP_SECRET is not valid base32.") from exc

    counter = int((when or time.time()) // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code % 1_000_000:06d}"


# ------------------------------------------------------------------ session


def load_session(path: Path = DEFAULT_SESSION_PATH) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        log(f"Session cache at {path} is unreadable; ignoring it.")
        return None


def save_session(state: dict, path: Path = DEFAULT_SESSION_PATH) -> None:
    """Write the session with owner-only permissions.

    The file contains live auth cookies — anyone who can read it can act as the
    account, so it is created 0600 and the parent directory 0700.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    log(f"Session cached at {path} (owner-only).")


def session_from_cookies() -> dict | None:
    """Build a session from X_AUTH_TOKEN / X_CT0 instead of logging in.

    Copying the cookies out of a browser you are already signed into avoids the
    scripted-login challenge flow entirely, which is why it is worth supporting.
    """
    auth_token = os.environ.get("X_AUTH_TOKEN")
    ct0 = os.environ.get("X_CT0")
    if not auth_token:
        return None

    cookies = [
        {
            "name": "auth_token",
            "value": auth_token,
            "domain": ".x.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "None",
        }
    ]
    if ct0:
        cookies.append(
            {
                "name": "ct0",
                "value": ct0,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            }
        )
    log("Using auth cookies from X_AUTH_TOKEN/X_CT0.")
    return {"cookies": cookies, "origins": []}


# -------------------------------------------------------------------- login


def _credentials() -> tuple[str, str]:
    username = os.environ.get("X_USERNAME")
    password = os.environ.get("X_PASSWORD")
    if not username or not password:
        raise AuthError(
            "Set X_USERNAME and X_PASSWORD in the environment (or X_AUTH_TOKEN to "
            "reuse browser cookies). Do not pass credentials as command-line arguments."
        )
    return username, password


def _fill_first(page, selectors: list[str], value: str, timeout_ms: int = 8000) -> bool:
    """Try several selectors because X's login DOM changes without notice."""
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=timeout_ms, state="visible")
        except Exception:  # noqa: BLE001 - selector simply absent; try the next
            continue
        if element:
            element.fill(value)
            return True
    return False


def _click_first(page, selectors: list[str], timeout_ms: int = 8000) -> bool:
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=timeout_ms, state="visible")
        except Exception:  # noqa: BLE001
            continue
        if element:
            element.click()
            return True
    return False


def interactive_login(playwright, headless: bool = True, session_path: Path = DEFAULT_SESSION_PATH) -> dict:
    """Drive X's login flow and return a Playwright storage_state dict.

    X's flow is a sequence of screens rather than one form, and which screens
    appear depends on the account: it may ask for the password immediately, or
    interject an email/phone confirmation, or ask for a 2FA code. We therefore
    react to whatever screen is on-screen instead of assuming a fixed order.
    """
    username, password = _credentials()
    email = os.environ.get("X_EMAIL")
    totp_secret = os.environ.get("X_TOTP_SECRET")

    browser = playwright.chromium.launch(
        headless=headless,
        executable_path=os.environ.get("X_CHROMIUM_PATH") or None,
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        locale="en-US",
    )
    page = context.new_page()

    try:
        log("Opening the login flow.")
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=45_000)

        if not _fill_first(page, ['input[autocomplete="username"]', 'input[name="text"]'], username, 20_000):
            raise AuthError("Could not find the username field — X's login page has changed.")
        _click_first(page, ['button:has-text("Next")', 'div[role="button"]:has-text("Next")'])

        # Work through whatever screens appear, in whatever order they appear.
        for _ in range(6):
            page.wait_for_timeout(1500)

            if page.query_selector('input[name="password"]'):
                _fill_first(page, ['input[name="password"]'], password)
                _click_first(page, ['button[data-testid="LoginForm_Login_Button"]', 'button:has-text("Log in")'])
                continue

            # "Enter your phone number or email address" interstitial.
            challenge = page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
            if challenge:
                if not email:
                    raise AuthError(
                        "X asked for a confirmation email or phone number. Set X_EMAIL "
                        "to the address on the account and retry."
                    )
                challenge.fill(email)
                _click_first(page, ['button:has-text("Next")', 'div[role="button"]:has-text("Next")'])
                continue

            # Two-factor code.
            twofa = page.query_selector('input[data-testid="ocfEnterTextTextInput"][name="text"]')
            if twofa and totp_secret:
                twofa.fill(totp_now(totp_secret))
                _click_first(page, ['button:has-text("Next")', 'button:has-text("Log in")'])
                continue

            if "/home" in page.url or page.query_selector('[data-testid="SideNav_AccountSwitcher_Button"]'):
                break

        page.goto(HOME_URL, wait_until="domcontentloaded", timeout=45_000)
        page.wait_for_timeout(2000)

        if "/login" in page.url or "/i/flow/login" in page.url:
            raise AuthError(
                "Login did not complete. X most likely presented a challenge this script "
                "could not answer (captcha, or a code sent to email/SMS). Run with "
                "--headful to solve it by hand once, or export X_AUTH_TOKEN from a "
                "browser you are already signed into."
            )

        state = context.storage_state()
        save_session(state, session_path)
        log("Logged in.")
        return state
    finally:
        context.close()
        browser.close()


def get_session(playwright, session_path: Path = DEFAULT_SESSION_PATH, headless: bool = True, force_login: bool = False) -> dict:
    """Return a usable session, preferring cached cookies over a fresh login."""
    if not force_login:
        from_env = session_from_cookies()
        if from_env:
            return from_env
        cached = load_session(session_path)
        if cached:
            log("Reusing cached session.")
            return cached
    return interactive_login(playwright, headless=headless, session_path=session_path)
