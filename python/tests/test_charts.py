"""Tests for the chart builders in mckviz/charts.py: each passes mv.lint(strict=True), and each keeps the house rules."""
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402

import mckviz as mv  # noqa: E402

C = mv.colors
DATA = Path(__file__).resolve().parents[2] / "examples" / "data"
MINUS = "−"


@pytest.fixture(autouse=True)
def _style():
    mv.use(plotly_default=False)
    yield
    plt.close("all")


def hexes(patches):
    return [to_hex(p.get_facecolor()).upper() for p in patches]


def finish(fig):
    mv.titles(fig, "Two of seven workstreams are off track, both waiting on one integration",
              "Status by workstream, as of 31 Mar 2026 (FY26)")
    mv.source(fig, "Source: Synthetic data for illustration only")
    mv.layout(fig)
    return mv.lint(fig, strict=True, quiet=True)


# ----------------------------------------------------------------------------------------------- builders
STEPS = ["FY25", "Merit", "Hires", "Lag", "Automation", "Contractors", "FY26"]
VALS = [4210, 139, 96, -58, -71, -24, 4292]
CATS = ["Technology", "Corporate", "Distribution"]
PARTS = [("Full-time", [58, 88, 71]), ("Part-time", [12, 4, 22]), ("Contingent", [30, 8, 7])]
PLAN = [dict(workstream="Data platform", owner="Lead A", start="2025-04", end="2026-09", status="on_track",
             what_changed="Loads daily"),
        dict(workstream="Skills inventory", owner="Lead B", start="2025-04", end="2027-03", status="at_risk",
             what_changed="Integration moved"),
        dict(workstream="SWP refresh", owner="Lead C", start="2025-10", end="2026-09", status="off_track",
             what_changed="Paused"),
        dict(workstream="Succession", owner="Lead D", start="2026-07", end="2027-03", status="not_started",
             what_changed="")]
MS = [dict(workstream="Data platform", milestone="Live", due="2025-10", forecast="2025-10", state="met"),
      dict(workstream="Skills inventory", milestone="Integration", due="2026-03", forecast="2026-06", state="moved"),
      dict(workstream="SWP refresh", milestone="Feed", due="2026-02", forecast=None, state="missed"),
      dict(workstream="Succession", milestone="Kickoff", due="2026-07", forecast="2026-07", state="upcoming")]


def _waterfall(ax):
    return mv.waterfall(ax, STEPS, VALS, focus={"Automation", "Contractors"}, floor=3900)


def _waterfall_semantic(ax):
    return mv.waterfall(ax, STEPS, VALS, semantic="down", horizontal=True)


def _hstack(ax):
    return mv.hstack(ax, CATS, PARTS, story="Contingent", focus={"Technology"}, base=[4100, 5300, 14200],
                     base_label="Workers")


def _dumbbell(ax):
    return mv.dumbbell(ax, ["RN", "Pharmacist", "Data Scientist"], [101, 146, 128], [94, 138, 131], tick_fmt="${:,.0f}K")


def _heat(ax):
    m = np.array([[5, 2, -1], [6, -1, -5], [4, -3, -11]])
    return mv.heat(ax, m, rows=["Corporate", "Med-Surg", "Oncology"], cols=["Belonging", "Growth", "Workload"],
                   focus_cols={"Workload"}, key_ends=("Below", "Above"))


def _heat_seq(ax):
    m = np.array([[12.5, 30.1], [44.0, 71.2]])
    return mv.heat(ax, m, rows=["A", "B"], cols=["2025", "2026"], kind="sequential", n=[[50, 8], [40, 30]])


def _kpi(ax):
    return mv.kpi_card(ax, 62, "254 of 410 critical roles have a ready-now successor", change=14, vs="vs. Mar 2025",
                       target=75, ring_value=62)


def _kpi_row(ax):
    return mv.kpi_row(ax, [dict(name="Internal fill rate", value="34%", change=3, vs="vs. FY25"),
                           dict(name="Days to fill", value="47", change=4, unit=" days", better="down")])


