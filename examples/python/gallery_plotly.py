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


def card(fig, headline, subtitle, source, footnote=None, dark=False) -> str:
    margin = {"t": 36, "l": 8, "r": 8, "b": 8}
    margin.update({k: v for k in margin if (v := fig.layout.margin[k]) is not None})   # keep chart-specific margins
    fig.update_layout(margin=margin, autosize=True)
    # Draw only after Libre Franklin has loaded: Plotly caches label widths from the first render, so a plot drawn
    # with the fallback font keeps margins that clip the real labels (e.g. long bold category names).
    div_id = f"chart-{next(_ids)}"
    spec = fig.to_json().replace("</", "<\\/")                 # keep "</" from closing the <script> early
    body = (f'<div id="{div_id}" style="height:440px; width:100%;"></div>\n'
            f'<script>document.fonts.ready.then(() => {{ const f = {spec}; '
            f'Plotly.newPlot("{div_id}", f.data, f.layout, {json.dumps(PLOT_CFG)}); }});</script>')
    notes = "<br>".join(html.escape(x) for x in (footnote, source) if x)
    return f"""
<figure class="mck-chart{' mck-chart--dark' if dark else ''}">
  <h2 class="mck-headline">{html.escape(headline)}</h2>
  <p class="mck-subtitle">{html.escape(subtitle)}</p>
  <div class="mck-plot">{body}</div>
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
    fig.update_xaxes(visible=False, range=[0, df.vol_attrition_pct.max() * 1.15])
    fig.update_layout(margin_r=48)                                   # room for the end labels on narrow screens
    fig.update_yaxes(showgrid=False, showline=False, ticklabelstandoff=8, automargin=True, tickvals=df.job_family,
                     ticktext=[f"<b>{j}</b>" if j in set(focus) else j for j in df.job_family])   # echo the highlight
    return card(fig, f"Two frontline job families lose about 1 in 4 people a year, well above the {ent:.1f}% enterprise rate",
                "Voluntary attrition by job family, FY26 (%)", SRC,
                "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.")


def line_gap():
    df = pd.read_csv(DATA / "data_ai_supply_demand.csv")
    fig = go.Figure()
    fig.add_scatter(x=df.year, y=df.internal_supply_fte, name="Internal supply", line_color=C.focus, mode="lines",
                    hovertemplate="%{y:,} FTE<extra>Internal supply</extra>")
    fig.add_scatter(x=df.year, y=df.demand_fte, name="Demand", line_color=C.navy, mode="lines", fill="tonexty",
                    fillcolor=mv.rgba(C.accent, 0.12), hovertemplate="%{y:,} FTE<extra>Demand</extra>")
    for r, col, name, ya in ((df.iloc[-1].demand_fte, C.navy, "Demand", "bottom"),
                             (df.iloc[-1].internal_supply_fte, C.focus, "Internal supply", "top")):
        fig.add_annotation(x=df.year.iloc[-1], y=r, text=f"<b>{name}</b> {r:,.0f}", xanchor="right", yanchor=ya,
                           yshift=6 if ya == "bottom" else -6, font={"color": col, "size": 13})   # label at the line end
    gap = int(df.demand_fte.iloc[-1] - df.internal_supply_fte.iloc[-1])
    fig.add_annotation(x=df.year.iloc[-1], y=(df.demand_fte.iloc[-1] + df.internal_supply_fte.iloc[-1]) / 2,
                       text=f"<b>Gap: {gap:,} FTE</b>", xanchor="right", xshift=-8, font={"color": C.negative_text, "size": 14})
    fig.update_layout(showlegend=False, hovermode="x unified", margin_r=24)
    fig.update_yaxes(range=[750, df.demand_fte.max() * 1.08], dtick=200, tickformat=",")
    fig.update_xaxes(tickvals=df.year, ticktext=[str(y) for y in df.year], tickangle=0)
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
    return card(fig, f"Distribution centers are our strongest internal talent engine \u2013 {total_dc} promotions and moves in two years",
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
