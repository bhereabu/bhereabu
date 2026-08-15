# 1. Projects — Claude that remembers you

A new chat starts from zero every time. It doesn't know your name, your work, or
how you like to be answered. Projects fix that: you create one, upload reference
documents, write standing instructions, and Claude holds all of it permanently.

Set this up before anything else on this list. Everything else gets better once
Claude already knows who you are.

## Setup

1. claude.ai sidebar → **Projects** → **New project**
2. Name it after the work, not the tool ("AI newsletter", not "Claude project")
3. Paste the instructions below into **Project instructions** (via **Edit**)
4. Add reference files to **Project knowledge**: style guides, past work, specs,
   glossaries, anything you'd otherwise re-paste

## Project instructions — paste into the Project Instructions field

```
You are my content research assistant. I run a newsletter about AI and crypto for a technical audience.

Always assume my readers know the basics. Don't explain what an LLM is or what a blockchain is.

When I share a topic or article, your job is to:
1. Identify the 3 most counterintuitive or surprising angles
2. Find connections to recent events I might have missed
3. Suggest how I could frame this as a story, not a summary

Tone: direct, no corporate language, no filler phrases.
Format: short paragraphs, no bullet points unless I ask.
Never start a response with "Great question" or "Certainly".
```

## Adapting it

The template above is a content-research project. The shape transfers to any
domain — swap the four blocks and keep the structure:

| Block | What it does | Replace with |
|---|---|---|
| Role line | Sets the job | "You are my [role] for [context]" |
| Assumption line | Kills over-explaining | What your audience already knows |
| Numbered job | The repeatable task | The 2-4 things you always want done |
| Tone / format / never | Kills the defaults you dislike | Your actual preferences |

The "never" line does more work than people expect. Listing the specific openers
and habits you don't want removes them permanently instead of once per chat.
