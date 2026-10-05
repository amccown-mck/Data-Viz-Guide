# Changelog

All notable changes to the McKesson data-visualization kit (the guide, the themes, the `mckviz` package and the agent assets). The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/): a major version changes a rule or breaks code that uses `mckviz`, a minor version adds things, a patch fixes them.

The version lives in one place, the `VERSION` file at the repo root. `tokens/build.py` copies it into the Python package, and the guide cover, the agent rules, the portable skill and the release bundle read it from there. Releases are tagged `v<version>` (for example `v1.1.0`); `pip install` and the release bundle refer to those tags.

## [Unreleased]

### Added
- **`mckviz.charts`: the guide's chart builders in the package** (2026-10-05). `waterfall`, `hstack` (100% stacked with the story segment on the baseline), `dumbbell`, `rank_slope`, `heat` + `key_strip`, `kpi_card` / `kpi_row` / `ring` / `delta_label`, `status` / `sdot` / `status_column`, `tracker`, `roadmap`, `multiples`. Sizes come from the typography roles and colours from `mv.colors`; every builder passes `mv.lint(strict=True)` and the rules are tested (navy totals, green only with ▲, status always colour + symbol + word, story segment first, minimum n, shared scales). The cookbook's waterfall, stacked-bar, dumbbell, heatmap, KPI and small-multiples recipes use them.
- **Plans and status cookbook page** (`docs/cookbook/plans-status.md`): roadmap, tracker, status column and status history in Python, the web status pill, tracker table and Plotly roadmap, and pointers to the starter-deck slides; linked from the chooser and the guide's Plans build spread.
- **Office starter: 14 slides and 7 new sheets.** KPI card, roadmap/Gantt (native stacked bar with phase bands, milestones ◆ ◇ ✕, slip arrow, dashed Today line, status at the row ends), initiative tracker table, two-charts-on-a-slide, column with highlight, dumbbell, slope and bubble; the workbook mirrors KPI, Roadmap, Tracker, Column, Dumbbell, Slope and Scatter with formula-driven numbers, dropdown statuses and conditional symbols. `docs/office-setup.md` gains "Starter deck, slide by slide". Needs a visual check on Windows (list in ROADMAP).
- **Web dashboard components** in `mck-viz.css`: `.mck-kpi` tile (▲/▼, good/bad, dark variant), `.mck-status--*` pills (colour + symbol + word, never colour alone), `.mck-grid` (1/2/3 columns), `.mck-table--heat` cell classes, `.mck-tracker`. **`dist/web/mck-viz.js`**, generated from the tokens: `tok`, `highlight`, `fmtNum` and `suppressSmall` (identical output to the Python helpers), `textOn`, `status`, `plotlyLayout`, `zeroLine`, `srTable`. **Offline chart card** `templates/html/chart-card-offline.html` with local fonts and `dist/web/vendor/plotly.min.js` (Plotly.js 4.1.1, MIT, 4.8 MB). HTML/JavaScript recipes on the waterfall, stacked-bar, heatmap, KPI and plans-status pages. The release bundle ships all of it.
- **Consistency test** (`python/tests/test_consistency.py`): AGENTS.md, the Copilot files, the colour and typography docs, the Power BI doc and the rules template must agree with `tokens.json` on the categorical order, the slide-title and chart-headline specs and the minimum n, and must not carry superseded wording. It caught four stale lines on its first run.
- **Portable skill:** `dist/skills/mck-chart/` ships the sample CSVs its recipes read (`assets/data/`) and rewrites repo paths, so the snippets run from the skill folder outside this repo; `tools/build_skill.py --zip` writes `dist/skills/mck-chart.zip` for Claude.ai. The skill now covers Plotly (`mv.pl_highlight`, `mv.pl_finish`), says there is no Python-to-pptx path, and lists the Plans and status family; the chart brief has one format (skill template, AGENTS.md hand-back, guide page).
- **Lint:** a third overlaid y axis and 3-D traces are errors in Plotly; `texttemplate` labels count as labels; Plotly text under 11 px warns. Colours on a token ramp (heatmaps and colour-mapped scatters drawn with `mv.sequential_cmap()` / `mv.diverging_cmap()`) no longer trip the 6-colour or off-palette rules, and `imshow` images are checked.
- **Plotly template:** waterfall (grey / orange / navy totals), heatmap and Sankey defaults, a zero line, thousands separators and font fallbacks in the hover label. Vega-Lite config gains area, rect, arc, rule and header. CSS gains `--mck-cat-tint-1/2`, `--mck-slide-title-*` (the underscore names stay as aliases for one release), token-derived phone sizes, `.sr-only`; the amber variables are gone (tokens say not for charts).
- **Office:** a flat format scheme (no shadows, gradients or bevels; drawn shapes at effect 0), the `.potx` master and layouts on the Standard Template grid with the "McKesson Proprietary and Confidential" footer, real file properties, square chart corners, Medium data labels, Excel type from the tokens with named cell styles, computed Excel headlines, and status colours plus the steps ramp on the Palette sheet.
- `python/README.md`, package metadata (readme, license, classifiers) and a Plotly floor of 5.24 (`title.subtitle`, numeric `font.weight`).
- 11 more cookbook Python blocks are marked `# verified`, so `tools/check_snippets.py` now runs 47 (line, stacked area, slope/bump, small multiples, bubble timeline, Sankey).
- Plotly gallery: phone layouts for the bar (margin from the longest label, wrapped names), line (top key under 600 px) and Sankey (taller, thinner nodes); every card has `role="img"` and an aria label. The chart-card starter draws a zero baseline, carries a hidden data table and `<noscript>` summary, and sizes plots from the aspect tokens.
- `examples/data/make_data.py` sorts stably, so regenerating the data no longer reorders tied rows.
- **Phone versions of the hero exhibits.** On screens under 560 px the guide used to scroll the 33 wide anatomy charts sideways behind a "Swipe to see the full chart" hint. The 29 that are charts are now drawn a second time in phone mode (340 px wide, taller, smaller type where needed, markers and labels re-placed, map keys under the map), embedded next to the desktop SVG and swapped in by CSS; the PDF is unchanged. Pages mark them `{{exhibit:name|phone}}`; `exhibits.ph(desktop, phone)` picks values by medium. The four slide mock-ups keep the swipe. Card and stage padding shrink on phones. The standalone HTML grows from 8.8 to about 10 MB.

