"""Build the Office starter files from tokens and example data.

    python office/build_office.py

Writes (all generated; never edit by hand):
    dist/office/McKesson-DataViz-Starter.pptx   16:9 deck, McKesson theme, native editable sample charts
    dist/office/McKesson-DataViz.potx           the same theme and layouts as a template, with no slides
    dist/office/McKesson-DataViz-Charts.xlsx    palette sheet + native sample charts + a heat table
    dist/office/McKesson-DataViz-Starter-Official.pptx   the same slides on the McKesson Standard Template, only when
                                                the template is present locally (reference/mckesson-branding/); it
                                                contains internal brand assets, so it is gitignored and goes only into
                                                the internal release bundle

The theme colors and fonts come from dist/office/Theme Colors|Theme Fonts (built by tokens/build.py), and every chart
color comes from mckviz, so a token change flows through after `python tokens/build.py` and this script.
Requires: mckviz, python-pptx, xlsxwriter, lxml, pandas.
"""
from __future__ import annotations

import copy
import io
import shutil
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE, XL_TICK_MARK
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

import mckviz as mv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT = ROOT / "dist" / "office"
THEME_COLORS = OUT / "Theme Colors" / "McKesson Data Viz.xml"
THEME_FONTS = OUT / "Theme Fonts" / "McKesson Data Viz.xml"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
C = mv.colors
FONT = mv.FONT
SRC = "Source: Synthetic data for illustration only"
BAND_GAP = 50                       # Office gap width 50% -> bar : gap ~ 2 : 1 (chart.bar.band_fill)

# Slide geometry (16:9, inches)
W, H = 13.333, 7.5
# The McKesson Standard Template's grid: 0.39 in side margins, title box 0.38-1.31 in, footer and logo at 7.13 in.
LEFT, RIGHT = 0.39, 0.39
TITLE_TOP, TITLE_H, TITLE_PT = 0.38, 0.93, 26              # typography.roles.slide_title: Bold, McKesson Blue, 24-28 pt
SUB_TOP, CHART_TOP, CHART_H = 1.32, 1.8, 4.6
FOOT_TOP = 6.45                                            # source / footnote block ends at 6.95 in, above the footer
BODY_TOP, BODY_BOTTOM = 1.32, 6.95                         # content area: under the title box, above the source line
# Footer (as in the Standard Template): page number | thin blue rule | confidentiality line | date, centred on 7.2 in.
FOOTER_TOP, FOOTER_H, FOOTER_PT = 7.08, 0.24, 8
FOOTER_TEXT = "McKesson Proprietary and Confidential"
MASTER_NAME = "McKesson Data Viz"
AUTHOR = "McKesson Workforce Innovation"
TODAY = datetime.now()
DATE_TEXT = f"{TODAY.month}/{TODAY.day}/{TODAY.year}"        # placeholder text; PowerPoint updates the date field
OFFICIAL = ROOT / "reference" / "mckesson-branding" / "McKesson Standard Template.pptx"


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color.lstrip("#").upper())


# ====================================================================== theme
_SOLID = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
_LINE = (f'<a:ln w="12700" cap="flat" cmpd="sng" algn="ctr">{_SOLID}<a:prstDash val="solid"/><a:miter lim="800000"/>'
         '</a:ln>')
# Flat, not rounded: every theme fill is solid, every line 1 pt, and no effect style carries a shadow, glow or bevel,
# so Shape Styles and SmartArt in the template cannot bring back Office 2007's gradients and drop shadows.
FLAT_FMT_SCHEME = (f'<a:fmtScheme xmlns:a="{A_NS}" name="McKesson Flat">'
                   f'<a:fillStyleLst>{_SOLID * 3}</a:fillStyleLst>'
                   f'<a:lnStyleLst>{_LINE * 3}</a:lnStyleLst>'
                   f'<a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>" * 3}</a:effectStyleLst>'
                   f'<a:bgFillStyleLst>{_SOLID * 3}</a:bgFillStyleLst></a:fmtScheme>')


def themed_xml(theme_xml: bytes) -> bytes:
    """Swap the McKesson color and font schemes and a flat format scheme into a theme part (pptx or xlsx)."""
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(theme_xml, parser)
    elements = root.find(f"{{{A_NS}}}themeElements")
    for path, tag in ((THEME_COLORS, "clrScheme"), (THEME_FONTS, "fontScheme")):
        new = etree.fromstring(path.read_bytes(), parser)
        elements.replace(elements.find(f"{{{A_NS}}}{tag}"), new)
    elements.replace(elements.find(f"{{{A_NS}}}fmtScheme"), etree.fromstring(FLAT_FMT_SCHEME, parser))
    root.set("name", "McKesson Data Viz")
    # Excel silently ignores a theme whose XML declaration uses single quotes (lxml's default), so write it by hand.
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + etree.tostring(root, encoding="UTF-8")


def apply_theme(prs) -> None:
    theme = prs.slide_master.part.part_related_by(RT.THEME)
    theme._blob = themed_xml(theme.blob)


def widen_to_16x9(prs) -> None:
    """The default template is 4:3; stretch master and layout shapes that carry their own position."""
    factor = Inches(W) / prs.slide_width
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    for container in (prs.slide_master, *prs.slide_layouts):
        for shp in container.shapes:
            if shp._element.xfrm is not None:
                shp.left, shp.width = int(shp.left * factor), int(shp.width * factor)


def _xfrm(sp, left, top, width, height) -> None:
    """Give a master/layout shape its own position (replacing any inherited one)."""
    sppr = sp.find(qn("p:spPr"))
    old = sppr.find(qn("a:xfrm"))
    if old is not None:
        sppr.remove(old)
    xfrm = etree.Element(qn("a:xfrm"))
    etree.SubElement(xfrm, qn("a:off"), x=str(Inches(left)), y=str(Inches(top)))
    etree.SubElement(xfrm, qn("a:ext"), cx=str(Inches(width)), cy=str(Inches(height)))
    sppr.insert(0, xfrm)


def _body_pr(sp, anchor="t", wrap=True) -> None:
    """Zero insets so text starts exactly on the grid line."""
    tx = sp.find(qn("p:txBody"))
    old = tx.find(qn("a:bodyPr"))
    bp = etree.Element(qn("a:bodyPr"), lIns="0", tIns="0", rIns="0", bIns="0", anchor=anchor,
                       wrap="square" if wrap else "none")
    etree.SubElement(bp, qn("a:normAutofit") if wrap else qn("a:noAutofit"))
    tx.replace(old, bp)


def _lvl(style, n, size_pt, color_scheme=None, color_hex=None, bold=False, marl_in=0.0, algn="l", font=None,
         space_before_pt=0, line_pct=None):
    """A flat a:lvlNpPr: no bullet, no hanging indent."""
    old = style.find(qn(f"a:lvl{n}pPr"))
    p = etree.Element(qn(f"a:lvl{n}pPr"), marL=str(Inches(marl_in)), indent="0", algn=algn, defTabSz="914400",
                      rtl="0", eaLnBrk="1", latinLnBrk="0", hangingPunct="1")
    if line_pct:
        etree.SubElement(etree.SubElement(p, qn("a:lnSpc")), qn("a:spcPct"), val=str(line_pct * 1000))
    etree.SubElement(etree.SubElement(p, qn("a:spcBef")), qn("a:spcPts"), val=str(space_before_pt * 100))
    etree.SubElement(p, qn("a:buNone"))
    r = etree.SubElement(p, qn("a:defRPr"), sz=str(int(size_pt * 100)), kern="1200")
    if bold:
        r.set("b", "1")
    fill = etree.SubElement(r, qn("a:solidFill"))
    if color_hex:
        etree.SubElement(fill, qn("a:srgbClr"), val=color_hex.lstrip("#").upper())
    else:
        etree.SubElement(fill, qn("a:schemeClr"), val=color_scheme or "tx1")
    major = font is None and style.tag == qn("p:titleStyle")
    etree.SubElement(r, qn("a:latin"), typeface=font or ("+mj-lt" if major else "+mn-lt"))
    etree.SubElement(r, qn("a:ea"), typeface="+mj-ea" if major else "+mn-ea")
    etree.SubElement(r, qn("a:cs"), typeface="+mj-cs" if major else "+mn-cs")
    if old is not None:
        style.replace(old, p)
    else:
        style.append(p)


