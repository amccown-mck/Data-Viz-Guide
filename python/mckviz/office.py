"""mckviz.office - native, editable PowerPoint slides in the house style (needs python-pptx).

    from mckviz import office                  # or mv.office
    prs = office.deck()                        # the McKesson branded template: master, logo, footer, Libre Franklin
    office.bar_slide(prs, df.job_family, df.vol_attrition_pct, focus={"Pharmacy Technician"},
                     headline="Pharmacy technicians lose 1 in 4 people a year, above the 19.9% enterprise rate",
                     subtitle="Voluntary attrition by job family, FY26 (%)", source="Source: Workday HCM, as of ...",
                     benchmark=19.9, benchmark_label="Enterprise 19.9%", fmt="{:.1f}%")
    path = office.save(prs, "/tmp/attrition.pptx")  # check it here (render, validate) ...
    office.deliver(path)                            # ... then one copy to /mnt/data (Copilot: the user's OneDrive)

Each slide is a real PowerPoint chart (right-click › Edit Data works): bar_slide (a ranking), column_slide (periods or
stages), line_slide (over time), stack_slide (parts of a whole), waterfall_slide (a bridge) and dumbbell_slide
(us vs. a comparator); picture_slide puts any other mckviz figure on the slide as a picture. Each has the headline
in the title placeholder (Bold McKesson Blue, 34 pt down to 26 to fit), the subtitle, the chart, and the source at
9 pt bottom-left above the footer. Geometry is computed from the text, measured with the bundled Libre Franklin, so
labels fit and never sit on a benchmark line. The slide helpers below are shared with office/build_office.py, which
builds the template and the starter deck.
"""
from __future__ import annotations

import re
import warnings
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, Sequence

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE, XL_TICK_MARK
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from . import FONT, TOKENS, colors as C, few_highlights, text_on

_HERE = Path(__file__).resolve().parent
TEMPLATE = _HERE / "template.pptx"
FONTS = _HERE / "fonts"
SEMI, MEDIUM = f"{FONT} SemiBold", f"{FONT} Medium"
BAND_GAP = int(round((1 - TOKENS["chart"]["bar"]["band_fill"]) / TOKENS["chart"]["bar"]["band_fill"] * 100, -1))  # 50%

# Slide geometry (16:9, inches)
W, H = 13.333, 7.5
# The McKesson Standard Template's grid: 0.39 in side margins, title box 0.38-1.31 in, footer and logo at 7.13 in.
LEFT, RIGHT = 0.39, 0.39
TITLE_TOP, TITLE_H, TITLE_PT = 0.38, 0.93, 26              # typography.roles.slide_title: Bold, McKesson Blue, 24-28 pt
TITLE_LINES = {34: 1, 30: 1, 28: 2, 26: 2}     # lines each size may take in the 0.93 in title box (a line ~1.14 x size)
SUB_TOP, CHART_TOP, CHART_H = 1.32, 1.8, 4.6
FOOT_TOP = 6.45                                            # source / footnote block ends at 6.95 in, above the footer
BODY_TOP, BODY_BOTTOM = 1.32, 6.95                         # content area: under the title box, above the source line
# Footer (as in the Standard Template): page number | thin blue rule | confidentiality line | date, centred on 7.2 in.
FOOTER_TOP, FOOTER_H, FOOTER_PT = 7.08, 0.24, 8
# Two chart widths on a one-chart slide: full width, or chart + insights (the chart two-thirds, a gutter as wide as
# the two-charts slide's, and the insights panel the right third).
GUTTER = 0.5
SIDE_CHART_W = (W - LEFT - RIGHT - GUTTER) * 2 / 3          # 8.04 in
TAKE_LEFT = LEFT + SIDE_CHART_W + GUTTER
TAKE_W = W - RIGHT - TAKE_LEFT                               # 4.02 in
# The insights panel sits in the same place on every slide; plot areas line up with it (PLOT_Y, PLOT_H are fractions
# of the chart frame), so the chart's top and baseline meet the card's top and bottom edges.
CARD_TOP, CARD_BOTTOM = CHART_TOP + 0.15, 6.0
PLOT_Y, PLOT_H = (CARD_TOP - CHART_TOP) / CHART_H, (CARD_BOTTOM - CARD_TOP) / CHART_H
FOOTER_TEXT = "McKesson Proprietary and Confidential"
MASTER_NAME = "McKesson Data Viz"
AUTHOR = "McKesson Workforce Innovation"
TODAY = datetime.now()
DATE_TEXT = f"{TODAY.month}/{TODAY.day}/{TODAY.year}"        # placeholder text; PowerPoint updates the date field
C15 = "http://schemas.microsoft.com/office/drawing/2012/chart"


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color.lstrip("#").upper())


def flat(shape) -> None:
    """No theme effect (shadow, glow, bevel) on a drawn shape or connector: effectRef idx 0."""
    ref = shape._element.find(".//" + qn("a:effectRef"))
    if ref is not None:
        ref.set("idx", "0")


# ====================================================================== text measurement
@lru_cache(maxsize=None)
def _font(weight: str, size: float):
    from matplotlib.font_manager import FontProperties
    return FontProperties(fname=str(FONTS / f"LibreFranklin-{weight}.ttf"), size=size)


def text_width(text: str, size: float, weight: str = "Regular", tracking: float = 0.0) -> float:
    """Width in inches of one line of `text` at `size` pt in the bundled Libre Franklin; `tracking` is PowerPoint's
    character spacing in pt (a:rPr spc / 100), added after every character."""
    from matplotlib.textpath import TextToPath
    width = TextToPath().get_text_width_height_descent(text, _font(weight, size), ismath=False)[0]
    return (width + tracking * len(text)) / 72


def wrapped_lines(text, size, width, weight="Regular", tracking=0.0) -> int:
    """How many lines `text` wraps to in a `width`-inch box at `size` pt: greedy word wrap, measured with the bundled
    Libre Franklin, so a caption that would spill is caught at build time, not on the slide."""
    lines, line = 1, ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, size, weight, tracking) > width:
            lines, line = lines + 1, word
        else:
            line = trial
    return lines


# ====================================================================== slide furniture
def _shapes(target):
    """A slide or a group shape -> its shape collection (so helpers can draw into a group)."""
    return target.shapes if hasattr(target, "shapes") else target


def text_box(slide, left, top, width, height, text, size, color, bold=False, light=False, anchor=MSO_ANCHOR.TOP,
             align=PP_ALIGN.LEFT, font=None, name=None, wrap=True):
    """Text box with zero insets. `font` names a weight explicitly (e.g. "Libre Franklin SemiBold")."""
    box = _shapes(slide).add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    if name:
        box.name = name
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
        run.font.name = font or (f"{FONT} Light" if light else FONT)
    return box


def layout(prs, name: str, fallback: int):
    """A layout by name (the official template), else the default template's layout by index."""
    return next((l for l in prs.slide_layouts if l.name == name), prs.slide_layouts[fallback])


def on_grid(prs_or_layout) -> bool:
    """True for the kit's own master (already on the grid); False for the official template."""
    master = prs_or_layout.slide_master._element
    return master.find(qn("p:cSld")).get("name") == MASTER_NAME


def add_footer(slide, lay) -> None:
    """Copy the layout's slide-number and date placeholders onto the slide (python-pptx doesn't), with live fields,
    so the official template's footer reads: page | McKesson Proprietary and Confidential | date."""
    kinds = (13, 15, 16) if on_grid(lay) else (13, 16)
    for ph in lay.placeholders:
        kind = ph.placeholder_format.type
        if kind not in kinds:                                  # SLIDE_NUMBER, FOOTER (kit master only), DATE
            continue
        slide.shapes.clone_placeholder(ph)
        p = slide.placeholders[ph.placeholder_format.idx].text_frame.paragraphs[0]._p
        if kind == 15:
            r = etree.SubElement(p, qn("a:r"))
            etree.SubElement(r, qn("a:rPr"), lang="en-US")
            etree.SubElement(r, qn("a:t")).text = FOOTER_TEXT
            continue
        fld = etree.SubElement(p, qn("a:fld"))
        fld.set("id", "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" if kind == 13 else "{3A1B2C4D-5E6F-4A7B-8C9D-0E1F2A3B4C5D}")
        fld.set("type", "slidenum" if kind == 13 else "datetime1")
        etree.SubElement(fld, qn("a:t")).text = "‹#›" if kind == 13 else DATE_TEXT


BRAND_TITLE_PT = (34, 30, 28, 26)      # the branded master's 34 pt, stepped down until the headline fits the box
BRAND_TITLE_TRACKING = -0.84           # pt per character: the branded master's title style (spc="-84"), at any size


def title_size(headline: str, width: float = W - LEFT - RIGHT) -> int:
    """The branded master's title size (34 pt) when the headline fits on one line, else 30 pt on one line, else 28 or
    26 pt on two (two lines of 30 pt or more overflow the title box into the subtitle). Measured in Libre Franklin
    Bold. A headline that needs three lines even at 26 pt would run into the subtitle: ValueError, shorten it."""
    for size in BRAND_TITLE_PT:
        if wrapped_lines(headline, size, width, "Bold", BRAND_TITLE_TRACKING) <= TITLE_LINES[size]:
            return size
    raise ValueError(f"the headline needs three lines even at 26 pt and would run into the subtitle; shorten it "
                     f"(two lines hold about 150 characters): {headline!r}")


def chart_slide(prs, headline, subtitle, footnote, notes, source):
    """Title Only layout: headline in the title placeholder, subtitle, then source/footnote bottom-left."""
    lay = layout(prs, "Title Only", 5)
    slide = prs.slides.add_slide(lay)
    title = slide.shapes.title
    title.text = headline                                      # position, size, weight and color come from the master
    if not on_grid(prs):                                       # the branded template: place the title on its grid
        title.left, title.top = Inches(LEFT), Inches(TITLE_TOP)
        title.width, title.height = Inches(W - LEFT - RIGHT), Inches(TITLE_H)
        tf = title.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = True
        size = title_size(headline)
        for r in tf.paragraphs[0].runs:                        # the master's 34 pt when it fits, else down to 26
            r.font.size = Pt(size)
            r.font.bold = True
    if subtitle:
        text_box(slide, LEFT, SUB_TOP, W - LEFT - RIGHT, 0.35, subtitle, 14, C.text)
    foot = "\n".join(x for x in (footnote, source) if x)
    if foot:
        text_box(slide, LEFT, FOOT_TOP, W - LEFT - RIGHT, 0.5, foot, 9, C.text_muted, light=True,
                 anchor=MSO_ANCHOR.BOTTOM)
    if lay.name == "Title Only":
        add_footer(slide, lay)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


def shape(target, kind, left, top, width, height, color=None, line=None, line_w=0.75, dash=False, name=None):
    """A flat autoshape: solid fill (or none), optional outline, effectRef 0."""
    s = _shapes(target).add_shape(kind, Inches(left), Inches(top), Inches(width), Inches(height))
    if color:
        fill(s, color)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(line_w)
        if dash:
            s.line.dash_style = 4
    else:
        s.line.fill.background()
    flat(s)
    if name:
        s.name = name
    return s


def shape_text(s, text, size, color, font=FONT, align=PP_ALIGN.CENTER, bold=False):
    tf = s.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.name = Pt(size), bold, font
    r.font.color.rgb = rgb(color)


def line_shape(slide, x1, y1, x2, y2, color, width_pt=0.75, dash=True, arrow=False, name=None):
    ln = _shapes(slide).add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(width_pt)
    if dash:
        ln.line.dash_style = 4          # MSO_LINE_DASH_STYLE.DASH
    if arrow:                           # arrowhead at the end point
        etree.SubElement(ln.line._get_or_add_ln(), qn("a:tailEnd"), type="triangle", w="med", len="med")
    if name:
        ln.name = name
    flat(ln)
    return ln


