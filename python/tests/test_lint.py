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


def test_headline_starting_with_a_digit_warns():
    fig = good_bar()
    found = mv.lint(fig, headline="2 frontline job families lose about 1 in 4 people a year", quiet=True)
    assert any(f.rule == "headline" and f.level == "warn" and "digit" in f.message for f in found)
    found = mv.lint(fig, headline="Two frontline job families lose about 1 in 4 people a year", quiet=True)
    assert not [f for f in found if f.rule == "headline"]
    plt.close(fig)


def test_glyph_the_font_lacks_warns_unless_a_fallback_family_has_it():
    fig = good_bar()
    ax = fig.axes[0]
    t = ax.text(5, 1, "\u25b6 Pharmacy Technician", fontsize=10)      # ▶ is not in Libre Franklin
    with pytest.warns(UserWarning, match="Glyph 9654"):                 # matplotlib's own notice when it draws the box
        found = mv.lint(fig, quiet=True)
    hits = [f for f in found if f.rule == "missing-glyph"]
    assert hits and hits[0].level == "warn" and "\u25b6" in hits[0].message
    t.set_fontfamily([mv.FONT, "DejaVu Sans"])                          # the builders' fallback for ▲▼
    assert not [f for f in mv.lint(fig, quiet=True) if f.rule == "missing-glyph"]
    t.set_text("\u2212 7.5 pts")                                        # true minus is in Libre Franklin
    t.set_fontfamily(mv.FONT)
    assert not [f for f in mv.lint(fig, quiet=True) if f.rule == "missing-glyph"]
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


def test_label_line_ends_nudges_close_labels_apart():
    fig, ax = plt.subplots(figsize=(6, 3))
    for i, v in enumerate([25.2, 23.8, 18.6]):
        ax.plot(range(5), [v] * 5, label=f"Series {i}")
    ax.set_ylim(0, 40)
    mv.label_line_ends(ax)
    to_pt = 72 / fig.dpi
    pos = sorted(ax.transData.transform(t.xy)[1] * to_pt + t.xyann[1] for t in ax.texts)
    gaps = [b - a for a, b in zip(pos, pos[1:])]
    assert min(gaps) >= 0.99 * (mv._role("label")["size_pt"] - 1) * 1.25, gaps
    plt.close(fig)


def test_lint_prints_on_a_console_that_cannot_encode_symbols(monkeypatch):
    import io
    import sys
    ascii_out = io.TextIOWrapper(io.BytesIO(), encoding="ascii")        # like a Windows pipe in CI
    monkeypatch.setattr(sys, "stdout", ascii_out)
    fig, ax = plt.subplots()
    ax.pie([1] * 7)
    found = mv.lint(fig)                                                 # findings contain "≤"; must not raise
    assert any(f.rule == "pie-max-5" for f in found)
    plt.close(fig)


def test_status_colors_are_allowed_on_a_tracker_but_amber_is_not_a_series_color():
    fig, ax = plt.subplots()
    s = mv.STATUS
    ax.scatter([0, 1, 2, 3], [0, 0, 0, 0], s=200,
               color=[s["on_track"]["value"], s["at_risk"]["value"], s["off_track"]["value"], s["not_started"]["value"]])
    mv.titles(fig, "Two of four workstreams are at risk or off track", "Workstream status, Mar 2026")
    mv.source(fig, "Source: PMO tracker (synthetic data for illustration)")
    found = mv.lint(fig, quiet=True)
    assert not [f for f in found if f.rule in ("no-red-green", "do-not-use")], found
    assert any(f.rule == "status-colors" for f in found)
    plt.close(fig)

    fig, ax = plt.subplots()                                   # amber as a plain series color is still an error
    ax.bar([0, 1], [3, 4], color=[s["at_risk"]["value"], C.focus])
    assert any(f.rule == "do-not-use" for f in mv.lint(fig, quiet=True))
    plt.close(fig)