def _ring(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    r = mv.ring(ax, 67, target=80)
    mv.big(ax, 0, 0, "67%", ha="center", va="center", size=30)
    return r


def _tracker(ax):
    return mv.tracker(ax, PLAN, milestones=MS)


def _roadmap(ax):
    return mv.roadmap(ax, PLAN, MS, today="2026-03")


def _status_column(ax):
    y = range(len(PLAN))
    ax.barh(list(y), [64, 71, 38, 0], color=C.context)
    ax.set_xlim(0, 110)
    ax.set_xticks([])
    return mv.status_column(ax, [p["status"] for p in PLAN])


def _diverging(ax):
    gaps = [7.5, 4.2, -1.0, -5.7, -12.5]
    return mv.diverging_bars(ax, CATS[:3] + ["Nursing", "Finance"], gaps, worse="above", suffix=" pts",
                             zero_label="Enterprise 19.9%")


def _label_points(ax):
    xs, ys, sizes = [40, 95, 140, 150], [58, 28, 41, 10], [900, 300, 500, 120]
    names = ["Customer Care", "Sales", "Software Engineering", "Finance"]
    ax.scatter(xs, ys, s=sizes, c=mv.highlight(names, focus={"Customer Care"}), lw=0)
    ax.set_xlim(28, 152)
    return mv.label_points(ax, xs, ys, names, sizes, focus={"Customer Care"})


def _rank_slope(ax):
    return mv.rank_slope(ax, ["Data", "Sales", "Ops"], [3, 1, 2], [1, 2, 3], focus={"Data"}, headers=("2023", "2026"))


def _sankey(ax):
    import pandas as pd

    return mv.sankey(ax, pd.read_csv(DATA / "reskilling_pipeline.csv"), focus={"progressed"}, worse={"not_placed"},
                     stages=("Nominated", "Enrolled", "Completed", "Outcome"))


def _strip(ax):
    import pandas as pd

    return mv.strip(ax, pd.read_csv(DATA / "compa_ratio_individuals.csv"), "job_family", "compa_ratio",
                    focus={"Pharmacy Technician"}, share=("below", 0.90), zone=(None, 0.90), zone_label="Below 0.90",
                    ref=1.0, ref_label="Range midpoint", xfmt="{x:.2f}")


def _share_bar(ax):
    import pandas as pd

    return mv.share_bar(ax, pd.read_csv(DATA / "compa_ratio_individuals.csv"), "job_family", "compa_ratio",
                        below=0.90, focus={"Pharmacy Technician"}, ref="overall", ref_label="All job families")


def _line(ax):
    na = float("nan")
    q = ["Q1 '25", "Q2", "Q3", "Q4", "Q1 '26", "Q2", "Q3", "Q4"]
    return mv.line(ax, q, {"Oncology": [9.0, 9.9, 11.2, 13.1, 13.4, 13.0, 12.8, 12.6],
                           "Technology": [11.8, 10.9, 9.8, 9.0, 8.8, 8.9, 9.1, na],
                           "Corporate": [8.2, 7.9, 7.6, 7.1, 7.0, 6.9, 6.8, 6.6]},
                   focus={"Oncology"}, target=10, target_label="Target 10%", event=(2, 3, "Reorg"),
                   forecast_from=5, band={"Oncology": ([na] * 5 + [13.0, 12.2, 11.6], [na] * 5 + [13.0, 13.4, 13.8])})


def _dot_plot(ax):
    return mv.dot_plot(ax, ["Ops", "Sales", "Tech", "HR"], [66, 76, 74, 71], focus={"Ops"}, benchmark=72,
                       benchmark_label="Company 72", fmt="{:.0f}")


def _bar(ax):
    return mv.bar(ax, ["Finance", "Sales", "Supply Chain", "Pharmacy Ops"], [71, 64, 38, 41],
                  focus={"Supply Chain", "Pharmacy Ops"}, benchmark=50.8, benchmark_label="Company 50.8%",
                  fmt="{:.0f}%")


BUILDERS = {"bar": _bar, "dot_plot": _dot_plot, "line": _line, "share_bar": _share_bar, "strip": _strip, "sankey": _sankey, "waterfall": _waterfall, "waterfall_semantic": _waterfall_semantic, "hstack": _hstack,
            "dumbbell": _dumbbell, "heat": _heat, "heat_sequential": _heat_seq, "kpi_card": _kpi,
            "kpi_row": _kpi_row, "ring": _ring, "tracker": _tracker, "roadmap": _roadmap,
            "status_column": _status_column, "rank_slope": _rank_slope, "diverging_bars": _diverging,
            "label_points": _label_points}


@pytest.mark.parametrize("name", list(BUILDERS))
def test_builder_passes_strict_lint(name):
    fig, ax = plt.subplots(figsize=(10, 5))
    BUILDERS[name](ax)
    findings = finish(fig)
    assert not [f for f in findings if f.level == "error"]


def test_multiples_passes_strict_lint():
    fig = plt.figure(figsize=(10, 6))
    data = {"Oncology": [9.0, 9.9, 11.2, 13.1], "Technology": [11.8, 10.9, 9.8, 9.0], "RxTS": [7.5, 7.6, 7.0, 6.7],
            "Corporate": [8.2, 7.9, 7.6, 7.1]}
    ns = mv.multiples(fig, data, x=["Q1", "Q2", "Q3", "Q4"], worse={"Oncology"}, ncols=2)
    finish(fig)
    assert ns.order[0] == "Oncology"                                   # ordered by the latest value
    assert len({a.get_ylim() for a in ns.axes}) == 1                   # one shared scale
    assert ns.axes[0].get_ylim()[0] == 0                               # zero baseline for positive data
    own = [ln for ln in ns.axes[0].get_lines() if ln.get_zorder() == 3][0]
    assert to_hex(own.get_color()).upper() == C.negative.upper()


def test_builders_work_with_dataframes_and_csv_paths():
    pd = pytest.importorskip("pandas")
    plan = pd.read_csv(DATA / "initiative_plan.csv")
    fig, ax = plt.subplots(figsize=(11, 5))
    mv.roadmap(ax, plan, DATA / "initiative_milestones.csv", today="2026-03")
    finish(fig)
    fig, ax = plt.subplots(figsize=(10, 5))
    m = pd.read_csv(DATA / "engagement_vs_benchmark.csv").pivot(index="business_unit", columns="driver",
                                                                 values="delta_vs_benchmark_pts")
    ns = mv.heat(ax, m)
    assert len(ns.cells) == m.size


# ----------------------------------------------------------------------------------------------- the rules
def test_waterfall_totals_navy_deltas_grey_focus_blue():
    fig, ax = plt.subplots()
    ns = _waterfall(ax)
    cols = hexes(ns.bars)
    assert cols[0] == cols[-1] == C.total.upper()
    assert cols[4] == cols[5] == C.focus.upper()
    assert set(cols[1:4]) == {C.context.upper()}
    labels = [t.get_text() for t in ns.labels]
    assert labels[1] == "+139" and labels[3] == f"{MINUS}58"           # explicit plus, true minus
    assert "starts at 3,900" in ns.note
    assert ax.get_ylim()[0] == 3900
    breaks = [ln for ln in ax.get_lines() if to_hex(ln.get_color()) == "#ffffff"]
    assert len(breaks) == 4                                            # two slashes on each of the two totals


def test_waterfall_semantic_colors_carry_arrows():
    fig, ax = plt.subplots()
    ns = mv.waterfall(ax, STEPS, VALS, semantic="down")                # cost: an increase is unfavorable
    cols = hexes(ns.bars)
    assert cols[1] == C.negative.upper() and cols[4] == C.positive.upper()
    assert ns.labels[4].get_text().startswith(mv.charts.DOWN)          # green only with its symbol
    assert ns.labels[1].get_text().startswith(mv.charts.UP)


def test_waterfall_guards():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="cuts into"):
        mv.waterfall(ax, STEPS, VALS, floor=4300)
    with pytest.raises(ValueError, match="kinds"):
        mv.waterfall(ax, STEPS, VALS, kinds=["total"] * 6 + ["sum"])
    fig, ax = plt.subplots()
    mv.waterfall(ax, STEPS, VALS)
    assert ax.get_ylim()[0] == 0                                       # zero baseline unless a floor is asked for


