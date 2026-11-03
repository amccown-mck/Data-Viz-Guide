# Guide refresh log

The published guide (the HTML and PDF on the People Analytics SharePoint) is rebuilt in one pass, not after every change. This page holds what that pass must cover, so nothing is lost in between.

**How to use it:** when a change alters what the guide shows or says (a rule, a builder the guide names, a chart, code on a page), add a line under the right heading in the same commit: what changed, which guide page, and the commit or date. Mark a source edit done when the page is updated. The rebuild clears the log: it starts again empty, with the date of the build it follows.

**Last published build:** release 1.2.0 (2026-10-18), the most recent full guide build (`dist/guide`); the owner confirmed the SharePoint copy is that build (2026-11-03).

## Changed in the source: needs only the rebuild

- **Highlights follow the headline, with no fixed cap** (2026-11-02, `16637e8`): the wording on `fundamentals`, `magnitude`, `ranking` and `cheat-sheet` says "what the headline names (usually one or two)" instead of a cap of two.
- **`mv.bar`** (2026-11-02, `065abf5`): the Magnitude page's Python snippet builds the sorted bar in one call.

## Needs a source edit before the rebuild

- [ ] **`correlation.html`, Python platform note:** the snippet still draws the bubble scatter by hand (`ax.scatter(... s=df.headcount * K ...)`). Show `mv.bubble` instead (2026-11-03): one call, limits, key above the plot, labels clear of the bubbles.
- [ ] **`magnitude.html` and `chooser.html`, options:** a **bubble strip** (`mv.bubble_strip`, `docs/cookbook/bubble-strip.md`, 2026-11-03) when how many people each category covers matters; today the page offers only proportional bubbles for a wide range.
- [ ] **`toolkit.html`, what `mv.lint` checks:** add labels, keys and legends that sit on the data or on each other (`label-on-data`, `label-overlap`, 2026-11-03).
- [ ] **Insights panel** (2026-11-03, branch `feat/insights`): wherever the guide shows or describes the slide's "Key takeaways" card (the chart + takeaways layout), show the insights panel: numbered claims with evidence, a big number only when one derived number is the point, "What it means" for one implication.
- [ ] **Annotations** (2026-11-03, branch `feat/insights`): `formats.html`'s "Presentations: build it up" step 3 shows a benchmark and a bracket drawn by hand in the guide's figure; draw it with `mv.bracket`, and say on the page which annotation fits which job (bracket, number marker, gap, note; one or two per chart), as `references/insights.md` does.
- [ ] **`toolkit.html`, the mckviz list:** the annotation helpers (`mv.mark`, `mv.bracket`, `mv.gap`, `mv.note`) and lint's `annotations` warning.

## Worth a look at the rebuild (no change known yet)

- The guide's own bubble figures (`guide/ex_correlation.py`, `ex_change_over_time.py`, `ex_geo.py`) place their size keys by hand. Their data is fixed, so they render fine; switch them to `mv.size_key` / `mv.bubble` only if the rebuild shows a collision.

## The rebuild

1. Release the kit as the next minor version (`docs/maintaining.md`, "Release"): `VERSION`, the changelog's Unreleased block, the full build chain. `tools/build_guide.py` must report "every spread fits".
2. Review the PDF pages that changed by eye (`tools/render_pdf_pages.py` contact sheets).
3. Upload the HTML and the PDF to SharePoint **as new versions of the same files**, so the links in the agent's `instruction.txt` keep working; open both links afterwards to check.
4. Empty this log and set "Last published build".