def _footer_para(sp, text=None, field=None) -> None:
    """Replace a footer placeholder's text with plain text or a live field (slidenum / datetime1)."""
    tx = sp.find(qn("p:txBody"))
    for p in tx.findall(qn("a:p")):
        tx.remove(p)
    p = etree.SubElement(tx, qn("a:p"))
    if field:
        fld = etree.SubElement(p, qn("a:fld"), type=field,
                               id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" if field == "slidenum"
                               else "{3A1B2C4D-5E6F-4A7B-8C9D-0E1F2A3B4C5D}")
        etree.SubElement(fld, qn("a:rPr"), lang="en-US")
        etree.SubElement(fld, qn("a:t")).text = "\u2039#\u203a" if field == "slidenum" else DATE_TEXT
    elif text:
        r = etree.SubElement(p, qn("a:r"))
        etree.SubElement(r, qn("a:rPr"), lang="en-US")
        etree.SubElement(r, qn("a:t")).text = text
    etree.SubElement(p, qn("a:endParaRPr"), lang="en-US")


def _footer_style(sp, algn="l") -> None:
    """Footer text: Light 8 pt muted grey, vertically centred on the footer line."""
    _body_pr(sp, anchor="ctr", wrap=False)
    tx = sp.find(qn("p:txBody"))
    lst = tx.find(qn("a:lstStyle"))
    for child in list(lst):
        lst.remove(child)
    _lvl(lst, 1, FOOTER_PT, color_hex=C.text_muted, algn=algn, font=f"{FONT} Light")


FOOTER_SLOTS = {                 # placeholder type -> (left, width, field, text); template order: page | rule | text | date
    "sldNum": (LEFT, 0.2, "slidenum", None),
    "ftr": (0.72, 2.15, None, FOOTER_TEXT),
    "dt": (2.95, 1.4, "datetime1", None),
}


def grid_master(prs) -> None:
    """Put the master and the layouts on the McKesson Standard Template's grid (python-pptx's default template has
    a centred 44 pt title at 0.5 in, a 32 pt bulleted body and footers at 0.5 in): title Bold 26 pt McKesson Blue at
    0.39 / 0.38 in, body 16/14 pt without bullets from 1.32 in, and the footer (page, confidentiality line, date)."""
    master = prs.slide_master._element
    master.find(qn("p:cSld")).set("name", MASTER_NAME)
    content_w = W - LEFT - RIGHT
    for sp in master.find(qn("p:cSld")).find(qn("p:spTree")).iterchildren(qn("p:sp")):
        ph = sp.find(".//" + qn("p:ph"))
        kind = ph.get("type", "body") if ph is not None else None
        if kind == "title":
            _xfrm(sp, LEFT, TITLE_TOP, content_w, TITLE_H)
            _body_pr(sp)
        elif kind == "body":
            _xfrm(sp, LEFT, BODY_TOP, content_w, BODY_BOTTOM - BODY_TOP)
            _body_pr(sp)
        elif kind in FOOTER_SLOTS:
            left, width, field, text = FOOTER_SLOTS[kind]
            _xfrm(sp, left, FOOTER_TOP, width, FOOTER_H)
            _footer_style(sp)
            _footer_para(sp, text, field)
    # The thin McKesson Blue rule between the page number and the confidentiality line.
    tree = master.find(qn("p:cSld")).find(qn("p:spTree"))
    next_id = max(int(e.get("id")) for e in tree.iter(qn("p:cNvPr"))) + 1
    tree.append(etree.fromstring(
        f'<p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{A_NS}">'
        f'<p:nvCxnSpPr><p:cNvPr id="{next_id}" name="Footer rule"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{Inches(0.62)}" y="{Inches(7.13)}"/><a:ext cx="0" cy="{Inches(0.14)}"/></a:xfrm>'
        f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
        f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{C.blue.lstrip("#").upper()}"/></a:solidFill></a:ln>'
        f'</p:spPr></p:cxnSp>'))
    # Show page number, footer and date on new slides; no header.
    hf = master.find(qn("p:hf"))
    if hf is None:
        hf = etree.Element(qn("p:hf"))
        master.find(qn("p:txStyles")).addprevious(hf)
    hf.set("hdr", "0")
    # Text styles: the title and a flat, bullet-free body.
    styles = master.find(qn("p:txStyles"))
    _lvl(styles.find(qn("p:titleStyle")), 1, TITLE_PT, color_scheme="tx2", bold=True, line_pct=90)
    body = styles.find(qn("p:bodyStyle"))
    for n in range(1, 10):
        _lvl(body, n, 16 if n == 1 else 14, marl_in=0.25 * (n - 1), space_before_pt=6, line_pct=100)
    # Layouts: footers say the confidentiality line; placeholders that carry their own position stay inside the
    # margins; the default template's per-layout 20-40 pt sizes, all caps and centring give way to the master's.
    half = (content_w - 0.3) / 2
    for lay in prs.slide_layouts:
        name = lay.name
        for sp in lay._element.find(qn("p:cSld")).find(qn("p:spTree")).iterchildren(qn("p:sp")):
            ph = sp.find(".//" + qn("p:ph"))
            if ph is None:
                continue
            kind, idx = ph.get("type", "body"), int(ph.get("idx", "0"))
            if kind == "ftr":
                _footer_para(sp, FOOTER_TEXT)
                continue
            if kind in ("sldNum", "dt"):
                _footer_para(sp, field=FOOTER_SLOTS[kind][2])
                continue
            for el in sp.iter(qn("a:defRPr")):
                for attr in ("sz", "cap"):
                    if attr in el.attrib and not (kind == "body" and el.get("b") == "1"):
                        el.attrib.pop(attr)
                if el.get("b") == "1" and kind == "body":
                    el.set("sz", "1600")                        # the comparison layout's column heads
            for el in sp.iter(*(qn(f"a:lvl{n}pPr") for n in range(1, 10))):
                if el.get("algn") == "ctr":
                    el.set("algn", "l")
            if name in ("Two Content", "Comparison") and kind != "title":
                col = (idx - 1) if name == "Two Content" else (0 if idx in (1, 2) else 1)
                head = name == "Comparison" and idx in (1, 3)
                top = BODY_TOP if head or name == "Two Content" else BODY_TOP + 0.5
                height = 0.4 if head else BODY_BOTTOM - top
                _xfrm(sp, LEFT + col * (half + 0.3), top, half, height)
                _body_pr(sp)
            else:
                xfrm = sp.find(qn("p:spPr")).find(qn("a:xfrm"))
                if xfrm is not None:                                # clamp to the side margins
                    off, ext = xfrm.find(qn("a:off")), xfrm.find(qn("a:ext"))
                    x = max(int(off.get("x")), Inches(LEFT))
                    r = min(int(off.get("x")) + int(ext.get("cx")), Inches(W - RIGHT))
                    off.set("x", str(x))
                    ext.set("cx", str(r - x))


