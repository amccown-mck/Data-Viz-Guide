# Data-Viz-Guide

This is the McKesson data-visualization starter kit. It covers principles, design tokens, a chart cookbook, and ready-to-use themes for building **explanatory, consulting-grade** charts. It is written for analysts, engineers, consultants, and coding agents.

> Version 1.1.0 (see [CHANGELOG.md](CHANGELOG.md); the version lives in [VERSION](VERSION)). The guide and toolkit are complete; see [ROADMAP.md](ROADMAP.md) for open questions and what's next.

**Start here: the guide.** Open [dist/guide/index.html](dist/guide/index.html) in a browser, or read the same pages as a 16:9 PDF: [McKesson-DataViz-Guide.pdf](dist/guide/McKesson-DataViz-Guide.pdf). To send the clickable guide to someone without the repo, send the standalone [McKesson-DataViz-Guide.html](dist/guide/McKesson-DataViz-Guide.html): one file that works offline. The chart chooser and cheat sheet are in the guide's top bar. Fundamentals; then every chart family (magnitude, part-to-whole, change over time, ranking, distribution, correlation, relationships and flows, geo-spatial, single number) as anatomy, variants, best practice and how to build it in each tool; then formats and the toolkit.

| You are... | Go to |
|---|---|
| Learning the house style | [The guide](dist/guide/index.html) ([PDF](dist/guide/McKesson-DataViz-Guide.pdf)) |
| Making any chart | [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → [docs/qa-checklist.md](docs/qa-checklist.md) |
| Wanting it on one page | [Chart chooser](dist/guide/chooser.html) and [cheat sheet](dist/guide/cheat-sheet.html) in the guide, or as PDFs to print or pin: [chooser](dist/print/chart-chooser.pdf), [cheat sheet](dist/print/cheat-sheet.pdf) |
| Coding in Python | In any project: `pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"` (fonts and map data included), then `import mckviz as mv; mv.use()`. Working on this repo: `pip install -e "./python[examples]"` (the `examples` extra adds Plotly and pandas). Examples are in [examples/python/](examples/python/); running `mv.lint` in CI: [docs/ci.md](docs/ci.md) |
| Building HTML / JS | Start from [templates/html/chart-card.html](templates/html/chart-card.html); themes in [dist/web/](dist/web/): CSS variables, Plotly template, Vega-Lite config |
| Using Excel / PowerPoint | [docs/office-setup.md](docs/office-setup.md): install the fonts and theme, then start from the template, starter deck and chart workbook in [dist/office/](dist/office/) |
| Using Power BI | [docs/powerbi-setup.md](docs/powerbi-setup.md), then import [dist/powerbi/mckesson-dataviz-theme.json](dist/powerbi/mckesson-dataviz-theme.json) |
| Using R | `source("dist/r/theme_mck.R")` ([theme](dist/r/theme_mck.R)); examples in [examples/r/](examples/r/gallery_ggplot2.R) |
| A coding agent, or setting one up | [For agents](#for-agents) below |

## Getting the kit

- **Technical users:** clone this repo, or install just the Python package from a tagged release (above). Releases are tagged `v<version>`; [CHANGELOG.md](CHANGELOG.md) says what changed.
- **Everyone else:** download the release zip from SharePoint, `McKesson-DataViz-Kit-v<version>.zip`, unzip it and open `START-HERE.html`. It holds the standalone and PDF guide, the one-pagers, the Office template, starter deck and workbook, the Power BI theme, the fonts, the web themes, the `mckviz` wheel and the agent files. To make the zip: run the builds, then `python tools/make_bundle.py` (writes `dist/release/`, which is not committed).

## For agents

Three ways to give an AI assistant the McKesson chart rules, from fullest to lightest:

| Option | What it is | Use it when |
|---|---|---|
| **This repo's [AGENTS.md](AGENTS.md)** | Full instructions, read automatically by Claude Code (via `CLAUDE.md`), GitHub Copilot (via `.github/copilot-instructions.md`), Cursor, Codex and others, plus the in-repo [`mck-chart` skill](.github/skills/mck-chart/SKILL.md) | You work **in this repo**, on charts or on the kit itself |
| **The portable skill** [dist/skills/mck-chart/](dist/skills/mck-chart/SKILL.md) | A self-contained skill folder: the workflow, the one-page rules, the chart chooser, principles, QA checklist, every cookbook page, theme files and an environment check. The agent loads the detail only when it makes a chart | You make charts **in another repo or tool**: copy the folder to `~/.claude/skills/` (all your projects), a repo's `.claude/skills/` or `.github/skills/`, or upload `agents/mck-chart-skill.zip` from the release bundle to Claude.ai as a custom skill |
| **The single rules file** [dist/agents/mck-viz-rules.md](dist/agents/mck-viz-rules.md) | One self-contained page: workflow, color roles with hex values, type, honest scales, people-data rules, QA checklist | The tool takes one instructions file (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/`), or you paste it into a chat |

In Python, pair any of them with the `mckviz` package (`pip install` from the tag), so agents check their own charts with `mv.lint(fig)`.

To change the brand, edit `tokens/tokens.json`, run `python tokens/build.py`, and then check `dist/palette-report.md`. Do not hand-edit `dist/`.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed.