---
name: x-article-fetch
description: Fetch X (Twitter) long-form Articles and posts as clean Markdown using the user's own logged-in X account, via password login or imported browser cookies. Use this whenever the user wants to read, save, archive, summarise, or quote an x.com or twitter.com link and a logged-out reader is not enough — including subscriber-only Articles, posts on accounts that hide content from logged-out visitors, and any x.com URL that returned empty, truncated, or "something went wrong" content from a plain fetch. Also use it when the user mentions X_USERNAME/X_PASSWORD/auth_token, asks to log in to X to grab something, or wants a whole account's Articles pulled down. Prefer this over a generic web fetch for any x.com/twitter.com article link.
---

# Fetching X Articles with an authenticated session

X Articles are long-form posts. They are the awkward case: the post's own `text`
field is empty and the entire body lives in a Draft.js block structure, so a
generic scraper returns nothing useful even when it can reach the page. On top of
that, X serves much of its content only to logged-in sessions.

This skill signs in as the user's own account, opens the Article in a real
browser, captures the JSON the page fetches for itself, and reassembles the body
into Markdown.

## Before using it, know the trade-off

Automated access contravenes X's Terms of Service, which prohibit automated use
without written consent, and accounts do get suspended for it. That is the user's
call to make, not yours — but make sure they have made it knowingly rather than
discovering it afterwards. Two things reduce the risk materially, and both are
worth mentioning the first time:

- **Log in rarely.** Each password login is a fresh chance to trip a challenge,
  and repeated logins are what draws attention. The session cache exists for this
  reason: authenticate once, reuse the cookies for weeks.
- **Never use a primary account.** If an account is going to be suspended, it
  should be one the user can afford to lose.

If the content is public and logged-out-readable, a logged-out reader such as the
FxEmbed API is strictly safer and needs no account at all. Suggest that first when
it would actually work; reach for this skill when it would not.

## Credentials

Credentials are read from the environment only — never from command-line
arguments, which are visible to every other process on the machine via `ps`, and
never written into a file in the repository.

| Variable | Required | Purpose |
|---|---|---|
| `X_USERNAME` | for password login | Handle or email |
| `X_PASSWORD` | for password login | Account password |
| `X_EMAIL` | sometimes | Answers the "confirm your email" interstitial |
| `X_TOTP_SECRET` | if 2FA is on | Base32 secret from the authenticator setup screen |
| `X_AUTH_TOKEN` | alternative | `auth_token` cookie copied from a signed-in browser |
| `X_CT0` | with `X_AUTH_TOKEN` | `ct0` cookie, paired with the above |
| `X_SESSION_PATH` | optional | Where to cache the session (default `~/.cache/x-article-fetch/session.json`) |

**Cookie import is the more reliable path.** Scripted password login is what
triggers captchas, email codes and "unusual activity" holds; a cookie lifted from
a browser the user is already signed into skips that entire flow. If password
login fails twice, stop retrying and suggest the cookie route rather than
hammering the login endpoint — repeated failed logins are exactly what escalates
into a lock.

Never echo a credential back to the user, never write one into a file the repo
tracks, and never put one in a commit message or a shell history line. If the user
pastes a password into the chat, use it via the environment and suggest they
rotate it, since it now lives in the transcript.

## Setup

```bash
pip install playwright
playwright install chromium
```

The session cache holds live auth cookies — anyone who can read it can act as the
account — so it is written owner-only (0600) into a 0700 directory. Leave it out
of version control.

## Usage

```bash
# One article to stdout
python scripts/fetch_article.py https://x.com/user/status/1234567890123456789

# To a file, no images
python scripts/fetch_article.py 1234567890123456789 -o article.md --no-images

# Raw article object instead of Markdown
python scripts/fetch_article.py <url> --format json

# Force a fresh login, with the browser visible so a challenge can be solved by hand
python scripts/fetch_article.py <url> --login --headful
```

The target accepts a full URL from any X mirror (query strings such as `?s=46`
are fine) or a bare numeric ID.

Exit codes are worth reacting to rather than just reporting: `0` success, `1` no
Article body found (usually an ordinary post, or deleted/protected), `2`
authentication failed.

## How it works, and why it is built this way

X's GraphQL query IDs rotate every few weeks, so any client with a hardcoded
endpoint breaks on that schedule. This skill sidesteps that: it loads the article
page in a logged-in browser and listens to the responses the page requests for
itself, then searches those payloads for an object carrying `content.blocks`.
Whatever X renames, the page still has to fetch its own content.

`scripts/draftjs_to_md.py` converts the block structure. A few details in there
are easy to get wrong and worth preserving if you edit it:

- `entityMap` arrives as an **array** of `{key, value}`, not the object classic
  Draft.js uses. Both shapes are handled.
- Inline styles are capitalised (`"Bold"`), so matching is case-insensitive.
- Offsets are **UTF-16 code units**. Python indexes strings by code point, so any
  emoji or astral character would shift every later offset. The converter splices
  in UTF-16 space and decodes at the end — do not "simplify" that to string
  slicing.
- `atomic` blocks reference media by `mediaId`, resolved against the article's
  media entities. Unresolvable media degrades to `*[embedded media]*` rather than
  vanishing, so the reader can tell something was there.

## When it does not find an Article

A missing body is usually not a bug. Check in this order:

1. **Is it actually an Article?** Most x.com links are ordinary posts, which have
   no Draft.js body at all. The script says so and exits `1`.
2. **Is the session still good?** Cookies expire. `--login` re-authenticates.
3. **Did a challenge appear?** Run `--headful` once, solve it by hand, and the
   cached session carries the result forward.

`references/troubleshooting.md` covers the failure modes in more detail — read it
when a run fails in a way the above does not explain.

## Reporting results

Say plainly which path authenticated the session (cached, cookie import, or fresh
login), because that is what the user needs to know to reason about the next run.
If a login challenge was hit, say which kind — a captcha, an email code and a 2FA
prompt need different responses from the user, and "login failed" tells them
nothing actionable.
