# Plans and status: roadmap, tracker, status column

> **Question type:** Plans and status
> **Use for:** what happens when, who owns it, and whether it is on track (programs, initiatives, workstreams) · **Avoid when:** the question is about a measure (attrition, cost, headcount) → use a [bar](bar.md), [line](line.md) or [table](tables.md); status colors never encode data

## When to use
- **Roadmap (Gantt):** the plan over time for a handful of workstreams (≤ ~10), with milestones and a today line, so a steering committee sees what slipped and what waits on it.
- **Tracker table:** the same workstreams as rows, exceptions first: status, owner, next milestone and what changed since the last review. The default for a status update.
- **Status column:** a status pill beside an existing chart or scorecard (budget used, milestones met), so the judgment sits next to the evidence.

## When not to use
- To color a measure red/amber/green (attrition by unit, pay vs. market) → use grey context plus blue focus, and orange only for worse; see [color.md §4](../color.md#4-status-colors-red-amber-green).
- For many items over a long time (a release calendar of 60 items) → a table sorted by date, or a filtered roadmap per program.
- For a single date → a sentence, or a milestone in the headline.
- For process stages with volumes (nominated → enrolled → completed) → a [Sankey](sankey.md) or bars in `mv.STEPS` colors.

## McKesson spec

| Element | Rule |
|---|---|
| Color | Status colors only from `color.status` (`mv.STATUS`): On track `#00AF68`, At risk `#FFB500`, Off track `#DA2103`, Not started `#BFBFBF`, Complete `#005A8C`, as small dots or chips, never large fills. **Always with the symbol and the word** (✓ On track, ! At risk, ✕ Off track, – Not started, ✓ Complete). Roadmap bars are not status: grey `chart.context`, the workstreams the headline names in blue `chart.focus`, not-started in `chart.context_light`. Milestones: met = navy filled ◆, due = hollow navy ◇, missed = red ✕, original date of a moved milestone = hollow grey ◇ with an arrow to the new date. The today line is a dashed navy `chart.total`. |
| Labels | Workstream names left-aligned, the owner under each in muted 9 pt. Off-track and at-risk workstreams bold navy. Label a moved milestone in place ("Moved Mar to Jun"); name the milestone kinds once in a small key, bottom left. |
| Axes / gridlines | No value axis. Quarters and fiscal years along the top (McKesson FY starts in April: FY26 = Apr 2025–Mar 2026), light quarter rules, a thin rule under the header. |
| Sort / order | Roadmap: related work together (a dependency above its dependents). Tracker: **exceptions first** (off track, at risk, on track, not started, complete), then by start date. |
| Proportions | Thin bars (about a third of the row), rows ≈ 0.4 in; one row per workstream. |
| Limits | ≤ ~10 workstreams per view. The roll-up ("7 workstreams: 2 off track, 1 at risk ...") goes over the tracker. Status as of a date stated in the subtitle. |

## Do / don't

| Do | Don't |
|---|---|
| Pair every status color with its symbol and word | Use a red or green dot alone, or color the whole row |
| Put exceptions first and say what changed | List workstreams alphabetically with no "since last time" |
| Show a slip as the original date, an arrow and the new date | Silently move the milestone |
| State the as-of date and draw a today line | Leave the reader to guess where "now" is |
| Keep bars grey and blue; let status live in its own column | Color Gantt bars red/amber/green |

## Workforce examples
- **Roadmap:** *Headline:* "Two of seven workstreams are off track, both waiting on the skills inventory's Workday integration". *Subtitle:* "Workforce Innovation roadmap by workstream, FY26–FY27, with status as of 31 Mar 2026". *Data:* [`initiative_plan.csv`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/examples/data/initiative_plan.csv), [`initiative_milestones.csv`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/examples/data/initiative_milestones.csv).
- **Tracker:** *Headline:* "Three of seven workstreams need a decision, all because the Workday integration slipped three months". *Subtitle:* "Status, owner, next milestone and change since February, as of 31 Mar 2026". *Data:* the same two files.
- **Status column:** *Headline:* "The skills inventory has used 71% of its budget with the integration still three months out". *Subtitle:* "Budget used by workstream, FY26–FY27 plan, as of 31 Mar 2026 (%)". *Data:* `initiative_plan.csv` (`budget_used_pct`, `status`); monthly history in [`initiative_status_history.csv`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/examples/data/initiative_status_history.csv).

## Build it

### Python — matplotlib + `mckviz`
**Roadmap (Gantt).** `mv.roadmap` draws the name and owner, the status pill, the bars, the milestones, slips and the today line, and sizes the figure to the rows.
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
plan = pd.read_csv("assets/data/initiative_plan.csv")
ms = pd.read_csv("assets/data/initiative_milestones.csv")
off = plan[plan.status == "off_track"]
dep = off.depends_on.iloc[0]
words = {2: "Two", 3: "Three"}

fig, ax = plt.subplots(figsize=(11, 4.5))
rm = mv.roadmap(ax, plan, ms, start="2025-04", end="2027-03", today="2026-03", today_label="Today, 31 Mar 2026")
# off-track bars blue, the rest grey; ◆ met, ◇ due, ✕ missed, moved = grey ◇ -> arrow -> ◇ with "Moved Mar to Jun"

mv.titles(fig, f"{words[len(off)]} of {len(plan)} workstreams are off track, both waiting on the "
               f"{dep.lower().replace(' rollout', '')}'s Workday integration",
          "Workforce Innovation roadmap by workstream, FY26–FY27, with status as of 31 Mar 2026")
mv.source(fig, "Source: Workforce Innovation PMO (synthetic data for illustration only), as of 31 Mar 2026")
mv.lint(fig, strict=True)
mv.save(fig, "out/roadmap.png", dpi=200)
```

**Tracker table.** Exceptions first, a roll-up over the table, and the next milestone worked out from the milestone file (missed and moved ones in bold navy).
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
plan = pd.read_csv("assets/data/initiative_plan.csv")
ms = pd.read_csv("assets/data/initiative_milestones.csv")
moved = ms[ms.state == "moved"].iloc[0]
slip = (pd.Period(moved.forecast, "M") - pd.Period(moved.due, "M")).n
n_exc = plan.status.isin(["off_track", "at_risk"]).sum()
words = {2: "two", 3: "three", 4: "four"}

fig, ax = plt.subplots(figsize=(11, 5))
tr = mv.tracker(ax, plan, milestones=ms)        # columns: Status | Workstream, owner | Next milestone | What changed

mv.titles(fig, f"{words[n_exc].capitalize()} of {len(plan)} workstreams need a decision, all because the Workday "
               f"integration slipped {words[slip]} months",
          "Status, owner, next milestone and change since February, as of 31 Mar 2026")
mv.source(fig, "Source: Workforce Innovation PMO (synthetic data for illustration only), as of 31 Mar 2026")
mv.lint(fig, strict=True)
mv.save(fig, "out/tracker.png", dpi=200)
```

**Status column** beside a chart: the evidence (budget used) as grey bars with the headline's row in blue, and the judgment as a pill per row.
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
plan = pd.read_csv("assets/data/initiative_plan.csv")
open_ = plan[plan.status != "done"]
top = open_.sort_values("budget_used_pct", ascending=False).iloc[0]          # the most spent of the open work

fig, ax = plt.subplots(figsize=(10, 4.6))
y = list(range(len(plan)))
bars = ax.barh(y, plan.budget_used_pct, color=mv.highlight(plan.workstream, focus=top.workstream), height=0.6)
ax.set_yticks(y, plan.workstream)
ax.invert_yaxis()
ax.set_xlim(0, 112)                                  # room for the value labels before the status column
mv.label_bars(ax, bars, fmt="{:.0f}%")
mv.clean_axes(ax, keep=("left",), grid=None)
ax.set_xticks([])
mv.status_column(ax, plan.status)                    # dot + symbol + word, aligned with each bar

mv.titles(fig, f"The {top.workstream[0].lower() + top.workstream[1:]} has used {top.budget_used_pct:.0f}% of its "
               "budget, the most of any open workstream, with its integration three months late",
          "Budget used by workstream, FY26–FY27 plan, as of 31 Mar 2026 (%)")
mv.source(fig, "Source: Workforce Innovation PMO (synthetic data for illustration only), as of 31 Mar 2026")
mv.lint(fig, strict=True)
mv.save(fig, "out/status-column.png", dpi=200)
```

**Status over time:** one `mv.sdot` (color + symbol) per workstream and month, and the word for the latest month.
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
C = mv.colors
hist = pd.read_csv("assets/data/initiative_status_history.csv")
grid = hist.pivot(index="workstream", columns="month", values="status").loc[list(dict.fromkeys(hist.workstream))]
went_off = [w for w in grid.index if grid.loc[w].iloc[-1] == "off_track"]

fig, ax = plt.subplots(figsize=(10, 4.2))
for i, w in enumerate(grid.index):
    hot = w in went_off
    ax.text(-0.7, i, w, ha="right", va="center", fontsize=11, color=C.headline if hot else C.text,
            fontweight="semibold" if hot else "normal")
    for j in range(grid.shape[1]):
        mv.sdot(ax, j, i, grid.iloc[i, j], size=14)
    ax.text(grid.shape[1] - 0.4, i, mv.STATUS[grid.iloc[i, -1]]["label"], va="center", fontsize=11,
            color=C.headline if hot else C.text, fontweight="semibold" if hot else "normal")
for j, m in enumerate(grid.columns):
    ax.text(j, -0.9, pd.Period(m, "M").strftime("%b"), ha="center", fontsize=10, color=C.text_muted)
ax.text(grid.shape[1] - 0.4, -0.9, "Now", fontsize=10, color=C.text_muted)
ax.set_xlim(-0.6, grid.shape[1] + 1.4)
ax.set_ylim(len(grid) - 0.5, -1.2)
ax.axis("off")

mv.titles(fig, f"{len(went_off)} workstreams went off track this quarter after the skills inventory turned at risk",
          "Monthly status by workstream, Oct 2025–Mar 2026")
mv.source(fig, "Source: Workforce Innovation PMO (synthetic data for illustration only), as of 31 Mar 2026")
mv.lint(fig, strict=True)
mv.save(fig, "out/status-history.png", dpi=200)
```
The pieces work on their own too: `mv.status(ax, x, y, "at_risk")` draws one pill anywhere (pass `transform=ax.transAxes` for axes coordinates), `mv.sdot` one dot with its symbol, `mv.status_key("On track")` normalizes names, and `mv.STATUS_ORDER` sorts exceptions first.

### HTML / JavaScript — Plotly + `mck-viz.js`
A status roll-up and tracker built from `.mck-status` pills (color + symbol + word, never color alone) and a `.mck-tracker` table, then a Plotly roadmap as horizontal stacked bars (an invisible offset, then work complete in focus blue and work remaining in `chart.context_light`) with a dashed Today line. Exceptions (off track, at risk) sort first and are bold. Copy `assets/web/mck-viz.css` and `assets/web/mck-viz.js` next to the page (offline or locked-down intranet: also `assets/web/vendor/plotly.min.js`, see [formats.md](../formats.md#web-and-html-articles-microsites-internal-tools)); `mck.status(key)` returns `{color, symbol, word, ink}` from the tokens.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Workforce program status</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="mck-viz.css">   <!-- assets/web/mck-viz.css, copied next to this page -->
<script src="mck-viz.js"></script>           <!-- assets/web/mck-viz.js: tokens, status(), helpers, Plotly template -->
<script src="https://cdn.plot.ly/plotly-4.1.1.min.js" charset="utf-8"></script>   <!-- offline: vendor/plotly.min.js -->
<style>
  body { margin: 0; padding: 24px 16px; background: var(--mck-surface-subtle); }
  main { display: grid; gap: 24px; max-width: 1008px; margin: 0 auto; }
  .mck-chart { margin: 0; max-width: none; }
  .rollup { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: var(--mck-label-size); margin: 0 0 12px; }
  .rollup b { color: var(--mck-text-headline); }
  .mck-plot { height: 340px; }
  @media (max-width: 600px) { body { padding: 0; } main { gap: 12px; } }
</style>
</head>
<body>
<main>
  <figure class="mck-chart" aria-labelledby="pl-headline">
    <h2 class="mck-headline" id="pl-headline">Three of six workforce workstreams are behind, and all three wait on the Workday integration</h2>
    <p class="mck-subtitle">Workforce Innovation program status, FY26–FY27, as of Oct 2026</p>
    <div class="rollup" id="pl-rollup"></div>
    <div class="mck-scroll">
      <table class="mck-tracker" id="pl-tracker">
        <colgroup><col style="width:16%"><col style="width:30%"><col style="width:26%"><col></colgroup>
        <thead><tr><th scope="col">Status</th><th scope="col">Workstream, owner</th><th scope="col">Next milestone</th>
          <th scope="col">What changed</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <noscript><p class="mck-subtitle">Off track: Skills inventory. At risk: SWP model refresh, Gen AI reskilling.
      On track: Manager insights dashboards. Not started: Pay equity review. Complete: Internal mobility marketplace.</p></noscript>
  </figure>

  <figure class="mck-chart" aria-labelledby="rm-headline">
    <h2 class="mck-headline" id="rm-headline">The Workday integration slipped four months; the two workstreams that depend on it now finish in FY27 Q4</h2>
    <p class="mck-subtitle">Roadmap: planned start to finish by workstream; blue = work complete, as of Oct 2026</p>
    <div class="mck-plot" id="rm-chart" role="img" aria-label="Roadmap of six workstreams from Apr 2025 to Mar 2027 with a
         Today line at Oct 2026. Skills inventory is 55% complete and off track; SWP model refresh and Gen AI reskilling are
         at risk; the internal mobility marketplace is complete; pay equity review has not started."></div>
    <table class="sr-only" id="rm-table"></table>
    <figcaption class="mck-footnote">Months from the start of FY26 (Apr 2025). Status as reported by workstream owners.<br>
      Source: Synthetic data for illustration only</figcaption>
  </figure>
</main>
<script>
const { tok, status } = mck;
const MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"];
const mon = m => `${MONTHS[m % 12]} ${2025 + Math.floor((m + 3) / 12)}`;   // month index 0 = Apr 2025 (FY26 start)
const TODAY = 18.15;                                          // early Oct 2026
const plan = [   // DATA: workstream, owner, status key, start, end (month index), share done, next milestone, slip, what changed
  { ws: "Skills inventory (Workday)", owner: "HR Technology", st: "off_track", start: 3, end: 20, done: 0.55,
    next: "Workday integration live", slip: "Dec 2026 (was Aug)", note: "Vendor API delay; integration re-planned" },
  { ws: "SWP model refresh", owner: "Workforce Planning", st: "at_risk", start: 6, end: 23, done: 0.5,
    next: "Scenario model v2", slip: "Missed Sep; no new date", note: "Waiting on skills data from the inventory" },
  { ws: "Gen AI reskilling", owner: "Learning", st: "at_risk", start: 4, end: 23, done: 0.6,
    next: "Cohort 3 launch", slip: "Jan 2027 (was Nov)", note: "Needs skills profiles to pick cohorts" },
  { ws: "Manager insights dashboards", owner: "People Analytics", st: "on_track", start: 9, end: 21, done: 0.75,
    next: "Pilot with 40 managers", due: "Nov 2026", note: "Pilot group confirmed" },
  { ws: "Pay equity review", owner: "Total Rewards", st: "not_started", start: 19, end: 24, done: 0,
    next: "Kick-off", due: "Nov 2026", note: "Starts after the FY27 merit cycle" },
  { ws: "Internal mobility marketplace", owner: "Talent", st: "done", start: 0, end: 15, done: 1,
    next: "All milestones met", due: "", note: "Live for all US employees" },
];
const ORDER = ["off_track", "at_risk", "on_track", "not_started", "done"];   // exceptions first
plan.sort((a, b) => ORDER.indexOf(a.st) - ORDER.indexOf(b.st));
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
const pill = (key, extra = "") => `<span class="mck-status mck-status--${key.replace("_", "-")}${extra}">${status(key).word}</span>`;

/* ---------- Roll-up and tracker: color + symbol + word, never color alone ---------- */
document.getElementById("pl-rollup").innerHTML = `<b>${plan.length} workstreams</b>` + ORDER.map(k => {
  const n = plan.filter(p => p.st === k).length;
  return n ? `<span>${pill(k)} <b>${n}</b></span>` : "";
}).join("");
document.querySelector("#pl-tracker tbody").innerHTML = plan.map(p => {
  const exc = p.st === "off_track" || p.st === "at_risk";
  const when = p.slip ? `<span class="slip">${esc(p.slip)}</span>` : p.due ? `<span class="due">${esc(p.due)}</span>` : "";
  return `<tr class="${exc ? "is-exception" : ""}"><td>${pill(p.st)}</td>
    <th scope="row">${esc(p.ws)}<span class="owner">${esc(p.owner)}</span></th>
    <td>${esc(p.next)}${when}</td><td>${esc(p.note)}</td></tr>`;
}).join("");

/* ---------- Roadmap: horizontal stacked bars (invisible offset + done + remaining) and a Today line ---------- */
const names = plan.map(p => (p.st === "off_track" || p.st === "at_risk" ? `<b>${p.ws}</b>` : p.ws));
const seg = (name, x, color, extra = {}) => ({ type: "bar", orientation: "h", name, y: names, x, marker: { color }, ...extra });
const narrow = window.matchMedia("(max-width: 600px)").matches;
mck.ready(() => Plotly.newPlot("rm-chart", [
  seg("offset", plan.map(p => p.start), "rgba(0,0,0,0)", { hoverinfo: "skip" }),
  seg("Complete", plan.map(p => (p.end - p.start) * p.done), tok("chart-focus"),
      { customdata: plan.map(p => Math.round(p.done * 100)), hovertemplate: "%{y}<br>%{customdata}% complete<extra></extra>" }),
  seg("Remaining", plan.map(p => (p.end - p.start) * (1 - p.done)), tok("chart-context-light"),
      { customdata: plan.map(p => `${mon(p.start)} to ${mon(p.end - 1)}`), hovertemplate: "%{y}<br>%{customdata}<extra></extra>" }),
], mck.plotlyLayout("roadmap", {
  margin: { t: 40, r: narrow ? 24 : 120 },                   // phones: fewer ticks, status stays in the tracker
  xaxis: { range: [0, 24], tickvals: narrow ? [0, 12, 24] : [0, 6, 12, 18, 24],
           ticktext: narrow ? ["Apr '25", "Apr '26", "Apr '27"] : ["Apr 2025", "Oct", "Apr 2026", "Oct", "Apr 2027"],
           showgrid: true, gridcolor: tok("chart-grid") },
  yaxis: { tickfont: { color: tok("text-primary") }, showticklabels: true },
  shapes: [{ type: "line", x0: TODAY, x1: TODAY, y0: 0, y1: 1, yref: "paper", layer: "above",
             line: { color: tok("chart-annotation"), width: 1, dash: "dash" } }],
  annotations: [{ x: TODAY, y: 1, yref: "paper", yanchor: "bottom", yshift: 18, text: "<b>Today</b>", showarrow: false,
                  font: { color: tok("chart-annotation") } },
    ...(narrow ? [] : plan.map((p, i) => {                   // status at the row end: colored dot + word
      const s = status(p.st);
      return { x: 24, y: names[i], xanchor: "left", xshift: 10, showarrow: false, align: "left",
               text: `<span style="color:${s.color}">●</span> ${p.st === "off_track" || p.st === "at_risk" ? `<b>${s.word}</b>` : s.word}`,
               font: { color: tok("text-primary") } };
    }))],
}), mck.plotConfig));
mck.srTable("rm-table", "Workstream schedule", ["Workstream", "Status", "Start", "Finish", "Complete (%)"],
            plan.map(p => [p.ws, status(p.st).word, mon(p.start), mon(p.end - 1), Math.round(p.done * 100)]));
</script>
</body>
</html>
```
Status colors are for status only, never for data series: the roadmap bars stay blue and grey, and status shows as a dot plus the word at the row end (on phones, in the tracker only). The tracker also works as static HTML: `<span class="mck-status mck-status--at-risk">At risk</span>` needs no script. Wrap wide trackers in `<div class="mck-scroll">` so they scroll sideways on phones instead of squeezing.

### Excel and PowerPoint
Start from the roadmap and tracker slides in the starter deck; see the starter-deck slide guide in [docs/office-setup.md](../office-setup.md).

### Power BI
- Put status in a **Table** visual: a status text column ("✓ On track") with **Font color › fx › Rules** from the `mv.STATUS` hexes, and the workstream and owner next to it. Never conditional-format a measure's bars red/amber/green.
- Sort by a status-order column (off track = 1 ... complete = 5) so exceptions come first.

### R — ggplot2 (optional)
```r
# Status colors: mck_status in assets/r/theme_mck.R; draw the symbol and the word with geom_text next to each dot.
```

## QA specifics
- [ ] Every status color has its symbol and its word; nothing is colored by status alone.
- [ ] No data series (bars, lines, cells) uses red, amber or green.
- [ ] Exceptions first; the as-of date is in the subtitle and the today line is labelled.
- [ ] A moved milestone shows the original date, an arrow and the new date; missed ones say "no new date" or the new date.
- [ ] Roll-up counts and the headline numbers come from the data, not typed.

## Inspiration
- [p047 — Bubble timeline](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p047-bubble-timeline.md) (time along the top, events as marks)
