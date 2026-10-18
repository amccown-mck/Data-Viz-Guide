# KPI and big-number callouts

> **Question type:** Single number
> **Use for:** one number that carries the message (a rate, count or share), with one sentence of context and a comparison; a single-% ring for progress toward a whole · **Avoid when:** the story is a trend or a comparison across groups → use a [line](line.md) or [bars](bar.md)

## When to use
- When **one number is the finding**: executive summaries, slide openers, report margins, town-hall and social cards, intranet hero tiles.
- As the **header row of a dashboard**: 3–5 KPI cards with the same anatomy (name, number, comparison, one-line definition) above the primary chart.
- **Single-% ring gauge:** one share of one whole moving toward a target, on a 0–100% scale (succession coverage, completion of required learning, workforce-plan positions filled, skills-profile completion).
- **Dark-card variant** (Deep Navy background) for keynotes, dim rooms, social posts and campaign tiles.
- **Inline in print:** a big number in a text column, next to the paragraph it supports.
- At any level of the hierarchy: an individual's self-service view ("3 of 5 AI-fluency modules complete"), a team, the firm, or an external sector statistic that frames the story.

## When not to use
- The **trend** is the message → use a [line](line.md), or add a small sparkline under the number.
- **Several groups** must be compared → use [bars](bar.md) or a [dot plot](dot-plot-dumbbell.md). A row of 8 KPI cards is a bar chart in disguise.
- More than one part of a whole matters → use a [donut](donut-pie.md) (≤ 5 parts) or a [100% stacked bar](stacked-bar.md).
- The value can exceed 100% or go negative (headcount growth, cost variance): **no ring**. Show the big number and the delta only.
- More than ~5 numbers need to be read precisely → use a [table](tables.md).
- The rate rests on a tiny population (n < 10) or is too volatile to headline: don't make it a big number.

## McKesson spec

| Element | Rule |
|---|---|
| Number | Typography role `kpi`: Libre Franklin **Bold 700**, **54 pt** on a 13.33 in slide / **56 px** on screen, Navy `#143359` on white, white on `surface.dark` `#0B3266`. Scale with the canvas (≈ 40 pt on an 8 in card). Bold, so the number pops. **One** big number per card. Round hard (62%, 4.3K, $1.2M); the `%` or unit stays with the number. |
| Context sentence | **One sentence** (≤ ~15 words) saying exactly what is counted, set directly below or beside the number: 14 pt / 15 px Regular `#505050` (white on dark). Prefer counts that make the % concrete: "254 of 410 critical roles have a ready-now successor". The headline above it still states the insight. |
| Comparison / delta | Always give the reader a reference: prior period, target, benchmark or peer ("+14 pts vs. Mar 2025", "13 pts short of the 75% target"). Medium/Semibold, 12–14 pt. Use an explicit + and a true minus (−), and say **"pts"** for percentage-point changes (never "%"). Color it only when good vs. bad is the point: `semantic.positive_text` `#007A48` / `semantic.negative_text` `#A75B00` on white, `semantic.positive` `#00AF68` / `semantic.negative` `#EF8200` on dark. Judge favorability from the audience's view (time to fill down = good). Pair the color with ▲/▼ or words, never red vs. green. |
| Ring gauge | Starts at 12 o'clock and runs **clockwise**. Filled arc `chart.focus` `#005A8C` with the remainder in `chart.context_light` `#DEDBD1`; on dark, `chart.focus_on_dark` `#66C4FF` with `chart.context_on_dark` `#5A7194`. Stroke ≈ 15–20% of the radius (hole ≈ 80%, thinner than the 62% donut hole). No rounded caps, gaps, gradients or 3D. The number sits centered inside. A target is a thin tick across the ring, labelled ("Target 75%"). 0–100% of one whole only. |
| Dark card | Background `surface.dark` `#0B3266`, text white, one highlight `#66C4FF`. Orange `#EF8200` only for an unfavorable comparison, never as decoration. Stick to the 3-tone `color.social` combinations. The card must stand alone: headline, number, comparison, source and as-of date all on the card. |
| Layout / limits | Left-align text on one edge (only the numeral inside a ring is centered). ≤ 5 KPI cards in a dashboard row, ≤ 2 big numbers per live slide. Identical anatomy and order across cards: name → number → comparison → sentence. Every card has a source and as-of date, and every number is based on **n ≥ 10** people. |

