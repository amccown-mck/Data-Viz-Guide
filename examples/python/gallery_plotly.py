"""Interactive reference charts (Plotly) assembled into one self-contained HTML page of McKesson chart cards.

    python examples/python/gallery_plotly.py   -> examples/output/gallery.html

Pattern: headline / subtitle / source live in HTML (crisp, responsive typography); the Plotly figure carries
only the data. Styling comes from dist/web/mck-viz.css (inlined) and the "mck" Plotly template.
"""
import html
import itertools
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.io.json import to_json_plotly
from plotly.offline import get_plotlyjs_version

import mckviz as mv

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "examples" / "data"
OUT = ROOT / "examples" / "output"
SRC = "Source: Synthetic data for illustration only"
mv.use()
C = mv.colors
PLOT_CFG = {"displayModeBar": False, "responsive": True}
_ids = itertools.count(1)                                  # stable div ids: the page rebuilds byte-identically


PHONE_MAX = 600                                            # px; matches the @media breakpoint in mck-viz.css


def text_px(text: str, size: float, bold: bool = False) -> int:
    """Rough rendered width of a label in Libre Franklin (average glyph ~0.55 em, bold ~0.6 em)."""
    return round(len(text) * size * (0.6 if bold else 0.55))


def wrap(label: str, max_chars: int = 18) -> str:
    """Break a long category name at the space nearest its middle (phone tick labels)."""
    if len(label) <= max_chars or " " not in label:
        return label
    mid = len(label) / 2
    cut = min((i for i, ch in enumerate(label) if ch == " "), key=lambda i: abs(i - mid))
    return label[:cut] + "<br>" + label[cut + 1:]


def responsive(fig, aria, desktop=None, phone=None):
    """Attach the card's screen-reader label and its desktop/phone switches to the figure (read and removed by card()).

    desktop / phone: {"height": px, "relayout": {...}, "restyle": {...}}, applied after the first draw and whenever the
    viewport crosses PHONE_MAX, like fit() in templates/html/chart-card.html.
    """
    fig.update_layout(meta={"aria": aria, "fit": {"desktop": desktop or {}, "phone": phone or {}}})
    return fig


def card(fig, headline, subtitle, source, footnote=None, dark=False) -> str:
    meta = fig.layout.meta or {}
    fig.layout.meta = None
    fit = meta.get("fit", {"desktop": {}, "phone": {}})
    aria = f"{headline}. {meta['aria']}" if meta.get("aria") else headline
    margin = {"t": 36, "l": 8, "r": 8, "b": 8}
    margin.update({k: v for k in margin if (v := fig.layout.margin[k]) is not None})   # keep chart-specific margins
    fig.update_layout(margin=margin, autosize=True)
    # Draw only after Libre Franklin has loaded: Plotly caches label widths from the first render, so a plot drawn
    # with the fallback font keeps margins that clip the real labels (e.g. long bold category names).
    div_id = f"chart-{next(_ids)}"
    spec = fig.to_json().replace("</", "<\\/")                 # keep "</" from closing the <script> early
    height = fit["desktop"].get("height", 440)
    body = (f'<div id="{div_id}" style="height:{height}px; width:100%;"></div>\n'
            f'<script>mckDraw("{div_id}", {spec}, {to_json_plotly(fit).replace("</", "<\\/")});</script>')
    notes = "<br>".join(html.escape(x) for x in (footnote, source) if x)
    return f"""
<figure class="mck-chart{' mck-chart--dark' if dark else ''}">
  <h2 class="mck-headline">{html.escape(headline)}</h2>
  <p class="mck-subtitle">{html.escape(subtitle)}</p>
  <div class="mck-plot" role="img" aria-label="{html.escape(aria)}">{body}</div>
  <figcaption class="mck-footnote">{notes}</figcaption>
</figure>"""


def bar_highlight():
    df = pd.read_csv(DATA / "attrition_by_job_family.csv").sort_values("vol_attrition_pct")
    ent = df.enterprise_rate_pct.iloc[0]
    focus = df.job_family[df.vol_attrition_pct > 20]
    fig = go.Figure(go.Bar(
        x=df.vol_attrition_pct, y=df.job_family, orientation="h", marker_color=mv.highlight(df.job_family, focus=focus),
        text=[f" {v:.1f}%" for v in df.vol_attrition_pct], textposition="outside", cliponaxis=False,
        customdata=df.headcount, hovertemplate="%{y}<br>%{x:.1f}% attrition<br>%{customdata:,} employees<extra></extra>"))
    fig.add_vline(x=ent, line={"color": C.annotation, "width": 1, "dash": "dot"}, layer="below")
    fig.add_annotation(x=ent, y=1, yref="paper", yanchor="bottom", text=f"Enterprise {ent:.1f}%", font={"size": 12})
    # The value labels hang off the bar ends into the right margin (cliponaxis=False), so size that margin from the
    # longest label instead of padding the axis range: it then fits at any width, 390 px phones included.
    lab = mv.TOKENS["typography"]["roles"]["label"]["size_px"]
    fig.update_xaxes(visible=False, range=[0, df.vol_attrition_pct.max()])
    fig.update_layout(margin_r=max(text_px(t, lab) for t in fig.data[0].text) + 8)
    ticktext = [f"<b>{j}</b>" if j in set(focus) else j for j in df.job_family]   # echo the highlight
    fig.update_yaxes(showgrid=False, showline=False, ticklabelstandoff=8, automargin=True, tickvals=df.job_family,
                     ticktext=ticktext)
    top = df.sort_values("vol_attrition_pct", ascending=False)
    responsive(fig, f"{top.job_family.iloc[0]} {top.vol_attrition_pct.iloc[0]:.1f}% and {top.job_family.iloc[1]} "
                    f"{top.vol_attrition_pct.iloc[1]:.1f}%; the other job families range from "
                    f"{top.vol_attrition_pct.min():.1f}% to {top.vol_attrition_pct.iloc[2]:.1f}%.",
               desktop={"height": 440, "relayout": {"yaxis.ticktext": ticktext}},
               phone={"height": 480, "relayout": {"yaxis.ticktext": [wrap(t) for t in ticktext]}})   # long names on 2 lines
    return card(fig, f"Two frontline job families lose about 1 in 4 people a year, well above the {ent:.1f}% enterprise rate",
                "Voluntary attrition by job family, FY26 (%)", SRC,
                "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.")


