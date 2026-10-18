# Data Viz Starter Kit · McKesson Edition

**Your own data storytelling team, ready when you are.**

> Version 1.1.0 (see [CHANGELOG.md](CHANGELOG.md); the version lives in [VERSION](VERSION)). How we name and describe the kit: [docs/positioning.md](docs/positioning.md). What's next: [ROADMAP.md](ROADMAP.md). License: MIT ([LICENSE](LICENSE)); fonts and map data carry their own open licenses, listed there. Maintainer: Ashley McCown, Workforce Innovation, via [issues](https://github.com/amccown-mck/Data-Viz-Guide/issues).

**What it is.** Top consulting firms have a team behind every executive presentation, people whose whole job is turning analysis into a chart a leader gets at a glance. The Data Viz Starter Kit puts that know-how in your hands. You get a guide that teaches the craft, templates and code that start you off right in PowerPoint, Excel, Power BI and Python, and a quick check before you share. Your AI assistant can use it too.

**Why it matters.** Clear charts move decisions forward. When the point of a chart is obvious, a meeting spends its time on what to do, not on what the chart means. That's the standard top consulting firms hold every chart to, and it's a craft anyone can learn with the right tools. This kit makes it the easy path for every McKesson team. The rules are short: start from the question, write the finding as the headline, grey for context with one blue focus, honest scales, direct labels, a source line, no group under 10 people.

**Why it isn't another style guide.** A style guide describes good charts. This kit makes them the default. Every color, font and chart rule lives in one file and is generated into the PowerPoint template, the Excel workbook, the Power BI theme, the web and R themes and the `mckviz` Python package, so a new chart starts on-brand instead of being fixed later. And the rules are written to be checked: a reviewer has a checklist, code has `mv.lint`, and an AI assistant works from the rules and runs the checks itself before you see the chart.

**Start here: the guide.** Open [dist/guide/index.html](dist/guide/index.html) in a browser, or read the same pages as a 16:9 PDF: [McKesson-DataViz-Guide.pdf](dist/guide/McKesson-DataViz-Guide.pdf). To send the clickable guide to someone without the repo, send the standalone [McKesson-DataViz-Guide.html](dist/guide/McKesson-DataViz-Guide.html): one file that works offline. The chart chooser and cheat sheet are in the guide's top bar. Short on time? [demo/](demo/README.md) is the kit on one screen: the explainer video (4:47) and the outputs it shows. The video's source and the engine that made it are in [video/](video/README.md), ready for the next one.

## Who it's for: three ways in

Anyone at McKesson who needs to communicate with data: analysts, consultants, data scientists, and the leaders who present their work. People move between tools all week, so start from where you're working, not who you are.

| Way in | You work in | Start with |
|---|---|---|
| **In PowerPoint and Excel** | PowerPoint, Excel, Power BI | [The guide](dist/guide/index.html) ([PDF](dist/guide/McKesson-DataViz-Guide.pdf)), the [chart chooser](dist/print/chart-chooser.pdf) and [cheat sheet](dist/print/cheat-sheet.pdf) to print or pin, then [docs/office-setup.md](docs/office-setup.md): install the fonts and theme and start from the template, starter deck and chart workbook in [dist/office/](dist/office/). Power BI: [docs/powerbi-setup.md](docs/powerbi-setup.md) and [the theme](dist/powerbi/mckesson-dataviz-theme.json) |
| **In code** | Python, R, the web | **Python:** in any project, `pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"` (fonts and map data included), then `import mckviz as mv; mv.use()`; examples in [examples/python/](examples/python/), `mv.lint` in CI in [docs/ci.md](docs/ci.md). **Web:** [templates/html/chart-card.html](templates/html/chart-card.html) and the themes in [dist/web/](dist/web/). **R:** `source("dist/r/theme_mck.R")`, examples in [examples/r/](examples/r/gallery_ggplot2.R) |
| **With an AI assistant** | Copilot, Claude, coding agents | [For agents](#for-agents) below |

Workforce Innovation uses the kit first, so the examples are workforce data on purpose: attrition, headcount, hiring, planning. The rules work the same for finance, operations or sales.

Making any chart, whatever the tool: [docs/principles.md](docs/principles.md) → [docs/choosing-a-chart.md](docs/choosing-a-chart.md) → the chart's page in [docs/cookbook/](docs/cookbook/) → [docs/qa-checklist.md](docs/qa-checklist.md).

## What you get

| What a consulting firm's team gives you | What the kit gives you |
|---|---|
| **A data storytelling expert who knows which chart** | **The guide and chart chooser.** Fundamentals, formats, 12 chart families, a chooser that says why and a cheat sheet. [dist/guide/](dist/guide/) |
| **A house style** | **Themes and templates**, generated from one brand file for HTML/CSS, Plotly, Vega-Lite, matplotlib, ggplot2, Power BI, PowerPoint and Excel, plus the template, starter deck and workbook. [dist/](dist/) |
| **Worked examples to copy** | **The cookbook**: 23 chart types, each with a spec table, do/don't rules and tested code or click-by-click steps for every platform [docs/cookbook/](docs/cookbook/). In Python, **`mckviz`** adds the style, labels, number formats, chart builders and maps [python/](python/) |
| **A review before it reaches an executive** | **The QA checklist** [docs/qa-checklist.md](docs/qa-checklist.md) and **`mv.lint`**, which checks a matplotlib or Plotly chart against the rules |
| **Associates who follow the house rules** | **The agent playbook** in three sizes: [AGENTS.md](AGENTS.md), the portable [mck-chart skill](dist/skills/mck-chart/SKILL.md), the [one-page rules](dist/agents/mck-viz-rules.md) |

## Getting the kit

- **Technical users:** clone this repo, or install just the Python package from a tagged release (above). Releases are tagged `v<version>`; [CHANGELOG.md](CHANGELOG.md) says what changed.
- **Everyone else:** download the release zip from the repo's [Releases](https://github.com/amccown-mck/Data-Viz-Guide/releases), `DataViz-Starter-Kit-McKesson-Edition-v<version>.zip`, unzip it and open `START-HERE.html`. It holds the standalone and PDF guide, the one-pagers, the Office template, starter deck and workbook, the Power BI theme, the fonts, the web themes, the `mckviz` wheel and the agent files. To make the zip: run the builds, then `python tools/make_bundle.py` (writes `dist/release/`, which is not committed).

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

All example data is synthetic, and every source line says so.

`reference/` holds paraphrased notes on the McKinsey guide that were used as inspiration. They are for internal reference only, and no source images are committed. Working on the kit itself: [AGENTS.md](AGENTS.md), section B.
