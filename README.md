# Claude Feature Toolkit

A 17-item guide to Claude's lesser-known features, implemented rather than
described. Every prompt in the source is a file you can copy, every buildable
thing is built and runs, and every setup step is a checklist with the exact
navigation path.

Start at **[`index.html`](index.html)** — open it in a browser for the whole set
with one-click copy on each prompt. Or browse the files directly below.

## The 15-minute path

If you do nothing else, do these four in this order. Each takes minutes and pays
off every day after.

1. **[Projects](prompts/01-projects.md)** — stop re-explaining yourself every chat.
2. **[Memory](prompts/04-memory.md)** — off by default; turn it on and seed it.
3. **[Adaptive Thinking](prompts/03-adaptive-thinking.md)** — turn it on, re-ask a
   question you've asked before, compare.
4. **[CLAUDE.md](CLAUDE.md)** — if you use Cowork or Claude Code, write one for
   your main project folder.

## Everything

### Foundations

| # | Item | What's here |
|---|---|---|
| 1 | [Projects](prompts/01-projects.md) | Project instructions template plus how to adapt it |
| 2 | [Artifacts](setup/02-artifacts.md) | How to ask for one, and a **[built habit tracker](apps/habit-tracker.html)** |
| 3 | [Adaptive Thinking](prompts/03-adaptive-thinking.md) | Hard-decision prompt, plus the API parameters |
| 4 | [Memory](prompts/04-memory.md) | Seed prompt, and how Memory differs from Projects |

### Role prompts

| # | Item | Use it for |
|---|---|---|
| 5 | [Personal psychologist](prompts/05-psychologist.md) | Decisions you keep circling; a CBT-style questioner |
| 6 | [The hard mentor](prompts/06-hard-mentor.md) | Stress-testing a plan you're still shaping |
| 7 | [Personal trainer](prompts/07-personal-trainer.md) | A 12-week program built on your real numbers |
| 8 | [Difficult conversation](prompts/08-difficult-conversation.md) | Rehearsing against a model of the other person |
| 9 | [Devil's advocate](prompts/09-devils-advocate.md) | Attacking a decision you've already made |

### Where Claude runs

| # | Item | What's here |
|---|---|---|
| 10 | [Claude in Chrome](prompts/10-chrome-tasks.md) | Setup plus four browser-automation tasks |
| 11 | [Claude Cowork](setup/11-cowork.md) | Desktop setup and the three things to configure on day one |
| 12 | [Scheduled Tasks](prompts/12-scheduled-tasks.md) | Four recurring tasks and what makes one work |
| 13 | [Skills](setup/13-skills.md) | Install, and write your own — see the working **[daily-brief skill](.claude/skills/daily-brief/SKILL.md)** |
| 14 | [CLAUDE.md](CLAUDE.md) | This repo's own file, written as a working example |
| 15 | [Claude Code](setup/15-claude-code.md) | CLI, IDE, and GitHub Actions setup |
| 16 | [Claude Design](setup/16-claude-design.md) | Decks and layouts, and how to escape the default look |

### For developers

| # | Item | What's here |
|---|---|---|
| 17 | [Prompt Caching](examples/prompt-caching/README.md) | Runnable **[Python](examples/prompt-caching/cached_request.py)** and **[Node](examples/prompt-caching/cached_request.mjs)** examples that print the cache hit |

## Running the two things that run

**Habit tracker** — open `apps/habit-tracker.html` in any browser. No build step,
no dependencies. Data persists in `localStorage`; the 7-day dots show your last
week and a missed day resets the streak.

**Prompt caching** — needs an API key:

```bash
export ANTHROPIC_API_KEY=...

pip install anthropic && python examples/prompt-caching/cached_request.py
# or
npm i @anthropic-ai/sdk && node examples/prompt-caching/cached_request.mjs
```

Both send the same large system prompt twice and print the `usage` numbers, so
you see the cache write on call 1 and the read on call 2.

## Where this corrects the source

The source guide's developer section was a generation behind. The implementation
uses current values and flags each change in
[`examples/prompt-caching/README.md`](examples/prompt-caching/README.md):

- `claude-opus-4-6` → **`claude-opus-5`**
- "5 minutes" → 5 minutes **or 1 hour** via `{"type": "ephemeral", "ttl": "1h"}`
- "90% cost reduction" → true of reads (~0.1x); **writes cost 1.25x or 2x**, so
  break-even is 2 requests on the 5-minute TTL and 3 on the 1-hour
- Added the **minimum cacheable prefix** (512 tokens on Opus 5), which the guide
  omits and which silently causes nothing to cache

[`PLAN.md`](PLAN.md) has the full mapping from guide item to deliverable.
