# Caveman Mode

This repo has [caveman](https://github.com/JuliusBrussee/caveman) installed for token-efficient communication.

## Usage
- `/caveman` — activate caveman mode (default: full)
- `/caveman lite` — professional terseness
- `/caveman ultra` — maximum compression
- `/caveman-commit` — concise git commit messages
- `/caveman-review` — one-line PR review comments
- `stop caveman` or `normal mode` — deactivate

## What's installed
- `.claude/hooks/` — SessionStart and UserPromptSubmit hooks for auto-activation and mode tracking
- `.claude/skills/` — Skill definitions (caveman, caveman-commit, caveman-review, caveman-compress)
- `.claude/settings.local.json` — Repo-level hook configuration
- `caveman/` — Full caveman repo clone (reference/source)
