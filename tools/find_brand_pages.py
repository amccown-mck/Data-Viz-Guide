"""Find brand pages mentioning color/typography, dump their text, and render them to PNG for review."""
import re
import sys
from pathlib import Path

import pymupdf

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
KEYS = re.compile(r"colou?r|palette|typograph|font|hex|#[0-9A-F]{6}|RGB|CMYK|PMS|chart|graph|data", re.I)

for pdf in sorted(SRC.glob("*.pdf")):
    doc = pymupdf.open(pdf)
    for i, page in enumerate(doc, 1):
        text = page.get_text()
        hits = sorted({m.group(0).lower() for m in KEYS.finditer(text)})
        if hits:
            print(f"\n--- {pdf.stem[:20]} p{i}: {hits}")
            print(re.sub(r"\s+", " ", text)[:700])
