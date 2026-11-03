"""Tests for mckviz.office: native, editable PowerPoint slides. The bar slide's checks are the four things the first
Copilot test of a native slide got wrong (2026-10-26): a column chart sorted ascending, gridlines left on, the plot
pushed right, and the benchmark drawn between two columns instead of across the chart."""
from __future__ import annotations

import warnings
from datetime import datetime

import pytest

pptx = pytest.importorskip("pptx")

from pptx.enum.chart import XL_CHART_TYPE  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Emu  # noqa: E402

import mckviz as mv  # noqa: E402
from mckviz import office  # noqa: E402

FAMILIES = ["Finance", "Pharmacy Technician", "Customer Care", "Distribution Center Associate", "HR", "Sales"]
RATES = [7.4, 27.4, 18.9, 24.1, 8.1, 10.6]


def bar(prs=None, **kw):
    prs = prs or office.deck()
    args = dict(focus={"Pharmacy Technician", "Distribution Center Associate"}, benchmark=19.9,
                benchmark_label="Enterprise 19.9%", fmt="{:.1f}%", headline="Two job families lose 1 in 4 a year",
                subtitle="Voluntary attrition by job family, FY26 (%)", source="Source: Synthetic data")
    args.update(kw)
    return office.bar_slide(prs, FAMILIES, RATES, **args)


def manual_layout(chart) -> dict[str, float]:
    man = chart._chartSpace.chart.plotArea.find(qn("c:layout")).find(qn("c:manualLayout"))
    return {tag: float(man.find(qn(f"c:{tag}")).get("val")) for tag in ("x", "y", "w", "h")}


def named(slide, name):
    return next(s for s in slide.shapes if s.name == name)


def test_deck_is_the_branded_template():
    prs = office.deck()
    assert len(prs.slides) == 0                                # the template's example slide is gone
    assert round(Emu(prs.slide_width).inches, 2) == 13.33 and round(Emu(prs.slide_height).inches, 2) == 7.5
    assert any(lay.name == "Title Only" for lay in prs.slide_layouts)
    assert any(s.name == "McK Logo" for s in prs.slide_master.shapes)
    assert mv.office is office                                 # lazy attribute on the package


@pytest.mark.parametrize("headline, size", [
    ("Pharmacy technicians lose more than 1 in 4 people a year", 34),
    ("Two frontline job families lose about 1 in 4 people a year, well above the 19.9% enterprise rate", 28)])
def test_title_takes_the_master_size_when_it_fits(headline, size):
    assert office.title_size(headline) == size
    slide = office.chart_slide(office.deck(), headline, "Subtitle", None, "", "Source: s")
    assert slide.shapes.title.text_frame.paragraphs[0].runs[0].font.size.pt == size


def test_title_too_long_for_two_lines_is_refused():
    with pytest.raises(ValueError, match="shorten"):
        office.title_size("Pharmacy technicians and distribution center associates lose about 1 in 4 people a year, "
                          "above the enterprise rate of 19.9%, while every other job family stays below it")


def test_horizontal_bars_largest_on_top():
    r = bar()
    assert r.chart.chart_type == XL_CHART_TYPE.BAR_CLUSTERED
    assert r.order == sorted(FAMILIES, key=lambda f: -RATES[FAMILIES.index(f)])
    assert list(r.chart.plots[0].categories) == r.order          # Edit Data reads top to bottom, like the slide
    assert r.chart.category_axis.reverse_order                   # PowerPoint draws bars bottom-up otherwise


def test_sort_false_keeps_the_given_order():
    assert bar(sort=False).order == FAMILIES


def test_no_gridlines_no_value_axis():
    r = bar()
    xml = r.chart._chartSpace.xml
    assert "majorGridlines" not in xml and "minorGridlines" not in xml
    assert not r.chart.value_axis.visible


def test_plot_starts_after_the_longest_label():
    r = bar()
    fw = office.W - office.LEFT - office.RIGHT
    x = manual_layout(r.chart)["x"]
    longest = office.text_width("Distribution Center Associate", office.TICK_PT)
    assert longest < x * fw < longest + 0.6                      # room for the label, and no empty left third
    assert manual_layout(bar(prs=office.deck(), sort=False).chart)["x"] == x


