"""Tests for the chart builders in mckviz/charts.py: each passes mv.lint(strict=True), and each keeps the house rules."""
from __future__ import annotations

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


BUILDERS = {"waterfall": _waterfall, "waterfall_semantic": _waterfall_semantic, "hstack": _hstack,
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
    with pytest.raises(ValueError, match="at most two"):
        mv.waterfall(ax, STEPS, VALS, focus={"Merit", "Hires", "Lag"})
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
