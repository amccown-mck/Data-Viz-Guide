"""Run the code blocks in the cookbook the way a reader would paste them.

    python tools/check_snippets.py                         # every "# verified" ```python block, all pages
    python tools/check_snippets.py docs/cookbook/venn.md   # one or more pages
    python tools/check_snippets.py --lang r                # every ```r block (smoke test; needs Rscript)

Each block runs in its own subprocess from the repo root: Python with the matplotlib backend Agg, R with a null
graphics device so printed plots are built (which surfaces errors) but nothing is written to disk.
Exits non-zero if any block fails, so it can gate CI.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "python": re.compile(r"^```python\n(# verified.*?)^```", re.M | re.S),
    "r": re.compile(r"^```r\n(.*?)^```", re.M | re.S),
}
R_PRELUDE = "pdf(NULL)\n"                                  # auto-printed ggplots render to a null device


def blocks(md: Path, lang: str) -> list[tuple[int, str]]:
    text = md.read_text(encoding="utf-8")
    return [(text[:m.start()].count("\n") + 1, m.group(1)) for m in PATTERNS[lang].finditer(text)]


def rscript() -> str:
    found = shutil.which("Rscript") or next(
        (str(p) for p in sorted(Path(r"C:\Program Files\R").glob("R-*/bin/Rscript.exe"), reverse=True)), None)
    if not found:
        sys.exit("Rscript not found; install R or put Rscript on PATH.")
    return found


def run(code: str, lang: str) -> subprocess.CompletedProcess:
    suffix, cmd = (".py", [sys.executable]) if lang == "python" else (".R", [rscript()])
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(code if lang == "python" else R_PRELUDE + code)
    try:
        env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(cmd + [f.name], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=env, timeout=300)
    finally:
        os.unlink(f.name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pages", nargs="*", help="markdown pages (default: docs/cookbook/*.md)")
    ap.add_argument("--lang", choices=sorted(PATTERNS), default="python")
    args = ap.parse_args()
    pages = [Path(p).resolve() for p in args.pages] or sorted((ROOT / "docs" / "cookbook").glob("*.md"))
    failed = total = 0
    for md in pages:
        for line, code in blocks(md, args.lang):
            total += 1
            res = run(code, args.lang)
            ok = res.returncode == 0
            failed += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {md.relative_to(ROOT)}:{line}")
            if not ok:
                lines = [ln for ln in res.stderr.strip().splitlines() if "was built under R version" not in ln]
                print("     " + "\n     ".join(lines[-6:]))
    print(f"\n{failed} of {total} {args.lang} block(s) failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