def test_benchmark_is_a_line_across_every_bar():
    r = bar()
    frame = next(s for s in r.slide.shapes if s.has_chart)
    fl, ft, fw, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))
    lay = manual_layout(r.chart)
    line = named(r.slide, "Benchmark line")
    assert line.begin_x == line.end_x                            # vertical: across the bars, not between them
    x = Emu(line.begin_x).inches
    assert x == pytest.approx(fl + fw * (lay["x"] + lay["w"] * 19.9 / r.x_max), abs=0.01)
    top, bottom = sorted(Emu(v).inches for v in (line.begin_y, line.end_y))
    assert top <= ft + fh * lay["y"] and bottom >= ft + fh * (lay["y"] + lay["h"]) - 0.01
    assert named(r.slide, "Benchmark label").text_frame.text == "Enterprise 19.9%"


def test_no_label_sits_on_the_benchmark():
    r = bar()
    assert r.inside == ["Customer Care"]                         # 18.9% ends just short of the 19.9% line
    i = r.order.index("Customer Care")
    pos = r.chart.plots[0].series[0].points[i].data_label._dLbl.find(qn("c:dLblPos")).get("val")
    assert pos == "inEnd"
    assert bar(benchmark=None).inside == []


def test_every_label_fits_inside_the_plot():
    r = bar()
    plot_in = manual_layout(r.chart)["w"] * (office.W - office.LEFT - office.RIGHT)
    for name, v in zip(FAMILIES, RATES):
        weight = "Bold" if name in ("Pharmacy Technician", "Distribution Center Associate") else "Medium"
        end = v / r.x_max * plot_in + office.LABEL_PAD + office.text_width(f"{v:.1f}%", office.LABEL_PT, weight)
        assert end <= plot_in


def test_labels_follow_edit_data():
    r = bar()
    for pt in r.chart.plots[0].series[0].points:
        d = pt.data_label._dLbl
        assert d.find(qn("c:showVal")).get("val") == "1"
        assert d.find(qn("c:numFmt")).get("formatCode") == '0.0"%"'
        assert d.find(qn("c:tx")) is None                        # not typed text


def test_focus_fills_and_bold_labels():
    r = bar(focus={"Pharmacy Technician"}, accent="Distribution Center Associate")
    pts = r.chart.plots[0].series[0].points
    fills = {n: str(pts[i].format.fill.fore_color.rgb) for i, n in enumerate(r.order)
             if n in ("Pharmacy Technician", "Distribution Center Associate")}
    assert fills == {"Pharmacy Technician": mv.colors.focus.lstrip("#").upper(),
                     "Distribution Center Associate": mv.colors.accent.lstrip("#").upper()}
    assert pts[r.order.index("Pharmacy Technician")].data_label.font.bold


def test_headline_subtitle_source_on_the_slide():
    r = bar()
    texts = [s.text_frame.text for s in r.slide.shapes if s.has_text_frame]
    assert r.slide.shapes.title.text == "Two job families lose 1 in 4 a year"
    assert "Voluntary attrition by job family, FY26 (%)" in texts
    assert "Source: Synthetic data" in texts


def test_short_list_keeps_bars_of_normal_weight():
    r = office.bar_slide(office.deck(), ["A", "B", "C"], [1, 3, 2], headline="h", source="s")
    assert manual_layout(r.chart)["h"] * office.CHART_H == pytest.approx(3 * office.MAX_BAND)


INSIGHTS = [("Two families account for most exits", "Pharmacy Technician and DC Associate: 73% of exits"),
            ("The rest sit below the enterprise rate", "All eight other families are under it")]


def test_insights_take_the_right_third_with_no_box_and_number_only_what_the_chart_marks():
    r = bar(insights=INSIGHTS, implication="Retention effort here reaches most voluntary exits.")
    frame = next(s for s in r.slide.shapes if s.has_chart)
    assert Emu(frame.width).inches == pytest.approx(office.SIDE_CHART_W, abs=0.01)
    panel = named(r.slide, "Insights")
    names = [s.name for s in panel.shapes]
    assert "Implication" in names and not any(n.endswith("marker") for n in names)   # nothing on the chart to match
    with pytest.warns(UserWarning, match="shown unnumbered"):
        r = bar(insights=[INSIGHTS[0] + ("Pharmacy Technician",), INSIGHTS[1]])        # only one points at a bar
    assert not any(s.name.startswith("Marker") for s in r.slide.shapes)
    assert not any("card" in n.lower() for n in names)            # no filled box behind the text
    left = min(Emu(s.left).inches for s in panel.shapes)
    assert left == pytest.approx(office.TAKE_LEFT, abs=0.01)


