# 16. Claude Design — AI for visual work

Most people don't know this product exists. Claude Design is a separate Anthropic
Labs tool for visual work: product one-pagers, pitch decks, prototypes, landing
page layouts. You describe what you need and it builds it, exporting to PPTX,
Canva, PDF, or HTML.

For people who aren't designers, it replaces a three-hour Figma session with a
ten-minute conversation.

## Access

It's an Anthropic Labs project — find it through the Labs section of your Claude
account or at the Labs site. The source guide promised a direct link and then
didn't include one, so navigate from Labs rather than guessing a URL.

## What to ask for

Give it the audience and the decision you want the reader to make, not just the
topic. "A pitch deck about our product" produces a generic deck; the version below
produces something you can send.

```
Build me a [deck / one-pager / landing page] for [audience].
The single thing they should take away: [one sentence].
What they already know: [context you can skip].
What I need them to do next: [the ask].

Content to work from:
[paste your notes, bullets, or existing copy]

Style: [reference, brand colors, or "clean and minimal"]
Export to [PPTX / PDF / HTML].
```

## Getting a look that isn't the default

Open-ended design briefs settle into a house style. Two things break out of it:

- **Specify concretely.** Exact hex values, a named typeface, and layout
  constraints get followed precisely.
- **Ask for options first.** "Before building, propose 4 distinct visual
  directions for this brief — background hex, accent hex, typeface, and one line
  of rationale each. I'll pick one, then build only that."

The second is the better move when you don't already know what you want.

## Where it fits next to Artifacts

They overlap and the split is about the output.

| | Artifacts ([#2](02-artifacts.md)) | Claude Design |
|---|---|---|
| Produces | Working interactive apps | Visual documents and layouts |
| Lives | In the chat side panel | In a dedicated design tool |
| Exports | HTML you copy out | PPTX, Canva, PDF, HTML |

Building a calculator that runs: Artifacts. Building the deck that explains why
you built it: Claude Design.
