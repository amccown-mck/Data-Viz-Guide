---
name: mck-chart
description: {{description}}
---
<!-- {{generated_note}} -->
# McKesson chart workflow

<!-- portable -->
This skill is the Data Viz Starter Kit, McKesson Edition (v{{version}}), for any repo or tool. Everything it refers to is in this folder: `references/rules.md` (the house rules on one page), `references/choosing-a-chart.md`, `references/principles.md`, `references/qa-checklist.md`, one page per chart type in `references/cookbook/`, and theme files in `assets/`. Setup for each platform is in [Setup](#setup) at the end.
<!-- /portable -->
<!-- copilot -->
This skill is the Data Viz Starter Kit, McKesson Edition (v{{version}}), Microsoft 365 Copilot edition. Everything it refers to is in this skill: `references/rules.md` (the house rules on one page, with the hex value of every color role), the decision tree, the QA checklist, one page per chart type in `references/cookbook/`, and synthetic sample data in `assets/data/`. Charts are drawn in the Python sandbox with `mckviz`, which ships here as source: **load it first** with `scripts/mck_setup.py` (see [Setup](#setup)).
<!-- /copilot -->
<!-- repo -->
This is the in-repo copy of the skill; the full rules are in `AGENTS.md`. A portable copy that works in any repo (and zips for Claude.ai) is generated into `dist/skills/mck-chart/` by `python tools/build_skill.py`.
<!-- /repo -->

<!-- portable,repo -->
Work through the five steps in order. Keep a short **chart brief** as you go and show it to the user with the result.
<!-- /portable,repo -->
<!-- copilot -->
Work through the five steps in order. Keep a short **chart brief** in your reasoning as you go: your working notes, shown only if asked.
<!-- /copilot -->

```
Question:     <one sentence the chart answers>
Mode:         explanatory | exploratory          Medium: slide | report | web | mobile | dashboard
Path:         <shape> -> <question type> -> <chart> (start, go further: <condition>, or option: <why>)
Chart:        <type> ({{docs}}cookbook/<page>.md)
Color:        <pattern> (<why>)   Focus: <what is blue>   Accent: <optional single navy exception>
Headline:     <insight sentence, numbers computed from data>
Subtitle:     <metric, unit, scope, period>
Source:       Source: <system>, as of <date>; <population>
Min n check:  <smallest group shown> (must be ≥ 10)
QA:           pass | exceptions: <list>
```

**Task guides.** This page covers every chart. When the request is one of these, also read the guide before you build; it adds to the steps below and doesn't replace them:
- **Several options or a storyline** ("show me a few ways", "several ways to show it", "N options", "pros and cons for a meeting", "one page to share"): `{{refs}}options.md`, how to pick the angles and the options page. Always `mv.options_page`, never hand-built HTML.
- **Feedback on a chart the user shares:** `{{refs}}review.md`.
- **A slide or deck (a real .pptx), or a native chart in Excel or Power BI, or HTML or R:** `{{refs}}native-formats.md`.

## 1. Question
- Restate the request as **one question** ("Which job families lose the most people, and how far above the enterprise rate?"). If the data can't answer it, say so before you build anything.
- Decide the **mode** (explanatory is the default) and the **medium** (slide, report, web, mobile, dashboard). The medium changes the layout. See `{{docs}}formats.md`.
- Look at the data: grain (individual, team, firm, sector), the n per group, units, time span, and whether a benchmark or target exists.

## 2. Chart type: walk the decision tree
- **Put the data in the tree first:** `print(mv.suggest(df))` on the rows as the user gave them; one row per person stays one row per person, because totaling first hides the spread. It shows how it read each column, the shape, the questions it can answer, the chart to **start with**, and the **go further** rules and **options** that hold, with evidence. Pass `category=`, `measure=`, `size=` or `time=` if a guess is wrong. Without Python, walk `{{docs}}chart-decision-tree.md`.
- **The start chart is the answer most of the time** (a sorted bar for a ranking). Switch only for a **Go further** rule (the start chart would mislead: values clustered far from zero, two units on one axis). Take an **Option** only when the headline depends on it, or as an extra view on an options page. Status pills always show color + symbol + word ("✓ On track").
- **Build with the one-call builder the tree names, also when the user names the chart:** `mv.suggest` prints it after each chart (`mv.bar`, `mv.strip`, `mv.sankey`, ...), `{{docs}}chart-decision-tree.md` lists every chart's, and its cookbook page shows the call. Don't redraw by hand a chart a builder draws.
- **Color from what it encodes** (`{{docs}}chart-decision-tree.md`, section 4): Focus (grey, the named items blue) by default. Focus + accent (grey, a blue group, one navy standout) for a "led by" headline; two items named as equals stay Focus, both blue. Uniform + accent (light blue, one navy exception) when every item is in the story. Categorical when every part must be told apart; Sequential for ordered bands or one measure; Diverging around a benchmark. Stacks: `mv.hstack(story=, accent=, uniform=)`.
- Write the **Path** and **Color** lines in the brief, then **read** `{{docs}}principles.md` and `{{docs}}cookbook/<page>.md`. Note the page's spec table and "When not to use".
- Common traps: clustered values far from zero → dot plot, not truncated bars. Two units over time → two aligned charts, not dual axes. More than 6 categories → highlight plus grey, or group into "Other". A spread across people → distribution, not an average.

## 3. Build
- Start from the cookbook snippet for the platform the user needs. For anything but a PNG or PDF from Python, read `{{refs}}native-formats.md`.
  - **Python:** `import mckviz as mv; mv.use(); C = mv.colors` (`mv.use()` styles matplotlib and activates the "mck" Plotly template). Use `mv.fmt_num` for numbers (K/M/B, %, true minus), `mv.signed(v, decimals=1)` for a signed delta in a headline (its default is 0 decimals: pass the decimals the chart labels use, so "+2.0" in the headline matches "+2.0 hrs" on the bar) and `mv.suppress_small` for the minimum-n rule. Real US, county and world maps: `from mckviz import geo` (see `{{docs}}cookbook/maps.md`).
    - **matplotlib** for slides, PNG, PDF and print: `mv.highlight` for colors, `mv.titles` / `mv.source` / `mv.save` for the frame, `mv.label_bars` / `mv.label_line_ends` for labels.
    - **Copy the cookbook page's runnable snippet and change only the data, labels and focus.** The headline, subtitle and source come from `mv.titles` and `mv.source`, never `fig.text`; when a name is wrong, the error lists the right ones.
<!-- copilot -->
    - **Save only with `mv.save(fig, "<name>.png", dpi=200)`**, then `plt.close(fig)`. Never `plt.savefig`, `fig.savefig` or `plt.show`: the sandbox patches them into Copilot's "Chart" card, which drops the house style. Plotly only for an interactive HTML file the user asks for.
<!-- /copilot -->
<!-- portable,repo -->
    - **Plotly** when the output is interactive or HTML: `mv.pl_highlight` for colors, `mv.pl_finish(fig, headline, subtitle, source_text)` for the frame, then `fig.write_html(...)`.
<!-- /portable,repo -->
- **Highlight what the headline names, and only that:** usually one or two items, more when the headline names a group ("four support roles"). When more qualify than the story is about (three functions below a line), highlight the ones the headline names and keep the rest grey; when most would be blue, none stands out (the builders warn).
- **No hex literals.** Use color roles only: context grey, focus blue, navy accent (the one exception), light blue for a uniform series, navy totals and benchmarks. Orange only when it means "worse" (below target, shrinking, a shortfall), green only when it means "better", both with ▲▼ or words. Red/amber/green only as status colors (`mv.STATUS`) with a symbol and word, never for data series.
- Direct labels, a zero baseline for bars, sorting by value (or natural order), and units in the subtitle.
- When a chart shows a **derived measure** (leavers = headcount × attrition rate, hours freed = FTE × share, cost = headcount × average pay), say so in the footnote and call the result an estimate ("Estimated leavers = headcount × voluntary attrition rate"). Never present a derived count as a recorded one.
- Drop or merge any group with n < 10 **before** plotting (`df, note = mv.suppress_small(df, "headcount")`, then pass `note` as the footnote), and keep individual values out of tooltips.

## 4. Headline
- Compute the finding in code (shares, gaps, counts, multipliers, "n of m"), then write a full sentence with a verb and the number: "Two frontline job families lose about 1 in 4 people a year, well above the 19.9% enterprise rate".
- **Spell out a number that starts the headline** ("Two frontline job families...", not "2 frontline..."); digits are fine anywhere else. `mv.lint` warns when a headline starts with a digit.
- Check every word against the chart: "all", "most", "doubled", "fastest" must be literally true. Recompute; don't eyeball.
- The headline names what the focus color shows. If the two disagree, fix the highlight or the headline.
- The subtitle is neutral: metric, unit, scope, period. The source line names the system, the as-of date and the population (or "Synthetic data for illustration only").
- **Missing metadata.** When the user gives no source system, as-of date or period, ask once if the conversation allows a question. Otherwise write an explicit placeholder in the source line, `Source: [confirm source and as-of date]; <population>`, leave the period out of the subtitle, and say so in the hand-back. Never invent a system name ("Workday HRIS") or a period ("FY26") that the user did not give.

## 5. QA
- Python: run `mv.lint(fig)` (for HTML chart cards, pass `headline=`, `subtitle=`, `source=`). Fix every error and read the warnings.
- Render the chart and **look at it**: open the PNG, or screenshot the HTML at desktop width and at 390 px.
- Go through `{{docs}}qa-checklist.md` and the cookbook page's "QA specifics". Fix what fails. For anything you can't fix, name it in the brief under "QA exceptions".
- Write `QA: pass` only when `mv.lint` ran with no errors and you looked at the render. Otherwise say what was and wasn't checked (`QA: checklist by hand; mv.lint not run because ...`).
- Write alt text: the headline plus 2–3 key numbers.
<!-- repo -->
- If you edited cookbook code in this repo, run `python tools/check_snippets.py docs/cookbook/<page>.md`.
<!-- /repo -->

## Hand-back
<!-- portable,repo -->
Give the user the output (file path, or code plus the rendered image), the chart brief, and the alt text. Mention any assumptions about the data (definitions, exclusions, suppressed groups), every placeholder left in the chart (source, as-of date, period), and which install path the build used (mckviz, or the no-package fallback and its font).
<!-- /portable,repo -->
<!-- copilot -->
Write for a busy colleague who knows Excel and PowerPoint, not chart terms. Lead with what they asked for (for a chart, its headline), then the chart, then:
- **Why this chart:** one or two plain sentences that teach the choice ("A sorted bar makes a ranking of ten job families instant; blue marks the two the headline names").
- **Before you share:** placeholders left in the chart (source, as-of date, period), data assumptions (definitions, exclusions, groups left out for privacy) and QA exceptions.
- **Alt text:** one line.

Leave the brief's labels (Path, Mode, Focus, QA) and tool names out of the reply. When it helps, end with one line offering two or three next steps (a slide, other ways to show it, a different highlight); not while the user is making small edits.

**Files reach the user's OneDrive once, through `mv.deliver`:** build and check in `/tmp/` (`mv.look(png)` shows a render), then `mv.deliver(path, ...)` as the last step, and link only what it returns. mckviz refuses to write into `/mnt/data/`; never `cp`, `mv` or `rm` there. A revision the user asks for goes under a new name (`revision=`).
In Copilot, `mv.save` the PNG to `/tmp/`, `mv.deliver` it, and **show it inline as an image** (`![<headline>](sandbox:/mnt/data/<name>.png)`) with a download link under it. If a "Chart" card appears instead (a bare re-plot, axes "X" and "Y"), rebuild with `mv.save` and deliver it under a new name. Show the code only if the user asks.
<!-- /copilot -->
<!-- portable -->

## Setup
- **Python** (3.10+): run `python scripts/check_env.py` (in this folder). It installs `mckviz` from the wheel in `assets/python/` when it isn't installed yet, falls back to GitHub, registers Libre Franklin and prints which path worked. By hand, in this order, stopping at the first that works:
  1. `pip install assets/python/mckviz-*.whl` (no access to GitHub needed; the fonts and map data are inside; add `--no-deps` if PyPI is unreachable and matplotlib is already installed), plus `plotly` and `pandas` if you use them.
  2. `pip install "mckviz @ git+{{repo_url}}@v{{version}}#subdirectory=python"`.
  3. If neither works, build without the package: take the color roles from `references/rules.md` and define them once as named constants, register the TTFs in `assets/fonts/` with matplotlib (`font_manager.addfont`), and go through `references/qa-checklist.md` by hand in place of `mv.lint`. If the font cannot be registered either, use **Liberation Sans or Arimo** (metric-compatible with Arial), leave label slack, and list the font under QA exceptions in the brief. Say in the hand-back which path you used.
- **HTML / JS:** copy `assets/web/` next to the page; `assets/html/chart-card.html` is a working starter (bar and line cards). Fonts: `assets/fonts/` has the TTFs for an offline `@font-face`.
- **R:** `source("assets/r/theme_mck.R")`. **Power BI:** import `assets/powerbi/mckesson-dataviz-theme.json`.
- **Excel / PowerPoint:** the template (`assets/office/McKesson-DataViz.potx`), the theme color and font XML (`assets/office/Theme Colors/`, `Theme Fonts/`), the pptxgenjs theme (`assets/office/pptxgenjs-theme.js`) and the fonts (`assets/fonts/`) are in this folder. The starter deck and chart workbook are in the release bundle (`DataViz-Starter-Kit-McKesson-Edition-v{{version}}.zip`) or at {{repo_url}}.
- **Cookbook snippets run from this folder:** paths such as `assets/data/workforce_mix.csv` (synthetic sample data) and `assets/web/mck-viz.css` are relative to the skill folder, so `cd` here first, or replace the path with the user's file and keep the structure. Outputs go to `out/`.
<!-- /portable -->
<!-- copilot -->

## Setup
- **Load mckviz at the top of every chart script.** The sandbox can't install packages or reach the internet, so the package ships here as source, and `scripts/mck_setup.py` assembles it in a temp folder (it restores the font and the matplotlib style, which ship as text) and applies the style. In Microsoft 365 Copilot this skill sits under `/home/oai/skills/` (for example `/home/oai/skills/appCatalog/<id>/mck-chart/`), and each command runs in a fresh process, so start every script with:
  ```python
  import glob, runpy
  setup_py = glob.glob("/home/oai/skills/**/mck-chart/scripts/mck_setup.py", recursive=True)[0]
  setup = runpy.run_path(setup_py, run_name="__main__")      # prints what loaded; takes a second
  mv, C, SKILL_DIR = setup["mv"], setup["C"], setup["SKILL_DIR"]
  ```
  If the glob finds nothing, search for `mck_setup.py` (`find / -name mck_setup.py 2>/dev/null`) and use that path. Check the last line it prints: if Libre Franklin did not load, list the fallback font under QA exceptions.
- **If mckviz won't load** (matplotlib is missing, or the script can't run), build without the package: take the color roles from `references/rules.md` and define them once as named constants, and go through `references/qa-checklist.md` by hand in place of `mv.lint`. If no code can run at all, give the user the chart spec (type, sort, which bar is blue, labels, headline, subtitle, source) and the cookbook page's Excel / PowerPoint steps. Say in the hand-back which path you used.
- **Data:** read the user's upload in the sandbox (pandas). Cookbook paths such as `assets/data/workforce_mix.csv` (synthetic sample data) are relative to `SKILL_DIR`; when a snippet reads one, swap in the user's data and keep the structure. Files that cookbook pages name under `assets/web/`, `assets/r/` or `assets/office/` aren't in this edition (see `references/native-formats.md`).
<!-- /copilot -->