def test_one_insight_alone_has_no_number_and_a_big_number_can_lead():
    r = bar(big=("73%", "of all voluntary exits come from two job families"),
            insights=[("Both run above the enterprise rate", "Each by more than four points")])
    names = [s.name for s in named(r.slide, "Insights").shapes]
    assert "Big number" in names and not any(n.endswith("marker") for n in names)


def test_an_insight_that_only_repeats_the_chart_warns():
    with pytest.warns(UserWarning, match="only repeats numbers the slide already shows"):
        office.bar_slide(office.deck(), ["A", "B", "C"], [27.4, 24.1, 8.1], fmt="{:.1f}%", headline="h",
                         source="s", insights=[("A leads", "A is at 27.4%")])
    with warnings.catch_warnings():
        warnings.simplefilter("error")                             # a derived number (8 families) is not a repeat
        office.bar_slide(office.deck(), ["A", "B", "C"], [27.4, 24.1, 8.1], fmt="{:.1f}%", headline="h",
                         source="s", insights=[("A and B lead", "Together 51.5 points; the other 8 trail")])


def test_takeaways_now_teach_the_insights_form():
    with pytest.raises(TypeError, match=r"insights=\[\(claim, evidence\)"):
        bar(takeaways=[("27.4%", "Pharmacy technicians"), ("2 of 6", "families above the enterprise rate")])
    with pytest.raises(ValueError, match="one to three insights"):
        bar(insights=INSIGHTS * 2)
    with pytest.raises(ValueError, match="claim over two lines"):
        bar(insights=[("A very long claim " * 6, "evidence")])


@pytest.mark.parametrize("fmt, code", [
    ("{:,.0f}", "#,##0"), ("{:.1f}%", '0.0"%"'), ("${:,.1f}M", '"$"#,##0.0"M"'), ("{:.0%}", "0%"),
    ("{:.2f}", "0.00"), ("{}", None), (lambda v: f"{v} pts", None)])
def test_number_format(fmt, code):
    assert office.number_format(fmt) == code


def test_callable_format_types_the_labels():
    r = office.bar_slide(office.deck(), ["A", "B"], [0.1, 0.3], fmt=lambda v: f"{v * 100:.0f} pts", headline="h",
                         source="s")
    assert [p.data_label.text_frame.text for p in r.chart.plots[0].series[0].points] == ["30 pts", "10 pts"]


@pytest.mark.parametrize("kw, msg", [
    (dict(focus={"Z"}), "not among"), (dict(values=[1, -2, 3]), "zero"), (dict(values=[1, float("nan"), 3]), "missing")])
def test_rejects(kw, msg):
    values = kw.pop("values", [1, 2, 3])
    with pytest.raises(ValueError, match=msg):
        office.bar_slide(office.deck(), ["A", "B", "C"], values, headline="h", source="s", **kw)


def test_short_bar_on_the_benchmark_warns():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        office.bar_slide(office.deck(), ["A", "B"], [100, 1], benchmark=1.5, headline="h", source="s")
    assert any("too short" in str(w.message) for w in caught)


YEARS = ["FY22", "FY23", "FY24", "FY25", "FY26"]
FILL = [22, 23, 25, 24, 29]


def column(prs=None, **kw):
    args = dict(focus={"FY26"}, fmt="{:.0f}%", headline="Internal fill reached 29% in FY26",
                subtitle="Internal fill rate (%)", source="Source: Synthetic data")
    args.update(kw)
    return office.column_slide(prs or office.deck(), YEARS, FILL, **args)


def test_columns_keep_their_order_with_labels_on_top():
    r = column()
    assert r.chart.chart_type == XL_CHART_TYPE.COLUMN_CLUSTERED
    assert list(r.chart.plots[0].categories) == YEARS
    xml = r.chart._chartSpace.xml
    assert "majorGridlines" not in xml and "minorGridlines" not in xml
    assert not r.chart.value_axis.visible
    pts = r.chart.plots[0].series[0].points
    assert str(pts[4].format.fill.fore_color.rgb) == mv.colors.focus.lstrip("#").upper()
    assert pts[4].data_label.font.bold and not pts[0].data_label.font.bold
    assert pts[0].data_label._dLbl.find(qn("c:numFmt")).get("formatCode") == '0"%"'


def test_column_labels_fit_under_the_top():
    r = column()
    plot_h = office.PLOT_H * office.CHART_H
    assert max(FILL) / r.y_max * plot_h + office.LABEL_PAD + office.LINE_H <= plot_h


