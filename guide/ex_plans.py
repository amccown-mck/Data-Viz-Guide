"""Plans and status exhibits: roadmap (Gantt), initiative tracker (HTML), milestone timeline, status history, scorecard
status column, process stages, best practice. Registered on import.

Status (RAG) colors come only from mv.STATUS and only mark status: workstreams and milestones, never data series.
Every status color is paired with its symbol (drawn inside the dot) and its word."""
from __future__ import annotations

import html as _html

import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

import mckviz as mv
from exhibits import ANNOT, ANTI, HTML, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, exhibit, fig_px, marker

ST = mv.STATUS                                       # key -> {"value", "symbol", "label"}
ORDER = ["off_track", "at_risk", "on_track", "not_started", "done"]       # exception first
WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def mi(s: str) -> int:
    """Month index from Apr 2025 (= 0), McKesson FY26 Q1."""
    y, m = map(int, s.split("-"))
    return (y - 2025) * 12 + m - 4


def mon(s: str, year: bool = False) -> str:
    return MON[int(s[5:]) - 1] + (f" {s[:4]}" if year else "")


# ------------------------------------------------------------------ data
PLAN = _csv("initiative_plan").fillna("")
MS = _csv("initiative_milestones").fillna("")
HIST = _csv("initiative_status_history")
PIPE = _csv("reskilling_pipeline")
AS_OF, AS_OF_M = "31 Mar 2026", "2026-03"
TODAY = mi(AS_OF_M) + 1                              # the line sits at the end of the as-of month
SPAN = 24                                            # FY26 Q1 .. FY27 Q4
PHASES = [("Foundations", 0, 9), ("Pilot", 9, 18), ("Scale", 18, 24)]
SHORTW = {"Workforce data platform": "Workforce data platform", "Skills inventory rollout": "Skills inventory",
          "SWP model refresh": "SWP model refresh", "Gen AI reskilling": "Gen AI reskilling",
          "Pharmacy technician career path": "Pharmacy tech career path", "DC scheduling pilot": "DC scheduling pilot",
          "Succession refresh": "Succession refresh"}
TINYW = {"Workforce data platform": "Data platform", "Skills inventory rollout": "Skills inventory",
         "SWP model refresh": "SWP refresh", "Gen AI reskilling": "Gen AI reskilling",
         "Pharmacy technician career path": "Pharm tech path", "DC scheduling pilot": "DC scheduling",
         "Succession refresh": "Succession"}

N_WS = len(PLAN)
COUNT = PLAN.status.value_counts().to_dict()
OFF = PLAN[PLAN.status == "off_track"]
DEP = OFF.depends_on.iloc[0]
assert len(OFF) == 2 and set(OFF.depends_on) == {DEP}              # headline: "two ... both waiting on"
EXC = PLAN[PLAN.status.isin(["off_track", "at_risk"])]
assert all((w == DEP) or (d == DEP) for w, d in zip(EXC.workstream, EXC.depends_on))    # "all tied to"
MOVED = MS[(MS.workstream == DEP) & (MS.state == "moved")].iloc[0]
SLIP = mi(MOVED.forecast) - mi(MOVED.due)
DUE = MS[MS.due.map(mi) < TODAY]
MS_DUE, MS_MET = len(DUE), int((DUE.state == "met").sum())
MISSED = MS[MS.state == "missed"]
NEXT = {}                                            # workstream -> next milestone row (first not met)
for w, g in MS.groupby("workstream", sort=False):
    left = g[g.state != "met"]
    NEXT[w] = left.iloc[0] if len(left) else None

ROLLUP = [(k, COUNT.get(k, 0)) for k in ORDER if COUNT.get(k, 0)]
_rollup_txt = ", ".join(f"{n} {ST[k]['label'].lower()}" for k, n in ROLLUP)

# status history: when the dependency turned and when its dependents went off track
_h = HIST.pivot(index="workstream", columns="month", values="status")
_MONTHS = list(_h.columns)


def _first(w, s):
    return next(m for m in _MONTHS if _h.loc[w, m] == s)


H_DEP_RISK = _first(DEP, "at_risk")
H_OFF = [(w, _first(w, "off_track")) for w in OFF.workstream]

# Data & AI reskilling academy stages (same flows as the Sankey in Relationships and flows)
_out = PIPE.groupby("from_stage").people.sum()
STAGES = [("Nominated", int(_out["Nominated"])), ("Enrolled", int(_out["Enrolled"])),
          ("Completed", int(_out["Completed"])),
          ("Redeployed", int(PIPE.people[PIPE.to_stage == "Redeployed to data role"].sum()))]

# scorecard: budget used vs. share of the plan's time elapsed
PLAN["elapsed_pct"] = [max(0, min(100, (TODAY - mi(s)) / (mi(e) + 1 - mi(s)) * 100)) for s, e in zip(PLAN.start, PLAN.end)]
PLAN["over"] = PLAN.budget_used_pct - PLAN.elapsed_pct >= 10                    # spending ahead of the calendar
OVER = PLAN[PLAN.over]
assert list(OVER.workstream) == [DEP]