def on_grid(prs_or_layout) -> bool:
    """True for the kit's own master (already on the grid); False for the official template."""
    master = prs_or_layout.slide_master._element
    return master.find(qn("p:cSld")).get("name") == MASTER_NAME


def set_properties(prs, title: str, description: str) -> None:
    """Replace python-pptx's defaults (author 'Steve Canny', 2013 dates, its own description) and drop its
    default thumbnail, which would otherwise show a generic picture in File Explorer and SharePoint."""
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    cp = prs.core_properties
    cp.title, cp.subject, cp.author, cp.last_modified_by = title, "McKesson data-viz starter kit", AUTHOR, AUTHOR
    cp.comments, cp.keywords, cp.category = description, "McKesson; data visualization; charts; template", ""
    cp.created = cp.modified = now
    cp.last_printed = now
    cp.revision = 1
    rels = prs.part.package._rels
    for rid, rel in list(rels.items()):
        if rel.reltype == RT.THUMBNAIL:
            rels.pop(rid)


def flat(shape) -> None:
    """No theme effect (shadow, glow, bevel) on a drawn shape or connector: effectRef idx 0."""
    ref = shape._element.find(".//" + qn("a:effectRef"))
    if ref is not None:
        ref.set("idx", "0")


# ====================================================================== slide furniture
def text_box(slide, left, top, width, height, text, size, color, bold=False, light=False, anchor=MSO_ANCHOR.TOP,
             align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
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
        run.font.name = f"{FONT} Light" if light else FONT
    return box


def layout(prs, name: str, fallback: int):
    """A layout by name (the official template), else the default template's layout by index."""
    return next((l for l in prs.slide_layouts if l.name == name), prs.slide_layouts[fallback])


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
        etree.SubElement(fld, qn("a:t")).text = "\u2039#\u203a" if kind == 13 else DATE_TEXT


def chart_slide(prs, headline, subtitle, footnote, notes, source=SRC):
    """Title Only layout: headline in the title placeholder, subtitle, then source/footnote bottom-left."""
    lay = layout(prs, "Title Only", 5)
    slide = prs.slides.add_slide(lay)
    title = slide.shapes.title
    title.text = headline                                      # position, size, weight and color come from the master
    if not on_grid(prs):                                       # the official template: place the title on its grid
        title.left, title.top = Inches(LEFT), Inches(TITLE_TOP)
        title.width, title.height = Inches(W - LEFT - RIGHT), Inches(TITLE_H)
        tf = title.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = True
        for r in tf.paragraphs[0].runs:                        # the official master says 34 pt; insight titles use 26
            r.font.size = Pt(TITLE_PT)
            r.font.bold = True
    text_box(slide, LEFT, SUB_TOP, W - LEFT - RIGHT, 0.35, subtitle, 14, C.text)
    foot = "\n".join(x for x in (footnote, source) if x)
    if foot:
        text_box(slide, LEFT, FOOT_TOP, W - LEFT - RIGHT, 0.5, foot, 9, C.text_muted, light=True,
                 anchor=MSO_ANCHOR.BOTTOM)
    if lay.name == "Title Only":
        add_footer(slide, lay)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


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
    run.font.name = FONT if bold else f"{FONT} Medium"         # typography.roles.label: Medium; emphasis: Bold
    run.font.color.rgb = rgb(color)
    if position is not None:
        dl.position = position


def line_shape(slide, x1, y1, x2, y2, color, width_pt=0.75, dash=True):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(width_pt)
    if dash:
        ln.line.dash_style = 4          # MSO_LINE_DASH_STYLE.DASH
    flat(ln)
    return ln


# ====================================================================== headlines (computed from the data, shared by both files)
def waterfall_headline(df) -> str:
    focus = {"Automation savings", "Contractor conversion"}
    growth = df.value_musd[(df.kind == "delta") & (df.value_musd > 0)].sum()
    offset = -df.value_musd[df.step.isin(focus)].sum()
    return f"Automation and contractor conversion offset ~{offset / growth * 100:.0f}% of FY26 labor cost growth"


def stacked_headline(df) -> str:
    others = df.contingent_pct[df.function != "Technology"].mean()
    tech = float(df.contingent_pct[df.function == "Technology"].iloc[0])
    return f"Technology uses contingent labor at more than {int(tech / others)}× the average rate of other functions"


# ====================================================================== slides
def slide_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = slide.shapes.add_textbox(Inches(LEFT), Inches(2.6), Inches(W - 2 * LEFT), Inches(1.2))
    box.text_frame.margin_left = box.text_frame.margin_right = 0
    p = box.text_frame.paragraphs[0]
    for text, bold in (("Workforce", True), (" chart starter", False)):     # brand signature: bold lead + light rest
        run = p.add_run()
        run.text = text
        run.font.size = Pt(44)
        run.font.bold = bold
        run.font.name = FONT if bold else f"{FONT} Light"
        run.font.color.rgb = rgb(C.blue)
    text_box(slide, LEFT, 3.75, 9.5, 1.2,
             "Native, editable charts in the McKesson data-viz style. Copy a slide, then right-click the chart › "
             "Edit Data to drop in your numbers.", 16, C.text)
    text_box(slide, LEFT, FOOT_TOP, 9, 0.5, "McKesson data-viz starter kit · generated from tokens/tokens.json", 9,
             C.text_muted, light=True, anchor=MSO_ANCHOR.BOTTOM)
    slide.notes_slide.notes_text_frame.text = (
        "Install Libre Franklin (fonts/LibreFranklin) and the theme (docs/office-setup.md) before editing, "
        "so the text renders in the brand font.")


def slide_rules(prs):
    slide = chart_slide(prs, "Every chart in this deck follows the same six rules",
                        "Checklist for any chart you add (full version: docs/qa-checklist.md)", None,
                        "Keep this slide out of client-facing decks; it is a reminder for the author.", source=None)
    rules = [
        ("Headline = the insight", "A full sentence with the number. The slide title is the headline."),
        ("Subtitle = the measure", "Metric, unit, scope, period. Neutral, no opinion."),
        ("Grey, then highlight", "Everything grey (B4B0A5); the headline's item blue (005A8C); one exception navy (143359). Orange only means worse."),
        ("Label directly", "Data labels on bars and line ends; delete the value axis, gridlines and legend."),
        ("Honest scales", "Bars from zero (waterfall breaks marked); no dual axes; ≤ 6 colors."),
        ("Source and n", "Source, as-of date and population bottom-left. No group under 10 people."),
    ]
    for i, (head, body) in enumerate(rules):
        col, row = i % 2, i // 2
        x, y = LEFT + col * 6.2, 1.95 + row * 1.5
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.08), Inches(1.0))
        fill(bar, C.focus)
        bar.line.fill.background()
        flat(bar)
        text_box(slide, x + 0.25, y, 5.6, 0.4, head, 16, C.headline, bold=True)
        text_box(slide, x + 0.25, y + 0.42, 5.6, 0.6, body, 13, C.text)
    return slide