## Do / don't

| Do | Don't |
|---|---|
| Set the numeral in Bold, large, with plenty of space around it | Set it small or in a thin weight, or squeeze it into a box with borders and drop shadows |
| Add one sentence that says exactly what is counted, and from what population | Show a bare "62%" and leave the reader to guess the metric and the denominator |
| Give a comparison (prior period, target, benchmark) with an explicit sign and "pts" | Show a delta with no reference ("+14") or write "+14%" for a percentage-point change |
| Use a ring only for a share of one whole, 0–100%, starting at 12 o'clock | Use a ring or speedometer for values that can pass 100%, or several nested rings |
| Keep every card in a row identical in structure and alignment | Mix sizes, fonts and orders so each card needs reading from scratch |
| Use the dark card for dim rooms, keynotes and social, with white text and `#66C4FF` | Put mid-blue or grey small text on Deep Navy where it fails contrast |
| Put the source and as-of date on the card itself | Rely on the slide footer or the email body to say where the number came from |

## Workforce examples
- **Firm, internal (SWP), dark ring card:** *Headline:* "Succession coverage rose 14 points in a year but is still short of the 75% target". *Subtitle:* "Critical roles with at least one ready-now successor, Mar 2026 (% of 410 roles)". *Data:* talent-review and succession records in the HCM system. Ring at 62% with a target tick at 75%, the sentence "254 of 410 critical roles now have at least one ready-now successor", and the delta "+14 pts vs. Mar 2025 (48%)".
- **Team, internal, KPI row on white:** *Headline:* "Pharmacy Ops is filling more roles internally, and faster, but regrettable attrition is up". *Subtitle:* "Pharmacy Operations talent KPIs, FY26 year to date vs. FY25". *Data:* ATS requisitions plus HRIS movements and exits. Three cards: internal fill rate 41% (+6 pts, favorable green), median time to fill 38 days (−5 days, favorable green), regrettable attrition 6.8% (+0.9 pts, unfavorable orange).
- **Sector, external, inline big number:** *Headline:* "Demand for healthcare-support talent will grow about three times faster than the US labor market". *Subtitle:* "Projected employment growth, healthcare support occupations vs. all occupations, US, 2024–2034 (%)". *Data:* a national occupational employment projection (government statistics agency). Big number "+12%" with the comparison "vs. +4% for all occupations" and one sentence on what it means for pharmacy-technician hiring; source and projection vintage in the footnote. (Illustrative figures.)

## Build it

### Python — matplotlib + `mckviz`
Dark ring card. For the light version, drop `dark=True` (and the facecolors): the ring turns blue on light grey and the numeral navy.
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mckviz as mv

mv.use()
C = mv.colors

value, prior, target, n_roles = 62, 48, 75, 410                  # % of critical roles with a ready-now successor
delta = value - prior

fig, ax = plt.subplots(figsize=(8, 3.6), facecolor=C.surface_dark)
# Ring from 12 o'clock, clockwise, thin, flat ends, target tick; the number Bold inside it; one sentence;
# the change with ▲/▼ (green only because higher is better here); the gap to target in orange (a shortfall).
mv.kpi_card(ax, value, f"{round(n_roles * value / 100)} of {n_roles} critical roles now have at least one "
            "ready-now successor", change=delta, vs=f"vs. Mar 2025 ({prior}%)", target=target, ring_value=value,
            dark=True)

mv.titles(fig, f"Succession coverage rose {delta} points in a year but is still short of the {target}% target",
          f"Critical roles with at least one ready-now successor, Mar 2026 (% of {n_roles} roles)", dark=True)
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Ready-now = assessed in the FY26 talent review as able to step in within 12 months.", dark=True)
mv.lint(fig, strict=True)
mv.save(fig, "out/kpi-ring-dark.png", dpi=200, facecolor=C.surface_dark)
```
For a big number without a ring (e.g., in a report margin), leave out `ring_value`: the numeral goes top-left with the sentence, change and target under it. For a row of KPIs with identical anatomy, use `mv.kpi_row(ax, [dict(name=..., value=..., change=..., vs=..., better="up" | "down"), ...])`; `mv.delta_label(change, unit=" pts", vs=..., better=...)` returns the arrow text and its color for your own layouts, and `mv.ring`, `mv.big` and `mv.small` draw the parts separately.

### Python — Plotly / HTML
KPI row on white with `go.Indicator`. Deltas are colored by favorability, not by direction.
```python
# verified: builds without error
from pathlib import Path

