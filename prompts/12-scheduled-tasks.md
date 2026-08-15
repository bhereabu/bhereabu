# 12. Scheduled Tasks — Claude that works while you sleep

Most people treat Claude as something they activate: open a chat, type, wait,
close the tab. Scheduled tasks invert that. You define the work once and it runs
on a schedule with no trigger from you, saving the output where you asked for it.

## Setup

In Claude Cowork or the Claude desktop app, open the scheduling control (look for
**Schedule** / **Tasks** / the clock icon), give the task a name, pick the
frequency and time, and paste the task description. The task runs in its own
session, so the description has to stand alone — it can't refer to an earlier
conversation.

## Morning brief — the one from the guide

```
Every weekday morning at 7:30am, do the following:

1. Search for the top AI and crypto news from the last 24 hours
2. Pick the 5 most important stories - focus on things that are surprising, counterintuitive, or have real implications for builders and investors
3. For each story write: headline, 2-sentence summary, why it matters
4. Save the result as "brief-[date].md" in my /briefs folder

Keep the tone direct and analytical. No fluff. Readable in 3 minutes.
```

This pairs with the installable version of the same job in
[`.claude/skills/daily-brief/SKILL.md`](../.claude/skills/daily-brief/SKILL.md) —
install the skill and the scheduled task shrinks to one line.

## Three more that earn their slot

**Weekly project digest** (Fridays, 5pm)

```
Every Friday at 5pm:

1. Read every file changed in [folder] this week
2. Write a one-page summary: what moved, what stalled, what's blocking
3. List anything I said I'd do that still isn't done
4. Save as "digest-[date].md" in /digests

Be blunt about what stalled. Don't pad the list to make the week look productive.
```

**Inbox triage** (weekdays, 8am)

```
Every weekday at 8am, go through [source] and sort what arrived since yesterday into:
- Needs a reply from me today (with a one-line draft for each)
- Needs a decision but not today
- FYI only

Save as "triage-[date].md". Do not send anything.
```

**Monthly stale-content sweep** (1st of the month)

```
On the 1st of each month, scan [folder] for documents that reference dates, prices, versions, or model names that are more than 3 months old.
List each one with the specific line that's stale and what it should probably say now.
Save as "stale-[date].md".
```

## What makes a scheduled task work

Write it as a complete standalone instruction. There's no conversation to refer
back to and no chance to answer a clarifying question, so every choice has to be
made in the description.

Four things every task needs:

1. **A specific window** — "in the last 24 hours", "changed this week". Without
   one, the task re-does old work.
2. **A count** — "the 5 most important". Unbounded tasks produce unbounded output
   that you stop reading by week two.
3. **A destination** — an exact filename pattern and folder.
4. **A length or time budget** — "readable in 3 minutes" beats "concise".

Add a "do not" line for anything that sends, posts, or deletes. Unattended tasks
should produce drafts, not actions.

## Maintenance

Review the output after the first week and again after a month. A task you've
stopped reading is worse than no task, because it looks like coverage. Delete it
or fix the count and the window.