def line_gap():
    df = pd.read_csv(DATA / "data_ai_supply_demand.csv")
    fig = go.Figure()
    fig.add_scatter(x=df.year, y=df.internal_supply_fte, name="Internal supply", line_color=C.focus, mode="lines",
                    hovertemplate="%{y:,} FTE<extra>Internal supply</extra>")
    fig.add_scatter(x=df.year, y=df.demand_fte, name="Demand", line_color=C.navy, mode="lines", fill="tonexty",
                    fillcolor=mv.rgba(C.negative, 0.12), hovertemplate="%{y:,} FTE<extra>Demand</extra>")
    # Direct labels to the RIGHT of the line ends (clear of the steep demand line), as in the chart-card template.
    end = df.iloc[-1]
    gap = int(end.demand_fte - end.internal_supply_fte)
    for y, col, text in ((end.demand_fte, C.navy, f"<b>Demand</b> {end.demand_fte:,.0f}"),
                         (end.internal_supply_fte, C.focus, f"<b>Internal supply</b> {end.internal_supply_fte:,.0f}"),
                         ((end.demand_fte + end.internal_supply_fte) / 2, C.negative_text, f"<b>Gap {gap:,} FTE</b><br>by 2030")):
        fig.add_annotation(x=end.year, y=y, text=text, xanchor="left", xshift=8, align="left", font={"color": col, "size": 13})
    fig.update_layout(showlegend=False, hovermode="x unified", margin_r=150, legend_traceorder="reversed")
    fig.update_yaxes(range=[750, df.demand_fte.max() * 1.08], dtick=200, tickformat=",")
    fig.update_xaxes(tickvals=df.year, ticktext=[str(y) for y in df.year], tickangle=0, range=[df.year.iloc[0], df.year.iloc[-1]])
    # Phones: the end labels would squeeze the plot, so swap them for a compact key on top (template fit()).
    responsive(fig, f"Demand grows from {df.demand_fte.iloc[0]:,.0f} FTE in {df.year.iloc[0]} to {end.demand_fte:,.0f} in "
                    f"{end.year:.0f}; internal supply reaches {end.internal_supply_fte:,.0f}, a gap of {gap:,} FTE.",
               desktop={"relayout": {"showlegend": False, "annotations": [a.to_plotly_json() for a in fig.layout.annotations],
                                     "margin.r": 150}},
               phone={"relayout": {"showlegend": True, "annotations": [], "margin.r": 16}})
    return card(fig, f"Without action, Data & AI demand outruns internal supply by ~{round(gap, -1):,} FTE by 2030",
                "Forecast Data & AI roles, FTE, 2024\u20132030 (base scenario)", SRC,
                "Supply = current headcount \u2212 projected attrition + planned internal moves; excludes external hiring.")


