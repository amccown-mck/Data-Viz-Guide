# Data-Viz-Guide

This is the McKesson data-visualization starter kit. It covers principles, design tokens, a chart cookbook, and ready-to-use themes for building **explanatory, consulting-grade** charts. It is written for analysts, engineers, consultants, and coding agents.

> Status: v1.0 review draft. The guide and toolkit are complete; see [ROADMAP.md](ROADMAP.md) for open questions and what's next.

**Start here: the guide.** Open [dist/guide/index.html](dist/guide/index.html) in a browser, or read the same pages as a 16:9 PDF: [McKesson-DataViz-Guide.pdf](dist/guide/McKesson-DataViz-Guide.pdf). To send the clickable guide to someone without the repo, send the standalone [McKesson-DataViz-Guide.html](dist/guide/McKesson-DataViz-Guide.html): one file that works offline. The chart chooser and cheat sheet are in the guide's top bar. Fundamentals; then every chart family (magnitude, part-to-whole, change over time, ranking, distribution, correlation, relationships and flows, geo-spatial, single number) as anatomy, variants, best practice and how to build it in each tool; then formats and the toolkit.

| You are... | Go to |
|---|---|
| Learning the house style | [The guide](dist/guide/index.html) ([PDF](dist/guide/McKesson-DataViz-Guide.pdf)) |
| Making any chart | [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → [docs/qa-checklist.md](docs/qa-checklist.md) |
| Wanting it on one page | [Chart chooser](dist/guide/chooser.html) and [cheat sheet](dist/guide/cheat-sheet.html) in the guide, or as PDFs to print or pin: [chooser](dist/print/chart-chooser.pdf), [cheat sheet](dist/print/cheat-sheet.pdf) |
| Coding in Python | Clone this repo, then `pip install -e "./python[examples]"` (the `examples` extra adds Plotly and pandas), then `import mckviz as mv; mv.use()`. Examples are in [examples/python/](examples/python/) |
| Building HTML / JS | Start from [templates/html/chart-card.html](templates/html/chart-card.html); themes in [dist/web/](dist/web/): CSS variables, Plotly template, Vega-Lite config |
| Using Excel / PowerPoint | [docs/office-setup.md](docs/office-setup.md): install the fonts and theme, then start from the template, starter deck and chart workbook in [dist/office/](dist/office/) |
| Using Power BI | [docs/powerbi-setup.md](docs/powerbi-setup.md), then import [dist/powerbi/mckesson-dataviz-theme.json](dist/powerbi/mckesson-dataviz-theme.json) |
| Using R | `source("dist/r/theme_mck.R")` ([theme](dist/r/theme_mck.R)); examples in [examples/r/](examples/r/gallery_ggplot2.R) |
| A coding agent | [AGENTS.md](AGENTS.md) (also loaded via `CLAUDE.md` and `.github/copilot-instructions.md`); chart workflow skill in [.github/skills/mck-chart](.github/skills/mck-chart/SKILL.md) |
| Adding chart rules to another repo | Copy [dist/agents/mck-viz-rules.md](dist/agents/mck-viz-rules.md), a single self-contained rules file |

To change the brand, edit `tokens/tokens.json`, run `python tokens/build.py`, and then check `dist/palette-report.md`. Do not hand-edit `dist/`.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed.