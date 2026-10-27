# Maintaining the kit

How to rebuild, check, release and extend the Data Viz Starter Kit, and notes that save time. Moved here from `ROADMAP.md` on 2026-10-27; the rules for agents are in [`AGENTS.md`](../AGENTS.md).

## Rebuild and check

```powershell
cd C:\Users\exs4yig\AgentsToolkitProjects\Data-Viz-Guide
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
.\.venv\Scripts\python.exe tools\make_bundle.py                   # release zip for a GitHub Release -> dist\release\ (after the builds)
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

## Release

Bump `VERSION`, move the changelog's Unreleased block to a dated entry, move the install lines and the bundle name to the new tag, run the full build chain (`tokens/build.py`, the galleries, `office/build_office.py`, `tools/build_guide.py`, `tools/build_skill.py --zip`, the checks, `tools/make_bundle.py`), commit "Release x.y.z", push, tag `vx.y.z`, `gh release create` with the assets, then link the assets from the demo page.

## Extend the guide

How to extend: add `guide/ex_<section>.py` (exhibits register on import) and `guide/pages/<section>.html` (spreads with `{{exhibit:…}}`, `{{text:…}}`, `{{folio}}`), add the page to `PAGES` in `tools/build_guide.py`, build, then review contact sheets and the PDF pages by eye. For a hero exhibit, mark it `{{exhibit:name|phone}}` and check it in phone mode too (render with `exhibits.PHONE = True`; branch on `ph(desktop, phone)` where markers or labels collide). Testing at phone width: headless Chrome will not open a window under 500 px, so load the page in a 390 px `<iframe>` and screenshot that.

## Working notes


- The source McKinsey images and brand PDFs stay **outside** the repo, in OneDrive `Desktop\McK-Data-Viz\`: `gif-frames\unique\` (61 stills), `hi-res-slides\` (4 spreads), `_work\mck-pages\` (page notes), `McK-Brand-reference\` (brand PDFs), `rebrand-site-images\` (rebrand case-study images). Never commit them.
- The transcripts of the sessions that built v0.1 were lost; this file and `git log` are the record.
- **Mac gotcha (2026-10-04):** if the repo sits in an iCloud-synced folder (Desktop or Documents), macOS keeps re-applying the `hidden` flag to dot-folders such as `.venv`, and Python 3.12+ silently skips hidden `.pth` files, so `import mckviz` fails until `chflags -R nohidden .venv` is run again. iCloud also leaves `name 2.ext` duplicates behind. Keep the clone outside iCloud (for example `~/repos/`), or re-run `chflags` before building.
- Edit colors and type only in `tokens/tokens.json`, then rebuild. Never hand-edit `dist/`.
- **How McKesson actually uses color (owner, 2026-09-30):** `#005A8C` is the primary and used all the time; navy `#143359` and light blue `#66C4FF` are common. Orange `#EF8200` is almost never used unless it carries meaning (executives read it as a warning), so it is `semantic.negative` only: below target, shrinking, a shortfall, the low end of the diverging scale. The highlight accent is navy. Amber `#FFB502` is never used internally. **Categorical order, settled 2026-10-04** after the palette moved to the Standard Template's colors on 2026-10-01: blue `#005A8C`, navy `#143359`, bright blue `#009EFF` (the brand azure swatch; the template extraction had `#009DFF`, a one-digit error), teal `#00AF9D`, mint `#05CE90`, orange last. Prefer ≤ 4. The earlier note (blue, navy, light blue, teal, deep teal) described the pre-template palette and is superseded.
- Examples use the Workforce Innovation lens (workforce analytics, intelligence and planning), not plain HR reporting. The team is called "Workforce Innovation" in audience and team wording. They mix internal and external signals at the individual, team, firm, and sector levels.
- Platform priority: HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