import plotly.graph_objects as go

import mckviz as mv

mv.use()  # registers + activates the "mck" Plotly template
C = mv.colors
KPI = mv.TOKENS["typography"]["roles"]["kpi"]                    # Bold 700, 56 px

# value, prior, format, suffix, higher_is_better, one sentence of context
kpis = [("Internal fill rate", 41, 35, ".0f", "%", True, "of open Pharmacy Ops roles were filled<br>by internal candidates"),
        ("Median time to fill", 38, 43, ".0f", " days", False, "from requisition approval to accepted<br>offer, all Pharmacy Ops roles"),
        ("Regrettable attrition", 6.8, 5.9, ".1f", "%", False, "of high performers left voluntarily,<br>trailing 12 months")]
good, bad = C.positive_text, C.negative_text                      # green good / orange bad, text-safe on white

fig = go.Figure()
for i, (name, val, prior, fmt, suffix, up_good, context) in enumerate(kpis):
    x0 = i / 3
    fig.add_trace(go.Indicator(
        mode="number+delta", value=val, align="left",
        number={"valueformat": fmt, "suffix": suffix,
                "font": {"size": KPI["size_px"], "weight": KPI["weight"], "color": C.headline}},
        delta={"reference": prior, "valueformat": fmt, "position": "bottom",
               "suffix": " pts vs. FY25" if suffix == "%" else " days vs. FY25",
               "increasing": {"color": good if up_good else bad}, "decreasing": {"color": bad if up_good else good},
               "font": {"size": 14, "weight": 600}},
        title={"text": name, "align": "left", "font": {"size": 15, "color": C.text}},
        domain={"x": [x0 + 0.02, x0 + 0.31], "y": [0.45, 1]}))
    fig.add_annotation(text=context, x=x0 + 0.02, y=0.48, xref="paper", yref="paper", xanchor="left", yanchor="top",
                       showarrow=False, align="left", font={"size": 13, "color": C.text})
mv.pl_finish(fig, "Pharmacy Ops is filling more roles internally, and faster, but regrettable attrition is up",
             "Pharmacy Operations talent KPIs, FY26 year to date vs. FY25", "Source: Synthetic data for illustration only",
             footnote="Regrettable = voluntary exits of employees rated 'exceeds' or above. Groups with fewer than 10 people suppressed.")
fig.update_layout(height=380, margin={"l": 24, "r": 24, "t": 110})
Path("out").mkdir(exist_ok=True)
fig.write_html("out/kpi-row.html", include_plotlyjs="cdn")
```
For a ring in Plotly, use `go.Pie(values=[62, 38], hole=0.8, sort=False, direction="clockwise", rotation=0, marker_colors=[C.focus, C.context_light], textinfo="none")` with the numeral as a centered annotation. In HTML pages, plain HTML text is often the better choice for a big number: a `<p class="mck-kpi">` styled from [`assets/web/mck-viz.css`](../../assets/web/mck-viz.css) (`--mck-kpi-size: 56px`, `--mck-kpi-weight: 700`) is crisper, accessible and responsive.

### Excel and PowerPoint
**Big number (text box)**
1. Install Libre Franklin from `assets/fonts`, and the McKesson Data Viz theme colors from `office/` (see [bar.md](bar.md#excel-and-powerpoint)).
2. **Insert › Text Box**, type the number (e.g., `62%`). Set **Home › Font** to **Libre Franklin, Bold, 54 pt**, with **Font Color › More Colors › Hex 143359** (Navy; *Text 2* in the theme is McKesson Blue, for slide titles). In **Format Shape › Text Options › Text Box**, set the left inset to 0 cm so the numeral aligns with the headline edge, and **Do not Autofit**.
3. Add a second text box directly below: **one sentence**, Libre Franklin 14 pt, `#505050` ("254 of 410 critical roles now have at least one ready-now successor").
4. Add the comparison: Libre Franklin Medium 12–14 pt, `#007A48` (favorable) or `#A75B00` (unfavorable), e.g., "+14 pts vs. Mar 2025". For a true minus, use **Insert › Symbol**, character code **2212**.
5. Select the boxes, then **Shape Format › Align › Align Left** and **Group** (Ctrl+G). Copy the group to build a row of identical cards, and use **Align › Distribute Horizontally**.
6. Live numbers in Excel: select a text box border, type `=Summary!B2` in the formula bar, and the box displays the cell (format the cell, not the box). Paste into PowerPoint with **Paste Special › Paste link** if it must update.

