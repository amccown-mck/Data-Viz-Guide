"""Tests for mv.options_page: one self-contained HTML file, with every option's chart, notes and headline."""
from __future__ import annotations

import base64
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

import mckviz as mv  # noqa: E402


@pytest.fixture(autouse=True)
def _style():
    mv.use(plotly_default=False)
    yield
    plt.close("all")


def chart(headline):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(["A", "B"], [1, 2], color=mv.highlight(["A", "B"], focus="B"))
    mv.titles(fig, headline, "Metric by group, 2026 (%)")
    mv.source(fig, "Source: Synthetic data for illustration only")
    return fig


def option(i, **kw):
    return mv.Option(chart(f"Group B leads on view {i} by a wide margin"), name=f"View {i}",
                     question=f"What does view {i} answer?", how_to_read="Bars by group.", strength="Simple.",
                     tradeoff="Only two groups.", **kw)


def build(tmp_path, options, **kw):
    path = mv.options_page(tmp_path / "views.html", "Two groups: two ways to show it", options, **kw)
    return path.read_text(encoding="utf-8")


def test_page_has_every_option_and_takes_headlines_from_the_figures(tmp_path):
    html = build(tmp_path, [option(1), option(2), option(3)], lede="Three views.",
                 findings=[("B leads", "on every view."), "A trails."], notes={"Group": "A team."},
                 source="Source: Synthetic data for illustration only", label="Internal")
    assert html.count('<section class="option"') == 3
    assert html.count("<tr>") == 3                                            # the at-a-glance table
    for i in (1, 2, 3):
        assert f"Group B leads on view {i} by a wide margin" in html            # headline in the table and alt text
        assert f'id="opt{i}"' in html and f'href="#opt{i}"' in html
    for part in ("How to read it", "Strength", "Trade-off", "What the data shows", "<b>B leads:</b>",
                 "Definitions and data notes", "<footer>Source: Synthetic data", '<p class="label">Internal</p>'):
        assert part in html


def test_page_is_self_contained(tmp_path):
    html = build(tmp_path, [option(1), option(2)])
    assert not re.search(r'(src|href)="(https?:)?//', html)                    # nothing loaded from the web
    pngs = re.findall(r'src="data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
    assert len(pngs) == 2
    assert all(base64.b64decode(p)[:8] == b"\x89PNG\r\n\x1a\n" for p in pngs)
    assert "@font-face { font-family: 'Libre Franklin'" in html               # the font travels with the page
    assert "#" + mv.colors.focus.lstrip("#") in html                           # colors come from the tokens


def test_text_is_escaped(tmp_path):
    html = build(tmp_path, [option(1, alt='Say "<b>hi</b>" & go'), option(2)], findings=["<script>x</script>"])
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;x&lt;/script&gt;" in html
    assert 'alt="Say &quot;&lt;b&gt;hi&lt;/b&gt;&quot; &amp; go"' in html


def test_png_paths_and_suggested_lead(tmp_path):
    png = mv.save(chart("Group B leads by a wide margin on the saved view"), tmp_path / "saved.png", dpi=72)
    saved = mv.Option(png, name="Saved", question="Q?", how_to_read="R.", strength="S.", tradeoff="T.",
                      headline="Group B leads by a wide margin on the saved view")
    html = build(tmp_path, [option(1), saved], recommendation="Lead with the saved view.", lead=2)
    assert html.count('<span class="badge">Suggested lead</span>') == 1
    assert html.index("Suggested lead") > html.index('id="opt2"')
    assert "Where to start" in html


def test_bad_input_is_refused(tmp_path):
    with pytest.raises(ValueError, match="2 to 8"):
        build(tmp_path, [option(1)])
    with pytest.raises(ValueError, match="lead=3"):
        build(tmp_path, [option(1), option(2)], lead=3)
    fig, _ = plt.subplots()
    bare = mv.Option(fig, name="Bare", question="Q?", how_to_read="R.", strength="S.", tradeoff="T.")
    with pytest.raises(ValueError, match="mv.titles"):
        build(tmp_path, [option(1), bare])


def test_pdf_is_skipped_without_weasyprint(tmp_path, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "weasyprint", None)                     # import fails, as on most Windows PCs
    path = mv.options_page(tmp_path / "views.html", "Two groups: two ways to show it", [option(1), option(2)])
    assert mv.page_pdf(path) is None and not path.with_suffix(".pdf").exists()


def test_pdf_is_written_beside_the_page(tmp_path, monkeypatch):
    import sys
    import types

    calls = {}

    class HTML:                                                               # stands in for weasyprint.HTML
        def __init__(self, filename):
            calls["src"] = filename

        def write_pdf(self, target):
            open(target, "wb").write(b"%PDF-1.7")

    monkeypatch.setitem(sys.modules, "weasyprint", types.SimpleNamespace(HTML=HTML))
    path = mv.options_page(tmp_path / "views.html", "Two groups: two ways to show it", [option(1), option(2)])
    pdf = mv.page_pdf(path)
    assert pdf == path.with_suffix(".pdf") and pdf.read_bytes().startswith(b"%PDF")
    assert calls["src"] == str(path)


def test_working_files_stay_out_of_the_delivery_folder(tmp_path, monkeypatch):
    onedrive = tmp_path / "mnt-data"                      # stands in for Copilot's /mnt/data
    onedrive.mkdir()
    monkeypatch.setattr(mv, "DELIVER_DIR", onedrive)
    monkeypatch.chdir(onedrive)                           # the sandbox starts there, so a bare name lands in it
    fig = chart("Group B leads by a wide margin on this view")
    for attempt in (lambda: mv.save(fig, "chart.png"), lambda: mv.save(fig, onedrive / "chart.png"),
                    lambda: mv.options_page(onedrive / "views.html", "t", [option(1), option(2)]),
                    lambda: mv.page_pdf(onedrive / "views.html")):
        with pytest.raises(ValueError, match="/tmp first.*mv.deliver"):
            attempt()
    assert not list(onedrive.iterdir())                   # nothing written there
    work = tmp_path / "work"
    page = mv.options_page(work / "views.html", "Two groups: two ways to show it", [option(1), option(2)])
    png = mv.save(fig, work / "chart.png")
    assert mv.deliver(png, page) == [onedrive / "chart.png", onedrive / "views.html"]