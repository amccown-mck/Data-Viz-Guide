# Data-Viz-Guide

This is the McKesson data-visualization starter kit. It covers principles, design tokens, a chart cookbook, and ready-to-use themes for building **explanatory, consulting-grade** charts. It is written for analysts, engineers, consultants, and coding agents.

> Status: v0.1, a work in progress. See [ROADMAP.md](ROADMAP.md) for what is done and what comes next.

| You are... | Go to |
|---|---|
| Making any chart | [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → [docs/qa-checklist.md](docs/qa-checklist.md) |
| Coding in Python | `pip install -e ./python`, then `import mckviz as mv; mv.use()`. Examples are in [examples/python/](examples/python/) |
| Building HTML / JS | [dist/web/](dist/web/): CSS variables, Plotly template, Vega-Lite config |
| Using Excel / PowerPoint | [dist/office/](dist/office/): theme colors and fonts XML. Install the fonts from [fonts/](fonts/) |
| Using Power BI | [dist/powerbi/mckesson-dataviz-theme.json](dist/powerbi/mckesson-dataviz-theme.json) |
| Using R | [dist/r/theme_mck.R](dist/r/theme_mck.R) |
| A coding agent | [AGENTS.md](AGENTS.md) |

To change the brand, edit `tokens/tokens.json`, run `python tokens/build.py`, and then check `dist/palette-report.md`. Do not hand-edit `dist/`.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed.