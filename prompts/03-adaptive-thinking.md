# 3. Adaptive Thinking — reasoning you can watch

Extended thinking is a mode where Claude reasons through a problem before
answering, and you can read the whole process. For a lookup question it's
overkill. For a real decision, a strategy question, or anything where you want
Claude to actually think instead of pattern-match, the output is different in kind.

Most people have never turned it on.

## Turning it on

- **claude.ai** — the model/settings control under the message box. Turn on
  extended (adaptive) thinking, then re-ask a question you've asked before and
  compare the two answers.
- **API** — `thinking: {"type": "adaptive"}` plus `output_config: {"effort": "high"}`.
  On Claude Opus 5 thinking is on by default; you opt *out* with
  `{"type": "disabled"}`. To read the reasoning, add `"display": "summarized"` —
  the default omits it and the field comes back empty.

## Use this when facing a real decision

```
I'm deciding between two options and I want you to think through this carefully before answering.

Option A: [describe option A]
Option B: [describe option B]

My situation: [your context, constraints, what matters most]

Work through this before responding. Think about:
- The second and third-order consequences of each option
- What I'm probably overweighting or underweighting emotionally
- What information I might be missing that would change the decision
- Which option has better downside protection if things go wrong

Then give me your actual recommendation with your reasoning.
```

## Why this prompt works

The four bullets are the parts people skip when they reason alone. Second-order
consequences, emotional weighting, missing information, and downside protection
are exactly where solo decisions go wrong, and naming them stops the answer from
collapsing into a pros-and-cons table.

The last line matters as much as the rest. Without "give me your actual
recommendation", you get an even-handed survey and still have to decide alone.
