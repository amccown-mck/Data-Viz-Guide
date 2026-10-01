"""Inventory fonts, fill/stroke colors, and text-color usage in brand reference PDFs."""
import sys
from collections import Counter
from pathlib import Path

import fitz

SRC = Path(sys.argv[1])


def hexify(rgb):
    if rgb is None:
        return None
    return "#{:02X}{:02X}{:02X}".format(*(round(c * 255) for c in rgb[:3]))


for pdf in sorted(SRC.glob("*.pdf")):
    doc = fitz.open(pdf)
    fonts, fills, strokes, text_colors = Counter(), Counter(), Counter(), Counter()
    sizes = Counter()
    for page in doc:
        for f in page.get_fonts(full=True):
            fonts[f[3]] += 1
        for d in page.get_drawings():
            if d.get("fill"):
                fills[hexify(d["fill"])] += 1
            if d.get("color"):
                strokes[hexify(d["color"])] += 1
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    c = span["color"]
                    text_colors[(f"#{c:06X}", span["font"])] += len(span["text"])
                    sizes[(span["font"], round(span["size"], 1))] += len(span["text"])
    print(f"\n===== {pdf.name}  pages={len(doc)}  size={doc[0].rect}")
    print("-- fonts:", fonts.most_common(25))
    print("-- fills:", fills.most_common(30))
    print("-- strokes:", strokes.most_common(15))
    print("-- text color x font (chars):", text_colors.most_common(25))
    print("-- font x size (chars):", sizes.most_common(30))
