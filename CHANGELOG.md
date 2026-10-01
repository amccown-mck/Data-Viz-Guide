# Changelog

All notable changes to the McKesson data-visualization kit (the guide, the themes, the `mckviz` package and the agent assets). The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/): a major version changes a rule or breaks code that uses `mckviz`, a minor version adds things, a patch fixes them.

The version lives in one place, the `VERSION` file at the repo root. `tokens/build.py` copies it into the Python package, and the guide cover, the agent rules, the portable skill and the release bundle read it from there. Releases are tagged `v<version>` (for example `v1.1.0`); `pip install` and the release bundle refer to those tags.

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

### Changed
- **Palette from the McKesson Standard Template:** categorical blues and teals in a fixed order; green means "better" (with a symbol or word) as orange means "worse"; red/amber/green status colors for status only, each with its symbol and word; blue-to-green ordered steps for stages; McKesson Blue slide titles. `mv.lint` knows the status colors.
- **Type hierarchy:** slide title Bold, chart headline SemiBold 18 pt, big KPI numbers Bold, in the tokens and every generated theme.
- Guide review fixes: stacked bar anatomy, variants and best practice redone; semantic waterfall colors; clearer zero-baseline example; dumbbell and bubble keys; left-aligned inline table bars; dual-axis pairs read left to right; no scrollbars in print (the build checks sideways overflow too).
- The highlight accent in the agent instructions is navy, never orange.
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
