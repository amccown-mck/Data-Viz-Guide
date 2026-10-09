"""Build the Office starter files from tokens and example data.

    python office/build_office.py

Writes (all generated; never edit by hand):
    dist/office/McKesson-DataViz-Starter.pptx   16:9 deck, McKesson theme, native editable sample charts, plus a KPI
                                                card, roadmap (Gantt), initiative tracker and two-charts slide
    dist/office/McKesson-DataViz.potx           the same theme and layouts as a template, with no slides
    dist/office/McKesson-DataViz-Charts.xlsx    palette sheet + native sample charts + a heat table + KPI, roadmap and
                                                tracker sheets driven by formulas
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
from types import SimpleNamespace

import pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.chart.data import BubbleChartData, CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import (XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE,
                            XL_TICK_LABEL_POSITION, XL_TICK_MARK)
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

import mckviz as mv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"
OUT = ROOT / "dist" / "office"
FONTS = ROOT / "fonts" / "LibreFranklin"
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


def wrapped_lines(text, size, width, weight="Regular") -> int:
    """How many lines `text` wraps to in a `width`-inch box at `size` pt: greedy word wrap, measured with the bundled
    Libre Franklin, so a caption that would spill is caught at build time, not on the slide."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextToPath
    prop = FontProperties(fname=str(FONTS / f"LibreFranklin-{weight}.ttf"), size=size)
    measure = lambda t: TextToPath().get_text_width_height_descent(t, prop, ismath=False)[0] / 72   # noqa: E731
    lines, line = 1, ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and measure(trial) > width:
            lines, line = lines + 1, word
        else:
            line = trial
    return lines


def takeaways(slide, points, title="Key takeaways"):
    """Chart + takeaways: a flat card in the right third of the slide (TAKE_LEFT, TAKE_W) beside a two-thirds chart
    (SIDE_CHART_W), in the same place on every slide (CARD_TOP to CARD_BOTTOM; the chart's plot area uses PLOT_Y and
    PLOT_H to line up with it). Light fill, a blue rule along the top (the guide's flat card), the label, then two or
    three points spread down the card with hairlines between them: each a Bold navy number on one line and a caption
    of at most two lines, written from the data. Facts, not advice."""
    assert 2 <= len(points) <= 3, "two or three takeaways"
    pad, label_h, num_h, cap_h = 0.25, 0.42, 0.42, 0.46
    x, w = TAKE_LEFT + pad, TAKE_W - 2 * pad
    for num, cap in points:
        assert wrapped_lines(num, 24, w, "Bold") == 1, f"takeaway number wraps: {num!r}"
        assert wrapped_lines(cap, 14, w) <= 2, f"takeaway caption over two lines: {cap!r}"
    y0 = CARD_TOP + pad + label_h
    item = num_h + cap_h
    gap = min((CARD_BOTTOM - pad - y0 - len(points) * item) / (len(points) - 1), 0.6)
    assert gap >= 0.2, "the card is too short for its points"
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


def points_on_edges(chart) -> None:
    """Line chart: put the first and last categories on the plot's edges (Axis Position › On tick marks) instead of
    the middle of their bands, so a two-period slope uses the plot's full width."""
    va = chart._chartSpace.find(".//" + qn("c:valAx"))
    el = va.find(qn("c:crossBetween"))
    if el is None:
        el = etree.Element(qn("c:crossBetween"))
        next(e for e in (va.find(qn(t)) for t in ("c:crossesAt", "c:crosses")) if e is not None).addnext(el)
    el.set("val", "midCat")


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


# ====================================================================== data for the new slides (shared by both files)
STATUS = mv.STATUS                                        # key -> {"value", "symbol", "label"}
STATUS_ORDER = ["off_track", "at_risk", "on_track", "not_started", "done"]       # exceptions first
WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PLAN_SPAN = 24                                            # months: FY26 Q1 (Apr 2025) .. FY27 Q4 (Mar 2027)
PHASES = [("Foundations", 0, 9), ("Pilot", 9, 18), ("Scale", 18, 24)]
AS_OF, AS_OF_M = "31 Mar 2026", "2026-03"
PLAN_SRC = "Source: Workforce Innovation program office (synthetic data for illustration), as of 31 Mar 2026"
STATUS_DEF = ("Off track = a milestone missed with no recovery date; at risk = a milestone moved, with a recovery date; "
              "complete = every milestone met.")
SHORTW = {"Skills inventory rollout": "Skills inventory", "Pharmacy technician career path": "Pharmacy tech career path"}
SHORT_JF = {"Pharmacy Technician": "Pharmacy Tech", "Distribution Center Associate": "DC Associate",
            "Software Engineering": "Software Eng.", "Supply Chain Planning": "Supply Chain"}
SEMI, MEDIUM = f"{FONT} SemiBold", f"{FONT} Medium"
UP, DOWN = "▲", "▼"


def mi(s: str) -> int:
    """Month index from Apr 2025 (= 0), McKesson FY26 Q1."""
    y, m = map(int, s.split("-"))
    return (y - 2025) * 12 + m - 4


def mon(s: str, year: bool = False) -> str:
    return MON[int(s[5:]) - 1] + (f" {s[:4]}" if year else "")


def plan_data() -> SimpleNamespace:
    """Roadmap and tracker numbers, computed as in guide/ex_plans.py."""
    plan = pd.read_csv(DATA / "initiative_plan.csv").fillna("")
    ms = pd.read_csv(DATA / "initiative_milestones.csv").fillna("")
    n = len(plan)
    off = plan[plan.status == "off_track"]
    dep = off.depends_on.iloc[0]
    assert len(off) == 2 and set(off.depends_on) == {dep}            # headline: "two ... both waiting on"
    exc = plan[plan.status.isin(["off_track", "at_risk"])]
    moved = ms[(ms.workstream == dep) & (ms.state == "moved")].iloc[0]
    slip = mi(moved.forecast) - mi(moved.due)
    nxt = {}
    for w, g in ms.groupby("workstream", sort=False):
        left = g[g.state != "met"]
        nxt[w] = left.iloc[0] if len(left) else None
    # The paused workstream restarts when the integration lands, so its end moves by the same months (a forecast).
    paused = plan.what_changed.str.contains("paused")
    plan = plan.assign(offset=plan.start.map(mi), duration=[mi(e) - mi(s) + 1 for s, e in zip(plan.start, plan.end)],
                       slip=[slip if p else 0 for p in paused], short=[SHORTW.get(w, w) for w in plan.workstream])
    count = plan.status.value_counts().to_dict()
    rollup = [(k, count.get(k, 0)) for k in STATUS_ORDER if count.get(k, 0)]
    sorted_plan = plan.assign(o=plan.status.map(STATUS_ORDER.index)).sort_values(["o", "start"], kind="stable")
    return SimpleNamespace(
        plan=plan, ms=ms, n=n, off=off, exc=exc, dep=dep, moved=moved, slip=slip, next=nxt, rollup=rollup,
        sorted=sorted_plan, paused=plan.workstream[paused].iloc[0], today=mi(AS_OF_M) + 1,
        headline=(f"{WORDS[len(off)].capitalize()} of {WORDS[n]} workstreams are off track, both waiting on the "
                  f"skills inventory's Workday integration"),
        subtitle=f"Workforce Innovation roadmap by workstream, FY26–FY27, with status as of {AS_OF}",
        tr_headline=(f"{WORDS[len(exc)].capitalize()} of {WORDS[n]} workstreams need a decision, all because the "
                     f"Workday integration slipped {WORDS[slip]} months"),
        tr_subtitle=f"Status, owner, dates, next milestone and change since February, as of {AS_OF}")


def next_milestone(P, w) -> tuple[str, str, bool]:
    """(milestone, when, flagged): the first milestone not yet met, as in the guide's tracker."""
    m = P.next[w]
    if m is None:
        return "All milestones met", "", False
    if m.state == "missed":
        return m.milestone, f"Missed {mon(m.due)}; no new date", True
    if m.state == "moved":
        return m.milestone, f"{mon(m.forecast, True)} (was {mon(m.due)})", True
    return m.milestone, mon(m.due, True), False


def kpi_data() -> SimpleNamespace:
    """Succession coverage KPI card, as in guide/ex_single_number.py."""
    sc = pd.read_csv(DATA / "succession_coverage_bu.csv")
    roles, now, prior = int(sc.critical_roles.sum()), int(sc.ready_now_mar26.sum()), int(sc.ready_now_mar25.sum())
    pct, pct0, tgt = round(now / roles * 100), round(prior / roles * 100), int(sc.target_pct.iloc[0])
    d, gap = pct - pct0, tgt - pct
    return SimpleNamespace(
        df=sc, roles=roles, now=now, prior=prior, pct=pct, pct0=pct0, tgt=tgt, d=d, gap=gap,
        headline=(f"Succession coverage rose {d} points in a year but is still {gap} short of the {tgt}% target"
                  if gap > 0 else f"Succession coverage rose {d} points in a year and meets the {tgt}% target"),
        subtitle=f"Critical roles with at least one ready-now successor, Mar 2026 (% of {roles} roles)",
        sentence=f"{now} of {roles} critical roles have at least one ready-now successor",
        delta=f"{UP if d >= 0 else DOWN} {mv.signed(d)} pts vs. Mar 2025 ({pct0}%)",
        gap_text=f"{gap} pts short of the {tgt}% FY27 target" if gap > 0 else f"At or above the {tgt}% FY27 target",
        footnote="Ready-now = assessed in the FY26 talent review as able to step in within 12 months.",
        source="Source: Workday talent review and succession records (synthetic data for illustration), as of 31 Mar 2026")


def two_charts_data() -> SimpleNamespace:
    """Attrition and engagement by job family, as in guide/ex_formats.py's two-charts spread."""
    sc = pd.read_csv(DATA / "job_family_scorecard.csv").set_index("job_family")
    top = list(sc.vol_attrition_pct.nlargest(2).index)
    assert set(sc.engagement_index.nsmallest(2).index) == set(top)
    others = sc.drop(top)
    eng_others = float((others.engagement_index * others.headcount).sum() / others.headcount.sum())
    a = [float(sc.vol_attrition_pct[f]) for f in top]
    e = sorted(int(sc.engagement_index[f]) for f in top)
    return SimpleNamespace(
        df=sc.sort_values("vol_attrition_pct"), top=top,              # ascending: the largest sits at the top
        title="The two job families that lose the most people also report the lowest engagement",
        left=f"Pharmacy Techs and DC Associates lose about 1 in {round(100 / (sum(a) / 2))} people a year",
        right=f"They score {e[0]} and {e[1]} on engagement, against {eng_others:.0f} for everyone else",
        left_sub="Voluntary attrition by job family, FY26 (%)",
        right_sub="Engagement index by job family, FY26 (0–100)",
        left_src=("Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.\n"
                  "Source: Workday HCM (synthetic data for illustration), FY26; U.S. regular employees"),
        right_src=("Engagement index = mean of the survey's engagement items, rescaled to 0–100.\n"
                   "Source: Engagement survey (synthetic data for illustration), FY26; U.S. regular employees"))


