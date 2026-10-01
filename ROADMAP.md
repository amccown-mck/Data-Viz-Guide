# Roadmap and status

Last updated: 2026-09-30 (guide pilot). Read this first when resuming work, whether you're a person or an agent.

## Done

| Area | What exists | Where |
|---|---|---|
| Inspiration capture | Paraphrased notes on each page of the McKinsey Data Viz Guidelines (pp. 26–86 plus 4 hi-res pages). No images are committed. | `reference/inspiration-mckinsey/pages/` |
| Brand extraction | Libre Franklin typeface, plus the core, 2026, and extended palettes taken from the Social Media guide and FY26 Impact Report | `tokens/tokens.json`, `tools/*.py` |
| Design tokens | Single source of truth, including chart roles (focus, accent, context, total), categorical-6, sequential, and diverging (orange-blue, CVD-safe) | `tokens/tokens.json` |
| Token build | `python tokens/build.py` generates CSS, Plotly, Vega-Lite, mplstyle, ggplot2, Power BI theme, Office theme XML, a palette report, and swatches | `dist/` |
| Python package | `mckviz`: `use()`, `highlight()`, `titles()`, `source()`, `label_bars()`, `label_line_ends()`, `callout()`, `shade_period()`, `pl_finish()` | `python/mckviz/` |
| Fonts | Static Libre Franklin TTFs (SIL OFL) | `fonts/LibreFranklin/` |
| Example data | 12 synthetic workforce / SWP datasets, including individual-level compa-ratios | `examples/data/` (`make_data.py`) |
| Galleries | 11 matplotlib PNGs that were visually QA'd, plus a Plotly HTML gallery (checked at desktop and phone widths) | `examples/python/`, `examples/output/` |
| Core docs | principles, color, typography-and-layout, choosing-a-chart, formats, qa-checklist | `docs/` |
| Cookbook | 23 chart pages (including distribution, tables, venn) plus `_template.md` | `docs/cookbook/` |
| Agent assets | `AGENTS.md`, `CLAUDE.md`, Copilot instructions, path-scoped instructions, `mck-chart` skill, portable rules | `AGENTS.md`, `.github/`, `.claude/skills/`, `dist/agents/` |
| Office starters | `.potx` template, starter deck (4 native charts), chart workbook (palette, 4 charts, heat table), set-up guide; checked by rendering in PowerPoint/Excel | `dist/office/`, `office/build_office.py`, `docs/office-setup.md` |
| Print sheets | One-page consultant cheat sheet and chart chooser (PDF), colors read from tokens | `dist/print/`, `templates/print/`, `tools/build_print.py` |
| HTML starter | Self-contained chart-card page using `dist/web/` | `templates/html/chart-card.html` |
| Snippet check | `python tools/check_snippets.py` runs every `# verified` Python block in the cookbook; `--lang r` runs every R block | `tools/check_snippets.py` |
| Chart lint | `mv.lint(fig)` for matplotlib/Plotly, gallery runner, pytest suite | `python/mckviz/lint.py`, `tools/lint_charts.py`, `python/tests/` |
| R examples | ggplot2 gallery (bar highlight, line with end labels, diverging heatmap) using the generated theme | `examples/r/`, `examples/output/r-*.png` |
| Guide | Browsable HTML guide + 16:9 PDF from one source (95 spreads, 323 exhibits), modelled on the McKinsey spreads: overview, Fundamentals, nine chart families (anatomy, variants, best practice, build it), Formats, Toolkit. Exhibits drawn from tokens and data; every quoted number computed | `guide/`, `tools/build_guide.py`, `dist/guide/` |

## Current focus: the guide itself (decided 2026-09-30)

The original ask was a McKesson data-viz guideline as thorough as the McKinsey guide, usable by consultants, developers and coding agents. By v0.1 the toolkit was strong but the guide itself was thin, so the guide now comes first. Agreed with the owner: **pilot first** (done), **local files** (HTML + PDF in the repo; sharing decided later), and a look that **balances McKinsey-level polish with the McKesson brand**.

Status: **done** (2026-09-30). The owner approved the pilot ("exactly the right direction"); all sections are written: Fundamentals, Magnitude, Part-to-whole, Change over time, Ranking, Distribution, Correlation, Relationships and flows, Geo-spatial, Single number, Formats, Toolkit. Brand-usage feedback from the same review is applied kit-wide (see Working notes).

Open, for the owner:
- The guide's chart cards use a lighter headline (Semibold, 19 px, about 1.4× the subtitle) than the tokens (Bold, 22 px). If the owner prefers it, change `typography.roles.headline` so every tool output follows, then rebuild everything.
- Phone view: wide exhibits scroll sideways ("Swipe to see the full chart") rather than shrink. Phone-specific exhibits would help if the guide is read on phones a lot.
- Maps use an equal-area US tile grid because no geometry library is installed; real state shapes need geopandas or Plotly with geometry.