**Single-% ring (doughnut trick)**

7. In Excel, enter the value and the remainder in two cells: `B2 = 0.62`, `B3 = 1-B2`. Select both, then **Insert › Charts › Insert Pie or Doughnut Chart › Doughnut**.
8. **Format Data Series › Series Options:** **Angle of first slice 0°** (starts at 12 o'clock, runs clockwise) and **Doughnut Hole Size 80%**.
9. Click the value slice on its own: **Fill › Solid › Hex 005A8C**. Click the remainder: **Hex DEDBD1**. On a dark card, use `66C4FF` and `5A7194`. Set **Border › No line** on both.
10. Delete the chart title, legend and data labels. Set **Format Chart Area › Fill: No fill** and **Border: No line**.
11. Lay the big-number text box over the ring's center (**Align Center** + **Align Middle**) and group them. For a target, draw a thin **Line** shape across the ring at the target angle (75% = 9 o'clock) and label it "Target 75%".
12. Dark card: on the slide, **Design › Format Background › Solid fill › Hex 0B3266**. Set the text to white, the ring to `66C4FF` / `5A7194` and the favorable delta to `00AF68`. Keep a source line (9 pt, white) on the card.
13. In PowerPoint, paste the ring with **Home › Paste › Use Destination Theme & Embed Workbook** so the number stays editable, and keep **≤ 2 big numbers per live slide**.

### Power BI
- Import [`assets/powerbi/mckesson-dataviz-theme.json`](../../assets/powerbi/mckesson-dataviz-theme.json) (**View › Themes › Browse for themes**). Its **`callout` text class** (Libre Franklin 32, Navy `#143359`) styles Card values by default. Raise **Format › Callout value** to 40–54. The theme sets the callout face to Libre Franklin Bold, falling back to Segoe UI Bold where Libre Franklin isn't installed, so the numeral is bold everywhere.
- **Card (new)** visual: callout value = the measure. Use the visual **title** for the metric name and **Reference labels** for the comparison (e.g., `Δ vs PY = [Fill rate] - [Fill rate PY]`, formatted `+0" pts";−0" pts"`). Add the context sentence as a dynamic subtitle measure, e.g., `FORMAT([Roles covered], "#,0") & " of " & FORMAT([Critical roles], "#,0") & " critical roles have a ready-now successor"`.
- **KPI** visual (number + trend + target): **Indicator** = the measure, **Trend axis** = month, **Target** = the target or prior-year measure. Under **Format › Colors**, set Good `#00AF68`, Neutral `#B4B0A5`, Bad `#EF8200`, and set the direction (**High is good** / **Low is good**) per metric.
- Ring: use a **Donut chart** with two measures (`Value`, `1 - Value`), **Slices › Inner radius** ≈ 80, colors `#005A8C` / `#DEDBD1`, labels and legend off, and a Card with a transparent background on top. Avoid the built-in half-circle **Gauge** unless min = 0, max = 100% and the target is shown.
- Suppress small groups at the source: `Fill rate (safe) = IF([Requisitions] < 10, BLANK(), [Fill rate])`.