_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _numbers(text: str) -> set[str]:
    """The numbers written in a text, commas dropped ("6,200" -> "6200"), to compare an insight with the chart."""
    return {n.replace(",", "") for n in _NUM.findall(text)}


def _tracked(box, spacing_pt: float) -> None:
    """Letter-spacing on every run of a text box (PowerPoint's character spacing), for the small capitals labels."""
    for para in box.text_frame.paragraphs:
        for run in para.runs:
            run._r.get_or_add_rPr().set("spc", str(int(spacing_pt * 100)))


def _check_insights(insights, implication, big, shown) -> list[tuple[str, str, str | None]]:
    """Normalise the panel's content and say when it only repeats the chart: an insight whose numbers are all already
    labels on the chart adds nothing the reader can't see. Returns (claim, evidence, at) triples."""
    items = []
    for it in insights or ():
        if isinstance(it, str) or not 2 <= len(it) <= 3:
            raise ValueError("each insight is (claim, evidence) or (claim, evidence, at): a bold one-line claim, then "
                             "the evidence behind it; `at` names the bar or point its number marker goes on")
        items.append((str(it[0]), str(it[1]), str(it[2]) if len(it) == 3 and it[2] is not None else None))
    if not 1 <= len(items) + bool(big) <= 4 or len(items) > 3:
        raise ValueError("one to three insights (plus a big number, if one derived number is the point)")
    seen = set().union(*(_numbers(s) for s in shown)) if shown else set()
    for i, (claim, evidence, _) in enumerate(items, 1):
        nums = _numbers(claim + " " + evidence)
        if nums and nums <= seen:
            warnings.warn(f"insight {i} only repeats numbers the chart already shows ({', '.join(sorted(nums))}): say "
                          "what they add up to, how they compare, or why, so the panel adds to the chart",
                          stacklevel=4)
    if big and _numbers(big[0]) and _numbers(big[0]) <= seen:
        warnings.warn(f"the big number {big[0]!r} is already a label on the chart: use it for a derived number "
                      "(a share of the total, a gap, a multiple), or drop it", stacklevel=4)
    if implication is not None and not str(implication).strip():
        raise ValueError("implication is a sentence, or None")
    return items


MARKER = 0.24                                              # a number marker on the chart (in)


def _marker(target, x, y, n, name) -> None:
    """A navy circle with a white number, centred on (x, y): ties a point on the chart to its insight."""
    dot = shape(target, MSO_SHAPE.OVAL, x - MARKER / 2, y - MARKER / 2, MARKER, MARKER, C.headline, name=name)
    shape_text(dot, str(n), 10, "#FFFFFF", font=FONT, bold=True)


def _marked(insights) -> set[str]:
    """The names the insights put a marker on (their `at`)."""
    return {str(it[2]) for it in insights or () if not isinstance(it, str) and len(it) == 3 and it[2] is not None}


def insights_panel(slide, insights, *, implication: str | None = None, big: tuple[str, str] | None = None,
                   title: str = "Key insights", shown: Iterable[str] = (), anchors: dict | None = None,
                   marked: Iterable[int] = ()):
    """Chart + insights: the right third of the slide (TAKE_LEFT, TAKE_W) beside a two-thirds chart, top-aligned with
    the plot, in the quiet consulting style: a small capitals label over a navy hairline, no box, no fill.

    insights: one to three (claim, evidence) pairs, or (claim, evidence, at): the claim a bold navy line (two at
        most) that says something the chart doesn't show on its own (what the bars add up to, a comparison, a cause),
        the evidence one to three lines under it. `at` names the bar or column the insight is about, and puts its
        number there (native bar and column slides; on a picture, mv.mark on the figure). The insights are numbered
        only when every one has its marker on the chart; otherwise none is, since a number with no match on the chart
        reads as a mistake. implication: an optional last item under "What it means": what the finding means for the
        business, from the data (a recommendation is the user's call, worked out with them). big: (number, caption) at the top, only when
        one derived number is the whole point ("73%", "of voluntary exits come from two job families").
    shown: the labels the chart carries; an insight that only repeats them raises a warning. anchors: {name: (x, y)}
    where each bar's marker goes (the slide builders pass it); marked: the mv.mark numbers already on a picture.
    Returns the group."""
    items = _check_insights(insights, implication, big, shown)
    ats = [at for *_, at in items]
    for i, at in enumerate(ats, 1):
        if at is not None and anchors is None:
            raise ValueError(f"insight {i}: this slide type can't place a marker yet (at={at!r}). On a picture slide, "
                             "put it on the figure with mv.mark(ax, n, ...); on bar and column slides, at= names a bar")
        if at is not None and at not in anchors:
            raise ValueError(f"insight {i}: at={at!r} is not a bar on the chart: {', '.join(anchors)}")
    marked = set(marked)
    if any(ats):                                                # numbered only if every insight has its marker
        numbered = all(ats)
        if not numbered:
            loose = [str(i) for i, at in enumerate(ats, 1) if at is None]
            warnings.warn(f"insight {', '.join(loose)} has no at=, so no marker on the chart: the insights are shown "
                          "unnumbered and no markers are drawn. Give every insight an at=, or none", stacklevel=3)
        else:
            for i, at in enumerate(ats, 1):
                _marker(slide, *anchors[at], i, f"Marker {i}: {at}")
    elif marked:                                                # a picture whose figure carries mv.mark numbers
        numbered = marked == set(range(1, len(items) + 1))
        if not numbered:
            warnings.warn(f"the figure's markers ({', '.join(map(str, sorted(marked)))}) don't match insights 1 to "
                          f"{len(items)}: the insights are shown unnumbered. Mark each insight once, or none",
                          stacklevel=3)
    else:
        numbered = False
    x, w = TAKE_LEFT, TAKE_W
    mark, gap_x = (0.30, 0.14) if numbered else (0.0, 0.0)    # number marker, and the gap before the text
    tx, tw = x + mark + gap_x, w - mark - gap_x
    lh = {14: 0.235, 12: 0.205, 13: 0.22, 40: 0.62}          # line heights (in) at each size, 1.2 x the size
    for claim, evidence, _ in items:
        if wrapped_lines(claim, 14, tw, "Bold") > 2:
            raise ValueError(f"insight claim over two lines; make it one short claim: {claim!r}")
        if wrapped_lines(evidence, 12, tw) > 3:
            raise ValueError(f"insight evidence over three lines; keep the one fact that backs the claim: {evidence!r}")
    if big:
        if wrapped_lines(big[0], 40, w, "Bold") != 1:
            raise ValueError(f"big number wraps; shorten it: {big[0]!r}")
        if wrapped_lines(big[1], 14, w) > 2:
            raise ValueError(f"big number caption over two lines; shorten it: {big[1]!r}")
    if implication and wrapped_lines(implication, 13, w) > 4:
        raise ValueError(f"implication over four lines; one or two sentences: {implication!r}")

    g = slide.shapes.add_group_shape()
    g.name = "Insights"
    y = CARD_TOP
    label = text_box(g, x, y, w, 0.2, title.upper(), 10, C.focus, bold=True, name="Insights label", wrap=False)
    _tracked(label, 1.2)
    y += 0.27
    line_shape(g, x, y, x + w, y, C.headline, dash=False, name="Insights rule")
    y += 0.22
    if big:
        text_box(g, x, y, w, lh[40], big[0], 40, C.focus, bold=True, name="Big number")
        y += lh[40]
        n = wrapped_lines(big[1], 14, w)
        text_box(g, x, y, w, n * lh[14], big[1], 14, C.text, name="Big number caption")
        y += n * lh[14] + 0.2
        if items or implication:
            line_shape(g, x, y, x + w, y, C.context_light, dash=False, name="Big number rule")
            y += 0.2
    for i, (claim, evidence, _) in enumerate(items, 1):
        if i > 1:
            line_shape(g, tx, y, x + w, y, C.context_light, dash=False, name=f"Insight rule {i}")
            y += 0.2
        if numbered:
            dot = shape(g, MSO_SHAPE.OVAL, x, y + 0.01, mark, mark, C.headline, name=f"Insight {i}: marker")
            shape_text(dot, str(i), 11, "#FFFFFF", font=FONT, bold=True)
        nc, ne = wrapped_lines(claim, 14, tw, "Bold"), wrapped_lines(evidence, 12, tw)
        text_box(g, tx, y, tw, nc * lh[14], claim, 14, C.headline, bold=True, name=f"Insight {i}: claim")
        y += nc * lh[14] + 0.05
        text_box(g, tx, y, tw, ne * lh[12], evidence, 12, C.text, name=f"Insight {i}: evidence")
        y += ne * lh[12] + 0.2
    if implication:
        line_shape(g, x, y, x + w, y, C.headline, dash=False, name="Implication rule")
        y += 0.16
        lab = text_box(g, x, y, w, 0.2, "WHAT IT MEANS", 10, C.focus, bold=True, name="Implication label", wrap=False)
        _tracked(lab, 1.2)
        y += 0.28
        n = wrapped_lines(implication, 13, w)
        text_box(g, x, y, w, n * lh[13], implication, 13, C.headline, name="Implication")
        y += n * lh[13]
    if y > CARD_BOTTOM + 0.3:
        raise ValueError(f"the insights run {y - CARD_BOTTOM:.1f} in past the chart's bottom: fewer insights, or "
                         "shorter evidence")
    nf = slide.notes_slide.notes_text_frame
    nf.text += (f"\n\nLayout: chart + insights. The chart is two-thirds of the width ({SIDE_CHART_W:.2f} in); the "
                f"insights are the right third ({TAKE_W:.2f} in), top-aligned with the plot. Each insight is a claim the "
                "chart doesn't show on its own, then the fact behind it; its number matches the marker on the chart. "
                "Retype them for your data (each is its own text box in the Insights group).")
    return g


def takeaways_card(slide, points, title="Key takeaways"):
    """Replaced by insights_panel (2026-11-03): the (number, caption) card repeated the chart's numbers."""
    raise TypeError("takeaways are now insights: insights=[(claim, evidence), ...], each a bold claim the chart "
                    "doesn't show on its own and the fact behind it (office.insights_panel)")


def add_chart(slide, chart_type, data, top=CHART_TOP, height=CHART_H, left=LEFT, width=None):
    width = width or (W - LEFT - RIGHT)
    frame = slide.shapes.add_chart(chart_type, Inches(left), Inches(top), Inches(width), Inches(height), data)
    chart = frame.chart
    chart.has_title = False                    # the slide title is the headline
    chart.has_legend = False
    chart.font.name = FONT
    chart.font.size = Pt(12)
    chart.font.color.rgb = rgb(C.text)
    no_rounded_corners(chart._chartSpace)
    return frame, chart


def no_rounded_corners(chart_space) -> None:
    """Flat, not rounded: <c:roundedCorners val="0"/> (Office rounds the chart border when the element is missing)."""
    old = chart_space.find(qn("c:roundedCorners"))
    if old is None:
        old = etree.Element(qn("c:roundedCorners"))
        after = [chart_space.find(qn(t)) for t in ("c:date1904", "c:lang")]
        after = [e for e in after if e is not None]
        if after:
            after[-1].addnext(old)
        else:
            chart_space.insert(0, old)
    old.set("val", "0")


def plot_layout(chart, x, y, w, h) -> None:
    """Pin the inner plot area (fractions of the chart frame) so drawn overlays line up with the data."""
    plot_area = chart._chartSpace.chart.plotArea
    old = plot_area.find(qn("c:layout"))
    if old is not None:
        plot_area.remove(old)
    layout = etree.SubElement(plot_area, qn("c:layout"))
    plot_area.insert(0, layout)
    manual = etree.SubElement(layout, qn("c:manualLayout"))
    for tag, val in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"),
                     ("x", x), ("y", y), ("w", w), ("h", h)):
        etree.SubElement(manual, qn(f"c:{tag}")).set("val", str(val))