# ----------------------------------------------------------------------------------------------- colormaps and images
def _titled(fig):
    mv.titles(fig, "Three of five sites run more than 4 points above the benchmark", "Gap to benchmark by site, 2026 (pts)")
    mv.source(fig, "Source: test")
    return fig


@pytest.mark.parametrize("cmap", [mv.sequential_cmap(), mv.sequential_cmap("teal"), mv.sequential_cmap("orange"),
                                  mv.diverging_cmap()])
def test_imshow_heatmap_with_token_cmap_is_one_on_palette_color(cmap):
    import numpy as np

    fig, ax = plt.subplots()
    ax.imshow(np.arange(64, dtype=float).reshape(8, 8), cmap=cmap)
    found = mv.lint(_titled(fig), quiet=True)
    assert not {"max-6-colors", "palette"} & rules(found), found
    plt.close(fig)


def test_color_mapped_scatter_and_pcolormesh_with_token_cmaps_pass():
    import numpy as np

    fig, (a, b) = plt.subplots(1, 2)
    x = np.linspace(-1, 1, 40)
    a.scatter(x, x ** 2, c=x, cmap=mv.diverging_cmap())
    b.pcolormesh(np.arange(30, dtype=float).reshape(5, 6), cmap=mv.sequential_cmap())
    found = mv.lint(_titled(fig), quiet=True)
    assert not {"max-6-colors", "palette"} & rules(found), found
    plt.close(fig)


def test_imshow_is_seen_and_an_off_palette_cmap_still_fails():
    import numpy as np

    fig, ax = plt.subplots()
    ax.imshow(np.arange(64, dtype=float).reshape(8, 8), cmap="viridis")
    found = mv.lint(_titled(fig), quiet=True)
    assert "palette" in rules(found, "warn")
    assert "max-6-colors" in rules(found, "error")
    plt.close(fig)


def test_single_off_palette_color_near_a_ramp_end_is_still_flagged():
    fig, ax = plt.subplots()
    ax.bar([0, 1], [1, 2], color=[C.focus, "#7A3FD1"])          # purple: on no ramp
    found = mv.lint(_titled(fig), quiet=True)
    assert "palette" in rules(found, "warn")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------- Plotly gaps
HEAD = dict(headline="Two frontline job families lose about 1 in 4 people a year",
            subtitle="Voluntary attrition by job family, FY26 (%)", source="Source: test", quiet=True)


@pytest.mark.parametrize("trace", [go.Scatter3d(x=[1, 2], y=[1, 2], z=[1, 2]), go.Surface(z=[[1, 2], [3, 4]]),
                                   go.Mesh3d(x=[0, 1, 0], y=[0, 0, 1], z=[0, 1, 1])])
def test_plotly_3d_traces_are_errors(trace):
    assert "no-3d" in rules(mv.lint(go.Figure(trace), **HEAD), "error")


def test_plotly_third_y_axis_is_an_error_and_subplots_are_not():
    from plotly.subplots import make_subplots

    fig = go.Figure([go.Scatter(y=[1, 2], line_color=C.focus), go.Scatter(y=[2, 1], yaxis="y2", line_color=C.accent),
                     go.Scatter(y=[3, 4], yaxis="y3", line_color=C.context)])
    fig.update_layout(yaxis2=dict(overlaying="y", side="right"), yaxis3=dict(overlaying="y", anchor="free"))
    assert "no-dual-axis" in rules(mv.lint(fig, **HEAD), "error")
    lone = go.Figure([go.Scatter(y=[1, 2]), go.Scatter(y=[3, 4], yaxis="y3")])
    assert "no-dual-axis" in rules(mv.lint(lone, **HEAD), "warn")
    panels = make_subplots(rows=3, cols=1)
    for i in range(3):
        panels.add_trace(go.Scatter(y=[1, 2], line_color=C.focus), row=i + 1, col=1)
    assert "no-dual-axis" not in rules(mv.lint(panels, **HEAD))