How to extend: add `guide/ex_<section>.py` (exhibits register on import) and `guide/pages/<section>.html` (spreads with `{{exhibit:…}}`, `{{text:…}}`, `{{folio}}`), add the page to `PAGES` in `tools/build_guide.py`, build, then review contact sheets and the PDF pages by eye.

## Toolkit steps (v0.1 plan, in priority order)

1. ~~**Finish the cookbook.**~~ Done: `distribution`, `tables` and `venn` pages added, with gallery charts and verified snippets.
2. ~~**Agent assets.**~~ Done: expanded `AGENTS.md`; `CLAUDE.md` and `.github/copilot-instructions.md` point to it; path-scoped `.github/instructions/viz-{python,web,r}.instructions.md`; the `mck-chart` workflow skill (`.github/skills/`, with a Claude Code shim in `.claude/skills/`); the portable rules file is generated from `agents/mck-viz-rules.template.md` into `dist/agents/mck-viz-rules.md` by `tokens/build.py`.
3. ~~**HTML starter.**~~ Done: `templates/html/chart-card.html` (bar + line cards, token colors via CSS variables, drawn after the font loads, top key on phones). `gallery.html` checked at 1060 px and 390 px and fixed: clipped labels (Plotly cached fallback-font widths), bold focus labels, footnote, rgba literals → `mv.rgba()`, stable div ids. Known gaps on phones: the longest bold bar label still clips slightly at 390 px, the line-end labels touch the steep demand line, and the Sankey is cramped. Port the template's mobile key swap if the gallery is used on phones.
4. ~~**Excel / PowerPoint (priority 2 audience).**~~ Done: `office/build_office.py` generates `dist/office/McKesson-DataViz.potx`, `McKesson-DataViz-Starter.pptx` (native bar highlight, line, waterfall, 100% stacked) and `McKesson-DataViz-Charts.xlsx`; set-up how-to in `docs/office-setup.md`; one-page `dist/print/cheat-sheet.pdf` and `chart-chooser.pdf` (sources in `templates/print/`, printed by `tools/build_print.py`).
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
.\.venv\Scripts\python.exe tools\build_print.py                    # cheat sheet + chart chooser PDFs (needs Chrome or Edge)
.\.venv\Scripts\python.exe tools\build_guide.py                    # the guide: dist/guide/*.html + PDF; checks every spread fits 16:9
.\.venv\Scripts\python.exe tools\check_snippets.py                # run every verified cookbook snippet (~40 s)
.\.venv\Scripts\python.exe tools\check_snippets.py --lang r       # run every cookbook R block (needs R + packages below)
.\.venv\Scripts\python.exe tools\check_powerbi_theme.py           # validate the Power BI theme against Microsoft's schema
.\.venv\Scripts\python.exe tools\lint_charts.py                   # lint every gallery chart (mv.lint)
.\.venv\Scripts\python.exe -m pytest python\tests                 # mckviz unit tests
& "C:\Program Files\R\R-4.5.1\bin\Rscript.exe" examples\r\gallery_ggplot2.R   # R gallery -> examples/output/r-*.png
# R packages: ggplot2 dplyr readr tidyr stringr scales ragg systemfonts gt sf maps mapproj ggalluvial treemapify packcircles
```

## Working notes

- The source McKinsey images and brand PDFs stay **outside** the repo, in OneDrive `Desktop\McK-Data-Viz\`: `gif-frames\unique\` (61 stills), `hi-res-slides\` (4 spreads), `_work\mck-pages\` (page notes), `McK-Brand-reference\` (brand PDFs), `rebrand-site-images\` (rebrand case-study images). Never commit them.
- The transcripts of the sessions that built v0.1 were lost; this file and `git log` are the record.
- Edit colors and type only in `tokens/tokens.json`, then rebuild. Never hand-edit `dist/`.
- **How McKesson actually uses color (owner, 2026-09-30):** `#005A8C` is the primary and used all the time; navy `#143359` and light blue `#66C4FF` are common. Orange `#EF8200` is almost never used unless it carries meaning (executives read it as a warning), so it is `semantic.negative` only: below target, shrinking, a shortfall, the low end of the diverging scale. The highlight accent is navy. Amber `#FFB502` is never used internally. Categorical order: blue, navy, light blue, teal, deep teal, orange (last resort). Deep teals are common.
- Examples use the Workforce Innovation lens (workforce analytics, intelligence and planning), not plain HR reporting. The team is called "Workforce Innovation" in audience and team wording. They mix internal and external signals at the individual, team, firm, and sector levels.
- Platform priority: HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