def points_on_edges(chart) -> None:
    """Line chart: put the first and last categories on the plot's edges (Axis Position › On tick marks) instead of
    the middle of their bands, so a two-period slope uses the plot's full width."""
    va = chart._chartSpace.find(".//" + qn("c:valAx"))
    el = va.find(qn("c:crossBetween"))
    if el is None:
        el = etree.Element(qn("c:crossBetween"))
        next(e for e in (va.find(qn(t)) for t in ("c:crossesAt", "c:crosses")) if e is not None).addnext(el)
    el.set("val", "midCat")


def legend_top_left(chart) -> None:
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(12)
    leg = chart._chartSpace.chart.find(qn("c:legend"))
    layout = leg.find(qn("c:layout"))
    if layout is None:
        layout = etree.SubElement(leg, qn("c:layout"))
        leg.find(qn("c:legendPos")).addnext(layout)
    manual = etree.SubElement(layout, qn("c:manualLayout"))
    for tag, val in (("xMode", "edge"), ("yMode", "edge"), ("x", 0.0), ("y", 0.0), ("w", 0.42), ("h", 0.07)):
        etree.SubElement(manual, qn(f"c:{tag}")).set("val", str(val))


def no_fill(series) -> None:
    series.format.fill.background()
    series.format.line.fill.background()


def fill(target, hex_color) -> None:
    """Solid fill for a chart series/point (.format.fill) or an autoshape (.fill)."""
    f = target.format.fill if hasattr(target, "format") else target.fill
    f.solid()
    f.fore_color.rgb = rgb(hex_color)


def baseline(axis, visible=True) -> None:
    axis.major_tick_mark = XL_TICK_MARK.NONE
    axis.minor_tick_mark = XL_TICK_MARK.NONE
    if visible:
        axis.format.line.color.rgb = rgb(C.axis)
        axis.format.line.width = Pt(0.75)
    else:
        axis.format.line.fill.background()


def point_label(point, text, color, bold=False, size=12, position=None):
    dl = point.data_label
    dl.has_text_frame = True
    dl.text_frame.text = text
    run = dl.text_frame.paragraphs[0].runs[0]
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = FONT if bold else MEDIUM                    # typography.roles.label: Medium; emphasis: Bold
    run.font.color.rgb = rgb(color)
    if position is not None:
        dl.position = position


def dlbl(point, *, val=False, cat=False, ser=False, pos=None, num_fmt=None, size=12, color=C.text, bold=False,
         sep=" ", text=None, dx=0.0, dy=0.0, box=None, align=None):
    """One data label: which fields it shows (for XY charts 'cat' is the X value, 'val' the Y value), position, number
    format, font (Medium; Bold when emphasized), or fixed `text`; dx/dy nudge it (fractions of the chart frame);
    box=(w, h) sizes the label (fractions of the frame), so a long one stays on one line instead of wrapping at about
    a fifth of the chart's width; align ("l" / "r") then sets which side of the box the text keeps to."""
    if text is not None:
        point_label(point, text, color, bold=bold, size=size, position=pos)
        d = point.data_label._dLbl
    else:
        dl = point.data_label
        f = dl.font
        f.size, f.bold, f.name = Pt(size), bold, FONT if bold else MEDIUM
        f.color.rgb = rgb(color)
        if pos is not None:
            dl.position = pos
        d = dl._dLbl
        for tag, on in (("showLegendKey", 0), ("showVal", val), ("showCatName", cat), ("showSerName", ser),
                        ("showPercent", 0), ("showBubbleSize", 0)):
            el = d.find(qn(f"c:{tag}"))
            if el is None:
                el = etree.SubElement(d, qn(f"c:{tag}"))
            el.set("val", "1" if on else "0")
        if sum(map(bool, (val, cat, ser))) > 1:
            etree.SubElement(d, qn("c:separator")).text = sep
        if num_fmt:
            nf = etree.Element(qn("c:numFmt"), formatCode=num_fmt, sourceLinked="0")
            anchor = next(e for e in (d.find(qn(t)) for t in ("c:spPr", "c:txPr", "c:dLblPos", "c:showLegendKey"))
                          if e is not None)
            anchor.addprevious(nf)
    if dx or dy:
        lay = etree.Element(qn("c:layout"))
        man = etree.SubElement(lay, qn("c:manualLayout"))
        etree.SubElement(man, qn("c:x"), val=f"{dx:.4f}")
        etree.SubElement(man, qn("c:y"), val=f"{dy:.4f}")
        d.find(qn("c:idx")).addnext(lay)
    if box:                                                    # Format Data Label › Size (Office 2013+ extension)
        ext_lst = d.find(qn("c:extLst"))
        if ext_lst is None:
            ext_lst = etree.SubElement(d, qn("c:extLst"))
        ext = etree.SubElement(ext_lst, qn("c:ext"), uri="{CE6537A1-D6FC-4f65-9D91-7224C49458BB}", nsmap={"c15": C15})
        man = etree.SubElement(etree.SubElement(ext, f"{{{C15}}}layout"), qn("c:manualLayout"))
        etree.SubElement(man, qn("c:w"), val=f"{box[0]:.4f}")
        etree.SubElement(man, qn("c:h"), val=f"{box[1]:.4f}")
    if align:
        for para in d.iter(qn("a:p")):
            ppr = para.find(qn("a:pPr"))
            if ppr is None:
                ppr = etree.Element(qn("a:pPr"))
                para.insert(0, ppr)
            ppr.set("algn", align)
        for body in d.iter(qn("a:bodyPr")):                    # a sized label centres its text block otherwise
            body.set("wrap", "square")
            body.set("anchorCtr", "0")


# ====================================================================== decks and one-call slides
def deck():
    """A new, empty deck on the McKesson branded template (its master, logo, footer, theme and Libre Franklin; built
    from office/brand/ by office/build_office.py). Chart slides use its Title Only layout."""
    return Presentation(str(TEMPLATE))


DELIVER_DIR = Path("/mnt/data")       # Copilot: every file written here syncs to the user's OneDrive as a new copy


def _in_deliver_dir(path: Path) -> bool:
    return DELIVER_DIR.is_dir() and DELIVER_DIR.resolve() in path.resolve().parents


def save(prs, path) -> Path:
    """Save the deck (its title taken from the first slide's headline) to a working folder such as /tmp, then check
    it there (render, validate) and hand it over with deliver(). Where /mnt/data exists (Copilot), saving into it
    directly is refused: every write there, including a validator's rewrite and its .orig backup, becomes another
    copy in the user's OneDrive, and deleting the file doesn't remove the copy."""
    path = Path(path)
    if _in_deliver_dir(path):
        raise ValueError(f"save the deck to /tmp first (e.g. /tmp/{path.name}), check it there, then "
                         f"mv.office.deliver('/tmp/{path.name}') copies it to {DELIVER_DIR} once")
    cp = prs.core_properties
    if len(prs.slides) and prs.slides[0].shapes.title is not None:
        cp.title = prs.slides[0].shapes.title.text
    cp.created = cp.modified = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp.revision = 1
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return path


def deliver(*paths, to=None, revision=None):
    """mv.deliver for decks: copy the finished, checked deck (and its preview PNG) into the delivery folder once, as
    the last step. Delivering the same file again does nothing; a second version of a deck already delivered in this
    chat is refused unless `revision=` says what the user asked to change. Never cp, mv or rm in the delivery
    folder."""
    from . import deliver as _deliver

    return _deliver(*paths, to=to if to is not None else DELIVER_DIR, revision=revision)


def _fmt(fmt, v) -> str:
    return fmt.format(v) if isinstance(fmt, str) else fmt(v)


_FMT = re.compile(r'^(?P<pre>[^{}"]*)\{:(?P<comma>,?)\.(?P<d>\d+)(?P<t>[f%])\}(?P<post>[^{}"]*)$')


def number_format(fmt) -> str | None:
    """The Excel number format for a Python label format ("{:,.0f}" -> #,##0; "{:.1f}%" -> 0.0"%"; "${:,.1f}M" ->
    "$"#,##0.0"M"; "{:.0%}" -> 0%), so the chart's labels show the data's own values and follow Edit Data. None
    when there is no equivalent (a callable, or a format this doesn't parse): the labels are then typed text."""
    m = _FMT.match(fmt) if isinstance(fmt, str) else None
    if not m:
        return None
    d = int(m["d"])
    body = ("#,##0" if m["comma"] else "0") + ("." + "0" * d if d else "") + ("%" if m["t"] == "%" else "")
    return "".join((f'"{m["pre"]}"' if m["pre"] else "", body, f'"{m["post"]}"' if m["post"] else ""))


LABEL_PT, TICK_PT, NOTE_PT = 12, 12, 11
LABEL_PAD = 0.1          # in: PowerPoint's gap between a bar's end and an outside-end label (measured ~0.07)
TICK_GAP = 0.3           # in: the longest category label's room beyond its measured width (PowerPoint wraps early)
MAX_BAND = 0.6           # in: one bar plus its gap at most, so a short list keeps bars of normal weight
LINE_H = LABEL_PT * 1.25 / 72                                # in: one line of label text


def _bars(labels, values) -> tuple[list[str], list[float]]:
    """Labels and values for bars or columns: one value each, none missing, none below zero."""
    names = [str(v) for v in labels]
    vals = [float(v) for v in values]
    if len(names) != len(vals):
        raise ValueError("one value per label")
    if not names:
        raise ValueError("no bars")
    if any(v != v for v in vals):
        raise ValueError("a value is missing (NaN): drop or fill it first")
    if min(vals) < 0:
        raise ValueError("bars start at zero: for signed changes use a diverging bar (mv.diverging_bars)")
    return names, vals


def _highlight(names, focus, accent) -> tuple[set[str], str | None, set[str]]:
    """focus (McKesson Blue) and accent (navy) as strings, checked: each one of `names`, and few enough to stand out."""
    focus = {str(f) for f in focus}
    accent = str(accent) if accent is not None else None
    hot = focus | ({accent} if accent else set())
    few_highlights(hot, len(names), "items", stacklevel=4)
    if unknown := hot - set(names):
        raise ValueError(f"focus/accent not among the labels: {sorted(unknown)}")
    return focus, accent, hot


def _chart(slide, chart_type, data, width, alt):
    """The slide's one chart, in the chart area, named "Chart" with its alt text."""
    frame, chart = add_chart(slide, chart_type, data, width=width)
    frame.name = "Chart"
    frame._element.nvGraphicFramePr.cNvPr.set("descr", alt)
    return frame, chart


def _frame_in(frame) -> tuple[float, float, float, float]:
    return tuple(Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))


def _shown(slide, values=()) -> list[str]:
    """What the slide already says: the text on it (headline, subtitle, typed labels, the benchmark) and the chart's
    values as they are written (27.4, or 27 for a whole number), for the insights panel's repetition check."""
    out = [s.text_frame.text for s in slide.shapes if s.has_text_frame]
    for v in values:                                           # 27.4 as 27.4; only a whole number as 27
        out += [f"{v:.0f}"] if float(v).is_integer() else [f"{v:.1f}", f"{v:g}"]
    return out


def _no_takeaways(takeaways) -> None:
    if takeaways is not None:
        raise TypeError("takeaways= is now insights=[(claim, evidence), ...] (with implication= and big= when "
                        "needed): each a bold claim the chart doesn't show on its own, then the fact behind it")


