"""mckviz.office - native, editable PowerPoint slides in the house style (needs python-pptx).

    from mckviz import office                  # or mv.office
    prs = office.deck()                        # the kit's template: McKesson theme, Libre Franklin, the slide grid
    office.bar_slide(prs, df.job_family, df.vol_attrition_pct, focus={"Pharmacy Technician"},
                     headline="Pharmacy technicians lose 1 in 4 people a year, above the 19.9% enterprise rate",
                     subtitle="Voluntary attrition by job family, FY26 (%)", source="Source: Workday HCM, as of ...",
                     benchmark=19.9, benchmark_label="Enterprise 19.9%", fmt="{:.1f}%")
    path = office.save(prs, "/tmp/attrition.pptx")  # check it here (render, validate) ...
    office.deliver(path)                            # ... then one copy to /mnt/data (Copilot: the user's OneDrive)

Each slide is a real PowerPoint chart (right-click › Edit Data works), on the McKesson Standard Template's grid: the
headline in the title placeholder (Bold 26 pt McKesson Blue), the subtitle, the chart, the source at 9 pt bottom-left
and the footer. Geometry is computed from the text, measured with the bundled Libre Franklin, so labels fit and never
sit on a benchmark line. The slide helpers below are shared with office/build_office.py, which builds the template
and the starter deck.
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
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_MARK
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from . import FONT, TOKENS, colors as C, text_on

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
# Two chart widths on a one-chart slide: full width, or chart + takeaways (the chart two-thirds, a gutter as wide as
# the two-charts slide's, and the takeaways panel the right third).
GUTTER = 0.5
SIDE_CHART_W = (W - LEFT - RIGHT - GUTTER) * 2 / 3          # 8.04 in
TAKE_LEFT = LEFT + SIDE_CHART_W + GUTTER
TAKE_W = W - RIGHT - TAKE_LEFT                               # 4.02 in
# The takeaways card sits in the same place on every slide; plot areas line up with it (PLOT_Y, PLOT_H are fractions
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


def takeaways_card(slide, points, title="Key takeaways"):
    """Chart + takeaways: a flat card in the right third of the slide (TAKE_LEFT, TAKE_W) beside a two-thirds chart
    (SIDE_CHART_W), in the same place on every slide (CARD_TOP to CARD_BOTTOM; the chart's plot area uses PLOT_Y and
    PLOT_H to line up with it). Light fill, a blue rule along the top (the guide's flat card), the label, then two or
    three points spread down the card with hairlines between them: each a Bold navy number on one line and a caption
    of at most two lines, written from the data. Facts, not advice."""
    if not 2 <= len(points) <= 3:
        raise ValueError("two or three takeaways")
    pad, label_h, num_h, cap_h = 0.25, 0.42, 0.42, 0.46
    x, w = TAKE_LEFT + pad, TAKE_W - 2 * pad
    for num, cap in points:
        if wrapped_lines(num, 24, w, "Bold") != 1:
            raise ValueError(f"takeaway number wraps; shorten it: {num!r}")
        if wrapped_lines(cap, 14, w) > 2:
            raise ValueError(f"takeaway caption over two lines; shorten it: {cap!r}")
    y0 = CARD_TOP + pad + label_h
    item = num_h + cap_h
    gap = min((CARD_BOTTOM - pad - y0 - len(points) * item) / (len(points) - 1), 0.6)
    g = slide.shapes.add_group_shape()
    g.name = "Takeaways"
    shape(g, MSO_SHAPE.RECTANGLE, TAKE_LEFT, CARD_TOP, TAKE_W, CARD_BOTTOM - CARD_TOP, C.surface_subtle,
          name="Takeaways card")
    shape(g, MSO_SHAPE.RECTANGLE, TAKE_LEFT, CARD_TOP, TAKE_W, 0.04, C.focus, name="Takeaways rule")
    text_box(g, x, CARD_TOP + pad, w, 0.26, title, 14, C.headline, font=SEMI, name="Takeaways label")
    for i, (num, cap) in enumerate(points):
        y = y0 + i * (item + gap)
        if i:
            line_shape(g, x, y - gap / 2, x + w, y - gap / 2, C.context_light, dash=False, name=f"Takeaway rule {i}")
        text_box(g, x, y, w, num_h, num, 24, C.headline, bold=True, name=f"Takeaway {i + 1}: number")
        text_box(g, x, y + num_h, w, cap_h, cap, 14, C.text, name=f"Takeaway {i + 1}: caption")
    nf = slide.notes_slide.notes_text_frame
    nf.text += (f"\n\nLayout: chart + takeaways. The chart is two-thirds of the width ({SIDE_CHART_W:.2f} in); the "
                f"takeaways card is the right third ({TAKE_W:.2f} in) after a {GUTTER} in gutter, in the same place on "
                f"every slide ({CARD_TOP:.2f}-{CARD_BOTTOM:.2f} in), and the plot area lines up with it. Keep 2-3 "
                "points, each a number and a caption of one or two lines: facts from the chart, no advice. Retype them "
                "for your data (each is its own text box in the Takeaways group).")
    return g


# ====================================================================== native chart helpers
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


def deliver(path, to=None) -> Path:
    """Copy a finished, checked deck (or its preview PNG) into the delivery folder once, as the last step: /mnt/data
    in Copilot (the user's OneDrive), or `to`. Refuses to overwrite: a second write there is a second copy in
    OneDrive. For a revision the user asked for, deliver under a new name. Don't render, validate or delete in the
    delivery folder afterwards."""
    import shutil

    src = Path(path)
    dest_dir = Path(to) if to is not None else DELIVER_DIR
    if not src.is_file():
        raise FileNotFoundError(src)
    if not dest_dir.is_dir():
        raise FileNotFoundError(f"no delivery folder {dest_dir}; pass to=")
    dest = dest_dir / src.name
    if dest.exists():
        raise FileExistsError(f"{dest} was already delivered; for a revision, save under a new name and deliver that")
    shutil.copyfile(src, dest)
    return dest


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


def bar_slide(prs, labels: Sequence[str], values: Sequence[float], *, headline: str, source: str,
              subtitle: str | None = None, footnote: str | None = None, focus: Iterable[str] = (),
              accent: str | None = None, benchmark: float | None = None, benchmark_label: str | None = None,
              fmt="{:,.0f}", sort: bool = True, takeaways: Sequence[tuple[str, str]] | None = None,
              alt: str | None = None, notes: str | None = None):
    """A ranking as a native, editable horizontal bar chart on a slide: bars sorted largest first from the top, grey
    context with the headline's bars in McKesson Blue (navy for one accent, at most two highlighted), the value at
    each bar's end (Bold for the highlighted bars), no gridlines and no value axis, the category labels sized to
    their text so the plot starts right after them, and an optional benchmark as a dashed navy line across all bars,
    named above the plot. A value label that would sit on the benchmark line moves inside its bar.

        office.bar_slide(prs, df.job_family, df.rate, focus={"Pharmacy Technician"}, benchmark=19.9,
                         benchmark_label="Enterprise 19.9%", fmt="{:.1f}%", headline=..., subtitle=..., source=...)

    source: the source line (write the skill's placeholder when the user gave none). fmt: the value format, as a
    Python format string; the common ones become the chart's number format, so the labels follow Edit Data. sort:
    False keeps the given order (a natural order). takeaways: two or three (number, caption) pairs for the card in
    the right third; the chart then takes two-thirds. alt: the chart's alt text (default: the headline). Values must
    be zero or more (bars start at zero; use a diverging bar for signed changes). Returns SimpleNamespace(slide,
    chart, order, x_max, inside).
    """
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
    focus = {str(f) for f in focus}
    accent = str(accent) if accent is not None else None
    hot = focus | ({accent} if accent else set())
    if len(hot) > 2:
        raise ValueError("highlight at most two bars")
    if unknown := hot - set(names):
        raise ValueError(f"focus/accent not among the labels: {sorted(unknown)}")
    order = sorted(range(len(names)), key=lambda i: -vals[i]) if sort else list(range(len(names)))
    names, vals = [names[i] for i in order], [vals[i] for i in order]
    num_fmt = number_format(fmt)

    edit = ("Right-click the chart › Edit Data to change the numbers; the labels follow." if num_fmt else
            "The value labels are typed text: retype them if the numbers change (Edit Data changes only the bars).")
    default_notes = f"Ranking bar (mckviz.office.bar_slide). {edit} To recolor a bar: click it twice to select only " \
                    "that bar › Format Data Point › Fill."
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    fw = SIDE_CHART_W if takeaways else W - LEFT - RIGHT

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
    x_max = max(v * plot_in / (plot_in - LABEL_PAD - lw - 0.05) for v, lw in zip(vals, lab_w))
    if benchmark is not None:
        x_max = max(x_max, benchmark * 1.03)
    x_max = x_max or 1.0

    data = CategoryChartData(number_format=num_fmt) if num_fmt else CategoryChartData()
    data.categories = names
    data.add_series(subtitle or "Value", vals)
    frame, chart = add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, data, width=fw)
    frame.name = "Chart"
    frame._element.nvGraphicFramePr.cNvPr.set("descr", alt or headline)
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
    if takeaways:
        takeaways_card(slide, takeaways)
    return SimpleNamespace(slide=slide, chart=chart, order=names, x_max=x_max, inside=inside)


def picture_slide(prs, fig, *, headline: str, source: str, subtitle: str | None = None, footnote: str | None = None,
                  alt: str | None = None, takeaways: Sequence[tuple[str, str]] | None = None, notes: str | None = None,
                  dpi: int = 200):
    """A chart that has no native PowerPoint slide yet (line, stack, Sankey, strip, ...) as a picture on the slide
    grid: the mckviz figure drawn at the chart area's size, so its text keeps its point size on the slide. The slide
    carries the headline, subtitle and source, so any that mv.titles / mv.source put on the figure are taken off first
    (show the figure's PNG with them as the preview, then pass the same figure here). The speaker notes say the chart
    is a picture.

        fig, ax = plt.subplots(); mv.line(ax, ...); mv.titles(fig, ...); mv.source(fig, ...)
        mv.save(fig, "/tmp/preview.png")                        # the inline preview
        office.picture_slide(prs, fig, headline=..., subtitle=..., source=...)

    alt: the picture's alt text (default: the headline). takeaways: as in bar_slide. Returns SimpleNamespace(slide,
    picture).
    """
    import io

    from PIL import Image

    fur = getattr(fig, "_mck", {})
    for key in ("head", "sub", "foot"):                        # the slide's own text replaces the figure's
        if fur.get(key) is not None:
            fur[key].remove()
    fig._mck = {}
    fw = SIDE_CHART_W if takeaways else W - LEFT - RIGHT
    top, bottom = CARD_TOP - 0.1, FOOT_TOP - 0.1
    slot_h = bottom - top
    fig.set_size_inches(fw, slot_h)
    if fur.get("head") is not None or fur.get("sub") is not None:
        fig.subplots_adjust(top=0.97)                          # mv.layout had lowered the plot under the titles
    buf = io.BytesIO()
    fig.canvas.print_figure(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.05,
                            facecolor="white")                 # as mv.save: never the sandbox's patched savefig
    buf.seek(0)
    w_px, h_px = Image.open(buf).size
    w_in, h_in = w_px / dpi, h_px / dpi
    scale = min(1.0, fw / w_in, slot_h / h_in)                 # natural size (true point sizes) unless too big
    buf.seek(0)
    default_notes = ("This chart is a picture: it has no native PowerPoint version yet. To change it, rebuild it from "
                     "the data with mckviz and replace the picture.")
    slide = chart_slide(prs, headline, subtitle, footnote, notes or default_notes, source)
    pic = slide.shapes.add_picture(buf, Inches(LEFT), Inches(top), Inches(w_in * scale), Inches(h_in * scale))
    pic.name = "Chart"
    pic._element.nvPicPr.cNvPr.set("descr", alt or headline)
    if takeaways:
        takeaways_card(slide, takeaways)
    return SimpleNamespace(slide=slide, picture=pic)