def slide_bar(prs):
    df = pd.read_csv(DATA / "attrition_by_job_family.csv").sort_values("vol_attrition_pct")   # ascending: top = largest
    ent = float(df.enterprise_rate_pct.iloc[0])
    focus = set(df.job_family[df.vol_attrition_pct > 20])
    slide = chart_slide(
        prs, f"Two frontline job families lose about 1 in 4 people a year, well above the {ent:.1f}% enterprise rate",
        "Voluntary attrition by job family, FY26 (%)",
        "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.",
        "Bar highlight. To change the data: right-click › Edit Data. To recolor a bar: click it twice to select only that "
        "bar › Format Data Point › Fill. The dashed enterprise line is a drawn shape positioned for an axis of 0–30: "
        "move it if the rate changes. Build-up: duplicate the slide, make all bars grey on the first copy.")
    data = CategoryChartData()
    data.categories = list(df.job_family)
    data.add_series("Voluntary attrition (%)", list(df.vol_attrition_pct))
    frame, chart = add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, data)
    px, py, pw, ph = 0.25, 0.08, 0.68, 0.9
    plot_layout(chart, px, py, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = BAND_GAP
    plot.vary_by_categories = False
    series = plot.series[0]
    fill(series, C.context)
    for i, (fam, val) in enumerate(zip(df.job_family, df.vol_attrition_pct)):
        hi = fam in focus
        if hi:
            fill(series.points[i], C.focus)
        point_label(series.points[i], f"{val:.1f}%", C.headline if hi else C.text, bold=hi,
                    position=XL_LABEL_POSITION.OUTSIDE_END)
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = 0, 30
    va.visible = False
    va.has_major_gridlines = False
    ca = chart.category_axis
    baseline(ca)
    ca.tick_labels.font.size = Pt(12)
    ca.tick_labels.font.color.rgb = rgb(C.text)
    # Benchmark: a labelled, dashed navy line drawn at the enterprise rate on the pinned plot area.
    fl, ft, fw, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))
    x = fl + fw * (px + pw * ent / 30)
    line_shape(slide, x, ft + fh * py - 0.05, x, ft + fh * (py + ph), C.total)
    text_box(slide, x - 1.0, ft + fh * py - 0.33, 2.0, 0.26, f"Enterprise {ent:.1f}%", 11, C.annotation,
             align=PP_ALIGN.CENTER)
    return slide


def slide_line(prs):
    df = pd.read_csv(DATA / "data_ai_supply_demand.csv")
    gap = int(df.demand_fte.iloc[-1] - df.internal_supply_fte.iloc[-1])
    slide = chart_slide(
        prs, f"Without action, Data & AI demand outruns internal supply by about {round(gap, -1):,} FTE by 2030",
        "Forecast Data & AI roles, 2024–2030, base scenario (FTE)",
        "Supply = current headcount − projected attrition + planned internal moves; excludes external hiring. "
        "Forecast, not actuals.",
        "Line chart with end labels instead of a legend. The end labels are data labels on the last point "
        "(Format Data Label › Label Contains: Series Name + Value). The gap note is a text box.")
    data = CategoryChartData()
    data.categories = [str(y) for y in df.year]
    data.add_series("Demand", list(df.demand_fte))
    data.add_series("Internal supply", list(df.internal_supply_fte))
    frame, chart = add_chart(slide, XL_CHART_TYPE.LINE, data)
    px, py, pw, ph = 0.06, 0.04, 0.74, 0.86
    plot_layout(chart, px, py, pw, ph)
    lo, hi = 800, 1700
    for series, color, name in zip(chart.plots[0].series, (C.total, C.focus), ("Demand", "Internal supply")):
        series.format.line.color.rgb = rgb(color)
        series.format.line.width = Pt(2.25)
        series.smooth = False
        series.marker.style = XL_MARKER_STYLE.NONE
        last = series.points[len(df) - 1]
        point_label(last, f"{name} {series.values[-1]:,.0f}", color, bold=True, position=XL_LABEL_POSITION.RIGHT)
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = lo, hi, 200
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = rgb(C.grid)
    va.major_gridlines.format.line.width = Pt(0.75)
    va.tick_labels.number_format = "#,##0"
    va.tick_labels.number_format_is_linked = False
    va.tick_labels.font.size = Pt(11)
    va.tick_labels.font.color.rgb = rgb(C.text_muted)
    baseline(va, visible=False)
    ca = chart.category_axis
    baseline(ca)
    ca.tick_labels.font.size = Pt(11)
    ca.tick_labels.font.color.rgb = rgb(C.text_muted)
    fl, ft, fw, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))
    mid = (df.demand_fte.iloc[-1] + df.internal_supply_fte.iloc[-1]) / 2
    y = ft + fh * (py + ph * (1 - (mid - lo) / (hi - lo)))
    text_box(slide, fl + fw * (px + pw) + 0.12, y - 0.25, 2.4, 0.5, f"Gap {gap:,} FTE\nby 2030", 12,
             C.negative_text, bold=True)
    return slide


def slide_waterfall(prs):
    df = pd.read_csv(DATA / "labor_cost_bridge.csv")
    focus = {"Automation savings", "Contractor conversion"}
    slide = chart_slide(
        prs, waterfall_headline(df),
        "Labor cost bridge, FY25 to FY26 ($M)",
        "Value axis starts at $3,900M (break marks on the totals) so the drivers are readable.",
        "Waterfall built as a stacked column: an invisible 'Base' series lifts each change to the running total. "
        "Edit the 'Change' and 'Total' columns in Edit Data; recompute 'Base' as the running total before each step. "
        "Office 2016+ also has Insert › Waterfall, but it can't break the axis or recolor single bars by rule.")
    base, change, total, running = [], [], [], 0.0
    for r in df.itertuples():
        if r.kind == "total":
            running = r.value_musd
            base.append(0); change.append(0); total.append(r.value_musd)
        else:
            base.append(running + min(r.value_musd, 0)); change.append(abs(r.value_musd)); total.append(0)
            running += r.value_musd
    data = CategoryChartData()
    data.categories = [textwrap.fill(s, 14) for s in df.step]
    data.add_series("Base", base)
    data.add_series("Change", change)
    data.add_series("Total", total)
    data.add_series("Label", [0] * len(df))           # zero-height carrier: its labels sit just above each column
    frame, chart = add_chart(slide, XL_CHART_TYPE.COLUMN_STACKED, data)
    px, py, pw, ph = 0.02, 0.06, 0.96, 0.76
    plot_layout(chart, px, py, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = BAND_GAP
    plot.overlap = 100
    s_base, s_change, s_total, s_label = plot.series
    no_fill(s_base)
    no_fill(s_label)
    fill(s_total, C.total)
    fill(s_change, C.context)
    lo, hi = 3900, 4500
    tops = []
    for i, r in df.iterrows():
        if r.kind == "total":
            tops.append(r.value_musd)
            point_label(s_label.points[i], f"{r.value_musd:,.0f}", C.headline, bold=True,
                        position=XL_LABEL_POSITION.INSIDE_BASE)
        else:
            tops.append(base[i] + change[i])
            hit = r.step in focus
            if hit:
                fill(s_change.points[i], C.focus)
            point_label(s_label.points[i], mv.signed(r.value_musd), C.headline if hit else C.text, bold=hit,
                        position=XL_LABEL_POSITION.INSIDE_BASE)
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = lo, hi
    va.visible = False
    va.has_major_gridlines = False
    ca = chart.category_axis
    baseline(ca)
    ca.tick_labels.font.size = Pt(11)
    ca.tick_labels.font.color.rgb = rgb(C.text)
    # Axis-break marks: two short white slashes across the bottom of each total bar.
    fl, ft, fw, fh = (Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))
    n = len(df)
    slot = fw * pw / n
    bar_w = slot / (1 + BAND_GAP / 100)
    y0 = ft + fh * (py + ph) - 0.28
    for i in (0, n - 1):
        cx = fl + fw * px + slot * (i + 0.5)
        for dy in (0.0, 0.09):
            line_shape(slide, cx - bar_w / 2 - 0.03, y0 + dy + 0.05, cx + bar_w / 2 + 0.03, y0 + dy - 0.05, "#FFFFFF",
                       width_pt=2.5, dash=False)
    return slide


