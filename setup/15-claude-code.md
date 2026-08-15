# 15. Claude Code — AI that writes, tests, and fixes code

Some people still don't know you can write production code with Claude. Not just
snippets — full features and complex refactors, described in plain English.

Claude Code goes further. It works inside your development environment rather than
a chat window: it reads your actual codebase, writes code, runs tests, reads the
error output, and fixes the bugs in a loop until the task is done.

## Setup

**Terminal**

```bash
npm install -g @anthropic-ai/claude-code
cd your-project
claude
```

**IDE** — install the Claude Code extension for VS Code or the plugin for
JetBrains. Both drive the same agent from inside the editor.

**Web and desktop** — claude.ai/code runs the same thing against a repo without a
local install.

## The loop that matters

The difference from autocomplete is that Claude Code closes the feedback loop
itself. Give it a failing test and it reads the failure, edits the code, re-runs
the test, and repeats until green. That means the useful instruction is usually a
verifiable end state, not a set of steps:

```
The integration tests in tests/api/ fail on Node 22 but pass on Node 20.
Find out why and fix it. Run the suite until it's green on both.
```

## GitHub Actions

Claude Code drops into CI and reviews or writes pull requests without you touching
anything. Add the action to `.github/workflows/`, give it an `ANTHROPIC_API_KEY`
secret, and it can:

- Review every PR against your conventions
- Take an issue labelled a certain way and open a PR for it
- Fix failing CI on its own branch

## Set up CLAUDE.md first

Claude Code reads `CLAUDE.md` at the start of every session, so your conventions,
commands, and terminology apply automatically instead of being re-explained. See
[#14](../CLAUDE.md) — this repo's own file is a working example.

The fastest way to create one: run `/init` in a project and let it draft the file
from what's already there, then edit it down.

## Two habits worth adopting early

- **Work on a branch.** Claude Code makes real edits. A branch makes every change
  reviewable and reversible.
- **Give it a way to check itself.** A test command, a linter, a build step. A
  task with a verifiable finish line comes back done; a task without one comes
  back plausible.