def test_column_benchmark_is_a_line_across_and_clears_its_labels():
    r = column(benchmark=24, benchmark_label="Target 24%")
    line = named(r.slide, "Benchmark line")
    assert line.begin_y == line.end_y                            # horizontal, across every column
    frame = next(s for s in r.slide.shapes if s.has_chart)
    fl, fw = Emu(frame.left).inches, Emu(frame.width).inches
    lay = manual_layout(r.chart)
    assert Emu(line.begin_x).inches <= fl + fw * lay["x"] + 0.01
    assert Emu(line.end_x).inches >= fl + fw * (lay["x"] + lay["w"])
    assert named(r.slide, "Benchmark label").text_frame.text == "Target 24%"
    assert set(r.inside) == {"FY22", "FY23", "FY25"}             # their top labels would cross the line at 24
    assert column().inside == []


def test_long_column_labels_warn():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        office.column_slide(office.deck(), FAMILIES * 2, RATES * 2, headline="h", source="s")
    assert any("bar_slide" in str(w.message) for w in caught)


QUARTERS = ["Q1 '24", "Q2", "Q3", "Q4", "Q1 '25", "Q2", "Q3", "Q4"]
LINES = {"Pharmacy Technician": [31, 30.5, 30, 29.8, 29, 28.4, 28, 27.4],
         "Customer Care": [19, 19.2, 19.4, 19, 18.8, 18.9, 19.1, 18.9],
         "Finance": [8, 7.9, 7.8, 7.6, 7.5, 7.6, 7.5, 7.4],
         "HR": [8.5, 8.4, 8.3, 8.2, 8.3, 8.1, 8.2, 7.6]}


def line(prs=None, **kw):
    args = dict(focus={"Pharmacy Technician"}, fmt="{:.1f}%", headline="Pharmacy technician attrition fell",
                subtitle="Voluntary attrition (%)", source="Source: Synthetic data")
    args.update(kw)
    return office.line_slide(prs or office.deck(), QUARTERS, LINES, **args)


def end_label(r, name):
    s = next(s for s in r.chart.plots[0].series if s.name == name)
    return s.points[len(QUARTERS) - 1].data_label._dLbl


def test_line_colors_and_draw_order():
    r = line(accent="Customer Care")
    assert r.chart.chart_type == XL_CHART_TYPE.LINE
    assert set(r.order[-2:]) == {"Pharmacy Technician", "Customer Care"}   # highlighted lines draw last, on top
    assert r.colors == {"Pharmacy Technician": mv.colors.focus, "Customer Care": mv.colors.accent,
                        "Finance": mv.colors.context, "HR": mv.colors.context}
    assert not r.chart.has_legend


def test_line_end_labels_name_and_value_follow_edit_data():
    r = line()
    hot = end_label(r, "Pharmacy Technician")
    assert hot.find(qn("c:showSerName")).get("val") == "1" and hot.find(qn("c:showVal")).get("val") == "1"
    assert hot.find(qn("c:numFmt")).get("formatCode") == '0.0"%"'
    grey = end_label(r, "Finance")
    assert grey.find(qn("c:showSerName")).get("val") == "1" and grey.find(qn("c:showVal")).get("val") == "0"


def test_close_end_labels_are_nudged_apart():
    r = line()
    nudged = {nm: end_label(r, nm).find(qn("c:layout")) for nm in ("Finance", "HR")}
    assert any(lay is not None for lay in nudged.values())       # 7.4% and 7.6% would overlap
    assert end_label(r, "Pharmacy Technician").find(qn("c:layout")) is None


def test_line_axis_and_gridlines():
    r = line()
    va = r.chart.value_axis
    assert va.has_major_gridlines and va.visible
    assert va.tick_labels.number_format == '0"%"'                 # whole-number steps: no decimals on the axis
    lo, hi = r.y_range
    assert lo <= 7.4 and hi >= 31


def test_line_target_and_forecast():
    r = line(target=20, target_label="Target 20%", forecast_from="Q1 '25")
    assert named(r.slide, "Target label").text_frame.text == "Target 20%"
    tl = named(r.slide, "Target line")
    assert tl.begin_y == tl.end_y
    s = r.chart.plots[0].series[0]
    assert s.points[7].format.line.dash_style is not None         # dashed after the last actual
    assert named(r.slide, "Forecast divider")


