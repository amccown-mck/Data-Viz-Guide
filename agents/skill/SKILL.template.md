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
This skill is the Data Viz Starter Kit, McKesson Edition (v{{version}}), Microsoft 365 Copilot edition. Everything it refers to is in this skill: `references/rules.md` (the house rules on one page, with the hex value of every color role), `references/choosing-a-chart.md`, `references/principles.md`, `references/qa-checklist.md`, one page per chart type in `references/cookbook/`, and synthetic sample data in `assets/data/`. Charts are drawn in the Python sandbox with `mckviz`, which ships in this skill as source: **load it first** with `scripts/mck_setup.py` (see [Setup](#setup)). The user usually pastes a table, uploads a spreadsheet, or shares a chart and asks for feedback on it (see [Reviewing a chart](#reviewing-a-chart)).
<!-- /copilot -->
<!-- repo -->
This is the in-repo copy of the skill; the full rules are in `AGENTS.md`. A portable copy that works in any repo (and zips for Claude.ai) is generated into `dist/skills/mck-chart/` by `python tools/build_skill.py`.
<!-- /repo -->

Work through the five steps in order. Keep a short **chart brief** as you go and show it to the user with the result.

```
Question:     <one sentence the chart answers>
Mode:         explanatory | exploratory          Medium: slide | report | web | mobile | dashboard
Path:         <shape> -> <question type> -> <chart> (start, or go further: <condition that holds>)
Chart:        <type> ({{docs}}cookbook/<page>.md)
Color:        <pattern> (<why>)   Focus: <what is blue>   Accent: <optional single navy exception>
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

## 2. Chart type: walk the decision tree
- **Put the data in the tree first:** `print(mv.suggest(df))`. It says how it read each column, which shape the data has, the questions that shape can answer, the chart to **start with**, and the richer charts to **go further** with whose conditions hold in this data, with the evidence ("headcount runs from 450 to 11,800"). Check how it read the columns and pass `category=`, `measure=`, `size=` or `time=` if a guess is wrong. Without Python, walk `{{docs}}chart-decision-tree.md` by hand.
- **Pick the question, then the chart.** Use the start chart when no condition holds. When one holds, use the richer chart if it answers the question better (counts that differ 26-fold make a bubble strip show both how close the groups are and how many people each covers); don't fall back to a bar or a stacked bar out of habit. Status pills always show color + symbol + word ("✓ On track").
- **Pick the color from what it encodes** (`{{docs}}chart-decision-tree.md`, section 4): Focus (grey, the named items blue) is the default; Uniform + accent or Focus + accent for one exception; Categorical when every part or series must be told apart; Sequential light-to-dark for ordered bands or one measure; Diverging around a benchmark; Story segment + greys only when one part is the story. A stack of greys is right only in that last case.
- Write the **Path** and **Color** lines in the brief, then **read** `{{docs}}principles.md` and `{{docs}}cookbook/<page>.md`. Note the page's spec table and "When not to use".
- Common traps: clustered values far from zero → dot plot, not truncated bars. Two units over time → two aligned charts, not dual axes. More than 6 categories → highlight plus grey, or group into "Other". A spread across people → distribution, not an average.

### Storyline or options requests
When the user pastes a table and asks for "N options" or "charts that fit this storyline", don't build N charts of the same thing. Work the data first, then the angles:
- **List the question types the data can support:** `mv.suggest(df)` lists every shape and question the data fits and what it can't support. One period and one measure per category supports magnitude (ranked bars with a benchmark line), deviation from a benchmark (diverging bars, `mv.diverging_bars`) and derived counts (headcount × rate, as a second ranked bar or a KPI card). A slope or change-over-time chart needs **two periods**. A heat table needs **two dimensions**. A correlation or bubble scatter needs two measures per category (a count can be the bubble area). A part-to-whole needs parts that sum to a whole.
- **Say what the data cannot support.** If an asked-for chart needs a field the table lacks (a trend without a second period, a heat table with one dimension), name it and what would be needed, instead of forcing it.
- **Vary the charts.** Each option is a different chart type from a different leaf; when `mv.suggest` lists go-further charts, at least one option uses one. Five bar charts are not five options.
- **Build one chart per supported angle**, each with its own headline computed from the data and its own focus. Different angles may name different focus items; each chart's headline must match its own highlight.
- **Hand back a one-line brief per option** (angle, chart type, headline) plus **a recommendation of which one to lead with** and why (usually the one whose headline answers the storyline's question most directly), then the full chart brief for that one.

### The options page
When people see the same data differently ("show me a few ways to present this", "leadership can't agree how to show it", "options with pros and cons for a meeting"), build 3–6 views as above and hand them over as **one self-contained HTML page** with `mv.options_page` (the charts, Libre Franklin and the styles are all inside the file; it opens offline and prints one option per page):
```python
opts = [mv.Option(fig, name="Roles ranked by exposure", question="Which roles have the most exposed work?",
                  how_to_read="One bar per role, sorted, against the workforce average.",
                  strength="Every role is visible.", tradeoff="It treats a role of 450 people like one of 11,800.",
                  alt="<headline plus 2-3 key numbers>"), ...]
mv.options_page("<topic>-options.html", title="<Topic>: four ways to show it", options=opts,
                lede="Four views of the same data. Each answers a different question; use one or combine them.",
                findings=[("<bold lead>", "<rest, numbers computed from the data>"), ...],   # 2-3 facts
                notes={"<term>": "<definition>", "Data": "<n, scope, exclusions, suppressed groups>"},
                source="Source: <system>, as of <date>; <population>", label="Internal · For discussion")
```
- Each option is a finished chart (headline, subtitle, source, `mv.lint` clean) from the same data. Give each one a different question, a fair strength, and a real trade-off: what it hides, distorts or assumes.
- Stay neutral unless the user asks which to lead with; then add `recommendation="..."` and `lead=<option number>`.
- Mark sensitivity with `label=` (ask once if the data is internal; never leave real people data unlabeled).
- With four or more options, make one a **blended table** (`mv.table`: inline bars, one heat column, a change column, bold focus rows, a weighted total), so every reader can find their own row; put it last, as the reference view.
- Hand back the page, a one-line brief per option, and how to use it: open it in a browser, "Save as PDF" for a handout, Download or Copy under each chart for PowerPoint.
<!-- copilot -->
- In Copilot, write the page to `/mnt/data/`, run `plt.close("all")` after `mv.options_page`, and give a download link to the .html. Don't show every chart inline: list the options with their headlines instead.
<!-- /copilot -->

## 3. Build
- Start from the cookbook snippet for the platform the user needs:
  - **Python:** `import mckviz as mv; mv.use(); C = mv.colors` (`mv.use()` styles matplotlib and activates the "mck" Plotly template). Use `mv.fmt_num` for numbers (K/M/B, %, true minus), `mv.signed(v, decimals=1)` for a signed delta in a headline (its default is 0 decimals: pass the decimals the chart labels use, so "+2.0" in the headline matches "+2.0 hrs" on the bar) and `mv.suppress_small` for the minimum-n rule. Real US, county and world maps: `from mckviz import geo` (see `{{docs}}cookbook/maps.md`).
    - **matplotlib** for slides, PNG, PDF and print: `mv.highlight` for colors, `mv.titles` / `mv.source` / `mv.save` for the frame, `mv.label_bars` / `mv.label_line_ends` for labels.
    - **Copy the cookbook page's runnable snippet and change only the data, labels and focus.** Don't hand-build the frame with `fig.text` (the headline, subtitle and source come from `mv.titles` and `mv.source`, laid out by `mv.save`), and don't guess names. The color roles are `C.focus` (blue), `C.focus_light`, `C.context` (grey), `C.context_light`, `C.accent` (navy exception), `C.total` (navy totals and benchmarks), `C.negative` (orange, worse), `C.positive` (green, better), `C.text`, `C.text_muted`, `C.headline`, `C.title`; there is no `C.grey` or `C.muted`.
<!-- copilot -->
    - **Always draw with mckviz in the Python sandbox** and show the PNG it saves (`mv.save(fig, "<name>.png", dpi=200)`, then `plt.close(fig)`). **Save only with `mv.save`**: never `plt.savefig`, `fig.savefig` or `plt.show`, which the sandbox has patched to turn the chart into a card. **Never use Copilot's built-in chart card** (the interactive "Chart" with a `</>` icon), even when it is quicker: it can't apply the house style (it draws rounded bars, gridlines, its own blue and font, a value axis instead of direct labels, and no headline, subtitle or source on the chart). If Python can't run, say so and use the fallback in [Setup](#setup); never substitute the chart card. Use Plotly only when the user asks for an interactive HTML file to download, and only if `import plotly` works in the sandbox.
  - **Excel / PowerPoint:** a deck that leaves the team needs a **native, editable chart**, not a picture. Give the PNG for a draft or a quick look, then the cookbook page's Excel / PowerPoint steps with the user's numbers, labels and focus filled in, and the headline, subtitle and source written out ready to paste. The colors for those steps are the hex values in `references/rules.md`. The PowerPoint template, the starter deck (native charts on the template grid) and the chart workbook are in the release bundle ({{repo_url}}/releases); `references/office-setup.md` covers the theme and the font.
  - **Power BI:** follow the cookbook page's Power BI section. The report theme is `assets/powerbi/mckesson-dataviz-theme.json` (also in the release bundle) and `references/powerbi-setup.md` has the steps. Write the DAX for the highlight measure and the minimum-n rule (`IF([Headcount] < 10, BLANK(), ...)`) when the user needs it.
<!-- /copilot -->
<!-- portable,repo -->
    - **Plotly** when the output is interactive or HTML: `mv.pl_highlight` for colors, `mv.pl_finish(fig, headline, subtitle, source_text)` for the frame, then `fig.write_html(...)`.
  - **HTML:** the chart-card pattern with {{web_css}} plus {{web_plotly}} or {{web_vega}}{{chart_card}}.
  - **Excel / PowerPoint:** build a **native, editable chart**, never a pasted picture, when a pptx tool is available. In Claude.ai, or any environment with a pptx skill (pptxgenjs), use it with the theme and chart options in {{pptx_theme}} (`MCK.theme`, `MCK.text.*` on the slide grid, `MCK.barChart` with `MCK.pointColors(labels, focus)`) and the recipe in `{{docs}}office-setup.md` ("A native chart from code with pptxgenjs"): the headline in the title placeholder at 26 pt Bold McKesson Blue, the subtitle and source as text, and the benchmark line and bold focus labels as shapes over the pinned plot area. Without a pptx tool, start from the starter deck (`McKesson-DataViz-Starter.pptx`, native charts on the template grid) and follow the cookbook page's Excel / PowerPoint section by hand, or render a PNG with matplotlib and place it on the slide as the last resort.
  - **Power BI, R:** follow the cookbook page's section for that platform, using {{themes}}.
<!-- /portable,repo -->
- **At most two highlighted items**, and they are what the headline names. When more qualify (three functions below a line), highlight the two the headline is about and keep the rest grey, or make the one exception the navy accent.
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
Give the user the output (file path, or code plus the rendered image), the chart brief, and the alt text. Mention any assumptions about the data (definitions, exclusions, suppressed groups), every placeholder left in the chart (source, as-of date, period), and which install path the build used (mckviz, or the no-package fallback and its font).
<!-- copilot -->
In Copilot, save the PNG to `/mnt/data/` and **show it inline as an image** (`![<headline>](sandbox:/mnt/data/<name>.png)`), with a download link under it. A PNG from `mv.save` shows as a static image. If an interactive "Chart" card appears instead (a bare re-plot with a generic "X" or "Y" axis title), something saved with `savefig` or `plt.show`: that card is not the deliverable, so never present it as the chart; save again with `mv.save` and show that file. Open the reply with the headline sentence (never a question or a topic label like "Copilot adoption: where are we lagging?"). Show the code only if the user asks for it.

## Reviewing a chart
When the user shares a chart (an image, a slide, a dashboard screenshot) and asks for feedback:
- Say what question the chart seems to answer and who it is for. If you can't tell, that is the first finding.
- Check it against `references/rules.md`, `references/qa-checklist.md` and the cookbook page for its chart type. Rank the issues by how much they hurt the reading: a misleading scale or the wrong chart type first, then the headline (is it a finding, and does the chart prove it?), the highlight, labels and legend, color meaning, people-data rules (groups under 10), and the source line.
- For each issue, give the fix in one line. Keep what already works.
- Offer to redraw it. Build from the user's data when they can share it; values read off an image are approximate, so say so and ask the user to confirm them before the redraw goes in a deck.
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
- **Data:** read the user's upload in the sandbox (pandas). Cookbook paths such as `assets/data/workforce_mix.csv` (synthetic sample data) are relative to `SKILL_DIR`; when a snippet reads one, swap in the user's data and keep the structure.
- **Not in this edition:** Copilot skills can't carry the web themes (CSS), the R theme, the PowerPoint template (.potx) or the font files as they are, so files that cookbook pages name under `assets/web/`, `assets/html/`, `assets/r/` and `assets/office/` aren't here. They're in the release bundle ({{repo_url}}/releases), which is where the user gets the Office template and the font.
<!-- /copilot -->