def bar_slide(prs, labels: Sequence[str], values: Sequence[float], *, headline: str, source: str,
              subtitle: str | None = None, footnote: str | None = None, focus: Iterable[str] = (),
              accent: str | None = None, benchmark: float | None = None, benchmark_label: str | None = None,
              fmt="{:,.0f}", sort: bool | str = True, insights: Sequence[tuple] | None = None, implication: str | None = None,
              big: tuple[str, str] | None = None, takeaways=None, bracket: tuple | None = None,
              alt: str | None = None, notes: str | None = None):
    """A ranking as a native, editable horizontal bar chart on a slide: bars sorted with the story on top, grey
    context with the headline's bars in McKesson Blue (navy for one accent), the value at
    each bar's end (Bold for the highlighted bars), no gridlines and no value axis, the category labels sized to
    their text so the plot starts right after them, and an optional benchmark as a dashed navy line across all bars,
    named above the plot. A value label that would sit on the benchmark line moves inside its bar.

        office.bar_slide(prs, df.job_family, df.rate, focus={"Pharmacy Technician"}, benchmark=19.9,
                         benchmark_label="Enterprise 19.9%", fmt="{:.1f}%", headline=..., subtitle=..., source=...)

    source: the source line (write the skill's placeholder when the user gave none). fmt: the value format, as a
    Python format string; the common ones become the chart's number format, so the labels follow Edit Data. sort:
    True puts the story on top: largest first, or smallest first when the highlighted bars are the small ones (a
    "lagging" or "lowest" headline); "descending" / "ascending" force the order; False keeps the given order (a
    natural order). insights, implication, big: the insights panel in the right third (insights_panel); the chart
    then takes two-thirds; an insight's `at` puts its number marker after that bar's label. bracket: (names, text),
    a bracket beside two or more adjacent bars saying what they add up to ("73% of all\nvoluntary exits"). alt: the chart's alt text (default: the headline). Values must
    be zero or more (bars start at zero; use a diverging bar for signed changes). Returns SimpleNamespace(slide,
    chart, order, x_max, inside).
    """
    from .charts import story_order                           # shared with mv.bar, so the chart and slide agree

    names, vals = _bars(labels, values)
    focus, accent, hot = _highlight(names, focus, accent)
    order = story_order(names, vals, hot, sort)
    names, vals = [names[i] for i in order], [vals[i] for i in order]
    num_fmt = number_format(fmt)

    edit = ("Right-click the chart › Edit Data to change the numbers; the labels follow." if num_fmt else
            "The value labels are typed text: retype them if the numbers change (Edit Data changes only the bars).")
    default_notes = f"Ranking bar (mckviz.office.bar_slide). {edit} To recolor a bar: click it twice to select only " \
                    "that bar › Format Data Point › Fill."
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT

    # Geometry from the text: the plot starts right after the longest category label and ends at the frame's
    # right edge; the axis maximum leaves room for the widest value label at the end of its bar.
    cat_w = max(text_width(n, TICK_PT) for n in names)
    if cat_w > 0.4 * fw:
        warnings.warn(f"category labels up to {cat_w:.1f} in wide take over 40% of the chart; shorten them",
                      stacklevel=2)
    px = min(cat_w * 1.05 + TICK_GAP, 0.45 * fw) / fw
    ph = min(PLOT_H, len(names) * MAX_BAND / CHART_H)       # top-aligned with the card when the list is short
    pw = 1 - px - 0.02
    plot_in = pw * fw
    texts = [_fmt(fmt, v) for v in vals]
    lab_w = [text_width(t, LABEL_PT, "Bold" if n in hot else "Medium") for n, t in zip(names, texts)]
    marked = _marked(insights)
    rows, bw = [], 0.0
    if bracket is not None:
        b_names, b_text = bracket
        rows = sorted(names.index(str(n)) for n in b_names if str(n) in names)
        if len(rows) != len(list(b_names)) or len(rows) < 2 or rows != list(range(rows[0], rows[-1] + 1)):
            raise ValueError("bracket: (names, text) with two or more bars that sit next to each other once sorted")
        bw = max(text_width(s, NOTE_PT, "SemiBold") for s in b_text.split("\n")) + 0.26
    extra = [(MARKER + 0.08 if n in marked else 0) + (bw if i in rows else 0) for i, n in enumerate(names)]
    x_max = max(v * plot_in / (plot_in - LABEL_PAD - lw - e - 0.05) for v, lw, e in zip(vals, lab_w, extra))
    if benchmark is not None:
        x_max = max(x_max, benchmark * 1.03)
    x_max = x_max or 1.0

    data = CategoryChartData(number_format=num_fmt) if num_fmt else CategoryChartData()
    data.categories = names
    data.add_series(subtitle or "Value", vals)
    frame, chart = _chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, data, fw, alt or headline)
    plot_layout(chart, px, PLOT_Y, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = int(BAND_GAP)
    plot.vary_by_categories = False
    series = plot.series[0]
    fill(series, C.context)

    # Which labels would sit on the benchmark line: those whose outside-end label spans it.
    to_in = plot_in / x_max
    inside = []
    if benchmark is not None:
        b = benchmark * to_in
        for n, v, lw in zip(names, vals, lab_w):
            end = v * to_in
            if end - 0.03 <= b <= end + LABEL_PAD + lw + 0.05:
                if end < lw + 2 * LABEL_PAD:
                    warnings.warn(f"the {n!r} label sits on the benchmark line and its bar is too short to hold it; "
                                  "check the slide", stacklevel=2)
                else:
                    inside.append(n)
    for i, n in enumerate(names):
        pt = series.points[i]
        bar = C.accent if n == accent else C.focus if n in focus else C.context
        if bar != C.context:
            fill(pt, bar)
        pos = XL_LABEL_POSITION.INSIDE_END if n in inside else XL_LABEL_POSITION.OUTSIDE_END
        color = text_on(bar) if n in inside else C.headline if n in hot else C.text
        if num_fmt:
            dlbl(pt, val=True, num_fmt=num_fmt, pos=pos, size=LABEL_PT, color=color, bold=n in hot)
        else:
            dlbl(pt, text=texts[i], pos=pos, size=LABEL_PT, color=color, bold=n in hot)

    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = 0, x_max
    va.visible = False
    va.has_major_gridlines = va.has_minor_gridlines = False
    ca = chart.category_axis
    ca.reverse_order = True                                  # first row on top (PowerPoint draws bars bottom-up)
    ca.has_major_gridlines = ca.has_minor_gridlines = False
    baseline(ca)
    ca.tick_labels.font.size = Pt(TICK_PT)
    ca.tick_labels.font.color.rgb = rgb(C.text)

    if benchmark is not None:
        fl, ft, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.height))
        x = fl + fw * px + benchmark * to_in
        top, bottom = ft + fh * PLOT_Y, ft + fh * (PLOT_Y + ph)
        line_shape(slide, x, top - 0.05, x, bottom, C.total, name="Benchmark line")
        text = benchmark_label or _fmt(fmt, benchmark)
        tw = text_width(text, NOTE_PT) + 0.1
        lx = min(max(x - tw / 2, fl), fl + fw - tw)            # centred on the line, kept inside the chart
        text_box(slide, lx, top - 0.33, tw, 0.26, text, NOTE_PT, C.annotation, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.BOTTOM, name="Benchmark label", wrap=False)
        slide.notes_slide.notes_text_frame.text += (
            f"\n\nThe dashed benchmark line is a drawn shape at {_fmt(fmt, benchmark)} on an axis of 0 to "
            f"{_fmt(fmt, x_max)} (Format Axis › Maximum). If the benchmark or the axis changes, move the line.")
    fl, ft, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.height))
    band = fh * ph / len(names)
    ends = []                                                   # where each bar's label (and marker) ends, and its row
    anchors = {}
    for i, (n, v, lw) in enumerate(zip(names, vals, lab_w)):
        end = fl + fw * px + v * to_in
        right = end + 0.05 if n in inside else end + LABEL_PAD + lw
        y = ft + fh * PLOT_Y + (i + 0.5) * band
        if n in marked:
            anchors[n] = (right + 0.06 + MARKER / 2, y)
            right += 0.06 + MARKER
        ends.append((right, y))
    if rows:
        x = max(ends[i][0] for i in rows) + 0.08
        half = band * 50 / (100 + BAND_GAP)                     # half a bar's height
        top, bottom = ends[rows[0]][1] - half, ends[rows[-1]][1] + half
        for x1, y1, x2, y2 in ((x, top, x + 0.06, top), (x + 0.06, top, x + 0.06, bottom), (x, bottom, x + 0.06, bottom)):
            line_shape(slide, x1, y1, x2, y2, C.annotation, dash=False, name="Bracket")
        lines = bracket[1].split("\n")
        h = len(lines) * 0.19
        text_box(slide, x + 0.14, (top + bottom) / 2 - h / 2, bw, h, bracket[1], NOTE_PT, C.headline, font=SEMI,
                 anchor=MSO_ANCHOR.MIDDLE, name="Bracket label")
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=anchors,
                       shown=_shown(slide, vals))
    return SimpleNamespace(slide=slide, chart=chart, order=names, x_max=x_max, inside=inside)


