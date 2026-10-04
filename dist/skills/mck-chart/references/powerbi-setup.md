# Set up Power BI

Dashboards are exploratory, but they follow the same visual rules as slides: grey context, one blue focus, insight titles, minimum group sizes. The theme handles the defaults. Measures and conditional formatting handle the highlight logic, because a theme can't know which bar the headline is about.

## 1. Apply the theme
1. Download [`dist/powerbi/mckesson-dataviz-theme.json`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/powerbi/mckesson-dataviz-theme.json).
2. In Power BI Desktop: **View › Themes › Browse for themes**, pick the file, and confirm.
3. To reuse it, open the **Themes** gallery and use **Save current theme**, or keep the JSON on a shared drive. Org admins can publish it as an **organizational theme** so it appears in everyone's gallery.

### What the theme sets
| Setting | Value | Why |
|---|---|---|
| Data colors 1–6 | `#005A8C` `#143359` `#009EFF` `#00AF9D` `#05CE90` `#EF8200` | The categorical palette in its fixed order: blue, navy, bright blue, teal, mint, then orange as a last resort. Prefer ≤ 5 series. Use more than 6 only for exploration; for a published page, group the tail into "Other". |
| Data colors 7–10 | Light blue and teal tints (`#B6E2FA` `#66CFC4` `#009EFF` `#B3E7E2`) | Only so 7+ series don't repeat a color. Every color is unique. |
| Good / neutral / bad | Green `#00AF68` / grey `#B4B0A5` / orange `#EF8200` | KPI and conditional-formatting defaults. Orange means worse. Never red–green. |
| Min / center / max | `#E6F3FB` / `#EFEDE7` / `#143359` | Default gradient for heat tables and maps. |
| Titles | Libre Franklin, 14 pt, bold, navy, left-aligned; subtitle 11 pt grey | Question or insight titles, top-left like every other chart. |
| Axes and gridlines | Labels `#737373` 9 pt, gridlines `#E6E4DE`, axis titles off | Units go in the subtitle. |
| Legend | Top-left, no title | Turn it off when data labels can carry the series names. |
| Visual chrome | White visual backgrounds, no borders or shadows, Light Sand `#EFEDE7` page | Cards read as panels without boxes. |

Run `python tools/check_powerbi_theme.py` after any token change. It validates the file against Microsoft's newest [report-theme JSON schema](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema) and checks the house rules: unique data colors, categorical order and font stack.

## 2. Fonts: what people will actually see
The theme asks for `Libre Franklin, Segoe UI, wf_segoe-ui_normal, helvetica, arial, sans-serif`. Libre Franklin isn't one of the fonts Power BI ships, so what renders depends on where the report is opened:

| Where | What renders |
|---|---|
| Power BI Desktop, font installed (see [office-setup.md](office-setup.md#1-install-the-fonts)) | Libre Franklin |
| Power BI Desktop, font not installed | Segoe UI |
| Power BI Service, app, embedded, in a browser | Each viewer's browser walks the stack: Libre Franklin if **that viewer** has it installed, otherwise Segoe UI (`wf_segoe-ui_normal` is Power BI's own web font, so it's always there) |
| Mobile apps | Segoe UI, or the platform default |
| Export to PDF / PowerPoint, subscriptions | Rendered by the service, so expect Segoe UI |

What this means in practice:
- **Most viewers will see Segoe UI.** That is the intended fallback, and it is fine: both are neutral grotesque sans serifs. Libre Franklin runs a little wider, so leave about 10% slack on labels that nearly fit. Never size a visual so a label only just fits in Libre Franklin.
- **Weights come from the font name.** Power BI has a Bold toggle but no weight control, so the theme names the weight: visual titles use `Libre Franklin SemiBold` (falling back to `Segoe UI Semibold`), and card callouts use `Libre Franklin Bold` (falling back to `Segoe UI Bold`), so big KPI numbers are bold. Leave the titles' Bold toggle off.
- Don't type a font name into individual visuals. Leave the theme's stack in place, so the fallback works the same way everywhere.

## 3. Highlight with measures, not by hand
Clicking a bar and recoloring it breaks the moment the data refreshes. Drive color from a measure instead:

```DAX
Bar color =
VAR rate = [Attrition %]
RETURN IF ( rate > 0.20, "#005A8C", "#B4B0A5" )      -- focus blue above the threshold, context grey otherwise
```
Apply it with **Format › Columns (or Bars) › Colors › fx › Format style: Field value › Bar color**. The same pattern works for a navy accent on the one exception (`#143359`), an orange flag for values below target (`#EF8200`, only when below target is the message), or a data-label font color. Keep the hex codes in one "Colors" measure table, so a palette change is one edit.

## 4. Titles that state the insight
Use a measure for the title, so it stays true when filters change:
```DAX
Attrition title =
VAR top = TOPN ( 1, VALUES ( 'Job'[Job family] ), [Attrition %] )
RETURN MAXX ( top, 'Job'[Job family] ) & " has the highest attrition at " & FORMAT ( MAXX ( top, [Attrition %] ), "0.0%" )
```
Then **Format › General › Title › Text › fx › Field value › Attrition title**. Put the neutral description (metric, unit, scope, period) in the **subtitle**.

## 5. Protect small groups
Blank every measure below the minimum group size, so cards, tooltips, drill-downs and exports all inherit it:
```DAX
Headcount (safe) = IF ( [Headcount] < 10, BLANK (), [Headcount] )
Attrition % (safe) = IF ( [Headcount] < 10, BLANK (), [Attrition %] )
```
Use the "safe" measures in every visual, and hide the raw ones (**Model › Hide in report view**). Also check the **totals**: if only one member of a total is blanked, its value can be worked out by subtraction. Combine with row-level security for anything below firm level.

## 6. Page layout
- Top-left is the most important spot: a row of 3–5 KPI cards, then the primary chart, then the detail.
- One page is about one decision. If a page needs scrolling, make it two pages.
- Keep slicers in one consistent place (a left rail or a top bar), and show the active filters.
- Recipes for each visual (bar, line, matrix heat table, map, KPI and more) are under **Power BI** on each [cookbook page](cookbook/).

## Checklist before publishing
- [ ] Theme applied. No visual has a hand-typed font or a hand-picked color outside the palette.
- [ ] Highlight colors come from measures; there are ≤ 6 series colors per visual.
- [ ] Every visual has a question or insight title and a subtitle with the metric, unit, scope and period.
- [ ] Every measure shown is a "safe" (minimum-n) version, totals included.
- [ ] Checked in the Service as a viewer without Libre Franklin. Nothing is clipped in Segoe UI.

## Status
The theme JSON validates against schema 2.157 and passes the house-rule checks in `tools/check_powerbi_theme.py`. **Not yet done by hand:** loading the theme in Power BI Desktop, building a sample page, and publishing it to the Service to confirm the Segoe UI fallback renders as described. This guide's font table follows from how Power BI renders text in the browser. Confirm it with a real report before rollout (see ROADMAP step 5).
