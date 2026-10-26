"""mv.suggest: place a table in the chart decision tree and say which charts fit it, and why.

    s = mv.suggest(df)                       # print(s) for the report; s.shapes for the matches
    s = mv.suggest(df, measure="vol_attrition_pct", size="headcount")    # when the guesses need help

The tree is tokens/chooser.json (copied into the package as _chooser.json): three questions in order. 1. What is in the
data? (its shape, read from the columns here, not guessed) 2. What should the reader see? (the question the shape can
answer) 3. Start with the leaf's chart, and go further when one of its conditions holds in this data. Color comes from
what it encodes. The report ends with the Path line for the chart brief.

The column reading is a heuristic: it looks at names and values (a period column, a count, a rate, parts that add up
to 100, from/to columns, places, status words). Check the "Read the data as" lines, and pass category=, measure=,
size= or time= when a guess is wrong.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_tree() -> dict:
    for cand in (_HERE / "_chooser.json", *(p / "tokens" / "chooser.json" for p in _HERE.parents)):
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    raise FileNotFoundError("mckviz: _chooser.json is missing; run tokens/build.py")


TREE: dict = _load_tree()

_TIME_NAME = re.compile(r"(^|_)(year|yr|fy|fiscal_year|quarter|qtr|month|date|period|week)(_|$)", re.I)
_TIME_VALUE = re.compile(r"^(FY ?\d{2,4}|Q[1-4] ?(FY ?)?\d{2,4}|\d{4} ?Q[1-4]|(19|20)\d{2}(-\d{2}){0,2}|"
                         r"[A-Z][a-z]{2,8}\.? \d{4})$")
_PERIOD_TOKEN = re.compile(r"^((19|20)\d{2}|fy\d{2,4}|q[1-4]|h[12]|[a-z]{3}\d{2}|\d{2})$", re.I)
_COMPARE_TOKEN = re.compile(r"^(internal|external|market|us|benchmark|target|actual|plan|forecast|budget|prior|current|"
                            r"before|after|last|this)$", re.I)
_GEO_NAME = re.compile(r"(^|_)(state|country|county|fips|iso|iso_n3|iso_a3|region|metro|msa)(_|$)", re.I)
_DATE_NAME = re.compile(r"^(start|end|due|deadline|forecast|baseline|finish)(_|$)", re.I)
_STATUS_NAME = re.compile(r"^(status|rag)$", re.I)
_STATUS_WORDS = {"on_track", "on track", "at_risk", "at risk", "off_track", "off track", "not_started", "not started",
                 "done", "complete", "completed", "met", "missed", "slipped", "late", "moved", "upcoming", "due",
                 "green", "amber", "red"}
_COUNT_NAME = re.compile(r"(headcount|employees|people|workers|associates|count|moves|agents|candidates|hires|exits|"
                         r"roles|population|members|staff|fte|^n$|_n$)", re.I)
_RATE_NAME = re.compile(r"(pct|percent|rate|share|ratio|_idx|index|score)", re.I)
_TARGET_NAME = re.compile(r"(benchmark|target|goal|enterprise|average|avg|overall|company)", re.I)
_ORDERED_PARTS = re.compile(r"(unfav|neutral|fav|disagree|agree|low|medium|med|high|under|over|band|tier|level)", re.I)
_TOTAL_ROW = re.compile(r"^(total|all|overall|company|enterprise|mckesson)\b", re.I)


@dataclass
class Further:
    chart: str
    page: str
    helper: str | None
    when: str            # the trigger's wording
    holds: bool
    evidence: str = ""
    why: str = ""


@dataclass
class Leaf:
    ask: str
    type: str
    start: dict
    further: list[Further]
    avoid: str
    color: str           # the default color pattern's name
    color_switch: list[str] = field(default_factory=list)


@dataclass
class ShapeMatch:
    id: str
    label: str
    evidence: list[str]
    leaves: list[Leaf]


@dataclass
class Suggestion:
    rows: int
    roles: dict[str, str]
    shapes: list[ShapeMatch]
    cannot: list[str]

    def __str__(self) -> str:
        out = [f"Read the data as ({self.rows} rows):"]
        out += [f"  {c}: {r}" for c, r in self.roles.items()]
        if not self.shapes:
            out.append("No shape matched. Pass category=, measure=, size= or time=, or pick from "
                       "references/chart-decision-tree.md by hand.")
        for i, s in enumerate(self.shapes, 1):
            out.append("")
            out.append(f"{i}. {s.label}  [{s.id}]" + ("  (most likely)" if i == 1 else ""))
            out += [f"   because {e}" for e in s.evidence]
            for leaf in s.leaves:
                out.append(f"   Q: {leaf.ask}  ({leaf.type})")
                out.append(f"      Start with: {leaf.start['chart']}  -> cookbook/{leaf.start['page']}.md"
                           + (f"  ({leaf.start['helper']})" if leaf.start.get("helper") else ""))
                for f in [f for f in leaf.further if f.holds]:
                    out.append(f"      Go further: {f.chart}  -> cookbook/{f.page}.md"
                               + (f"  ({f.helper})" if f.helper else ""))
                    out.append(f"         because {f.evidence or f.when}")
                others = [f.chart for f in leaf.further if not f.holds]
                if others:
                    out.append(f"      (not indicated here: {'; '.join(others)})")
                out.append(f"      Avoid: {leaf.avoid}")
                out.append(f"      Color: {leaf.color}" + (f"; switch to {', '.join(leaf.color_switch)}"
                                                           if leaf.color_switch else ""))
        if self.cannot:
            out.append("")
            out.append("This data can't support:")
            out += [f"  - {c}" for c in self.cannot]
        out.append("")
        out.append("Record the choice in the chart brief:  Path: <shape> -> <question type> -> <chart> (start or "
                   "go further: <condition>);  Color: <pattern>")
        return "\n".join(out)

    __repr__ = __str__


# ------------------------------------------------------------------------------------------------ reading columns
def _is_numeric(s) -> bool:
    import pandas as pd

    return pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)


def _role(name: str, s) -> str:
    vals = s.dropna()
    text = vals.astype(str).str.strip()
    if _DATE_NAME.search(name):
        return "date"
    if _STATUS_NAME.search(name) or (len(text) and text.str.lower().isin(_STATUS_WORDS).mean() > 0.8):
        return "status"                                  # before geo: a "state" column of on_track/met is a status
    if name.lower() == "kind" or (len(text) and set(text.str.lower()) <= {"total", "delta", "subtotal"}):
        return "kind"
    if re.match(r"^(from|source)(_|$)", name, re.I):
        return "from"
    if re.match(r"^(to|target_stage|destination)(_|$)", name, re.I):
        return "to"
    if _GEO_NAME.search(name):
        return "geo"
    if _TIME_NAME.search(name) or (len(text) and text.str.match(_TIME_VALUE).mean() > 0.8 and not _is_numeric(s)):
        return "time"
    if _is_numeric(s):
        if len(vals) and set(vals.unique()) <= {0, 1} and vals.nunique() == 2:
            return "binary"
        return "numeric"
    if s.dtype == bool or (len(text) and set(text.str.lower()) <= {"true", "false"}):
        return "binary"
    return "category"


def _numeric_kind(name: str, s, rows: int) -> str:
    vals = s.dropna()
    if rows > 1 and vals.nunique() == 1:
        return "constant"
    if re.search(r"(^|_)rank", name, re.I):
        return "rank"
    if re.search(r"(^|_)per(_|$)", name, re.I):          # candidates_per_role, overtime_hrs_per_fte_wk
        return "rate"
    if _RATE_NAME.search(name):
        return "rate"
    if _COUNT_NAME.search(name) and (vals >= 0).all():
        return "count"
    return "measure"


def _pairs(cols: list[str]) -> list[tuple[str, str, str]]:
    """Numeric columns that differ by one name token that is a period or a comparison: (a, b, 'time'|'compare')."""
    found = []
    toks = {c: c.lower().split("_") for c in cols}
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            ta, tb = toks[a], toks[b]
            if len(ta) != len(tb):
                continue
            diff = [(x, y) for x, y in zip(ta, tb) if x != y]
            if len(diff) != 1:
                continue
            x, y = diff[0]
            if _PERIOD_TOKEN.match(x) and _PERIOD_TOKEN.match(y):
                found.append((a, b, "time"))
            elif _COMPARE_TOKEN.match(x) or _COMPARE_TOKEN.match(y):
                found.append((a, b, "compare"))
    return found


def _unit(name: str) -> str:
    parts = name.lower().split("_")
    return parts[-1] if len(parts) > 1 else ""


# ------------------------------------------------------------------------------------------------ the tree
def _leaves(shape_id: str, facts: dict[str, tuple[bool, str]]) -> list[Leaf]:
    shape = next(s for s in TREE["shapes"] if s["id"] == shape_id)
    colors, trig = TREE["colors"], TREE["triggers"]
    leaves = []
    for q in shape["questions"]:
        if q.get("needs") and not facts.get(q["needs"], (False, ""))[0]:
            continue
        further = []
        for f in q["further"]:
            holds, ev = facts.get(f["when"], (False, ""))
            further.append(Further(f["chart"], f["page"], f.get("helper"), trig[f["when"]], holds, ev, f.get("why", "")))
        switch = []
        for sw in q.get("color_switch", []):
            cond = trig.get(sw["when"], sw["when"])
            if sw["when"] in trig and not facts.get(sw["when"], (False, ""))[0]:
                continue
            switch.append(f"{colors[sw['use']]['name']} when {cond}")
        leaves.append(Leaf(q["ask"], q["type"], q["start"], further, q["avoid"], colors[q["color"]]["name"], switch))
    return leaves


def suggest(df, *, category: str | None = None, measure: str | None = None, size: str | None = None,
            time: str | None = None) -> Suggestion:
    """Read `df` (a pandas DataFrame), place it in the decision tree and return a Suggestion (print it)."""
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    rows = len(df)
    roles = {c: _role(str(c), df[c]) for c in df.columns}
    if time:
        roles[time] = "time"
    if category:
        roles[category] = "category"
    num = [c for c, r in roles.items() if r == "numeric"]
    kinds = {c: _numeric_kind(str(c), df[c], rows) for c in num}
    if size:
        kinds[size] = "count"
    if measure and measure in kinds and kinds[measure] in ("count", "constant"):
        kinds[measure] = "rate" if _RATE_NAME.search(measure) else "measure"
    shown = {c: (f"{roles[c]} ({kinds[c]})" if c in kinds else roles[c]) +
             (f", {df[c].nunique()} distinct" if roles[c] in ("category", "time", "geo") else "") for c in df.columns}

    cats = [c for c, r in roles.items() if r == "category"]
    times = [c for c, r in roles.items() if r == "time"]
    geos = [c for c, r in roles.items() if r == "geo"]
    binaries = [c for c, r in roles.items() if r == "binary"]
    counts = [c for c in num if kinds[c] == "count"]
    consts = [c for c in num if kinds[c] == "constant"]
    values = [c for c in num if kinds[c] in ("rate", "measure", "rank")]
    label = category or next((c for c in cats if df[c].nunique() == rows), None)
    target_cols = [c for c in num if _TARGET_NAME.search(str(c)) and c != measure]
    measure = measure or next((c for c in values if c not in target_cols), None) or (values[0] if values else None)
    size = size or next((c for c in counts if c != measure), None)

    # parts of a whole: two or more numeric columns that add up to 100 (or 1) on most rows
    parts: list[str] = []
    cand = [c for c in num if kinds[c] in ("rate", "measure")]
    if len(cand) >= 2:
        total = df[cand].sum(axis=1)
        if ((total - 100).abs() <= 2).mean() >= 0.9 or ((total - 1).abs() <= 0.02).mean() >= 0.9:
            parts = cand
    pairs = [p for p in _pairs([c for c in num]) if not (p[0] in parts and p[1] in parts)]
    period_levels = df[times[0]].nunique() if times else 0

    def rng(col):
        v = df[col].dropna().astype(float)
        return (float(v.min()), float(v.max())) if len(v) else (0.0, 0.0)

    facts: dict[str, tuple[bool, str]] = {}

    def fact(key, holds, evidence=""):
        facts[key] = (bool(holds), evidence if holds else "")

    ncat = df[label].nunique() if label else (df[cats[0]].nunique() if cats else rows)
    if measure:
        lo, hi = rng(measure)
        fact("clustered", lo > 0 and lo > 0.5 * hi, f"{measure} runs from {lo:g} to {hi:g}, far from zero")
        fact("wide_range", lo > 0 and hi / lo > 20, f"{measure}: the largest is {hi / lo:.0f}x the smallest"
             if lo > 0 else "")
        v = df[measure].dropna().astype(float)
        q1, q3 = v.quantile(0.25), v.quantile(0.75)
        fact("tight_spread", hi > lo and (q3 - q1) < 0.2 * (hi - lo) and len(v) >= 8,
             f"the middle half of {measure} spans {q3 - q1:.3g} of a {hi - lo:.3g} range")
        fact("rate_and_size", kinds.get(measure) == "rate" and size is not None,
             f"{measure} is a rate and {size} a count, so {measure} × {size} is an absolute amount")
    fact("many_categories", ncat > 12, f"{ncat} categories")
    fact("very_many_categories", ncat > 20, f"{ncat} categories")
    fact("few_categories", 0 < ncat <= 6, f"{ncat} categories")
    if size:
        slo, shi = rng(size)
        fact("has_size", slo > 0 and shi / slo >= 5, f"{size} runs from {slo:,.0f} to {shi:,.0f}")
    total_row = label is not None and df[label].astype(str).str.match(_TOTAL_ROW).any()
    bench = consts or [c for c in target_cols if c != measure]
    fact("has_benchmark", bool(bench) or total_row or any(_TARGET_NAME.search(str(c)) for c in df.columns),
         f"{', '.join(map(str, bench))} is the same on every row" if consts else
         ("a Total row" if total_row else f"a benchmark column ({', '.join(map(str, bench or df.columns[:1]))})"))
    fact("has_target", any(re.search(r"(target|goal)", str(c), re.I) for c in df.columns),
         f"a target column ({', '.join(str(c) for c in df.columns if re.search(r'(target|goal)', str(c), re.I))})")
    fact("parts_ordered", bool(parts) and sum(bool(_ORDERED_PARTS.search(c)) for c in parts) >= 2,
         f"the parts look ordered ({', '.join(parts)})")
    fact("many_parts", len(parts) > 5, f"{len(parts)} parts")
    fact("one_category", rows == 1, "one row")
    fact("parts_over_time", bool(parts) and bool(times), f"{', '.join(parts)} add up to 100 in each period")
    fact("ranks", any(kinds.get(c) == "rank" for c in num), "the values are ranks")
    gap_cols = [c for c in num if re.search(r"(gap|delta|diff|change|vs)", str(c), re.I)]
    fact("gap_is_point", bool(gap_cols) or any(k == "compare" for _, _, k in pairs),
         f"{', '.join(gap_cols)} is a difference" if gap_cols else "the pair is us vs. a comparison")
    series = [c for c in cats if c != label] if times else []
    nseries = df[series[0]].nunique() if series else len([c for c in values if c not in parts])
    fact("many_series", nseries > 4, f"{nseries} series")
    units = {_unit(str(c)) for c in values if c not in parts}
    fact("two_units", bool(times) and len(units) >= 2 and len(values) >= 2,
         f"{', '.join(str(c) for c in values[:2])} are in different units")
    fact("several_numbers", rows == 1 and len(num) >= 3, f"{len(num)} numbers in one row")
    fact("counts_not_rates", bool(geos) and measure is None and bool(counts),
         f"{', '.join(counts)} are counts")
    fact("more_than_three_sets", len(binaries) > 3, f"{len(binaries)} sets")
    fact("has_status_history", "status" in roles.values() and bool(times), "status recorded by period")
    if cats and not label and rows >= 30:
        g = df[cats[0]].nunique()
        fact("has_groups", 3 <= g <= 8, f"{g} groups in {cats[0]}")

    shapes: list[tuple[str, list[str]]] = []

    def add(shape_id, *evidence):
        if shape_id not in [s for s, _ in shapes]:
            shapes.append((shape_id, [e for e in evidence if e]))

    if any(r in ("date", "status") for r in roles.values()) and (cats or times):
        add("plans", f"{', '.join(c for c, r in roles.items() if r in ('date', 'status'))} are dates or status")
    if "kind" in roles.values():
        add("bridge", "a kind column marks totals and deltas")
    if "from" in roles.values() and "to" in roles.values():
        add("flows", "from and to columns")
    if len(binaries) >= 2 and (counts or rows > 1) and not times:
        add("sets", f"{len(binaries)} yes/no membership columns ({', '.join(binaries)})")
    if rows == 1:
        add("single", "one row")
    if times and period_levels >= 3 and "plans" not in [s for s, _ in shapes]:
        add("time", f"{times[0]} has {period_levels} periods" + (f", {nseries} series" if series else ""))
    if times and period_levels == 2:
        add("pairs", f"{times[0]} has two periods")
    if pairs:
        a, b, k = pairs[0]
        add("pairs", f"{a} and {b} are a {'before/after' if k == 'time' else 'comparison'} pair")
    if parts and not times:
        add("composition", f"{', '.join(parts)} add up to 100 on each row")
    if not times and not label and not geos and rows >= 30 and (values or measure) and len(cats) <= 1:
        add("people", f"{rows} rows" + (f" in {df[cats[0]].nunique()} groups" if cats else ""))
    if len([c for c in cats if c != label]) + (1 if label else 0) >= 2 and not times and not label and values:
        a, b = cats[:2]
        if not df.duplicated([a, b]).any():
            add("matrix", f"{a} × {b} with one value per pair")
    if geos and rows > 1:
        add("geo", f"{geos[0]} is a place column")
    if label and rows > 1:
        in_pairs = {c for a, b, _ in pairs for c in (a, b)}
        nvals = len([c for c in values if c not in parts and c not in target_cols and c not in in_pairs
                     and c not in gap_cols])
        if nvals >= 2:
            add("cat_measures", f"{nvals} measures per {label}")
        structural = {"plans", "bridge", "flows", "sets", "composition"} & {s for s, _ in shapes}
        if measure and measure not in parts and not structural:
            add("cat_measure", f"{measure} per {label}" + (f", {size} as a count" if size else ""))

    matches = [ShapeMatch(sid, next(s["label"] for s in TREE["shapes"] if s["id"] == sid), ev, _leaves(sid, facts))
               for sid, ev in shapes]
    ids = [s for s, _ in shapes]
    cannot = []
    if not ({"time", "pairs"} & set(ids)):
        cannot.append("change over time: it needs two or more periods")
    if not ({"cat_measures", "matrix", "people"} & set(ids)) and len(values) < 2:
        cannot.append("correlation: it needs two measures per category (a count can be the bubble size)")
    if not ({"composition", "bridge"} & set(ids)) and not facts.get("parts_over_time", (False,))[0]:
        cannot.append("part-to-whole: it needs parts that add up to a whole")
    if "people" not in ids:
        cannot.append("distribution: it needs one row per person or team")
    return Suggestion(rows, shown, matches, cannot)