def column_slide(prs, labels: Sequence[str], values: Sequence[float], *, headline: str, source: str,
                 subtitle: str | None = None, footnote: str | None = None, focus: Iterable[str] = (),
                 accent: str | None = None, benchmark: float | None = None, benchmark_label: str | None = None,
                 fmt="{:,.0f}", insights: Sequence[tuple] | None = None, implication: str | None = None,
              big: tuple[str, str] | None = None, takeaways=None, alt: str | None = None,
                 notes: str | None = None):
    """A few values in their natural order (fiscal years, quarters, stages) as native, editable columns: grey with the
    headline's columns in McKesson Blue (navy for one accent), the value on top of each
    column (Bold for the highlighted ones), no gridlines and no value axis, columns from zero, and an optional
    benchmark as a dashed navy line across all columns, named at its right end. A value label that would sit on the
    line moves inside its column. For a ranking, or labels too long for a column, use bar_slide.

        office.column_slide(prs, df.fiscal_year, df.internal_fill_pct, focus={"FY26"}, fmt="{:.0f}%",
                            headline=..., subtitle=..., source=...)

    The arguments are bar_slide's, without sort (columns keep the given order). Returns SimpleNamespace(slide, chart,
    y_max, inside).
    """
    names, vals = _bars(labels, values)
    focus, accent, hot = _highlight(names, focus, accent)
    num_fmt = number_format(fmt)
    edit = ("Right-click the chart › Edit Data to change the numbers; the labels follow." if num_fmt else
            "The value labels are typed text: retype them if the numbers change (Edit Data changes only the columns).")
    default_notes = f"Columns (mckviz.office.column_slide). {edit} To recolor a column: click it twice to select " \
                    "only that column › Format Data Point › Fill."
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT

    # Geometry: the benchmark's name sits right of the plot, so the plot ends before it; the axis maximum leaves room
    # for a label on top of the tallest column.
    texts = [_fmt(fmt, v) for v in vals]
    bench_text = (benchmark_label or _fmt(fmt, benchmark)) if benchmark is not None else None
    reserve = text_width(bench_text, NOTE_PT) + 0.25 if bench_text else 0.0
    px = 0.02
    pw = 1 - px - 0.02 - reserve / fw
    plot_w, plot_h = pw * fw, PLOT_H * CHART_H
    band = plot_w / len(names)
    if (widest := max(text_width(n, TICK_PT) for n in names)) > 0.95 * band:
        warnings.warn(f"category labels up to {widest:.1f} in wide don't fit a {band:.1f} in column and will wrap; "
                      "shorten them or use bar_slide", stacklevel=2)
    room = [MARKER + 0.08 if n in _marked(insights) else 0 for n in names]
    y_max = max(v * plot_h / (plot_h - LABEL_PAD - LINE_H - r - 0.05) for v, r in zip(vals, room))
    if benchmark is not None:
        y_max = max(y_max, benchmark * 1.05)
    y_max = y_max or 1.0

    data = CategoryChartData(number_format=num_fmt) if num_fmt else CategoryChartData()
    data.categories = names
    data.add_series(subtitle or "Value", vals)
    frame, chart = _chart(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, data, fw, alt or headline)
    plot_layout(chart, px, PLOT_Y, pw, PLOT_H)
    plot = chart.plots[0]
    plot.gap_width = int(BAND_GAP)
    plot.vary_by_categories = False
    series = plot.series[0]
    fill(series, C.context)

    to_in = plot_h / y_max
    inside = []
    if benchmark is not None:
        b = benchmark * to_in
        for n, v in zip(names, vals):
            top = v * to_in
            if top - 0.03 <= b <= top + LABEL_PAD + LINE_H + 0.05:
                if top < LINE_H + 2 * LABEL_PAD:
                    warnings.warn(f"the {n!r} label sits on the benchmark line and its column is too short to hold "
                                  "it; check the slide", stacklevel=2)
                else:
                    inside.append(n)
    for i, n in enumerate(names):
        pt = series.points[i]
        col = C.accent if n == accent else C.focus if n in focus else C.context
        if col != C.context:
            fill(pt, col)
        pos = XL_LABEL_POSITION.INSIDE_END if n in inside else XL_LABEL_POSITION.OUTSIDE_END
        color = text_on(col) if n in inside else C.headline if n in hot else C.text
        if num_fmt:
            dlbl(pt, val=True, num_fmt=num_fmt, pos=pos, size=LABEL_PT, color=color, bold=n in hot)
        else:
            dlbl(pt, text=texts[i], pos=pos, size=LABEL_PT, color=color, bold=n in hot)

    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = 0, y_max
    va.visible = False
    va.has_major_gridlines = va.has_minor_gridlines = False
    ca = chart.category_axis
    ca.has_major_gridlines = ca.has_minor_gridlines = False
    baseline(ca)
    ca.tick_labels.font.size = Pt(TICK_PT)
    ca.tick_labels.font.color.rgb = rgb(C.text)
    _horizontal_ticks(ca)

    if benchmark is not None:
        fl, ft, _, fh = _frame_in(frame)
        left, right = fl + fw * px, fl + fw * (px + pw)
        y = ft + fh * (PLOT_Y + PLOT_H) - benchmark * to_in
        line_shape(slide, left, y, right + 0.05, y, C.total, name="Benchmark line")
        text_box(slide, right + 0.12, y - 0.13, reserve - 0.12, 0.26, bench_text, NOTE_PT, C.annotation,
                 anchor=MSO_ANCHOR.MIDDLE, name="Benchmark label", wrap=False)
        slide.notes_slide.notes_text_frame.text += (
            f"\n\nThe dashed benchmark line is a drawn shape at {_fmt(fmt, benchmark)} on an axis of 0 to "
            f"{_fmt(fmt, y_max)} (Format Axis › Maximum). If the benchmark or the axis changes, move the line.")
    anchors = {}
    marked = _marked(insights)
    if marked:
        fl, ft, _, fh = _frame_in(frame)
        left, step = fl + fw * px, fw * pw / len(names)
        for i, (n, v) in enumerate(zip(names, vals)):
            if n in marked:
                top = ft + fh * (PLOT_Y + PLOT_H) - v * to_in
                above = top - 0.05 if n in inside else top - LABEL_PAD - LINE_H
                anchors[n] = (left + (i + 0.5) * step, above - 0.06 - MARKER / 2)
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=anchors,
                       shown=_shown(slide, vals))
    return SimpleNamespace(slide=slide, chart=chart, y_max=y_max, inside=inside)


def _horizontal_ticks(axis) -> None:
    """Category labels stay level (PowerPoint tilts them when they crowd; better to wrap, or warn first)."""
    body = axis._element.find(qn("c:txPr")).find(qn("a:bodyPr"))
    body.set("rot", "0")
    body.set("vert", "horz")


def _skip_labels(axis, step: int) -> None:
    """Label every `step`-th category (Format Axis › Interval between labels)."""
    if step <= 1:
        return
    ax = axis._element
    after = next(e for e in (ax.find(qn(t)) for t in ("c:lblOffset", "c:lblAlgn", "c:auto", "c:crosses"))
                 if e is not None)
    for tag in ("c:tickMarkSkip", "c:tickLblSkip"):           # schema order: tickLblSkip, then tickMarkSkip
        after.addnext(etree.Element(qn(tag), val=str(step)))


def _axis_format(fmt, step: float):
    """The value axis's label format: `fmt` with only the decimals the tick step needs, as (Python format, Excel
    number format); a format this can't parse is kept, and the axis then shows the data's own format."""
    if not isinstance(fmt, str) or not _FMT.match(fmt):
        return fmt, None
    d = 0
    while d < 3 and abs(step * 10 ** d - round(step * 10 ** d)) > 1e-9:
        d += 1
    if _FMT.match(fmt)["t"] == "%":                             # "{:.0%}": the step is a fraction
        d = max(0, d - 2)
    py = re.sub(r"\.\d+", f".{d}", fmt, count=1)
    return py, number_format(py)


def line_slide(prs, x: Sequence, series, *, headline: str, source: str, subtitle: str | None = None,
               footnote: str | None = None, focus: Iterable[str] = (), accent: str | None = None,
               target: float | None = None, target_label: str | None = None, forecast_from=None,
               fmt="{:,.1f}", ylim: tuple[float, float] | None = None,
               insights: Sequence[tuple] | None = None, implication: str | None = None,
               big: tuple[str, str] | None = None, takeaways=None, alt: str | None = None, notes: str | None = None):
    """Lines over time as a native, editable line chart, with mv.line's house rules: grey context, the headline's
    series in McKesson Blue (one navy accent at most), labels at the line ends instead of a legend (name and value
    for the highlighted lines, name only for the grey ones, nudged apart so they never overlap), light horizontal
    gridlines, straight segments, no markers.

        office.line_slide(prs, df.quarter, {"Pharmacy Technician": [...], "DC Associate": [...]},
                          focus={"Pharmacy Technician"}, target=20, target_label="Target 20%", fmt="{:.1f}%",
                          headline=..., subtitle=..., source=...)

    x: the period labels, evenly spaced. series: {name: values} or a DataFrame whose columns are the series; NaN
    leaves a gap. focus / accent: as in mv.line; with neither, one series is the focus and two to four get the
    categorical colors; more than four raises (name the focus). target: a dashed navy line across the plot, named by
    target_label. forecast_from: the last actual period (a label in x, or a 0-based position); every line is dashed
    after it, with a dotted divider. fmt: the format of the end values; the value axis uses it with the decimals its
    step needs. ylim: fixed axis limits (a line may start above zero). insights, implication, big, alt, notes: as in bar_slide.
    mv.line's event shading and scenario bands have no native version: use picture_slide for those. Returns
    SimpleNamespace(slide, chart, order, colors, y_range).
    """
    import math

    from matplotlib.ticker import MaxNLocator

    from . import CATEGORICAL

    if hasattr(series, "columns"):
        data_in = {str(c): [float(v) for v in series[c]] for c in series.columns}
    else:
        data_in = {str(k): [float(v) for v in vals] for k, vals in dict(series).items()}
    periods = [str(v) for v in x]
    n = len(periods)
    if n < 2:
        raise ValueError("a line needs at least two periods")
    if any(len(v) != n for v in data_in.values()):
        raise ValueError("every series needs one value per period in x")
    if not data_in:
        raise ValueError("no series")
    focus, accent, hot = _highlight(list(data_in), focus, accent)
    categorical = False
    if not hot:
        if len(data_in) == 1:
            focus = hot = set(data_in)
        elif len(data_in) <= 4:
            categorical = True
        else:
            raise ValueError(f"{len(data_in)} lines: name the focus (the rest go grey), or use mv.multiples on a "
                             "picture_slide")
    strong = set(data_in) if categorical else hot
    color = {nm: (CATEGORICAL[i] if categorical else C.accent if nm == accent else C.focus if nm in focus
                  else C.context) for i, nm in enumerate(data_in)}
    names = sorted(data_in, key=lambda nm: nm in strong)        # grey first, so the highlighted lines draw on top

    def at(lab) -> int:                                          # a label that appears once, or a 0-based position
        hits = [i for i, v in enumerate(periods) if v == str(lab)]
        if len(hits) == 1:
            return hits[0]
        if isinstance(lab, str) or int(lab) != lab or not 0 <= int(lab) < n:
            raise ValueError(f"{lab!r} appears {len(hits)} times in x; pass its 0-based position instead")
        return int(lab)

    cut = None if forecast_from is None else at(forecast_from)
    finite = [v for vals in data_in.values() for v in vals if v == v]
    if not finite:
        raise ValueError("every value is missing")
    if ylim is not None:
        lo, hi = ylim
        ticks = [t for t in MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]).tick_values(lo, hi) if lo <= t <= hi]
    else:
        span = finite + ([target] if target is not None else [])
        ticks = list(MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]).tick_values(min(span), max(span)))
        lo, hi = ticks[0], ticks[-1]
    step = ticks[1] - ticks[0] if len(ticks) > 1 else (hi - lo)
    tick_fmt, axis_fmt = _axis_format(fmt, step)

    # End labels: the last value of each line (name and value when highlighted, name only when grey).
    ends = []
    for nm in names:
        idx = [i for i, v in enumerate(data_in[nm]) if v == v]
        if idx:
            i = idx[-1]
            text = f"{nm}  {_fmt(fmt, data_in[nm][i])}" if nm in strong else nm
            ends.append((nm, i, data_in[nm][i], text))

    default_notes = ("Line chart (mckviz.office.line_slide). Right-click the chart › Edit Data to change the numbers; "
                     "the end labels follow (each is a data label on the last point: Series Name + Value), but "
                     "their nudges apart are fixed, so check they don't overlap. To recolor a line: Format Data "
                     "Series › Line.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT

    # Geometry from the text: the plot starts after the widest value-axis label and ends before the widest end
    # label; the first and last periods sit on the plot's edges.
    tick_w = max(text_width(_fmt(tick_fmt, t), TICK_PT) for t in ticks)
    end_w = {nm: text_width(t, LABEL_PT, "Bold" if nm in strong else "Medium") for nm, _, _, t in ends}
    px = (tick_w + 0.2) / fw
    pw = 1 - px - (max(end_w.values()) + LABEL_PAD + 0.1) / fw
    plot_w, plot_h = pw * fw, PLOT_H * CHART_H
    if pw < 0.45:
        warnings.warn("the end labels take over half the chart's width; shorten the series names", stacklevel=2)
    widest = max(text_width(p, TICK_PT) for p in periods)
    skip = max(1, math.ceil((widest + 0.25) / (plot_w / (n - 1))))   # label every k-th period when they crowd

    data = CategoryChartData(number_format=number_format(fmt)) if number_format(fmt) else CategoryChartData()
    data.categories = periods
    for nm in names:
        data.add_series(nm, [v if v == v else None for v in data_in[nm]])
    frame, chart = _chart(slide, XL_CHART_TYPE.LINE, data, fw, alt or headline)
    plot_layout(chart, px, PLOT_Y, pw, PLOT_H)
    points_on_edges(chart)
    fl, ft, _, fh = _frame_in(frame)

    def slide_y(v):                                              # a value's height on the slide, in inches
        return ft + fh * PLOT_Y + plot_h * (1 - (v - lo) / (hi - lo))

    # End labels, nudged apart: from the top down, each at least one line below the one above.
    placed, prev = {}, None
    for nm, i, v, _ in sorted(ends, key=lambda e: slide_y(e[2])):
        y = slide_y(v) if prev is None else max(slide_y(v), prev + LINE_H)
        placed[nm] = prev = y
    for k, s in enumerate(chart.plots[0].series):
        nm = names[k]
        width = Pt(TOKENS["chart"]["line"]["width_pt"] if nm in strong else TOKENS["chart"]["line"]["context_width_px"])
        s.smooth = False
        s.marker.style = XL_MARKER_STYLE.NONE
        s.format.line.color.rgb = rgb(color[nm])
        s.format.line.width = width
        if cut is not None:
            for i in range(cut + 1, n):                         # a point's line is the segment that ends at it
                ln = s.points[i].format.line
                ln.color.rgb = rgb(color[nm])
                ln.width = width
                ln.dash_style = 4                               # MSO_LINE_DASH_STYLE.DASH
        end = next((e for e in ends if e[0] == nm), None)
        if end is None:
            continue
        _, i, v, text = end
        dy = (placed[nm] - slide_y(v)) / fh
        box = ((end_w[nm] + 0.15) / fw, (LINE_H + 0.05) / fh)
        tone = color[nm] if nm in strong else C.text_muted
        num = number_format(fmt)
        if nm in strong and num:
            dlbl(s.points[i], val=True, ser=True, sep="  ", num_fmt=num, pos=XL_LABEL_POSITION.RIGHT, size=LABEL_PT,
                 color=tone, bold=True, dy=dy, box=box, align="l")
        elif nm in strong:
            dlbl(s.points[i], text=text, pos=XL_LABEL_POSITION.RIGHT, size=LABEL_PT, color=tone, bold=True, dy=dy,
                 box=box, align="l")
        else:
            dlbl(s.points[i], ser=True, pos=XL_LABEL_POSITION.RIGHT, size=LABEL_PT, color=tone, dy=dy, box=box,
                 align="l")

    va = chart.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = lo, hi, step
    va.has_minor_gridlines = False
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = rgb(C.grid)
    va.major_gridlines.format.line.width = Pt(TOKENS["chart"]["grid"]["width_px"])
    baseline(va, visible=False)
    va.tick_labels.font.size = Pt(TICK_PT)
    va.tick_labels.font.color.rgb = rgb(C.text_muted)
    if axis_fmt:
        va.tick_labels.number_format = axis_fmt
        va.tick_labels.number_format_is_linked = False
    ca = chart.category_axis
    ca.has_major_gridlines = ca.has_minor_gridlines = False
    baseline(ca)
    ca.tick_labels.font.size = Pt(TICK_PT)
    ca.tick_labels.font.color.rgb = rgb(C.text_muted)
    _horizontal_ticks(ca)
    _skip_labels(ca, skip)

    plot_left = fl + fw * px
    if target is not None:
        y = slide_y(target)
        line_shape(slide, plot_left, y, plot_left + plot_w, y, C.total, name="Target line")
        if target_label:
            # Above the line at its left end, or below it when the lines start just above it.
            first = [vals[0] for vals in data_in.values() if vals[0] == vals[0]]
            above = not any(0 <= slide_y(target) - slide_y(v) < LINE_H + 0.1 for v in first)
            text_box(slide, plot_left + 0.05, y - LINE_H - 0.04 if above else y + 0.04, text_width(target_label,
                     NOTE_PT) + 0.1, LINE_H, target_label, NOTE_PT, C.annotation, name="Target label", wrap=False)
    if cut is not None:
        xc = plot_left + plot_w * cut / (n - 1)
        top = ft + fh * PLOT_Y
        divider = line_shape(slide, xc, top, xc, top + plot_h, C.axis, name="Forecast divider")
        divider.line.dash_style = 3                             # MSO_LINE_DASH_STYLE.ROUND_DOT
        text_box(slide, xc + 0.06, top, 1.0, LINE_H, "Forecast", NOTE_PT, C.text_muted, name="Forecast label",
                 wrap=False)
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=None, shown=_shown(slide, [v for vs in data_in.values() for v in vs]))
    return SimpleNamespace(slide=slide, chart=chart, order=names, colors=color, y_range=(lo, hi))