### Changed
- **Categorical order is now McKesson's usage order:** blue `#005A8C`, navy `#143359`, bright blue `#009EFF`, teal `#00AF9D`, mint `#05CE90`, orange `#EF8200` last (it was the Standard Template's own sequence with teal second). The token holds exactly six; the two light tints moved to `color.categorical.fill_tints` (`mv.FILL_TINTS`), so `mv.categorical(7)` raises instead of returning a 1.3:1 tint and the Plotly colorway, Vega range, R palette, Power BI theme and Office accents all stop at six. `#009DFF` was a one-digit error for the brand azure swatch. Guidance tightens to "prefer ≤ 4".
- Slide titles are stated once everywhere as Bold 26 pt McKesson Blue `#005A8C` (ten cookbook pages, the typography doc and the rules file said 24 pt navy); Office instructions name the right accent slots (Accent 2 navy, Accent 3 bright blue; light blue and context grey via More Colors).
- The guide's code font is now bundled: Inconsolata Regular (SIL OFL, `fonts/Inconsolata/`) replaces the Windows-only `Consolas, "Cascadia Mono"` stack in `guide/guide.css`, with Consolas, Cascadia Mono and Menlo as fallbacks. On a Mac the guide used to fall back to Courier, which is wider, so two spreads overflowed their 16:9 page when built there; now Windows and Mac builds lay out identically. Code sizes went up about 10% to keep the same visual size (Inconsolata is narrower).
- `START-HERE.html` in the release bundle lists Menlo as a code-font fallback for Mac readers.
- `ROADMAP.md` gains Mac resume commands and a note on iCloud-synced folders.

## [1.1.0] - 2026-10-01

Second review round, plus packaging so the kit travels outside this repo.