def test_forecast_label_must_be_unique():
    with pytest.raises(ValueError, match="position"):
        line(forecast_from="Q2")                                  # "Q2" appears twice
    assert named(line(forecast_from=5).slide, "Forecast divider")


@pytest.mark.parametrize("kw, msg", [
    (dict(focus=set()), "name the focus"), (dict(focus={"Z"}), "not among")])
def test_line_rejects(kw, msg):
    many = {k: [1, 2] for k in "ABCDE"}
    with pytest.raises(ValueError, match=msg):
        office.line_slide(office.deck(), ["Q1", "Q2"], many, headline="h", source="s", **kw)


def test_two_to_four_lines_without_focus_are_categorical():
    r = office.line_slide(office.deck(), ["Q1", "Q2"], {"A": [1, 2], "B": [2, 1]}, headline="h", source="s")
    assert r.colors == {"A": mv.CATEGORICAL[0], "B": mv.CATEGORICAL[1]}


def test_line_gaps_stay_gaps():
    r = office.line_slide(office.deck(), ["Q1", "Q2", "Q3"], {"A": [1, float("nan"), 3]}, headline="h", source="s")
    assert r.chart.plots[0].series[0].values == (1.0, None, 3.0)


FUNCTIONS = ["Technology", "Corporate", "Distribution"]
MIX = [("Full-time", [58, 88, 71]), ("Part-time", [12, 4, 22]), ("Contingent", [30, 8, 7])]


def test_stack_story_segment_first_on_the_baseline():
    r = office.stack_slide(office.deck(), FUNCTIONS, MIX, story="Contingent", headline="h", source="s")
    assert r.chart.chart_type == XL_CHART_TYPE.BAR_STACKED_100
    assert r.order == ["Contingent", "Full-time", "Part-time"]            # moved to the front
    assert r.colors[0] == mv.colors.focus and mv.colors.focus not in r.colors[1:]
    assert r.chart.category_axis.reverse_order                            # first category on top
    assert not r.chart.has_legend
    assert named(r.slide, "Segment name: Contingent").text_frame.text == "Contingent"


def test_stack_labels_where_they_fit():
    r = office.stack_slide(office.deck(), FUNCTIONS, MIX, story="Contingent", headline="h", source="s")
    contingent = r.chart.plots[0].series[0]
    assert all(p.data_label._dLbl.find(qn("c:showVal")).get("val") == "1" for p in contingent.points)
    with warnings.catch_warnings():
        warnings.simplefilter("error")                         # a sliver's name right-aligns to the bar's end
        tiny = office.stack_slide(office.deck(), ["A"], [("Big", [99.5]), ("Small", [0.5])], headline="h", source="s")
    name = named(tiny.slide, "Segment name: Small")
    frame = next(s for s in tiny.slide.shapes if s.has_chart)
    lay = manual_layout(tiny.chart)
    plot_right = Emu(frame.left).inches + Emu(frame.width).inches * (lay["x"] + lay["w"])
    assert Emu(name.left + name.width).inches == pytest.approx(plot_right, abs=0.01)
    assert tiny.chart.plots[0].series[1].points[0].data_label._dLbl.find(qn("c:showVal")).get("val") == "0"


def test_stack_base_counts_and_rejects():
    r = office.stack_slide(office.deck(), FUNCTIONS, MIX, story="Contingent", base=[4100, 5300, 14200],
                           base_label="Workers", headline="h", source="s")
    assert named(r.slide, "Base: Distribution").text_frame.text == "14,200"
    with pytest.raises(ValueError, match="not one of the parts"):
        office.stack_slide(office.deck(), FUNCTIONS, MIX, story="Bogus", headline="h", source="s")
    with pytest.raises(ValueError, match="accent"):
        office.stack_slide(office.deck(), FUNCTIONS, MIX, uniform=True, headline="h", source="s")


STEPS = ["FY25", "Merit", "Hires", "Backfill lag", "Automation", "Contractors", "FY26"]
BRIDGE = [4210, 139, 96, -58, -71, -24, 4292]


def test_waterfall_floats_the_steps_on_a_hidden_base():
    r = office.waterfall_slide(office.deck(), STEPS, BRIDGE, focus={"Automation"}, headline="h", source="s")
    assert r.chart.chart_type == XL_CHART_TYPE.COLUMN_STACKED
    base = r.chart.plots[0].series[0]
    assert base.values[1] == 4210 and base.values[3] == 4210 + 139 + 96 - 58     # a fall starts at its new level
    assert r.ends[-2] == pytest.approx(4292)
    assert r.colors[4] == mv.colors.focus and r.colors[0] == mv.colors.total and r.colors[1] == mv.colors.context
    label = r.chart.plots[0].series[3].points[3].data_label.text_frame.text
    assert label == "−58"                                                     # a true minus