def slide_stacked(prs):
    df = pd.read_csv(DATA / "workforce_mix.csv").sort_values("contingent_pct")       # ascending: top = largest
    slide = chart_slide(
        prs, stacked_headline(df),
        "Workforce composition by function, 2026 (% of workers)", None,
        "100% stacked bar. The segment the headline is about (contingent) sits on the baseline in blue, so every "
        "bar's value starts level; the rest are greys. The key is top-left in stack order; or delete it and type "
        "the segment names above the top bar.")
    data = CategoryChartData()
    data.categories = list(df.function)
    parts = [("contingent_pct", "Contingent", C.focus), ("employee_ft_pct", "Full-time", C.context),
             ("employee_pt_pct", "Part-time", C.context_light)]       # story segment first: on the baseline
    for col, name, _ in parts:
        data.add_series(name, list(df[col]))
    frame, chart = add_chart(slide, XL_CHART_TYPE.BAR_STACKED_100, data)
    plot_layout(chart, 0.14, 0.1, 0.84, 0.86)
    plot = chart.plots[0]
    plot.gap_width = BAND_GAP
    plot.overlap = 100
    for series, (col, name, color) in zip(plot.series, parts):
        fill(series, color)
        series.format.line.color.rgb = rgb("#FFFFFF")
        series.format.line.width = Pt(1.5)
        for i, (fn, v) in enumerate(zip(df.function, df[col])):
            hi = col == "contingent_pct" and fn == "Technology"
            if v >= 5:                                         # labels only where they fit
                point_label(series.points[i], f"{v:.0f}%", mv.text_on(color), bold=hi, size=12 if hi else 11,
                            position=XL_LABEL_POSITION.CENTER)
    va = chart.value_axis
    va.visible = False
    va.has_major_gridlines = False
    ca = chart.category_axis
    baseline(ca, visible=False)
    ca.tick_labels.font.size = Pt(12)
    ca.tick_labels.font.color.rgb = rgb(C.text)
    legend_top_left(chart)
    return slide


def build_pptx() -> Path:
    prs = Presentation()
    widen_to_16x9(prs)
    apply_theme(prs)
    grid_master(prs)
    template = OUT / "McKesson-DataViz.potx"
    set_properties(prs, "McKesson Data Viz template",
                   "16:9 PowerPoint template with the McKesson data-viz theme on the Standard Template grid.")
    _save_as_template(prs, template)                       # theme + layouts only, before any slides are added
    set_properties(prs, "McKesson data-viz chart starter",
                   "Native, editable sample charts in the McKesson data-viz style, generated from tokens/tokens.json.")
    slide_cover(prs)
    slide_rules(prs)
    for build in (slide_bar, slide_line, slide_waterfall, slide_stacked):
        build(prs)
    path = OUT / "McKesson-DataViz-Starter.pptx"
    prs.save(path)
    return path


def clear_slides(prs) -> None:
    """Remove every slide (the official template ships 40 sample and icon slides); masters and layouts stay."""
    ids = prs.slides._sldIdLst
    for sld in list(ids):
        prs.part.drop_rel(sld.rId)
        ids.remove(sld)


def official_cover(prs) -> None:
    lay = layout(prs, "Title 1", 0)
    slide = prs.slides.add_slide(lay)
    slide.shapes.title.text = "Workforce chart starter"
    for ph in slide.placeholders:
        if ph.placeholder_format.type == 4:                    # SUBTITLE
            ph.text = "Native, editable charts in the McKesson data-viz style. Copy a slide, then right-click the " \
                      "chart › Edit Data to drop in your numbers."
    slide.notes_slide.notes_text_frame.text = (
        "Built from the McKesson Standard Template by office/build_office.py. Internal use only.")


def build_pptx_official() -> Path | None:
    """The same slides on the McKesson Standard Template, when it is available locally (never committed)."""
    if not OFFICIAL.exists():
        return None
    prs = Presentation(str(OFFICIAL))
    clear_slides(prs)
    set_properties(prs, "McKesson data-viz chart starter (Standard Template)",
                   "Native, editable sample charts on the McKesson Standard Template. Internal use only.")
    official_cover(prs)
    slide_rules(prs)
    for build in (slide_bar, slide_line, slide_waterfall, slide_stacked):
        build(prs)
    path = OUT / "McKesson-DataViz-Starter-Official.pptx"
    prs.save(path)
    return path


def _save_as_template(prs, path: Path) -> None:
    """A .potx is a .pptx whose main part has the template content type."""
    buf = io.BytesIO()
    prs.save(buf)
    src = zipfile.ZipFile(buf)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            blob = src.read(item.filename)
            if item.filename == "[Content_Types].xml":
                blob = blob.replace(b"presentationml.presentation.main+xml", b"presentationml.template.main+xml")
            dst.writestr(item, blob)


