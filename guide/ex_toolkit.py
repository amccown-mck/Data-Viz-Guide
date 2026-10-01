"""Toolkit snippets: the QA checklist rendered from docs/qa-checklist.md, so the guide never drifts from it."""
from __future__ import annotations

import html
import re

from exhibits import HTML, ROOT


def _inline(md: str) -> str:
    """Escape, then turn **bold**, `code` and [text](link) into HTML (links become plain text)."""
    s = html.escape(md, quote=False)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s.replace(" — ", ", ").replace("—", ", ")


def qa_checklist() -> str:
    groups, current = [], None
    for line in (ROOT / "docs" / "qa-checklist.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = (line[3:].strip(), [])
            groups.append(current)
        elif line.startswith("- [ ]") and current:
            current[1].append(_inline(line[5:].strip()))
    cols = "".join(f'<div><h4>{html.escape(name)}</h4><ul class="checklist">'
                   + "".join(f"<li>{item}</li>" for item in items) + "</ul></div>" for name, items in groups)
    return f'<div class="qa-grid">{cols}</div>'


HTML["qa_checklist"] = qa_checklist()
