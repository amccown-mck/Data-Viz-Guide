"""Sam restyle (direction A rendering, same rig) + final Spark mascot.

python3 restyle.py            -> board-restyle.html/.png, final/sam.svg, final/spark.svg, board-final.html/.png
python3 restyle.py --hair pony --outfit blue --eyewear frames   -> swap the final look

Hair, outfit and eyewear are separate groups (.hair-back, .hair-front, .outfit, .eyewear),
each generated from a preset, so a variant swap is one argument.
"""
import math
import os
import subprocess
import sys

import build as B
from build import (BLUE, NAVY, DEEP, SKY, AZURE, TEAL, MINT, LIME, SAND, SAND2, WGREY, ORANGE, WHITE,
                   SKIN, SKIN_SH, BLUSH, MOUTH, TONGUE, SH_L, SH_R, EL_L, EL_R, HD_L, HD_R, EYE_L, EYE_R,
                   capsule, star_path, sparkle_path, ik)

HERE = os.path.dirname(os.path.abspath(__file__))
FINAL = os.path.join(HERE, "final")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

GOLD, GOLD_SH = "#E4B24C", "#B8862C"
LIP, LIP_D = "#C4566B", "#8E3446"
LASH = "#24161B"
FONT = "'Libre Franklin', LF, Arial, sans-serif"

HAIRS = {
    "waves": dict(base="#3A221F", tip="#3A221F", hi="#4A2B26", brow="#3A221F")  # one color: caramel tips blended into the camel blazer,
    "pony":  dict(base="#1C1317", tip="#1C1317", hi="#4A3640", brow="#1C1317"),
    "lob":   dict(base="#6B2B1A", tip="#6B2B1A", hi="#A24E2D", brow="#4A2016"),
}
OUTFITS = {
    "camel": dict(blazer="#C98A4B", sleeve="#B67A3F", shade="#A96D33", lapel="#B67A3E", inner=WHITE, inner_kind="tee",
                  pants=NAVY, pants_sh="#0E2747", shoe="sneaker"),
    "blue":  dict(blazer=BLUE, sleeve="#0A6699", shade="#004873", lapel=DEEP, inner=LIME, inner_kind="cami",
                  pants="#F3EEE4", pants_sh="#D9D1C2", shoe="flat"),
    "cream": dict(blazer="#F4EEE2", sleeve="#E8DFCE", shade="#DDD3C1", lapel="#E7DECF", inner=DEEP, inner_kind="tee",
                  pants="#B98250", pants_sh="#9B6939", shoe="sneaker"),
}