def test_waterfall_floor_breaks_the_totals_and_says_so():
    r = office.waterfall_slide(office.deck(), STEPS, BRIDGE, floor=3900, headline="h", source="s")
    assert r.y_range[0] == 3900
    assert len([s for s in r.slide.shapes if s.name == "Axis break"]) == 4    # two slashes on each total
    assert any("starts at 3,900" in s.text_frame.text for s in r.slide.shapes if s.has_text_frame)
    with pytest.raises(ValueError, match="cuts into"):
        office.waterfall_slide(office.deck(), STEPS, BRIDGE, floor=4300, headline="h", source="s")


def test_waterfall_semantic_colors_and_arrows():
    r = office.waterfall_slide(office.deck(), STEPS, BRIDGE, semantic="down", headline="h", source="s")
    assert r.colors[1] == mv.colors.negative and r.colors[4] == mv.colors.positive
    assert r.chart.plots[0].series[3].points[1].data_label.text_frame.text.startswith("▲")


ROLES = ["RN, Specialty", "Pharmacy Technician", "Software Engineer", "Data Scientist"]
MARKET, OURS = [101, 44, 142, 128], [94, 41, 138, 131]


def test_dumbbell_flags_and_gaps():
    r = office.dumbbell_slide(office.deck(), ROLES, MARKET, OURS, tick_fmt="${:,.0f}K", headline="h", source="s")
    assert r.chart.chart_type == XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS
    assert list(r.flagged) == [True, True, False, False]                       # 5% or more below market
    assert [s.name for s in r.chart.plots[0].series] == ROLES                 # the row names, first on top
    first = r.chart.plots[0].series[0]
    assert first.points[0].data_label._dLbl.find(qn("c:showSerName")).get("val") == "1"
    assert first.points[1].data_label.text_frame.text == "−6.9%"              # at the right-most dot
    assert r.chart.category_axis.tick_labels.number_format == '"$"#,##0"K"'
    assert named(r.slide, "Key")


def test_dumbbell_axis_holds_every_dot():
    r = office.dumbbell_slide(office.deck(), ROLES, MARKET, OURS, headline="h", source="s")
    lo, hi = r.x_range
    assert lo <= 41 and hi >= 142


def figure_with_titles():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mv.use(plotly_default=False)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    mv.line(ax, ["Q1", "Q2", "Q3", "Q4"], {"A": [1, 2, 3, 4], "B": [2, 2, 2, 3]}, focus={"A"})
    mv.titles(fig, "Figure headline", "Figure subtitle")
    mv.source(fig, "Figure source")
    mv.layout(fig)
    return fig


@pytest.mark.filterwarnings("ignore:picture_slide")             # built at 10 x 5.6 on purpose
def test_picture_slide_says_each_title_once():
    fig = figure_with_titles()
    r = office.picture_slide(office.deck(), fig, headline="A rose every quarter", subtitle="Metric (%)",
                             source="Source: s")
    assert not {t.get_text() for t in fig.texts} & {"Figure headline", "Figure subtitle", "Figure source"}
    assert r.slide.shapes.title.text == "A rose every quarter"
    assert r.picture._element.nvPicPr.cNvPr.get("descr") == "A rose every quarter"
    assert "picture" in r.slide.notes_slide.notes_text_frame.text


def test_picture_figure_fills_the_chart_area_and_is_placed_as_built():
    for side in (False, True):
        fig, ax = office.picture_figure(side)
        assert tuple(fig.get_size_inches()) == pytest.approx(office.picture_size(side))
        assert ax.get_position().width > 0.9                   # the plot fills it, before the chart is drawn
        ax.barh(["A", "B"], [1, 2])
        r = office.picture_slide(office.deck(), fig, headline="h", source="s", insights=INSIGHTS if side else None)
        assert tuple(fig.get_size_inches()) == pytest.approx(office.picture_size(side))   # never resized
        assert Emu(r.picture.width).inches > 0.9 * office.picture_size(side)[0]