### R — ggplot2 (optional)
```r
library(ggplot2)
source("assets/r/theme_mck.R")

value <- 62; prior <- 48; target <- 75
dark <- "#0B3266"; focus_dark <- "#66C4FF"; context_dark <- "#5A7194"
ring <- data.frame(part = factor(c("rest", "done"), levels = c("rest", "done")),   # "done" stacks from 0
                   pct  = c(100 - value, value))

ggplot(ring, aes(x = 2, y = pct, fill = part)) +
  geom_col(width = 0.35, colour = NA) +
  annotate("segment", x = 1.75, xend = 2.25, y = target, yend = target, colour = "white", linewidth = 0.8) +
  annotate("text", x = 2.5, y = target, label = paste0("Target ", target, "%"), colour = "white", size = 3,
           family = "Libre Franklin") +
  annotate("text", x = 0.5, y = 0, label = paste0(value, "%"), colour = "white", size = 40 / .pt,
           fontface = "bold", family = "Libre Franklin") +         # kpi role: Bold; 54 pt on a full slide
  annotate("text", x = 0.5, y = 0, vjust = 4.2, label = sprintf("+%d pts vs. Mar 2025", value - prior),
           colour = "#00AF68", size = 4, fontface = "bold", family = "Libre Franklin") +
  coord_polar(theta = "y", start = 0, direction = 1) +            # 12 o'clock, clockwise
  scale_x_continuous(limits = c(0.5, 2.7)) +
  scale_fill_manual(values = c(done = focus_dark, rest = context_dark), guide = "none") +
  labs(title = "Succession coverage rose 14 points in a year but is still short of the 75% target",
       subtitle = "Critical roles with at least one ready-now successor, Mar 2026 (% of 410 roles)",
       caption = "Ready-now = able to step in within 12 months (FY26 talent review).\nSource: Synthetic data for illustration only") +
  theme_void(base_family = "Libre Franklin") +
  theme(plot.background = element_rect(fill = dark, colour = NA),
        plot.title = element_text(face = "bold", size = 18, colour = "white"),
        plot.subtitle = element_text(size = 12, colour = "white", margin = margin(b = 12)),
        plot.caption = element_text(size = 9, colour = "white", hjust = 0),
        plot.title.position = "plot", plot.caption.position = "plot",
        plot.margin = margin(16, 16, 16, 16))
```
For a plain big number on a light background, use `ggplot() + annotate("text", x = 0, y = 0, label = "41%", hjust = 0, size = 54 / .pt, fontface = "bold", family = "Libre Franklin", colour = mck_colors$headline) + theme_void()` and add the sentence and delta as further left-aligned `annotate()` calls below it.