def stroke(d, w, color, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def m(*moods):
    return "m " + " ".join(f"m-{x}" for x in moods)


# ---------------------------------------------------------------- poses
# Angles in degrees. Left arm: + swings outward (to the viewer's left); right arm mirrored.
# Hand-tuned so every pose is reached by swinging outward/up from rest, never through the body.
REST = (12, -6, -12, 6)
POSES = {
    # name: (lu, lf, ru, rf); None = that arm keeps rest (so one-arm poses combine)
    "type":   (10, -65, -10, 65),        # hands behind the laptop lid
    "coffee": (None, None, -50, 134),    # mug at chest height, elbow out
    "wave":   (100, 60, None, None),     # hand above the shoulder, clear of the hair
    "shrug":  (20, 85, -20, -85),        # elbows tucked, forearms out, palms up
    "cheeks": (128.5, 107, -128.5, -107),  # hands on the cheeks, below the eyes
    "phone":  (-41, -147, None, None),   # phone at chin height in front of the chest
    "point":  (None, None, -128, -12),   # straight-ish arm up and out at 45 degrees
    "cheer":  (115, 35, -115, -35),      # both arms up in a V (alias for celebrations)
}


def rig_css():
    ease = "transition:transform .35s cubic-bezier(.34,1.12,.64,1)"
    css = [
        f".sam{{--lu:{REST[0]}deg;--lf:{REST[1]}deg;--ru:{REST[2]}deg;--rf:{REST[3]}deg;overflow:visible}}",
        f".sam .arm-l{{transform-box:view-box;transform-origin:{SH_L[0]}px {SH_L[1]}px;transform:rotate(var(--lu));{ease}}}",
        f".sam .arm-l .fore{{transform-box:view-box;transform-origin:{EL_L[0]}px {EL_L[1]}px;transform:rotate(var(--lf));{ease}}}",
        f".sam .arm-r{{transform-box:view-box;transform-origin:{SH_R[0]}px {SH_R[1]}px;transform:rotate(var(--ru));{ease}}}",
        f".sam .arm-r .fore{{transform-box:view-box;transform-origin:{EL_R[0]}px {EL_R[1]}px;transform:rotate(var(--rf));{ease}}}",
        f".sam .prop-coffee{{transform-box:view-box;transform-origin:{HD_R[0]}px {HD_R[1]}px;transform:rotate(calc(-1 * (var(--ru) + var(--rf))))}}",
        f".sam .prop-phone{{transform-box:view-box;transform-origin:{HD_L[0]}px {HD_L[1]}px;transform:rotate(calc(-1 * (var(--lu) + var(--lf))))}}",
    ]
    for name, (lu, lf, ru, rf) in POSES.items():
        parts = []
        if lu is not None:
            parts.append(f"--lu:{lu}deg;--lf:{lf}deg")
        if ru is not None:
            parts.append(f"--ru:{ru}deg;--rf:{rf}deg")
        css.append(f".sam.pose-{name}{{{';'.join(parts)}}}")
    return "\n".join(css)


MOODS = ["neutral", "happy", "stressed", "ooh", "proud", "focus", "shrug", "deadpan"]
STATE_CSS = (
    ".sam .m{display:none}\n"
    + ",".join(f".sam.mood-{x} .m-{x}" for x in MOODS) + "{display:inline}\n"
    + """.sam .prop,.sam .hat{display:none}
.sam.with-laptop .prop-laptop,.sam.with-coffee .prop-coffee,.sam.with-phone .prop-phone,.sam.pose-phone .prop-phone{display:inline}
.sam.with-hat-1 .hat-1,.sam.with-hat-2 .hat-2,.sam.with-hat-3 .hat-3{display:inline}
.sam.with-hat-1 .shades{display:none}
.sam .hand-open,.sam .hand-point{display:none}
.sam.pose-wave .arm-l .hand-open,.sam.pose-shrug .hand-open,.sam.pose-cheeks .hand-open{display:inline}
.sam.pose-wave .arm-l .hand-fist,.sam.pose-shrug .hand-fist,.sam.pose-cheeks .hand-fist{display:none}
.sam.pose-point .arm-r .hand-point{display:inline}
.sam.pose-point .arm-r .hand-fist{display:none}
.sam .head{transform-box:view-box;transform-origin:150px 210px;transition:transform .35s ease}
.sam.pose-shrug .head{transform:rotate(-6deg)}
.sam.pose-phone .head{transform:rotate(-5deg) translateY(2px)}
.sam.pose-point .head{transform:rotate(4deg)}
.sam.mood-ooh .head{transform:rotate(4deg) translateY(-2px)}
.sam.mood-stressed .head{transform:translateY(3px)}
.sam.mood-deadpan .head{transform:rotate(-3deg)}
.sam.no-fx .body{filter:none}
.sam-a.on-dark .shadow-flood{flood-color:#66C4FF;flood-opacity:.22}
.sam-a .ground{fill:#143359;opacity:.12} .sam-a.on-dark .ground{fill:#000;opacity:.25}
""")


# ---------------------------------------------------------------- face
def eye_open(x, y, o, dx=0, dy=0, lid=None, wide=False):
    """o=-1 left eye (outer corner left), +1 right eye. lid = y offset of upper lid (None = open)."""
    s = ""
    if wide:
        s += f'<ellipse cx="{x}" cy="{y}" rx="9.5" ry="10.5" fill="#fff"/>'
        s += f'<circle cx="{x + dx}" cy="{y + dy}" r="4.4" fill="{LASH}"/><circle cx="{x + dx + 1.6}" cy="{y + dy - 1.6}" r="1.4" fill="#fff"/>'
        s += stroke(f"M{x - o * 10} {y - 2} Q{x} {y - 15} {x + o * 11} {y - 4}", 3, LASH)
        return s
    s += f'<ellipse cx="{x + dx}" cy="{y + dy}" rx="7.2" ry="8.8" fill="{LASH}"/>'
    s += f'<circle cx="{x + dx + 2.6}" cy="{y + dy - 3.2}" r="2.6" fill="#fff"/><circle cx="{x + dx - 2.2}" cy="{y + dy + 3.6}" r="1.2" fill="#fff" opacity=".8"/>'
    if lid is None:
        s += stroke(f"M{x - o * 9} {y - 2} Q{x} {y - 14} {x + o * 10} {y - 5} L{x + o * 15} {y - 9}", 3.6, LASH)
    else:
        L = y + lid
        s += f'<path d="M{x - 12} {y - 16} L{x + 12} {y - 16} L{x + 12} {L} Q{x} {L - 4} {x - 12} {L} Z" fill="{SKIN}"/>'
        s += stroke(f"M{x - o * 9} {L} Q{x} {L - 4} {x + o * 10} {L} L{x + o * 15} {L - 4}", 3.6, LASH)
    return s


def face(uid):
    (lx, ly), (rx, ry) = EYE_L, EYE_R
    o = []
    E = lambda inner, *moods: o.append(f'<g class="eyes {m(*moods)}">{inner}</g>')
    E(eye_open(lx, ly, -1, lid=-4) + eye_open(rx, ry, 1, lid=-4), "neutral")
    E(eye_open(lx, ly, -1) + eye_open(rx, ry, 1), "happy")
    E(eye_open(lx, ly, -1, dx=3) + eye_open(rx, ry, 1, dx=3), "shrug")
    E(eye_open(lx, ly, -1, dy=3, lid=-1) + eye_open(rx, ry, 1, dy=3, lid=-1), "focus")
    E(eye_open(lx, ly, -1, dy=2, lid=1) + eye_open(rx, ry, 1, dy=2, lid=1), "deadpan")
    st = eye_open(lx, ly, -1, dx=1, dy=3, wide=True) + eye_open(rx, ry, 1, dx=1, dy=3, wide=True)
    st += "".join(stroke(f"M{x - 7} {y + 15} Q{x} {y + 18} {x + 7} {y + 15}", 2, SKIN_SH) for x, y in (EYE_L, EYE_R))
    E(st, "stressed")
    so = ""
    for (x, y) in (EYE_L, EYE_R):
        so += f'<path d="{star_path(x, y, 13, 5.8)}" fill="{NAVY}" stroke="{NAVY}" stroke-width="2.5" stroke-linejoin="round"/>'
        so += f'<path d="{sparkle_path(x + 3, y - 3, 3.8)}" fill="{LIME}"/>'
    E(so, "ooh")
    pr = ""
    for (x, y), oo in ((EYE_L, -1), (EYE_R, 1)):
        pr += stroke(f"M{x - 9} {y + 2} Q{x} {y - 9} {x + 9} {y + 2} M{x + oo * 9} {y + 2} L{x + oo * 13} {y - 2}", 4.2, LASH)
    E(pr, "proud")
    # cheeks + nose
    o.append(f'<g class="cheeks {m("neutral", "happy", "ooh", "proud", "shrug", "focus")}">'
             f'<ellipse cx="104" cy="168" rx="11" ry="6" fill="{BLUSH}" opacity=".38"/>'
             f'<ellipse cx="196" cy="168" rx="11" ry="6" fill="{BLUSH}" opacity=".38"/></g>')
    o.append(f'<path class="nose" d="M147 160 Q150 153 154 160 Q150 163 147 160 Z" fill="{SKIN_SH}"/>')
    # mouths
    M = lambda inner, *moods: o.append(f'<g class="mouth {m(*moods)}">{inner}</g>')
    M(f'<path d="M137 174 Q150 182 164 170 Q152 190 137 174 Z" fill="{LIP}"/>'
      + stroke("M137 174 Q150 182 164 170", 2.2, LIP_D), "neutral")
    M(f'<path d="M136 171 Q150 174 164 171 Q162 189 150 189 Q138 189 136 171 Z" fill="{MOUTH}" stroke="{LIP}" stroke-width="2.6" stroke-linejoin="round"/>'
      f'<path d="M138 172 Q150 174 162 172 L161 177 Q150 179 139 177 Z" fill="#fff"/>'
      f'<path d="M143 184 Q150 180 157 184 Q150 188 143 184 Z" fill="{TONGUE}"/>', "happy")
    M(f'<path d="M131 168 Q150 171 169 168 Q167 193 150 193 Q133 193 131 168 Z" fill="{MOUTH}" stroke="{LIP}" stroke-width="2.6" stroke-linejoin="round"/>'
      f'<path d="M134 169 Q150 172 166 169 L165 175 Q150 177 135 175 Z" fill="#fff"/>'
      f'<path d="M141 187 Q150 180 159 187 Q150 193 141 187 Z" fill="{TONGUE}"/>', "proud")
    M(f'<ellipse cx="150" cy="180" rx="8" ry="10" fill="{MOUTH}" stroke="{LIP}" stroke-width="2.6"/>'
      f'<ellipse cx="150" cy="186" rx="4.6" ry="3" fill="{TONGUE}"/>', "ooh")
    M(stroke("M136 180 q3.5 -5 7 0 t7 0 t7 0 t7 0", 3.6, LIP_D), "stressed")
    M(f'<ellipse cx="153" cy="178" rx="5" ry="3.6" fill="{LIP}"/>', "focus")
    M(stroke("M140 179 Q150 178 160 174", 3.8, LIP_D), "shrug")
    M(stroke("M139 179 L161 179", 3.8, LIP_D), "deadpan")
    return "".join(o)


def brows(hc):
    o = []
    def pair(l, r, *moods):
        o.append(f'<g class="brows {m(*moods)}">{stroke(l, 5.6, hc)}{stroke(r, 5.6, hc)}</g>')
    pair("M110 121 Q121 111 137 115", "M163 115 Q179 111 190 121", "neutral", "focus")
    pair("M110 117 Q121 106 137 110", "M163 110 Q179 106 190 117", "happy", "proud")
    pair("M110 122 Q125 119 138 109", "M162 109 Q175 119 190 122", "stressed")
    pair("M111 111 Q122 99 137 104", "M163 104 Q178 99 189 111", "ooh")
    pair("M110 112 Q121 101 137 106", "M163 120 L190 119", "shrug")
    pair("M111 121 L137 121", "M163 121 L189 121", "deadpan")
    return "".join(o)


def face_fx():
    drop = "M214 92 C214 92 202 108 202 115 a12 12 0 0 0 24 0 C226 108 214 92 214 92 Z"
    sp = "".join(f'<path d="{sparkle_path(x, y, r)}" fill="{c}" stroke="{NAVY}" stroke-width="2"/>'
                 for (x, y, r, c) in ((52, 74, 13, LIME), (250, 60, 16, SKY), (256, 124, 8, LIME), (64, 122, 7, SKY)))
    return (f'<g class="fx-sweat {m("stressed")}"><path d="{drop}" fill="{SKY}"/>'
            f'<path d="M207 112 q0 -5 4 -9" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/></g>'
            f'<g class="fx-stress {m("stressed")}">{stroke("M62 70 l-12 -10 M58 86 l-16 -2 M70 58 l-6 -14", 4, ORANGE)}</g>'
            f'<g class="fx-sparkles {m("ooh", "proud")}">{sp}</g>'
            '')


# ---------------------------------------------------------------- hair
def hair(kind, uid):
    h = HAIRS[kind]
    if kind == "waves":
        back = ("M150 22 C102 22 68 52 64 104 C60 140 74 162 64 188 C54 214 70 234 60 260 "
                "C54 280 64 296 80 298 C94 300 106 290 108 276 L192 276 C194 290 206 300 220 298 "
                "C236 296 246 280 240 260 C230 234 246 214 236 188 C226 162 240 140 236 104 C232 52 198 22 150 22 Z")
        tips = ("M40 250 C56 236 68 258 84 244 C96 234 104 246 110 252 L190 252 C196 246 204 234 216 244 "
                "C232 258 244 236 260 250 L260 320 L40 320 Z")
        band = "M40 236 C56 222 68 244 84 230 C96 220 104 232 110 238 L190 238 C196 232 204 220 216 230 C232 244 244 222 260 236 L260 320 L40 320 Z"
        bk = (f'<clipPath id="{uid}-hclip"><path d="{back}"/></clipPath>'
              f'<g class="hair-back"><path d="{back}" fill="{h["base"]}"/>'
              f'<g clip-path="url(#{uid}-hclip)"><path d="{band}" fill="{h["tip"]}"/>'
              f'<path d="{tips}" fill="{h["tip"]}"/>'
              f'<path d="M206 120 C214 150 204 170 214 196 M94 120 C86 150 96 170 86 196" stroke="{h["hi"]}" stroke-width="5" fill="none" stroke-linecap="round"/>'
              f'</g></g>')
        front = ("M116 38 C150 22 214 30 228 92 C236 128 222 150 232 178 C240 200 228 218 212 216 "
                 "C222 198 214 182 210 162 C204 132 196 108 178 90 C160 76 136 76 120 66 C118 56 116 46 116 38 Z "
                 "M116 38 C90 40 72 70 70 112 C68 142 80 162 72 188 C66 206 74 218 88 216 "
                 "C84 198 90 182 88 160 C86 128 94 96 112 70 C114 58 116 48 116 38 Z")
        fr = (f'<g class="hair-front"><path d="{front}" fill="{h["base"]}"/>'
              f'<path d="M128 42 C164 36 200 50 214 84" stroke="{h["hi"]}" stroke-width="6" fill="none" stroke-linecap="round"/>'
              f'<clipPath id="{uid}-fclip"><path d="{front}"/></clipPath>'
              f'<g class="money-piece" clip-path="url(#{uid}-fclip)" fill="none" stroke-linecap="round">'
              f'<path d="M94 64 C80 96 76 132 78 168 C79 190 78 204 82 218" stroke="{h["tip"]}" stroke-width="14"/>'
              f'<path d="M206 64 C222 96 226 132 224 168 C223 190 224 204 220 218" stroke="{h["tip"]}" stroke-width="12"/>'
              f'<path d="M98 72 C88 100 86 130 88 160" stroke="{h["tip"]}" stroke-width="3"/></g></g>')
        return bk, fr
    if kind == "pony":
        back = "M78 132 C74 70 108 38 150 38 C192 38 226 70 222 132 L220 160 L80 160 Z"
        tail = ("M184 44 C214 18 258 34 258 88 C258 132 240 170 250 216 C254 240 238 256 222 248 "
                "C234 214 224 178 228 140 C230 104 222 76 196 60 Z")
        bk = (f'<g class="hair-back"><path d="{tail}" fill="{h["base"]}"/>'
              f'<path d="M236 60 C250 86 246 124 236 156" stroke="{h["hi"]}" stroke-width="6" fill="none" stroke-linecap="round"/>'
              f'<path d="{back}" fill="{h["base"]}"/></g>')
        front = "M78 138 C70 76 104 38 150 38 C196 38 230 76 222 138 C214 104 190 80 150 78 C110 80 86 104 78 138 Z"
        fr = (f'<g class="hair-front"><path d="{front}" fill="{h["base"]}"/>'
              f'<path d="M104 62 C130 46 168 44 194 52 M98 80 C124 62 164 56 192 58" stroke="{h["hi"]}" stroke-width="4" fill="none" stroke-linecap="round"/>'
              f'<ellipse cx="192" cy="48" rx="10" ry="7" fill="{LIME}" transform="rotate(-30 192 48)"/>'
              f'{stroke("M84 124 C78 146 90 160 82 180", 3, h["base"])}{stroke("M216 124 C222 146 210 160 218 180", 3, h["base"])}</g>')
        return bk, fr
    # lob
    back = "M68 132 C62 62 104 32 150 32 C196 32 238 62 232 132 L238 228 L196 214 L104 214 L62 228 Z"
    bk = f'<g class="hair-back"><path d="{back}" fill="{h["base"]}"/></g>'
    front = ("M178 36 C126 28 78 54 72 116 L66 232 L100 222 C92 188 90 150 98 118 C112 92 144 82 174 64 Z "
             "M178 36 C206 42 226 66 228 104 L236 232 L204 222 C212 184 212 144 206 116 C200 92 190 74 178 62 Z")
    fr = (f'<g class="hair-front"><path d="{front}" fill="{h["base"]}"/>'
          f'<path d="M96 70 C120 48 152 40 176 42" stroke="{h["hi"]}" stroke-width="7" fill="none" stroke-linecap="round"/>'
          f'<path d="M80 130 L76 214 M222 120 L226 214" stroke="{h["hi"]}" stroke-width="4" fill="none" stroke-linecap="round"/></g>')
    return bk, fr


# ---------------------------------------------------------------- eyewear
def eyewear(kind):
    if kind == "shades":
        lens = lambda cx, cy, r: (f'<g transform="rotate({r} {cx} {cy})"><rect x="{cx - 24}" y="{cy - 12}" width="48" height="24" rx="11" fill="#1F3F66" stroke="{GOLD}" stroke-width="2.6"/>'
                                  f'<path d="M{cx - 14} {cy + 7} L{cx - 2} {cy - 8}" stroke="{SKY}" stroke-width="4" stroke-linecap="round" opacity=".8"/></g>')
        return (f'<g class="eyewear shades">{lens(122, 56, -5)}{lens(178, 56, 5)}'
                f'{stroke("M146 54 Q150 50 154 54", 2.6, GOLD)}</g>')
    if kind == "frames":
        s = ""
        for (x, y), oo in ((EYE_L, -1), (EYE_R, 1)):
            d = (f"M{x - oo * 20} {y - 12} L{x + oo * 14} {y - 15} Q{x + oo * 27} {y - 21} {x + oo * 24} {y - 6} "
                 f"L{x + oo * 20} {y + 8} Q{x + oo * 17} {y + 15} {x + oo * 8} {y + 15} L{x - oo * 12} {y + 15} "
                 f"Q{x - oo * 21} {y + 14} {x - oo * 21} {y + 4} Z")
            s += f'<path d="{d}" fill="#fff" fill-opacity=".12" stroke="{DEEP}" stroke-width="6" stroke-linejoin="round"/>'
            s += f'<circle cx="{x + oo * 22}" cy="{y - 13}" r="2.4" fill="{LIME}"/>'
        s += stroke("M146 138 Q150 134 154 138", 5, DEEP) + stroke("M104 136 L84 130 M196 136 L216 130", 5, DEEP)
        return f'<g class="eyewear frames">{s}</g>'
    return ""


# ---------------------------------------------------------------- hats (stack on top of each other)
def hats():
    t = f'font-family="{FONT}" font-weight="700" text-anchor="middle"'
    h1 = (f'<g class="hat hat-1">'
          f'<ellipse cx="150" cy="72" rx="94" ry="13" fill="{NAVY}"/>'
          f'<path d="M64 74 Q150 86 236 74" stroke="{DEEP}" stroke-width="3" fill="none"/>'
          f'<path d="M102 72 C104 44 110 26 126 24 C140 22 142 32 150 32 C158 32 160 22 174 24 C190 26 196 44 198 72 Q150 80 102 72 Z" fill="{NAVY}"/>'
          f'<path d="M103 52 L197 52 L198 68 Q150 75 102 68 Z" fill="{LIME}"/>'
          f'<text x="150" y="66" {t} font-size="14" fill="{NAVY}">PPT</text></g>')
    h2 = (f'<g class="hat hat-2">'
          f'<path d="M114 28 C114 -4 130 -18 150 -18 C170 -18 186 -4 186 28 Z" fill="{TEAL}"/>'
          f'<path d="M150 -18 L150 28" stroke="#00737A" stroke-width="2"/><circle cx="150" cy="-18" r="4" fill="#00737A"/>'
          f'<path d="M180 24 Q214 18 232 28 Q214 34 180 30 Z" fill="#00737A"/>'
          f'<text x="133" y="16" {t} font-size="16" fill="#fff">PY</text></g>')
    h3 = (f'<g class="hat hat-3">'
          f'<path d="M150 -28 L150 -54" stroke="{WGREY}" stroke-width="4"/>'
          f'<path d="M150 -38 l-6 -3 l12 -6 l-12 -6 l6 -3" stroke="{WGREY}" stroke-width="2.4" fill="none" stroke-linejoin="round"/>'
          f'<circle cx="150" cy="-60" r="8" fill="{LIME}" stroke="{NAVY}" stroke-width="2.4"/>'
          f'<path d="M146 -63 l3 -2" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
          f'<rect x="118" y="-30" width="64" height="16" rx="8" fill="#8E949C"/>'
          f'<circle cx="134" cy="-22" r="4" fill="{LIME}"/><circle cx="150" cy="-22" r="4" fill="{SKY}"/><circle cx="166" cy="-22" r="4" fill="{LIME}"/>'
          f'<rect x="112" y="-28" width="8" height="12" rx="3" fill="#6E747C"/><rect x="180" y="-28" width="8" height="12" rx="3" fill="#6E747C"/></g>')
    return h1 + h2 + h3


# ---------------------------------------------------------------- body
def hand_open(hx, hy, side, fill=SKIN):
    t = -1 if side == "l" else 1
    thumb = f"M{hx + t * 6} {hy - 6} Q{hx + t * 19} {hy - 8} {hx + t * 17} {hy + 4} Q{hx + t * 15} {hy + 9} {hx + t * 7} {hy + 6} Z"
    palm = f"M{hx - 10} {hy - 8} Q{hx - 11} {hy + 19} {hx} {hy + 19} Q{hx + 11} {hy + 19} {hx + 10} {hy - 8} Z"
    return (f'<g class="hand-open" stroke="{SKIN_SH}" stroke-width="1.8" stroke-linejoin="round"><path d="{thumb}" fill="{fill}"/><path d="{palm}" fill="{fill}"/>'
            f'{stroke(f"M{hx - 4} {hy + 18} L{hx - 4} {hy + 10} M{hx + 4} {hy + 18} L{hx + 4} {hy + 10}", 2.2, SKIN_SH)}</g>')


def hand_point(hx, hy):
    return (f'<g class="hand-point" stroke="{SKIN_SH}" stroke-width="1.6"><rect x="{hx - 4.5}" y="{hy - 2}" width="9" height="30" rx="4.5" fill="{SKIN}"/>'
            f'<circle cx="{hx}" cy="{hy}" r="11.5" fill="{SKIN}"/>'
            f'<ellipse cx="{hx + 9}" cy="{hy + 2}" rx="4" ry="6.5" fill="{SKIN}" transform="rotate(-25 {hx + 9} {hy + 2})"/>'
            f'{stroke(f"M{hx - 7} {hy + 5} q5 3 9 0", 2.2, SKIN_SH)}</g>')


def phone(uid):
    hx, hy = HD_L
    x, y = hx - 12, hy - 34
    return (f'<g class="prop prop-phone"><rect x="{x}" y="{y}" width="24" height="44" rx="6" fill="{LIME}"/>'
            f'<rect x="{x + 3}" y="{y + 3}" width="11" height="12" rx="3" fill="{NAVY}"/>'
            f'<circle cx="{x + 6.5}" cy="{y + 7}" r="2" fill="#4A6A90"/><circle cx="{x + 10.5}" cy="{y + 11}" r="2" fill="#4A6A90"/>'
            f'<rect x="{x}" y="{y}" width="24" height="44" rx="6" fill="none" stroke="#B6CC2C" stroke-width="2"/></g>')


def arm(side, uid, o):
    """One continuous blazer sleeve: upper arm, elbow cap, tapered forearm, cuff, hand over the cuff.
    The forearm group is drawn over the upper arm so folded poses (phone) read cleanly."""
    sx, sy = SH_L if side == "l" else SH_R
    ex, ey = EL_L if side == "l" else EL_R
    hx, hy = HD_L if side == "l" else HD_R
    inner = 1 if side == "l" else -1
    wrist = hy - 12
    up = capsule(sx, sy, ey, 30)
    fore = (f"M{ex - 14} {ey} A14 14 0 0 1 {ex + 14} {ey} L{ex + 11} {wrist} "
            f"L{ex - 11} {wrist} Z")
    prop = B.coffee_A(uid) if side == "r" else phone(uid)
    gold = (f'<rect x="{hx - 9}" y="{hy - 12}" width="18" height="5" rx="2.5" fill="{GOLD}"/>'
            f'<circle cx="{hx + inner * 6}" cy="{hy - 10}" r="3.6" fill="{GOLD}"/><circle cx="{hx + inner * 6}" cy="{hy - 10}" r="2" fill="{NAVY}"/>'
            if side == "l" else
            f'<rect x="{hx - 9}" y="{hy - 12}" width="18" height="3.4" rx="1.7" fill="{GOLD}"/>'
            f'<rect x="{hx - 9}" y="{hy - 8.5}" width="18" height="2.6" rx="1.3" fill="{GOLD_SH}"/>')
    return f"""<g class="arm arm-{side}">
  <path class="sleeve-upper" d="{up}" fill="{o['sleeve']}"/>
  <path d="{capsule(sx + inner * 8, sy + 8, ey - 6, 9)}" fill="url(#{uid}-dots)"/>
  <g class="fore">
    <circle class="elbow" cx="{ex}" cy="{ey}" r="15" fill="{o['sleeve']}"/>
    <path class="sleeve-fore" d="{fore}" fill="{o['sleeve']}"/>
    <path d="M{ex + inner * 6} {ey + 6} L{ex + inner * 5} {wrist - 6}" stroke="url(#{uid}-dots)" stroke-width="7" stroke-linecap="round"/>
    <rect class="cuff" x="{ex - 12.5}" y="{wrist - 9}" width="25" height="10" rx="4" fill="{o['shade']}"/>
    {gold}
    {prop}
    <g class="hand-fist"><circle cx="{hx}" cy="{hy}" r="11.5" fill="{SKIN}" stroke="{SKIN_SH}" stroke-width="1.6"/>
      {stroke(f"M{hx - 6} {hy + 4} q6 4 12 0", 2.2, SKIN_SH)}</g>
    {hand_open(hx, hy, side)}{hand_point(hx, hy) if side == "r" else ""}
  </g>
</g>"""


def outfit(kind, uid):
    o = OUTFITS[kind]
    p, ps = o["pants"], o["pants_sh"]
    legs = (f'<g class="legs"><path d="M112 346 L149 346 L150 396 L98 396 Z" fill="{p}"/>'
            f'<path d="M151 346 L188 346 L202 396 L150 396 Z" fill="{p}"/>'
            f'<path d="M151 346 L188 346 L202 396 L176 396 Z" fill="url(#{uid}-dots)"/>'
            f'{stroke("M124 352 L118 394 M176 352 L182 394", 2, ps)}')
    if o["shoe"] == "sneaker":
        legs += (f'<path d="M100 394 L146 394 L148 402 Q148 405 144 405 L98 405 Q94 405 96 400 Z" fill="{WHITE}"/>'
                 f'<path d="M154 394 L200 394 L204 400 Q206 405 202 405 L156 405 Q152 405 152 402 Z" fill="{WHITE}"/>'
                 f'<rect x="96" y="401" width="52" height="4" rx="2" fill="{SAND2}"/><rect x="152" y="401" width="54" height="4" rx="2" fill="{SAND2}"/>')
    else:
        legs += (f'<path d="M146 395 L146 404 L96 404 Q86 402 100 395 Z" fill="{NAVY}"/>'
                 f'<path d="M154 395 L154 404 L204 404 Q214 402 200 395 Z" fill="{NAVY}"/>')
    legs += "</g>"
    blazer = ("M104 222 C94 224 90 232 90 246 L86 352 C86 358 90 362 96 362 L204 362 C210 362 214 358 214 352 "
              "L210 246 C210 232 206 224 196 222 L172 214 L128 214 Z")
    neck = f'<rect x="136" y="188" width="28" height="40" rx="10" fill="{SKIN_SH}"/>'
    if o["inner_kind"] == "cami":
        inner = (f'<path d="M126 214 L174 214 L170 362 L130 362 Z" fill="{SKIN}"/>'
                 f'<path d="M128 240 Q150 248 172 240 L170 362 L130 362 Z" fill="{o["inner"]}"/>'
                 f'{stroke("M134 241 L136 218 M166 241 L164 218", 1.8, "#B6CC2C")}'
                 f'{stroke("M138 222 Q150 234 162 222", 1.8, GOLD)}<circle cx="150" cy="230" r="3" fill="{GOLD}"/>')
    else:
        inner = (f'<path d="M126 214 L174 214 L170 362 L130 362 Z" fill="{o["inner"]}"/>'
                 f'<path d="M134 214 Q150 232 166 214 Z" fill="{SKIN_SH}"/>'
                 f'{stroke("M140 222 Q150 236 160 222", 1.8, GOLD)}<circle cx="150" cy="231" r="2.6" fill="{GOLD}"/>')
    lapels = (f'<path d="M128 214 L148 300 L138 300 L112 252 L120 244 L110 236 Z" fill="{o["lapel"]}"/>'
              f'<path d="M172 214 L152 300 L162 300 L188 252 L180 244 L190 236 Z" fill="{o["lapel"]}"/>')
    bl = (f'<path class="torso" d="{blazer}" fill="{o["blazer"]}"/>'
          f'<path d="M126 214 L174 214 L170 362 L130 362 Z" fill="none"/>')
    shade = (f'<path d="M178 216 C196 220 208 228 210 246 L214 352 C214 358 210 362 204 362 L176 362 '
             f'C190 310 192 254 178 216 Z" fill="url(#{uid}-dots)"/>')
    details = (f'{stroke("M96 316 L124 316 M176 316 L204 316", 2.4, o["shade"])}'
               f'<circle cx="160" cy="320" r="3.4" fill="{o["shade"]}"/>'
               f'<rect x="100" y="270" width="2" height="2" fill="none"/>')
    return f'<g class="outfit outfit-{kind}">{legs}{neck}{bl}{shade}<g class="inner">{inner}</g>{lapels}{details}</g>'


def defs(uid):
    return B.defs_A(uid) + (f'<pattern id="{uid}-dotsC" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
                            f'<circle cx="3" cy="3" r="1.9" fill="#C98E52"/></pattern>')


def sam(uid, classes="mood-neutral", hair_kind="waves", outfit_kind="camel", eyewear_kind="shades", hoops=True):
    hb, hf = hair(hair_kind, uid)
    hc = HAIRS[hair_kind]["brow"]
    hoop = (f'<g class="hoops"><circle cx="82" cy="176" r="9" fill="none" stroke="{GOLD}" stroke-width="3.2"/>'
            f'<circle cx="218" cy="176" r="9" fill="none" stroke="{GOLD}" stroke-width="3.2"/></g>') if hoops else ""
    head = "M80 128 C80 76 108 60 150 60 C192 60 220 76 220 128 C220 176 194 206 150 206 C106 206 80 176 80 128 Z"
    ears = f'<circle cx="80" cy="148" r="12" fill="{SKIN}"/><circle cx="220" cy="148" r="12" fill="{SKIN}"/>'
    return f"""<svg class="sam sam-a {classes}" viewBox="0 0 300 420" overflow="visible" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sam">
<defs>{defs(uid)}</defs>
<style>{STATE_CSS}{rig_css()}</style>
<ellipse class="ground" cx="150" cy="405" rx="80" ry="8"/>
<g class="body" filter="url(#{uid}-fx)">
  {hb}
  {outfit(outfit_kind, uid)}
  <g class="head">
    {ears}
    <path class="face" d="{head}" fill="{SKIN}"/>
    {face(uid)}
    {eyewear(eyewear_kind) if eyewear_kind == "frames" else ""}
    {hf}
    {hoop}
    {eyewear(eyewear_kind) if eyewear_kind == "shades" else ""}
    {brows(hc)}
    {face_fx()}
    {hats()}
  </g>
  {arm("l", uid, OUTFITS[outfit_kind])}
  {arm("r", uid, OUTFITS[outfit_kind])}
  {B.laptop_A(uid, "#C8D0DA", LIME, SAND2, WGREY)}
</g>
</svg>"""


# ================================================================ Spark (final mascot)
SPARK_POSES = ["stand", "walk", "read", "thumbs", "think", "wave"]
SPARK_CSS = (
    ".spark{overflow:visible}\n.spark .pz{display:none}\n"
    + ",".join(f".spark.pose-{p} .p-{p}" for p in SPARK_POSES) + "{display:inline}\n"
    + """.spark .leg-l{transform-box:view-box;transform-origin:96px 166px}
.spark .leg-r{transform-box:view-box;transform-origin:124px 166px}
.spark.pose-walk .leg-l{transform:rotate(22deg)}
.spark.pose-walk .leg-r{transform:rotate(-18deg)}
.spark .bod{transform-box:view-box;transform-origin:110px 200px}
.spark.pose-walk .bod{transform:rotate(6deg)}
.spark.pose-think .bod{transform:rotate(4deg)}
.spark.pose-wave .bod{transform:rotate(-4deg)}
/* .walking: looping walk cycle, works on its own (shows the walk arms/face) */
.spark.walking .pz{display:none}
.spark.walking .p-walk{display:inline}
.spark.walking .leg-l{animation:spark-leg .44s ease-in-out infinite alternate}
.spark.walking .leg-r{animation:spark-leg .44s ease-in-out infinite alternate-reverse}
.spark.walking .bod{animation:spark-bob .22s ease-in-out infinite alternate}
.spark.walking .arms-walk{transform-box:view-box;transform-origin:110px 124px;animation:spark-swing .44s ease-in-out infinite alternate}
@keyframes spark-leg{from{transform:rotate(24deg)}to{transform:rotate(-22deg)}}
@keyframes spark-bob{from{transform:rotate(6deg) translateY(0)}to{transform:rotate(6deg) translateY(-5px)}}
@keyframes spark-swing{from{transform:rotate(-6deg)}to{transform:rotate(6deg)}}
@media (prefers-reduced-motion:reduce){.spark.walking .leg-l,.spark.walking .leg-r,.spark.walking .bod,.spark.walking .arms-walk{animation:none}}
.spark .gnd{fill:#143359;opacity:.13} .spark.on-dark .gnd{fill:#000;opacity:.3}
""")


def pz(*poses):
    return "pz " + " ".join(f"p-{x}" for x in poses)


def spark(uid, classes="pose-stand"):
    col, limb, hand = B.CLAY, "#9A4A31", B.CREAM
    hi, ink = B.CLAY_HI, "#3A1E14"
    ray = "M92 112 L98 50 A12 12 0 0 1 122 50 L128 112 Z"
    rays = "".join(f'<path d="{ray}" transform="rotate({22.5 + 45 * k} 110 112)"/>' for k in range(8))
    cx, cy = 110, 104

    def eye(x, y, r=5.2):
        return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r + 1.6}" fill="{ink}"/><circle cx="{x + 1.8}" cy="{y - 2.4}" r="1.9" fill="#fff"/>'
    arc = lambda x0, x1, up=True: stroke(f"M{x0} {cy + 2} Q{(x0 + x1) / 2} {cy + (-6 if up else 7)} {x1} {cy + 2}", 3.4, ink)
    f = []
    f.append(f'<g class="eyes {pz("stand", "walk")}">{eye(cx - 13, cy)}{eye(cx + 13, cy)}</g>')
    f.append(f'<g class="eyes {pz("read")}">{arc(cx - 19, cx - 7, False)}{arc(cx + 7, cx + 19, False)}</g>')
    f.append(f'<g class="eyes {pz("thumbs")}">{eye(cx - 13, cy)}{arc(cx + 7, cx + 19)}</g>')
    f.append(f'<g class="eyes {pz("wave")}">{arc(cx - 19, cx - 7)}{arc(cx + 7, cx + 19)}</g>')
    f.append(f'<g class="eyes {pz("think")}">{eye(cx - 9, cy - 2, 4.6)}{eye(cx + 15, cy - 2, 4.6)}'
             f'{stroke(f"M{cx + 8} {cy - 13} L{cx + 21} {cy - 15}", 3, ink)}</g>')
    f.append(f'<ellipse cx="{cx - 22}" cy="{cy + 11}" rx="6" ry="3.6" fill="#F08A7A" opacity=".55"/><ellipse cx="{cx + 22}" cy="{cy + 11}" rx="6" ry="3.6" fill="#F08A7A" opacity=".55"/>')
    f.append(f'<path class="{pz("stand", "walk")}" d="M{cx - 6} {cy + 12} Q{cx} {cy + 18} {cx + 6} {cy + 12}" stroke="{ink}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    f.append(f'<ellipse class="{pz("read")}" cx="{cx}" cy="{cy + 15}" rx="3.4" ry="4" fill="{ink}"/>')
    f.append(f'<g class="{pz("thumbs", "wave")}"><path d="M{cx - 8} {cy + 10} Q{cx} {cy + 11} {cx + 8} {cy + 10} Q{cx + 7} {cy + 21} {cx} {cy + 21} Q{cx - 7} {cy + 21} {cx - 8} {cy + 10} Z" fill="{ink}"/>'
             f'<path d="M{cx - 4} {cy + 18} Q{cx} {cy + 14} {cx + 4} {cy + 18} Q{cx} {cy + 21} {cx - 4} {cy + 18} Z" fill="#F0806C"/></g>')
    f.append(f'<path class="{pz("think")}" d="M{cx - 5} {cy + 15} Q{cx + 1} {cy + 12} {cx + 7} {cy + 14}" stroke="{ink}" stroke-width="3" fill="none" stroke-linecap="round"/>')

    def a(d, cl, hp=None, extra=""):
        hh = f'<circle cx="{hp[0]}" cy="{hp[1]}" r="7.5" fill="{hand}"/>' if hp else ""
        return f'<g class="{cl}">{stroke(d, 7.5, limb)}{hh}{extra}</g>'
    arms = [a("M64 124 Q50 136 48 150", pz("stand"), (48, 152)), a("M156 124 Q170 136 172 150", pz("stand"), (172, 152)),
            f'<g class="arms-walk {pz("walk")}">' + a("M64 124 Q50 128 42 120", "", (40, 118)) + a("M156 124 Q168 140 178 150", "", (180, 152)) + "</g>",
            a("M64 124 Q52 138 52 150", pz("thumbs"), (52, 152)),
            a("M156 124 Q178 124 182 110", pz("thumbs"), None,
              f'<g transform="translate(184 98) scale(1.35) translate(-184 -98)"><path d="M178 92 Q176 76 183 75 Q190 75 188 90 Z" fill="{hand}"/>'
              f'<rect x="172" y="89" width="22" height="19" rx="8" fill="{hand}"/>{stroke("M175 96 h11 M175 101 h11", 1.6, limb, "opacity=" + chr(34) + ".45" + chr(34))}</g>'),
            a("M64 124 Q46 140 60 154", pz("think"), (62, 154)), a("M156 124 Q164 152 136 146", pz("think"), (134, 144)),
            a("M64 124 Q52 138 52 150", pz("wave"), (52, 152)),
            a("M156 122 Q180 116 184 86", pz("wave"), None,
              f'<g transform="rotate(-12 186 78)"><ellipse cx="186" cy="76" rx="9" ry="11" fill="{hand}"/>'
              f'<ellipse cx="176" cy="80" rx="3.6" ry="6" fill="{hand}" transform="rotate(-30 176 80)"/></g>'
              f'{stroke("M200 62 q6 6 4 14 M206 52 q9 9 6 22", 2.8, WGREY)}')]
    book = (f'<g class="{pz("read")}">{stroke("M64 124 Q60 146 74 156", 7.5, limb)}{stroke("M156 124 Q160 146 146 156", 7.5, limb)}'
            f'<path d="M70 128 L110 136 L150 128 L150 172 L110 180 L70 172 Z" fill="{BLUE}"/>'
            f'<path d="M74 126 L110 133 L110 175 L74 168 Z" fill="#FFFDF6"/><path d="M146 126 L110 133 L110 175 L146 168 Z" fill="#F4F1EA"/>'
            f'{stroke("M80 140 L102 144 M80 148 L102 152 M80 156 L96 159", 2.4, WGREY)}'
            f'{stroke("M120 160 v-8 M128 158 v-16 M136 156 v-11", 4, BLUE)}<rect x="118" y="138" width="22" height="5" rx="2.5" fill="{LIME}"/>'
            f'<circle cx="74" cy="158" r="7.5" fill="{hand}"/><circle cx="146" cy="158" r="7.5" fill="{hand}"/></g>')
    think = (f'<g class="{pz("think")}"><circle cx="176" cy="54" r="5" fill="#fff" stroke="{NAVY}" stroke-width="2"/><circle cx="188" cy="36" r="8" fill="#fff" stroke="{NAVY}" stroke-width="2"/>'
             f'<rect x="150" y="-2" width="62" height="34" rx="17" fill="#fff" stroke="{NAVY}" stroke-width="2.4"/>'
             f'{stroke("M168 22 v-6 M178 22 v-14 M188 22 v-9", 4, BLUE)}{stroke("M196 12 l3 -6 l3 6", 3, MINT)}</g>')
    return f"""<svg class="spark {classes}" viewBox="0 0 220 240" overflow="visible" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Claude mascot">
<style>{SPARK_CSS}</style>
<ellipse class="gnd" cx="110" cy="205" rx="44" ry="5.5"/>
<g class="{pz('walk')}" stroke="{WGREY}" stroke-width="3.4" stroke-linecap="round"><path d="M22 112 h18 M14 130 h22 M24 148 h14"/></g>
{think}
<g class="bod">
  <g class="leg-l"><path d="M96 160 L92 194" stroke="{limb}" stroke-width="9" stroke-linecap="round"/><path d="M80 203 Q80 192 92 192 Q101 192 101 203 Z" fill="{NAVY}"/></g>
  <g class="leg-r"><path d="M124 160 L128 194" stroke="{limb}" stroke-width="9" stroke-linecap="round"/><path d="M119 203 Q119 192 128 192 Q140 192 140 203 Z" fill="{NAVY}"/></g>
  <g class="spark-body" fill="{col}">{rays}<circle cx="110" cy="112" r="40"/></g>
  {stroke("M84 50 L89 62", 6, hi)}{stroke("M48 86 L58 91", 6, hi)}
  <circle cx="110" cy="110" r="35" fill="{hand}"/>
  {"".join(f)}
  {"".join(arms)}
  {book}
</g>
</svg>"""


# ================================================================ boards
CSS = """
@font-face{font-family:'Libre Franklin';src:url(../../dist/guide/fonts/LibreFranklin-Regular.ttf);font-weight:400}
@font-face{font-family:'Libre Franklin';src:url(../../dist/guide/fonts/LibreFranklin-SemiBold.ttf);font-weight:600}
@font-face{font-family:'Libre Franklin';src:url(../../dist/guide/fonts/LibreFranklin-Bold.ttf);font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FBFAF7;font-family:'Libre Franklin',sans-serif;color:#143359;width:1920px;height:1080px;overflow:hidden;padding:52px 80px}
.eyebrow{font-size:18px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#005A8C}
h1{font-size:52px;font-weight:700;line-height:1.05;margin-top:8px}
.lede{font-size:21px;line-height:1.4;color:#505050;margin-top:10px;max-width:1300px}
.card{border-radius:24px;background:#EFEDE7;position:relative;display:flex;align-items:flex-end;justify-content:center}
.card.dark{background:#0B3266}
.lbl{position:absolute;left:18px;top:14px;font-size:17px;font-weight:700}
.dark .lbl{color:#fff}
.cap{font-size:14px;font-weight:600;color:#505050;text-align:center}
.dark .cap{color:#B6E2FA}
.row{display:flex;gap:14px}
svg{display:block}
h2{font-size:30px;font-weight:700;margin-top:16px}
.note{font-size:17px;line-height:1.4;color:#505050;margin-top:6px}
.tag{display:inline-block;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 10px;border-radius:999px;background:#D9F14E;margin-left:10px;vertical-align:middle}
"""
_n = [0]


def sized(svg, h, vb_w=300, vb_h=420):
    _n[0] += 1
    return svg.replace(f'viewBox="0 0 {vb_w} {vb_h}"', f'viewBox="0 0 {vb_w} {vb_h}" height="{h}" width="{round(h * vb_w / vb_h)}"', 1)


def S(classes, h, **kw):
    _n[0] += 1
    return sized(sam(f"r{_n[0]}", classes, **kw), h)


def K(classes, h):
    _n[0] += 1
    return sized(spark(f"k{_n[0]}", classes), h, 220, 240)


def shoot(html_path, png_path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080",
                    "--virtual-time-budget=3000", f"--screenshot={png_path}", f"file://{html_path}"],
                   check=True, capture_output=True)
    print("wrote", png_path)