def test_a_smaller_figure_fills_the_area_and_says_how_to_build_it():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 2.5))                   # built at its own size, as an agent might
    ax.barh(["A", "B"], [1, 2])
    with pytest.warns(UserWarning, match=r"office.picture_figure\(\)"):
        r = office.picture_slide(office.deck(), fig, headline="h", source="s")
    w, h = Emu(r.picture.width).inches, Emu(r.picture.height).inches
    area_w, area_h = office.picture_size()
    assert w > 0.6 * area_w or h > 0.6 * area_h                # enlarged towards the area, not left small
    assert w <= area_w + 0.01 and h <= area_h + 0.01
    assert w <= 1.5 * 6.2                                      # text grows 1.5x at most


@pytest.mark.filterwarnings("ignore:picture_slide")
def test_picture_stays_in_the_chart_area():
    for kw in ({}, {"insights": INSIGHTS}):
        r = office.picture_slide(office.deck(), figure_with_titles(), headline="h", source="s", **kw)
        pic = r.picture
        right = office.LEFT + (office.SIDE_CHART_W if kw else office.W - office.LEFT - office.RIGHT)
        assert Emu(pic.left + pic.width).inches <= right + 0.01
        assert Emu(pic.top).inches >= office.SUB_TOP + 0.35
        assert Emu(pic.top + pic.height).inches <= office.FOOT_TOP


def test_save_refuses_the_delivery_folder_and_deliver_copies_once(tmp_path, monkeypatch):
    onedrive = tmp_path / "mnt-data"
    onedrive.mkdir()
    monkeypatch.setattr(office, "DELIVER_DIR", onedrive)
    prs = office.deck()
    bar(prs=prs)
    with pytest.raises(ValueError, match="/tmp first"):
        office.save(prs, onedrive / "deck.pptx")               # a validator run there would leave copies
    work = office.save(prs, tmp_path / "work" / "deck.pptx")
    assert office.deliver(work) == onedrive / "deck.pptx"
    before = (onedrive / "deck.pptx").stat().st_mtime_ns
    assert office.deliver(work) == onedrive / "deck.pptx"     # a rerun: the same file, nothing written
    import time

    time.sleep(1.1)                                            # the embedded workbook's own dates tick over
    rebuilt = office.deck()
    bar(prs=rebuilt)
    office.save(rebuilt, work)                                 # built again the same way, at another time
    again = pptx.Presentation(str(work))
    again.core_properties.modified = again.core_properties.created = datetime(2020, 1, 1)
    again.save(str(work))
    assert work.read_bytes() != (onedrive / "deck.pptx").read_bytes()
    assert office.deliver(work) == onedrive / "deck.pptx"
    assert (onedrive / "deck.pptx").stat().st_mtime_ns == before
    bar(prs=prs)
    office.save(prs, work)
    with pytest.raises(FileExistsError, match="already delivered in this chat"):
        office.deliver(work)                                   # a changed deck: a second OneDrive copy, refused
    v2 = office.save(prs, tmp_path / "work" / "deck_v2.pptx")
    with pytest.raises(FileExistsError, match="revision="):
        office.deliver(v2)                                     # the agent's own retry under a new name, refused
    assert office.deliver(v2, revision="user asked for a second slide") == onedrive / "deck_v2.pptx"
    (onedrive / "deck_v2.pptx").unlink()                       # (tidy for the check below; never done in Copilot)
    with pytest.raises(ValueError, match="already in the delivery folder"):
        mv.deliver(onedrive / "deck.pptx", to=onedrive)
    assert [p.name for p in onedrive.iterdir()] == ["deck.pptx"]