# ====================================================================== Excel
def build_xlsx() -> Path:
    import xlsxwriter

    path = OUT / "McKesson-DataViz-Charts.xlsx"
    wb = xlsxwriter.Workbook(str(path), {"default_format_properties": {"font_name": FONT, "font_size": 10,
                                                                         "font_color": C.text}})
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    wb.set_properties({"title": "McKesson data-viz chart workbook", "subject": "McKesson data-viz starter kit",
                       "author": AUTHOR, "manager": "", "company": "McKesson", "category": "",
                       "keywords": "McKesson; data visualization; charts",
                       "comments": "Palette sheet, native sample charts and a heat table in the McKesson data-viz "
                                   "style, generated from tokens/tokens.json.", "created": now})
    roles = mv.TOKENS["typography"]["roles"]
    pt = {k: roles[k]["size_pt"] for k in ("headline", "subtitle", "label", "tick", "footnote")}
    f = {   # typography.roles: headline SemiBold 18, subtitle 14, labels Medium 12, ticks 11, footnote/source Light 9
        "head": wb.add_format({"font_size": pt["headline"], "font_color": C.headline, "font_name": f"{FONT} SemiBold"}),
        "sub": wb.add_format({"font_size": pt["subtitle"], "font_color": C.text}),
        "note": wb.add_format({"font_size": pt["footnote"], "font_color": C.text_muted, "font_name": f"{FONT} Light"}),
        "th": wb.add_format({"bold": True, "font_color": C.headline, "bottom": 1, "bottom_color": C.axis,
                             "text_wrap": True, "valign": "bottom"}),
        "th_num": wb.add_format({"bold": True, "font_color": C.headline, "bottom": 1, "bottom_color": C.axis,
                                 "text_wrap": True, "valign": "bottom", "align": "right"}),
        "cell": wb.add_format({"bottom": 1, "bottom_color": C.grid}),
        "int": wb.add_format({"num_format": "#,##0", "bottom": 1, "bottom_color": C.grid}),
        "dec": wb.add_format({"num_format": "0.0", "bottom": 1, "bottom_color": C.grid}),
        "delta": wb.add_format({"num_format": '+0.0;"−"0.0;0.0', "bottom": 1, "bottom_color": C.grid}),
        "hex": wb.add_format({"font_name": "Consolas", "font_size": 10}),
        "bold": wb.add_format({"bold": True, "font_color": C.headline}),
        "focus_row": wb.add_format({"bold": True, "font_color": C.headline, "bottom": 1, "bottom_color": C.grid}),
    }

    def frame(ws, headline, subtitle, footnote, last_row):
        ws.hide_gridlines(2)
        ws.set_row(0, 26)
        ws.set_row(1, 20)
        ws.write(0, 0, headline, f["head"])
        ws.write(1, 0, subtitle, f["sub"])
        if footnote:
            ws.write(last_row, 0, footnote, f["note"])
        ws.write(last_row + 1, 0, SRC, f["note"])

    def base_chart(kind, subtype=None):
        chart = wb.add_chart({"type": kind, **({"subtype": subtype} if subtype else {})})
        chart.set_title({"none": True})
        chart.set_legend({"none": True})
        chart.set_chartarea({"border": {"none": True}, "fill": {"none": True}})
        chart.set_plotarea({"border": {"none": True}, "fill": {"none": True}})
        chart.set_size({"width": 860, "height": 430})
        return chart

    axis_font = {"name": FONT, "size": pt["tick"], "color": C.text_muted}
    label_font = {"name": f"{FONT} Medium", "size": pt["label"], "color": C.text}       # data labels: Medium
    bold_label = {**label_font, "name": FONT, "bold": True}                             # emphasized labels: Bold

    # --- Read me
    ws = wb.add_worksheet("Read me")
    ws.hide_gridlines(2)
    ws.set_row(0, 26)
    ws.set_row(1, 20)
    ws.set_column(0, 0, 110)
    lines = [
        ("McKesson data-viz chart workbook", f["head"]),
        ("Native Excel charts styled to the McKesson data-viz rules. Copy a chart into your workbook or PowerPoint "
         "(Paste › Use Destination Theme & Embed Workbook), then point it at your data.", f["sub"]),
        ("", None),
        ("How to reuse a chart", f["bold"]),
        ("1. Right-click the chart › Select Data to point it at your range, or overwrite the numbers in the table "
         "next to it.", None),
        ("2. Right-click › Save as Template… to keep the formatting as a .crtx chart template.", None),
        ("3. Recolor only what the headline names: click a bar twice to select just that point › Fill.", None),
        ("", None),
        ("The rules (full version: docs/principles.md)", f["bold"]),
        ("• The headline is the insight, as a full sentence with the number. The subtitle is the metric, unit, "
         "scope and period.", None),
        ("• Grey context, blue focus, one navy exception; orange only for negatives. At most 6 categorical colors.",
         None),
        ("• Label values directly and delete the value axis, gridlines and legend. Bars start at zero.", None),
        ("• Source, as-of date and population at the bottom. No group of fewer than 10 people.", None),
        ("", None),
        ("Theme: Page Layout › Colors and Fonts show 'McKesson Data Viz' in this file. To use them everywhere, "
         "install the theme files (docs/office-setup.md) and Libre Franklin (fonts/LibreFranklin).", f["note"]),
        ("Generated by office/build_office.py from tokens/tokens.json. Synthetic data for illustration only.",
         f["note"]),
    ]
    for i, (text, fmt) in enumerate(lines):
        ws.write(i, 0, text, fmt) if fmt else ws.write(i, 0, text)

    # --- Palette
    ws = wb.add_worksheet("Palette")
    ws.hide_gridlines(2)
    ws.set_column(0, 0, 6)
    ws.set_column(1, 1, 22)
    ws.set_column(2, 3, 12)
    ws.set_column(4, 4, 70)
    ws.write(0, 0, "Chart color roles", f["head"])
    ws.write(1, 0, "Use roles, not favorite colors: grey everything, then color only what the headline names.", f["sub"])
    roles = [("Context", C.context, "Everything the reader should see but not focus on"),
             ("Context light", C.context_light, "De-emphasized fills, suppressed cells"),
             ("Focus", C.focus, "What the headline is about; default single-series color"),
             ("Accent", C.accent, "The one exception that must pop (navy; never orange)"),
             ("Light blue series", C.focus_light, "The series when navy marks the exception"),
             ("Total / benchmark", C.total, "Totals, target and benchmark lines"),
             ("Axis / baseline", C.axis, "Thin zero baseline"),
             ("Grid", C.grid, "Gridlines, only when values aren't labelled"),
             ("Headline text", C.headline, "Headlines, emphasized labels"),
             ("Body text", C.text, "Subtitles, data labels"),
             ("Muted text", C.text_muted, "Ticks, footnotes, source"),
             ("Unfavorable text", C.negative_text, "Unfavorable values as text (fill: orange, for negatives only)"),
             ("Favorable", C.positive, "Favorable fills (text: " + C.positive_text + ")")]
    row = 3
    ws.write_row(row, 0, ["", "Role", "Hex", "RGB", "Use"], f["th"])
    for name, hx, use in roles:
        row += 1
        ws.write(row, 0, "", wb.add_format({"bg_color": hx}))
        ws.write(row, 1, name, f["cell"])
        ws.write(row, 2, hx, f["hex"])
        ws.write(row, 3, ", ".join(str(int(hx[i:i + 2], 16)) for i in (1, 3, 5)), f["hex"])
        ws.write(row, 4, use, f["cell"])
    # Status (RAG): its own block, with the rule beside it, so nobody picks these for data series.
    row += 2
    ws.write(row, 0, "Status colors: status only, with symbol and word", f["bold"])
    row += 1
    ws.write_row(row, 0, ["", "Status", "Hex", "Symbol", "Rule"], f["th"])
    status_rule = ("Status only (trackers, roadmaps, scorecard status columns), never for data series. Always show the "
                   "symbol and the word with the color, so it reads without color and in grayscale.")
    for st in mv.STATUS.values():
        row += 1
        ws.write(row, 0, st["symbol"], wb.add_format({"bg_color": st["value"], "font_color": mv.text_on(st["value"]),
                                                      "bold": True, "align": "center"}))
        ws.write(row, 1, st["label"], f["cell"])
        ws.write(row, 2, st["value"], f["hex"])
        ws.write(row, 3, st["symbol"], f["cell"])
    ws.merge_range(row - len(mv.STATUS) + 1, 4, row, 4, status_rule,
                   wb.add_format({"text_wrap": True, "valign": "top", "bottom": 1, "bottom_color": C.grid}))
    row = 1
    for title, colors, note in (("Categorical (fixed order, max 6)", mv.CATEGORICAL[:6], "Series 1 → 6"),
                                ("Sequential blue (light → dark)", mv.SEQUENTIAL["blue"], "Heatmaps, single measure"),
                                ("Sequential orange (risk only)", mv.SEQUENTIAL["orange"], "Only when darker means worse, and say so"),
                                ("Diverging orange–blue (midpoint = benchmark)", mv.DIVERGING, "Gaps to benchmark"),
                                ("Steps, blue → green (ordered stages)", mv.STEPS,
                                 "Process stages and journeys only; not for data magnitude or unordered categories")):
        row += 2                                           # ramps sit in equal-width columns G:M
        ws.write(row, 6, f"{title}: {note.lower()}", f["bold"])
        row += 1
        for j, hx in enumerate(colors):
            ws.write(row, 6 + j, "", wb.add_format({"bg_color": hx}))
        row += 1
        for j, hx in enumerate(colors):
            ws.write(row, 6 + j, hx, f["hex"])
    ws.set_column(5, 5, 3)
    ws.set_column(6, 12, 10)

    # --- Bar
    df = pd.read_csv(DATA / "attrition_by_job_family.csv").sort_values("vol_attrition_pct", ascending=False)
    ent = float(df.enterprise_rate_pct.iloc[0])
    focus = set(df.job_family[df.vol_attrition_pct > 20])
    ws = wb.add_worksheet("Bar")
    frame(ws, f"Two frontline job families lose about 1 in 4 people a year, well above the {ent:.1f}% enterprise rate",
          "Voluntary attrition by job family, FY26 (%)",
          "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.", 30)
    ws.set_column(0, 0, 30)
    ws.set_column(1, 2, 14)
    ws.write_row(3, 0, ["Job family", "Voluntary attrition (%)", "Headcount"], f["th"])
    for i, r in enumerate(df.itertuples(), start=4):
        hi = r.job_family in focus
        ws.write(i, 0, r.job_family, f["focus_row"] if hi else f["cell"])
        ws.write(i, 1, r.vol_attrition_pct, f["dec"])
        ws.write(i, 2, r.headcount, f["int"])
    n = len(df)
    chart = base_chart("bar")
    chart.add_series({
        "categories": ["Bar", 4, 0, 3 + n, 0], "values": ["Bar", 4, 1, 3 + n, 1], "gap": BAND_GAP,
        "fill": {"color": C.context},
        "points": [{"fill": {"color": C.focus if j in focus else C.context}} for j in df.job_family],
        "data_labels": {"value": True, "position": "outside_end", "num_format": '0.0"%"', "font": label_font,
                        "custom": [{"value": f"{v:.1f}%", "font": {**bold_label, "color": C.headline}}
                                   if j in focus else None for j, v in zip(df.job_family, df.vol_attrition_pct)]},
    })
    chart.set_x_axis({"visible": False, "min": 0, "max": 30, "major_gridlines": {"visible": False}})
    chart.set_y_axis({"reverse": True, "num_font": {**axis_font, "size": pt["label"], "color": C.text},
                      "major_tick_mark": "none", "line": {"color": C.axis, "width": 0.75}})
    ws.insert_chart(3, 4, chart)
    ws.write(26, 4, f"Enterprise rate {ent:.1f}%: add it as a labelled dashed line (Insert › Shapes › Line, "
                    f"{C.total}, 0.75 pt) or see the PowerPoint starter deck.", f["note"])

    # --- Line
    df = pd.read_csv(DATA / "data_ai_supply_demand.csv")
    gap = int(df.demand_fte.iloc[-1] - df.internal_supply_fte.iloc[-1])
    ws = wb.add_worksheet("Line")
    frame(ws, f"Without action, Data & AI demand outruns internal supply by about {round(gap, -1):,} FTE by 2030",
          "Forecast Data & AI roles, 2024–2030, base scenario (FTE)",
          "Supply = current headcount − projected attrition + planned internal moves. Forecast, not actuals.", 30)
    ws.set_column(0, 2, 14)
    ws.write_row(3, 0, ["Year", "Demand", "Internal supply"], f["th"])
    for i, r in enumerate(df.itertuples(), start=4):
        ws.write(i, 0, str(r.year), f["cell"])
        ws.write(i, 1, r.demand_fte, f["int"])
        ws.write(i, 2, r.internal_supply_fte, f["int"])
    n = len(df)
    chart = base_chart("line")
    for col, color in ((1, C.total), (2, C.focus)):
        name = "Demand" if col == 1 else "Internal supply"
        chart.add_series({
            "name": ["Line", 3, col], "categories": ["Line", 4, 0, 3 + n, 0], "values": ["Line", 4, col, 3 + n, col],
            "line": {"color": color, "width": 2.25}, "marker": {"type": "none"},
            "data_labels": {"value": True, "position": "right", "font": {**bold_label, "color": color},
                            "custom": [{"delete": True}] * (n - 1) + [{"value": f"{name} {df.iloc[-1, col]:,.0f}"}]},
        })
    chart.set_y_axis({"min": 800, "max": 1700, "major_unit": 200, "num_format": "#,##0", "num_font": axis_font,
                      "line": {"none": True}, "major_gridlines": {"visible": True, "line": {"color": C.grid, "width": 0.75}}})
    chart.set_x_axis({"num_font": axis_font, "major_tick_mark": "none", "line": {"color": C.axis, "width": 0.75}})
    chart.set_plotarea({"layout": {"x": 0.07, "y": 0.05, "width": 0.7, "height": 0.82},
                        "border": {"none": True}, "fill": {"none": True}})
    ws.insert_chart(3, 4, chart)

    # --- Waterfall
    df = pd.read_csv(DATA / "labor_cost_bridge.csv")
    wf_focus = {"Automation savings", "Contractor conversion"}
    ws = wb.add_worksheet("Waterfall")
    frame(ws, waterfall_headline(df),
          "Labor cost bridge, FY25 to FY26 ($M)",
          "Value axis starts at $3,900M so the drivers are readable; say so wherever the chart is used.", 30)
    ws.set_column(0, 0, 28)
    ws.set_column(1, 5, 11)
    ws.write_row(3, 0, ["Step", "Value", "Base", "Change", "Total", "Label"], f["th"])
    run = 0.0                                              # Base = running total before the step (invisible series)
    for i, r in enumerate(df.itertuples(), start=4):
        ws.write(i, 0, r.step, f["focus_row"] if r.step in wf_focus else f["cell"])
        ws.write(i, 1, r.value_musd, f["int"])
        if r.kind == "total":
            run = r.value_musd
            ws.write_row(i, 2, [0, 0, r.value_musd, 0], f["int"])
        else:
            ws.write_row(i, 2, [run + min(r.value_musd, 0), abs(r.value_musd), 0, 0], f["int"])
            run += r.value_musd
    n = len(df)
    chart = base_chart("column", "stacked")
    chart.add_series({"name": "Base", "categories": ["Waterfall", 4, 0, 3 + n, 0], "values": ["Waterfall", 4, 2, 3 + n, 2],
                      "fill": {"none": True}, "border": {"none": True}, "gap": BAND_GAP})
    chart.add_series({
        "name": "Change", "categories": ["Waterfall", 4, 0, 3 + n, 0], "values": ["Waterfall", 4, 3, 3 + n, 3],
        "fill": {"color": C.context},
        "points": [{"fill": {"color": C.focus if st in wf_focus else C.context}} for st in df.step],
    })
    chart.add_series({"name": "Total", "categories": ["Waterfall", 4, 0, 3 + n, 0],
                      "values": ["Waterfall", 4, 4, 3 + n, 4], "fill": {"color": C.total}})
    labels = []                                            # zero-height carrier series: labels sit just above each column
    for st, v, k in zip(df.step, df.value_musd, df.kind):
        hot = st in wf_focus
        labels.append({"value": f"{v:,.0f}" if k == "total" else mv.signed(v),
                       "font": {**(bold_label if k == "total" or hot else label_font),
                                "color": C.headline if k == "total" or hot else C.text}})
    chart.add_series({"name": "Label", "categories": ["Waterfall", 4, 0, 3 + n, 0],
                      "values": ["Waterfall", 4, 5, 3 + n, 5], "fill": {"none": True}, "border": {"none": True},
                      "data_labels": {"value": True, "position": "inside_base", "custom": labels}})
    chart.set_y_axis({"min": 3900, "max": 4500, "visible": False, "major_gridlines": {"visible": False}})
    chart.set_x_axis({"num_font": {**axis_font, "color": C.text}, "major_tick_mark": "none",
                      "line": {"color": C.axis, "width": 0.75}})
    ws.insert_chart(3, 7, chart)

    # --- Stacked 100%
    df = pd.read_csv(DATA / "workforce_mix.csv").sort_values("contingent_pct", ascending=False)
    ws = wb.add_worksheet("Stacked 100%")
    frame(ws, stacked_headline(df),
          "Workforce composition by function, 2026 (% of workers)", None, 30)
    ws.set_column(0, 3, 13)
    ws.write_row(3, 0, ["Function", "Contingent", "Full-time", "Part-time"], f["th"])   # story segment first
    for i, r in enumerate(df.itertuples(), start=4):
        ws.write(i, 0, r.function, f["focus_row"] if r.function == "Technology" else f["cell"])
        ws.write_row(i, 1, [r.contingent_pct, r.employee_ft_pct, r.employee_pt_pct], f["int"])
    n = len(df)
    chart = base_chart("bar", "percent_stacked")
    for col, color in ((1, C.focus), (2, C.context), (3, C.context_light)):
        chart.add_series({
            "name": ["Stacked 100%", 3, col], "categories": ["Stacked 100%", 4, 0, 3 + n, 0],
            "values": ["Stacked 100%", 4, col, 3 + n, col], "fill": {"color": color},
            "border": {"color": "#FFFFFF", "width": 1.5}, "gap": BAND_GAP, "overlap": 100,
            "data_labels": {"value": True, "position": "center", "num_format": '0"%"',
                            "font": {**label_font, "color": mv.text_on(color)}},
        })
    chart.set_legend({"position": "top", "font": {**axis_font, "size": pt["label"], "color": C.text}, "layout": {"x": 0.0, "y": 0.0, "width": 0.45, "height": 0.08}})
    chart.set_x_axis({"visible": False, "major_gridlines": {"visible": False}})
    chart.set_y_axis({"reverse": True, "num_font": {**axis_font, "size": pt["label"], "color": C.text},
                      "major_tick_mark": "none", "line": {"none": True}})
    ws.insert_chart(3, 5, chart)

    # --- Heat table (conditional formatting, the tables.md pattern)
    df = pd.read_csv(DATA / "job_family_scorecard.csv").sort_values("vol_attrition_pct", ascending=False)
    ws = wb.add_worksheet("Heat table")
    frame(ws, "The two largest frontline job families combine the highest attrition with the lowest engagement",
          "Workforce scorecard by job family, FY26; totals weighted by headcount",
          "Attrition shaded in 5-point classes. Orange change = attrition rising vs. FY25.", 15)
    # Column B is a bar-only helper (=headcount) so the inline bar never sits under the digits.
    heads = ["Job family", "", "Headcount", "Voluntary attrition (%)", "Change vs. FY25 (pts)", "Median days to fill",
             "Internal fill rate (%)", "Engagement index"]
    ws.set_column(0, 0, 30)
    ws.set_column(1, 1, 9)
    ws.set_column(2, 7, 13)
    ws.set_row(3, 30)
    ws.write(3, 0, heads[0], f["th"])
    ws.write(3, 1, "", f["th"])
    for j, h in enumerate(heads[2:], start=2):
        ws.write(3, j, h, f["th_num"])
    hi_set = set(df.job_family[df.vol_attrition_pct > 20])
    first, last = 4, 3 + len(df)
    for i, r in enumerate(df.itertuples(), start=first):
        ws.write(i, 0, r.job_family, f["focus_row"] if r.job_family in hi_set else f["cell"])
        ws.write_formula(i, 1, f"=C{i + 1}", f["cell"], r.headcount)
        ws.write(i, 2, r.headcount, f["int"])
        ws.write(i, 3, r.vol_attrition_pct, f["dec"])
        ws.write(i, 4, r.attrition_change_pts, f["delta"])
        ws.write_row(i, 5, [r.median_days_to_fill, r.internal_fill_pct, r.engagement_index], f["int"])
    tot = last + 1
    total = {"bold": True, "font_color": C.headline, "top": 2, "top_color": C.total}
    total_fmts = [wb.add_format(total), wb.add_format({**total, "num_format": "#,##0"})]
    ws.write(tot, 0, f"All {len(df)} job families", total_fmts[0])
    ws.write(tot, 1, "", total_fmts[0])
    ws.write_formula(tot, 2, f"=SUM(C{first + 1}:C{last + 1})", total_fmts[1])
    weights = f"$C${first + 1}:$C${last + 1}"
    for j, (col, fmt) in enumerate((("D", "0.0"), ("E", '+0.0;"−"0.0;0.0'), ("F", "0"), ("G", "0"), ("H", "0")), start=3):
        total_fmts.append(wb.add_format({**total, "num_format": fmt}))
        ws.write_formula(tot, j, f"=SUMPRODUCT({col}{first + 1}:{col}{last + 1},{weights})/SUM({weights})",
                         total_fmts[-1])                                   # weighted, not an average of rates
    ramp = mv.SEQUENTIAL["blue"]
    rng = f"D{first + 1}:D{last + 1}"
    for k, color in enumerate(ramp):                                    # 6 even 5-pt classes, last one open-ended
        lo = k * 5
        crit = {"criteria": ">=", "value": lo} if k == len(ramp) - 1 else             {"criteria": "between", "minimum": lo, "maximum": lo + 4.999}
        ws.conditional_format(rng, {"type": "cell", **crit,
                                    "format": wb.add_format({"bg_color": color, "font_color": mv.text_on(color)})})
    ws.conditional_format(f"E{first + 1}:E{last + 1}", {"type": "cell", "criteria": ">", "value": 0,
                                                        "format": wb.add_format({"font_color": C.negative_text})})
    ws.conditional_format(f"B{first + 1}:B{last + 1}", {"type": "data_bar", "bar_color": C.context, "bar_solid": True,
                                                        "bar_only": True, "min_type": "num", "min_value": 0,
                                                        "bar_no_border": True})
    wb.close()
    # Named cell styles (Home › Cell Styles › Custom), so people can restyle their own sheets the same way.
    named = {"Headline": [f["head"]], "Subtitle": [f["sub"]], "Source": [f["note"]], "Focus row": [f["focus_row"]],
             "Total": total_fmts}
    _theme_xlsx(path, {name: sorted({x._get_xf_index() for x in fmts}) for name, fmts in named.items()})
    return path


