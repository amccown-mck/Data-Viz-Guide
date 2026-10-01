"""Print the one-page reference sheets in templates/print/*.html to PDF with headless Chrome or Edge.

    python tools/build_print.py            -> dist/print/<name>.pdf

The pages read colors from dist/web/mck-viz.css and fonts from fonts/LibreFranklin, so run tokens/build.py first
after a token change. Set CHROME=<path> if the browser isn't found automatically.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "templates" / "print"
OUT = ROOT / "dist" / "print"
CANDIDATES = [
    os.environ.get("CHROME", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("msedge") or "",
]


def browser() -> str:
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("No Chrome/Edge found; set CHROME to the browser executable.")


def main() -> None:
    exe = browser()
    OUT.mkdir(parents=True, exist_ok=True)
    for page in sorted(SRC.glob("*.html")):
        pdf = OUT / f"{page.stem}.pdf"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        "--virtual-time-budget=5000", f"--print-to-pdf={pdf}", page.as_uri()],
                       check=True, capture_output=True)
        pages = _page_count(pdf)
        print(f"wrote {pdf.relative_to(ROOT)} ({pages} page{'s' if pages != 1 else ''})")
        if pages != 1:
            print(f"  warning: {page.name} should fit on one page")


def _page_count(pdf: Path) -> int:
    try:
        import pymupdf
        return len(pymupdf.open(pdf))
    except ImportError:
        return pdf.read_bytes().count(b"/Type /Page") - pdf.read_bytes().count(b"/Type /Pages")


if __name__ == "__main__":
    main()
