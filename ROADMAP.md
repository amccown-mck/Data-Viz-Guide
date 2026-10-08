# Roadmap and status

Last updated: 2026-10-08 (chart + takeaways frame for one-chart slides; LF line endings via .gitattributes). Read this first when resuming work, whether you're a person or an agent.

## Done

| Area | What exists | Where |
|---|---|---|
| Inspiration capture | Paraphrased notes on each page of the McKinsey Data Viz Guidelines (pp. 26–86 plus 4 hi-res pages). No images are committed. | `reference/inspiration-mckinsey/pages/` |
| Brand extraction | Libre Franklin typeface, plus the core, 2026, and extended palettes taken from the Social Media guide and FY26 Impact Report | `tokens/tokens.json`, `tools/*.py` |
| Design tokens | Single source of truth, including chart roles (focus, accent, context, total), categorical-6, sequential, and diverging (orange-blue, CVD-safe) | `tokens/tokens.json` |
| Token build | `python tokens/build.py` generates CSS, Plotly, Vega-Lite, mplstyle, ggplot2, Power BI theme, Office theme XML, a palette report, and swatches | `dist/` |
| Python package | `mckviz` 1.1.0: `use()`, `highlight()`, `titles()`, `source()`, `label_bars()`, `label_line_ends()`, `callout()`, `shade_period()`, `pl_finish()`, `fmt_num()`, `suppress_small()`, `lint()`, and `mckviz.geo` (real maps). Installable from a tag: `pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"`; fonts and map data are package data | `python/mckviz/` |
| Fonts | Static Libre Franklin TTFs (SIL OFL); synced into `python/mckviz/fonts/` by `tokens/build.py`. Inconsolata Regular (SIL OFL) for code in the guide, so Windows and Mac builds lay out the same | `fonts/LibreFranklin/`, `fonts/Inconsolata/` |
| Versioning | One `VERSION` file read by `pyproject.toml`, the guide cover, the agent rules, the skill and the bundle; `CHANGELOG.md` (Keep a Changelog). The owner tags `v<version>` | `VERSION`, `CHANGELOG.md` |
| Release bundle | `tools/make_bundle.py` → `dist/release/McKesson-DataViz-Kit-v<version>.zip` (not committed) with `START-HERE.html` for non-technical readers: guide (standalone + PDF), one-pagers, Office, Power BI, fonts, web themes, `mckviz` wheel, agent rules and skill | `tools/make_bundle.py` |
| Portable agent skill | `dist/skills/mck-chart/`: SKILL.md, rules, chooser, principles, QA, all cookbook pages, theme assets, `scripts/check_env.py`; works in `~/.claude/skills/`, `.claude/skills/`, `.github/skills/`, and zipped for Claude.ai. Generated with the in-repo `.github/skills/mck-chart/SKILL.md` from one template | `agents/skill/`, `tools/build_skill.py` |
| CI recipe | Running `mv.lint(fig, strict=True)` in another repo's GitHub Actions | `docs/ci.md` |
| Example data | 12 synthetic workforce / SWP datasets, including individual-level compa-ratios | `examples/data/` (`make_data.py`) |
| Galleries | 11 matplotlib PNGs that were visually QA'd, plus a Plotly HTML gallery (checked at desktop and phone widths) | `examples/python/`, `examples/output/` |
| Core docs | principles, color, typography-and-layout, choosing-a-chart, formats, qa-checklist | `docs/` |
| Cookbook | 23 chart pages (including distribution, tables, venn) plus `_template.md` | `docs/cookbook/` |
| Agent assets | `AGENTS.md`, `CLAUDE.md`, Copilot instructions, path-scoped instructions, `mck-chart` skill, portable rules | `AGENTS.md`, `.github/`, `.claude/skills/`, `dist/agents/` |
| Office starters | `.potx` template, starter deck (4 native charts), chart workbook (palette, 4 charts, heat table), set-up guide; checked by rendering in PowerPoint/Excel | `dist/office/`, `office/build_office.py`, `docs/office-setup.md` |
| Print sheets | Cheat sheet and chart chooser: pages of the guide (top-bar buttons, linked to every chart page), printed to PDF by the guide build | `guide/pages/chooser.html`, `guide/pages/cheat-sheet.html`, `dist/print/` |
| HTML starter | Self-contained chart-card page using `dist/web/` | `templates/html/chart-card.html` |
| Snippet check | `python tools/check_snippets.py` runs every `# verified` Python block in the cookbook; `--lang r` runs every R block | `tools/check_snippets.py` |
| Chart lint | `mv.lint(fig)` for matplotlib/Plotly, gallery runner, pytest suite | `python/mckviz/lint.py`, `tools/lint_charts.py`, `python/tests/` |
| R examples | ggplot2 gallery (bar highlight, line with end labels, diverging heatmap) using the generated theme | `examples/r/`, `examples/output/r-*.png` |
| Guide | Browsable HTML guide + 16:9 PDF from one source (103 spreads, 348 exhibits), plus a standalone single-file HTML that works offline, modelled on the McKinsey spreads: overview, Fundamentals, nine chart families (anatomy, variants, best practice, build it), Formats, Toolkit. Exhibits drawn from tokens and data; every quoted number computed | `guide/`, `tools/build_guide.py`, `dist/guide/` |

