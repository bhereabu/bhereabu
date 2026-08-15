---
name: daily-brief
description: Produce a short, scannable news brief on a topic and save it as a dated Markdown file. Use when the user asks for a brief, a daily/morning brief, a news roundup, "what happened in X", or asks to catch up on recent developments in a field. Also fires for scheduled brief tasks.
---

# Daily Brief

Turns "what happened in X" into a consistent, dated file that reads in three
minutes. Written to be the reusable half of the scheduled morning brief in
`prompts/12-scheduled-tasks.md` - install this and the scheduled task shrinks to
one line.

## Inputs

Take these from the request. Where the user didn't say, use the default and note
the assumption at the top of the file.

| Input | Default |
|---|---|
| Topic | The subject of the request |
| Window | Last 24 hours (last 7 days for a weekly brief) |
| Count | 5 stories |
| Output folder | `/briefs` |
| Audience | Technical readers already in the field |

## Procedure

1. Search for coverage in the topic within the window. Use several distinct
   queries rather than one - a single query returns one slice of the story.
2. Discard anything published outside the window, and anything that's a
   re-report of a story already on the list. Prefer the primary source over the
   coverage of it.
3. Rank what's left by how much it should change a reader's behavior or beliefs.
   Surprising and counterintuitive beats big-and-expected. A funding round is
   only news if the number or the investor is the story.
4. Take the top N. If fewer than N clear the bar, ship fewer and say so - a
   padded list trains the reader to skim.
5. Write the file and save it as `brief-YYYY-MM-DD.md` in the output folder.

## Output format

```markdown
# [Topic] brief - [Weekday, D Month YYYY]

*[N] stories from the last [window]. [X] minute read.*

## 1. [Headline, stated as what happened, not as a teaser]

[Two sentences. What happened and the specific detail that makes it matter -
the number, the name, the change in position.]

**Why it matters:** [One sentence on the implication for the reader. Not a
restatement of the summary.]

[Source](url)

...

---

*Nothing else cleared the bar this [window].*   <- only when you shipped fewer than N
```

## Writing rules

- Direct and analytical. No throat-clearing, no "in a significant development".
- Numbers, not adjectives. "Cut inference cost 60%" beats "dramatically cheaper".
- Assume the reader knows the field. Don't define the basics.
- Every story gets a source link. No link means it doesn't run.
- "Why it matters" must say something the summary didn't. If it's a paraphrase,
  the story is probably filler - cut it.
- Never open with "Great question" or "Certainly".

## Scheduling it

Once installed, the recurring task is one line:

```
Every weekday at 7:30am, run the daily-brief skill for AI and crypto.
```
