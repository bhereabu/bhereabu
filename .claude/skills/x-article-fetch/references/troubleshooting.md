# Troubleshooting

Read this when a run fails in a way the SKILL.md checklist does not explain.

## Authentication

### "Login did not complete" (exit 2)

X presented a screen the script could not answer. In practice this is one of:

| What appeared | What to do |
|---|---|
| Captcha / arkose challenge | Run `--login --headful`, solve it by hand once. The cached session carries forward. |
| Code sent to email or SMS | Same — solve headful. There is no way to automate a code sent out-of-band. |
| "Confirm your email address" | Set `X_EMAIL` to the address on the account and retry. |
| 2FA authenticator prompt | Set `X_TOTP_SECRET` to the base32 secret from the authenticator setup screen. |

Stop after two failed password logins. Repeated failures escalate to an account
lock, which is far more disruptive than the original problem. Switch to cookie
import instead.

### Cookie import

The reliable path when password login keeps tripping challenges:

1. Sign into x.com in a normal browser.
2. DevTools → Application → Cookies → `https://x.com`.
3. Copy the values of `auth_token` and `ct0`.
4. `export X_AUTH_TOKEN=… X_CT0=…`

These are session credentials — treat them exactly like a password. They stay
valid until the browser session is invalidated, so re-copy them after logging out
anywhere.

### "The cached session is no longer valid"

Cookies expired, or X invalidated the session (a password change does this, as
does logging out everywhere). Re-run with `--login`.

## Extraction

### Exit 1: "No Article body found"

In order of likelihood:

1. **It is an ordinary post, not an Article.** Most x.com links are. Articles are
   the long-form format with a title and a Draft.js body; a normal tweet has
   neither. The page title printed in the error usually makes this obvious.
2. **The post is deleted, or the account is suspended or protected.** The page
   loads but carries no content.
3. **The body never loaded.** Articles lazy-load; the script scrolls and waits,
   but a slow connection can outlast the timeout. Raise `--timeout`.

### The body is there but formatting is wrong

Check what the converter received before changing the converter — dump the raw
object first:

```bash
python scripts/fetch_article.py <url> --format json -o raw.json
```

If `content.blocks` looks right but the Markdown does not, the bug is in
`draftjs_to_md.py`. The two things most likely to be at fault:

- **Styles landing at the wrong character.** Almost always a UTF-16 offset
  problem, and almost always in text containing emoji or other astral characters.
  The converter splices in UTF-16 space precisely to avoid this; if someone
  "simplified" it to Python string slicing, that is the regression.
- **Missing images.** `atomic` blocks reference media by `mediaId`, which must
  resolve against `media_entities` in the same article object. If the id is absent
  from that list the converter emits `*[embedded media]*` — that marker means the
  reference was unresolvable, not that the block was empty.

### Empty or partial output on a long article

X paginates very long Article bodies. If the tail is missing, increase the scroll
loop in `fetch()` — it currently scrolls six times waiting for a body to appear,
which is tuned for finding the payload rather than exhausting a long one.

## Playwright

### "Playwright is not installed"

```bash
pip install playwright && playwright install chromium
```

### Browser download blocked, or a Chromium already exists

Point at an existing binary rather than downloading another:

```bash
export X_CHROMIUM_PATH=/path/to/chromium
```

Some managed environments preinstall browsers and set `PLAYWRIGHT_BROWSERS_PATH`;
in those, `playwright install` is unnecessary and may be blocked outright.

### Runs work headful but fail headless

X does fingerprint headless browsers. If a login only succeeds with `--headful`,
do the login headful once and let every subsequent run use the cached session
headless — the session cookie does not care how it was obtained.

## Network

Corporate proxies and sandboxed environments frequently block `x.com` outright.
A failure that reports a proxy status (403/407 on CONNECT) is an egress policy
denial, not an authentication problem — no credential change will fix it, and the
host needs allowing upstream.