### HTML / JavaScript — `mck-viz.css` + `mck-viz.js`
A KPI row: `.mck-kpi` tiles in a `.mck-grid` (1 column under 560 px, 2 to 980 px, 3 above). Name, Bold navy number (`kpi` role), comparison with ▲/▼ for direction and green/orange text for favorability, one sentence, and an optional meter with a target tick and a gap line. Copy `assets/web/mck-viz.css` and `assets/web/mck-viz.js` next to the page (offline or locked-down intranet: also `assets/web/vendor/plotly.min.js`, see [formats.md](../formats.md#web-and-html-articles-microsites-internal-tools)). `mck-viz.js` carries the tokens, the Plotly template and the helpers (`mck.tok`, `mck.fmtNum`, `mck.plotlyLayout`, ...), so no hex value is typed in the page.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pharmacy Ops KPIs</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="mck-viz.css">   <!-- assets/web/mck-viz.css, copied next to this page -->
<script src="mck-viz.js"></script>           <!-- assets/web/mck-viz.js: fmtNum, suppressSmall -->
<style>
  body { margin: 0; padding: 24px 16px; background: var(--mck-surface-subtle); font-family: var(--mck-font); }
  .kpi-row { max-width: 1008px; margin: 0 auto; }
</style>
</head>
<body>
<section class="kpi-row" aria-labelledby="kpi-headline">
  <h2 class="mck-headline" id="kpi-headline">Pharmacy Ops is filling more roles internally, and faster, but regrettable attrition is up</h2>
  <p class="mck-subtitle">Pharmacy Operations talent KPIs, FY26 year to date vs. FY25</p>
  <div class="mck-grid" id="kpis">
    <noscript>Internal fill rate 41% (+6 pts vs. FY25); median time to fill 38 days (−5 days); regrettable attrition 6.8% (+0.9 pts).</noscript>
  </div>
  <p class="mck-footnote">Regrettable = voluntary exits of employees rated "exceeds" or above. Groups with fewer than 10 people suppressed.<br>
    Source: Synthetic data for illustration only. As of Mar 2026.</p>
</section>
<script>
const { fmtNum } = mck;
const kpis = [   // DATA: name, value, prior, unit, higher is better, the one sentence of context, optional target, n
  { name: "Internal fill rate", value: 41, prior: 35, unit: "pct", up: true, target: 45, n: 410,
    text: "of open Pharmacy Ops roles were filled by internal candidates" },
  { name: "Median time to fill", value: 38, prior: 43, unit: "days", up: false, n: 410,
    text: "from requisition approval to accepted offer, all Pharmacy Ops roles" },
  { name: "Regrettable attrition", value: 6.8, prior: 5.9, unit: "pct", up: false, n: 1250,
    text: "of high performers left voluntarily, trailing 12 months" },
];
const [shown] = mck.suppressSmall(kpis, "n", { otherLabel: null });   // no KPI rests on fewer than 10 people
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

function tile(k) {
  const pct = k.unit === "pct", dec = Number.isInteger(k.value) ? 0 : 1;
  const value = pct ? fmtNum(k.value, { kind: "pct", decimals: dec }) : `${fmtNum(k.value)}<small> days</small>`;
  const d = k.value - k.prior;                                   // pts for a change in a %, never "%"
  const delta = `${fmtNum(d, { kind: "plain", decimals: dec, sign: true })} ${pct ? "pts" : "days"} vs. FY25`;
  const dir = d > 0 ? "is-up" : d < 0 ? "is-down" : "";
  const fav = d === 0 ? "" : (d > 0) === k.up ? "is-good" : "is-bad";   // favorability, from the audience's view
  const gap = k.target == null ? "" : `<span class="mck-kpi__meter" style="--value:${k.value}%;--target:${k.target}%"></span>
      <p class="mck-kpi__gap">${fmtNum(k.target - k.value, { kind: "plain" })} pts short of the ${k.target}% target</p>`;
  return `<div class="mck-kpi">
      <p class="mck-kpi__name">${esc(k.name)}</p>
      <p class="mck-kpi__value">${value}</p>
      <p class="mck-kpi__delta ${dir} ${fav}">${delta}<span class="sr-only">, ${fav === "is-good" ? "better" : "worse"}</span></p>
      <p class="mck-kpi__label">${esc(k.text)}</p>${gap}
    </div>`;
}
document.getElementById("kpis").innerHTML = shown.map(tile).join("");
</script>
</body>
</html>
```
The tiles are plain HTML, so they also work as static markup with no script. On dark surfaces add `mck-kpi--dark` (white number, `#66C4FF` meter, `semantic.positive`/`negative` deltas). A bare `<p class="mck-kpi">41%</p>` still styles just the number.

## QA specifics
- [ ] The big number is set in the `kpi` role: Bold, large, Navy on white or white on `#0B3266`. It is the only big number on the card, and it is rounded sensibly.
- [ ] One sentence states exactly what is counted and from what population, and the headline states the insight. The number, sentence and headline all agree (recompute: 62% × 410 = 254).
- [ ] A comparison is present (prior period, target or benchmark) with an explicit +/−, "pts" for percentage-point changes, and colors chosen by favorability with a non-color cue.
- [ ] The ring shows 0–100% of one whole, starts at 12 o'clock, runs clockwise, has a hole ≈ 80% and no rounded caps, and any target tick is labelled.
- [ ] On dark cards, all text passes 4.5:1 contrast (white; no `#5A7194` text), and the source and as-of date are on the card itself.
- [ ] Cards in a row share identical anatomy and alignment (≤ 5 per row, ≤ 2 big numbers per live slide), and no KPI rests on fewer than 10 people.

## Inspiration
- [p076 — Social media](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p076-social-media.md)
- [p078 — Social media considerations](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p078-social-media-considerations.md)
- [p083 — Presentations](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p083-presentations.md)
- [p085 — Print (big-number callouts)](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p085-print.md)
