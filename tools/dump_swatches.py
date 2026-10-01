"""Dump filled rectangles (position + hex) from one PDF page, to map palette swatches to labels."""
import sys

import pymupdf

doc = pymupdf.open(sys.argv[1])
page = doc[int(sys.argv[2]) - 1]
rows = []
for d in page.get_drawings():
    if d.get("fill") and d["rect"].width > 5 and d["rect"].height > 5:
        r = d["rect"]
        hx = "#{:02X}{:02X}{:02X}".format(*(round(c * 255) for c in d["fill"][:3]))
        rows.append((round(r.x0), round(r.y0), round(r.width), round(r.height), hx))
for row in sorted(rows):
    print(row)
print("--- labels")
for b in page.get_text("blocks"):
    print(round(b[0]), round(b[1]), b[4].replace("\n", " ")[:60])
