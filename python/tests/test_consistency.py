"""The hand-written rule files agree with tokens/tokens.json.

Colors and type sizes live in tokens/tokens.json; AGENTS.md, the Copilot instructions, the docs and the rules
template restate some of them in prose. Each check below names one file and one rule, and states the exact
wording it expects, built from the tokens. A file that doesn't state a rule isn't checked for it, but no file
may keep the superseded wording (slide title "24 pt Bold Navy", teal as the second category).

    python -m pytest python/tests/test_consistency.py -q
"""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path

import pytest

import mckviz as mv

REPO = Path(__file__).resolve().parents[2]
if not (REPO / "tokens" / "tokens.json").exists():
    pytest.skip("needs the kit repo (tokens/tokens.json)", allow_module_level=True)

TOKENS = json.loads((REPO / "tokens" / "tokens.json").read_text(encoding="utf-8"))
CATEGORICAL = [h.upper() for h in TOKENS["color"]["categorical"]["values"]]
ROLES = TOKENS["typography"]["roles"]
TITLE_PT, TITLE_PX = ROLES["slide_title"]["size_pt"], ROLES["slide_title"]["size_px"]
TITLE_HEX = TOKENS["color"]["text"]["title"]["value"]
HEAD_PT, HEAD_PX = ROLES["headline"]["size_pt"], ROLES["headline"]["size_px"]
HEAD_HEX = TOKENS["color"]["text"]["headline"]["value"]
MIN_N = inspect.signature(mv.suppress_small).parameters["min_n"].default

# How the docs name each categorical color. A new token color needs a name here.
NAMES = {"#005A8C": "blue", "#143359": "navy", "#009EFF": "bright blue", "#00AF9D": "teal", "#05CE90": "mint",
         "#EF8200": "orange"}
CAT_NAMES = [NAMES[h] for h in CATEGORICAL]
TEAL = next(h for h, name in NAMES.items() if name == "teal")

FILES = ["AGENTS.md", ".github/copilot-instructions.md", ".github/instructions/viz-python.instructions.md",
         ".github/instructions/viz-web.instructions.md", ".github/instructions/viz-r.instructions.md",
         "docs/color.md", "docs/powerbi-setup.md", "docs/typography-and-layout.md",
         "agents/mck-viz-rules.template.md"]


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def names_in_order(n: int = 5) -> str:
    """'blue, navy, bright blue, teal, mint' as a regex (comma lists, any case)."""
    return r",\s*".join(re.escape(x) for x in CAT_NAMES[:n])


def hexes_in_order(n: int = 5) -> str:
    """The first n categorical hexes in order, up to 120 characters apart, with no other categorical hex between."""
    other = "|".join(CATEGORICAL)
    gap = rf"(?:(?!{other}).){{0,120}}?"
    return gap.join(re.escape(h) for h in CATEGORICAL[:n])


# (file, rule, regex the file must contain). Built from the tokens, so a token change shows every file to update.
REQUIRED = [
    # categorical order
    ("AGENTS.md", "categorical order (names)", names_in_order()),
    ("docs/color.md", "categorical order (hex table)", hexes_in_order(6)),
    ("docs/powerbi-setup.md", "categorical order (data colors 1-6)", hexes_in_order(6)),
    ("docs/powerbi-setup.md", "categorical order (names)", names_in_order()),
    ("agents/mck-viz-rules.template.md", "categorical order (names)", names_in_order()),
    ("agents/mck-viz-rules.template.md", "categorical order (from tokens)", re.escape("{{list:categorical.values}}")),
    # slide title
    ("AGENTS.md", "slide title spec", rf"Slide title Bold {TITLE_PT} pt McKesson Blue `{TITLE_HEX}`"),
    ("docs/typography-and-layout.md", "slide title (type roles table)",
     rf"\| Slide title \| Bold 700 \| {TITLE_PT} \| {TITLE_PX} \| McKesson Blue `{TITLE_HEX}`"),
    ("docs/typography-and-layout.md", "slide title (two charts on a slide)",
     rf"\| Slide title \| Bold {TITLE_PT} pt, McKesson Blue"),
    ("docs/color.md", "slide titles are McKesson Blue", r"Slide titles are McKesson Blue"),
    ("agents/mck-viz-rules.template.md", "slide title spec (from tokens)",
     re.escape("Slide title: bold {{role:slide_title.size_pt}} pt, McKesson Blue `{{color:text.title}}`")),
    # chart headline
    ("AGENTS.md", "chart headline spec", rf"headline SemiBold {HEAD_PT} pt navy `{HEAD_HEX}`"),
    ("docs/typography-and-layout.md", "chart headline (type roles table)",
     rf"\| Chart headline \| SemiBold 600 \| {HEAD_PT} \| {HEAD_PX} \| Navy `{HEAD_HEX}`"),
    ("docs/typography-and-layout.md", "chart headline (two charts on a slide)",
     rf"\| Chart headline \(each chart\) \| SemiBold {HEAD_PT} pt, Navy"),
    ("agents/mck-viz-rules.template.md", "chart headline spec (from tokens)",
     re.escape("Chart headline (a chart with its own title): semibold {{role:headline.size_pt}} pt")),
    # minimum n
    ("AGENTS.md", "minimum n (mv.suppress_small)", rf"min_n={MIN_N}\b"),
    ("AGENTS.md", "minimum n (Power BI DAX)", rf"< {MIN_N}\b"),
    (".github/copilot-instructions.md", "minimum n", rf"fewer than {MIN_N} people"),
    (".github/instructions/viz-python.instructions.md", "minimum n", rf"n < {MIN_N}\b"),
    (".github/instructions/viz-web.instructions.md", "minimum n", rf"fewer than {MIN_N} people"),
    (".github/instructions/viz-r.instructions.md", "minimum n", rf"n >= {MIN_N}\b"),
    ("docs/powerbi-setup.md", "minimum n (DAX)", rf"\[Headcount\] < {MIN_N}\b"),
    ("agents/mck-viz-rules.template.md", "minimum n", rf"fewer than {MIN_N} people"),
]

