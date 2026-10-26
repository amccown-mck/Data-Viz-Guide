# Sankey diagram

> **Question type:** Relationships & flows
> **Use for:** showing how a volume of people moves between states or stages and where the big transfers and leaks are · **Avoid when:** nothing branches or you only need conversion rates → use a [bar](bar.md) chart (funnel) instead

## When to use
- People move **from one set of states to another**, and the story is about the **dominant paths** or the **leakage**: internal mobility between job families, hiring source → role family, reskilling or hiring pipelines (nominated → enrolled → completed → redeployed).
- Volumes are **conserved**: what flows into a node flows out (or exits are shown as their own nodes).
- You have **2–4 stages** and a handful of nodes per stage, and a few flows are much bigger than the rest. The chart's job is to make those big flows obvious.

## When not to use
- A single linear pipeline with no branching (applicants → screened → offered → hired) → use a sorted [bar](bar.md) chart or funnel with conversion rates.
- Many-to-many flows where most cells are small (e.g., 15 × 15 job-family moves) → use a [heatmap](heatmap.md) origin × destination matrix.
- Change of a single total over time → use a [line](line.md) chart. Composition at one stage → use a [100% stacked bar](stacked-bar.md).
- Readers need exact values for every flow → use a [table](tables.md) and keep the Sankey for the main point.
- Overlapping memberships (people in more than one group at once) → use a [Venn](venn.md); Sankeys assume each person sits in exactly one node per stage.

## McKesson spec

