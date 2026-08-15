# 4. Memory — Claude that knows who you are

With Memory on, Claude builds a profile of you over time: your job, your current
projects, how you like to communicate. Start a fresh chat and the context is
already there. You never introduce yourself again.

It's off by default, and most people don't know it exists.

## Turning it on

claude.ai → **Settings** → **Capabilities** (or **Features**) → enable **Memory**.
You can review and edit what it has stored from the same screen, which is worth
doing once a month.

## Seed it in one message

```
I want you to remember the following about me so you don't need to ask again:

My name is [name]. I work as [role] at [company or project].
My main focus right now is [what you're working on].
My audience or customers are [who they are].

When I ask for help, always assume this context unless I say otherwise.
My preferred communication style: [direct / detailed / casual / formal].
Things I find annoying in responses: [e.g. bullet points, long intros, excessive caveats].

Save all of this to memory now.
```

## Memory vs. Projects

They solve overlapping problems and you want both.

| | Memory | Projects |
|---|---|---|
| Scope | Everywhere, all chats | One project's chats |
| Holds | Who you are, how you work | Task instructions, reference documents |
| Changes | Accumulates as you talk | You edit it deliberately |

Put durable facts about *you* in Memory. Put the *job* in Project instructions.
When the two conflict, the project instructions are the more specific context and
should win, so write them that way ("in this project, ignore my usual preference for...").

## Keeping it clean

Memory drifts. Two habits keep it useful:

- When something changes ("I left [company], I'm now at [company]"), say so
  explicitly and ask Claude to update memory rather than add to it.
- Skim the stored memories occasionally and delete anything from a finished
  project. Stale context is worse than no context.
