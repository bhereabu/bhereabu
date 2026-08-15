# 11. Claude Cowork — Claude that lives on your desktop

Claude on the web can't see your computer. Every file has to be pasted or
uploaded, and the result has to be copied back out by hand.

Cowork is a desktop app with direct access to your file system. It reads your
actual files, edits documents in place, creates new ones, and organizes folders,
with no copying into a chat box.

## Setup

1. Download Claude for desktop (Mac or Windows) from claude.ai and install it
2. Sign in
3. Point it at a working folder when it asks for access
4. Confirm it can see the folder: *"List the files in this folder and tell me what
   this project is."*

Start it on one folder rather than your whole drive. You can add more later, and
a narrow scope makes the first week easier to reason about.

## What changes

The web app asks you to describe your files. Cowork reads them. That turns a class
of tasks from tedious to trivial:

- "Rename every file in /invoices to `YYYY-MM-vendor.pdf` based on its contents."
- "Read all 40 interview notes in /research and pull out the themes that appear in
  more than five of them."
- "This spreadsheet and this doc disagree on the Q3 numbers. Find every place they
  differ."
- "Reorganize /drafts by status: published, in review, abandoned. Tell me which
  ones you weren't sure about."

## The three things to set up on day one

1. **A CLAUDE.md in the folder.** Cowork reads it at the start of every session.
   See [#14](../CLAUDE.md) — this repo's own file is a working example.
2. **Skills.** Customize → Skills shows what's installed. See [#13](13-skills.md).
3. **A scheduled task.** See [#12](../prompts/12-scheduled-tasks.md).

Those three are what separate Cowork from a chat window with file access.

## Working safely

File edits are real edits. Two habits cover most of the risk:

- Work in a folder under version control, or take a copy of anything irreplaceable
  before a bulk operation.
- For anything sweeping — renames, moves, deletes across many files — ask for the
  plan first: *"Show me the full list of renames before doing any of them."*