VARIANTS = [
    ("1. Caramel waves", dict(hair_kind="waves", outfit_kind="camel", eyewear_kind="shades"),
     "Long glossy waves with caramel balayage, tinted shades pushed up, camel oversized blazer with sleeves shoved up, white tee, gold hoops, watch, navy wide-legs, white sneakers."),
    ("2. Power pony", dict(hair_kind="pony", outfit_kind="blue", eyewear_kind="frames"),
     "Sleek high ponytail, bold cat-eye statement frames, McKesson-blue blazer with navy satin lapels over a lime silk cami, cream wide-legs, pointed flats."),
    ("3. Copper lob", dict(hair_kind="lob", outfit_kind="cream", eyewear_kind="none"),
     "Sharp blunt lob in copper, no eyewear, cream oversized blazer over a navy tee, gold pendant, camel wide-legs, white sneakers."),
]


def board_restyle(pick=0):
    cols = ""
    for i, (name, kw, desc) in enumerate(VARIANTS):
        tag = '<span class="tag">pick</span>' if i == pick else ""
        smalls = "".join(f'<div>{S(c + " on-dark", 150, **kw)}<div class="cap">{n}</div></div>'
                         for n, c in (("Stressed", "mood-stressed pose-type with-laptop"), ("Ooh", "mood-ooh pose-cheeks"),
                                      ("Proud", "mood-proud pose-coffee with-coffee"), ("Deadpan", "mood-deadpan pose-rest")))
        cols += f"""<div style="width:568px">
  <div class="card" style="height:520px;gap:0;padding-bottom:10px">
    <div style="margin-right:-30px">{S("mood-neutral pose-rest", 470, **kw)}</div>
    <div style="margin-left:-30px">{S("mood-happy pose-phone pose-coffee with-coffee", 470, **kw)}</div></div>
  <div class="card dark" style="height:200px;margin-top:14px;gap:6px;padding-bottom:8px">{smalls}</div>
  <h2>{name}{tag}</h2><p class="note">{desc}</p></div>"""
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Sam restyle</title><style>{CSS}</style></head><body>
<div class="eyebrow">Sam restyle · direction A rendering, same rig</div>
<h1>Cool girl, executive influencer: three looks</h1>
<div class="row" style="margin-top:26px;gap:28px">{cols}</div></body></html>"""
    p = os.path.join(HERE, "board-restyle.html")
    open(p, "w").write(html)
    shoot(p, os.path.join(HERE, "board-restyle.png"))


def board_final(kw):
    moods = "".join(f'<div class="card" style="width:178px;height:262px"><div class="lbl">{x}</div>{S("mood-" + x, 228, **kw)}</div>' for x in MOODS)
    poses = [("rest", "mood-neutral"), ("type", "mood-focus pose-type with-laptop"), ("coffee", "mood-proud pose-coffee with-coffee"),
             ("wave", "mood-happy pose-wave"), ("shrug", "mood-shrug pose-shrug"), ("cheeks", "mood-ooh pose-cheeks"),
             ("phone", "mood-focus pose-phone"), ("point", "mood-happy pose-point")]
    pose_html = "".join(f'<div class="card" style="width:178px;height:262px"><div class="lbl">{n}</div>{S(c, 228, **kw)}</div>' for n, c in poses)
    sp = "".join(f'<div class="card" style="width:178px;height:206px"><div class="lbl">{p}</div>{K("pose-" + p, 168)}</div>' for p in SPARK_POSES)
    sp += f'<div class="card" style="width:178px;height:206px"><div class="lbl">.walking</div>{K("walking", 168)}</div>'
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Sam final</title><style>{CSS}
body{{padding:40px 64px}} .lbl{{font-size:15px;top:10px;left:14px}}</style></head><body>
<div style="display:flex;justify-content:space-between;align-items:flex-end">
<div><div class="eyebrow">Final · final/sam.svg + final/spark.svg</div><h1 style="font-size:44px">Sam: 8 moods, 8 poses, a hat stack · Spark: 6 poses + walk</h1></div></div>
<div style="display:flex;gap:14px;margin-top:20px">
  <div style="display:flex;flex-direction:column;gap:14px">
    <div class="row" style="gap:12px">{moods}</div>
    <div class="row" style="gap:12px">{pose_html}</div>
    <div class="row" style="gap:12px">{sp}</div>
  </div>
  <div style="display:flex;flex-direction:column;gap:14px">
    <div class="card" style="width:240px;height:400px;padding-bottom:6px"><div class="lbl">hats 1+2+3 · pose-cheer</div>{S("mood-proud pose-cheer with-hat-1 with-hat-2 with-hat-3", 280, **kw)}</div>
    <div class="card dark" style="width:240px;height:350px;padding-bottom:8px;align-items:flex-end"><div class="lbl">on-dark</div>{S("mood-happy pose-wave on-dark", 230, **kw)}<div style="margin-left:-40px">{K("pose-thumbs on-dark", 100)}</div></div>
  </div>
</div></body></html>"""
    p = os.path.join(HERE, "board-final.html")
    open(p, "w").write(html)
    shoot(p, os.path.join(HERE, "board-final.png"))


def main():
    args = sys.argv[1:]
    look = dict(hair_kind="waves", outfit_kind="camel", eyewear_kind="shades")
    for k, key in (("--hair", "hair_kind"), ("--outfit", "outfit_kind"), ("--eyewear", "eyewear_kind")):
        if k in args:
            look[key] = args[args.index(k) + 1]
    os.makedirs(FINAL, exist_ok=True)
    open(os.path.join(FINAL, "sam.svg"), "w").write(sam("sam", "mood-neutral pose-rest", **look))
    open(os.path.join(FINAL, "spark.svg"), "w").write(spark("spark", "pose-stand"))
    if "--no-board" not in args:
        if "--final-only" not in args:
            board_restyle()
        board_final(look)


if __name__ == "__main__":
    main()