def column_data() -> SimpleNamespace:
    df = pd.read_csv(DATA / "internal_fill_by_fy.csv")
    v, fy = df.internal_fill_pct.astype(int), df.fiscal_year
    now, prior, first = int(v.iloc[-1]), int(v.iloc[-2]), int(v.iloc[0])
    assert now == v.max()
    before = prior - first                                     # the change over the years before the latest
    assert now - prior > before
    falls = [i for i in range(1, len(df)) if v.iloc[i] < v.iloc[i - 1]]
    assert len(falls) == 1
    dip = falls[0]
    return SimpleNamespace(
        df=df, headline=(f"Internal candidates filled {now}% of roles in FY26, up {now - prior} points and the "
                         f"highest in {WORDS[len(df)]} years"),
        subtitle=f"Share of open roles filled by internal candidates, {fy.iloc[0]}–{fy.iloc[-1]} (%)",
        footnote="Internal fill rate = roles filled by internal candidates ÷ all roles filled.",
        points=[(f"+{now - first} points", f"Since {fy.iloc[0]}, from {first}% to {now}% of roles filled internally"),
                (f"+{now - prior} points", f"In {fy.iloc[-1]} alone, more than the {WORDS[len(df) - 2]} years before it "
                                           f"combined ({mv.signed(before, 0)})"),
                (fy.iloc[dip], f"The one down year: the rate slipped from {v.iloc[dip - 1]}% to {v.iloc[dip]}%")])


def dumbbell_data() -> SimpleNamespace:
    df = pd.read_csv(DATA / "pay_vs_market.csv").sort_values("gap_pct")      # widest gap below market at the top
    low = df.nsmallest(2, "gap_pct")
    names = {"RN, Specialty": "Specialty nurses", "Pharmacy Technician": "pharmacy technicians"}
    a, b = (names.get(r, r) for r in low.role)
    below, above = df[df.gap_pct < 0], df[df.gap_pct > 0]
    usd = df.internal_median_k - df.market_median_k             # the gap in $K
    widest = df.role[usd.idxmin()]
    usd_k = lambda k: mv.fmt_num(k * 1000, "K", decimals=0, prefix="$")       # noqa: E731
    assert widest not in set(low.role)                         # the dollar view names a different role
    return SimpleNamespace(
        df=df, focus=set(low.role),
        headline=(f"{a[0].upper() + a[1:]} and {b} are paid about {abs(low.gap_pct.mean()):.0f}% below market, "
                  f"the widest gaps of {len(df)} benchmarked roles"),
        subtitle="Median base pay, McKesson vs. market, by role, 2026 ($K)",
        footnote="External market = posted-pay median for comparable roles and metros.",
        points=[(f"{len(below)} of {len(df)}", f"Roles paid below market; the other {WORDS[len(above)]} are "
                                               f"{above.gap_pct.min():.1f}–{above.gap_pct.max():.1f}% above it"),
                (usd_k(usd.min()), f"{widest}s, the widest gap in dollars "
                                   f"({mv.signed(df.gap_pct[usd.idxmin()], 1, '%')}); {a.lower()}: {usd_k(usd[low.index[0]])}")])


def slope_data() -> SimpleNamespace:
    df = pd.read_csv(DATA / "internal_fill_by_bu.csv")
    w = df[df.fiscal_year.isin(["FY25", "FY26"])].pivot(index="business_unit", columns="fiscal_year",
                                                       values="internal_fill_pct")
    w["d"] = w.FY26 - w.FY25
    w = w.sort_values("FY26", ascending=False)
    top, second = w.d.nlargest(2)
    focus = w.d.idxmax()
    ratio = top / second
    times = "twice" if abs(ratio - 2) < 0.25 else f"{ratio:.0f}×"
    assert (w.d > 0).all()
    rank25, rank26 = w.FY25.rank(ascending=False), w.FY26.rank(ascending=False)
    assert rank26[focus] == 1 and rank25[focus] > 1
    ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}
    runner = w.FY26.drop(focus).idxmax()
    spread = lambda s: int(s.max() - s.min())                   # noqa: E731
    assert spread(w.FY26) > spread(w.FY25)
    return SimpleNamespace(
        df=w, focus=focus,
        headline=f"{focus}'s internal fill rate rose {top:.0f} points in FY26, {times} the next-largest gain",
        subtitle="Internal fill rate by business unit, FY25 and FY26 (% of roles filled internally)",
        footnote="Internal fill rate = roles filled by internal candidates ÷ all roles filled.",
        points=[(f"{len(w)} of {len(w)}", f"Units raised their internal fill rate, by {w.d.min():.0f} to "
                                             f"{w.d.max():.0f} points"),
                (f"+{w.FY26[focus] - w.FY26[runner]:.0f} points", f"{focus}'s lead over the next unit; it ranked "
                                                                 f"{ordinal[int(rank25[focus])]} in FY25"),
                (f"{spread(w.FY26)} points", f"Gap between the highest and lowest unit, up from {spread(w.FY25)} in FY25")])


def bubble_data() -> SimpleNamespace:
    df = pd.read_csv(DATA / "automation_exposure.csv")
    top = df.nlargest(2, "genai_exposure_pct")
    short = {"Claims & Billing Specialist": "Claims & Billing", "Customer Care": "Customer Care"}
    a, b = (short.get(r, r) for r in top.role)
    med = df.median_pay_k.median()
    assert (top.median_pay_k < med).all()
    big = df.loc[df.headcount.idxmax()]
    assert big.genai_exposure_pct == df.genai_exposure_pct.min()
    pay = sorted(int(p) for p in top.median_pay_k)
    return SimpleNamespace(
        df=df, focus=set(top.role), short=short,
        headline=(f"The two roles most exposed to Gen AI, {a} and {b}, employ {int(top.headcount.sum()):,} people"),
        subtitle="Share of tasks exposed to Gen AI vs. median pay, by role, 2026 (bubble area = headcount)",
        footnote="Exposure = share of task hours matched to gen-AI-capable activities in an external task taxonomy.",
        points=[(f"${pay[0]}–{pay[1]}K", f"Median pay in the two most exposed roles, vs. ${med:.0f}K across all "
                                            f"{len(df)}"),
                (f"{big.genai_exposure_pct}%", f"Of tasks exposed in the largest role, {big.role}")])


# ====================================================================== drawn-shape helpers
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


def status_dot(target, cx, cy, key, d=0.2):
    """Status: a small flat circle in the status color with its symbol inside (white or navy ink)."""
    st = STATUS[key]
    s = shape(target, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, st["value"], name=f"Status dot: {st['label']}")
    shape_text(s, st["symbol"], round(d * 72 * 0.62), mv.text_on(st["value"]), bold=True)
    return s


def status_label(target, x, cy, key, size=11, d=0.2, bold=None, width=1.1):
    """Dot (color + symbol) and the word; off track and at risk in SemiBold navy."""
    status_dot(target, x + d / 2, cy, key, d)
    b = key in ("off_track", "at_risk") if bold is None else bold
    text_box(target, x + d + 0.07, cy - 0.13, width, 0.26, STATUS[key]["label"], size, C.headline if b else C.text,
             font=SEMI if b else FONT, anchor=MSO_ANCHOR.MIDDLE, wrap=False, name=f"Status word: {STATUS[key]['label']}")


def milestone(target, cx, cy, kind, s=0.17, name=""):
    """Milestone marks (as in the guide): met = navy filled diamond; due = hollow navy; was = hollow grey (the original
    date of a moved milestone); missed = an off-track cross."""
    label = {"met": "met", "upcoming": "due", "moved": "due (moved)", "was": "original date", "missed": "missed"}[kind]
    nm = f"Milestone {label}" + (f": {name}" if name else "")
    if kind == "missed":
        k = s * 1.3
        return shape(target, MSO_SHAPE.MATH_MULTIPLY, cx - k / 2, cy - k / 2, k, k, STATUS["off_track"]["value"],
                     line="#FFFFFF", line_w=0.5, name=nm)
    if kind == "met":
        return shape(target, MSO_SHAPE.DIAMOND, cx - s / 2, cy - s / 2, s, s, C.total, line="#FFFFFF", name=nm)
    edge = C.text_muted if kind == "was" else C.total
    return shape(target, MSO_SHAPE.DIAMOND, cx - s / 2, cy - s / 2, s, s, "#FFFFFF", line=edge,
                 line_w=1.0 if kind == "was" else 1.25, name=nm)


def frame_in(frame):
    return tuple(Emu(v).inches for v in (frame.left, frame.top, frame.width, frame.height))


# ====================================================================== chart helpers for the new charts
C15 = "http://schemas.microsoft.com/office/drawing/2012/chart"


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


def point_line(point, color=None, width_pt=None):
    """The line segment that leads into an XY or line point (Office draws segment k with point k's format)."""
    if color is None:
        point.format.line.fill.background()
    else:
        point.format.line.color.rgb = rgb(color)
        point.format.line.width = Pt(width_pt)


def point_marker(point, color, size, style=XL_MARKER_STYLE.CIRCLE, edge="#FFFFFF"):
    m = point.marker
    m.style = style
    m.size = size
    m.format.fill.solid()
    m.format.fill.fore_color.rgb = rgb(color)
    if edge:
        m.format.line.color.rgb = rgb(edge)
        m.format.line.width = Pt(0.75)
    else:
        m.format.line.fill.background()


def axis_ticks(axis, size=11, color=C.text_muted, fmt=None):
    axis.tick_labels.font.size = Pt(size)
    axis.tick_labels.font.color.rgb = rgb(color)
    if fmt:
        axis.tick_labels.number_format = fmt
        axis.tick_labels.number_format_is_linked = False


def gridlines(axis, color=C.grid):
    axis.has_major_gridlines = True
    axis.major_gridlines.format.line.color.rgb = rgb(color)
    axis.major_gridlines.format.line.width = Pt(0.75)


def row_series_chart(slide, rows, left, top, width, height, x_min, *, layout):
    """Dot plot / dumbbell on a category axis: an XY chart with one series per row (y = row position, top row first).
    Point 0 sits at the axis minimum and carries the row name (label: Series Name, Left); later points are the dots,
    joined by the series line. Returns the chart frame and chart."""
    data = XyChartData()
    n = len(rows)
    for i, (name, xs) in enumerate(rows):
        s = data.add_series(name)
        s.add_data_point(x_min, n - i)
        for x in xs:
            s.add_data_point(x, n - i)
    frame, chart = add_chart(slide, XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, data, top=top, height=height, left=left,
                             width=width)
    plot_layout(chart, *layout)
    return frame, chart


def xy_axes(chart, n, x_min, x_max, major, fmt, headroom=0.5):
    va, xa = chart.value_axis, chart.category_axis          # XY: value_axis = Y, category_axis = X (a value axis too)
    va.minimum_scale, va.maximum_scale = 0.5, n + headroom
    va.visible = False
    va.has_major_gridlines = False
    xa.minimum_scale, xa.maximum_scale, xa.major_unit = x_min, x_max, major
    gridlines(xa)
    baseline(xa, visible=False)
    axis_ticks(xa, fmt=fmt)


