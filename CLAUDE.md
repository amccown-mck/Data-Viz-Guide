# Claude Code instructions

All agent instructions for this repo live in AGENTS.md, which is imported below. Keep rules there, not here, so every agent reads the same thing.

@AGENTS.md

For a new chart, use the `/mck-chart` skill (`.claude/skills/mck-chart/`). It defers to the shared workflow in `.github/skills/mck-chart/SKILL.md`: question → chart type → build → headline → QA.