## Current focus: the guide itself (decided 2026-09-30)

The original ask was a McKesson data-viz guideline as thorough as the McKinsey guide, usable by consultants, developers and coding agents. By v0.1 the toolkit was strong but the guide itself was thin, so the guide now comes first. Agreed with the owner: **pilot first** (done), **local files** (HTML + PDF in the repo; sharing decided later), and a look that **balances McKinsey-level polish with the McKesson brand**.

Status: **done** (2026-09-30). The owner approved the pilot ("exactly the right direction"); all sections are written: Fundamentals, Magnitude, Part-to-whole, Change over time, Ranking, Distribution, Correlation, Relationships and flows, Geo-spatial, Single number, Formats, Toolkit. Brand-usage feedback from the same review is applied kit-wide (see Working notes).

Second review (2026-10-01), applied: standalone single-file guide to send around; chart chooser and cheat sheet rebuilt as guide pages (top-bar buttons, every chart name links to its page; one-page PDFs printed from them, `templates/print/` and `tools/build_print.py` retired); type hierarchy (slide title Bold 24 pt, chart headline SemiBold 18 pt, KPI numbers Bold) in tokens and every generator, plus a two-charts-on-a-slide spread; real US, world and zoom-in maps (now `mckviz.geo` with data in `python/mckviz/geodata/`; `guide/geo_shapes.py` is a shim); stacked bar anatomy, variants and best practice redone (story segment on the baseline, names over the top bar, base counts); semantic waterfall colors (favorable green, unfavorable orange); clearer zero-baseline example; dumbbell key; left-aligned inline table bars; dual-axis pairs read left to right; bubble-timeline key no longer clips.

Third round (2026-10-01, v1.1.0), from a reader review (a consultant and a developer read the whole guide) and the McKesson Standard Template the owner shared (kept locally in `reference/mckesson-branding/`, gitignored):
- **Brand template:** palette from the template's infographic slides (categorical blues and teals; green = better; red/amber/green for status only, each with symbol and word; blue-to-green steps); slide titles Bold McKesson Blue 24-28 pt; flat, not rounded; Office starter on the template's grid, plus a locally built `McKesson-DataViz-Starter-Official.pptx` on the template (release bundle only).
- **New sections and pages:** Plans and status (roadmap, tracker, milestones, status over time, process stages); the McKesson slide; flat not rounded; storyline (ghost deck); scenarios for executives.
- **Progressive disclosure:** Start-here quick path, 19-page Quick guide PDF, Formats right after Fundamentals, variants/build/continued pages fold on screen.
- **Distribution:** `VERSION` + `CHANGELOG.md`; `mckviz` installable from a tag with fonts and maps inside; `mv.fmt_num`, `mv.suppress_small`; release zip (`tools/make_bundle.py`) with START-HERE for SharePoint; portable agent skill (`dist/skills/mck-chart/`, zip for Claude.ai).
- **Fixes:** no local paths in the PDF or standalone file (GitHub links), no print scrollbars (build checks sideways overflow), lint safe on any console, runnable page-21 code, contents with page numbers.

Open for the owner: publish the release zip to SharePoint; Power BI checks (on hold); load the portable skill in Claude.ai (`dist/skills/mck-chart.zip`) and Copilot once to confirm. (`v1.1.0` is tagged.)

## Toolkit audit and hygiene (2026-10-04)

