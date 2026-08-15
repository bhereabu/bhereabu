# 13. Skills — install new capabilities like plugins

Skills are pre-built instruction sets that give Claude a specific capability.
Instead of explaining what you need every time, you install a skill once and
Claude already knows how to handle that kind of task — building PowerPoint files,
working with PDFs, or running a workflow that's specific to how you work.

The phone analogy holds. The base phone works. With the right apps installed it
does a lot more.

## Finding and installing

- **See what's installed** — Cowork → **Customize** → **Skills**
- **Add more** — **Browse plugins** in the left sidebar → pick a plugin → install.
  The skills from that plugin appear in your Skills tab automatically, and Claude
  uses them when a task calls for it.

You don't invoke a skill by name. Claude reads the descriptions and loads the
matching one when the task fits, which is why the description field matters more
than the body.

## Writing your own

A skill is a folder with a `SKILL.md` inside it. This repo ships a working one:

```
.claude/skills/daily-brief/SKILL.md
```

Read it as the template — [`daily-brief`](../.claude/skills/daily-brief/SKILL.md)
turns the scheduled morning brief from [#12](../prompts/12-scheduled-tasks.md)
into something you invoke in one line.

The structure is:

```markdown
---
name: skill-name
description: What this does and exactly when Claude should reach for it.
---

# Skill Name

The instructions Claude follows when this skill loads.
```

## What makes a skill fire at the right time

The `description` is the only part Claude sees before deciding whether to load the
skill, so it has to state the trigger, not just the topic.

| Weak | Strong |
|---|---|
| "Helps with documents" | "Use when the user asks for a .docx, a report, or a formatted document deliverable" |
| "Brand stuff" | "Apply when generating any customer-facing copy, deck, or landing page" |

Name the artifacts and phrasings you actually use. That's what the match runs
against.

## What belongs in a skill

Put in what only you know: your workflow, your house style, your naming
conventions, the exact commands for a fragile step. Leave out general knowledge —
Claude doesn't need to be told what a spreadsheet is, and every paragraph costs
context on every trigger.

Keep each skill to one job. Two loosely related jobs in one file means the whole
thing loads when only half is relevant.

## Skills vs. CLAUDE.md

Both feed Claude instructions without you repeating yourself, at different scopes.

| | CLAUDE.md | Skill |
|---|---|---|
| Loads | Every session in that folder | Only when the task matches |
| Holds | Project rules, conventions, structure | A repeatable procedure |
| Costs | Context on every session | Context only when triggered |

Rule of thumb: if it's true of all work in this project, it's CLAUDE.md. If it's a
procedure you run sometimes, it's a skill.
