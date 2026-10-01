# Roadmap and status

Last updated: 2026-09-30. Read this first when resuming work, whether you're a person or an agent.

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
| Snippet check | `python tools/check_snippets.py` runs every `# verified` Python block in the cookbook | `tools/check_snippets.py` |

## Next steps (in priority order)

1. ~~**Finish the cookbook.**~~ Done: `distribution`, `tables` and `venn` pages added, with gallery charts and verified snippets.
2. ~~**Agent assets.**~~ Done: expanded `AGENTS.md`; `CLAUDE.md` and `.github/copilot-instructions.md` point to it; path-scoped `.github/instructions/viz-{python,web,r}.instructions.md`; the `mck-chart` workflow skill (`.github/skills/`, with a Claude Code shim in `.claude/skills/`); the portable rules file is generated from `agents/mck-viz-rules.template.md` into `dist/agents/mck-viz-rules.md` by `tokens/build.py`.
3. ~~**HTML starter.**~~ Done: `templates/html/chart-card.html` (bar + line cards, token colors via CSS variables, drawn after the font loads, top key on phones). `gallery.html` checked at 1060 px and 390 px and fixed: clipped labels (Plotly cached fallback-font widths), bold focus labels, footnote, rgba literals → `mv.rgba()`, stable div ids. Known gaps on phones: the longest bold bar label still clips slightly at 390 px, the line-end labels touch the steep demand line, and the Sankey is cramped. Port the template's mobile key swap if the gallery is used on phones.
4. ~~**Excel / PowerPoint (priority 2 audience).**~~ Done: `office/build_office.py` generates `dist/office/McKesson-DataViz.potx`, `McKesson-DataViz-Starter.pptx` (native bar highlight, line, waterfall, 100% stacked) and `McKesson-DataViz-Charts.xlsx`; set-up how-to in `docs/office-setup.md`; one-page `dist/print/cheat-sheet.pdf` and `chart-chooser.pdf` (sources in `templates/print/`, printed by `tools/build_print.py`).
5. **Power BI (priority 3).** Partly done: the theme validates against Microsoft's report-theme schema 2.157 (`tools/check_powerbi_theme.py`, which also caught and now guards against duplicate data colors), and `docs/powerbi-setup.md` covers applying the theme, the font fallback, measure-driven highlights, insight titles and minimum-n DAX. **Still needs a person with Power BI** (Desktop has no scripting interface, and the Service can't be reached from here): load the theme in Desktop, build one sample page (bar highlight with a color measure, matrix heat table, KPI cards), publish it, and view it in the Service from a machine without Libre Franklin. Confirm or correct the font table in `docs/powerbi-setup.md`, and remove its "Status" note.
6. **R (nice-to-have).** Smoke-test `dist/r/theme_mck.R` with ggplot2 and add 2–3 examples.
7. **QA automation.** Add a lint script that checks a matplotlib or Plotly figure against the rules: more than 6 colors, a missing headline or source, legend vs. direct labels, and so on.
8. **Brand confirmation.** Confirm with Brand that the full swatch values on BrandHQ match the values extracted from the PDFs, and check the derived ramps (sequential, diverging, context grey).

## Resume commands

```powershell
cd C:\Users\exs4yig\repos\data-viz-guide
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .\python[examples] kaleido python-pptx openpyxl xlsxwriter pymupdf
.\.venv\Scripts\python.exe tokens\build.py                      # regenerate dist/
.\.venv\Scripts\python.exe examples\data\make_data.py           # regenerate data
.\.venv\Scripts\python.exe examples\python\gallery_matplotlib.py
.\.venv\Scripts\python.exe examples\python\gallery_plotly.py
.\.venv\Scripts\python.exe office\build_office.py                # regenerate .pptx/.potx/.xlsx in dist/office
.\.venv\Scripts\python.exe tools\build_print.py                    # cheat sheet + chart chooser PDFs (needs Chrome or Edge)
.\.venv\Scripts\python.exe tools\check_snippets.py                # run every verified cookbook snippet (~40 s)
```

## Working notes

- The source McKinsey images and brand PDFs stay **outside** the repo, in OneDrive `Desktop\McK-Data-Viz\`. Never commit them.
- Edit colors and type only in `tokens/tokens.json`, then rebuild. Never hand-edit `dist/`.
- Examples use the People Analytics, Workforce Intelligence, and SWP lens, not plain HR reporting. They mix internal and external signals at the individual, team, firm, and sector levels.
- Platform priority: HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
