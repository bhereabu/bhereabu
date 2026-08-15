# Implementation Plan — "Claudex" Feature Guide

## What the source document is

A 17-item guide to Claude capabilities most people never turn on. Each item pairs
a short explanation with either a ready-to-paste prompt or a setup instruction:

| # | Item | Kind |
|---|------|------|
| 1 | Projects — persistent context | Paste-able project instructions |
| 2 | Artifacts — working apps in chat | Buildable app (habit tracker) |
| 3 | Adaptive / Extended Thinking | Paste-able decision prompt |
| 4 | Memory | Paste-able memory-seed prompt |
| 5 | Personal psychologist (CBT) | Role prompt |
| 6 | The hard mentor | Role prompt |
| 7 | Personal trainer | Role prompt |
| 8 | Practice a difficult conversation | Role prompt |
| 9 | Devil's advocate | Role prompt |
| 10 | Claude in Chrome | Setup + task prompt |
| 11 | Claude Cowork | Setup |
| 12 | Scheduled Tasks | Task definition |
| 13 | Skills in Cowork | Setup + installable skill |
| 14 | CLAUDE.md | File to author |
| 15 | Claude Code | Setup |
| 16 | Claude Design | Setup |
| 17 | Prompt Caching (dev) | Runnable API code |

## Interpretation of "implement"

The document is instructional, not a software spec. Implementing it means producing
the artifacts it tells the reader to create, so nothing is left as prose:

- Every **prompt** becomes a versioned file you can copy, edit, and reuse.
- Every **buildable thing** gets built and actually works (habit tracker, caching example).
- Every **setup step** becomes a checklist with the exact clicks/commands.
- The whole set gets a **browsable index page** with one-click copy per prompt.

## Deliverables

```
README.md                              hub + 15-minute setup path
PLAN.md                                this file
CLAUDE.md                              item 14, written for THIS repo (not a sample)
index.html                             browsable prompt library, copy-to-clipboard
apps/
  habit-tracker.html                   item 2 — built to the doc's spec, working
prompts/
  01-projects.md                       project instructions template
  03-adaptive-thinking.md              hard-decision prompt
  04-memory.md                         memory-seed prompt
  05-psychologist.md                   CBT role
  06-hard-mentor.md                    brutal-mentor role
  07-personal-trainer.md               trainer role
  08-difficult-conversation.md         roleplay + debrief
  09-devils-advocate.md                case-against role
  10-chrome-tasks.md                   browser-automation tasks
  12-scheduled-tasks.md                recurring task definitions
setup/
  02-artifacts.md                      what artifacts can do, how to ask for one
  11-cowork.md                         desktop app setup
  13-skills.md                         install/browse skills
  15-claude-code.md                    CLI / IDE / GitHub Actions setup
  16-claude-design.md                  Anthropic Labs design tool
.claude/skills/daily-brief/SKILL.md    item 13 — a real, installable skill
examples/prompt-caching/               item 17 — runnable
  README.md                            economics, TTLs, verification
  cached_request.py                    Python, anthropic SDK
  cached_request.mjs                   Node, @anthropic-ai/sdk
```

## Corrections applied to the source

The document's dev section (item 17) is out of date. The implementation uses current
values and the code notes each change:

| Document says | Implemented as |
|---|---|
| `"model": "claude-opus-4-6"` | `claude-opus-5` (current Opus; 4.6 still works but is a generation behind) |
| "Cache persists for 5 minutes" | 5 min default, **or `"ttl": "1h"`** — the 1-hour TTL exists |
| "Up to 90% cost reduction" | Accurate for *reads* (~0.1x). Writes cost **1.25x** (5m) / **2x** (1h), so break-even is 2 requests on 5m, 3 on 1h |
| (unstated) | Minimum cacheable prefix — **512 tokens** on Opus 5, 1024 on Opus 4.8/Sonnet 5. Below that it silently doesn't cache |
| (unstated) | Verify with `usage.cache_read_input_tokens`; a zero there means a silent invalidator (timestamp/UUID in the prefix) |

## Build order

1. `CLAUDE.md` — governs everything written after it.
2. `prompts/` + `setup/` — the bulk of the guide, mechanical.
3. `apps/habit-tracker.html` — built and opened to confirm it runs.
4. `examples/prompt-caching/` — syntax-checked; not executed (needs an API key).
5. `.claude/skills/daily-brief/SKILL.md` — the scheduled-task/skill pairing (12 + 13).
6. `index.html` — generated last, links everything.
7. `README.md` — entry point, ordered by payoff.

## Out of scope

Anything requiring an account action outside this repo: creating a Project,
toggling Memory, installing the Chrome extension, installing Cowork, or scheduling a
task on claude.ai. Those are documented as checklists in `setup/` with the exact
navigation path — the repo holds the content you paste in, not the click itself.