# (rule, regex no file may contain)
FORBIDDEN = [
    ("slide title 24 pt Bold Navy (superseded)", r"(?i)\b24\s*pt\W+bold\W+navy|bold\W+24\s*pt\W+navy|navy\W+bold\W+24\s*pt"),
    ("a slide title of 24 pt (now 26)", r"(?i)slide title[^\n]{0,40}?\b24\s*pt\b"),
    ("teal listed second (names)", r"(?i)(?<!bright )(?<!light )\bblue,\s*teal\b"),
    ("teal listed second (hex)", rf"(?i){CATEGORICAL[0]}[`'\",\s|]*{TEAL}"),
]


def test_tokens_have_the_settled_order():
    assert CAT_NAMES[:5] == ["blue", "navy", "bright blue", "teal", "mint"], \
        f"tokens.json categorical order is {CAT_NAMES}; update the docs (and this test) if that is intended"
    assert MIN_N == 10, f"mv.suppress_small defaults to min_n={MIN_N}; the rules say 10"


@pytest.mark.parametrize("rel,rule,pattern", REQUIRED, ids=[f"{f}: {r}" for f, r, _ in REQUIRED])
def test_file_states_rule_as_tokens_do(rel, rule, pattern):
    assert re.search(pattern, read(rel), flags=re.S), \
        f"{rel}: {rule} does not match tokens.json (expected /{pattern}/)"


@pytest.mark.parametrize("rule,pattern", FORBIDDEN, ids=[r for r, _ in FORBIDDEN])
@pytest.mark.parametrize("rel", FILES)
def test_file_has_no_superseded_wording(rel, rule, pattern):
    hits = [f"line {i}: {line.strip()[:120]}" for i, line in enumerate(read(rel).splitlines(), 1)
            if re.search(pattern, line)]
    assert not hits, f"{rel}: still says {rule}: " + "; ".join(hits)


@pytest.mark.parametrize("page", sorted(p.name for p in (REPO / "docs" / "cookbook").glob("*.md")))
def test_cookbook_page_has_no_24pt_bold_navy_title(page):
    rel = f"docs/cookbook/{page}"
    hits = [f"line {i}" for i, line in enumerate(read(rel).splitlines(), 1)
            if re.search(r"(?i)bold\s+24\s*pt", line)]
    assert not hits, f"{rel}: a headline or title at Bold 24 pt ({', '.join(hits)}); slide titles are Bold " \
                     f"{TITLE_PT} pt McKesson Blue {TITLE_HEX}, chart headlines SemiBold {HEAD_PT} pt navy"


def test_generated_rules_file_matches_tokens():
    rel = "dist/agents/mck-viz-rules.md"
    text = read(rel)
    assert re.search(hexes_in_order(6), text), f"{rel}: categorical hexes not in token order (run tokens/build.py)"
    assert f"Slide title: bold {TITLE_PT} pt, McKesson Blue `{TITLE_HEX}`" in text, \
        f"{rel}: slide title is not Bold {TITLE_PT} pt {TITLE_HEX} (run tokens/build.py)"
    assert f"semibold {HEAD_PT} pt" in text, f"{rel}: chart headline is not SemiBold {HEAD_PT} pt"