def bubble_scatter():
    df = pd.read_csv(DATA / "automation_exposure.csv")
    focus = df.genai_exposure_pct >= 50
    fig = go.Figure(go.Scatter(
        x=df.median_pay_k, y=df.genai_exposure_pct, mode="markers+text", text=[r if f else "" for r, f in zip(df.role, focus)],
        textposition="middle right", textfont={"color": C.headline, "size": 12},
        marker={"size": df.headcount, "sizemode": "area", "sizeref": 2 * df.headcount.max() / 60 ** 2,
                "color": mv.highlight(df.role, focus=df.role[focus]), "line": {"color": "white", "width": 1}, "opacity": 0.9},
        customdata=df[["role", "headcount"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{y}% of task hours exposed<br>$%{x}K median pay<br>%{customdata[1]:,} people<extra></extra>"))
    fig.add_hrect(y0=50, y1=75, fillcolor=C.surface_subtle, line_width=0, layer="below")
    fig.add_annotation(x=0, xref="paper", y=74, yanchor="top", xanchor="left", text="<b>High exposure: 50%+ of task hours</b>",
                       font={"size": 11})
    fig.update_xaxes(title="Median base pay ($K)", range=[28, 155], tickprefix="$", ticksuffix="K")
    fig.update_yaxes(title="", range=[0, 75], ticksuffix="%")
    hi = df[focus].sort_values("genai_exposure_pct", ascending=False)
    responsive(fig, f"{len(hi)} roles at 50% or more of task hours exposed: "
                    + ", ".join(f"{r} {e:.0f}%" for r, e in zip(hi.role, hi.genai_exposure_pct)) + ".")
    return card(fig, "Four support roles carry the highest gen AI exposure \u2013 start redesign and reskilling there",
                "Share of task hours exposed to gen AI (%) vs. median base pay ($K) by role, 2026; bubble area = headcount", SRC,
                "Exposure = share of task hours matched to gen-AI-capable activities in an external task taxonomy.")


def sankey():
    df = pd.read_csv(DATA / "mobility_flows.csv")
    nodes = list(dict.fromkeys(list(df.from_family) + list(df.to_family)))
    idx = {n: i for i, n in enumerate(nodes)}
    focus_src = "DC Associate"
    link_col = [mv.rgba(C.focus, 0.55) if s == focus_src else mv.rgba(C.context, 0.45) for s in df.from_family]
    node_col = [C.focus if n in (focus_src, "DC Leadership", "Supply Chain Planning") else C.context for n in nodes]
    fig = go.Figure(go.Sankey(
        arrangement="snap", valueformat=",",
        node={"label": nodes, "color": node_col, "pad": 18, "thickness": 14, "line": {"width": 0}},
        link={"source": [idx[s] for s in df.from_family], "target": [idx[t] for t in df.to_family], "value": df.moves,
              "color": link_col, "hovertemplate": "%{source.label} \u2192 %{target.label}: %{value:,} moves<extra></extra>"}))
    fig.update_layout(font_size=12)
    total_dc = df.moves[df.from_family == focus_src].sum()
    up = df.moves[(df.from_family == focus_src) & (df.to_family == "DC Leadership")].sum()
    # Phones: taller, tighter node padding, thinner nodes and two-line labels, so labels between columns have room.
    # (restyle values are wrapped in a list: one entry per trace.)
    responsive(fig, f"{total_dc} moves out of DC Associate, {up} of them into DC Leadership.",
               desktop={"height": 440, "restyle": {"node.pad": 18, "node.thickness": 14, "node.label": [nodes]}, "relayout": {"font.size": 12}},
               phone={"height": 560, "restyle": {"node.pad": 10, "node.thickness": 10, "node.label": [[wrap(n, 12) for n in nodes]]}, "relayout": {"font.size": 11}})
    return card(fig, f"DC Associates made {total_dc} internal moves in two years; {round(up / total_dc * 10)} in 10 were "
                     "promotions into DC leadership",
                "Internal moves between job families, trailing 24 months (number of moves)", SRC)


def main():
    css = (ROOT / "dist" / "web" / "mck-viz.css").read_text(encoding="utf-8")
    cards = "\n".join(fn() for fn in (bar_highlight, line_gap, bubble_scatter, sankey))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>McKesson data-viz gallery (interactive)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js" charset="utf-8"></script>
<script>
/* Draw each card after Libre Franklin has loaded (Plotly caches label widths from its first render), then switch
   between the desktop and phone settings each figure carries, as fit() does in templates/html/chart-card.html. */
const MCK_NARROW = window.matchMedia("(max-width: {PHONE_MAX}px)");
function mckDraw(id, f, fit) {{
  const el = document.getElementById(id);
  const apply = () => {{
    const m = fit[MCK_NARROW.matches ? "phone" : "desktop"] || {{}};
    if (m.height) el.style.height = m.height + "px";
    if (m.restyle) Plotly.restyle(el, m.restyle, [0]);
    Plotly.relayout(el, m.relayout || {{}}).then(() => Plotly.Plots.resize(el));
  }};
  document.fonts.ready.then(() => Plotly.newPlot(id, f.data, f.layout, {json.dumps(PLOT_CFG)}).then(() => {{
    apply(); MCK_NARROW.addEventListener("change", apply);
  }}));
}}
</script>
<style>
{css}
body {{ margin: 0; background: var(--mck-surface-subtle); font-family: var(--mck-font); }}
main {{ display: grid; gap: 24px; padding: 32px; max-width: 1040px; margin: 0 auto; }}
@media (max-width: 600px) {{ main {{ padding: 16px 0; gap: 16px; }} .page-title {{ padding: 0 16px; font-size: 28px; }} }}
.page-title {{ font-weight: 300; font-size: 34px; color: var(--mck-blue); margin: 0; }}
.page-title strong {{ font-weight: 700; }}
</style>
</head>
<body>
<main>
<h1 class="page-title"><strong>Workforce</strong> intelligence gallery</h1>
{cards}
</main>
</body>
</html>"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gallery.html").write_text(page, encoding="utf-8")
    print("wrote", OUT / "gallery.html")


if __name__ == "__main__":
    main()