def _name_styles(styles_xml: bytes, named: dict[str, list[int]]) -> bytes:
    """xlsxwriter has no named cell styles: copy each format's xf into cellStyleXfs, add a <cellStyle> for it, and
    point the cell xfs at it, so Excel lists Headline, Subtitle, Source, Focus row and Total under Cell Styles."""
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    q = lambda tag: f"{{{ns}}}{tag}"
    root = etree.fromstring(styles_xml)
    style_xfs, cell_xfs, styles = root.find(q("cellStyleXfs")), root.find(q("cellXfs")), root.find(q("cellStyles"))
    for name, indices in named.items():
        new = copy.deepcopy(cell_xfs[indices[0]])
        new.attrib.pop("xfId", None)
        style_xfs.append(new)
        k = len(style_xfs) - 1
        for i in indices:
            cell_xfs[i].set("xfId", str(k))
        etree.SubElement(styles, q("cellStyle"), name=name, xfId=str(k))
    for el in (style_xfs, styles):
        el.set("count", str(len(el)))
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + etree.tostring(root, encoding="UTF-8")


def _rounded_off(chart_xml: bytes) -> bytes:
    root = etree.fromstring(chart_xml)
    no_rounded_corners(root)
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + etree.tostring(root, encoding="UTF-8")


def _theme_xlsx(path: Path, named: dict[str, list[int]]) -> None:
    """xlsxwriter writes the default Office theme; swap in the McKesson colors, fonts and flat format scheme, add the
    named cell styles and switch off rounded chart corners.

    xlsxwriter also writes <workbookPr defaultThemeVersion="124226"/>, which makes Excel load its built-in 2007 theme
    and ignore theme1.xml entirely, so that attribute has to go too.
    """
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            blob = src.read(item.filename)
            if item.filename == "xl/theme/theme1.xml":
                blob = themed_xml(blob)
            elif item.filename == "xl/workbook.xml":
                blob = blob.replace(b' defaultThemeVersion="124226"', b"")
            elif item.filename == "xl/styles.xml":
                blob = _name_styles(blob, named)
            elif item.filename.startswith("xl/charts/chart") and item.filename.endswith(".xml"):
                blob = _rounded_off(blob)
            dst.writestr(item, blob)
    shutil.move(tmp, path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for build in (build_pptx, build_xlsx, build_pptx_official):
        path = build()
        if path:
            print("wrote", path.relative_to(ROOT))
    print("wrote", (OUT / "McKesson-DataViz.potx").relative_to(ROOT))


if __name__ == "__main__":
    main()