# ====================================================================== new slides
def slide_kpi(prs):
    K = kpi_data()
    slide = chart_slide(
        prs, K.headline, K.subtitle, K.footnote,
        f"KPI card. Everything here is a text box or a flat rectangle, so edit the text directly. The number is Libre "
        f"Franklin Bold 54 pt navy {C.headline}; the comparison line is green {C.positive_text} with ▲ when it is good "
        f"news (orange {C.negative_text} with ▼ when it is worse); the gap to target is orange text, said in words.\n"
        f"Progress bar (group 'Progress bar'): the track is {BAR_W:.2f} in wide, so the blue fill's width = "
        f"{BAR_W:.2f} in × value (now {K.pct}% = {BAR_W * K.pct / 100:.2f} in), and the target tick's left edge = "
        f"{LEFT:.2f} in + {BAR_W:.2f} in × target − 0.02 in (Shape Format › Size and Position). Numbers: {K.now} of "
        f"{K.roles} ready-now = {K.pct}%; Mar 2025 {K.prior} = {K.pct0}%; target {K.tgt}%.", source=K.source)
    top = 2.05
    text_box(slide, LEFT, top, 2.6, 1.15, f"{K.pct}%", 54, C.headline, bold=True, anchor=MSO_ANCHOR.MIDDLE,
             name="KPI number")
    x = LEFT + 2.75
    text_box(slide, x, top + 0.02, 6.4, 0.32, K.sentence, 16, C.text, name="KPI sentence")
    text_box(slide, x, top + 0.47, 6.4, 0.28, K.delta, 14, C.positive_text if K.d >= 0 else C.negative_text,
             font=SEMI, name="KPI comparison")
    if K.gap > 0:
        text_box(slide, x, top + 0.82, 6.4, 0.28, K.gap_text, 14, C.negative_text, font=SEMI, name="KPI gap to target")
    grp = slide.shapes.add_group_shape()
    grp.name = "Progress bar"
    y = 4.05
    shape(grp, MSO_SHAPE.RECTANGLE, LEFT, y, BAR_W, 0.16, C.context_light, name="Track (0-100%)")
    shape(grp, MSO_SHAPE.RECTANGLE, LEFT, y, BAR_W * K.pct / 100, 0.16, C.focus, name=f"Fill ({K.pct}%)")
    tx = LEFT + BAR_W * K.tgt / 100
    shape(grp, MSO_SHAPE.RECTANGLE, tx - 0.02, y - 0.1, 0.04, 0.36, C.total, name=f"Target tick ({K.tgt}%)")
    text_box(grp, tx - 1.0, y - 0.38, 2.0, 0.24, f"Target {K.tgt}%", 11, C.annotation, align=PP_ALIGN.CENTER,
             name="Target label")
    text_box(grp, LEFT, y + 0.24, 1.0, 0.22, "0%", 11, C.text_muted, name="Scale 0%")
    text_box(grp, LEFT + BAR_W - 1.0, y + 0.24, 1.0, 0.22, "100%", 11, C.text_muted, align=PP_ALIGN.RIGHT,
             name="Scale 100%")
    return slide


BAR_W = 8.6                                                    # KPI progress-bar track width (in)