def _label_column(names: Sequence[str], fw: float) -> float:
    """The plot's left edge (a fraction of the chart frame) for horizontal rows: right after the longest row label."""
    cat_w = max(text_width(n, TICK_PT) for n in names)
    if cat_w > 0.4 * fw:
        warnings.warn(f"row labels up to {cat_w:.1f} in wide take over 40% of the chart; shorten them", stacklevel=3)
    return min(cat_w * 1.05 + TICK_GAP, 0.45 * fw) / fw


def stack_slide(prs, categories: Sequence[str], parts, *, headline: str, source: str, subtitle: str | None = None,
                footnote: str | None = None, story=None, accent: str | None = None, uniform: bool = False,
                colors: Sequence[str] | None = None, label_min: float = 0, fmt="{:.0f}%",
                base: Sequence[float] | None = None, base_label: str = "n",
                insights: Sequence[tuple] | None = None, implication: str | None = None,
                big: tuple[str, str] | None = None, takeaways=None, alt: str | None = None, notes: str | None = None):
    """Parts of a whole as native, editable 100% stacked bars, with mv.hstack's rules: the first category on top, the
    story segments first on the baseline (blue; navy for one accent; the rest greys, or light blues with
    uniform=True), white lines between segments, values inside every segment wide enough to hold one (and at least
    `label_min`), each segment named
    once above the top bar (no legend), and optional counts behind each bar at the right (`base`).

        parts = [("Contingent", df.contingent_pct), ("Full-time", df.ft_pct), ("Part-time", df.pt_pct)]
        office.stack_slide(prs, df.function, parts, story="Contingent", headline=..., subtitle=..., source=...)

    parts: [(name, values)] or {name: values} in stack order; each category's parts should add up to 100 (the chart
    draws shares either way, but the labels show the values given). story / accent / uniform / colors: as in
    mv.hstack (with neither story nor colors, the first part is the story). Sort the categories first (by the story
    segment, say). insights, implication, big, alt, notes: as in bar_slide. Returns SimpleNamespace(slide, chart, order, colors).
    """
    from .charts import _STACK_GREYS, _STACK_LIGHT_BLUES

    cats = [str(c) for c in categories]
    items = list(parts.items()) if isinstance(parts, dict) else [tuple(p) for p in parts]
    items = [(str(nm), [float(v) for v in vals]) for nm, vals in items]
    story = [] if story is None else [str(story)] if isinstance(story, str) else [str(x) for x in story]
    lead = ([str(accent)] if accent is not None else []) + story
    names = [nm for nm, _ in items]
    if unknown := set(lead) - set(names):
        raise ValueError(f"not one of the parts: {sorted(unknown)}")
    if len(story) > 2:
        raise ValueError("story: at most two segments; color the rest grey or pass colors=")
    if uniform and accent is None:
        raise ValueError("uniform=True needs accent=: the light-blue series only works with one navy exception")
    if any(len(v) != len(cats) for _, v in items):
        raise ValueError("every part needs one value per category")
    if any(v != v or v < 0 for _, vals in items for v in vals):
        raise ValueError("parts must be zero or more, none missing")
    items = [it for nm in lead for it in items if it[0] == nm] + [it for it in items if it[0] not in lead]
    if colors is None:
        rest = len(items) - (len(lead) if lead else 1)
        pool = _STACK_LIGHT_BLUES if uniform else _STACK_GREYS
        if rest > len(pool):
            raise ValueError(f"{len(items)} segments: group the small ones into 'Other' (at most 4 read well)")
        head = ([C.accent] if accent is not None else []) + [C.focus] * len(story) if lead else [C.focus]
        colors = head + pool[:rest]
    colors = list(colors)
    if len(colors) != len(items):
        raise ValueError("one color per part")
    totals = [sum(vals[i] for _, vals in items) for i in range(len(cats))]
    if isinstance(fmt, str) and fmt.endswith("%") and any(abs(t - 100) > 1.5 for t in totals):
        warnings.warn("the parts don't add up to 100 for every category, but the labels say %; check the data",
                      stacklevel=2)
    num_fmt = number_format(fmt)

    default_notes = ("100% stacked bar (mckviz.office.stack_slide). The colored segment is on the baseline so every "
                     "bar's value starts level. Right-click › Edit Data to change the numbers; the labels follow. The "
                     "segment names above the top bar are text boxes: move them if the top bar's split changes.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT
    base_txt = [f"{b:,.0f}" for b in base] if base is not None else []
    reserve = (max(text_width(t, LABEL_PT - 1) for t in base_txt + [base_label]) + 0.3) if base is not None else 0.0
    px = _label_column(cats, fw)
    pw = 1 - px - 0.02 - reserve / fw
    names_h = 0.35                                             # the segment names' row above the top bar
    py = PLOT_Y + names_h / CHART_H
    ph = min(PLOT_H - names_h / CHART_H, len(cats) * MAX_BAND / CHART_H)

    data = CategoryChartData(number_format=num_fmt) if num_fmt else CategoryChartData()
    data.categories = cats
    for nm, vals in items:
        data.add_series(nm, vals)
    frame, chart = _chart(slide, XL_CHART_TYPE.BAR_STACKED_100, data, fw, alt or headline)
    plot_layout(chart, px, py, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = int(BAND_GAP)
    plot.overlap = 100
    plot_w = fw * pw
    for s, (nm, vals), col in zip(plot.series, items, colors):
        fill(s, col)
        s.format.line.color.rgb = rgb("#FFFFFF")
        s.format.line.width = Pt(1.5)
        hot = col in (C.focus, C.accent)
        for i, v in enumerate(vals):
            seg_w = plot_w * v / (totals[i] or 1)              # a label only where it fits inside its segment
            if v >= label_min and seg_w >= text_width(_fmt(fmt, v), LABEL_PT - 1, "Bold") + 0.12:
                if num_fmt:
                    dlbl(s.points[i], val=True, num_fmt=num_fmt, pos=XL_LABEL_POSITION.CENTER, size=LABEL_PT - 1,
                         color=text_on(col), bold=hot)
                else:
                    dlbl(s.points[i], text=_fmt(fmt, v), pos=XL_LABEL_POSITION.CENTER, size=LABEL_PT - 1,
                         color=text_on(col), bold=hot)
            else:
                dlbl(s.points[i])                              # no label: the segment is too thin to hold one
    va = chart.value_axis
    va.visible = False
    va.has_major_gridlines = va.has_minor_gridlines = False
    ca = chart.category_axis
    ca.reverse_order = True                                    # first category on top
    ca.has_major_gridlines = ca.has_minor_gridlines = False
    baseline(ca, visible=False)
    ca.tick_labels.font.size = Pt(TICK_PT)
    ca.tick_labels.font.color.rgb = rgb(C.text)

    # Segment names once, above the top bar, each at its segment's left edge (pushed right if the one before is long;
    # a name that would run past the bar's end is right-aligned to it instead).
    fl, ft, _, fh = _frame_in(frame)
    plot_left = fl + fw * px
    band = ph * CHART_H / len(cats)
    bar_top = ft + fh * py + (band - band / (1 + BAND_GAP / 100)) / 2
    x, prev_end = plot_left, plot_left
    for (nm, vals), col in zip(items, colors):
        hot = col in (C.focus, C.accent)
        tw = text_width(nm, TICK_PT, "SemiBold" if hot else "Regular") + 0.1
        start = max(x, prev_end + 0.15 if prev_end > plot_left else x)
        if start + tw > plot_left + plot_w:
            start = plot_left + plot_w - tw
        if prev_end > plot_left and start < prev_end + 0.1:
            warnings.warn(f"the segment names {nm!r} and the one before it overlap above the top bar; shorten the "
                          "part names", stacklevel=2)
        text_box(slide, start, bar_top - LINE_H - 0.08, tw, LINE_H, nm, TICK_PT, col if hot else C.text,
                 font=SEMI if hot else None, name=f"Segment name: {nm}", wrap=False)
        prev_end = start + tw
        x += plot_w * vals[0] / (totals[0] or 1)
    if base is not None:
        bx = plot_left + plot_w + 0.25
        text_box(slide, bx, bar_top - LINE_H - 0.08, reserve, LINE_H, base_label, TICK_PT, C.text, name="Base label",
                 wrap=False)
        for i, t in enumerate(base_txt):
            cy = ft + fh * py + band * (i + 0.5)
            text_box(slide, bx, cy - LINE_H / 2, reserve, LINE_H, t, LABEL_PT - 1, C.text_muted, anchor=MSO_ANCHOR.MIDDLE,
                     name=f"Base: {cats[i]}", wrap=False)
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=None, shown=_shown(slide, [v for _, vs in items for v in vs]))
    return SimpleNamespace(slide=slide, chart=chart, order=[nm for nm, _ in items], colors=colors)


def waterfall_slide(prs, steps: Sequence[str], values: Sequence[float], kinds: Sequence[str] | None = None, *,
                    headline: str, source: str, subtitle: str | None = None, footnote: str | None = None,
                    focus: Iterable[str] = (), semantic: str | None = None, floor: float | None = None, fmt=None,
                    insights: Sequence[tuple] | None = None, implication: str | None = None,
                    big: tuple[str, str] | None = None, takeaways=None, alt: str | None = None,
                    notes: str | None = None):
    """A bridge from a start total to an end total as a native, editable waterfall, with mv.waterfall's rules: totals
    navy, steps grey, the headline's steps in McKesson Blue, each value above its column (steps with
    an explicit sign), no gridlines and no value axis. Built as a stacked column (an invisible base lifts each step),
    so it opens in any PowerPoint.

        office.waterfall_slide(prs, df.step, df.value_musd, df.kind, focus={"Automation savings"}, floor=3900,
                               headline=..., subtitle="Labor cost bridge, FY25 to FY26 ($M)", source=...)

    kinds: "total" or "delta" per step (default: first and last are totals; a "total" in the middle is a subtotal).
    semantic: "up" (an increase is favorable: green up, orange down) or "down" (an increase is unfavorable, e.g.
    cost), with ▲/▼ on the steps, instead of focus. floor: start the value axis here, so small steps are readable;
    the totals get two white break marks and the footnote says where the axis starts. fmt: callable(value, kind) ->
    label (default: totals "4,210", steps "+120" with a true minus). insights, implication, big, alt, notes: as in bar_slide. Returns
    SimpleNamespace(slide, chart, tops, ends, colors, y_range).
    """
    import textwrap

    from . import signed

    steps, vals = [str(s) for s in steps], [float(v) for v in values]
    n = len(steps)
    if len(vals) != n:
        raise ValueError("steps and values must have the same length")
    if any(v != v for v in vals):
        raise ValueError("a value is missing (NaN): drop or fill it first")
    kinds = list(kinds) if kinds is not None else ["total"] + ["delta"] * (n - 2) + ["total"]
    if len(kinds) != n or set(kinds) - {"total", "delta"}:
        raise ValueError("kinds must be 'total' or 'delta', one per step")
    if semantic not in (None, "up", "down"):
        raise ValueError("semantic must be None, 'up' (increase is favorable) or 'down' (increase is unfavorable)")
    focus = {str(f) for f in focus}
    few_highlights(focus, sum(k == "delta" for k in kinds), "steps")
    if unknown := focus - set(steps):
        raise ValueError(f"focus not among the steps: {sorted(unknown)}")
    fmt = fmt or (lambda v, k: f"{v:,.0f}" if k == "total" else signed(v))

    run, base, change, total, cols, tones, ends = 0.0, [], [], [], [], [], []
    for s, v, k in zip(steps, vals, kinds):
        if k == "total":
            base.append(0.0), change.append(0.0), total.append(v)
            run = v
            cols.append(C.total), tones.append("total")
        else:
            base.append(run + min(v, 0.0)), change.append(abs(v)), total.append(0.0)
            run += v
            if semantic:
                good = (v > 0) == (semantic == "up")
                cols.append(C.positive if good else C.negative), tones.append("good" if good else "bad")
            else:
                cols.append(C.focus if s in focus else C.context), tones.append("focus" if s in focus else "context")
        ends.append(run)
    tops = [b + c + t for b, c, t in zip(base, change, total)]
    if min(tops) < 0 or min(base) < 0:
        raise ValueError("the bridge goes below zero; a native waterfall can't show that, use picture_slide")
    lo = floor if floor is not None else 0.0
    if floor is not None and any(base[i] < floor for i in range(n) if kinds[i] == "delta"):
        raise ValueError(f"floor={floor:g} cuts into a step's bar; lower it")
    note = (f"Value axis starts at {floor:,.0f} (break marks on the totals) so the steps are readable."
            if floor is not None else "")
    if note:
        footnote = f"{footnote} {note}" if footnote else note

    default_notes = ("Waterfall (mckviz.office.waterfall_slide), built as a stacked column: an invisible 'Base' series "
                     "lifts each step to the running total. To change the numbers, Edit Data: 'Change' and 'Total', "
                     "then 'Base' as the running total before each step. The value labels are typed text "
                     "(Format Data Label › Text): retype them too. Office 2016+ also has Insert › Waterfall, but it "
                     "can't break the axis or color single steps by rule.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT
    px, pw = 0.02, 0.96
    plot_w, plot_h = pw * fw, PLOT_H * CHART_H
    band = plot_w / n
    wrap = max(6, int(band * 0.9 / text_width("n", TICK_PT - 1)))   # characters per line that fit one column
    ticks = [textwrap.fill(s, wrap) for s in steps]
    lines = max(t.count("\n") for t in ticks) + 1
    if lines > 3:
        warnings.warn("step names wrap to four lines or more under their columns; shorten them", stacklevel=2)
    # The plot ends high enough for the step names' lines under it (PowerPoint cuts a label that has no room).
    ph = min(PLOT_H, 1 - PLOT_Y - (lines * (TICK_PT - 1) * 1.25 / 72 + 0.15) / CHART_H)
    plot_h = ph * CHART_H
    room = LINE_H + 0.1                                         # a label above the tallest column
    hi = (max(tops) * plot_h - lo * room) / (plot_h - room)

    data = CategoryChartData()
    data.categories = ticks
    data.add_series("Base", base)
    data.add_series("Change", change)
    data.add_series("Total", total)
    data.add_series("Label", [0.0] * n)                        # zero height on top of each stack: carries its label
    frame, chart = _chart(slide, XL_CHART_TYPE.COLUMN_STACKED, data, fw, alt or headline)
    plot_layout(chart, px, PLOT_Y, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = int(BAND_GAP)
    plot.overlap = 100
    s_base, s_change, s_total, s_label = plot.series
    no_fill(s_base)
    no_fill(s_label)
    fill(s_total, C.total)
    fill(s_change, C.context)
    for i, (v, k, col, tone) in enumerate(zip(vals, kinds, cols, tones)):
        if k == "delta" and col != C.context:
            fill(s_change.points[i], col)
        text = fmt(v, k)
        if semantic and k == "delta" and v:
            text = f"{'▲' if v > 0 else '▼'} {text}"
        color = {"total": C.headline, "focus": C.headline, "good": C.positive_text,
                 "bad": C.negative_text}.get(tone, C.text)
        dlbl(s_label.points[i], text=text, pos=XL_LABEL_POSITION.INSIDE_BASE, size=LABEL_PT, color=color,
             bold=tone in ("total", "focus", "good", "bad"))
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = lo, hi
    va.visible = False
    va.has_major_gridlines = va.has_minor_gridlines = False
    ca = chart.category_axis
    ca.has_major_gridlines = ca.has_minor_gridlines = False
    baseline(ca)
    ca.tick_labels.font.size = Pt(TICK_PT - 1)
    ca.tick_labels.font.color.rgb = rgb(C.text)
    _horizontal_ticks(ca)

    if floor is not None:                                       # two white slashes across each total near the floor
        fl, ft, _, fh = _frame_in(frame)
        bar_w = band / (1 + BAND_GAP / 100)
        y0 = ft + fh * (PLOT_Y + ph) - 0.3
        for i in (i for i in range(n) if kinds[i] == "total"):
            cx = fl + fw * px + band * (i + 0.5)
            for dy in (0.0, 0.09):
                line_shape(slide, cx - bar_w / 2 - 0.03, y0 + dy + 0.05, cx + bar_w / 2 + 0.03, y0 + dy - 0.05,
                           "#FFFFFF", width_pt=2.5, dash=False, name="Axis break")
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=None, shown=_shown(slide, vals))
    return SimpleNamespace(slide=slide, chart=chart, tops=tops, ends=ends, colors=cols, y_range=(lo, hi))


def dumbbell_slide(prs, labels: Sequence[str], compare: Sequence[float], value: Sequence[float], *, headline: str,
                   source: str, subtitle: str | None = None, footnote: str | None = None,
                   compare_name: str = "Market", value_name: str = "McKesson", flag_below: float | None = -5.0,
                   flag_name: str | None = None, gap: str = "pct", decimals: int = 1, tick_fmt: str = "{:,.0f}",
                   xlim: tuple[float, float] | None = None, focus: Iterable[str] | None = None,
                   insights: Sequence[tuple] | None = None, implication: str | None = None,
                   big: tuple[str, str] | None = None, takeaways=None, alt: str | None = None,
                   notes: str | None = None):
    """Us vs. a comparator per row as a native, editable dumbbell, with mv.dumbbell's rules: the comparator's dot
    grey, ours blue (orange where we are `flag_below`% or more below), joined by a light bar; the gap after each pair
    (orange and bold when flagged), the row names at the left (bold navy when flagged or in `focus`), light vertical
    gridlines, and a key naming each dot type once above the top row.

        office.dumbbell_slide(prs, df.role, df.market_median_k, df.internal_median_k, tick_fmt="${:,.0f}K",
                              headline=..., subtitle="Median base pay, McKesson vs. market, 2026 ($K)", source=...)

    The first row is on top; sort the rows first (largest shortfall first, say). gap: "pct" (value vs. compare in %)
    or "abs" (in units). tick_fmt: the x-axis format, as a Python format string. Built as an XY chart with one series
    per row, so Edit Data changes the dots; the gap labels are typed text. insights, implication, big, alt, notes: as in bar_slide.
    Returns SimpleNamespace(slide, chart, flagged, gaps, x_range).
    """
    import numpy as np
    from matplotlib.ticker import MaxNLocator
    from pptx.chart.data import XyChartData

    from . import signed

    rows = [str(s) for s in labels]
    a, b = [float(v) for v in compare], [float(v) for v in value]
    if not (len(rows) == len(a) == len(b)) or not rows:
        raise ValueError("labels, compare and value must have the same, non-zero length")
    if any(v != v for v in a + b):
        raise ValueError("a value is missing (NaN): drop or fill it first")
    if gap not in ("pct", "abs"):
        raise ValueError("gap must be 'pct' or 'abs'")
    gaps = [(bv / av - 1) * 100 if gap == "pct" else bv - av for av, bv in zip(a, b)]
    flagged = [flag_below is not None and g <= flag_below for g in gaps]
    focus = {str(f) for f in (focus or ())}
    if unknown := focus - set(rows):
        raise ValueError(f"focus not among the labels: {sorted(unknown)}")
    lo_v, hi_v = min(a + b), max(a + b)
    pad = (hi_v - lo_v) * 0.08 or 1.0
    if xlim is None:                                            # from a round tick below the data to just past it
        ticks = list(MaxNLocator(nbins=5).tick_values(lo_v - pad, hi_v + pad))
        x_min, x_max = ticks[0], hi_v + pad
    else:
        x_min, x_max = xlim
        ticks = [t for t in MaxNLocator(nbins=5).tick_values(x_min, x_max) if x_min <= t <= x_max]
    major = ticks[1] - ticks[0] if len(ticks) > 1 else (x_max - x_min)
    suffix = "%" if gap == "pct" else ""
    gap_txt = [signed(g, decimals, suffix) for g in gaps]

    default_notes = ("Dumbbell (mckviz.office.dumbbell_slide), built as an XY chart with one series per row (the "
                     "series name is the row label). Each series has three points: the axis minimum (the label "
                     f"anchor, no marker), {compare_name} (grey dot) and {value_name} (blue, or orange when flagged). "
                     "Edit Data changes the dots; the gap labels at the right are typed text, so retype them too. The "
                     "key above the top row is shapes.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    _no_takeaways(takeaways)
    fw = SIDE_CHART_W if (insights or big) else W - LEFT - RIGHT
    hot = [f or r in focus for r, f in zip(rows, flagged)]
    name_w = max(text_width(r, TICK_PT, "SemiBold" if h else "Regular") for r, h in zip(rows, hot))
    px = min(name_w * 1.05 + TICK_GAP, 0.45 * fw) / fw
    gap_w = max(text_width(t, LABEL_PT - 1, "Bold") for t in gap_txt) + LABEL_PAD + 0.15
    pw = 1 - px - gap_w / fw - 0.02
    n = len(rows)
    headroom = 1.0                                              # a band above the top row for the key

    data = XyChartData()
    for i, (r, av, bv) in enumerate(zip(rows, a, b)):
        s = data.add_series(r)
        for xv in (x_min, av, bv):
            s.add_data_point(xv, n - i)
    frame, chart = _chart(slide, XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, data, fw, alt or headline)
    plot_layout(chart, px, PLOT_Y, pw, PLOT_H)
    for ser, r, av, bv, f, h, txt in zip(chart.plots[0].series, rows, a, b, flagged, hot, gap_txt):
        ser.smooth = False
        ser.marker.style = XL_MARKER_STYLE.NONE
        ser.format.line.color.rgb = rgb(C.context_light)
        ser.format.line.width = Pt(3)
        ser.points[1].format.line.fill.background()           # no segment from the label anchor to the first dot
        dlbl(ser.points[0], ser=True, pos=XL_LABEL_POSITION.LEFT, size=TICK_PT, color=C.headline if h else C.text,
             bold=h, box=(px * 0.95, 0.24 / CHART_H), align="r")
        for p, color, size in ((ser.points[1], C.context, 8), (ser.points[2], C.negative if f else C.focus, 10)):
            m = p.marker
            m.style, m.size = XL_MARKER_STYLE.CIRCLE, size
            m.format.fill.solid()
            m.format.fill.fore_color.rgb = rgb(color)
            m.format.line.fill.background()
        right = 1 if av >= bv else 2
        dlbl(ser.points[right], text=txt, pos=XL_LABEL_POSITION.RIGHT, size=LABEL_PT - 1,
             color=C.negative_text if f else C.text, bold=f)
    va, xa = chart.value_axis, chart.category_axis              # XY: value_axis = Y, category_axis = X
    va.minimum_scale, va.maximum_scale = 0.5, n + headroom
    va.visible = False
    va.has_major_gridlines = va.has_minor_gridlines = False
    xa.minimum_scale, xa.maximum_scale, xa.major_unit = x_min, x_max, major
    xa.has_major_gridlines = True
    xa.major_gridlines.format.line.color.rgb = rgb(C.grid)
    xa.major_gridlines.format.line.width = Pt(TOKENS["chart"]["grid"]["width_px"])
    baseline(xa, visible=False)
    xa.tick_labels.font.size = Pt(TICK_PT - 1)
    xa.tick_labels.font.color.rgb = rgb(C.text_muted)
    if (code := number_format(tick_fmt)) is not None:
        xa.tick_labels.number_format = code
        xa.tick_labels.number_format_is_linked = False

    # The key: each dot type once, above the top row, starting where the plot starts.
    fl, ft, _, fh = _frame_in(frame)
    plot_h = PLOT_H * CHART_H
    y_top, y_key = n + headroom, n + 0.65                      # the axis maximum, and the key's row above the top row
    ky = ft + fh * PLOT_Y + plot_h * (y_top - y_key) / (y_top - 0.5)
    keys = [(value_name, C.focus, C.focus, True)]
    if any(flagged):
        unit = "%" if gap == "pct" else ""
        keys.append((flag_name or f"{value_name}, {abs(flag_below):g}{unit}+ below {compare_name.lower()}",
                     C.negative, C.negative_text, True))
    keys.append((compare_name, C.context, C.text_muted, False))
    g = slide.shapes.add_group_shape()
    g.name = "Key"
    kx = fl + fw * px
    for lab, dot, tone, strong in keys:
        d = 0.12
        shape(g, MSO_SHAPE.OVAL, kx, ky - d / 2, d, d, dot, name=f"Key: {lab}")
        tw = text_width(lab, NOTE_PT, "SemiBold" if strong else "Regular") + 0.1
        text_box(g, kx + d + 0.06, ky - LINE_H / 2, tw, LINE_H, lab, NOTE_PT, tone, font=SEMI if strong else None,
                 anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        kx += d + 0.06 + tw + 0.25
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=None, shown=_shown(slide, a + b))
    return SimpleNamespace(slide=slide, chart=chart, flagged=np.array(flagged), gaps=np.array(gaps),
                           x_range=(x_min, x_max))


PICTURE_TOP, PICTURE_BOTTOM = CARD_TOP - 0.1, FOOT_TOP - 0.1     # the picture's area on the slide (inches)
MAX_PICTURE_SCALE = 1.5       # a smaller figure is enlarged to fill the area, but its text no more than this


def picture_size(insights: bool = False, *, takeaways: bool | None = None) -> tuple[float, float]:
    """The figure size (inches) that fills a picture slide's chart area: full width, or two-thirds beside the
    insights panel. (takeaways= is the old name.)"""
    side = insights if takeaways is None else takeaways
    return (SIDE_CHART_W if side else W - LEFT - RIGHT), PICTURE_BOTTOM - PICTURE_TOP


def picture_figure(insights: bool = False, *, takeaways: bool | None = None):
    """A figure and axes for a chart going onto picture_slide: the chart area's size, with the plot filling it
    before the chart is drawn (builders such as mv.sankey measure their labels against the plot when they draw, so
    margins added later leave empty space or crowd the labels). Returns (fig, ax).

        fig, ax = office.picture_figure()                       # picture_figure(insights=True) beside the insights
        mv.sankey(ax, flows, ...); mv.titles(fig, ...); mv.source(fig, ...)"""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=picture_size(insights, takeaways=takeaways))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.96)
    return fig, ax


def _fit_top(fig, margin: float = 0.01) -> None:
    """Lower the plots until what sits above them (a size key, a level y-axis title) is inside the figure: past the
    top edge, the tight crop would make the picture taller and the slide would shrink it."""
    axes = [a for a in fig.axes if a.get_visible()]
    if not axes:
        return
    for _ in range(4):
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        top = max(a.get_tightbbox(r).y1 for a in axes) / fig.bbox.height
        excess = top - (1 - margin)
        if abs(excess) < 0.003 or (excess < 0 and fig.subplotpars.top >= 0.97):
            break
        fig.subplots_adjust(top=min(0.97, fig.subplotpars.top - excess))


def picture_slide(prs, fig, *, headline: str, source: str, subtitle: str | None = None, footnote: str | None = None,
                  alt: str | None = None, insights: Sequence[tuple] | None = None, implication: str | None = None,
              big: tuple[str, str] | None = None, takeaways=None, notes: str | None = None,
                  dpi: int = 200):
    """A chart that has no native PowerPoint slide yet (Sankey, strip, treemap, heatmap, ...) as a picture on the slide
    grid: the mckviz figure drawn as its builder laid it out (resizing it afterwards would move labels onto each other
    or away from their columns), then scaled to fill the chart area (down as far as needed, up by 1.5x at most, with
    a warning when it wasn't built at the slide's size). Start the figure with picture_figure() so it fills the area
    at its true point sizes. The slide
    carries the headline, subtitle and source, so any that mv.titles / mv.source put on the figure are taken off first
    (show the figure's PNG with them as the preview, then pass the same figure here). The speaker notes say the chart
    is a picture.

        fig, ax = office.picture_figure()                       # picture_figure(insights=True) beside the insights
        mv.sankey(ax, ...); mv.titles(fig, ...); mv.source(fig, ...)
        mv.save(fig, "/tmp/preview.png")                        # the inline preview
        office.picture_slide(prs, fig, headline=..., subtitle=..., source=...)

    alt: the picture's alt text (default: the headline). insights, implication, big: as in bar_slide. Returns SimpleNamespace(slide,
    picture).
    """
    import io

    from PIL import Image

    from matplotlib.text import Text

    shown = [a.get_text() for a in fig.findobj(Text) if a.get_visible()]   # what the picture already says
    marked = [n for a in fig.axes for n in getattr(getattr(a, "_mck_notes", None), "marks", [])]
    fur = getattr(fig, "_mck", {})
    for key in ("head", "sub", "foot"):                        # the slide's own text replaces the figure's
        if fur.get(key) is not None:
            fur[key].remove()
    fig._mck = {}
    _no_takeaways(takeaways)
    fw, slot_h = picture_size(bool(insights or big))
    top = PICTURE_TOP
    if fur.get("head") is not None or fur.get("sub") is not None:
        fig.subplots_adjust(top=0.97)                          # mv.layout had lowered the plot under the titles
    _fit_top(fig)                                              # a size key or axis title above the plot stays inside
    buf = io.BytesIO()
    fig.canvas.print_figure(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.05,
                            facecolor="white")                 # as mv.save: never the sandbox's patched savefig
    buf.seek(0)
    w_px, h_px = Image.open(buf).size
    w_in, h_in = w_px / dpi, h_px / dpi
    scale = min(fw / w_in, slot_h / h_in, MAX_PICTURE_SCALE)   # fill the area; text scales too, so 1.5x at most
    fill_w, fill_h = w_in * scale / fw, h_in * scale / slot_h
    if min(fill_w, fill_h) < 0.85 or not 0.85 <= scale <= 1.15:   # built at another size or shape: say so
        warnings.warn(f"picture_slide: the figure was built at {w_in:.1f} x {h_in:.1f} in, so on the {fw:.1f} x "
                      f"{slot_h:.1f} in chart area it fills {fill_w:.0%} of the width and {fill_h:.0%} of the height "
                      f"(scaled {scale:.2f}x, text with it). Build it with office.picture_figure("
                      f"{'insights=True' if (insights or big) else ''}) to fill the slide at true point sizes", stacklevel=2)
    buf.seek(0)
    default_notes = ("This chart is a picture: it has no native PowerPoint version yet. To change it, rebuild it from "
                     "the data with mckviz and replace the picture.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    pic = slide.shapes.add_picture(buf, Inches(LEFT), Inches(top), Inches(w_in * scale), Inches(h_in * scale))
    pic.name = "Chart"
    pic._element.nvPicPr.cNvPr.set("descr", alt or headline)
    if insights or big:
        insights_panel(slide, insights or (), implication=implication, big=big, anchors=None, marked=marked, shown=shown)
    return SimpleNamespace(slide=slide, picture=pic)