Five parallel reviews (Office, Python, R, web, agent assets) found the generated core consistent with the tokens but the hand-written layers drifted and coverage behind the guide. **Tranche A (done, same day):** categorical order settled and propagated (see Working notes); slide title stated once; Office accent-slot text corrected; consistency test; lint false positives and Plotly gaps; 11 more verified snippets; packaging and README; portable skill with data and zip; Plotly template, Vega and CSS fixes; gallery phone gaps and aria; chart-card baseline and hidden table; flat Office theme, `.potx` on the grid with footer, Excel type and named styles, status swatches. **Needs a visual check on Windows:** the rebuilt `.potx`/`.pptx` (Slide Master positions, footer, no shadows, square chart corners) and the `.xlsx` (Cell Styles, Palette sheet).

**Tranche B, coverage (done 2026-10-05):** `mckviz.charts` with the guide's builders (waterfall, hstack, dumbbell, rank_slope, heat, KPI card/row/ring, status/tracker/roadmap, multiples), used by the cookbook; `docs/cookbook/plans-status.md`; the starter deck grew from 6 to 14 slides (KPI, roadmap, tracker, two charts, column, dumbbell, slope, bubble) with 7 mirrored sheets; web components (`.mck-kpi`, `.mck-status`, `.mck-grid`, heat and tracker tables), `mck-viz.js`, the offline chart card with vendored Plotly, and web recipes for waterfall, stacked bar, heatmap, KPI and plans/status. **Owner to check on Windows:** slides 8 (milestones, Today line, labels on the gridlines), 9 (row heights), 10 (names, stems), glyphs ✓ ✕ ▲; Excel Roadmap Today line and KPI bar. Slides 11–14 were checked on Windows on 2026-10-08 and moved to the new **chart + takeaways** frame (two-thirds chart, takeaways in the right third; see `docs/typography-and-layout.md` §3), which also fixed the slope-label overlap, the dumbbell name wrapping and the bubble axis title. **Open:** the guide has no spread for the two one-chart widths yet (the Formats section's McKesson slide would be the place). **Assumption to confirm:** the roadmap's slip bar assumes the paused SWP refresh slips 3 months like the Workday integration (the data has no forecast end). **Still open from the audit:** web recipes for the remaining families; a Standard-Template build of the new slides (needs the internal template locally); `.crtx` chart templates (python-pptx cannot write them). **Tranche C, R (needs a machine with R):** the 22 cookbook R blocks use `mck_font()`/`mck_wrap()` and token colours, drop legends and round line ends; R helpers (`mck_shade`, `mck_signed`, `mck_text_on`, binned diverging scale, sizes that follow `base_size`); re-render the gallery; make `check_snippets --lang r` render through `ragg`. **MCP server:** not yet; the rules are now single-sourced and tested, so it would be a thin wrapper over `tokens.json` plus `mv.lint` when a tool beyond Claude Code and Copilot needs it.

Open, for the owner:
- ~~Phone view~~ Done 2026-10-04: the 29 hero exhibits (anatomies, the fundamentals pair, the scenarios chart) are rendered a second time in phone mode (`exhibits.PHONE`, 340 px wide, taller, markers and labels re-placed with `ph(desktop, phone)`), marked `{{exhibit:name|phone}}` in the pages; `guide.css` shows that copy under 560 px. Only the four slide mock-ups (ghost deck, McKesson slide, two charts, roadmap) still scroll sideways with the swipe hint (`|min`). The standalone file grew to about 10 MB.
- Power BI: the theme now names `Libre Franklin SemiBold` for visual titles and `Libre Franklin Bold` for card callouts (Segoe UI fallbacks). Check both render as intended in Desktop and the Service.
- Excel's Filled Map offering Robinson for world maps is stated in the Geo build page but not verified in Excel.

Distribution and agents (v1.1.0, 2026-10-01), done: `mckviz` installs from a tag with fonts and maps inside; `mv.fmt_num`, `mv.suppress_small`; one `VERSION` plus `CHANGELOG.md`; the release zip for SharePoint; the portable `mck-chart` skill; the CI recipe. Open, for the owner:
- Tag the release (`git tag v1.1.0 && git push --tags`) so the `pip install ...@v1.1.0` lines in the docs resolve, and upload the zip from `python tools/make_bundle.py` to SharePoint. Run the full guide build first so the cover and the standalone file say 1.1.0.
- If the repo is private, `pip install` from GitHub needs a token (see `docs/ci.md`); the wheel in the bundle is the offline fallback.
- **Possible future: an MCP server** exposing the kit to any MCP-capable assistant (tools such as `lint_chart`, `get_color_roles`, `choose_chart(question_type)`, `get_cookbook(page)`), so agents get the current rules without copying files. Worth it only if many tools outside Claude Code and Copilot need the kit; the portable skill covers those two today.