### Added
- **Release bundle for SharePoint:** `python tools/make_bundle.py` writes `dist/release/McKesson-DataViz-Kit-v1.1.0.zip` with a `START-HERE.html` page for people who don't use git: the standalone and PDF guide, one-page PDFs, Office template, starter deck and workbook, Power BI theme, fonts, web themes, agent files and this changelog.
- **Portable agent skill:** `dist/skills/mck-chart/` (built by `tools/build_skill.py`, also run by `tokens/build.py`) is a self-contained Agent Skills folder: the workflow, the one-page rules, the chart chooser, principles, QA checklist, every cookbook page, theme assets and an environment check. It works in `~/.claude/skills/`, a repo's `.claude/skills/` or `.github/skills/`, and as a zip for Claude.ai custom skills. The repo's own `.github/skills/mck-chart/SKILL.md` is generated from the same template.
- **`mckviz` is installable from GitHub:** `pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"`. The Libre Franklin fonts (SIL OFL) and the map data ship inside the package.
- `mv.fmt_num(value, kind="auto" | "K" | "M" | "B" | "pct" | "plain", decimals=...)`: house number format with K/M/B, percentages, a true minus and optional explicit plus.
- `mv.suppress_small(df, n_col, min_n=10, other_label="Other")`: applies the minimum-n rule (merge small groups into "Other", or drop them) and returns the footnote to print.
- `mckviz.geo`: the TopoJSON reader, Albers USA and Equal Earth projections and map drawing that the guide's real maps use, with the us-atlas and world-atlas files built in. `docs/cookbook/maps.md` has a runnable real-states choropleth.
- `mv.__version__`; `mv.use()` warns once if the fonts can't be registered (it used to fall back to Arial silently).
- `docs/ci.md`: running `mv.lint(fig, strict=True)` in another repo's GitHub Actions.
- Chart chooser and cheat sheet as guide pages (top-bar buttons, every chart name links to its page), printed to one-page PDFs by the guide build.
- Standalone single-file guide (`dist/guide/McKesson-DataViz-Guide.html`) that works offline; kit-file links point at GitHub.
- Real US, world and zoom-in maps in the Geo-spatial section (Albers USA with Alaska and Hawaii insets, Equal Earth, county zoom with a locator).
- Two-charts-on-a-slide guidance and spread.
- **Plans and status** section: roadmap (Gantt), initiative tracker, milestone timeline, status over time, status column, process stages, best practice and build steps.
- **Progressive disclosure:** a Start-here quick path, a 19-page Quick guide PDF (`dist/guide/McKesson-DataViz-Quick-Guide.pdf`), and on screen each family's variants, build and continued pages fold behind a "More" line.
- Formats pages for the McKesson slide (the Standard Template's grid, footer and logo), flat-not-rounded design, storyline (a ghost deck of titles) and scenarios for executives.
- Office starter on the Standard Template's grid; when the internal template is present locally, the build also writes `McKesson-DataViz-Starter-Official.pptx` on it (gitignored; release bundle only).

### Changed
- **Palette from the McKesson Standard Template:** categorical blues and teals in a fixed order; green means "better" (with a symbol or word) as orange means "worse"; red/amber/green status colors for status only, each with its symbol and word; blue-to-green ordered steps for stages; McKesson Blue slide titles. `mv.lint` knows the status colors.
- **Type hierarchy:** slide title Bold, chart headline SemiBold 18 pt, big KPI numbers Bold, in the tokens and every generated theme.
- Guide review fixes: stacked bar anatomy, variants and best practice redone; semantic waterfall colors; clearer zero-baseline example; dumbbell and bubble keys; left-aligned inline table bars; dual-axis pairs read left to right; no scrollbars in print (the build checks sideways overflow too).
- The highlight accent in the agent instructions is navy, never orange.
- Formats now follows Fundamentals; Office set-up leads with a plain-English short version.
- `guide/geo_shapes.py` is now a thin re-export of `mckviz.geo`; the map files moved from `guide/geodata/` to `python/mckviz/geodata/`, and the county-subset script to `tools/make_geo_subset.py`.

### Removed
- `templates/print/` and `tools/build_print.py` (the one-pagers are guide pages now), and the one-off brand-extraction scripts.

## [1.0.0] - 2026-09-30

The guide's first complete review draft.

### Added
- **The guide:** a browsable HTML guide and 16:9 PDF from one source, modelled on consulting-grade data-viz guidelines and written for McKesson: overview, Fundamentals, nine chart families (magnitude, part-to-whole, change over time, ranking, distribution, correlation, relationships and flows, geo-spatial, single number), each with anatomy, variants, best practice and how to build it in each tool, then Formats and Toolkit. Every exhibit is drawn from the tokens and synthetic Workforce Innovation data, and every number in the text is computed.
- **Design tokens** (`tokens/tokens.json`) and a build that generates CSS, Plotly, Vega-Lite, matplotlib, ggplot2, Power BI and Office themes, a palette report and portable agent rules.
- **`mckviz`** Python package: `use()`, `highlight()`, `categorical()`, `titles()`, `source()`, `label_bars()`, `label_line_ends()`, `callout()`, `shade_period()`, `clean_axes()`, `signed()`, `text_on()`, `rgba()`, `save()`, `pl_finish()`, and `mv.lint()` for matplotlib and Plotly figures.
- **Cookbook:** 23 chart pages with spec tables, do/don't rules and code for Python, HTML, Excel and PowerPoint, Power BI and R; every `# verified` snippet runs in CI-style checks (`tools/check_snippets.py`).
- **Office starters:** `.potx` template, starter deck with native charts, chart workbook, and the set-up guide.
- **Power BI** theme validated against Microsoft's schema, with a set-up guide (highlights from a measure, minimum n in DAX).
- **HTML** chart-card starter; Python and R galleries; synthetic example datasets.
- **Agent assets:** `AGENTS.md` (read by Claude Code via `CLAUDE.md` and by Copilot), path-scoped Copilot instructions, the `mck-chart` workflow skill and a single portable rules file.
- Palette decisions from the owner review: McKesson Blue as the focus, navy accent, orange only for "worse", no amber.

[1.1.0]: https://github.com/amccown-mck/Data-Viz-Guide/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/amccown-mck/Data-Viz-Guide/releases/tag/v1.0.0