def test_deliver_several_files(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    files = []
    for name in ("page.html", "page.pdf"):
        (tmp_path / name).write_text(name)
        files.append(tmp_path / name)
    assert mv.deliver(*files, to=out) == [out / "page.html", out / "page.pdf"]
    other = tmp_path / "labor_cost_bridge.pptx"
    other.write_text("deck")
    assert mv.deliver(other, to=out) == out / "labor_cost_bridge.pptx"     # a different deliverable: fine


def test_clear_delivered_takes_earlier_decks_out_and_a_rerun_stays_a_no_op(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    prs = office.deck()
    bar(prs=prs)
    deck = office.save(prs, tmp_path / "deck.pptx")
    png = tmp_path / "deck_preview.png"
    png.write_bytes(b"png")
    mv.deliver(deck, png, to=out)
    assert mv.clear_delivered(to=out) == []                    # delivered in this run: left alone
    monkeypatch.setattr(mv, "_RUN", "a later script")
    (out / "notes.txt").write_text("not ours")
    cleared = mv.clear_delivered(to=out)                       # an earlier run's files: out of the folder
    assert sorted(p.name for p in cleared) == ["deck.pptx", "deck_preview.png"]
    assert [p.name for p in out.iterdir()] == ["notes.txt"]    # a file deliver() didn't write stays
    assert mv.deliver(deck, to=out) == out / "deck.pptx"       # delivering it again: still a no-op, no re-upload
    assert not (out / "deck.pptx").exists()


def test_bar_story_on_top():
    names, vals = ["A", "B", "C", "D"], [82, 71, 41, 38]
    low = office.bar_slide(office.deck(), names, vals, focus={"C", "D"}, headline="h", source="s")
    assert low.order == ["D", "C", "B", "A"]                   # a "lagging" story: the smallest, highlighted, on top
    high = office.bar_slide(office.deck(), names, vals, focus={"A"}, headline="h", source="s")
    assert high.order == ["A", "B", "C", "D"]
    assert office.bar_slide(office.deck(), names, vals, focus={"C"}, sort="descending", headline="h",
                            source="s").order == ["A", "B", "C", "D"]
    assert office.bar_slide(office.deck(), names, vals, headline="h", source="s").order == ["A", "B", "C", "D"]


@pytest.mark.parametrize("name, what", [
    ("Workforce_Mix_Slide_v3.pptx", "workforce_mix_slide.pptx"), ("deck-final.pptx", "deck.pptx"),
    ("deck (2).pptx", "deck.pptx"), ("deck_v2_fixed.pptx", "deck.pptx"), ("fy26_bridge.png", "fy26_bridge.png")])
def test_deliverable_ignores_version_tails(name, what):
    assert mv._deliverable(name) == what


def test_bar_chart_has_alt_text():
    frame = next(s for s in bar().slide.shapes if s.has_chart)
    assert frame._element.nvGraphicFramePr.cNvPr.get("descr") == "Two job families lose 1 in 4 a year"
    frame = next(s for s in bar(alt="Bars").slide.shapes if s.has_chart)
    assert frame._element.nvGraphicFramePr.cNvPr.get("descr") == "Bars"


def test_save_once_with_the_headline_as_title(tmp_path):
    prs = office.deck()
    bar(prs=prs)
    path = office.save(prs, tmp_path / "deck.pptx")
    assert path.exists()
    assert pptx.Presentation(str(path)).core_properties.title == "Two job families lose 1 in 4 a year"


def test_most_bars_highlighted_warns_instead_of_refusing():
    with pytest.warns(UserWarning, match="3 of 3 items highlighted"):
        office.bar_slide(office.deck(), ["A", "B", "C"], [1, 2, 3], focus={"A", "B", "C"}, headline="h", source="s")


def test_insight_markers_sit_after_their_bars_and_a_bracket_spans_its_group():
    r = bar(insights=[("Two families account for most exits", "73% of exits, from 58% of headcount", "Pharmacy Technician"),
                      ("Customer Care is the one to watch", "Just under the enterprise rate", "Customer Care")],
            bracket=(["Pharmacy Technician", "Distribution Center Associate"], "73% of all\nvoluntary exits"))
    names = [s.name for s in r.slide.shapes]
    assert "Marker 1: Pharmacy Technician" in names and "Marker 2: Customer Care" in names
    assert names.count("Bracket") == 3 and "Bracket label" in names
    frame = next(s for s in r.slide.shapes if s.has_chart)
    right = Emu(frame.left + frame.width).inches
    for s in r.slide.shapes:
        if s.name.startswith("Marker") or s.name.startswith("Bracket"):
            assert Emu(s.left + s.width).inches <= right + 0.05            # inside the chart's two-thirds
    with pytest.raises(ValueError, match="is not a bar on the chart"):
        bar(insights=[("A claim", "Its evidence", "Nobody"), ("B claim", "More evidence")])


def test_a_big_number_that_repeats_the_headline_is_refused_and_claims_carry_their_evidence():
    with pytest.raises(ValueError, match="the headline already says 73%"), pytest.warns(UserWarning, match="repeats"):
        bar(headline="Two frontline job families drive 73% of estimated voluntary exits",
            big=("73%", "of estimated voluntary exits"), insights=INSIGHTS)
    r = bar(insights=INSIGHTS)
    box = next(s for s in named(r.slide, "Insights").shapes if s.name == "Insight 1")
    paras = box.text_frame.paragraphs
    assert [p.text for p in paras] == list(INSIGHTS[0])                # claim, then evidence, in one flowing box
