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


def test_deck_is_the_kit_template():
    prs = office.deck()
    assert office.on_grid(prs)
    assert len(prs.slides) == 0
    assert round(Emu(prs.slide_width).inches, 2) == 13.33 and round(Emu(prs.slide_height).inches, 2) == 7.5
    assert mv.office is office                                 # lazy attribute on the package


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


def test_save_once_with_the_headline_as_title(tmp_path):
    prs = office.deck()
    bar(prs=prs)
    path = office.save(prs, tmp_path / "deck.pptx")
    assert path.exists()
    assert pptx.Presentation(str(path)).core_properties.title == "Two job families lose 1 in 4 a year"
