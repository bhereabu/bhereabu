# 7. Personal trainer

Generic fitness advice ignores your schedule, your injuries, your equipment, and
your actual goal. Give Claude the real numbers and it builds a real program, then
adjusts it as you report back.

## Paste at the start of a new chat

```
You are an expert personal trainer and sports nutritionist. I want you to build me a complete training program.

My situation:
Age: [age]
Current weight / body composition: [details]
Goal: [lose fat / build muscle / improve endurance / general fitness]
Available equipment: [gym / home / dumbbells only / etc.]
Days per week I can train: [number]
Time per session: [minutes]
Any injuries or limitations: [details or "none"]
Current fitness level: [beginner / intermediate / advanced]

Build me a 12-week program. Give me the full plan for each week with exercises, sets, reps, and rest periods. Explain why you're structuring it this way - I want to understand the logic, not just follow instructions. After I start, I'll report back weekly and you adjust based on how it's going.
```

## Getting the most out of it

Fill in every field, including "none" for injuries. A blank field gets a guess,
and the guess is always the generic answer you were trying to avoid.

The last two sentences are what separate this from a downloadable PDF. "Explain
why you're structuring it this way" means you learn the logic and can adapt when
life interferes. "I'll report back weekly" sets up the loop.

## The weekly check-in

Use the same shape every week so the adjustments are grounded:

```
Week [N] report.

Completed: [which sessions, which you skipped and why]
Loads: [what went up, what stalled]
How it felt: [energy, soreness, sleep]
Anything that hurt: [details or "nothing"]

Adjust week [N+1] based on this.
```

Do this in a Project (see [#1](01-projects.md)) so the whole history stays in one
place and the program compounds instead of resetting.

## Caveat

This is a planning tool, not medical advice. If you have a condition, an existing
injury, or you're coming back from one, get a doctor or physio to sign off on the
plan before starting it.
