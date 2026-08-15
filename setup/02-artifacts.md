# 2. Artifacts — working apps inside your chat

A common assumption is that Claude only produces text, and that anything it
"builds" is a block of code you have to take somewhere else to run. That's wrong.
An artifact is a live product in a side panel: a calculator, a habit tracker, a
game, a dashboard. You open it, click it, and use it without leaving the
conversation.

SVG graphics, interactive charts, and Mermaid diagrams all render. It's available
on the free plan and most people have never tried it.

## Try this

```
Build me a habit tracker as a working web app.

I want to track 5 daily habits.
Each day I can check them off.
Show a 7-day streak counter for each habit.
If I miss a day, the streak resets.

Design: dark background, clean minimal look.
Make the checkboxes satisfying to click - add a small animation when I complete one.
The data should persist if I refresh the page.
```

A finished build of exactly this spec is in
[`apps/habit-tracker.html`](../apps/habit-tracker.html) — open it in a browser to
see what the prompt produces.

## How to ask for one

The prompt above has four parts, and each one is doing work:

| Part | Line | Without it |
|---|---|---|
| What it is | "a habit tracker as a working web app" | You get a description of one |
| The rules | "5 habits", "streak resets" | You get plausible defaults, not yours |
| The feel | "dark background", "satisfying to click" | Generic default styling |
| The constraint | "persist if I refresh" | State disappears on reload |

The persistence line is the one people forget. Say it explicitly and the artifact
keeps your data across refreshes.

## Iterating

Artifacts update in place. Don't restate the whole spec — name the change:

- "Make the streak counter red when it resets."
- "Add a sixth habit slot and let me rename them."
- "The weekly view is cramped on mobile. Fix the layout under 500px."

## What works well as an artifact

Single-purpose tools with local state: calculators, trackers, converters, quiz
apps, small games, dashboards over data you paste in, diagrams, one-page landing
mockups.

What doesn't: anything needing a server, a database, private API keys, or a login.
Artifacts run in a sandboxed browser page with no backend of their own.