def slide_roadmap(prs):
    P = plan_data()
    plan, n = P.plan, P.n
    fl, ft, fw, fh = LEFT, 2.42, W - LEFT - RIGHT, 3.45
    px, py, pw, ph = 2.55 / fw, 0.0, 8.6 / fw, 1.0
    month = fw * pw / PLAN_SPAN
    X = lambda m: fl + fw * px + month * m                                                # noqa: E731
    plot_top, row_h = ft + fh * py, fh * ph / n
    Y = lambda i: plot_top + row_h * (i + 0.5)                                            # noqa: E731
    slide = chart_slide(
        prs, P.headline, P.subtitle,
        STATUS_DEF + "\n" + f"Light grey = forecast: the paused {P.paused} restarts when the integration goes live, {P.slip} months late.",
        "Roadmap (Gantt) built as a native Stacked Bar. Right-click › Edit Data: 'Start' = months after 1 Apr 2025 "
        "(FY26 Q1 = 0), 'Duration' = months including the last one, 'Slip' = forecast months beyond the plan (0 if on "
        "plan). The Start series has no fill, so each bar floats at its start. Bar colors: click a bar twice › Fill: "
        f"grey {C.context} on plan, blue {C.focus} off track, light {C.context_light} not started; the slip segment is "
        f"light grey with a dashed outline. The value axis (0-24 months) is deleted but its gridlines mark the quarters.\n"
        f"Move the Today line: select the group 'Today line' and set Shape Format › Size and Position › Horizontal "
        f"position = {X(0):.2f} in + months × {month:.3f} in, minus half the group's width (one month = {month:.3f} in; "
        f"today, the end of Mar 2026, is month {P.today}). Or select it and nudge with the arrow keys.\n"
        "Add a row: in Edit Data, insert a row inside the table so the chart range grows, then type the name, Start, "
        f"Duration and Slip 0. Rows get shorter (the plot height ÷ the number of rows), so drag each row's group "
        "('Row 3: SWP model refresh' holds its milestones and status) back onto its bar; for the new row, copy a "
        "group and change the dot color, symbol and word.\nMilestones are shapes: ◆ navy filled = met, ◇ hollow navy "
        "= due, ✕ = missed, grey ◇ = a moved milestone's original date with an arrow to the new one. A milestone in "
        f"month m sits at {X(0):.2f} in + (m + 0.5) × {month:.3f} in.", source=PLAN_SRC)
    # Header: phase band, fiscal years, quarters (drawn; they line up with the pinned plot area).
    hdr = slide.shapes.add_group_shape()
    hdr.name = "Timeline header"
    for i, (name, a, b) in enumerate(PHASES):
        s = shape(hdr, MSO_SHAPE.RECTANGLE, X(a) + (0.01 if a else 0), 1.8, (b - a) * month - (0.01 if a else 0), 0.2,
                  C.context_light if i % 2 == 0 else C.grid, name=f"Phase: {name}")
        shape_text(s, name, 10, C.headline, align=PP_ALIGN.LEFT)
        s.text_frame.margin_left = Inches(0.06)
    for k, name in enumerate(("FY26", "FY27")):
        text_box(hdr, X(k * 12), 2.03, 12 * month, 0.18, name, 11, C.headline, font=SEMI, align=PP_ALIGN.CENTER)
    for q in range(PLAN_SPAN // 3):
        text_box(hdr, X(q * 3), 2.21, 3 * month, 0.18, f"Q{q % 4 + 1}", 11, C.text_muted, align=PP_ALIGN.CENTER)
    text_box(hdr, LEFT, 2.21, 2.0, 0.18, "Workstream", 10, C.text_muted)
    text_box(hdr, X(PLAN_SPAN) + 0.18, 2.21, 1.0, 0.18, "Status", 10, C.text_muted)
    line_shape(hdr, LEFT, 2.41, W - RIGHT, 2.41, C.axis, dash=False, name="Header rule")
    # The chart: invisible start + duration + slip.
    data = CategoryChartData()
    data.categories = list(plan.short)
    data.add_series("Start (months after 1 Apr 2025)", list(plan.offset))
    data.add_series("Duration (months)", list(plan.duration))
    data.add_series("Slip (months)", list(plan.slip))
    frame, chart = add_chart(slide, XL_CHART_TYPE.BAR_STACKED, data, top=ft, height=fh)
    frame.name = "Roadmap chart"
    plot_layout(chart, px, py, pw, ph)
    plot = chart.plots[0]
    plot.gap_width = 80
    plot.overlap = 100
    s_start, s_dur, s_slip = plot.series
    no_fill(s_start)
    fill(s_dur, C.context)
    s_dur.format.line.fill.background()
    no_fill(s_slip)
    for i, r in plan.reset_index(drop=True).iterrows():
        if r.status == "off_track":
            fill(s_dur.points[i], C.focus)
        elif r.status == "not_started":
            fill(s_dur.points[i], C.context_light)
        if r.slip:
            pt = s_slip.points[i]
            fill(pt, C.context_light)
            pt.format.line.color.rgb = rgb(C.context)
            pt.format.line.width = Pt(0.75)
            pt.format.line.dash_style = 4
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = 0, PLAN_SPAN, 3
    gridlines(va)
    va.visible = False
    ca = chart.category_axis
    ca.reverse_order = True                                   # first workstream on top
    baseline(ca, visible=False)
    axis_ticks(ca, 12, C.text)
    bar_h = row_h / (1 + 0.8)
    # Per row: milestones, slip arrow and status, grouped so a row's marks move together.
    for i, r in plan.reset_index(drop=True).iterrows():
        g = slide.shapes.add_group_shape()
        g.name = f"Row {i + 1}: {r.workstream}"
        y = Y(i)
        for _, m in P.ms[P.ms.workstream == r.workstream].iterrows():
            if m.state == "moved":
                xa, xb = X(mi(m.due) + 0.5), X(mi(m.forecast) + 0.5)
                milestone(g, xa, y, "was", name=m.milestone)
                line_shape(g, xa + 0.1, y, xb - 0.11, y, C.annotation, width_pt=1.0, dash=False, arrow=True,
                           name="Moved: arrow")
                milestone(g, xb, y, "moved", name=m.milestone)
                text_box(g, (xa + xb) / 2 - 0.9, y - bar_h / 2 - 0.2, 1.8, 0.17, f"Moved {mon(m.due)} to "
                         f"{mon(m.forecast)}", 9, C.annotation, font=SEMI, align=PP_ALIGN.CENTER, name="Moved: label")
            else:
                milestone(g, X(mi(m.due) + 0.5), y, m.state, name=m.milestone)
        if r.slip:
            end = r.offset + r.duration
            line_shape(g, X(end) + 0.04, y, X(end + r.slip) - 0.06, y, C.annotation, width_pt=1.0, dash=False,
                       arrow=True, name="Slip: arrow")
            text_box(g, X(end + r.slip) + 0.06, y - 0.12, 1.2, 0.24, f"+{r.slip} months", 10, C.annotation, font=SEMI,
                     anchor=MSO_ANCHOR.MIDDLE, wrap=False, name="Slip: label")
        status_label(g, X(PLAN_SPAN) + 0.18, y, r.status)
    # Today line.
    bottom = ft + fh
    g = slide.shapes.add_group_shape()
    g.name = "Today line"
    line_shape(g, X(P.today), 2.41, X(P.today), bottom + 0.04, C.total, width_pt=1.0, name="Today")
    text_box(g, X(P.today) - 1.0, bottom + 0.06, 2.0, 0.2, f"Today, {AS_OF}", 10, C.annotation, font=SEMI,
             align=PP_ALIGN.CENTER, name="Today label")
    # Milestone key, bottom left.
    g = slide.shapes.add_group_shape()
    g.name = "Milestone key"
    kx, ky = LEFT + 0.09, bottom + 0.16
    for kind, lab in (("met", "Met"), ("upcoming", "Due"), ("missed", "Missed"), ("was", "Original date")):
        milestone(g, kx, ky, kind, s=0.15)
        text_box(g, kx + 0.14, ky - 0.11, 1.2, 0.22, lab, 10, C.text, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        kx += 0.32 + len(lab) * 0.075
    shape(g, MSO_SHAPE.RECTANGLE, kx - 0.07, ky - 0.06, 0.3, 0.12, C.context_light, line=C.context, dash=True,
          name="Key: slip")
    text_box(g, kx + 0.3, ky - 0.11, 1.4, 0.22, "Forecast slip", 10, C.text, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
    return slide


def _cell_borders(cell, bottom_color, bottom_w=9525):
    """Flat cell: no fill, no side or top border, a hairline bottom border."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for child in list(tcPr):
        tcPr.remove(child)
    for tag in ("lnL", "lnR", "lnT"):
        ln = etree.SubElement(tcPr, qn(f"a:{tag}"), w="0")
        etree.SubElement(ln, qn("a:noFill"))
    ln = etree.SubElement(tcPr, qn("a:lnB"), w=str(bottom_w), cap="flat", cmpd="sng", algn="ctr")
    etree.SubElement(etree.SubElement(ln, qn("a:solidFill")), qn("a:srgbClr"), val=bottom_color.lstrip("#").upper())
    etree.SubElement(ln, qn("a:prstDash"), val="solid")
    etree.SubElement(tcPr, qn("a:noFill"))


def _cell_text(cell, lines, anchor=MSO_ANCHOR.MIDDLE, margin_left=0.05):
    """lines -> [(text, size, color, font)], one paragraph each."""
    cell.margin_left, cell.margin_right = Inches(margin_left), Inches(0.08)
    cell.margin_top = cell.margin_bottom = Inches(0.03)
    cell.vertical_anchor = anchor
    tf = cell.text_frame
    tf.word_wrap = True
    for i, (text, size, color, font) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run()
        r.text = text
        r.font.size, r.font.name = Pt(size), font
        r.font.color.rgb = rgb(color)


TRACKER_COLS = [("Status", 1.35), ("Workstream, owner", 2.85), ("Plan dates", 1.8), ("Next milestone", 2.9),
                ("What changed", None)]


def slide_tracker(prs):
    P = plan_data()
    slide = chart_slide(
        prs, P.tr_headline, P.tr_subtitle, STATUS_DEF,
        "Initiative tracker: a native table (Insert › Table) with the 'No Style, No Grid' style, no fills, a 1 pt rule "
        f"under the header ({C.axis}) and hairlines between rows ({C.grid}). Rows: off track, then at risk, then the "
        "rest; exception names in SemiBold navy. The status dots are shapes in the group 'Status dots', one per row, "
        "on top of the table: to change a status, edit the word in the cell and the dot's fill and symbol "
        "(on track ✓ " + STATUS["on_track"]["value"] + ", at risk ! " + STATUS["at_risk"]["value"] + ", off track ✕ "
        + STATUS["off_track"]["value"] + ", not started – " + STATUS["not_started"]["value"] + ", complete ✓ "
        + STATUS["done"]["value"] + "). Rows are 0.54 in tall and hold two lines; keep text to two lines so the dots "
        "stay aligned, or move the group after resizing. Update the roll-up counts above the table by hand. Never "
        "color a whole row by status.", source=PLAN_SRC)
    # Roll-up: a count per status, exceptions first.
    g = slide.shapes.add_group_shape()
    g.name = "Roll-up"
    y = 1.9
    text_box(g, LEFT, y - 0.13, 1.5, 0.26, f"{P.n} workstreams", 12, C.headline, font=SEMI, anchor=MSO_ANCHOR.MIDDLE,
             wrap=False)
    x = LEFT + 1.55
    for k, cnt in P.rollup:
        status_dot(g, x + 0.1, y, k)
        text_box(g, x + 0.27, y - 0.13, 1.2, 0.26, f"{cnt} {STATUS[k]['label'].lower()}", 12, C.text,
                 anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        x += 0.5 + len(f"{cnt} {STATUS[k]['label']}") * 0.085
    # Table.
    d = P.sorted.reset_index(drop=True)
    cw = [w or (W - LEFT - RIGHT - sum(c[1] for c in TRACKER_COLS[:-1])) for _, w in TRACKER_COLS]
    top, head_h, row_h = 2.2, 0.32, 0.54
    gf = slide.shapes.add_table(len(d) + 1, len(cw), Inches(LEFT), Inches(top), Inches(sum(cw)),
                                Inches(head_h + row_h * len(d)))
    gf.name = "Tracker table"
    tbl = gf.table
    tblPr = tbl._tbl.tblPr
    tblPr.set("firstRow", "1")
    tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"                   # No Style, No Grid
    for j, w in enumerate(cw):
        tbl.columns[j].width = Inches(w)
    tbl.rows[0].height = Inches(head_h)
    for j, (head, _) in enumerate(TRACKER_COLS):
        c = tbl.cell(0, j)
        _cell_text(c, [(head, 11, C.headline, SEMI)], anchor=MSO_ANCHOR.BOTTOM)
        _cell_borders(c, C.axis, 12700)
    dots = slide.shapes.add_group_shape()
    dots.name = "Status dots"
    for i, r in d.iterrows():
        tbl.rows[i + 1].height = Inches(row_h)
        exc = r.status in ("off_track", "at_risk")
        ms_name, when, flagged = next_milestone(P, r.workstream)
        cells = [
            [(STATUS[r.status]["label"], 11, C.headline if exc else C.text, SEMI if exc else FONT)],
            [(r.workstream, 11, C.headline if exc else C.text, SEMI if exc else FONT), (r.owner, 10, C.text_muted, FONT)],
            [(f"{mon(r.start, True)} – {mon(r.end, True)}", 11, C.text, FONT)],
            [(ms_name, 11, C.text, FONT)] + ([(when, 10, C.headline if flagged else C.text_muted, SEMI if flagged
                                               else FONT)] if when else []),
            [(r.what_changed, 11, C.text, FONT)],
        ]
        for j, lines in enumerate(cells):
            c = tbl.cell(i + 1, j)
            _cell_text(c, lines, margin_left=0.33 if j == 0 else 0.05)
            _cell_borders(c, C.grid)
        status_dot(dots, LEFT + 0.05 + 0.1, top + head_h + row_h * (i + 0.5), r.status)
    return slide


def slide_two_charts(prs):
    T = two_charts_data()
    slide = chart_slide(
        prs, T.title, None, None,
        "Two charts on one slide: the slide title (Bold, McKesson Blue) is the one message both charts support; each "
        f"chart has its own SemiBold 18 pt navy headline ({C.headline}), a 14 pt subtitle and its own footnote and source, "
        "so either card can be copied to another slide. Same rows, same order and the same highlight in both charts, "
        "read left to right. Left: a bar chart (Edit Data). Right: a dot plot built as an XY scatter, one series per "
        "row (the series name is the row label): point 1 sits at the axis minimum (60) and carries the name, point 2 is "
        "the dot (X = engagement, Y = row number, 1 at the bottom); the grey line between them is the stem. Two charts "
        "is the limit; a third means a second slide.", source=None)
    df, n = T.df, len(T.df)
    gut = GUTTER
    colw = (W - LEFT - RIGHT - gut) / 2
    lay = (0.31, 0.02, 0.6, 0.96)
    names = [SHORT_JF.get(f, f) for f in df.index]
    for k, (head, sub, src) in enumerate(((T.left, T.left_sub, T.left_src), (T.right, T.right_sub, T.right_src))):
        x0 = LEFT + k * (colw + gut)
        text_box(slide, x0, 1.45, colw, 0.6, head, 18, C.headline, font=SEMI, name=f"Chart {k + 1} headline")
        text_box(slide, x0, 2.1, colw, 0.3, sub, 14, C.text, name=f"Chart {k + 1} subtitle")
        text_box(slide, x0, FOOT_TOP, colw, 0.5, src, 9, C.text_muted, light=True, anchor=MSO_ANCHOR.BOTTOM,
                 name=f"Chart {k + 1} source")
    # Left: bar.
    data = CategoryChartData()
    data.categories = names
    data.add_series("Voluntary attrition (%)", list(df.vol_attrition_pct))
    frame, chart = add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, data, top=2.5, height=3.8, left=LEFT, width=colw)
    plot_layout(chart, *lay)
    plot = chart.plots[0]
    plot.gap_width = BAND_GAP
    plot.vary_by_categories = False
    s = plot.series[0]
    fill(s, C.context)
    for i, (f, v) in enumerate(df.vol_attrition_pct.items()):
        hi = f in T.top
        if hi:
            fill(s.points[i], C.focus)
        point_label(s.points[i], f"{v:.1f}%", C.headline if hi else C.text, bold=hi, position=XL_LABEL_POSITION.OUTSIDE_END)
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = 0, 34
    va.visible = False
    va.has_major_gridlines = False
    baseline(chart.category_axis)
    axis_ticks(chart.category_axis, 11, C.text)
    # Right: dot plot (XY), same rows in the same order (the bar chart's first category is at the bottom = y 1).
    x_min, x_max = 60, 82
    rows = [(names[i], [float(df.engagement_index.iloc[i])]) for i in range(n - 1, -1, -1)]     # top row first
    frame, chart = row_series_chart(slide, rows, LEFT + colw + gut, 2.5, colw, 3.8, x_min, layout=lay)
    xy_axes(chart, n, x_min, x_max, 10, "0")
    focus_names = {SHORT_JF.get(f, f) for f in T.top}
    for ser, (name, xs) in zip(chart.plots[0].series, rows):
        hi = name in focus_names
        ser.smooth = False
        ser.marker.style = XL_MARKER_STYLE.NONE
        ser.format.line.color.rgb = rgb(C.grid)
        ser.format.line.width = Pt(1.0)
        dlbl(ser.points[0], ser=True, pos=XL_LABEL_POSITION.LEFT, size=11, color=C.headline if hi else C.text,
             bold=False, box=(lay[0] * 0.95, 0.24 / 3.8), align="r")
        point_marker(ser.points[1], C.focus if hi else C.context, 9)
        dlbl(ser.points[1], cat=True, pos=XL_LABEL_POSITION.RIGHT, num_fmt="0", color=C.headline if hi else C.text,
             bold=hi)
    return slide


def slide_column(prs):
    D = column_data()
    df = D.df
    slide = chart_slide(
        prs, D.headline, D.subtitle, D.footnote,
        "Column highlight: one blue column (the one the headline names), the rest grey; labels on top, value axis and "
        "gridlines deleted, columns from zero. Edit Data to change the numbers; to move the highlight, click a column "
        f"twice › Fill › {C.focus}, and set the others to {C.context}.")
    data = CategoryChartData()
    data.categories = list(df.fiscal_year)
    data.add_series("Internal fill rate (%)", list(df.internal_fill_pct))
    frame, chart = add_chart(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, data, width=SIDE_CHART_W)
    plot_layout(chart, 0.02, PLOT_Y, 0.96, PLOT_H)
    plot = chart.plots[0]
    plot.gap_width = BAND_GAP
    plot.vary_by_categories = False
    s = plot.series[0]
    fill(s, C.context)
    last = len(df) - 1
    for i, v in enumerate(df.internal_fill_pct):
        hi = i == last
        if hi:
            fill(s.points[i], C.focus)
        point_label(s.points[i], f"{v:.0f}%", C.headline if hi else C.text, bold=hi,
                    position=XL_LABEL_POSITION.OUTSIDE_END)
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = 0, int(df.internal_fill_pct.max() * 1.12) + 1     # room for the top label
    va.visible = False
    va.has_major_gridlines = False
    baseline(chart.category_axis)
    axis_ticks(chart.category_axis, 12, C.text)
    takeaways(slide, D.points)
    return slide


def slide_dumbbell(prs):
    D = dumbbell_data()
    df, n = D.df, len(D.df)
    x_min, x_max = 30, 160
    slide = chart_slide(
        prs, D.headline, D.subtitle, D.footnote,
        "Dumbbell built as an XY scatter with one series per role (the series name is the row label). Each series has "
        f"three points: (1) X = the axis minimum {x_min}, the label anchor, no marker, no line; (2) X = market, grey dot; "
        "(3) X = McKesson, blue dot (orange when below market is the story), joined to (2) by a light 3 pt line. Y = row "
        f"number, {n} at the top. Edit Data: change the market and McKesson X values; the gap labels on the right are "
        "typed text (Format Data Label › Text), so update them too. Key: the two dots above the top row are shapes.")
    rows = [(r.role, [float(r.market_median_k), float(r.internal_median_k)]) for r in df.itertuples()]
    lay = (0.23, PLOT_Y, 0.6, PLOT_H)                                      # names on one line at the left
    frame, chart = row_series_chart(slide, rows, LEFT, CHART_TOP, SIDE_CHART_W, CHART_H, x_min, layout=lay)
    xy_axes(chart, n, x_min, x_max, 25, '"$"#,##0"K"', headroom=1.0)       # a band above row 1 for the key
    for ser, r in zip(chart.plots[0].series, df.itertuples()):
        hi = r.role in D.focus
        ser.smooth = False
        ser.marker.style = XL_MARKER_STYLE.NONE
        ser.format.line.color.rgb = rgb(C.context_light)
        ser.format.line.width = Pt(3)
        point_line(ser.points[1], None)                       # no segment from the label anchor to the first dot
        dlbl(ser.points[0], ser=True, pos=XL_LABEL_POSITION.LEFT, size=11, color=C.headline if hi else C.text,
             box=(lay[0] * 0.95, 0.24 / CHART_H), align="r")
        point_marker(ser.points[1], C.context, 7, edge=None)
        point_marker(ser.points[2], C.negative if hi else C.focus, 9, edge=None)
        right = 1 if r.market_median_k >= r.internal_median_k else 2
        dlbl(ser.points[right], text=mv.signed(r.gap_pct, 1, "%"), pos=XL_LABEL_POSITION.RIGHT,
             color=C.negative_text if hi else C.text, bold=hi)
    fl, ft, fw, fh = frame_in(frame)
    ky = ft + fh * lay[1] + 0.12
    g = slide.shapes.add_group_shape()
    g.name = "Key"
    kx = fl + fw * lay[0]
    for color, lab, d in ((C.context, "Market", 0.1), (C.focus, "McKesson", 0.125)):
        shape(g, MSO_SHAPE.OVAL, kx, ky - d / 2, d, d, color, name=f"Key: {lab}")
        text_box(g, kx + 0.18, ky - 0.12, 1.2, 0.24, lab, 11, C.text, anchor=MSO_ANCHOR.MIDDLE, wrap=False)
        kx += 1.15
    takeaways(slide, D.points)
    return slide


def slide_slope(prs):
    D = slope_data()
    w = D.df
    lo, hi = int(w[["FY25", "FY26"]].min().min()) - 3, int(w[["FY25", "FY26"]].max().max()) + 2
    slide = chart_slide(
        prs, D.headline, D.subtitle, D.footnote,
        "Slope chart: a native Line with Markers chart with two categories (FY25, FY26) and one series per business "
        "unit. The focus line is blue 2.25 pt, the rest grey 1.25 pt; labels sit on the end points (left: value; right: "
        "series name + value), so Edit Data updates them. Labels that would touch are nudged apart (drag a label to "
        "move it). One fixed scale, value axis deleted.")
    data = CategoryChartData()
    data.categories = ["FY25", "FY26"]
    order = [b for b in w.index if b != D.focus] + [D.focus]               # focus series last: drawn on top
    for b in order:
        data.add_series(b, [float(w.FY25[b]), float(w.FY26[b])])
    frame, chart = add_chart(slide, XL_CHART_TYPE.LINE_MARKERS, data, width=SIDE_CHART_W)
    top = (CARD_TOP + 0.25 - CHART_TOP) / CHART_H                         # headers level with the card's label
    lay = (0.07, top, 0.5, PLOT_Y + PLOT_H - top)                         # room on the right for one-line names
    plot_layout(chart, *lay)
    fl, ft, fw, fh = frame_in(frame)
    ypos = lambda v: ft + fh * (lay[1] + lay[3] * (1 - (v - lo) / (hi - lo)))           # noqa: E731

    def spread(vals, gap=0.2):
        """Label centres (in) at least `gap` apart, each colliding cluster centred on its points -> nudges (fraction
        of the frame height); labels that don't collide stay put."""
        items = sorted((ypos(v), k) for k, v in vals.items())
        clusters = []
        for y, k in items:
            if clusters and y - (clusters[-1][-1][0]) < gap:
                clusters[-1].append((y, k))
            else:
                clusters.append([(y, k)])
        out = {}
        for cl in clusters:
            mid = sum(y for y, _ in cl) / len(cl)
            for j, (y, k) in enumerate(cl):
                out[k] = (mid + (j - (len(cl) - 1) / 2) * gap - y) / fh
        return out

    nudge0, nudge1 = spread({b: w.FY25[b] for b in order}), spread({b: w.FY26[b] for b in order})
    for ser, b in zip(chart.plots[0].series, order):
        f = b == D.focus
        color = C.focus if f else C.context
        ser.smooth = False
        ser.format.line.color.rgb = rgb(color)
        ser.format.line.width = Pt(2.25 if f else 1.25)
        for k in (0, 1):
            point_marker(ser.points[k], color, 7, edge=None)
        txt = C.headline if f else C.text
        dlbl(ser.points[0], val=True, pos=XL_LABEL_POSITION.LEFT, num_fmt='0"%"', color=txt, bold=f,
             dy=nudge0[b] if abs(nudge0[b]) > 0.002 else 0.0)
        dlbl(ser.points[1], val=True, ser=True, pos=XL_LABEL_POSITION.RIGHT, num_fmt='0"%"', color=txt, bold=f,
             dy=nudge1[b] if abs(nudge1[b]) > 0.002 else 0.0, box=(1 - lay[0] - lay[2] - 0.02, 0.24 / fh), align="l")
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale = lo, hi
    va.visible = False
    va.has_major_gridlines = False
    ca = chart.category_axis
    baseline(ca, visible=False)
    axis_ticks(ca, 12, C.headline)
    ca.tick_label_position = XL_TICK_LABEL_POSITION.HIGH                 # period headers on top
    points_on_edges(chart)
    takeaways(slide, D.points)
    return slide


def slide_bubble(prs):
    D = bubble_data()
    df = D.df
    slide = chart_slide(
        prs, D.headline, D.subtitle, D.footnote,
        "Bubble chart (native): X = share of tasks exposed to Gen AI (%), Y = median pay ($K), bubble size = headcount, "
        "with size representing area (honest scale) and the bubble scale at 50% so the largest roles don't cover the "
        "rest. One series; the two roles the headline names are blue and labelled (typed labels: update them if the "
        "roles change), the rest grey with a white outline. Edit Data: columns X, Y, Size. For a plain scatter, Change "
        "Chart Type › XY Scatter.")
    data = BubbleChartData()
    s = data.add_series("Roles")
    for r in df.itertuples():
        s.add_data_point(r.genai_exposure_pct, r.median_pay_k, r.headcount)
    fh = CHART_H + 0.15                                                   # room below the baseline for the axis title
    frame, chart = add_chart(slide, XL_CHART_TYPE.BUBBLE, data, width=SIDE_CHART_W, height=fh)
    plot_layout(chart, 0.115, (CARD_TOP - CHART_TOP) / fh, 0.84, (CARD_BOTTOM - CARD_TOP) / fh)
    plot = chart.plots[0]
    plot.bubble_scale = 50
    bp = chart._chartSpace.find(".//" + qn("c:bubbleChart"))
    sr = bp.find(qn("c:sizeRepresents"))
    if sr is None:
        sr = etree.SubElement(bp, qn("c:sizeRepresents"))
        bp.find(qn("c:axId")).addprevious(sr)
    sr.set("val", "area")
    ser = plot.series[0]
    fill(ser, C.context)
    ser.format.line.color.rgb = rgb("#FFFFFF")
    ser.format.line.width = Pt(1)
    lowest = min(D.focus, key=lambda role: float(df.genai_exposure_pct[df.role == role].iloc[0]))
    for i, r in enumerate(df.itertuples()):
        if r.role in D.focus:
            fill(ser.points[i], C.focus)
            ser.points[i].format.line.color.rgb = rgb("#FFFFFF")
            ser.points[i].format.line.width = Pt(1)
            dlbl(ser.points[i], text=D.short.get(r.role, r.role), color=C.headline, bold=True,      # labels apart,
                 pos=XL_LABEL_POSITION.LEFT if r.role == lowest else XL_LABEL_POSITION.ABOVE)       # inside the axis
    xa, ya = chart.category_axis, chart.value_axis
    xa.minimum_scale, xa.maximum_scale, xa.major_unit = 0, 70, 10
    ya.minimum_scale, ya.maximum_scale, ya.major_unit = 0, 160, 40
    gridlines(ya)
    baseline(xa)
    baseline(ya, visible=False)
    axis_ticks(xa, fmt='0"%"')
    axis_ticks(ya, fmt='"$"0"K"')
    for ax, title in ((xa, "Tasks exposed to Gen AI (%)"), (ya, "Median pay ($K)")):
        ax.has_title = True
        tf = ax.axis_title.text_frame
        tf.text = title
        r = tf.paragraphs[0].runs[0]
        r.font.size, r.font.bold, r.font.name = Pt(11), False, FONT
        r.font.color.rgb = rgb(C.text_muted)
    takeaways(slide, D.points)
    return slide


NEW_SLIDES = (slide_kpi, slide_roadmap, slide_tracker, slide_two_charts, slide_column, slide_dumbbell, slide_slope,
              slide_bubble)


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
    for build in (slide_bar, slide_line, slide_waterfall, slide_stacked, *NEW_SLIDES):
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
    for build in (slide_bar, slide_line, slide_waterfall, slide_stacked, *NEW_SLIDES):
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
        ("Sheets: Palette · Bar, Line, Waterfall, Stacked 100% · Heat table · KPI (big-number card with a progress bar) · "
         "Roadmap (Gantt as a stacked bar, with a Today line driven by the as-of date) · Tracker (status with dot, symbol "
         "and word) · Column, Dumbbell, Slope, Scatter. Inputs are in the tables; charts and text follow.", None),
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
    _xlsx_more(wb, f, base_chart, axis_font, label_font, bold_label, pt)
    wb.close()
    # Named cell styles (Home › Cell Styles › Custom), so people can restyle their own sheets the same way.
    named = {"Headline": [f["head"]], "Subtitle": [f["sub"]], "Source": [f["note"]], "Focus row": [f["focus_row"]],
             "Total": total_fmts}
    _theme_xlsx(path, {name: sorted({x._get_xf_index() for x in fmts}) for name, fmts in named.items()})
    return path


def _xlsx_more(wb, f, base_chart, axis_font, label_font, bold_label, pt) -> None:
    """KPI, Roadmap, Tracker and the extra chart sheets (same computed numbers as the starter deck)."""
    from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

    fmt = lambda **kw: wb.add_format(kw)                                               # noqa: E731
    big = fmt(bold=True, font_size=54, font_color=C.headline, num_format="0%", valign="vcenter")
    semi = lambda color: fmt(font_name=SEMI, font_size=14, font_color=color)           # noqa: E731
    muted = fmt(font_color=C.text_muted, font_size=pt["tick"])
    date = fmt(num_format="mmm yyyy", bottom=1, bottom_color=C.grid, align="left")
    pct0 = fmt(num_format="0%", bottom=1, bottom_color=C.grid)
    calc = fmt(num_format="0", bottom=1, bottom_color=C.grid, font_color=C.text_muted)
    input_hint = fmt(italic=True, font_color=C.text_muted, font_size=pt["footnote"], font_name=f"{FONT} Light")
    words = [STATUS[k]["label"] for k in ("on_track", "at_risk", "off_track", "not_started", "done")]
    syms = [STATUS[k]["symbol"] for k in ("on_track", "at_risk", "off_track", "not_started", "done")]
    match = "{" + ",".join(f'"{w}"' for w in words) + "}"
    sym_formula = lambda cell: (f'=IFERROR(CHOOSE(MATCH({cell},{match},0),' +              # noqa: E731
                                ",".join(f'"{s}"' for s in syms) + '),"")')

    def head(ws, headline, subtitle):
        ws.hide_gridlines(2)
        ws.set_row(0, 26)
        ws.set_row(1, 20)
        ws.write(0, 0, headline, f["head"])
        ws.write(1, 0, subtitle, f["sub"])

    def foot(ws, row, footnote, source):
        if footnote:
            ws.write(row, 0, footnote, f["note"])
        ws.write(row + 1, 0, source, f["note"])

    def status_cf(ws, rng, word_cell):
        """Status color on a ● (font) keyed on the status word: status colors only with symbol and word."""
        for k in STATUS_ORDER:
            st = STATUS[k]
            ws.conditional_format(rng, {"type": "formula", "criteria": f'={word_cell}="{st["label"]}"',
                                        "format": fmt(font_color=st["value"], bold=True)})

    # ---------------------------------------------------------------- KPI
    K = kpi_data()
    ws = wb.add_worksheet("KPI")
    head(ws, K.headline, K.subtitle)
    ws.set_column(0, 0, 16)
    ws.set_column(1, 20, 3.3)                     # 20 cells x 5% = the progress bar
    ws.set_column(21, 21, 3)
    ws.set_column(22, 22, 26)
    ws.set_column(23, 25, 14)
    # Inputs (W:Z) and calculations.
    ws.write(2, 22, "Inputs: edit these", f["bold"])
    ws.write_row(3, 22, ["Business unit", "Critical roles", "Ready now Mar 2025", "Ready now Mar 2026"], f["th"])
    r0 = 4
    for i, r in enumerate(K.df.itertuples(), start=r0):
        ws.write(i, 22, r.business_unit, f["cell"])
        ws.write_row(i, 23, [r.critical_roles, r.ready_now_mar25, r.ready_now_mar26], f["int"])
    r1 = r0 + len(K.df) - 1
    tot = r1 + 1
    tf = fmt(bold=True, font_color=C.headline, top=2, top_color=C.total, num_format="#,##0")
    ws.write(tot, 22, "Total", tf)
    for j, v in zip((23, 24, 25), (K.roles, K.prior, K.now)):
        col = xl_col_to_name(j)
        ws.write_formula(tot, j, f"=SUM({col}{r0 + 1}:{col}{r1 + 1})", tf, v)
    c = lambda r, j: xl_rowcol_to_cell(r, j, row_abs=True, col_abs=True)                # noqa: E731
    T, NOW, PRI, TGT = c(tot, 23), c(tot, 25), c(tot, 24), c(tot + 2, 23)
    ws.write(tot + 2, 22, "FY27 target", f["cell"])
    ws.write(tot + 2, 23, K.tgt / 100, pct0)
    ws.write(tot + 4, 22, "Calculated (don't edit)", f["bold"])
    CUR, OLD, D, GAP = c(tot + 5, 23), c(tot + 6, 23), c(tot + 7, 23), c(tot + 8, 23)
    for k, (lab, formula, val, cf) in enumerate((
            ("Coverage now", f"=ROUND({NOW}/{T},2)", K.pct / 100, pct0),
            ("Coverage Mar 2025", f"=ROUND({PRI}/{T},2)", K.pct0 / 100, pct0),
            ("Change (pts)", f"=ROUND(({CUR}-{OLD})*100,0)", K.d, calc),
            ("Gap to target (pts)", f"=ROUND(({TGT}-{CUR})*100,0)", K.gap, calc))):
        ws.write(tot + 5 + k, 22, lab, f["cell"])
        ws.write_formula(tot + 5 + k, 23, formula, cf, val)
    # The card: big number, sentence, comparison, gap, progress bar.
    for r in (3, 4, 5):
        ws.set_row(r, 26)
    ws.merge_range(3, 0, 5, 0, "", big)
    ws.write_formula(3, 0, f"={CUR}", big, K.pct / 100)
    ws.write_formula(3, 1, f'=TEXT({NOW},"#,##0")&" of "&TEXT({T},"#,##0")&" critical roles have at least one '
                           f'ready-now successor"', fmt(font_size=16, font_color=C.text), K.sentence)
    ws.write_formula(4, 1, f'=IF({D}>=0,"{UP} +","{DOWN} −")&ABS({D})&" pts vs. Mar 2025 ("&TEXT({OLD},"0%")&")"',
                     semi(C.positive_text), K.delta)
    ws.conditional_format(4, 1, 4, 1, {"type": "formula", "criteria": f"={D}<0",
                                       "format": fmt(font_color=C.negative_text)})
    ws.write_formula(5, 1, f'=IF({GAP}>0,{GAP}&" pts short of the "&TEXT({TGT},"0%")&" FY27 target",'
                           f'"At or above the "&TEXT({TGT},"0%")&" FY27 target")', semi(C.negative_text), K.gap_text)
    ws.conditional_format(5, 1, 5, 1, {"type": "formula", "criteria": f"={GAP}<=0",
                                       "format": fmt(font_color=C.positive_text)})
    ws.set_row(7, 16)
    ws.set_row(8, 12)
    ws.write(7, 0, f"Target {K.tgt}%", fmt(font_color=C.annotation, font_size=pt["tick"], align="right"))
    tick = fmt(font_color=C.total, bold=True, font_size=10, align="left", valign="bottom")
    for k in range(20):
        lo = k * 0.05
        ws.write_formula(7, 1 + k, f'=IF(AND({TGT}>={lo:.2f},{TGT}<{lo + 0.05:.2f}),"▼","")', tick,
                         "▼" if lo <= K.tgt / 100 < lo + 0.05 else "")
    for k in range(20):
        ws.write_blank(8, 1 + k, None, fmt(bg_color=C.context_light))
    ws.conditional_format(8, 1, 8, 20, {"type": "formula", "criteria": f"={CUR}>=(COLUMN(B9)-COLUMN($B$9))*0.05+0.025",
                                        "format": fmt(bg_color=C.focus)})
    ws.write(9, 1, "0%", muted)
    ws.write(9, 20, "100%", fmt(font_color=C.text_muted, font_size=pt["tick"], align="right"))
    ws.write(11, 0, "Each bar cell = 5 points (filled to the nearest 5); ▼ marks the target. Edit the inputs on the "
                    "right; the number, sentences, colors and bar follow.", input_hint)
    foot(ws, 13, K.footnote, K.source)

    # ---------------------------------------------------------------- Roadmap (Gantt as a stacked bar)
    P = plan_data()
    ws = wb.add_worksheet("Roadmap")
    head(ws, P.headline, P.subtitle)
    widths = [30, 26, 11, 11, 2.5, 2.5, 12, 10, 10, 9]
    for j, w in enumerate(widths):
        ws.set_column(j, j, w)
    heads = ["Workstream", "Owner", "Start", "End", "", "", "Status", "Start (month)", "Duration (months)",
             "Slip (months)"]
    ws.set_row(3, 30)
    ws.write_row(3, 0, heads, f["th"])
    r0, n = 4, P.n
    r1 = r0 + n - 1
    srow, arow = r1 + 3, r1 + 4                                     # timeline start and as-of cells
    START, ASOF, TODAYC = c(srow, 2), c(arow, 2), c(arow + 1, 2)
    dv = {"validate": "list", "source": words}
    for i, r in enumerate(P.plan.itertuples(), start=r0):
        ws.write(i, 0, r.workstream, f["cell"])
        ws.write(i, 1, r.owner, f["cell"])
        y, m = map(int, r.start.split("-"))
        ws.write_datetime(i, 2, datetime(y, m, 1), date)
        y, m = map(int, r.end.split("-"))
        ws.write_datetime(i, 3, datetime(y, m, 1), date)
        ws.write_formula(i, 4, f'=IF(G{i + 1}="","","●")', f["cell"], "●")
        ws.write_formula(i, 5, sym_formula(f"G{i + 1}"), fmt(bold=True, bottom=1, bottom_color=C.grid, align="center"),
                         STATUS[r.status]["symbol"])
        ws.write(i, 6, STATUS[r.status]["label"], f["cell"])
        ws.data_validation(i, 6, i, 6, dv)
        ws.write_formula(i, 7, f"=(YEAR(C{i + 1})-YEAR({START}))*12+MONTH(C{i + 1})-MONTH({START})", calc, r.offset)
        ws.write_formula(i, 8, f"=(YEAR(D{i + 1})-YEAR(C{i + 1}))*12+MONTH(D{i + 1})-MONTH(C{i + 1})+1", calc,
                         r.duration)
        ws.write(i, 9, r.slip, f["int"])
    status_cf(ws, f"E{r0 + 1}:E{r1 + 1}", f"$G{r0 + 1}")
    ws.conditional_format(f"G{r0 + 1}:G{r1 + 1}", {"type": "formula",
                                                   "criteria": f'=OR($G{r0 + 1}="Off track",$G{r0 + 1}="At risk")',
                                                   "format": fmt(bold=True, font_color=C.headline)})
    ws.write(srow, 0, "Timeline starts (FY26 Q1)", f["cell"])
    ws.write_datetime(srow, 2, datetime(2025, 4, 1), fmt(num_format="d mmm yyyy", bottom=1, bottom_color=C.grid))
    ws.write(arow, 0, "Status as of (moves the Today line)", f["cell"])
    ws.write_datetime(arow, 2, datetime(2026, 3, 31), fmt(num_format="d mmm yyyy", bottom=1, bottom_color=C.grid))
    ws.write(arow + 1, 0, "Today (months from start)", f["cell"])
    ws.write_formula(arow + 1, 2, f"=(YEAR({ASOF})-YEAR({START}))*12+MONTH({ASOF})-MONTH({START})"
                                  f"+DAY({ASOF})/DAY(EOMONTH({ASOF},0))", fmt(num_format="0.0", bottom=1,
                                                                             bottom_color=C.grid), P.today)
    ws.write(arow + 2, 0, "Start and End are the first day of the first and last month. Slip = forecast months beyond "
                          "the plan (light grey in the chart). Status: pick from the list; the dot and symbol follow.",
             input_hint)
    # Chart data (formulas): two header rows (phases, quarters) above the workstreams, plus the Today line.
    hc = 12                                                        # column M
    ws.write(2, hc, "Chart data (formulas; don't edit)", f["bold"])
    qn_ = [f"Q{q % 4 + 1} FY{26 + q // 4}" for q in range(PLAN_SPAN // 3)]
    cols = ["Row", "Start", "Duration", "Slip"] + [p[0] for p in PHASES] + qn_ + ["Today offset", "Today line"]
    ws.write_row(3, hc, cols, f["th"])
    ws.set_column(hc, hc, 24)
    ws.set_column(hc + 1, hc + len(cols) - 1, 8)
    rows = 2 + n
    for k in range(rows):
        rr = 4 + k
        if k < 2:
            ws.write(rr, hc, " ", f["cell"])
            ws.write_row(rr, hc + 1, [0, 0, 0], f["int"])
            for j, (_, a, b) in enumerate(PHASES):
                ws.write(rr, hc + 4 + j, (b - a) if k == 0 else 0, f["int"])
            for j in range(len(qn_)):
                ws.write(rr, hc + 7 + j, 3 if k == 1 else 0, f["int"])
            ws.write_row(rr, hc + 7 + len(qn_), [0, 0], f["int"])
        else:
            src = r0 + k - 2 + 1                                   # 1-based row of the workstream
            rp = P.plan.iloc[k - 2]
            ws.write_formula(rr, hc, f"=A{src}", f["cell"], rp.workstream)
            ws.write_formula(rr, hc + 1, f"=H{src}", f["int"], rp.offset)
            ws.write_formula(rr, hc + 2, f"=I{src}", f["int"], rp.duration)
            ws.write_formula(rr, hc + 3, f"=J{src}", f["int"], rp.slip)
            ws.write_row(rr, hc + 4, [0] * (3 + len(qn_)), f["int"])
            ws.write_formula(rr, hc + 7 + len(qn_), f"={TODAYC}-0.04", f["dec"], P.today - 0.04)
            ws.write(rr, hc + 8 + len(qn_), 0.08, f["dec"])
    last = 4 + rows - 1
    cats = ["Roadmap", 4, hc, last, hc]
    vals = lambda j: ["Roadmap", 4, hc + j, last, hc + j]                                # noqa: E731
    only = lambda k: [None if i == k else {"delete": True} for i in range(rows)]         # noqa: E731
    chart = base_chart("bar", "stacked")
    chart.set_size({"width": 980, "height": 430})
    chart.add_series({"name": "Start", "categories": cats, "values": vals(1), "fill": {"none": True},
                      "border": {"none": True}, "gap": 80, "overlap": 100})
    colors = {"off_track": C.focus, "not_started": C.context_light}
    chart.add_series({"name": "Duration", "categories": cats, "values": vals(2), "fill": {"color": C.context},
                      "points": [None, None] + [{"fill": {"color": colors.get(s, C.context)}} for s in P.plan.status]})
    chart.add_series({"name": "Slip", "categories": cats, "values": vals(3), "fill": {"none": True},
                      "border": {"none": True},
                      "points": [None, None] + [{"fill": {"color": C.context_light},
                                                 "border": {"color": C.context, "width": 0.75, "dash_type": "dash"}}
                                                if s else None for s in P.plan.slip]})
    for j, (name, _, _) in enumerate(PHASES):
        chart.add_series({"name": ["Roadmap", 3, hc + 4 + j], "categories": cats, "values": vals(4 + j),
                          "fill": {"color": C.context_light if j % 2 == 0 else C.grid},
                          "data_labels": {"series_name": True, "position": "inside_base", "custom": only(0),
                                          "font": {"name": FONT, "size": 9, "color": C.headline}}})
    for j in range(len(qn_)):
        chart.add_series({"name": ["Roadmap", 3, hc + 7 + j], "categories": cats, "values": vals(7 + j),
                          "fill": {"none": True}, "border": {"none": True},
                          "data_labels": {"series_name": True, "position": "center", "custom": only(1),
                                          "font": {"name": FONT, "size": 9, "color": C.text_muted}}})
    chart.set_x_axis({"min": 0, "max": PLAN_SPAN, "major_unit": 3, "visible": False,
                      "major_gridlines": {"visible": True, "line": {"color": C.grid, "width": 0.75}}})
    chart.set_y_axis({"reverse": True, "num_font": {**axis_font, "size": pt["label"], "color": C.text},
                      "major_tick_mark": "none", "line": {"none": True}})
    chart.set_plotarea({"layout": {"x": 0.25, "y": 0.02, "width": 0.72, "height": 0.96},
                        "border": {"none": True}, "fill": {"none": True}})
    today = wb.add_chart({"type": "bar", "subtype": "stacked"})
    today.add_series({"name": "Today offset", "categories": cats, "values": vals(7 + len(qn_)), "y2_axis": True,
                      "fill": {"none": True}, "border": {"none": True}, "gap": 0, "overlap": 100})
    today.add_series({"name": "Today", "categories": cats, "values": vals(8 + len(qn_)), "y2_axis": True,
                      "fill": {"color": C.total}, "border": {"none": True}})
    # xlsxwriter maps a secondary bar chart's axes the other way round: y2 is the value axis, x2 the categories.
    today.set_y2_axis({"min": 0, "max": PLAN_SPAN, "visible": False, "major_gridlines": {"visible": False}})
    today.set_x2_axis({"reverse": True, "visible": False})
    chart.combine(today)
    ws.insert_chart(r1 + 9, 0, chart)
    mrow = r1 + 32
    ws.write(mrow - 1, 0, f"Milestones (◆ met, ◇ due, ✕ missed; a moved milestone keeps its original date). Today line: "
                          f"change the as-of date above. Milestone diamonds aren't drawn in this chart: see the "
                          f"starter deck, or add them as shapes.", input_hint)
    ws.write_row(mrow, 0, ["Workstream", "Milestone", "Due", "Forecast", "", "Mark", "State"], f["th"])
    state_word = {"met": "Met", "upcoming": "Due", "moved": "Moved", "missed": "Missed"}
    mark = {"Met": "◆", "Due": "◇", "Moved": "◇", "Missed": "✕"}
    for i, m in enumerate(P.ms.itertuples(), start=mrow + 1):
        ws.write(i, 0, m.workstream, f["cell"])
        ws.write(i, 1, m.milestone, f["cell"])
        y, mm = map(int, m.due.split("-"))
        ws.write_datetime(i, 2, datetime(y, mm, 1), date)
        if m.forecast and m.forecast != m.due:
            y, mm = map(int, m.forecast.split("-"))
            ws.write_datetime(i, 3, datetime(y, mm, 1), date)
        else:
            ws.write(i, 3, "", f["cell"])
        ws.write(i, 4, "", f["cell"])
        w = state_word[m.state]
        ws.write_formula(i, 5, f'=IFERROR(CHOOSE(MATCH(G{i + 1},{{"Met","Due","Moved","Missed"}},0),"◆","◇","◇","✕"),"")',
                         fmt(bold=True, font_color=C.total, bottom=1, bottom_color=C.grid, align="center"), mark[w])
        ws.write(i, 6, w, f["cell"])
        ws.data_validation(i, 6, i, 6, {"validate": "list", "source": ["Met", "Due", "Moved", "Missed"]})
    mlast = mrow + len(P.ms)
    ws.conditional_format(f"F{mrow + 2}:F{mlast + 1}", {"type": "formula", "criteria": f'=$G{mrow + 2}="Missed"',
                                                         "format": fmt(font_color=STATUS["off_track"]["value"])})
    foot(ws, mlast + 2, STATUS_DEF + f" Light grey = forecast: the paused {P.paused} restarts when the integration "
                                     f"goes live, {P.slip} months late.", PLAN_SRC)

    # ---------------------------------------------------------------- Tracker
    ws = wb.add_worksheet("Tracker")
    head(ws, P.tr_headline, P.tr_subtitle)
    for j, w in enumerate([2.5, 2.5, 12, 30, 26, 11, 11, 28, 24, 60]):
        ws.set_column(j, j, w)
    r0 = 6
    r1 = r0 + n - 1
    WORD = f"$C${r0 + 1}:$C${r1 + 1}"
    parts = '&" · "&'.join(f'"{STATUS[k]["symbol"]} "&COUNTIF({WORD},"{STATUS[k]["label"]}")&" {STATUS[k]["label"].lower()}"'
                             for k, _ in P.rollup)
    ws.write_formula(3, 0, f'="{n} workstreams · "&{parts}', fmt(bold=True, font_color=C.headline, font_size=12),
                     f"{n} workstreams · " + " · ".join(f"{STATUS[k]['symbol']} {c_} {STATUS[k]['label'].lower()}"
                                                       for k, c_ in P.rollup))
    ws.set_row(5, 20)
    ws.write_row(5, 0, ["", "", "Status", "Workstream", "Owner", "Start", "End", "Next milestone", "When",
                        "What changed"], f["th"])
    wrap = fmt(text_wrap=True, valign="top", bottom=1, bottom_color=C.grid)
    for i, r in enumerate(P.sorted.itertuples(), start=r0):
        ws.set_row(i, 30)
        ws.write_formula(i, 0, f'=IF(C{i + 1}="","","●")', fmt(valign="top", bottom=1, bottom_color=C.grid), "●")
        ws.write_formula(i, 1, sym_formula(f"C{i + 1}"), fmt(bold=True, valign="top", align="center", bottom=1,
                                                             bottom_color=C.grid), STATUS[r.status]["symbol"])
        ws.write(i, 2, STATUS[r.status]["label"], wrap)
        ws.data_validation(i, 2, i, 2, dv)
        ws.write(i, 3, r.workstream, wrap)
        ws.write(i, 4, r.owner, wrap)
        for j, s in ((5, r.start), (6, r.end)):
            y, m = map(int, s.split("-"))
            ws.write_datetime(i, j, datetime(y, m, 1), fmt(num_format="mmm yyyy", valign="top", align="left",
                                                           bottom=1, bottom_color=C.grid))
        name, when, flagged = next_milestone(P, r.workstream)
        ws.write(i, 7, name, wrap)
        ws.write(i, 8, when, fmt(text_wrap=True, valign="top", bottom=1, bottom_color=C.grid, bold=flagged,
                                 font_color=C.headline if flagged else C.text))
        ws.write(i, 9, r.what_changed, wrap)
    status_cf(ws, f"A{r0 + 1}:A{r1 + 1}", f"$C{r0 + 1}")
    ws.conditional_format(f"C{r0 + 1}:D{r1 + 1}", {"type": "formula",
                                                   "criteria": f'=OR($C{r0 + 1}="Off track",$C{r0 + 1}="At risk")',
                                                   "format": fmt(bold=True, font_color=C.headline)})
    ws.write(r1 + 2, 0, "Pick the status from the list: the ● color, the symbol, the bold for exceptions and the "
                        "roll-up counts follow. Keep off track and at risk at the top (Data › Sort by a helper "
                        "column if needed). No row fills: the dot, symbol and word carry the status.", input_hint)
    foot(ws, r1 + 4, STATUS_DEF, PLAN_SRC)

    # ---------------------------------------------------------------- Column (highlight)
    D = column_data()
    ws = wb.add_worksheet("Column")
    head(ws, D.headline, D.subtitle)
    ws.set_column(0, 1, 14)
    ws.write_row(3, 0, ["Fiscal year", "Internal fill rate (%)"], f["th"])
    for i, r in enumerate(D.df.itertuples(), start=4):
        ws.write(i, 0, r.fiscal_year, f["focus_row"] if i == 3 + len(D.df) else f["cell"])
        ws.write(i, 1, r.internal_fill_pct, f["int"])
    n_ = len(D.df)
    chart = base_chart("column")
    chart.set_size({"width": 620, "height": 400})
    chart.add_series({
        "categories": ["Column", 4, 0, 3 + n_, 0], "values": ["Column", 4, 1, 3 + n_, 1], "gap": BAND_GAP,
        "fill": {"color": C.context}, "points": [None] * (n_ - 1) + [{"fill": {"color": C.focus}}],
        "data_labels": {"value": True, "position": "outside_end", "num_format": '0"%"', "font": label_font,
                        "custom": [None] * (n_ - 1) + [{"value": f"{D.df.internal_fill_pct.iloc[-1]}%",
                                                        "font": {**bold_label, "color": C.headline}}]}})
    chart.set_y_axis({"visible": False, "min": 0, "max": 35, "major_gridlines": {"visible": False}})
    chart.set_x_axis({"num_font": {**axis_font, "size": pt["label"], "color": C.text}, "major_tick_mark": "none",
                      "line": {"color": C.axis, "width": 0.75}})
    ws.insert_chart(3, 3, chart)
    foot(ws, 25, D.footnote, SRC)

    # ---------------------------------------------------------------- Dumbbell (XY scatter + custom error bars)
    D = dumbbell_data()
    ws = wb.add_worksheet("Dumbbell")
    head(ws, D.headline, D.subtitle)
    hd = ["Role", "Market ($K)", "McKesson ($K)", "Row", "Plus", "Minus", "Axis X", "Label X", "Gap", "Below market?",
          "McKesson (flagged)"]
    ws.set_column(0, 0, 22)
    ws.set_column(1, len(hd) - 1, 11)
    ws.set_row(3, 30)
    ws.write_row(3, 0, hd, f["th"])
    n_ = len(D.df)
    x_min, x_max = 30, 160
    for k, r in enumerate(D.df.itertuples()):
        i = 4 + k
        R = i + 1
        hi = r.role in D.focus
        ws.write(i, 0, r.role, f["focus_row"] if hi else f["cell"])
        ws.write_row(i, 1, [r.market_median_k, r.internal_median_k], f["int"])
        ws.write(i, 3, n_ - k, f["int"])
        ws.write_formula(i, 4, f"=MAX(0,B{R}-C{R})", calc, max(0, r.market_median_k - r.internal_median_k))
        ws.write_formula(i, 5, f"=MAX(0,C{R}-B{R})", calc, max(0, r.internal_median_k - r.market_median_k))
        ws.write(i, 6, x_min, f["int"])
        ws.write_formula(i, 7, f"=MAX(B{R},C{R})+3", calc, max(r.market_median_k, r.internal_median_k) + 3)
        ws.write_formula(i, 8, f'=IF(C{R}<B{R},"−","+")&TEXT(ABS(C{R}-B{R})/B{R},"0.0%")', f["cell"],
                         mv.signed(r.gap_pct, 1, "%"))
        ws.write(i, 9, "Yes" if hi else "No", f["cell"])
        ws.write_formula(i, 10, f'=IF(J{R}="Yes",C{R},NA())', calc, r.internal_median_k if hi else "#N/A")
    a, b = 4, 3 + n_
    S = "Dumbbell"
    chart = base_chart("scatter")
    chart.set_size({"width": 860, "height": 430})
    chart.add_series({"name": "Market", "categories": [S, a, 1, b, 1], "values": [S, a, 3, b, 3],
                      "marker": {"type": "circle", "size": 7, "fill": {"color": C.context}, "border": {"none": True}}})
    chart.add_series({"name": "McKesson", "categories": [S, a, 2, b, 2], "values": [S, a, 3, b, 3],
                      "marker": {"type": "circle", "size": 9, "fill": {"color": C.focus}, "border": {"none": True}},
                      "x_error_bars": {"type": "custom", "plus_values": f"={S}!$E${a + 1}:$E${b + 1}",
                                       "minus_values": f"={S}!$F${a + 1}:$F${b + 1}", "end_style": 0,
                                       "line": {"color": C.context_light, "width": 3}}})
    chart.add_series({"name": "McKesson, below market (the headline)", "categories": [S, a, 10, b, 10],
                      "values": [S, a, 3, b, 3],
                      "marker": {"type": "circle", "size": 9, "fill": {"color": C.negative}, "border": {"none": True}}})
    chart.add_series({"name": "Role labels", "categories": [S, a, 6, b, 6], "values": [S, a, 3, b, 3],
                      "marker": {"type": "none"},
                      "data_labels": {"value": False, "position": "left", "font": {**label_font, "size": pt["tick"]},
                                      "custom": [{"value": f"={S}!$A${a + 1 + k}"} for k in range(n_)]}})
    chart.add_series({"name": "Gap labels", "categories": [S, a, 7, b, 7], "values": [S, a, 3, b, 3],
                      "marker": {"type": "none"},
                      "data_labels": {"value": False, "position": "right", "font": label_font,
                                      "custom": [{"value": f"={S}!$I${a + 1 + k}",
                                                  **({"font": {**bold_label, "color": C.negative_text}}
                                                     if r.role in D.focus else {})}
                                                 for k, r in enumerate(D.df.itertuples())]}})
    chart.set_x_axis({"min": x_min, "max": x_max, "major_unit": 25, "num_format": '"$"#,##0"K"', "num_font": axis_font,
                      "line": {"none": True}, "major_tick_mark": "none",
                      "major_gridlines": {"visible": True, "line": {"color": C.grid, "width": 0.75}}})
    chart.set_y_axis({"min": 0.5, "max": n_ + 0.5, "visible": False, "major_gridlines": {"visible": False}})
    chart.set_plotarea({"layout": {"x": 0.2, "y": 0.04, "width": 0.65, "height": 0.86},
                        "border": {"none": True}, "fill": {"none": True}})
    ws.insert_chart(4 + n_ + 2, 0, chart)
    foot(ws, 4 + n_ + 25, D.footnote, SRC)

    # ---------------------------------------------------------------- Slope (line, two points per business unit)
    D = slope_data()
    ws = wb.add_worksheet("Slope")
    head(ws, D.headline, D.subtitle)
    ws.set_column(0, 0, 26)
    ws.set_column(1, 4, 11)
    ws.write_row(3, 0, ["Business unit", "FY25", "FY26", "Change (pts)", "End label"], f["th"])
    order = [x for x in D.df.index if x != D.focus] + [D.focus]
    for k, bu in enumerate(order):
        i, R = 4 + k, 5 + k
        hi = bu == D.focus
        ws.write(i, 0, bu, f["focus_row"] if hi else f["cell"])
        ws.write_row(i, 1, [int(D.df.FY25[bu]), int(D.df.FY26[bu])], f["int"])
        ws.write_formula(i, 3, f"=C{R}-B{R}", f["delta"], int(D.df.d[bu]))
        ws.write_formula(i, 4, f'=A{R}&" "&C{R}&"%"', f["cell"], f"{bu} {int(D.df.FY26[bu])}%")
    chart = base_chart("line")
    chart.set_size({"width": 760, "height": 460})
    for k, bu in enumerate(order):
        i = 4 + k
        hi = bu == D.focus
        color = C.focus if hi else C.context
        font = {**(bold_label if hi else label_font), "color": C.headline if hi else C.text}
        chart.add_series({"name": ["Slope", i, 0], "categories": ["Slope", 3, 1, 3, 2], "values": ["Slope", i, 1, i, 2],
                          "line": {"color": color, "width": 2.25 if hi else 1.25},
                          "marker": {"type": "circle", "size": 6, "fill": {"color": color}, "border": {"none": True}},
                          "data_labels": {"value": True, "position": "left", "num_format": '0"%"', "font": font,
                                          "custom": [None, {"delete": True}]}})
        chart.add_series({"name": ["Slope", i, 0], "categories": ["Slope", 3, 1, 3, 2], "values": ["Slope", i, 1, i, 2],
                          "line": {"none": True}, "marker": {"type": "none"},
                          "data_labels": {"value": True, "position": "right", "font": font,
                                          "custom": [{"delete": True}, {"value": f"=Slope!$E${i + 1}"}]}})
    chart.set_y_axis({"min": 10, "max": 45, "visible": False, "major_gridlines": {"visible": False}})
    chart.set_x_axis({"num_font": {**axis_font, "size": pt["label"], "color": C.headline, "bold": True},
                      "major_tick_mark": "none", "line": {"none": True}, "label_position": "high"})
    chart.set_plotarea({"layout": {"x": 0.18, "y": 0.08, "width": 0.45, "height": 0.84},
                        "border": {"none": True}, "fill": {"none": True}})
    ws.insert_chart(3, 6, chart)
    ws.write(12, 0, "Labels next to each other can touch: drag a label to nudge it.", input_hint)
    foot(ws, 26, D.footnote, SRC)

    # ---------------------------------------------------------------- Scatter (Excel: bubble via Change Chart Type)
    D = bubble_data()
    ws = wb.add_worksheet("Scatter")
    head(ws, D.headline, D.subtitle)
    ws.set_column(0, 0, 28)
    ws.set_column(1, 5, 12)
    ws.set_row(3, 30)
    ws.write_row(3, 0, ["Role", "Gen AI exposure (%)", "Median pay ($K)", "Headcount", "Flagged?",
                        "Pay (flagged)"], f["th"])
    n_ = len(D.df)
    for k, r in enumerate(D.df.itertuples()):
        i, R = 4 + k, 5 + k
        hi = r.role in D.focus
        ws.write(i, 0, r.role, f["focus_row"] if hi else f["cell"])
        ws.write_row(i, 1, [r.genai_exposure_pct, r.median_pay_k, r.headcount], f["int"])
        ws.write(i, 4, "Yes" if hi else "No", f["cell"])
        ws.write_formula(i, 5, f'=IF(E{R}="Yes",C{R},NA())', calc, r.median_pay_k if hi else "#N/A")
    a, b = 4, 3 + n_
    chart = base_chart("scatter")
    chart.add_series({"name": "Roles", "categories": ["Scatter", a, 1, b, 1], "values": ["Scatter", a, 2, b, 2],
                      "marker": {"type": "circle", "size": 9, "fill": {"color": C.context},
                                 "border": {"color": "#FFFFFF", "width": 0.75}}})
    chart.add_series({"name": "Flagged roles", "categories": ["Scatter", a, 1, b, 1], "values": ["Scatter", a, 5, b, 5],
                      "marker": {"type": "circle", "size": 10, "fill": {"color": C.focus},
                                 "border": {"color": "#FFFFFF", "width": 0.75}},
                      "data_labels": {"value": False, "position": "right", "font": {**bold_label, "color": C.headline},
                                      "custom": [{"value": f"=Scatter!$A${a + 1 + k}"} if r.role in D.focus
                                                 else {"delete": True} for k, r in enumerate(D.df.itertuples())]}})
    chart.set_x_axis({"min": 0, "max": 70, "major_unit": 10, "num_format": '0"%"', "num_font": axis_font,
                      "line": {"color": C.axis, "width": 0.75}, "major_tick_mark": "none",
                      "name": "Tasks exposed to Gen AI (%)", "name_font": {**axis_font, "bold": False}})
    chart.set_y_axis({"min": 0, "max": 160, "major_unit": 40, "num_format": '"$"0"K"', "num_font": axis_font,
                      "line": {"none": True}, "major_tick_mark": "none",
                      "major_gridlines": {"visible": True, "line": {"color": C.grid, "width": 0.75}},
                      "name": "Median pay ($K)", "name_font": {**axis_font, "bold": False}})
    ws.insert_chart(3, 7, chart)
    ws.write(4 + n_ + 1, 0, "Bubble version: select the chart › Change Chart Type › Bubble, then Select Data › each "
                            "series › Series bubble size = Headcount (Format Data Series › Size represents: Area).",
             input_hint)
    foot(ws, 28, D.footnote, SRC)


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
