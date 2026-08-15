# 10. Claude in Chrome — Claude that sees what you see

Most people run Claude in a separate tab and copy-paste between them. Claude for
Chrome removes that step: it reads your active tab, clicks links, fills forms, and
navigates to new URLs. You describe the task in plain English and step away.

## Setup

1. Chrome Web Store → search **Claude for Chrome** → **Add to Chrome**
2. Sign in with your Claude account
3. Click the extension icon to open the side panel
4. Open the page you want to work on, then give it the task

It acts on whatever tab is in front of it, so check what's open before you start.

## Example task — extract and compare

```
I'm on this job listings page.
Go through every listing visible and extract: job title, company name, salary range if shown, and the top 3 requirements.
Build me a comparison table sorted by salary, highest first.
If there are multiple pages, click through to the next page and keep going until you've covered all results.
```

## More tasks worth stealing

**Compare across tabs**

```
I have [N] product pages open in other tabs. For each one, pull the price, the shipping cost, the return window, and the warranty.
Put them in one table and flag anything where the real total differs from the headline price.
```

**Fill a long form from a document**

```
This is a [type] form. Fill it in using the details from [document/page].
Leave anything you're unsure about blank and list those fields for me at the end. Do not submit it - stop before the submit button so I can review.
```

**Audit a page**

```
Go through this page and list every external link, whether it opens in a new tab, and whether it's broken. Check each one by visiting it.
```

## Working with it

Anchor the task to what's on screen ("this page", "the table under Pricing")
rather than describing the site from memory. Say when to stop — "don't submit",
"stop after page 5", "list them, don't message anyone" — because an underspecified
stopping point is where these tasks go wrong.

Sites that require a login work only where you're already signed in, and pages
that load content on scroll may need an explicit "scroll to the bottom first".

## Before you hand over a tab

The extension can act on anything the page can do. Two rules worth keeping:

- Don't run it on a tab holding banking, payment, or admin access you wouldn't
  want an automated click to reach.
- For anything that sends, posts, buys, or deletes, tell it to stop and show you
  first. Review, then do the final click yourself.