def test_hstack_story_segment_on_the_baseline_with_white_separators():
    fig, ax = plt.subplots()
    ns = _hstack(ax)
    first = ns.bars[0]
    assert first.get_label() == "Contingent"
    assert all(r.get_x() == 0 for r in first)                          # starts at the baseline in every bar
    assert hexes(first)[0] == C.focus.upper()
    assert {hexes(b)[0] for b in ns.bars[1:]} <= {C.context.upper(), C.context_light.upper(), C.axis.upper()}
    assert all(to_hex(r.get_edgecolor()) == "#ffffff" for b in ns.bars for r in b)
    assert [t.get_text() for t in ns.names] == ["Contingent", "Full-time", "Part-time"]
    assert ax.get_legend() is None
    top = max(ax.get_yticklabels(), key=lambda t: t.get_position()[1])
    assert top.get_text() == "Technology"                              # the first category is the top bar
    assert top.get_fontweight() in (600, "semibold")


def test_hstack_limits_segments():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="Other"):
        mv.hstack(ax, ["A"], [(str(i), [20]) for i in range(5)])


def test_hstack_follows_the_three_color_patterns():
    order = lambda ns: [b.get_label() for b in ns.bars]                # noqa: E731
    fig, ax = plt.subplots()
    ns = mv.hstack(ax, CATS, PARTS, story="Part-time", accent="Contingent")      # focus + accent
    assert order(ns)[:2] == ["Contingent", "Part-time"]                         # the exception on the baseline
    assert [hexes(b)[0] for b in ns.bars] == [C.accent.upper(), C.focus.upper(), C.context.upper()]
    assert ns.names[0].get_color() == C.accent and ns.names[0].get_fontweight() in (600, "semibold")
    ns = mv.hstack(ax, CATS, PARTS, accent="Contingent", uniform=True)           # uniform + accent: no greys
    assert hexes(ns.bars[0])[0] == C.accent.upper()
    assert {hexes(b)[0] for b in ns.bars[1:]} <= {c.upper() for c in (C.focus_light, *mv.SEQUENTIAL["blue"][:2])}
    with pytest.raises(ValueError, match="accent"):
        mv.hstack(ax, CATS, PARTS, uniform=True)
    with pytest.raises(ValueError, match="not one of the parts"):
        mv.hstack(ax, CATS, PARTS, accent="Interns")


