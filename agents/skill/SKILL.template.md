---
name: mck-chart
description: Make a McKesson-standard chart or table from data, going from question to chart type, build with mckviz (or the web, Office, Power BI or R theme), insight headline, and QA checklist. Use whenever the user asks for a chart, graph, plot, visualization, scorecard or exhibit for McKesson, or for Workforce Innovation work (people analytics, workforce intelligence or planning / SWP data).
---
<!-- {{generated_note}} -->
# McKesson chart workflow

<!-- portable -->
This skill is the McKesson data-visualization kit (v{{version}}) for any repo or tool. Everything it refers to is in this folder: `references/rules.md` (the house rules on one page), `references/choosing-a-chart.md`, `references/principles.md`, `references/qa-checklist.md`, one page per chart type in `references/cookbook/`, and theme files in `assets/`. Setup for each platform is in [Setup](#setup) at the end.
<!-- /portable -->
<!-- repo -->
This is the in-repo copy of the skill; the full rules are in `AGENTS.md`. A portable copy that works in any repo (and zips for Claude.ai) is generated into `dist/skills/mck-chart/` by `python tools/build_skill.py`.
<!-- /repo -->

Work through the five steps in order. Keep a short **chart brief** as you go and show it to the user with the result.

```
Question:     <one sentence the chart answers>
Mode:         explanatory | exploratory          Medium: slide | report | web | mobile | dashboard
Chart:        <type> ({{docs}}cookbook/<page>.md)    Why: <question type → first choice / alternative>
Focus:        <what is blue>   Accent: <optional single navy exception>   Context: everything else, grey
Headline:     <insight sentence, numbers computed from data>
Subtitle:     <metric, unit, scope, period>
Source:       Source: <system>, as of <date>; <population>
Min n check:  <smallest group shown> (must be ≥ 10)
QA:           pass | exceptions: <list>
```

## 1. Question
- Restate the request as **one question** ("Which job families lose the most people, and how far above the enterprise rate?"). If the data can't answer it, say so before you build anything.
- Decide the **mode** (explanatory is the default) and the **medium** (slide, report, web, mobile, dashboard). The medium changes the layout. See `{{docs}}formats.md`.
- Look at the data: grain (individual, team, firm, sector), the n per group, units, time span, and whether a benchmark or target exists.

## 2. Chart type
- Name the question type: magnitude, part-to-whole, change over time, ranking, distribution, correlation, relationships & flows, geo-spatial, single number, or plans and status (roadmap / Gantt, initiative tracker, milestones; status pills always show color + symbol + word, e.g. "✓ On track").
- Pick from `{{docs}}choosing-a-chart.md` (the first choice unless a sanity check rules it out), then **read** `{{docs}}principles.md` and `{{docs}}cookbook/<page>.md`. Note the page's spec table and "When not to use".
- Common traps: clustered values far from zero → dot plot, not truncated bars. Two units over time → two aligned charts, not dual axes. More than 6 categories → highlight plus grey, or group into "Other". A spread across people → distribution, not an average.

## 3. Build
- Start from the cookbook snippet for the platform the user needs:
  - **Python:** `import mckviz as mv; mv.use(); C = mv.colors` (`mv.use()` styles matplotlib and activates the "mck" Plotly template). Use `mv.fmt_num` for numbers (K/M/B, %, true minus) and `mv.suppress_small` for the minimum-n rule. Real US, county and world maps: `from mckviz import geo` (see `{{docs}}cookbook/maps.md`).
    - **matplotlib** for slides, PNG, PDF and print: `mv.highlight` for colors, `mv.titles` / `mv.source` / `mv.save` for the frame, `mv.label_bars` / `mv.label_line_ends` for labels.
    - **Plotly** when the output is interactive or HTML: `mv.pl_highlight` for colors, `mv.pl_finish(fig, headline, subtitle, source_text)` for the frame, then `fig.write_html(...)`.
  - **HTML:** the chart-card pattern with {{web_css}} plus {{web_plotly}} or {{web_vega}}{{chart_card}}.
  - **Excel / PowerPoint:** there is no Python-to-pptx path. Start from the starter deck (`McKesson-DataViz-Starter.pptx`, native charts on the template grid) and follow the cookbook page's Excel / PowerPoint section; or render a PNG with matplotlib and place it on the slide.
  - **Power BI, R:** follow the cookbook page's section for that platform, using {{themes}}.
- **No hex literals.** Use color roles only: context grey, focus blue, navy accent (the one exception), light blue for a uniform series, navy totals and benchmarks. Orange only when it means "worse" (below target, shrinking, a shortfall), green only when it means "better", both with ▲▼ or words. Red/amber/green only as status colors (`mv.STATUS`) with a symbol and word, never for data series.
- Direct labels, a zero baseline for bars, sorting by value (or natural order), and units in the subtitle.
- Drop or merge any group with n < 10 **before** plotting (`df, note = mv.suppress_small(df, "headcount")`, then pass `note` as the footnote), and keep individual values out of tooltips.

## 4. Headline
- Compute the finding in code (shares, gaps, counts, multipliers, "n of m"), then write a full sentence with a verb and the number: "Two frontline job families lose about 1 in 4 people a year, well above the 19.9% enterprise rate".
- Check every word against the chart: "all", "most", "doubled", "fastest" must be literally true. Recompute; don't eyeball.
- The headline names what the focus color shows. If the two disagree, fix the highlight or the headline.
- The subtitle is neutral: metric, unit, scope, period. The source line names the system, the as-of date and the population (or "Synthetic data for illustration only").

## 5. QA
- Python: run `mv.lint(fig)` (for HTML chart cards, pass `headline=`, `subtitle=`, `source=`). Fix every error and read the warnings.
- Render the chart and **look at it**: open the PNG, or screenshot the HTML at desktop width and at 390 px.
- Go through `{{docs}}qa-checklist.md` and the cookbook page's "QA specifics". Fix what fails. For anything you can't fix, name it in the brief under "QA exceptions".
- Write alt text: the headline plus 2–3 key numbers.
<!-- repo -->
- If you edited cookbook code in this repo, run `python tools/check_snippets.py docs/cookbook/<page>.md`.
<!-- /repo -->

## Hand-back
Give the user the output (file path, or code plus the rendered image), the chart brief, and the alt text. Mention any assumptions about the data (definitions, exclusions, suppressed groups).
<!-- portable -->

## Setup
- **Python** (3.10+): `pip install "mckviz @ git+{{repo_url}}@v{{version}}#subdirectory=python"`, plus `plotly` and `pandas` if you use them. The fonts and map data come with the package. Run `python scripts/check_env.py` (in this folder) to confirm `mckviz` is installed and Libre Franklin registers; it prints the install command if not. If you can't install packages, take the colors from `references/rules.md` and define them once as named constants.
- **HTML / JS:** copy `assets/web/` next to the page; `assets/html/chart-card.html` is a working starter (bar and line cards).
- **R:** `source("assets/r/theme_mck.R")`. **Power BI:** import `assets/powerbi/mckesson-dataviz-theme.json`.
- **Excel / PowerPoint:** the template, starter deck, workbook and fonts are in the release bundle (`McKesson-DataViz-Kit-v{{version}}.zip`) or at {{repo_url}}.
- **Cookbook snippets run from this folder:** paths such as `assets/data/workforce_mix.csv` (synthetic sample data) and `assets/web/mck-viz.css` are relative to the skill folder, so `cd` here first, or replace the path with the user's file and keep the structure. `office/...` and `fonts/...` paths are folders in the release bundle. Outputs go to `out/`.
<!-- /portable -->
