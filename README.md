# Data Viz Starter Kit · McKesson Edition

One visual language for everyone who makes charts: business folks, technical folks and the AI agents working alongside them.

> Version 1.1.0 (see [CHANGELOG.md](CHANGELOG.md); the version lives in [VERSION](VERSION)). How we name and describe the kit: [docs/positioning.md](docs/positioning.md). What's next: [ROADMAP.md](ROADMAP.md). License: MIT ([LICENSE](LICENSE)); fonts and map data carry their own open licenses, listed there. Maintainer: Ashley McCown, Workforce Innovation, via [issues](https://github.com/amccown-mck/Data-Viz-Guide/issues).

**The problem.** It's 2:07 on a Tuesday and a VP wants to know where we're losing people, exec-ready by 3. The data takes twelve minutes to clean. The chart takes the rest: which chart tells this story, which blue is our blue, "Chart Title", `final_v7_REAL_final.pptx`, and the chatbot makes everything purple. Every tool has its own idea of good, so the same numbers look different in Excel, Python, Power BI and a chat window, and most of what gets made says nothing.

**What the kit does.** It makes the right chart the easy chart in every tool we use, and checks the rules before a chart leaves your hands. One set of rules: the question first, an insight headline, grey context with one blue focus, honest scales, direct labels, a source line, no group under 10 people. One brand file that every theme is generated from. A guide that says which chart and why, templates and code that are already on-brand, a lint that checks the result, and a playbook so AI assistants follow the same rules you do. Think of it as a consulting firm's chart practice in a box: the house style, the worked exhibits, the review step, and associates who follow the rules.

**Start here: the guide.** Open [dist/guide/index.html](dist/guide/index.html) in a browser, or read the same pages as a 16:9 PDF: [McKesson-DataViz-Guide.pdf](dist/guide/McKesson-DataViz-Guide.pdf). To send the clickable guide to someone without the repo, send the standalone [McKesson-DataViz-Guide.html](dist/guide/McKesson-DataViz-Guide.html): one file that works offline. The chart chooser and cheat sheet are in the guide's top bar. Short on time? [demo/](demo/README.md) is the kit on one screen: the explainer video (4:47) and the outputs it shows. The video's source and the engine that made it are in [video/](video/README.md), ready for the next one.

## Three hats

Many people wear all three: consultant before lunch, analyst after lunch, agent wrangler by 3.

| Hat | You live in | Start with |
|---|---|---|
| **Business folks**: consultants, analysts, anyone with a deck due | PowerPoint, Excel | [The guide](dist/guide/index.html) ([PDF](dist/guide/McKesson-DataViz-Guide.pdf)), the [chart chooser](dist/print/chart-chooser.pdf) and [cheat sheet](dist/print/cheat-sheet.pdf) to print or pin, then [docs/office-setup.md](docs/office-setup.md): install the fonts and theme and start from the template, starter deck and chart workbook in [dist/office/](dist/office/). Power BI: [docs/powerbi-setup.md](docs/powerbi-setup.md) and [the theme](dist/powerbi/mckesson-dataviz-theme.json) |
| **Technical folks**: analysts, data scientists, engineers | Python, R, Power BI, the web | **Python:** in any project, `pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"` (fonts and map data included), then `import mckviz as mv; mv.use()`; examples in [examples/python/](examples/python/), `mv.lint` in CI in [docs/ci.md](docs/ci.md). **Web:** [templates/html/chart-card.html](templates/html/chart-card.html) and the themes in [dist/web/](dist/web/). **R:** `source("dist/r/theme_mck.R")`, examples in [examples/r/](examples/r/gallery_ggplot2.R) |
| **AI agents**: Copilot, Claude, coding agents | Wherever you work | [For agents](#for-agents) below |

Making any chart, whatever the tool: [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → the chart's page in [docs/cookbook/](docs/cookbook/) → [docs/qa-checklist.md](docs/qa-checklist.md).

## What's in the box

| | |
|---|---|
| **A guide** | Which chart to use and when, how to keep it on-brand, what to avoid: fundamentals, formats, 12 chart families, a chart chooser and a cheat sheet. [dist/guide/](dist/guide/) |
| **A cookbook** | 23 chart types, each with a spec table, do/don't rules and tested code or click-by-click steps for every platform. [docs/cookbook/](docs/cookbook/) |
| **`mckviz`** | The Python package: style, labels, number formats, chart builders, maps and a chart lint, for matplotlib and Plotly. [python/](python/) |
| **Themes** | Generated from one brand file for HTML/CSS, Plotly, Vega-Lite, matplotlib, ggplot2, Power BI, PowerPoint and Excel, plus the template, starter deck and workbook. [dist/](dist/) |
| **A playbook for agents** | The rules in three sizes: [AGENTS.md](AGENTS.md), the portable [mck-chart skill](dist/skills/mck-chart/SKILL.md), the [one-page rules](dist/agents/mck-viz-rules.md). |

## Getting the kit

- **Technical users:** clone this repo, or install just the Python package from a tagged release (above). Releases are tagged `v<version>`; [CHANGELOG.md](CHANGELOG.md) says what changed.
- **Everyone else:** download the release zip from SharePoint, `DataViz-Starter-Kit-McKesson-Edition-v<version>.zip`, unzip it and open `START-HERE.html`. It holds the standalone and PDF guide, the one-pagers, the Office template, starter deck and workbook, the Power BI theme, the fonts, the web themes, the `mckviz` wheel and the agent files. To make the zip: run the builds, then `python tools/make_bundle.py` (writes `dist/release/`, which is not committed).

## For agents

Three ways to give an AI assistant the chart rules, from fullest to lightest:

| Option | What it is | Use it when |
|---|---|---|
| **This repo's [AGENTS.md](AGENTS.md)** | Full instructions, read automatically by Claude Code (via `CLAUDE.md`), GitHub Copilot (via `.github/copilot-instructions.md`), Cursor, Codex and others, plus the in-repo [`mck-chart` skill](.github/skills/mck-chart/SKILL.md) | You work **in this repo**, on charts or on the kit itself |
| **The portable skill** [dist/skills/mck-chart/](dist/skills/mck-chart/SKILL.md) | A self-contained skill folder: the workflow, the one-page rules, the chart chooser, principles, QA checklist, every cookbook page, theme files and an environment check. The agent loads the detail only when it makes a chart | You make charts **in another repo or tool**: copy the folder to `~/.claude/skills/` (all your projects), a repo's `.claude/skills/` or `.github/skills/`, or upload `agents/mck-chart-skill.zip` from the release bundle to Claude.ai as a custom skill |
| **The single rules file** [dist/agents/mck-viz-rules.md](dist/agents/mck-viz-rules.md) | One self-contained page: workflow, color roles with hex values, type, honest scales, people-data rules, QA checklist | The tool takes one instructions file (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/`), or you paste it into a chat |

In Python, pair any of them with the `mckviz` package (`pip install` from the tag), so agents check their own charts with `mv.lint(fig)`.

## The McKesson Edition

The brand lives in one file, [tokens/tokens.json](tokens/tokens.json): every color, font and chart constant. Change a line, run `python tokens/build.py`, and every theme, template and example updates; check `dist/palette-report.md` afterwards. Do not hand-edit `dist/`. Other McKesson businesses can have their own editions the same way.

Workforce Innovation is the first team using the kit, so the examples are workforce data on purpose: attrition, headcount, hiring, planning. The rules are the same for finance, operations or sales. All example data is synthetic, and every source line says so.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed. Working on the kit itself: [AGENTS.md](AGENTS.md), section B.
