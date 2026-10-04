# Treemaps

> **Question type:** Part-to-whole
> **Use for:** how one total splits across many parts nested in groups (function → role, business unit → job family, skill cluster → skill) · **Avoid when:** readers must compare or rank parts of similar size → use [sorted bars](bar.md)

## When to use
- To show **hierarchical part-to-whole**: one total broken into ~8–30 parts that sit inside 2–6 groups. Examples: headcount or labor cost by business unit → function, a skills portfolio by cluster → skill, gen AI-exposed capacity by function → role.
- When the message is **concentration**: "a few parts make up most of the total". Area makes the dominant tiles obvious at a glance, and nesting shows which group they belong to.
- When there are too many parts for a donut or a single stacked bar. A treemap uses the whole rectangle, so it stays readable at 20+ parts.
- As an **inline chart** in a report: a compact treemap fits one text column next to the paragraph it supports.
- **Variants:**
  - **Flat treemap:** one level only (e.g., exposed capacity by role). Use it when the grouping adds nothing.
  - **Nested treemap:** two levels, groups separated by wider white gutters. This is the default.
  - **Geographic treemap:** group blocks placed roughly where the regions sit on a map (West → East, e.g., US regions or distribution networks). Use it only when location matters more than the size sort, and say so in the subtitle.
  - **Marimekko (mosaic):** columns whose **width** is each group's size and whose **segments** show its mix (e.g., width = headcount by BU, segments = full-time / part-time / contingent). Build it as a [100% stacked bar](stacked-bar.md) with variable column widths.