def test_dumbbell_flags_shortfalls_in_orange_only():
    fig, ax = plt.subplots()
    ns = _dumbbell(ax)
    assert list(ns.flagged) == [True, True, False]
    face = [to_hex(c).upper() for c in ns.value_dots.get_facecolors()]
    assert face == [C.negative.upper(), C.negative.upper(), C.focus.upper()]
    assert {to_hex(c).upper() for c in ns.compare_dots.get_facecolors()} == {C.context.upper()}
    assert ns.labels[0].get_text().startswith(MINUS)


def test_diverging_bars_orange_only_on_the_worse_side_with_true_minus():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = _diverging(ax)
    assert hexes(ns.bars) == [C.negative.upper()] * 2 + [C.focus.upper()] * 3
    assert ns.worse.tolist() == [True, True, False, False, False]
    assert [t.get_text() for t in ns.labels] == ["+7.5 pts", "+4.2 pts", f"{MINUS}1.0 pts", f"{MINUS}5.7 pts",
                                                 f"{MINUS}12.5 pts"]
    assert "-" not in "".join(t.get_text() for t in ns.labels)
    assert [to_hex(t.get_color()).upper() for t in ns.labels[:2]] == [C.negative_text.upper()] * 2
    ticks = ax.get_yticklabels()
    assert [t.get_fontweight() for t in ticks[:2]] == [600, 600] and ticks[2].get_fontweight() != 600
    assert to_hex(ticks[0].get_color()).upper() == C.headline.upper()
    assert not ax.get_xticks().size                                    # labels replace the value axis
    # worse="below" flips the side; a format string keeps the true minus
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = mv.diverging_bars(ax, ["A", "B"], [3, -4], worse="below", fmt="{:+.0f}%")
    assert hexes(ns.bars) == [C.focus.upper(), C.negative.upper()]
    assert [t.get_text() for t in ns.labels] == ["+3%", f"{MINUS}4%"]
    with pytest.raises(ValueError):
        mv.diverging_bars(ax, ["A"], [1], worse="left")


def test_diverging_bars_negative_labels_stay_inside_the_plot():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = mv.diverging_bars(ax, ["Long category name here", "B", "C"], [-12.5, -1.0, 2.0], suffix=" pts")
    fig.canvas.draw()
    x0 = ax.get_window_extent().x0
    for t in ns.labels:
        assert t.get_window_extent().x0 >= x0 - 0.5                  # never left of the axes, into the names
    assert ns.xlim[0] < -12.5 and ns.xlim[1] > 2.0


def test_label_points_go_left_in_the_right_quarter_with_a_halo():
    fig, ax = plt.subplots(figsize=(10, 5))
    texts = _label_points(ax)
    sides = {t.get_text(): t.get_ha() for t in texts}
    assert sides == {"Customer Care": "left", "Sales": "left", "Software Engineering": "right", "Finance": "right"}
    assert all(t.get_path_effects() for t in texts)
    cc = [t for t in texts if t.get_text() == "Customer Care"][0]
    assert cc.get_fontweight() == 700 and to_hex(cc.get_color()).upper() == C.headline.upper()
    sales = [t for t in texts if t.get_text() == "Sales"][0]
    assert sales.get_fontweight() == 400 and to_hex(sales.get_color()).upper() == C.text_muted.upper()
    big_off, small_off = cc.xyann[0], [t for t in texts if t.get_text() == "Sales"][0].xyann[0]
    assert big_off > small_off > 0                                     # the offset clears the bubble
    with pytest.raises(ValueError):
        mv.label_points(ax, [1, 2], [1], ["a", "b"])


