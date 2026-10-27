"""Tests for mckviz.office: native, editable PowerPoint slides. The bar slide's checks are the four things the first
Copilot test of a native slide got wrong (2026-10-26): a column chart sorted ascending, gridlines left on, the plot
pushed right, and the benchmark drawn between two columns instead of across the chart."""
from __future__ import annotations

import warnings

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


def test_takeaways_take_the_right_third():
    r = bar(takeaways=[("27.4%", "Pharmacy technicians"), ("2 of 6", "families above the enterprise rate")])
    frame = next(s for s in r.slide.shapes if s.has_chart)
    assert Emu(frame.width).inches == pytest.approx(office.SIDE_CHART_W, abs=0.01)
    assert named(r.slide, "Takeaways")


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
    (dict(focus={"A", "B", "C"}), "at most two"), (dict(focus={"Z"}), "not among"),
    (dict(values=[1, -2, 3]), "zero"), (dict(values=[1, float("nan"), 3]), "missing")])
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
    (dict(focus=set()), "name the focus"), (dict(focus={"A", "B", "C"}), "at most two"),
    (dict(focus={"Z"}), "not among")])
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


def test_picture_slide_says_each_title_once():
    fig = figure_with_titles()
    r = office.picture_slide(office.deck(), fig, headline="A rose every quarter", subtitle="Metric (%)",
                             source="Source: s")
    assert not {t.get_text() for t in fig.texts} & {"Figure headline", "Figure subtitle", "Figure source"}
    assert r.slide.shapes.title.text == "A rose every quarter"
    assert r.picture._element.nvPicPr.cNvPr.get("descr") == "A rose every quarter"
    assert "picture" in r.slide.notes_slide.notes_text_frame.text


def test_picture_stays_in_the_chart_area():
    for kw in ({}, {"takeaways": [("4", "A at the end"), ("2x", "B's rise")]}):
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
    with pytest.raises(FileExistsError, match="new name"):
        office.deliver(work)                                   # a second write is a second OneDrive copy
    assert [p.name for p in onedrive.iterdir()] == ["deck.pptx"]


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
