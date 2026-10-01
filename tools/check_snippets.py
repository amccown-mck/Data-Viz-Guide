"""Run every ```python block in the cookbook that starts with a "# verified" comment.

    python tools/check_snippets.py                       # all cookbook pages
    python tools/check_snippets.py docs/cookbook/venn.md # one or more pages

Each block runs in its own subprocess from the repo root (matplotlib backend Agg), the way a reader would paste it.
Exits non-zero if any block fails, so it can gate CI.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r"^```python\n(# verified.*?)^```", re.M | re.S)


def blocks(md: Path) -> list[tuple[int, str]]:
    text = md.read_text(encoding="utf-8")
    return [(text[:m.start()].count("\n") + 1, m.group(1)) for m in BLOCK.finditer(text)]


def run(code: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
    try:
        env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
        return subprocess.run([sys.executable, f.name], cwd=ROOT, capture_output=True, text=True, env=env, timeout=300)
    finally:
        os.unlink(f.name)


def main(paths: list[str]) -> int:
    pages = [Path(p).resolve() for p in paths] or sorted((ROOT / "docs" / "cookbook").glob("*.md"))
    failed = 0
    for md in pages:
        for line, code in blocks(md):
            res = run(code)
            ok = res.returncode == 0
            failed += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {md.relative_to(ROOT)}:{line}")
            if not ok:
                print("     " + "\n     ".join(res.stderr.strip().splitlines()[-6:]))
    print(f"\n{failed} failing block(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