def test_heat_classes_and_suppression():
    fig, ax = plt.subplots()
    ns = _heat(ax)
    assert np.allclose(ns.bounds, -ns.bounds[::-1])                    # symmetric about zero
    assert ns.color_of(0) == mv.DIVERGING[len(mv.DIVERGING) // 2]
    assert ns.color_of(-11) == mv.DIVERGING[0]
    fig, ax = plt.subplots()
    ns = _heat_seq(ax)
    texts = [t.get_text() for t in ns.texts]
    assert texts[1] == "n<10"                                          # minimum n: no value, no class color
    assert hexes([ns.cells[1]])[0] == C.context_light.upper()


def test_delta_label_green_only_when_favorable_and_with_an_arrow():
    t, c = mv.delta_label(14, unit=" pts", vs="vs. Mar 2025")
    assert t == f"{mv.charts.UP} +14 pts vs. Mar 2025" and c == C.positive_text
    t, c = mv.delta_label(4, unit=" days", better="down")
    assert t.startswith(mv.charts.UP) and c == C.negative_text
    t, c = mv.delta_label(-3, better="down")
    assert t.startswith(mv.charts.DOWN) and c == C.positive_text
    assert mv.delta_label(0.2)[0].startswith("No change")


def test_kpi_card_shortfall_is_orange_text():
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ns = _kpi(ax)
    assert ns.target.get_text() == "13 pts short of the 75% target"
    assert ns.target.get_color() == C.negative_text
    assert ns.change.get_color() == C.positive_text
    with pytest.raises(ValueError):
        mv.ring(ax, 122)


@pytest.mark.parametrize("key", list(mv.STATUS))
def test_status_always_has_color_symbol_and_word(key):
    fig, ax = plt.subplots()
    ns = mv.status(ax, 0.5, 0.5, key)
    assert to_hex(ns.dot.get_facecolor()[0]).upper() == mv.STATUS[key]["value"].upper()
    assert len(ns.symbol.get_paths()[0].vertices) >= 2                 # a drawn symbol inside the dot
    ink = to_hex(ns.symbol.get_edgecolor()[0]).upper()
    assert ink == mv.text_on(mv.STATUS[key]["value"]).upper()
    assert ns.text.get_text() == mv.STATUS[key]["label"]


def test_status_names_are_normalized_and_checked():
    assert mv.status_key("On track") == "on_track"
    assert mv.status_key("off-track") == "off_track"
    assert mv.status_key("Complete") == "done"
    with pytest.raises(ValueError, match="unknown status"):
        mv.status_key("green")


def test_tracker_puts_exceptions_first():
    fig, ax = plt.subplots(figsize=(10, 4))
    ns = _tracker(ax)
    assert [r["status"] for r in ns.rows] == ["off_track", "at_risk", "on_track", "not_started"]
    assert all(s.text.get_text() for s in ns.statuses)


def test_roadmap_rules():
    fig, ax = plt.subplots(figsize=(10, 4))
    ns = _roadmap(ax)
    cols = hexes(ns.bars)
    assert cols[2] == C.focus.upper()                                  # off track: blue, the headline's rows
    assert cols[3] == C.context_light.upper()                          # not started: light grey
    assert cols[0] == C.context.upper()
    assert [s.text.get_text() for s in ns.statuses] == ["On track", "At risk", "Off track", "Not started"]
    texts = [t.get_text() for t in ax.texts] + [c.get_text() for c in ax.get_children() if hasattr(c, "get_text")]
    assert "Moved Mar to Jun" in texts
    assert ax.get_ylim()[0] > ax.get_ylim()[1]                         # first row on top


def test_records_accept_plain_dicts_without_pandas(monkeypatch):
    import builtins

    real = builtins.__import__

    def no_pandas(name, *a, **k):
        if name == "pandas":
            raise ImportError("no pandas")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", no_pandas)
    assert mv.charts._records(PLAN)[0]["workstream"] == "Data platform"
    with pytest.raises(ImportError, match="pip install pandas"):
        mv.charts._records("plan.csv")


def test_wrap_never_breaks_a_word():
    from mckviz.charts import _wrap
    assert _wrap("Shepherdsville", 13) == "Shepherdsville"
    assert _wrap("If at network avg", 13) == "If at network\navg"


def test_dumbbell_focus_bolds_the_named_row():
    fig, ax = plt.subplots()
    mv.dumbbell(ax, ["A", "B", "C"], [10, 20, 30], [11, 19, 31], flag_below=None, focus=["B"])
    weights = [t.get_fontweight() for t in ax.get_yticklabels()]
    assert weights[1] == 600 and weights[0] != 600 and weights[2] != 600


def test_sankey_conserves_flow_and_colors_by_kind():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = _sankey(ax)
    assert ns.columns == [["Nominated"], ["Enrolled", "Declined"], ["Completed", "Withdrew"],
                          ["Redeployed to data role", "Returned to prior role", "Left McKesson"]]
    assert ns.sizes["Nominated"] == 1200 and ns.sizes["Completed"] == 840               # max(inflow, outflow)
    h = {n: y1 - y0 for n, (_, y0, y1) in ns.nodes.items()}
    assert h["Enrolled"] / h["Nominated"] == pytest.approx(1010 / 1200)                 # one shared scale
    tones = {to_hex(b.get_facecolor()[0]).upper() for b in ns.bands}
    assert tones == {C.focus.upper(), C.context.upper(), C.negative.upper()}
    assert [to_hex(b.get_facecolor()[0]).upper() for b in ns.bands][0] == C.context.upper()   # grey drawn first
    texts = {t.get_text() for t in ns.labels}
    assert {"Completed  840", "Left McKesson  80", "Outcome"} <= texts


def test_sankey_refuses_small_flows_and_loops():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="n<10"):
        mv.sankey(ax, [("A", "B", 40), ("A", "C", 6)])
    with pytest.raises(ValueError, match="loop"):
        mv.sankey(ax, [("A", "B", 40), ("B", "A", 20)])
    with pytest.raises(ValueError, match="stage names"):
        mv.sankey(ax, [("A", "B", 40)], stages=("One", "Two", "Three"))