def test_plotly_texttemplate_counts_as_bar_labels():
    fig = go.Figure(go.Bar(x=VALS, y=CATS, orientation="h", texttemplate="%{x:.1f}%",
                           marker_color=mv.pl_highlight(CATS, focus=CATS[:2])))
    assert "labels-or-axis" in rules(mv.lint(fig, **HEAD), "warn")
    fig.update_xaxes(visible=False)
    assert "labels-or-axis" not in rules(mv.lint(fig, **HEAD))


def test_plotly_text_below_minimum_size_warns():
    fig = go.Figure(go.Bar(x=VALS, y=CATS, orientation="h", text=VALS, textfont_size=8, marker_color=C.focus))
    fig.update_xaxes(visible=False)
    fig.add_annotation(text="note", font_size=7, x=1, y=1, showarrow=False)
    found = mv.lint(fig, **HEAD)
    assert "min-text-size" in rules(found, "warn")
    assert "7" in next(f.message for f in found if f.rule == "min-text-size")
    fig.update_traces(textfont_size=12)
    fig.layout.annotations[0].font.size = 12
    assert "min-text-size" not in rules(mv.lint(fig, **HEAD))


def test_categorical_series_do_not_collapse_into_a_ramp():
    fig, ax = plt.subplots()
    colors = mv.CATEGORICAL + [mv.FILL_TINTS[0]]                     # 7 distinct non-grey fills
    ax.bar(range(7), [1] * 7, color=colors)
    found = mv.lint(_titled(fig), quiet=True)
    assert "max-6-colors" in rules(found, "error")                  # blue + navy + orange are not "the diverging ramp"
    assert "orange-semantic" in rules(found, "info")
    plt.close(fig)


def test_repeated_period_labels_as_x_are_flagged_in_both_backends():
    # matplotlib: "Q2" three times collapses to one category, so the line folds back on itself
    fig, ax = plt.subplots()
    ax.plot(["Q1 '24", "Q2", "Q3", "Q4", "Q1 '25", "Q2", "Q3"], [1, 2, 3, 4, 5, 6, 7], color=C.focus)
    mv.titles(fig, "Attrition fell three points after the reset", "Attrition by quarter, FY24–FY25 (%)")
    mv.source(fig, "Source: test")
    assert "x-repeats" in rules(mv.lint(fig, quiet=True), "warn")
    # unique periods pass, and so does a vertical rule (two points, same x) and a connected scatter with no repeats
    fig, ax = plt.subplots()
    ax.plot(["Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24", "Q1 '25"], [1, 2, 3, 4, 5], color=C.focus)
    ax.axvline(2, color=C.axis)
    ax.plot([1.0, 3.0, 2.0], [1, 2, 3], color=C.context)
    mv.titles(fig, "Attrition fell three points after the reset", "Attrition by quarter, FY24–FY25 (%)")
    mv.source(fig, "Source: test")
    assert "x-repeats" not in rules(mv.lint(fig, quiet=True), "warn")
    # plotly: same trap on a category axis; a fill-to-self band legitimately repeats x and is not flagged
    fig = go.Figure(go.Scatter(x=["Q1 '24", "Q2", "Q3", "Q4", "Q1 '25", "Q2"], y=[1, 2, 3, 4, 5, 6], mode="lines",
                               line_color=C.focus))
    assert "x-repeats" in rules(mv.lint(fig, **HEAD), "warn")
    band = go.Scatter(x=["a", "b", "c", "c", "b", "a"], y=[1, 2, 3, 4, 3, 2], fill="toself", line_width=0)
    line = go.Scatter(x=["a", "b", "c"], y=[1, 2, 3], mode="lines", line_color=C.focus)
    assert "x-repeats" not in rules(mv.lint(go.Figure([band, line]), **HEAD), "warn")
