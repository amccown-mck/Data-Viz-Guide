"""Render PDF pages to PNG and build numbered contact sheets for quick visual review."""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

pdf_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
pages = [int(p) for p in sys.argv[3].split(",")] if len(sys.argv) > 3 and sys.argv[3] else None
out_dir.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(pdf_path)

if pages:
    for p in pages:
        doc[p - 1].get_pixmap(dpi=110).save(out_dir / f"{pdf_path.stem[:12]}_p{p:02d}.png")
else:
    thumbs = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=40)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ImageDraw.Draw(img).rectangle([0, 0, 34, 18], fill="black")
        ImageDraw.Draw(img).text((3, 3), f"p{i}", fill="yellow")
        thumbs.append(img)
    cols, per_sheet = 4, 16
    w, h = thumbs[0].size
    for s in range(0, len(thumbs), per_sheet):
        chunk = thumbs[s : s + per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * h), "white")
        for j, t in enumerate(chunk):
            sheet.paste(t.resize((w, h)), ((j % cols) * w, (j // cols) * h))
        sheet.save(out_dir / f"{pdf_path.stem[:12]}_sheet{s // per_sheet + 1}.png")