def test_strip_orders_by_median_shows_n_and_share():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = _strip(ax)
    medians = [ns.stats[g]["median"] for g in ns.order]
    assert medians == sorted(medians, reverse=True)                                   # highest median on top
    assert ns.order[-1] == "Pharmacy Technician" and round(ns.stats["Pharmacy Technician"]["share"]) == 25
    texts = {t.get_text() for t in ns.labels}
    assert {"25%", "n=620", "Below 0.90", "Range midpoint"} <= texts
    dots = [c for c in ax.collections if c.get_offsets().shape[0] == 620]
    assert to_hex(dots[0].get_facecolor()[0]).upper() == C.focus.upper()
    top = min(ax.get_yticklabels(), key=lambda t: t.get_position()[1])
    assert top.get_text() == "Pharmacy Technician" and top.get_fontweight() in (600, "semibold")


def test_strip_suppresses_small_groups_and_limits_groups():
    fig, ax = plt.subplots()
    ns = mv.strip(ax, {"A": range(40), "B": range(30), "Tiny": range(6)})
    assert ns.suppressed == ["Tiny"] and "Tiny" not in ns.order
    with pytest.raises(ValueError, match="at most 8"):
        mv.strip(ax, {str(i): range(20) for i in range(9)})
    assert len(mv.strip(ax, {str(i): range(20) for i in range(9)}, dots=False).order) == 9   # boxes go to 20


def test_share_bar_computes_shares_from_people_and_sorts():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = _share_bar(ax)
    assert ns.order[0] == "Pharmacy Technician" and round(ns.shares["Pharmacy Technician"], 1) == 25.5
    assert [ns.shares[g] for g in ns.order] == sorted(ns.shares.values(), reverse=True)
    assert ns.counts["Pharmacy Technician"] == 158 and ns.n["Pharmacy Technician"] == 620
    assert round(ns.overall, 1) == round(100 * sum(ns.counts.values()) / sum(ns.n.values()), 1)
    texts = {t.get_text() for t in ax.texts}
    assert {"25%", "n=620", f"All job families {ns.overall:.0f}%"} <= texts
    assert hexes(ns.bars)[0] == C.focus.upper() and set(hexes(ns.bars)[1:]) == {C.context.upper()}


def test_share_bar_needs_one_threshold_and_suppresses_small_groups():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="exactly one"):
        mv.share_bar(ax, {"A": range(20)})
    ns = mv.share_bar(ax, {"A": range(40), "B": range(30), "Tiny": range(5)}, above=25)
    assert ns.suppressed == ["Tiny"] and ns.order == ["A", "B"]


def test_strip_boxes_only_the_focus_group_by_default():
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=(10, 5))
    _strip(ax)
    assert len([p for p in ax.patches if isinstance(p, Rectangle) and p.get_fill() is False
                or isinstance(p, Rectangle) and p.get_facecolor()[3] == 0]) == 1


def test_line_greys_context_labels_ends_and_dashes_the_forecast():
    fig, ax = plt.subplots(figsize=(10, 5))
    ns = _line(ax)
    assert to_hex(ns.lines["Oncology"].get_color()).upper() == C.focus.upper()
    assert to_hex(ns.lines["Technology"].get_color()).upper() == C.context.upper()
    texts = {t.get_text(): t for t in ns.labels}
    assert "Oncology\n12.6 (11.6–13.8)" in texts and "Technology" in texts             # band label; context: name only
    assert texts["Technology"].get_position()[0] == 6                                     # its last finite point
    assert any(ln.get_linestyle() == "--" for ln in ax.get_lines())                        # the forecast part
    ys = sorted(t.get_window_extent(fig.canvas.get_renderer()).y0 for t in ns.labels)
    tops = sorted(t.get_window_extent(fig.canvas.get_renderer()).y1 for t in ns.labels)
    assert all(b >= a - 1 for a, b in zip(tops[:-1], ys[1:]))                             # labels don't overlap
    assert ax.get_xlim()[1] > 7.5                                                          # room for the labels
    assert [t.get_text() for t in ax.get_xticklabels()][:2] == ["Q1 '25", "Q2"]


