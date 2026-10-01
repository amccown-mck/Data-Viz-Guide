"""mv.lint must pass a chart built the house way and flag each rule when it's broken.

    python -m pytest python/tests
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pytest

import mckviz as mv

mv.use()
C = mv.colors
CATS = ["Pharmacy Technician", "DC Associate", "Customer Care", "Sales", "Finance"]
VALS = [27.4, 24.1, 18.9, 10.6, 7.4]


def rules(findings, level=None):
    return {f.rule for f in findings if level is None or f.level == level}


def good_bar():
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(CATS[::-1], VALS[::-1], color=mv.highlight(CATS[::-1], focus=CATS[:2]), height=0.67)
    mv.label_bars(ax, bars, fmt="{:.1f}%")
    mv.clean_axes(ax, keep=("left",), grid=None)
    ax.set_xticks([])
    mv.titles(fig, "Two frontline job families lose about 1 in 4 people a year", "Voluntary attrition by job family, FY26 (%)")
    mv.source(fig, "Source: Synthetic data for illustration only")
    return fig


def test_house_style_bar_has_no_errors_or_warnings():
    fig = good_bar()
    found = mv.lint(fig, quiet=True)
    assert not [f for f in found if f.level in ("error", "warn")], found
    plt.close(fig)


def test_missing_titles_and_source_are_errors():
    fig, ax = plt.subplots()
    ax.bar(CATS, VALS, color=C.focus)
    found = mv.lint(fig, quiet=True)
    assert {"headline", "subtitle", "source"} <= rules(found, "error")
    plt.close(fig)


def test_label_headline_is_flagged():
    fig = good_bar()
    found = mv.lint(fig, headline="Attrition by job family", quiet=True)
    assert "headline" in rules(found, "warn")
    plt.close(fig)


def test_truncated_bars_rainbow_red_green_rotation_legend():
    fig, ax = plt.subplots()
    rainbow = ["red", "green", "blue", "orange", "purple", "brown", "pink", "olive"]
    names = [f"Site {i}" for i in range(8)]
    ax.bar(names, [60 + i for i in range(8)], color=rainbow, label="Engagement")
    ax.set_ylim(55, 70)
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45)
    mv.titles(fig, "Engagement is flat across all eight sites", "Engagement index by site, 2026 (0-100)")
    mv.source(fig, "Source: test")
    found = mv.lint(fig, quiet=True)
    assert {"bars-from-zero", "max-6-colors", "no-red-green"} <= rules(found, "error")
    assert {"palette", "no-rotated-labels"} <= rules(found, "warn")
    assert "direct-labels" in rules(found)
    with pytest.raises(mv.LintError):
        mv.lint(fig, strict=True, quiet=True)
    plt.close(fig)


def test_waterfall_break_is_a_warning_not_an_error():
    fig, ax = plt.subplots()
    ax.bar([0, 1, 2], [4210, 139, 4349], bottom=[0, 4210, 0], color=[C.total, C.context, C.total])
    ax.set_ylim(3900, 4500)
    mv.titles(fig, "Merit adds $139M to FY26 labor cost", "Labor cost bridge, FY25 to FY26 ($M)")
    mv.source(fig, "Source: test")
    found = mv.lint(fig, quiet=True)
    assert "bars-from-zero" in rules(found, "warn") and "bars-from-zero" not in rules(found, "error")
    plt.close(fig)


def test_sequential_ramp_counts_as_one_color():
    fig, ax = plt.subplots()
    ax.bar(range(6), [1] * 6, color=mv.SEQUENTIAL["blue"])
    ax.bar([7], [1], color=C.accent)
    mv.titles(fig, "Six classes and one accent use two encodings", "Test (count), 2026")
    mv.source(fig, "Source: test")
    assert "max-6-colors" not in rules(mv.lint(fig, quiet=True))
    plt.close(fig)


def test_dual_axis_and_tiny_text():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3], color=C.focus)
    ax.twinx().plot([1, 2, 3], [30, 20, 10], color=C.accent)
    ax.text(1, 1, "tiny", fontsize=5)
    mv.titles(fig, "Overtime rose 3 hours as vacancies doubled", "DC overtime and vacancies, 2026 (hours; %)")
    mv.source(fig, "Source: test")
    found = mv.lint(fig, quiet=True)
    assert {"no-dual-axis", "min-text-size"} <= rules(found, "warn")
    plt.close(fig)


def test_plotly_pie_and_html_titles():
    fig = go.Figure(go.Pie(labels=list("ABCDEFG"), values=[1] * 7))
    found = mv.lint(fig, headline="Seven parts split the total evenly at 14% each", subtitle="Share of total, 2026 (%)",
                    source="Source: test", quiet=True)
    assert "pie-max-5" in rules(found, "error")
    assert not {"headline", "subtitle", "source"} & rules(found, "error")


def test_plotly_bar_from_pl_finish_passes():
    fig = go.Figure(go.Bar(x=VALS, y=CATS, orientation="h", marker_color=mv.pl_highlight(CATS, focus=CATS[:2]),
                           text=[f"{v:.1f}%" for v in VALS], textposition="outside"))
    fig.update_xaxes(visible=False)
    mv.pl_finish(fig, "Two frontline job families lose about 1 in 4 people a year",
                 "Voluntary attrition by job family, FY26 (%)", "Source: Synthetic data for illustration only")
    found = mv.lint(fig, quiet=True)
    assert not [f for f in found if f.level in ("error", "warn")], found


def test_amber_is_do_not_use_and_orange_gets_a_semantic_reminder():
    fig = good_bar()
    ax = fig.axes[0]
    ax.patches[0].set_facecolor(mv.extended["amber"]["base"])
    assert "do-not-use" in rules(mv.lint(fig, quiet=True), "error")
    ax.patches[0].set_facecolor(C.orange)
    found = mv.lint(fig, quiet=True)
    assert "do-not-use" not in rules(found) and "orange-semantic" in rules(found, "info")
    plt.close(fig)


def test_uniform_accent_pattern_is_clean():
    fig = good_bar()
    for p, col in zip(fig.axes[0].patches, mv.highlight(CATS[::-1], accent=CATS[0], base=C.focus_light)):
        p.set_facecolor(col)
    found = mv.lint(fig, quiet=True)
    assert not [f for f in found if f.level in ("error", "warn")], found
    plt.close(fig)