| Element | Rule |
|---|---|
| Color | Color **transfer type** (or origin), not stage, and keep it the same at every step. Default: main path `chart.focus` `#005A8C`, other flows `chart.context` `#B4B0A5`, the one exception the headline names `chart.accent` navy `#143359`, or `semantic.negative` orange `#EF8200` when that exception is a loss or leak (people who drop out or aren't placed). Orange only ever means worse. Links are **semi-transparent** (opacity 0.45–0.65) so crossings stay visible. Nodes are thin bars in `chart.total` `#143359`. If you must tell origins apart, use the first 2–3 `color.categorical` values, never a rainbow. |
| Labels | Put the node name and value right next to the node (`Completed  840`). Use plain numbers with thousands separators and no boxes. Bold stage headers (Nominated · Enrolled · …) go above each column. The unit goes in the subtitle. Hover shows `source → target: value`. |
| Axes / gridlines | None. No frame, no background fill. |
| Sort / order | Stages run left → right in process order. Within a column, keep the main path together and the exits/leakage at the edge. Keep the same node order on every slide of a build-up. |
| Proportions | Band width ∝ value on **one shared scale**. Inflow = outflow at every intermediate node. Exits are explicit nodes, not silently dropped. |
| Limits | ≤ 4 stages, ≤ ~8 nodes per column, ≤ 3 link colors, ≤ 2 highlighted paths. **Every node and flow must be n ≥ 10.** Merge smaller flows into "Other" (context grey) and footnote it. |

## Do / don't

| Do | Don't |
|---|---|
| Give each transfer *type* one color (progressed / dropped / not placed) and reuse it at every step | Recolor each stage. The stage split is already obvious, so the color says nothing |
| Highlight the headline path in blue and push the rest to grey | Draw every flow in one dark color. Crossing paths become impossible to trace |
| Keep curved, organic bands and mark nodes with thin vertical bars | Box the values between steps or straighten flows into angular arrows |
| Use transparency so overlapping bands show through | Use flat opaque fills that hide smaller flows behind big ones |
| Show exits and leakage as named nodes with values | Let volumes vanish between stages with no explanation |
| Merge flows under 10 people into "Other" | Show a 3-person move between two small teams. It identifies individuals |

## Workforce examples
- **Headline:** "DC Associates made 440 internal moves in two years; 6 in 10 were promotions into DC leadership" — *Subtitle:* "Internal moves between job families, trailing 24 months (number of moves)" — data: Workday job-change events, `examples/data/mobility_flows.csv`. DC Associate flows are in focus blue and all others in grey (built in `examples/python/gallery_plotly.py`). Firm level, internal signal.
- **Headline:** "Referrals and internal moves fill 6 in 10 specialty-pharmacy roles but fewer than 1 in 5 Customer Care roles" — *Subtitle:* "Filled requisitions by hiring source and job family, FY26 (hires)" — data: ATS requisition source joined to Workday hires. Sources with fewer than 10 hires per family are merged into "Other". Team/function level, internal and external sourcing channels.
- **Headline:** "Most pharmacy technicians who leave distribution move to retail pharmacy, not to direct competitors" — *Subtitle:* "Next employer type for pharmacy technicians leaving U.S. healthcare-distribution employers, 2024–2026 (% of transitions)" — data: external labor-market profile-transition data (aggregated by the provider; cells under the provider's minimum suppressed). Sector level, external signal.

## Build it

### Python — matplotlib + `mckviz`
Primary route for slides, PNG and PDF. `mv.sankey` draws the spec in one call: curved semi-transparent bands on one shared scale, thin navy nodes, each node's name and total beside it, and grey context with the headline's flows in color. It refuses flows under 10 people. Columns come from the flows, so list each stage's main path first and the exits last to keep them at the bottom edge. Don't use `matplotlib.sankey`: it draws engineering-style single-node diagrams with straight arrows.

```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
flows = pd.read_csv("examples/data/reskilling_pipeline.csv")    # from_stage, to_stage, people, transfer
completed = flows.people[flows.to_stage == "Completed"].sum()
not_placed = flows.people[flows.transfer == "not_placed"].sum()
assert not_placed / completed > 0.5                              # the headline's claim, from the data

fig, ax = plt.subplots(figsize=(10, 5.6))
# One color per transfer TYPE, reused at every step: progressed blue, the leak the headline names orange
# (it is a loss), everything else grey. Pass-through nodes are labeled above, so the next column stays clear.
mv.sankey(ax, flows, focus={"progressed"}, worse={"not_placed"},
          stages=("Nominated", "Enrolled", "Completed", "Outcome"))
mv.titles(fig, "Half of reskilling graduates are not redeployed: placement, not training, is the biggest leak",
          "Data & AI reskilling academy, FY25–FY26 cohorts (people)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Blue = progressed to the next stage; orange = completed but not placed in a data role.")
mv.lint(fig, strict=True)
mv.save(fig, "out/sankey-reskilling.png", dpi=200)
```

`focus=`, `worse=` and `accent=` take transfer kinds (the optional fourth column) or node names, so `focus={"DC Associate"}` colors every flow in or out of that job family. The function returns the node positions (`.nodes`) for any extra annotation.

### Python — Plotly / HTML
For interactive web pages, where hover shows each flow. In this example the headline names the "not placed" leak, a loss, so it is the one flow in orange (`C.negative`). The `snap` arrangement lets Plotly place nodes. It may stack the exits at the top. That's fine as long as no bands cross needlessly.

```python
# verified runnable (from the repo root)
import tempfile
from pathlib import Path

import plotly.graph_objects as go

import mckviz as mv

mv.use()
C = mv.colors


def rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


# Reskilling pipeline: (from, to, people, transfer type). Every cell is n >= 10.
flows = [
    ("Nominated", "Enrolled", 1010, "progressed"), ("Nominated", "Declined", 190, "dropped"),
    ("Enrolled", "Completed", 840, "progressed"), ("Enrolled", "Withdrew", 170, "dropped"),
    ("Completed", "Redeployed to data role", 410, "progressed"),
    ("Completed", "Returned to prior role", 350, "not_placed"),
    ("Completed", "Left McKesson", 80, "not_placed"),
]
# One color per transfer TYPE, reused at every step; semi-transparent so overlaps stay visible.
link_color = {"progressed": rgba(C.focus, 0.55), "dropped": rgba(C.context, 0.45), "not_placed": rgba(C.negative, 0.65)}

nodes = list(dict.fromkeys(n for f in flows for n in f[:2]))
idx = {n: i for i, n in enumerate(nodes)}
size = {n: sum(v for s, t, v, _ in flows if t == n) or sum(v for s, t, v, _ in flows if s == n) for n in nodes}

fig = go.Figure(go.Sankey(
    arrangement="snap", valueformat=",",
    textfont={"size": 12, "color": C.headline},
    node={"label": [f"{n}  {size[n]:,}" for n in nodes], "color": C.total, "thickness": 6, "pad": 24,
          "line": {"width": 0}, "hovertemplate": "%{label}<extra></extra>"},
    link={"source": [idx[s] for s, *_ in flows], "target": [idx[t] for _, t, *_ in flows],
          "value": [v for *_, v, _ in flows], "color": [link_color[k] for *_, k in flows],
          "hovertemplate": "%{source.label} \u2192 %{target.label}: %{value:,} people<extra></extra>"},
))
for x, stage in ((0, "Nominated"), (0.335, "Enrolled"), (0.665, "Completed"), (1, "Outcome")):
    fig.add_annotation(x=x, y=1.02, xref="paper", yref="paper", yanchor="bottom", showarrow=False,
                       text=f"<b>{stage}</b>", font={"size": 12, "color": C.text},
                       xanchor={0: "left", 1: "right"}.get(x, "center"))

not_placed = size["Returned to prior role"] + size["Left McKesson"]
assert not_placed / size["Completed"] > 0.5  # headline claim: "half ... not redeployed"
mv.pl_finish(
    fig,
    "Half of reskilling graduates are not redeployed \u2013 placement, not training, is the biggest leak",
    "Data & AI reskilling academy, FY25\u2013FY26 cohorts (people); blue = progressed, orange = completed but not placed",
    source_text="Source: Learning records and Workday HCM, as of 31 Mar 2026; synthetic data for illustration",
)
fig.update_layout(height=500, margin={"l": 16, "r": 16, "t": 120})
fig.write_html(Path(tempfile.gettempdir()) / "sankey_reskilling.html", include_plotlyjs="cdn")
```

- For web pages, use the chart-card pattern: headline, subtitle and source in HTML, and the figure via `fig.to_html(full_html=False)`. See `card()` in `examples/python/gallery_plotly.py` and the styles in [`dist/web/mck-viz.css`](../../dist/web/mck-viz.css).
- To pin columns, pass `node.x` / `node.y` (0–1) with `arrangement="fixed"`. Then check that bands don't cross, because Plotly may keep its original link order.

### Excel and PowerPoint
1. Excel and PowerPoint (Microsoft 365) have **no native Sankey**. Build it in Python/HTML (above) and export with `fig.write_image("sankey.svg")`, or take a screenshot of the HTML card.
2. PowerPoint: **Insert → Pictures → This Device** → choose the SVG. To edit labels, select it and use **Graphics Format → Convert to Shape**. Set label text to **Libre Franklin** (Regular 12 pt, values Medium).
3. Put the headline in the slide title. Add the subtitle (Libre Franklin Regular 14 pt, `#505050`) and the source (Light 9 pt, `#737373`) as text boxes, bottom-left.
4. For a **linear pipeline with no branches**, use a native chart instead: **Insert → Insert Waterfall, Funnel… → Funnel**. Recolor the bars via **Format Data Point → Fill → Solid fill**: `#005A8C` for the focus stage, `#B4B0A5` for the rest.
5. For a build-up, duplicate the slide. On step 1, recolor all flows to `#DEDBD1`, then reveal the focus path in blue on the next slide. Keep node positions identical.
6. Put the exact flow table in the appendix or speaker notes.

### Power BI
- Apply the theme: **View → Themes → Browse for themes →** `dist/powerbi/mckesson-dataviz-theme.json`.
- There is no built-in Sankey. The AppSource **Sankey chart** custom visual works for exploration. Before you use it, check that it's on your tenant's approved/certified list (uncertified visuals can't be exported to PPT/PDF in some tenants). It has limited styling: set link colors by hand and expect it to ignore some theme settings.
- Enforce minimum n before the visual. Group small flows into "Other" in Power Query, then blank anything left: `Moves (safe) = VAR n = SUM(Mobility[moves]) RETURN IF(n < 10, BLANK(), n)`. Blanking alone silently drops volume, so footnote it.
- For linear pipelines, use the native **Funnel** visual with focus/context conditional colors.

### R — ggplot2 (optional)
```r
library(ggplot2)
library(ggalluvial)   # optional package for alluvial/Sankey-style flows
source("dist/r/theme_mck.R")

paths <- data.frame(
  nominated = "Nominated",
  enrolment = c("Enrolled", "Enrolled", "Enrolled", "Enrolled", "Declined"),
  course    = c("Completed", "Completed", "Completed", "Withdrew", "Declined"),
  outcome   = c("Redeployed", "Returned to prior role", "Left McKesson", "Withdrew", "Declined"),
  people    = c(410, 350, 80, 170, 190),
  type      = c("progressed", "not_placed", "not_placed", "dropped", "dropped")
)

ggplot(paths, aes(axis1 = nominated, axis2 = enrolment, axis3 = course, axis4 = outcome, y = people)) +
  geom_alluvium(aes(fill = type), alpha = 0.6, width = 1/20, knot.pos = 0.4) +
  geom_stratum(width = 1/20, fill = mck_colors$total, color = NA) +
  geom_text(stat = "stratum", aes(label = paste(after_stat(stratum), scales::comma(after_stat(count)))),
            hjust = 0, nudge_x = 0.04, size = 3.4, color = mck_colors$headline) +
  scale_x_discrete(limits = c("Nominated", "Enrolled", "Completed", "Outcome"), position = "top") +
  scale_fill_manual(values = c(progressed = mck_colors$focus, dropped = mck_colors$context,
                               not_placed = mck_colors$negative), guide = "none") +
  labs(title = "Half of reskilling graduates are not redeployed",
       subtitle = "Data & AI reskilling academy, FY25–FY26 cohorts (people)",
       caption = "Source: Learning records and Workday HCM; synthetic data", x = NULL, y = NULL) +
  theme_mck() +
  theme(axis.text.y = element_blank(), panel.grid = element_blank(), axis.line.x = element_blank())
```

## QA specifics
- [ ] Flows are conserved: inflow = outflow at every intermediate node, and every exit is a named node with a value.
- [ ] Every node and flow is **n ≥ 10**. Smaller flows are merged into "Other" and footnoted, and tooltips don't reveal suppressed cells.
- [ ] Color encodes transfer type (or origin) and is identical at every step. ≤ 3 link colors, and the colored path is the one the headline names.
- [ ] Links are semi-transparent and no flow is fully hidden behind another.
- [ ] Node labels show name + value with no boxes. Stage headers are present and the unit is in the subtitle.
- [ ] The headline number is recomputed from the flows (e.g., 430 of 840 graduates not placed = 51%).

## Inspiration
- [p056 — Sankey diagram](../../reference/inspiration-mckinsey/pages/p056-sankey-diagram.md)
- [p057 — Sankey diagram best practice](../../reference/inspiration-mckinsey/pages/p057-sankey-diagram-best-practice.md)