def test_line_colors_and_limits():
    fig, ax = plt.subplots()
    ns = mv.line(ax, ["FY24", "FY25", "FY26"], {"A": [1, 2, 3], "B": [3, 2, 1]})
    assert [to_hex(c).upper() for c in ns.colors.values()] == [c.upper() for c in mv.CATEGORICAL[:2]]
    with pytest.raises(ValueError, match="name the focus"):
        mv.line(ax, ["a", "b"], {str(i): [1, 2] for i in range(5)})
    with pytest.raises(ValueError, match="appears 2 times"):
        mv.line(ax, ["Q1", "Q2", "Q1"], {"A": [1, 2, 3]}, forecast_from="Q1")


def test_bar_puts_the_story_on_top_and_highlights_only_it():
    fig, ax = plt.subplots(figsize=(10, 4))
    ns = _bar(ax)
    assert ns.order == ["Supply Chain", "Pharmacy Ops", "Sales", "Finance"]   # a "lagging" story: smallest on top
    cols = [to_hex(b.get_facecolor()).upper() for b in ns.bars]
    assert cols[:2] == [C.focus.upper()] * 2 and set(cols[2:]) == {C.context.upper()}
    assert ax.get_xlim()[0] == 0 and not ax.get_xticks().size                 # from zero, no value axis
    assert {"38%", "71%", "Company 50.8%"} <= {t.get_text() for t in ns.labels}
    lead = mv.bar(ax, ["A", "B", "C"], [9, 30, 20], focus={"B"})
    assert lead.order == ["B", "C", "A"]                                      # a "leading" story: largest on top
    uniform = mv.bar(ax, ["A", "B", "C"], [9, 30, 20], accent="B", uniform=True)
    assert [to_hex(b.get_facecolor()).upper() for b in uniform.bars] == [C.accent.upper()] + [C.focus_light.upper()] * 2
    with pytest.raises(ValueError, match="diverging"):
        mv.bar(ax, ["a", "b"], [1, -2])


def test_bar_and_bar_slide_share_the_order():
    from mckviz import office

    names, vals = ["A", "B", "C", "D"], [82, 71, 41, 38]
    for focus in ({"C", "D"}, {"A"}, set()):
        fig, ax = plt.subplots()
        chart = mv.bar(ax, names, vals, focus=focus)
        slide = office.bar_slide(office.deck(), names, vals, focus=focus, headline="h", source="s")
        assert chart.order == slide.order
        plt.close(fig)


def test_dot_plot_sorts_highlights_and_names_the_benchmark():
    fig, ax = plt.subplots(figsize=(10, 4))
    ns = _dot_plot(ax)
    assert ns.order == ["Sales", "Tech", "HR", "Ops"]                                     # largest on top
    cols = [to_hex(c).upper() for c in ns.dots.get_facecolors()]
    assert cols[-1] == C.focus.upper() and set(cols[:-1]) == {C.context.upper()}
    assert {"66", "76", "Company 72"} <= {t.get_text() for t in ns.labels}
    assert ax.get_xlim()[0] > 0                                                           # no forced zero


def test_highlights_follow_the_headline_and_warn_only_when_most_are_blue():
    fig, ax = plt.subplots()
    labels = list("abcdefghij")
    with warnings.catch_warnings():
        warnings.simplefilter("error")                          # three of ten, named by the headline: fine
        mv.bar(ax, labels, range(1, 11), focus={"a", "b", "c"})
        mv.line(ax, ["Q1", "Q2"], {k: [1, 2] for k in labels[:6]}, focus={"a", "b", "c"})
        mv.highlight(labels, focus={"a", "b"}, accent="c")
    with pytest.warns(UserWarning, match="4 of 5 bars highlighted"):
        mv.bar(ax, labels[:5], range(1, 6), focus=set("abcd"))
    with pytest.warns(UserWarning, match="none stands out"):
        mv.highlight(labels[:4], focus=set("abc"))