## When not to use
- Readers must compare or rank parts of similar size precisely: area is hard to judge → use [sorted bars](bar.md), or a [dot plot](dot-plot-dumbbell.md) for tightly clustered values.
- ≤ 5 parts and one level → use a single [100% stacked bar](stacked-bar.md) or a [donut](donut-pie.md).
- How the mix changes over time → use a [stacked area](stacked-area.md) chart. The mix compared across several groups → use [100% stacked bars](stacked-bar.md) or [small multiples](small-multiples.md).
- Movement between categories (internal moves from one job family to another) → use a [Sankey](sankey.md).
- Any value is negative or a net change (area can't be negative) → use a [waterfall](waterfall.md) or [diverging bars](bar.md).
- The smallest parts matter but are < ~1% of the total: they become slivers no one can see or label → use [bars](bar.md), or group them into "Other".

## McKesson spec

| Element | Rule |
|---|---|
| Color | **Default: the focus pattern.** All tiles `chart.context` `#B4B0A5`; only the tile(s) the headline names in `chart.focus` `#005A8C` (≤ 2 tiles, or one whole group). Use `chart.accent` navy `#143359` for a single exception (e.g., "us" in an external benchmark). Groups are told apart by **gutters and labels, not by hue**. Color by group only when group identity *is* the message: ≤ 6 groups, categorical order (`#005A8C`, `#143359`, `#66C4FF`, `#00AF9D`, `#00737A`, then orange `#EF8200` only as a last resort), with a top-left key. If color encodes a second measure (e.g., exposure %), use the sequential blue scale (`#E6F3FB` → `#143359`) with a labelled key, and say "Size = …, color = …" in the subtitle. Never give every tile its own hue. |
| Labels | Directly **inside each tile, top-left**: the value on line 1 (label role, Bold, 12 pt / 13 px), the name on line 2 (Regular, 11 pt / 12 px). The group name goes as a small uppercase eyebrow (Semibold, 9 pt) on the group's first (largest) tile. Text color from `mv.text_on()`: white on `#005A8C` / `#143359`, Navy `#143359` on greys. If a label doesn't fit, put it **outside** with a thin leader, or list it in the footnote ("Not labelled: HR Operations 230"). Never shrink text below 9 pt / 11 px, never wrap mid-word, never add a colored label band across a tile. The unit goes in the subtitle. |
| Axes / gridlines | None. No frame, no shadow, no background fill. Use a legend only when color encodes groups or a second measure: horizontal, top-left. |
| Sort / order | **Largest top-left → smallest bottom-right**, for the groups and for the tiles inside each group (sorted squarified layout). Don't arrange tiles by org chart, alphabet or any "functional" order. The only exception is a deliberate geographic layout. Keep the group order identical across a deck. |
| Proportions | Area is **exactly proportional** to value: a parent equals the sum of its children (Plotly `branchvalues="total"`). Aim for near-square tiles (squarified layout, not long slivers). Use **consistent padding**: 1 pt white lines between tiles, ~3–4 pt white gutters between groups, and the same everywhere. The outer shape is a clean rectangle that fills its slot (16:9 slide, 4:3 half slide, one text column for print). No gaps, no tiles poking out. |
| Limits | ≤ ~30 leaf tiles and ≤ 6 groups: merge the tail into "Other" in `chart.context_light` `#DEDBD1`. Two levels on a static page; 3+ levels only with interactive drill-down. Values must all be positive. No tile built on **n < 10** people: merge it or suppress it with a footnote, including in tooltips and drill-downs. |

## Do / don't

| Do | Don't |
|---|---|
| Flow tiles from the largest at the top-left to the smallest at the bottom-right | Lay tiles out in org-chart or alphabetical order, so big and small blocks are scattered |
| Grey every tile and color only the one or two the headline names | Use a different color for each tile, or one bright hue per group "to make it pop" |
| Put value and name directly in the tile's top-left corner | Add a colored title band on top of each tile: it eats area and distorts the comparison |
| Keep thin, even white lines between tiles and slightly wider ones between groups | Leave uneven gaps or let blocks misalign with the outer edge |
| Move labels that don't fit outside the tile or into the footnote | Shrink labels to 6 pt or let them overflow into the next tile |
| State the share in the headline ("hold a third of…"), since areas are hard to read precisely | Expect readers to compare two similar tiles by eye; use bars for that |
| On live slides, build up: all-grey tiles with group labels first, then recolor the focus tiles and add the callout | Show a fully colored, fully labelled 25-tile treemap on the first click |

## Workforce examples
- **Firm, internal + external:** *Headline:* "Two customer-facing roles hold 33% of our gen AI-exposed capacity with 15% of headcount". *Subtitle:* "Estimated gen AI-exposed capacity by function and role, FY26 (FTE-equivalent)". *Data:* [`examples/data/automation_exposure.csv`](../../examples/data/automation_exposure.csv). Exposed capacity = headcount × share of task hours exposed to gen AI, from an external occupational task model mapped to internal roles. Customer Care and Claims & Billing are in focus blue, everything else grey.
- **Business unit, internal (SWP):** *Headline:* "Distribution and pharmacy roles hold 6 in 10 of the 2,900 employees eligible to retire by FY29". *Subtitle:* "Employees reaching retirement eligibility by FY29, by business unit and job family, as of Mar 2026 (headcount)". *Data:* HRIS age and service dates projected forward under the plan's eligibility rule (footnote it). Business units are the groups and job families are the tiles. The two largest families are in focus blue; families with < 10 eligible employees are merged into "Other".
- **Sector, external:** *Headline:* "Hospitals and retail pharmacy chains post 7 in 10 US pharmacy-technician openings, so they set the market we hire in". *Subtitle:* "US pharmacy technician job postings by employer sector and sub-sector, H1 2026 (thousands of postings)". *Data:* an external job-postings aggregator. The two leading sectors are in focus blue, and our own sector (wholesale and specialty distribution) is the single navy `#143359` accent tile, so readers can find us.

## Build it

### Python — matplotlib + `mckviz`
No treemap package is needed: the snippet includes a ~20-line squarified layout.
```python
# verified runnable (from the repo root)
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

import mckviz as mv

mv.use()
C = mv.colors

GROUP = {"Distribution Center Associate": "Operations", "Supply Chain Planning": "Operations",
         "Pharmacy Technician": "Pharmacy & clinical", "Specialty Nursing": "Pharmacy & clinical",
         "Customer Care": "Customer & revenue", "Claims & Billing Specialist": "Customer & revenue",
         "Sales": "Customer & revenue", "Marketing": "Customer & revenue",
         "Software Engineering": "Technology", "Data & Analytics": "Technology",
         "Finance Operations": "Corporate", "HR Operations": "Corporate"}
df = pd.read_csv(Path("examples/data/automation_exposure.csv"))
df["group"] = df.role.map(GROUP)
df["exposed_fte"] = df.headcount * df.genai_exposure_pct / 100
focus = {"Customer Care", "Claims & Billing Specialist"}
share = df.exposed_fte[df.role.isin(focus)].sum() / df.exposed_fte.sum()
hc_share = df.headcount[df.role.isin(focus)].sum() / df.headcount.sum()


def _worst(row, side):
    s = sum(row)
    return max(max(side**2 * r / s**2, s**2 / (side**2 * r)) for r in row)


def squarify(values, x, y, w, h):
    """Squarified layout. values sorted descending -> list of (x, y, w, h); the largest sits at (x, y)."""
    vals, rects = [v * w * h / sum(values) for v in values], []
    while vals:
        side, n = min(w, h), 1
        while n < len(vals) and _worst(vals[:n + 1], side) <= _worst(vals[:n], side):
            n += 1
        row, vals, s = vals[:n], vals[n:], sum(vals[:n])
        if w >= h:                                   # strip down the left edge
            cw, cy = s / h, y
            for r in row:
                rects.append((x, cy, cw, r / cw)); cy += r / cw
            x, w = x + cw, w - cw
        else:                                        # strip along the top edge
            rh, cx = s / w, x
            for r in row:
                rects.append((cx, y, r / rh, rh)); cx += r / rh
            y, h = y + rh, h - rh
    return rects


fig, ax = plt.subplots(figsize=(10, 5.6))
fig.subplots_adjust(left=0.03, right=0.97)
box = ax.get_position()
PT = box.width * fig.get_figwidth() * 72 / 100                    # points per layout unit
W, H = 100, box.height * fig.get_figheight() * 72 / PT             # square units, so squares look square
ax.set_xlim(0, W)
ax.set_ylim(H, 0)                                                  # y runs down: largest tile lands top-left
ax.axis("off")

unlabelled = []
groups = df.groupby("group").exposed_fte.sum().sort_values(ascending=False)
for (gx, gy, gw, gh), g in zip(squarify(groups.tolist(), 0, 0, W, H), groups.index):
    kids = df[df.group == g].sort_values("exposed_fte", ascending=False)
    for i, ((x, y, w, h), r) in enumerate(zip(squarify(kids.exposed_fte.tolist(), gx, gy, gw, gh), kids.itertuples())):
        fill = C.focus if r.role in focus else C.context
        ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec="white", lw=1))
        name = textwrap.fill(r.role, max(1, int((w * PT - 10) / 5)), break_long_words=False)
        lines = ([(g.upper(), 7.5, "semibold")] if i == 0 else []) + [(f"{r.exposed_fte:,.0f}", 11, "bold"),
                                                                       (name, 9, "normal")]
        fits = (max(len(s) * z * 0.54 for t, z, _ in lines for s in t.split("\n")) < w * PT - 8
                and sum(z * 1.25 * (t.count("\n") + 1) for t, z, _ in lines) < h * PT - 6)
        if not fits:                                               # never squeeze or overflow a label
            unlabelled.append(f"{r.role} {r.exposed_fte:,.0f}")
            continue
        dy = -5
        for text, size, weight in lines:
            ax.annotate(text, (x, y), xytext=(5, dy), textcoords="offset points", va="top", ha="left",
                        fontsize=size, fontweight=weight, color=mv.text_on(fill), linespacing=1.1)
            dy -= size * 1.25 * (text.count("\n") + 1)
    ax.add_patch(Rectangle((gx, gy), gw, gh, fc="none", ec="white", lw=4))   # wider gutter between groups

mv.titles(fig, f"Two customer-facing roles hold {share:.0%} of our gen AI-exposed capacity with {hc_share:.0%} of headcount",
          "Estimated gen AI-exposed capacity by function and role, FY26 (FTE-equivalent)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Exposed capacity = headcount \u00d7 share of task hours exposed to gen AI (external task model mapped to "
                   "internal roles). Tile area is proportional to value."
                   + (f"\nNot labelled (too small): {'; '.join(unlabelled)}." if unlabelled else ""))
mv.save(fig, "out/treemap-exposure.png", dpi=200)
```
For a **flat** treemap, call `squarify()` once on all roles, sorted descending. For a **slice-and-dice** layout (groups as side-by-side columns, children stacked inside each), replace the `if w >= h` test with a fixed direction per level: columns for groups, rows for children. It reads in a predictable order but produces slivers once a group has more than ~4 children. To color by group instead of focus, map `group → mv.categorical(n)` and add a top-left key.

### Python — Plotly / HTML
```python
# verified: builds without error
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()  # registers + activates the "mck" Plotly template
C = mv.colors

GROUP = {"Distribution Center Associate": "Operations", "Supply Chain Planning": "Operations",
         "Pharmacy Technician": "Pharmacy & clinical", "Specialty Nursing": "Pharmacy & clinical",
         "Customer Care": "Customer & revenue", "Claims & Billing Specialist": "Customer & revenue",
         "Sales": "Customer & revenue", "Marketing": "Customer & revenue",
         "Software Engineering": "Technology", "Data & Analytics": "Technology",
         "Finance Operations": "Corporate", "HR Operations": "Corporate"}
df = pd.read_csv(Path("examples/data/automation_exposure.csv"))
df["group"] = df.role.map(GROUP)
df["exposed_fte"] = (df.headcount * df.genai_exposure_pct / 100).round()
focus = {"Customer Care", "Claims & Billing Specialist"}

grp = df.groupby("group", as_index=False).agg(exposed_fte=("exposed_fte", "sum"), headcount=("headcount", "sum"))
ids = list(grp.group) + list(df.role)
fig = go.Figure(go.Treemap(
    ids=ids, labels=ids,
    parents=[""] * len(grp) + list(df.group),
    values=list(grp.exposed_fte) + list(df.exposed_fte),
    branchvalues="total",                              # parent value = sum of children, so areas stay honest
    sort=True, tiling={"packing": "squarify", "pad": 0},
    marker={"colors": ["rgba(0,0,0,0)"] * len(grp) + mv.pl_highlight(df.role, focus=focus),
            "line": {"color": "white", "width": 1}, "pad": {"t": 22, "l": 0, "r": 0, "b": 0}},
    customdata=list(grp.headcount) + list(df.headcount),
    texttemplate="<b>%{value:,.0f}</b><br>%{label}", textposition="top left",
    hovertemplate="<b>%{label}</b><br>%{value:,.0f} exposed FTE<br>%{customdata:,} employees"
                  "<br>%{percentRoot:.0%} of total<extra></extra>",
    pathbar={"visible": False}, root={"color": "white"}))
fig.update_traces(textfont={"size": 13, "color": [C.headline] * len(grp)
                            + [mv.text_on(c) for c in mv.pl_highlight(df.role, focus=focus)]})
fig.update_layout(uniformtext={"minsize": 10, "mode": "hide"})   # hide labels rather than shrink them
mv.pl_finish(fig, "Two customer-facing roles hold 33% of our gen AI-exposed capacity with 15% of headcount",
             "Estimated gen AI-exposed capacity by function and role, FY26 (FTE-equivalent)",
             "Source: Synthetic data for illustration only",
             footnote="Exposed capacity = headcount \u00d7 share of task hours exposed to gen AI. Tile area is proportional to value.")
fig.update_layout(margin={"l": 24, "r": 24, "t": 110})
Path("out").mkdir(exist_ok=True)
fig.write_html("out/treemap-exposure.html", include_plotlyjs="cdn")
```
The group names sit in a thin white header strip (`marker.pad.t`) above each group rather than in a colored band. Keep `pad.t` the same for every group. For an exploratory version, set `maxdepth=2`, turn `pathbar` back on and let readers click into a group. `px.treemap(df, path=["group", "role"], values="exposed_fte")` is a quicker start, but the explicit `go.Treemap` above gives direct control over each node's color and text. Never expose tiles or hover headcounts for groups with n < 10.

### Excel and PowerPoint
1. Install the **McKesson Data Viz** theme colors and fonts once, as described in [bar.md](bar.md#excel-and-powerpoint), then apply them (**Page Layout › Colors / Fonts**; in PowerPoint **Design › Variants › Colors / Fonts**).
2. Lay the data out as one row per leaf with columns **Group | Item | Value**, sorted by group and then by value (descending). Repeat the group name on every row: no merged or blank cells.
3. Select the table, then **Insert › Charts › Insert Hierarchy Chart › Treemap** (Microsoft 365 / Office 2016+). Excel squarifies and sorts the tiles automatically, with the largest at the top-left. Check this, but don't try to reorder tiles by hand.
4. Right-click a tile › **Format Data Series › Series Options › Label Options**: choose **Overlapping** (the group name sits on its largest tile) or **None**. Avoid **Banner**: it adds a header band to every group that eats tile area.
5. With the whole series selected: **Fill › Solid fill › More Colors › Hex B4B0A5** and **Border › Solid line, White, 1 pt**. Then click a focus tile a second time so only that point is selected and set **Fill › Hex 005A8C** (or `143359` for the single navy accent). Excel can't give groups a wider gutter than tiles, so keep the border at 1–1.5 pt everywhere.
6. **Chart Elements (+) › Data Labels**, then **Format Data Labels › Label Contains: Category Name + Value**, with **Separator: (New Line)**. Use Libre Franklin 11–12 pt in Navy `#143359`. Select the labels on blue tiles one at a time and set them to white. Delete any label that is clipped, and name that tile in the footnote.
7. Delete the chart title and the legend (the legend lists groups only when color encodes groups). Set **Format Chart Area › Border: No line**.
8. In PowerPoint, use **Insert › Chart › Treemap** for a native chart, or copy from Excel and **Home › Paste › Use Destination Theme & Embed Workbook**. Put the headline in the slide title (26 pt Bold McKesson Blue `#005A8C`) and the subtitle at 14 pt `#505050`, with the source at 9 pt Libre Franklin Light `#737373`, bottom-left. Treemaps need Office 2016 or later; older versions show a static picture.
9. Build-up: duplicate the slide. Step 1: all tiles grey with group labels. Step 2: the focus tiles recolored, with a short callout ("33% of exposed capacity").

### Power BI
- Import [`dist/powerbi/mckesson-dataviz-theme.json`](../../dist/powerbi/mckesson-dataviz-theme.json) via **View › Themes › Browse for themes**.
- Use the **Treemap** visual with **Category** = Function, **Details** = Role and **Values** = the measure. Power BI sorts the largest tiles to the top-left. Turn **Data labels** and **Category labels** on and the **Legend** off.
- Focus pattern: conditional color (**Format › Colors › fx**, Format style *Field value*) is available only when **Details** is empty. For a role-level highlight, put Role in **Category**, move Function to **Tooltips**, and use a measure such as `Tile Color = IF(SELECTEDVALUE(Roles[Role]) IN {"Customer Care", "Claims & Billing Specialist"}, "#005A8C", "#B4B0A5")`. Keep the two-level layout only when you color by group.
- Minimum n: `Exposed FTE (safe) = IF([Headcount] < 10, BLANK(), [Exposed FTE])`, so the tiles, tooltips and drill-through all inherit it.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr); library(readr)
library(treemapify)                                   # install.packages("treemapify")
source("dist/r/theme_mck.R")

grp <- c("Distribution Center Associate" = "Operations", "Supply Chain Planning" = "Operations",
         "Pharmacy Technician" = "Pharmacy & clinical", "Specialty Nursing" = "Pharmacy & clinical",
         "Customer Care" = "Customer & revenue", "Claims & Billing Specialist" = "Customer & revenue",
         "Sales" = "Customer & revenue", "Marketing" = "Customer & revenue",
         "Software Engineering" = "Technology", "Data & Analytics" = "Technology",
         "Finance Operations" = "Corporate", "HR Operations" = "Corporate")
focus <- c("Customer Care", "Claims & Billing Specialist")

df <- read_csv("examples/data/automation_exposure.csv") |>
  mutate(group = grp[role], exposed_fte = headcount * genai_exposure_pct / 100,
         fill = ifelse(role %in% focus, mck_colors$focus, mck_colors$context),
         ink  = ifelse(role %in% focus, "white", mck_colors$headline)) |>
  group_by(group) |> arrange(desc(exposed_fte), .by_group = TRUE) |>
  mutate(label = paste0(scales::comma(exposed_fte), "\n", role),
         label = ifelse(row_number() == 1, paste0(toupper(group), "\n", label), label)) |>   # group name on its largest tile
  ungroup()

ggplot(df, aes(area = exposed_fte, subgroup = group, fill = fill, label = label)) +
  geom_treemap(layout = "squarified", start = "topleft", colour = "white", linewidth = 1) +
  geom_treemap_subgroup_border(layout = "squarified", start = "topleft", colour = "white", linewidth = 4) +
  geom_treemap_text(aes(colour = ink), layout = "squarified", start = "topleft", place = "topleft",
                    family = "Libre Franklin", size = 10, reflow = TRUE, min.size = 9,   # hide, don't shrink
                    padding.x = grid::unit(2, "mm"), padding.y = grid::unit(2, "mm")) +
  scale_fill_identity() + scale_colour_identity() +
  labs(title = "Two customer-facing roles hold 33% of our gen AI-exposed capacity with 15% of headcount",
       subtitle = "Estimated gen AI-exposed capacity by function and role, FY26 (FTE-equivalent)",
       caption = "Exposed capacity = headcount x share of task hours exposed to gen AI.\nSource: Synthetic data for illustration only") +
  theme_mck() +
  theme(panel.grid = element_blank(), axis.text = element_blank(), axis.line.x = element_blank())
```
`start = "topleft"` keeps the largest tile at the top-left. Use the same `layout` and `start` in every `geom_treemap_*` layer so the borders and text line up with the tiles.

## QA specifics
- [ ] Tile areas are proportional to the values, each parent equals the sum of its children, and all values are positive. The headline's share ("33%") is recomputed from the data.
- [ ] Tiles flow from the largest at the top-left to the smallest at the bottom-right, for both groups and items. The group order is the same as elsewhere in the deck.
- [ ] Only the tile(s) the headline names are colored (≤ 2, or one group), and the rest are context grey. There are no per-tile rainbow colors or colored label bands.
- [ ] Every label sits inside its tile, top-left, at ≥ 9 pt / 11 px, with readable contrast. Labels that don't fit are placed outside or listed in the footnote, never clipped.
- [ ] Padding is even (1 pt between tiles, a slightly wider gutter between groups), and the outer edge is a clean rectangle with no gaps.
- [ ] ≤ ~30 tiles and ≤ 2 levels on static output. No tile, tooltip or drill-down is based on fewer than 10 people.

## Inspiration
- [p040 — Treemap](../../reference/inspiration-mckinsey/pages/p040-treemap.md)
- [p041 — Treemap variants](../../reference/inspiration-mckinsey/pages/p041-treemap-variants.md)
- [p042 — Treemap best practice](../../reference/inspiration-mckinsey/pages/p042-treemap-best-practice.md)
- [p086 — Print (inline charts)](../../reference/inspiration-mckinsey/pages/p086-print.md)