How to extend: add `guide/ex_<section>.py` (exhibits register on import) and `guide/pages/<section>.html` (spreads with `{{exhibit:…}}`, `{{text:…}}`, `{{folio}}`), add the page to `PAGES` in `tools/build_guide.py`, build, then review contact sheets and the PDF pages by eye. For a hero exhibit, mark it `{{exhibit:name|phone}}` and check it in phone mode too (render with `exhibits.PHONE = True`; branch on `ph(desktop, phone)` where markers or labels collide). Testing at phone width: headless Chrome will not open a window under 500 px, so load the page in a 390 px `<iframe>` and screenshot that.

## Toolkit steps (v0.1 plan, in priority order)

1. ~~**Finish the cookbook.**~~ Done: `distribution`, `tables` and `venn` pages added, with gallery charts and verified snippets.
2. ~~**Agent assets.**~~ Done: expanded `AGENTS.md`; `CLAUDE.md` and `.github/copilot-instructions.md` point to it; path-scoped `.github/instructions/viz-{python,web,r}.instructions.md`; the `mck-chart` workflow skill (`.github/skills/`, with a Claude Code shim in `.claude/skills/`); the portable rules file is generated from `agents/mck-viz-rules.template.md` into `dist/agents/mck-viz-rules.md` by `tokens/build.py`.
3. ~~**HTML starter.**~~ Done: `templates/html/chart-card.html` (bar + line cards, token colors via CSS variables, drawn after the font loads, top key on phones). `gallery.html` checked at 1060 px and 390 px and fixed: clipped labels (Plotly cached fallback-font widths), bold focus labels, footnote, rgba literals → `mv.rgba()`, stable div ids. Known gaps on phones: the longest bold bar label still clips slightly at 390 px, the line-end labels touch the steep demand line, and the Sankey is cramped. Port the template's mobile key swap if the gallery is used on phones.
4. ~~**Excel / PowerPoint (priority 2 audience).**~~ Done: `office/build_office.py` generates `dist/office/McKesson-DataViz.potx`, `McKesson-DataViz-Starter.pptx` (native bar highlight, line, waterfall, 100% stacked) and `McKesson-DataViz-Charts.xlsx`; set-up how-to in `docs/office-setup.md`; one-page `dist/print/cheat-sheet.pdf` and `chart-chooser.pdf` (now guide pages, printed by `tools/build_guide.py`).
5. **Power BI (priority 3).** Partly done: the theme validates against Microsoft's report-theme schema 2.157 (`tools/check_powerbi_theme.py`, which also caught and now guards against duplicate data colors), and `docs/powerbi-setup.md` covers applying the theme, the font fallback, measure-driven highlights, insight titles and minimum-n DAX. **Still needs a person with Power BI** (Desktop has no scripting interface, and the Service can't be reached from here): load the theme in Desktop, build one sample page (bar highlight with a color measure, matrix heat table, KPI cards), publish it, and view it in the Service from a machine without Libre Franklin. Confirm or correct the font table in `docs/powerbi-setup.md`, and remove its "Status" note.
6. ~~**R (nice-to-have).**~~ Done: smoke-tested with R 4.5.1 / ggplot2 4.0.3, and all 23 cookbook R blocks now run (`tools/check_snippets.py --lang r`; six used an undefined `df`/`events` and now build synthetic data). `theme_mck.R` fixes: gridlines moved to the parent element so `panel.grid = element_blank()` works; new `mck_font()` (by-name matching picked the italic TTF for regular text) and `mck_wrap()`. Three examples in `examples/r/gallery_ggplot2.R` render `examples/output/r-*.png`.
7. ~~**QA automation.**~~ Done: `mv.lint(fig)` (`python/mckviz/lint.py`) checks matplotlib and Plotly figures for missing headline/subtitle/source, label-like headlines, > 6 colors (a ramp counts once), off-palette colors, red–green, truncated bars (waterfall breaks warn), labels plus value axis, legends, dual axes, pies > 5, rotated and tiny text, 3D. `tools/lint_charts.py` lints the whole gallery (0 errors); `python -m pytest python/tests` covers each rule. Not covered (needs judgment): whether the headline is true, chart choice, overlaps.
8. **Brand confirmation.** Confirm with Brand that the full swatch values on BrandHQ match the values extracted from the PDFs, and check the derived ramps (sequential, diverging, context grey).

## Resume commands