def _bubble(fig, ax, pay_scale=1.0, exposure_scale=1.0, **kw):
    import pandas as pd

    df = pd.read_csv(DATA / "automation_exposure.csv")
    focus = set(df.role[df.genai_exposure_pct >= 50])                # the same four roles, whatever the scale
    df = df.assign(median_pay_k=df.median_pay_k * pay_scale, genai_exposure_pct=df.genai_exposure_pct * exposure_scale)
    avg = (df.genai_exposure_pct * df.headcount).sum() / df.headcount.sum()
    args = dict(focus=focus, size_label="Headcount",
                zone_y=(50, None), zone_label="High exposure: 50%+ of task hours", ref_y=avg,
                ref_y_label=f"Workforce average {avg:.0f}%", xfmt="${x:,.0f}K", yfmt="{x:.0f}%",
                xlabel="Median base pay", ylabel="Task hours exposed to gen AI")
    ns = mv.bubble(ax, df.median_pay_k, df.genai_exposure_pct, df.headcount, df.role, **{**args, **kw})
    mv.titles(fig, "Four support roles carry the highest gen AI exposure", "Exposure vs. pay; bubble area = headcount")
    mv.source(fig, "Source: Synthetic data for illustration only")
    return df, ns


@pytest.mark.parametrize("scale", [(1.0, 1.0), (1.25, 0.6), (0.7, 1.3)], ids=["cookbook", "shifted", "squeezed"])
@pytest.mark.parametrize("slide", [False, True], ids=["png", "slide"])
def test_bubble_layout_fits_any_data_with_nothing_on_the_bubbles(tmp_path, scale, slide):
    fig, ax = mv.office.picture_figure() if slide else plt.subplots(figsize=(10, 5.8))
    df, ns = _bubble(fig, ax, *scale)
    mv.save(fig, tmp_path / "b.png", dpi=100)                  # lays out the titles: the plot changes size
    r = fig.canvas.get_renderer()
    frame = ax.get_window_extent(r)
    px = r.points_to_pixels(1.0)
    for (x, y), s in zip(ax.transData.transform(ns.points.get_offsets()), ns.points.get_sizes()):
        rad = s ** 0.5 / 2 * px
        assert frame.x0 - 1 <= x - rad and x + rad <= frame.x1 + 1 and frame.y0 - 1 <= y - rad <= y + rad <= frame.y1 + 1
    rules = {f.rule for f in mv.lint(fig, quiet=True)}
    assert not rules & {"label-on-data", "label-overlap", "off-canvas"}, rules
    key = ns.key.get_window_extent(r)
    assert key.y0 >= frame.y1                                  # above the plot, never among the data
    assert fig._mck["sub"].get_window_extent(r).y0 >= key.y1 - 1  # and the subtitle clear of it


def test_bubble_area_follows_the_count_and_colors_follow_the_headline():
    fig, ax = plt.subplots(figsize=(10, 5.8))
    df, ns = _bubble(fig, ax, accent="Distribution Center Associate", label={"Customer Care"})
    sizes = dict(zip(ns.order, ns.points.get_sizes()))
    hc = dict(zip(df.role, df.headcount))
    assert sizes["Distribution Center Associate"] == pytest.approx(1800)            # the largest gets max_area
    assert sizes["Pharmacy Technician"] / sizes["Sales"] == pytest.approx(hc["Pharmacy Technician"] / hc["Sales"])
    assert ns.order[0] == "Distribution Center Associate"                           # largest drawn first
    fc = {n: to_hex(c).upper() for n, c in zip(ns.order, ns.points.get_facecolors())}
    assert fc["Customer Care"] == C.focus.upper() and fc["Sales"] == C.context.upper()
    assert fc["Distribution Center Associate"] == C.accent.upper()
    assert [t.get_text() for t in ns.labels] == ["Customer Care"]


def test_plain_scatter_has_equal_blue_dots_and_no_key():
    fig, ax = plt.subplots()
    ns = mv.bubble(ax, [1, 2, 3, 4], [4, 3, 5, 1])
    assert ns.key is None and len(set(ns.points.get_sizes())) == 1
    assert {to_hex(c).upper() for c in ns.points.get_facecolors()} == {C.focus.upper()}


def test_bubble_refuses_what_it_cannot_draw():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="not in the data"):
        mv.bubble(ax, [1, 2], [1, 2], [5, 6], ["a", "b"], focus={"c"})
    with pytest.raises(ValueError, match="log x"):
        mv.bubble(ax, [0, 2], [1, 2], logx=True)
    with pytest.raises(ValueError, match="same length"):
        mv.bubble(ax, [1, 2], [1])


def test_size_key_values_are_round_and_span_the_data():
    from mckviz.charts import _key_values

    assert _key_values(450, 11_800) == [1_000, 5_000, 10_000]
    assert _key_values(300, 6_200) == [500, 2_000, 5_000]
    assert _key_values(4_000, 9_000) == [2_000, 5_000]                              # no key bubble far below the data