TEXT.update(
    pl_headline=(f"{WORDS[len(OFF)].capitalize()} of {WORDS[N_WS]} workstreams are off track, both waiting on the "
                 f"skills inventory's Workday integration"),
    pl_subtitle=f"Workforce Innovation roadmap by workstream, FY26–FY27, with status as of {AS_OF}",
    pl_tr_headline=(f"{WORDS[len(EXC)].capitalize()} of {WORDS[N_WS]} workstreams need a decision, all because"
                    f" the Workday integration slipped {WORDS[SLIP]} months"),
    pl_tr_subtitle=f"Status, owner, next milestone and change since February, as of {AS_OF}",
    pl_n=str(N_WS), pl_off=str(len(OFF)), pl_exc=str(len(EXC)), pl_rollup=_rollup_txt,
    pl_ms_met=str(MS_MET), pl_ms_due=str(MS_DUE), pl_slip=str(SLIP),
    pl_moved_from=mon(MOVED.due), pl_moved_to=mon(MOVED.forecast),
    pl_h_dep=TINYW[DEP], pl_h_risk=mon(H_DEP_RISK),
    pl_h_off=" and ".join(f"{TINYW[w]} in {mon(m)}" for w, m in H_OFF),
    pl_h_off_m=" and ".join(mon(m) for _, m in H_OFF), pl_off_w=WORDS[len(OFF)],
    pl_over=TINYW[OVER.workstream.iloc[0]], pl_over_used=f"{OVER.budget_used_pct.iloc[0]:.0f}%",
    pl_over_elapsed=f"{OVER.elapsed_pct.iloc[0]:.0f}%",
    pl_redeploy=f"{STAGES[-1][1] / STAGES[0][1] * 100:.0f}%", pl_nominated=f"{STAGES[0][1]:,}",
    pl_n_statuses=str(len(ST)),
)


# ------------------------------------------------------------------ helpers (all drawing in px: 1 unit = 1 px)
def canvas(w=200, h=140):
    fig = fig_px(w, h)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def txt(ax, x, y, s, size=MINI, *, color=C.text, weight=400, ha="left", va="center", **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, **kw)


def sdot(ax, x, y, key, r=6.0, *, lw=None, z=6):
    """Status dot: the status color with its symbol drawn inside (so it survives any font), white or navy ink."""
    col = ST[key]["value"]
    ink = mv.text_on(col)
    lw = lw or max(1.0, r * 0.24)
    ax.add_patch(Circle((x, y), r, color=col, lw=0, zorder=z))
    s = r * 0.48
    kw = dict(color=ink, lw=lw, zorder=z + 1, solid_capstyle="butt", solid_joinstyle="miter")
    if key in ("on_track", "done"):
        ax.plot([x - s, x - s * 0.2, x + s], [y + s * 0.05, y - s * 0.7, y + s * 0.75], **kw)
    elif key == "off_track":
        ax.plot([x - s * 0.8, x + s * 0.8], [y - s * 0.8, y + s * 0.8], **kw)
        ax.plot([x - s * 0.8, x + s * 0.8], [y + s * 0.8, y - s * 0.8], **kw)
    elif key == "at_risk":
        ax.plot([x, x], [y - s * 0.2, y + s], **kw)
        ax.add_patch(Circle((x, y - s * 0.72), lw * 0.62, color=ink, lw=0, zorder=z + 1))
    else:                                                       # not started: a dash
        ax.plot([x - s * 0.7, x + s * 0.7], [y, y], **kw)


def status(ax, x, y, key, *, r=6.0, size=MINI, gap=5, bold=None, color=None):
    """Dot (color + symbol) and the word."""
    sdot(ax, x + r, y, key, r)
    b = key in ("off_track", "at_risk") if bold is None else bold
    return txt(ax, x + 2 * r + gap, y, ST[key]["label"], size, color=color or (C.headline if b else C.text),
               weight=600 if b else 400)


def diamond(ax, x, y, kind, ms=7.5, z=7):
    """Milestone marks: met = navy, filled; due = hollow; missed = an off-track cross; was = the original date."""
    if kind == "met":
        ax.plot(x, y, "D", ms=ms * 0.9, mfc=C.total, mec="white", mew=1, zorder=z)
    elif kind in ("upcoming", "moved"):
        ax.plot(x, y, "D", ms=ms * 0.9, mfc="white", mec=C.total, mew=1.3, zorder=z)
    elif kind == "was":
        ax.plot(x, y, "D", ms=ms * 0.9, mfc="white", mec=C.text_muted, mew=1, zorder=z)
    elif kind == "missed":
        ax.plot(x, y, "X", ms=ms * 1.05, mfc=ST["off_track"]["value"], mec="white", mew=0.8, zorder=z)


def arrow(ax, a, b, color=C.annotation, lw=1.0, z=6, head=3.2):
    ax.annotate("", b, a, arrowprops=dict(arrowstyle=f"-|>,head_length={head * 0.12:.2f},head_width={head * 0.065:.2f}",
                                          color=color, lw=lw, shrinkA=0, shrinkB=0), zorder=z)


def time_header(ax, x0, mw, y_q, *, size=MINI, phases=True, y_band=None, band_h=14, fy=True, y_fy=None):
    """Quarters (and fiscal years, and a phase band) over a monthly timeline that starts at FY26 Q1."""
    for q in range(SPAN // 3):
        txt(ax, x0 + (q * 3 + 1.5) * mw, y_q, f"Q{q % 4 + 1}", size, color=C.text_muted, ha="center")
    if fy:
        for k, name in enumerate(("FY26", "FY27")):
            txt(ax, x0 + (k * 12 + 6) * mw, y_fy, name, size, color=C.headline, weight=600, ha="center")
    if phases:
        for i, (name, a, b) in enumerate(PHASES):
            ax.add_patch(Rectangle((x0 + a * mw + (1 if a else 0), y_band - band_h / 2), (b - a) * mw - (1 if a else 0),
                                   band_h, color=C.context_light if i % 2 == 0 else C.grid, lw=0, zorder=1))
            txt(ax, x0 + a * mw + 5, y_band, name, size - 0.5, color=C.headline, zorder=2)


# ================================================================== ROADMAP (Gantt) anatomy
RM_ORDER = list(PLAN.workstream)                    # related work together: the dependency sits above its dependents


@exhibit
def plans_roadmap_anatomy():
    W, H = 620, 322
    fig, ax = canvas(W, H)
    x0, x1 = 252, 616
    mw = (x1 - x0) / SPAN
    X = lambda m: x0 + m * mw                                             # noqa: E731
    y_band, y_fy, y_q = 306, 287, 268
    rows_top, rowh = 242, 28
    n = len(PLAN)
    y_bot = rows_top - (n - 1) * rowh - 16
    time_header(ax, x0, mw, y_q, size=MINI, y_band=y_band, y_fy=y_fy)
    txt(ax, 0, y_q, "Workstream and owner", MINI - 0.5, color=C.text_muted)
    txt(ax, 160, y_q, "Status", MINI - 0.5, color=C.text_muted)
    ax.plot([0, x1], [y_q - 9, y_q - 9], color=C.axis, lw=0.7)
    for q in range(1, SPAN // 3):                                            # quarter rules, light
        ax.plot([X(q * 3)] * 2, [y_bot, y_q - 9], color=C.grid, lw=0.7, zorder=0)
    for i, r in PLAN.iterrows():
        y = rows_top - i * rowh
        hot = r.status == "off_track"
        txt(ax, 0, y + 5, SHORTW[r.workstream], LABEL - 0.5, color=C.headline if hot else C.text,
            weight=600 if hot else 400)
        txt(ax, 0, y - 7.5, r.owner, MINI - 1, color=C.text_muted)
        status(ax, 160, y, r.status, r=6, size=MINI)
        a, b = mi(r.start), mi(r.end) + 1
        col = C.focus if hot else (C.context_light if r.status == "not_started" else C.context)
        ax.add_patch(Rectangle((X(a), y - 5), (b - a) * mw, 10, color=col, lw=0, zorder=3))
        for _, m in MS[MS.workstream == r.workstream].iterrows():
            if m.state == "moved":
                xa, xb = X(mi(m.due) + 0.5), X(mi(m.forecast) + 0.5)
                diamond(ax, xa, y, "was")
                arrow(ax, (xa + 5, y), (xb - 5.5, y), lw=1.1)
                diamond(ax, xb, y, "moved")
                txt(ax, (xa + xb) / 2, y + 12, f"Moved {mon(m.due)} to {mon(m.forecast)}", MINI - 1, color=C.annotation,
                    ha="center", weight=600, zorder=9, bbox=dict(fc="white", ec="none", pad=0.6))
                dep_x, dep_y = xb, y
            else:
                diamond(ax, X(mi(m.due) + 0.5), y, m.state)
    # dependency: the moved integration holds up both off-track workstreams
    ys = [rows_top - RM_ORDER.index(w) * rowh for w in OFF.workstream]
    arrow(ax, (dep_x, dep_y - 6.5), (dep_x, ys[0] + 5.5), lw=1.1)
    arrow(ax, (dep_x, ys[0] - 5.5), (dep_x, ys[1] + 5.5), lw=1.1)
    swp_end = X(mi(OFF.end.iloc[0]) + 1)
    txt(ax, swp_end + 6, ys[0], "Both wait on\nskills data", MINI - 1, color=C.annotation, weight=600,
        linespacing=1.1)
    # today
    ax.plot([X(TODAY)] * 2, [y_bot, y_q - 9], color=C.total, lw=1.1, ls=(0, (3, 2.5)), zorder=8)
    txt(ax, X(TODAY), y_bot - 8, f"Today, {AS_OF}", MINI - 1, color=C.annotation, ha="center", weight=600)
    # milestone key, bottom left
    kx, ky = 0, 13
    for kind, lab in (("met", "Met"), ("upcoming", "Due"), ("missed", "Missed"), ("was", "Original date")):
        diamond(ax, kx + 4, ky, kind, ms=7)
        t = txt(ax, kx + 11, ky, lab, MINI - 1, color=C.text)
        kx += 13 + len(lab) * 5.6 + 10
    # anatomy markers
    marker(ax, (X(0), y_band), 3, offset=(-14, 0))
    marker(ax, (128, y_q), 4)
    marker(ax, (204, y_q), 5)
    pr = rows_top - RM_ORDER.index("Pharmacy technician career path") * rowh
    marker(ax, (X(mi("2026-12") + 1), pr), 6, offset=(12, 0))
    marker(ax, (kx - 4, ky), 7, offset=(10, 0))
    marker(ax, (X(TODAY), y_bot - 8), 8, offset=(-62, 0))
    marker(ax, (dep_x, (ys[0] + ys[1]) / 2), 9, offset=(-14, 0))
    alt = (TEXT["pl_headline"] + f". Gantt chart of {N_WS} workstreams across FY26–FY27: {TEXT['pl_rollup']}. "
           f"The skills inventory's Workday integration moved from {mon(MOVED.due)} to {mon(MOVED.forecast)} 2026; "
           f"the SWP model refresh and Gen AI reskilling have each missed a milestone waiting on it.")
    return fig, alt


# ================================================================== TRACKER (HTML table, .mck-table)
def _chip(key, size=16):
    col = ST[key]["value"]
    return (f'<span style="display:inline-grid;place-items:center;width:{size}px;height:{size}px;border-radius:50%;'
            f'background:{col};color:{mv.text_on(col)};font-size:{size * 0.62:.0f}px;font-weight:700;line-height:1;'
            f'flex:none" aria-hidden="true">{ST[key]["symbol"]}</span>')


def _status_cell(key, bold):
    w = f'<b style="font-weight:600;color:var(--mck-text-headline)">{ST[key]["label"]}</b>' if bold else ST[key]["label"]
    return f'<span style="display:inline-flex;align-items:center;gap:6px;white-space:nowrap">{_chip(key)}{w}</span>'


def _mk(n, ml=6):
    return f'<span class="mk" style="margin-left:{ml}px">{n}</span>'


def _next_text(w):
    m = NEXT[w]
    if m is None:
        return "All milestones met"
    if m.state == "missed":
        return (f'{_html.escape(m.milestone)}<br><span style="color:var(--mck-text-headline);font-weight:600">'
                f'Missed {mon(m.due)}; no new date</span>')
    if m.state == "moved":
        return (f'{_html.escape(m.milestone)}<br><span style="color:var(--mck-text-headline);font-weight:600">'
                f'{mon(m.forecast)} 2026 (was {mon(m.due)})</span>')
    return f'{_html.escape(m.milestone)}<br><span style="color:var(--mck-text-muted)">{mon(m.due, year=True)}</span>'


def _tracker() -> str:
    d = PLAN.assign(o=PLAN.status.map(ORDER.index)).sort_values(["o", "start"], kind="stable")
    pad = "padding:4px 8px 4px 0;vertical-align:top"
    heads = [("Status", _mk(4)), ("Workstream, owner", _mk(6)), ("Next milestone", _mk(7)),
             ("What changed", _mk(8))]
    th = "".join(f'<th scope="col" style="{pad}">{h}{m}</th>' for h, m in heads)
    rows = []
    for i, (_, r) in enumerate(d.iterrows()):
        exc = r.status in ("off_track", "at_risk")
        name = (f'<span style="font-weight:{600 if exc else 400};color:var(--mck-text-{"headline" if exc else "primary"})">'
                f'{_html.escape(r.workstream)}</span>{_mk(5) if i == 0 else ""}'
                f'<br><span style="color:var(--mck-text-muted);font-size:11px">{_html.escape(r.owner)}</span>')
        rows.append(f'<tr><td style="{pad};padding-top:5px">{_status_cell(r.status, exc)}</td>'
                    f'<th scope="row" style="{pad};min-width:0;font-weight:400">{name}</th>'
                    f'<td style="{pad}">{_next_text(r.workstream)}</td>'
                    f'<td style="{pad};color:var(--mck-text-primary)">{_html.escape(r.what_changed)}</td></tr>')
    roll = "".join(f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:8px;white-space:nowrap">'
                   f'{_chip(k, 14)}<b style="font-weight:700;color:var(--mck-text-headline)">{n}</b> {ST[k]["label"].lower()}'
                   f'</span>' for k, n in ROLLUP)
    return (f'<div style="font-size:12.5px;margin:0 0 6px;display:flex;flex-wrap:wrap;row-gap:4px;align-items:center">'
            f'<span style="font-weight:600;color:var(--mck-text-headline);margin-right:8px">{N_WS} workstreams</span>'
            f'{roll}{_mk(3, 0)}</div>'
            f'<div class="ex-wrap"><table class="mck-table" style="font-size:11.5px;line-height:1.3;margin:0">'
            f'<colgroup><col style="width:17%"><col style="width:28%"><col style="width:26%"><col></colgroup>'
            f"<thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")


HTML["plans_tracker"] = _tracker()


# ================================================================== VARIANTS (300 x 190)
@exhibit
def plans_var_milestones():
    fig, ax = canvas(300, 190)
    x0, x1 = 8, 292
    mw = (x1 - x0) / SPAN
    X = lambda m: x0 + m * mw                                             # noqa: E731
    yl = 102
    ax.plot([x0, x1], [yl, yl], color=C.axis, lw=1.2, zorder=1)
    for q in range(SPAN // 3 + 1):
        ax.plot([X(q * 3)] * 2, [yl - 3, yl + 3], color=C.axis, lw=0.8)
    for k, name in enumerate(("FY26", "FY27")):
        txt(ax, X(k * 12 + 6), 10, name, MINI - 1.5, color=C.headline, weight=600, ha="center")
        ax.plot([X(k * 12) + 2, X(k * 12 + 12) - 2], [20, 20], color=C.grid, lw=0.8)
    g = MS[MS.workstream == DEP].reset_index(drop=True)
    ax.plot([X(TODAY)] * 2, [26, 172], color=C.total, lw=1, ls=(0, (3, 2.5)), zorder=2)
    txt(ax, X(TODAY), 180, "Today", MINI - 2, color=C.annotation, ha="center", weight=600)
    levels = [46, -22, 22, -46]                                            # staggered so labels never collide
    for i, m in g.iterrows():
        lv = levels[i % len(levels)]
        up = lv > 0
        if m.state == "moved":
            xa, xb = X(mi(m.due) + 0.5), X(mi(m.forecast) + 0.5)
            diamond(ax, xa, yl, "was", ms=8)
            arrow(ax, (xa + 5, yl), (xb - 6, yl), lw=1.1)
            diamond(ax, xb, yl, "moved", ms=9)
            x, when = xb, f"{mon(m.forecast)} 2026 (was {mon(m.due)})"
        else:
            x, when = X(mi(m.due) + 0.5), mon(m.due, year=True)
            diamond(ax, x, yl, m.state, ms=9)
        ty = yl + lv
        ax.plot([x, x], [yl + (6 if up else -6), ty + (-2 if up else 2)], color=C.grid, lw=0.8, zorder=0)
        ha = "left" if x < 100 else ("right" if x > 220 else "center")
        txt(ax, x, ty + (11 if up else -2), m.milestone, MINI - 1.5, color=C.headline, weight=600, ha=ha,
            va="bottom" if up else "top", bbox=dict(fc="white", ec="none", pad=0.3), zorder=3)
        txt(ax, x, ty + (0 if up else -14), when, MINI - 2, color=C.text, ha=ha, va="bottom" if up else "top",
            bbox=dict(fc="white", ec="none", pad=0.3), zorder=3)
    met = int((g.state == "met").sum())
    return fig, (f"Milestone timeline of the skills inventory rollout, FY26–FY27: {met} of {len(g)} met; the Workday "
                 f"integration moved from {mon(MOVED.due)} to {mon(MOVED.forecast)} 2026; today line at {AS_OF}.")


@exhibit
def plans_var_history():
    fig, ax = canvas(300, 190)
    names_w, cw = 90, 24
    cx0 = names_w + 12
    top, rh = 158, 21
    for j, m in enumerate(_MONTHS):
        txt(ax, cx0 + j * cw, top + 18, mon(m), MINI - 2, color=C.text_muted, ha="center")
    txt(ax, cx0 + len(_MONTHS) * cw - 4, top + 18, "Now", MINI - 2, color=C.text_muted)
    for i, w in enumerate(RM_ORDER):
        y = top - i * rh
        hot = w in set(OFF.workstream)
        txt(ax, 0, y, TINYW[w], MINI - 1.5, color=C.headline if hot else C.text, weight=600 if hot else 400)
        for j, m in enumerate(_MONTHS):
            sdot(ax, cx0 + j * cw, y, _h.loc[w, m], r=6.2)
        now = _h.loc[w, _MONTHS[-1]]
        txt(ax, cx0 + len(_MONTHS) * cw - 4, y, ST[now]["label"], MINI - 2, color=C.headline if hot else C.text,
            weight=600 if hot else 400)
        if i:
            ax.plot([0, 300], [y + rh / 2, y + rh / 2], color=C.grid, lw=0.5, zorder=0)
    return fig, (f"Monthly status, Oct 2025–Mar 2026, one row per workstream, a symbol in every cell: "
                 f"{TINYW[DEP]} at risk from {mon(H_DEP_RISK)}; {TEXT['pl_h_off']} went off track.")


@exhibit
def plans_var_scorecard():
    fig, ax = canvas(300, 190)
    d = PLAN.assign(o=PLAN.status.map(ORDER.index)).sort_values(["o", "start"], kind="stable").reset_index(drop=True)
    top, rh = 150, 20.5
    cx_m, bx0, bw, sx = 120, 132, 64, 232
    hs = MINI - 2.5
    txt(ax, cx_m, top + 22, "Milestones\nmet / due", hs, color=C.headline, weight=700, ha="right", va="center",
        linespacing=1.05)
    txt(ax, bx0, top + 22, "Budget used\n(| = time elapsed)", hs, color=C.headline, weight=700, linespacing=1.05)
    txt(ax, sx, top + 22, "Status", hs, color=C.headline, weight=700)
    ax.plot([0, 300], [top + 11, top + 11], color=C.axis, lw=0.7)
    ax.plot([sx - 7, sx - 7], [top - len(d) * rh + rh / 2 + 1, top + 30], color=C.grid, lw=0.8)
    for i, r in d.iterrows():
        y = top - i * rh
        exc = r.status in ("off_track", "at_risk")
        tc = C.headline if exc else C.text
        txt(ax, 0, y, TINYW[r.workstream], MINI - 2, color=tc, weight=600 if exc else 400)
        g = MS[(MS.workstream == r.workstream) & (MS.due.map(mi) < TODAY)]
        txt(ax, cx_m, y, f"{int((g.state == 'met').sum())} / {len(g)}" if len(g) else "–", MINI - 2, color=tc,
            ha="right")
        ax.add_patch(Rectangle((bx0, y - 4), bw, 8, color=C.grid, lw=0))
        ax.add_patch(Rectangle((bx0, y - 4), bw * r.budget_used_pct / 100, 8,
                               color=C.negative if r.over else C.context, lw=0))
        if r.elapsed_pct > 0:
            ax.plot([bx0 + bw * r.elapsed_pct / 100] * 2, [y - 6.5, y + 6.5], color=C.total, lw=1.3)
        txt(ax, bx0 + bw + 4, y, f"{r.budget_used_pct:.0f}%", MINI - 2.5,
            color=C.negative_text if r.over else C.text, weight=600 if r.over else 400)
        status(ax, sx, y, r.status, r=5, size=MINI - 2, gap=4)
        if i:
            ax.plot([0, 300], [y + rh / 2, y + rh / 2], color=C.grid, lw=0.5, zorder=0)
    return fig, (f"Scorecard of {N_WS} workstreams, exceptions first: milestones met of due, budget used against "
                 f"time elapsed ({TEXT['pl_over']} has used {TEXT['pl_over_used']} of its budget in "
                 f"{TEXT['pl_over_elapsed']} of its time, in orange), and a status column with symbol and word.")


@exhibit
def plans_var_steps():
    fig, ax = canvas(300, 190)
    n = len(STAGES)
    cols = [mv.STEPS[i] for i in np.round(np.linspace(0, len(mv.STEPS) - 1, n)).astype(int)]
    w, tip, gap, y0, h = 300 / n, 11, 3, 82, 56
    for i, ((name, v), col) in enumerate(zip(STAGES, cols)):
        x = i * w
        pts = [(x, y0), (x + w - tip - gap, y0), (x + w - gap, y0 + h / 2), (x + w - tip - gap, y0 + h), (x, y0 + h)]
        if i:
            pts += [(x + tip, y0 + h / 2)]
        ax.add_patch(Polygon(pts, closed=True, color=col, lw=0))
        ink = mv.text_on(col)
        cx = x + (w - gap + (tip if i else 0)) / 2 - 3
        txt(ax, cx, y0 + h / 2 + 8, f"{v:,}", MINI + 2, color=ink, weight=700, ha="center")
        txt(ax, cx, y0 + h / 2 - 9, "people", MINI - 2.5, color=ink, ha="center")
        txt(ax, x + 2, y0 + h + 12, f"{i + 1} {name}", MINI - 1.5, color=C.headline, weight=600)
        txt(ax, x + 2, y0 - 12, f"{v / STAGES[0][1] * 100:.0f}% of\nnominees" if i else "Start", MINI - 2.5,
            color=C.text, va="top", linespacing=1.1)
    return fig, (f"Four flat chevrons, blue to green, for the Data & AI reskilling academy stages: "
                 + ", ".join(f"{s} {v:,}" for s, v in STAGES) + f"; {TEXT['pl_redeploy']} of nominees redeployed.")


# ================================================================== BEST PRACTICE (200 x 140)
_BP = PLAN.assign(o=PLAN.status.map(ORDER.index))
_BP5 = _BP[_BP.status != "done"].head(5)                                  # five rows, plan order (unsorted)


def _rows(ax, d, *, y0=112, rh=21, x_name=8, x_stat=112, mode="fix", size=MINI - 2):
    for i, (_, r) in enumerate(d.iterrows()):
        y = y0 - i * rh
        exc = r.status in ("off_track", "at_risk")
        if mode == "alone":                                               # color only: no symbol, no word
            ax.add_patch(Circle((x_stat + 6, y), 5.5, color=ST[r.status]["value"], lw=0))
            txt(ax, x_name, y, TINYW[r.workstream], size, color=C.text)
        else:
            txt(ax, x_name, y, TINYW[r.workstream], size, color=C.headline if exc else C.text,
                weight=600 if exc else 400)
            status(ax, x_stat, y, r.status, r=5.5, size=size, gap=4)
        if i:
            ax.plot([x_name, 196], [y + rh / 2, y + rh / 2], color=C.grid, lw=0.6, zorder=0)


def _bp(kind):
    fig, ax = canvas()
    if kind == "alone_avoid":
        _rows(ax, _BP5, mode="alone", x_stat=140)
    elif kind == "alone_fix":
        _rows(ax, _BP5)
    elif kind in ("data_avoid", "data_fix"):                              # skills-profile completion by function
        sp = _csv("skills_profile_completion")
        sp["pct"] = sp.profiles_mar26 / sp.employees * 100
        sp = sp.sort_values("pct")
        tgt = int(sp.target_pct.iloc[0])
        y = 108 - np.arange(len(sp)) * 21
        for yy, (_, r) in zip(y, sp.iterrows()):
            if kind == "data_avoid":
                col = (ST["on_track"]["value"] if r.pct >= tgt else ST["at_risk"]["value"] if r.pct >= 65
                       else ST["off_track"]["value"])
            else:
                col = C.focus if r.pct == sp.pct.min() else C.context
            ax.add_patch(Rectangle((72, yy - 6.5), r.pct * 1.05, 13, color=col, lw=0))
            txt(ax, 66, yy, r.function, MINI - 2.5, color=C.text, ha="right")
            txt(ax, 72 + r.pct * 1.05 - 3, yy, f"{r.pct:.0f}%", MINI - 2.5, color=mv.text_on(col), ha="right",
                zorder=4)
        if kind == "data_fix":
            xt = 72 + tgt * 1.05
            ax.plot([xt, xt], [y[-1] - 11, y[0] + 11], color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=0.5)
            txt(ax, xt, y[0] + 15, f"Target {tgt}%", MINI - 3, color=C.annotation, ha="center")
    elif kind == "flat_avoid":                                            # the template look: pills, shadows, rounding
        ax.add_patch(FancyBboxPatch((10, 116), 180, 14, boxstyle="round,pad=0,rounding_size=7", fc=C.headline, ec="none"))
        txt(ax, 100, 123, "WORKSTREAM STATUS", MINI - 3, color="white", weight=700, ha="center")
        for i, (_, r) in enumerate(_BP5.head(4).iterrows()):
            y = 94 - i * 24
            txt(ax, 12, y, TINYW[r.workstream], MINI - 2.5, color=C.text)
            ax.add_patch(FancyBboxPatch((118, y - 9.5), 72, 14, boxstyle="round,pad=0,rounding_size=7", fc="#9A9A9A",
                                        ec="none", alpha=0.45))
            ax.add_patch(FancyBboxPatch((116, y - 7), 72, 14, boxstyle="round,pad=0,rounding_size=7",
                                        fc=ST[r.status]["value"], ec="white", lw=1))
            txt(ax, 152, y, ST[r.status]["label"].upper(), MINI - 3.5, color=mv.text_on(ST[r.status]["value"]),
                weight=700, ha="center")
    elif kind == "flat_fix":
        ax.plot([8, 196], [124, 124], color=C.axis, lw=0.7)
        txt(ax, 8, 131, "Workstream", MINI - 2.5, color=C.text_muted)
        txt(ax, 112, 131, "Status", MINI - 2.5, color=C.text_muted)
        _rows(ax, _BP5.head(4), y0=108, rh=24)
    elif kind == "exception_avoid":                                       # every row lit, plan order
        for i, (_, r) in enumerate(_BP.iterrows()):
            y = 124 - i * 18
            col = ST[r.status]["value"]
            ax.add_patch(Rectangle((6, y - 8), 188, 16, color=col, lw=0))
            txt(ax, 12, y, TINYW[r.workstream], MINI - 2.5, color=mv.text_on(col), weight=600)
    elif kind == "exception_fix":
        d = _BP.sort_values(["o", "start"], kind="stable")
        exc = d[d.status.isin(["off_track", "at_risk"])]
        _rows(ax, exc, y0=118, rh=22)
        rest = d[~d.status.isin(["off_track", "at_risk"])]
        ax.plot([8, 196], [118 - len(exc) * 22 + 11] * 2, color=C.grid, lw=0.6)
        y = 118 - len(exc) * 22 - 4
        txt(ax, 8, y, f"{len(rest)} more on plan", MINI - 2, color=C.text, weight=600, va="top")
        parts = [f"{(rest.status == k).sum()} {ST[k]['label'].lower()}" for k in ORDER if (rest.status == k).any()]
        txt(ax, 8, y - 15, ", ".join(parts), MINI - 2.5, color=C.text_muted, va="top")
    return fig


for _k, _alt in {"alone_avoid": "Status shown only as red, amber and green dots, with no symbol or word.",
                 "alone_fix": "Each status dot carries its symbol, with the word beside it.",
                 "data_avoid": "Bars of skills-profile completion colored red, amber and green by value.",
                 "data_fix": "The same bars grey, the lowest in blue, with a labelled target line.",
                 "flat_avoid": "Rounded status pills with drop shadows under a rounded header.",
                 "flat_fix": "Flat rows: a small status dot with symbol and word, hairlines only.",
                 "exception_avoid": "Every row filled with its status color, in plan order.",
                 "exception_fix": "Off-track and at-risk rows first; the rest summarised in one grey line."}.items():
    EXHIBITS[f"plans_bp_{_k}"] = (lambda k=_k, a=_alt: (_bp(k), a))


# ------------------------------------------------------------------ roadmap best practice (200 x 140)
_GW = ["Workforce data platform", "Skills inventory rollout", "SWP model refresh", "Gen AI reskilling"]


def _mini_gantt(ax, *, colors=None, today=True, slip="show", names=True, x0=72, x1=196, top=104, rh=24, ms=True,
                rows=None, dsize=6.5):
    rows = rows or _GW
    mw = (x1 - x0) / SPAN
    X = lambda m: x0 + m * mw                                             # noqa: E731
    for k, name in enumerate(("FY26", "FY27")):
        txt(ax, X(k * 12 + 6), top + 20, name, MINI - 2.5, color=C.headline, weight=600, ha="center")
    ax.plot([X(12)] * 2, [top - (len(rows) - 1) * rh - 12, top + 14], color=C.grid, lw=0.7, zorder=0)
    for i, w in enumerate(rows):
        r = PLAN[PLAN.workstream == w].iloc[0]
        y = top - i * rh
        if names:
            txt(ax, x0 - 5, y, TINYW[w], MINI - 2.5, color=C.headline if r.status == "off_track" else C.text,
                weight=600 if r.status == "off_track" and colors is None else 400, ha="right")
        a, b = mi(r.start), mi(r.end) + 1
        col = colors[i] if colors else (C.focus if r.status == "off_track" else C.context)
        ax.add_patch(Rectangle((X(a), y - 4.5), (b - a) * mw, 9, color=col, lw=0, zorder=2))
        if not ms:
            continue
        for _, m in MS[MS.workstream == w].iterrows():
            if m.state == "moved":
                xa, xb = X(mi(m.due) + 0.5), X(mi(m.forecast) + 0.5)
                if slip == "show":
                    diamond(ax, xa, y, "was", ms=dsize - 0.5)
                    arrow(ax, (xa + 3.5, y), (xb - 4, y), lw=0.9, head=2.6)
                    txt(ax, xb, y - 12, f"{mon(m.forecast)}, was {mon(m.due)}", MINI - (2 if dsize >= 8 else 3), color=C.annotation,
                        ha="center", weight=600, zorder=9, bbox=dict(fc="white", ec="none", pad=0.4))
                diamond(ax, xb, y, "upcoming", ms=dsize)
            else:
                diamond(ax, X(mi(m.due) + 0.5), y, m.state, ms=dsize)
    if today:
        yb = top - (len(rows) - 1) * rh - 12
        ax.plot([X(TODAY)] * 2, [yb, top + 12], color=C.total, lw=1, ls=(0, (2.5, 2)), zorder=6)
        txt(ax, X(TODAY), yb - 7, "Today", MINI - 3, color=C.annotation, ha="center", weight=600)
    return X


def _bp_rm(kind):
    fig, ax = canvas()
    if kind == "colors_avoid":
        _mini_gantt(ax, colors=ANTI["rainbow"][:4], names=False, x0=8, today=False, ms=False, top=110)
        for i, w in enumerate(_GW):                                        # a legend at the bottom
            x, y = 10 + (i % 2) * 94, 22 - (i // 2) * 13
            ax.add_patch(Rectangle((x, y - 3.5), 7, 7, color=ANTI["rainbow"][i], lw=0))
            txt(ax, x + 10, y, TINYW[w], MINI - 3.5, color=C.text)
    elif kind == "colors_fix":
        _mini_gantt(ax, today=False, ms=False, top=100, rh=26)
    elif kind == "tasks_avoid":                                           # schematic: 14 task bars, seeded
        rng = np.random.default_rng(7)
        mw = 184 / SPAN
        for i in range(14):
            a = int(rng.integers(0, 18))
            b = min(SPAN, a + int(rng.integers(2, 7)))
            y = 128 - i * 8.6
            ax.add_patch(Rectangle((8 + a * mw, y - 3), (b - a) * mw, 6, color=C.focus, lw=0))
            lx = 6 + a * mw
            txt(ax, lx if lx > 34 else 10 + b * mw, y, f"Task {i + 1}.{int(rng.integers(1, 9))}", MINI - 4.5,
                color=C.text_muted, ha="right" if lx > 34 else "left")
    elif kind == "tasks_fix":
        _mini_gantt(ax, today=False, top=100, rh=26)
    elif kind == "today_avoid":
        _mini_gantt(ax, today=False, slip="hide", top=100, rh=26)
    elif kind == "today_fix":
        _mini_gantt(ax, slip="hide", top=106, rh=24)
    elif kind in ("slip_avoid", "slip_fix"):
        _mini_gantt(ax, slip="hide" if kind == "slip_avoid" else "show", top=96, rh=46, dsize=8,
                    rows=["Skills inventory rollout", "SWP model refresh"])
    return fig


for _k, _alt in {"colors_avoid": "Gantt bars in four bright colors decoded through a legend at the bottom.",
                 "colors_fix": "Gantt bars grey, the off-track workstream blue, names on the rows.",
                 "tasks_avoid": "Fourteen thin task bars with tiny labels.",
                 "tasks_fix": "Four workstream bars with milestones as diamonds.",
                 "today_avoid": "A roadmap with no today line.",
                 "today_fix": "The same roadmap with a labelled today line.",
                 "slip_avoid": "A milestone shown only at its new date, with no trace of the move.",
                 "slip_fix": "The original date as a grey diamond, an arrow to the new date, 'was Mar'."}.items():
    EXHIBITS[f"plans_bprm_{_k}"] = (lambda k=_k, a=_alt: (_bp_rm(k), a))