```powershell
cd C:\Users\exs4yig\repos\data-viz-guide
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .\python[examples] kaleido python-pptx openpyxl xlsxwriter pymupdf jsonschema pytest
.\.venv\Scripts\python.exe tokens\build.py                      # regenerate dist/
.\.venv\Scripts\python.exe examples\data\make_data.py           # regenerate data
.\.venv\Scripts\python.exe examples\python\gallery_matplotlib.py
.\.venv\Scripts\python.exe examples\python\gallery_plotly.py
.\.venv\Scripts\python.exe office\build_office.py                # regenerate .pptx/.potx/.xlsx in dist/office
.\.venv\Scripts\python.exe tools\build_guide.py                    # the guide: pages, standalone .html, PDF, one-pagers; checks every spread fits 16:9
.\.venv\Scripts\python.exe tools\check_snippets.py                # run every verified cookbook snippet (~40 s)
.\.venv\Scripts\python.exe tools\check_snippets.py --lang r       # run every cookbook R block (needs R + packages below)
.\.venv\Scripts\python.exe tools\check_powerbi_theme.py           # validate the Power BI theme against Microsoft's schema
.\.venv\Scripts\python.exe tools\lint_charts.py                   # lint every gallery chart (mv.lint)
.\.venv\Scripts\python.exe -m pytest python\tests                 # mckviz unit tests
.\.venv\Scripts\python.exe tools\make_bundle.py                   # release zip for SharePoint -> dist\release\ (after the builds)
& "C:\Program Files\R\R-4.5.1\bin\Rscript.exe" examples\r\gallery_ggplot2.R   # R gallery -> examples/output/r-*.png
# R packages: ggplot2 dplyr readr tidyr stringr scales ragg systemfonts gt sf maps mapproj ggalluvial treemapify packcircles
```

On a Mac (the owner also works from one), the same steps with `uv` (the system Python is 3.9; `mckviz` needs 3.10+):

```bash
cd ~/repos/Data-Viz-Guide
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e "./python[examples]" kaleido python-pptx openpyxl xlsxwriter pymupdf jsonschema pytest
chflags -R nohidden .venv        # see Working notes: iCloud marks dot-folders hidden and Python then skips the venv's .pth files
.venv/bin/python tokens/build.py
.venv/bin/python tools/build_guide.py      # needs Google Chrome in /Applications
.venv/bin/python tools/check_snippets.py
.venv/bin/python -m pytest python/tests
```

## Working notes

- The source McKinsey images and brand PDFs stay **outside** the repo, in OneDrive `Desktop\McK-Data-Viz\`: `gif-frames\unique\` (61 stills), `hi-res-slides\` (4 spreads), `_work\mck-pages\` (page notes), `McK-Brand-reference\` (brand PDFs), `rebrand-site-images\` (rebrand case-study images). Never commit them.
- The transcripts of the sessions that built v0.1 were lost; this file and `git log` are the record.
- **Mac gotcha (2026-10-04):** if the repo sits in an iCloud-synced folder (Desktop or Documents), macOS keeps re-applying the `hidden` flag to dot-folders such as `.venv`, and Python 3.12+ silently skips hidden `.pth` files, so `import mckviz` fails until `chflags -R nohidden .venv` is run again. iCloud also leaves `name 2.ext` duplicates behind. Keep the clone outside iCloud (for example `~/repos/`), or re-run `chflags` before building.
- Edit colors and type only in `tokens/tokens.json`, then rebuild. Never hand-edit `dist/`.
- **How McKesson actually uses color (owner, 2026-09-30):** `#005A8C` is the primary and used all the time; navy `#143359` and light blue `#66C4FF` are common. Orange `#EF8200` is almost never used unless it carries meaning (executives read it as a warning), so it is `semantic.negative` only: below target, shrinking, a shortfall, the low end of the diverging scale. The highlight accent is navy. Amber `#FFB502` is never used internally. **Categorical order, settled 2026-10-04** after the palette moved to the Standard Template's colors on 2026-10-01: blue `#005A8C`, navy `#143359`, bright blue `#009EFF` (the brand azure swatch; the template extraction had `#009DFF`, a one-digit error), teal `#00AF9D`, mint `#05CE90`, orange last. Prefer ≤ 4. The earlier note (blue, navy, light blue, teal, deep teal) described the pre-template palette and is superseded.
- Examples use the Workforce Innovation lens (workforce analytics, intelligence and planning), not plain HR reporting. The team is called "Workforce Innovation" in audience and team wording. They mix internal and external signals at the individual, team, firm, and sector levels.
- Platform priority: HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
