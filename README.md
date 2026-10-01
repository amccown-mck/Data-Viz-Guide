# Data-Viz-Guide

This is the McKesson data-visualization starter kit. It covers principles, design tokens, a chart cookbook, and ready-to-use themes for building **explanatory, consulting-grade** charts. It is written for analysts, engineers, consultants, and coding agents.

> Status: v0.1, a work in progress. See [ROADMAP.md](ROADMAP.md) for what is done and what comes next.

| You are... | Go to |
|---|---|
| Making any chart | [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → [docs/qa-checklist.md](docs/qa-checklist.md) |
| Coding in Python | `pip install -e ./python`, then `import mckviz as mv; mv.use()`. Examples are in [examples/python/](examples/python/) |
| Building HTML / JS | Start from [templates/html/chart-card.html](templates/html/chart-card.html); themes in [dist/web/](dist/web/): CSS variables, Plotly template, Vega-Lite config |
| Using Excel / PowerPoint | [docs/office-setup.md](docs/office-setup.md): install the fonts and theme, then start from the template, starter deck and chart workbook in [dist/office/](dist/office/) |
| Using Power BI | [dist/powerbi/mckesson-dataviz-theme.json](dist/powerbi/mckesson-dataviz-theme.json) |
| Using R | [dist/r/theme_mck.R](dist/r/theme_mck.R) |
| A coding agent | [AGENTS.md](AGENTS.md) (also loaded via `CLAUDE.md` and `.github/copilot-instructions.md`); chart workflow skill in [.github/skills/mck-chart](.github/skills/mck-chart/SKILL.md) |
| Adding chart rules to another repo | Copy [dist/agents/mck-viz-rules.md](dist/agents/mck-viz-rules.md), a single self-contained rules file |

To change the brand, edit `tokens/tokens.json`, run `python tokens/build.py`, and then check `dist/palette-report.md`. Do not hand-edit `dist/`.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed.