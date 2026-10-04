# Copilot instructions

The full instructions for this repo are in [`AGENTS.md`](../AGENTS.md). Read it before you make a chart or change the kit. Path-specific rules are in [`.github/instructions/`](instructions/), and the chart workflow skill is in [`.github/skills/mck-chart/`](skills/mck-chart/SKILL.md).

The short version, for when you can't open AGENTS.md:

- **Before charting:** read `docs/principles.md`, pick the chart with `docs/choosing-a-chart.md`, and follow `docs/cookbook/<chart>.md`.
- **Colors come from tokens, never hex literals.** Python: `import mckviz as mv; mv.use()`, then `mv.colors.focus`, `mv.highlight(...)`, `mv.SEQUENTIAL`, `mv.DIVERGING`. Web: `dist/web/mck-viz.css` variables, plus `dist/web/mck-plotly-template.js` or `dist/web/vega-lite-config.json`. R: `dist/r/theme_mck.R`.
- **Every chart has** an insight headline (a full sentence), a neutral subtitle (metric, unit, scope, period), direct labels instead of a legend, grey context with one blue focus (and an optional navy accent; orange only when it means "worse"), ≤ 6 categorical colors, and a "Source:" line.
- **Categorical order** (only when categories must be told apart): blue, navy, bright blue, teal, mint, orange last; prefer 4 or fewer. **Type:** slide title Bold 26 pt McKesson Blue `#005A8C`; a chart's own headline SemiBold 18 pt navy `#143359`; flat shapes, no rounded corners or shadows.
- **Honest scales:** bars start at zero, bubble area ∝ value, no dual axes.
- **People data:** never show a group of fewer than 10 people, including in tooltips and drill-downs.
- **Tokens:** edit only `tokens/tokens.json`, then run `python tokens/build.py`. Never hand-edit `dist/`.
- **QA:** run `docs/qa-checklist.md` before you return a chart. Run `python tools/check_snippets.py` after editing cookbook code.
