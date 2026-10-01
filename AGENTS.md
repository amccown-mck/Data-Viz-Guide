# Agent instructions (stub; to be expanded, see ROADMAP.md step 2)

When creating any chart or visualization in this repo or for McKesson:

1. Read `docs/principles.md` and the relevant `docs/cookbook/<chart>.md` before writing code.
2. In Python, use `import mckviz as mv; mv.use()`. Get colors from `mv.colors` / `mv.highlight()`. Never hard-code hex values.
3. In HTML/JS, use `dist/web/mck-viz.css` plus `dist/web/mck-plotly-template.js` or `dist/web/vega-lite-config.json`.
4. Every chart needs:
   - an insight headline (a full sentence stating the "so what")
   - a neutral subtitle (metric, unit, scope, period)
   - direct labels instead of legends where possible
   - grey context with one blue focus (and an optional orange accent)
   - at most 6 categorical colors
   - a "Source:" line
5. Run through `docs/qa-checklist.md` before returning the result.
6. Design tokens live only in `tokens/tokens.json`. After editing them, run `python tokens/build.py`. Never edit `dist/` by hand.
7. If you are resuming unfinished work, read `ROADMAP.md` first.
