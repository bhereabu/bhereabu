# Project: Claude Feature Toolkit

## About this project

A working toolkit built from a 17-item guide to Claude's lesser-known features.
Every item in the guide is turned into something you can use directly: a prompt
file you paste, an app that runs, or a checklist you follow. Readers are technical
and already use Claude — they do not need an explanation of what an LLM is.

## Writing rules

- Short paragraphs. Max 3 sentences.
- Prose over bullets in explanatory sections. Bullets are for checklists and tables.
- No em dashes. Use hyphens or restructure the sentence.
- Numbers beat adjectives. Write "cuts 40 lines to 6" not "greatly simplifies".
- Never use: "delve", "leverage" (as a verb), "utilize", "game-changing", "seamless".
- Contractions are fine.
- Never open a response or a doc section with "Great question" or "Certainly".

## Content rules

- Every prompt file must be copy-pasteable as-is, with `[bracketed placeholders]`
  for the parts the reader fills in. No commentary inside the prompt block.
- Every claim about API behavior (pricing, TTLs, model IDs, limits) must be
  current. If a value came from the source PDF, verify it before repeating it,
  and note the correction where it differs.
- Lead each file with what the thing is for, then the artifact, then the caveats.

## File structure

- Prompts you paste into a chat go in `prompts/`, numbered to match the guide.
- Setup checklists for products (Chrome, Cowork, Code, Design) go in `setup/`.
- Runnable apps go in `apps/`, single self-contained HTML files, no build step.
- API code samples go in `examples/<feature>/`.
- Installable skills go in `.claude/skills/<skill-name>/SKILL.md`.

## Code rules

- HTML apps are one file: no bundler, no npm install, no external fonts.
  A CDN `<script>` tag is acceptable; a build step is not.
- State that must survive a refresh goes in `localStorage` under a namespaced key.
- API samples default to `claude-opus-5` and always show how to verify the
  behavior they demonstrate (e.g. print `usage` fields, not just the response).
- No API keys in files. Read from the environment.
