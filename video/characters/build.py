"""Character exploration for the explainer video: three art directions for Sam
plus two Claude mascot variants, and a design board.

Run:  python build.py         (writes the SVGs, board-characters.html, and PNGs)

Every character is one inline SVG. Moods, poses and props are toggled with
classes on the root <svg>:
  Sam:     sam  mood-{neutral|happy|stressed|ooh|proud|focus|shrug}
                pose-{rest|type|coffee|wave|shrug|cheeks}
                with-laptop / with-coffee / on-dark
  Mascot:  spark  pose-{stand|walk|read|thumbs|think}  on-dark
"""
import os
import math
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = "../../dist/guide/fonts/"

# ----------------------------------------------------------------- palette
BLUE, NAVY, DEEP = "#005A8C", "#143359", "#0B3266"
SKY, AZURE, TEAL, MINT, LIME = "#66C4FF", "#009EFF", "#00AF9D", "#05CE90", "#D9F14E"
SAND, SAND2, WGREY, ORANGE = "#EFEDE7", "#DEDBD1", "#B4B0A5", "#EF8200"
WHITE = "#FFFFFF"
# natural tones (not brand)
SKIN, SKIN_SH, SKIN_HI = "#EDB08A", "#D68F69", "#F6C7A6"
HAIR, HAIR_HI = "#2B1D22", "#4E3640"
MOUTH, TONGUE, BLUSH = "#5E2230", "#F0806C", "#F2836B"
CLAY, CLAY_SH, CLAY_HI, CREAM = "#D97757", "#B95D40", "#EE9A7C", "#F6EBDD"

# ----------------------------------------------------------------- skeleton
# viewBox 0 0 300 420. Arms are drawn hanging straight down; poses rotate them.
SH_L, SH_R = (106, 238), (194, 238)          # shoulder pivots
UP_LEN, FORE_LEN = 42, 36                    # shoulder->elbow, elbow->wrist
EL_L = (SH_L[0], SH_L[1] + UP_LEN)
EL_R = (SH_R[0], SH_R[1] + UP_LEN)
HD_L = (SH_L[0], EL_L[1] + FORE_LEN + 8)     # hand centre
HD_R = (SH_R[0], EL_R[1] + FORE_LEN + 8)
EYE_L, EYE_R = (126, 142), (174, 142)

def ik(shoulder, target, elbow_out, l1=UP_LEN, l2=FORE_LEN + 8):
    """Two-bone IK. Returns (upper_deg, fore_relative_deg) for an arm drawn hanging down.
    elbow_out=+1 bends the elbow to the viewer's left, -1 to the right."""
    sx, sy = shoulder
    tx, ty = target
    dx, dy = tx - sx, ty - sy
    d = min(math.hypot(dx, dy), l1 + l2 - 0.01)
    a = math.atan2(dy, dx)
    cos_b = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1, min(1, cos_b)))
    ang1 = a + elbow_out * b
    ex, ey = sx + l1 * math.cos(ang1), sy + l1 * math.sin(ang1)
    hx, hy = sx + d * math.cos(a), sy + d * math.sin(a)
    def rot(vx, vy):  # rotation that takes (0,1) to (vx,vy)
        return math.degrees(math.atan2(-vx, vy))
    t1 = rot(ex - sx, ey - sy)
    t2 = rot(hx - ex, hy - ey)
    rel = (t2 - t1 + 180) % 360 - 180
    return round(t1, 1), round(rel, 1)


def pose(lt, rt, lbend=1, rbend=-1):
    return ik(SH_L, lt, lbend) + ik(SH_R, rt, rbend)


POSES = {
    #          left upper, left fore, right upper, right fore  (deg)
    "rest":   (14, -8, -14, 8),
    "type":   pose((128, 312), (172, 312), 1, -1),
    "coffee": (14, -8) + ik(SH_R, (186, 282), -1),
    "wave":   ik(SH_L, (64, 160), -1) + (-14, 8),
    "shrug":  pose((58, 226), (242, 226), -1, 1),
    "cheeks": pose((100, 190), (200, 190), -1, 1),
}


def pose_css(prefix=".sam"):
    out = [
        f"{prefix} .arm-l{{transform-box:view-box;transform-origin:{SH_L[0]}px {SH_L[1]}px;transform:rotate(var(--lu));transition:transform .35s cubic-bezier(.3,1.5,.5,1)}}",
        f"{prefix} .arm-l .fore{{transform-box:view-box;transform-origin:{EL_L[0]}px {EL_L[1]}px;transform:rotate(var(--lf));transition:transform .35s cubic-bezier(.3,1.5,.5,1)}}",
        f"{prefix} .arm-r{{transform-box:view-box;transform-origin:{SH_R[0]}px {SH_R[1]}px;transform:rotate(var(--ru));transition:transform .35s cubic-bezier(.3,1.5,.5,1)}}",
        f"{prefix} .arm-r .fore{{transform-box:view-box;transform-origin:{EL_R[0]}px {EL_R[1]}px;transform:rotate(var(--rf));transition:transform .35s cubic-bezier(.3,1.5,.5,1)}}",
        # the mug stays upright whatever the arm does
        f"{prefix} .prop-coffee{{transform-box:view-box;transform-origin:{HD_R[0]}px {HD_R[1]}px;transform:rotate(calc(-1 * (var(--ru) + var(--rf))))}}",
    ]
    for name, (lu, lf, ru, rf) in POSES.items():
        sel = f"{prefix}" if name == "rest" else f"{prefix}.pose-{name}"
        out.append(f"{sel}{{--lu:{lu}deg;--lf:{lf}deg;--ru:{ru}deg;--rf:{rf}deg}}")
    return "\n".join(out)


MOOD_CSS = """
.sam .hand-open{display:none}
.sam.pose-wave .arm-l .hand-open,.sam.pose-shrug .hand-open{display:inline}
.sam.pose-wave .arm-l .hand-fist,.sam.pose-shrug .hand-fist{display:none}
.sam .m{display:none}
.sam.mood-neutral .m-neutral,.sam.mood-happy .m-happy,.sam.mood-stressed .m-stressed,
.sam.mood-ooh .m-ooh,.sam.mood-proud .m-proud,.sam.mood-focus .m-focus,.sam.mood-shrug .m-shrug{display:inline}
.sam .prop{display:none}
.sam.with-laptop .prop-laptop,.sam.with-coffee .prop-coffee{display:inline}
.sam .head{transform-box:view-box;transform-origin:150px 210px}
.sam.no-fx .body{filter:none}
.sam.pose-shrug .head{transform:rotate(-6deg)}
.sam.mood-ooh .head{transform:rotate(4deg) translateY(-2px)}
.sam.mood-stressed .head{transform:translateY(3px)}
"""


def cls(*moods):
    return "m " + " ".join(f"m-{m}" for m in moods)


def star_path(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


def sparkle_path(cx, cy, r, w=0.28):
    """4-point sparkle with concave sides."""
    k = r * w
    return (f"M{cx},{cy - r} Q{cx + k},{cy - k} {cx + r},{cy} Q{cx + k},{cy + k} {cx},{cy + r} "
            f"Q{cx - k},{cy + k} {cx - r},{cy} Q{cx - k},{cy - k} {cx},{cy - r} Z")


def capsule(x, y1, y2, w):
    """vertical capsule path centred on x from y1 to y2 (end caps included)."""
    r = w / 2
    return (f"M{x - r},{y1} A{r},{r} 0 0 1 {x + r},{y1} L{x + r},{y2} "
            f"A{r},{r} 0 0 1 {x - r},{y2} Z")



def hand_open(hx, hy, side, fill, line=None, lw=2.4, riso_fill=None):
    """Open mitten hand, fingers pointing down the arm (local space), thumb toward the body."""
    t = 1 if side == "l" else -1
    thumb = f"M{hx + t * 6} {hy - 6} Q{hx + t * 20} {hy - 8} {hx + t * 18} {hy + 4} Q{hx + t * 16} {hy + 9} {hx + t * 8} {hy + 6} Z"
    palm = f"M{hx - 11} {hy - 8} Q{hx - 12} {hy + 20} {hx} {hy + 20} Q{hx + 12} {hy + 20} {hx + 11} {hy - 8} Z"
    fingers = f"M{hx - 4} {hy + 19} L{hx - 4} {hy + 11} M{hx + 4} {hy + 19} L{hx + 4} {hy + 11}"
    if riso_fill:
        return (f'<g class="hand-open">{riso(thumb, riso_fill, w=3.4)}{riso(palm, riso_fill, w=3.4)}'
                f'<path d="{fingers}" stroke="{NAVY}" stroke-width="2.4" stroke-linecap="round"/></g>')
    ln = line or SKIN_SH
    return (f'<g class="hand-open"><path d="{thumb}" fill="{fill}"/><path d="{palm}" fill="{fill}"/>'
            f'<path d="{fingers}" stroke="{ln}" stroke-width="{lw}" stroke-linecap="round"/></g>')

# ======================================================================
# Shared face geometry, drawn with a per-direction "pen"
# ======================================================================
class Pen:
    """Holds the style of a direction so the face code is written once."""
    def __init__(self, ink, eye, brow, brow_w, mouth_fill, line_w, outline=None):
        self.ink, self.eye, self.brow, self.brow_w = ink, eye, brow, brow_w
        self.mouth_fill, self.line_w, self.outline = mouth_fill, line_w, outline

    def stroke(self, d, w=None, color=None, extra=""):
        return (f'<path d="{d}" fill="none" stroke="{color or self.ink}" stroke-width="{w or self.line_w}" '
                f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def face_moods(p, uid, style, part="face"):
    """Eyes, mouth, cheeks, nose (part="face") or brows (part="brows") for every mood."""
    (lx, ly), (rx, ry) = EYE_L, EYE_R
    o = []
    oline = f' stroke="{p.outline}" stroke-width="3.2" stroke-linejoin="round"' if p.outline else ""

    # ---------- brows ----------
    def brow_pair(l, r, cl):
        return f'<g class="brows {cl}">{p.stroke(l, p.brow_w, p.brow)}{p.stroke(r, p.brow_w, p.brow)}</g>'
    o.append(brow_pair("M110 110 Q122 103 136 106", "M164 106 Q178 103 190 110", cls("neutral", "focus")))
    o.append(brow_pair("M111 106 Q123 99 136 102", "M164 102 Q177 99 189 106", cls("happy", "proud")))
    o.append(brow_pair("M109 112 Q124 108 138 99", "M162 99 Q176 108 191 112", cls("stressed")))
    o.append(brow_pair("M111 102 Q123 92 137 97", "M163 97 Q177 92 189 102", cls("ooh")))
    o.append(brow_pair("M111 101 Q123 93 137 98", "M164 108 L190 108", cls("shrug")))
    if part == "brows":
        return "".join(o)
    o = []

    # ---------- eyes ----------
    def dot_eyes(dx=0, dy=0, r=6.2, cl=""):
        s = ""
        for (x, y) in (EYE_L, EYE_R):
            x, y = x + dx, y + dy
            if style == "C":
                s += (f'<ellipse cx="{x}" cy="{y}" rx="{r + 1.6}" ry="{r + 3.4}" fill="url(#{uid}-eye)"/>'
                      f'<ellipse cx="{x + 2.6}" cy="{y - 3.6}" rx="2.8" ry="3.2" fill="#fff"/>'
                      f'<circle cx="{x - 2.4}" cy="{y + 4}" r="1.3" fill="#fff" opacity=".8"/>')
            else:
                s += (f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r + 1.4}" fill="{p.eye}"/>'
                      f'<circle cx="{x + 2.2}" cy="{y - 2.6}" r="2.1" fill="#fff"/>')
        return f'<g class="eyes {cl}">{s}</g>'
    o.append(dot_eyes(cl=cls("neutral", "happy")))
    o.append(dot_eyes(dx=4, dy=-1, cl=cls("shrug")))
    o.append(dot_eyes(dy=4, r=5.4, cl=cls("focus")))
    # stressed: wide, small pupils looking down at the screen, tired bags
    s = ""
    for (x, y) in (EYE_L, EYE_R):
        s += (f'<circle cx="{x}" cy="{y}" r="9.5" fill="#fff"{oline if style != "A" else ""}/>'
              f'<circle cx="{x + 1}" cy="{y + 3.5}" r="4.2" fill="{p.eye}"/>'
              f'<circle cx="{x + 2.2}" cy="{y + 2.2}" r="1.3" fill="#fff"/>')
        s += p.stroke(f"M{x - 8} {y + 15} Q{x} {y + 19} {x + 8} {y + 15}", 2.2, SKIN_SH)
    o.append(f'<g class="eyes {cls("stressed")}">{s}</g>')
    # ooh: star eyes
    s = ""
    for (x, y) in (EYE_L, EYE_R):
        if style == "A":
            s += f'<path d="{star_path(x, y, 12.5, 5.6)}" fill="{NAVY}" stroke="{NAVY}" stroke-width="2.5" stroke-linejoin="round"/>'
            s += f'<path d="{sparkle_path(x + 3, y - 3, 3.6)}" fill="{LIME}"/>'
        elif style == "B":
            s += f'<path d="{star_path(x + 2, y + 2, 13, 6)}" fill="{LIME}"/>'
            s += f'<path d="{star_path(x, y, 13, 6)}" fill="none" stroke="{NAVY}" stroke-width="3" stroke-linejoin="round"/>'
        else:
            s += f'<path d="{star_path(x, y, 13.5, 6.4)}" fill="url(#{uid}-star)" stroke="{NAVY}" stroke-width="2.4" stroke-linejoin="round"/>'
            s += f'<ellipse cx="{x - 3}" cy="{y - 4}" rx="2.4" ry="1.6" fill="#fff" opacity=".9"/>'
    o.append(f'<g class="eyes {cls("ooh")}">{s}</g>')
    # proud: closed happy arcs
    s = "".join(p.stroke(f"M{x - 9} {y + 3} Q{x} {y - 9} {x + 9} {y + 3}", p.brow_w * 0.72, p.eye) for (x, y) in (EYE_L, EYE_R))
    o.append(f'<g class="eyes {cls("proud")}">{s}</g>')

    # ---------- cheeks ----------
    bl = 0.42 if style != "C" else 0.5
    o.append(f'<g class="cheeks {cls("happy", "ooh", "proud", "neutral", "shrug", "focus")}">'
             f'<ellipse cx="106" cy="170" rx="11" ry="6.5" fill="{BLUSH}" opacity="{bl}"/>'
             f'<ellipse cx="194" cy="170" rx="11" ry="6.5" fill="{BLUSH}" opacity="{bl}"/></g>')

    # ---------- nose ----------
    if style == "B":
        o.append(p.stroke("M150 150 Q146 160 151 162", 2.6))
    elif style == "A":
        o.append(f'<path d="M146 158 Q150 152 154 158 Q150 162 146 158 Z" fill="{SKIN_SH}"/>')
    else:
        o.append(f'<ellipse cx="150" cy="158" rx="6" ry="4.4" fill="url(#{uid}-nose)"/>')

    # ---------- mouths ----------
    mo = p.mouth_fill
    tongue = TONGUE
    mouth_ol = f' stroke="{p.outline}" stroke-width="3" stroke-linejoin="round"' if p.outline else ""
    o.append(f'<g class="mouth {cls("neutral")}">{p.stroke("M139 174 Q150 182 161 174", p.line_w)}</g>')
    o.append(f'<g class="mouth {cls("focus")}">{p.stroke("M142 177 Q150 179 156 176", p.line_w)}'
             f'<path d="M154 177 q5 1 5 6 q-1 4 -5 2 z" fill="{tongue}"{mouth_ol}/></g>')
    o.append(f'<g class="mouth {cls("happy")}"><path d="M137 171 Q150 172 163 171 Q161 187 150 187 Q139 187 137 171 Z" fill="{mo}"{mouth_ol}/>'
             f'<path d="M143 183 Q150 178 157 183 Q150 188 143 183 Z" fill="{tongue}"/></g>')
    o.append(f'<g class="mouth {cls("stressed")}">{p.stroke("M136 179 q3.5 -5 7 0 t7 0 t7 0 t7 0", p.line_w)}</g>')
    o.append(f'<g class="mouth {cls("ooh")}"><ellipse cx="150" cy="180" rx="8" ry="10" fill="{mo}"{mouth_ol}/>'
             f'<ellipse cx="150" cy="186" rx="5" ry="3.2" fill="{tongue}"/></g>')
    o.append(f'<g class="mouth {cls("proud")}"><path d="M131 168 Q150 170 169 168 Q167 192 150 192 Q133 192 131 168 Z" fill="{mo}"{mouth_ol}/>'
             f'<path d="M134 169 Q150 171 166 169 L165 174 Q150 176 135 174 Z" fill="#fff"/>'
             f'<path d="M141 186 Q150 179 159 186 Q150 192 141 186 Z" fill="{tongue}"/></g>')
    o.append(f'<g class="mouth {cls("shrug")}">{p.stroke("M140 178 L156 175", p.line_w)}</g>')
    return "".join(o)


def face_fx(p, uid, style):
    """Sweat, sparkles, stress scribble: things floating around the head."""
    o = []
    # sweat drop
    drop = "M214 92 C214 92 202 108 202 115 a12 12 0 0 0 24 0 C226 108 214 92 214 92 Z"
    if style == "B":
        o.append(f'<g class="fx-sweat {cls("stressed")}"><path d="{drop}" fill="{SKY}" transform="translate(3 3)"/>'
                 f'<path d="{drop}" fill="none" stroke="{NAVY}" stroke-width="3"/></g>')
    elif style == "C":
        o.append(f'<g class="fx-sweat {cls("stressed")}"><path d="{drop}" fill="url(#{uid}-drop)"/>'
                 f'<ellipse cx="209" cy="113" rx="3" ry="4.5" fill="#fff" opacity=".85"/></g>')
    else:
        o.append(f'<g class="fx-sweat {cls("stressed")}"><path d="{drop}" fill="{SKY}"/>'
                 f'<path d="M207 112 q0 -5 4 -9" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/></g>')
    # stress marks (anime cross-vein + jitter lines)
    marks = (p.stroke("M70 70 l-12 -10 M66 86 l-16 -2 M78 58 l-6 -14", 4, ORANGE if style != "B" else NAVY))
    o.append(f'<g class="fx-stress {cls("stressed")}">{marks}</g>')
    # sparkles
    sp = ""
    for (x, y, r, c) in ((58, 70, 13, LIME), (242, 58, 16, SKY if style != "C" else LIME), (250, 120, 8, LIME), (72, 116, 7, SKY)):
        if style == "B":
            sp += f'<path d="{sparkle_path(x + 2, y + 2, r)}" fill="{c}"/><path d="{sparkle_path(x, y, r)}" fill="none" stroke="{NAVY}" stroke-width="2.4" stroke-linejoin="round"/>'
        else:
            sp += f'<path d="{sparkle_path(x, y, r)}" fill="{c}"{" stroke=" + chr(34) + NAVY + chr(34) + " stroke-width=" + chr(34) + "2" + chr(34) if style == "A" else ""}/>'
    o.append(f'<g class="fx-sparkles {cls("ooh", "proud")}">{sp}</g>')
    return "".join(o)


# side-parted swoop: part at (184,62), sweeps across the forehead to the left temple
FRINGE = ("M78 142 C68 84 102 42 152 42 C202 42 234 78 225 136 "
          "C222 108 210 80 186 62 C166 80 130 86 100 92 C88 104 82 124 78 142 Z")
FRINGE_SHADE = "M186 62 C210 80 222 108 225 136 C234 78 202 42 152 42 C178 46 190 54 186 62 Z"

# ======================================================================
# Direction A: bold editorial flat
# ======================================================================
def defs_A(uid):
    return f"""
<filter id="{uid}-fx" x="-15%" y="-15%" width="135%" height="135%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="7" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.25" result="speck"/>
  <feComposite in="speck" in2="SourceGraphic" operator="in" result="grain"/>
  <feComponentTransfer in="grain" result="grainSoft"><feFuncA type="linear" slope="0.16"/></feComponentTransfer>
  <feFlood class="shadow-flood" flood-color="{NAVY}" flood-opacity="0.13" result="fc"/>
  <feOffset in="SourceAlpha" dx="10" dy="8" result="off"/>
  <feComposite in="fc" in2="off" operator="in" result="shadow"/>
  <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/><feMergeNode in="grainSoft"/></feMerge>
</filter>
<pattern id="{uid}-dots" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
  <circle cx="3" cy="3" r="1.35" fill="#000" fill-opacity=".28"/></pattern>
<pattern id="{uid}-dotsL" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
  <circle cx="3" cy="3" r="1.2" fill="#fff" fill-opacity=".35"/></pattern>
"""


def arm_A(side, uid):
    sx, sy = SH_L if side == "l" else SH_R
    ex, ey = EL_L if side == "l" else EL_R
    hx, hy = HD_L if side == "l" else HD_R
    sleeve, sleeve_sh = "#0A6699", "#004A75"
    up = capsule(sx, sy, ey, 30)
    fore = capsule(ex, ey, hy - 10, 27)
    inner = 1 if side == "l" else -1
    shade = f'<path d="{capsule(sx + inner * 7, sy + 6, ey, 10)}" fill="url(#{uid}-dots)"/>'
    mug = coffee_A(uid) if side == "r" else ""
    return f"""<g class="arm arm-{side}">
  <path d="{up}" fill="{sleeve}"/>{shade}
  <g class="fore"><path d="{fore}" fill="{sleeve}"/>
    <rect x="{ex - 14}" y="{hy - 20}" width="28" height="9" rx="4.5" fill="{sleeve_sh}"/>
    {mug}
    <g class="hand-fist"><circle class="hand" cx="{hx}" cy="{hy}" r="12.5" fill="{SKIN}"/>
    <path d="M{hx - 6} {hy + 4} q6 4 12 0" stroke="{SKIN_SH}" stroke-width="2.4" fill="none" stroke-linecap="round"/></g>
    {hand_open(hx, hy, side, SKIN)}
  </g></g>"""


def coffee_A(uid):
    hx, hy = HD_R
    x, y = hx - 40, hy - 26          # mug top-left
    return f"""<g class="prop prop-coffee">
    <g class="steam" fill="none" stroke="{WGREY}" stroke-width="3.6" stroke-linecap="round">
      <path d="M{x + 10} {y - 8} q-6 -8 0 -16 t0 -16"/><path d="M{x + 24} {y - 6} q-6 -8 0 -16 t0 -14"/></g>
    <path d="M{x + 32} {y + 10} q16 0 16 13 t-16 13" fill="none" stroke="{WHITE}" stroke-width="6"/>
    <rect x="{x}" y="{y}" width="36" height="44" rx="8" fill="{WHITE}"/>
    <rect x="{x}" y="{y + 12}" width="36" height="11" fill="{LIME}"/>
    <rect x="{x}" y="{y}" width="36" height="5" rx="2.5" fill="{SAND2}"/>
  </g>"""


def laptop_A(uid, lid, logo_bg, desk, desk_edge):
    return f"""<g class="prop prop-laptop">
  <rect x="0" y="352" width="300" height="68" fill="{desk}"/>
  <rect x="0" y="352" width="300" height="9" fill="{desk_edge}"/>
  <path d="M62 262 Q62 254 70 254 L230 254 Q238 254 238 262 L242 352 L58 352 Z" fill="{lid}"/>
  <path d="M150 254 L230 254 Q238 254 238 262 L242 352 L150 352 Z" fill="url(#{uid}-dots)" opacity=".35"/>
  <circle cx="150" cy="302" r="19" fill="{logo_bg}"/>
  <path d="M141 311 v-8 M150 311 v-16 M159 311 v-11" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/>
  <rect x="44" y="348" width="212" height="10" rx="5" fill="#9AA4B0"/>
</g>"""


def sam_A(uid, classes="mood-neutral"):
    p = Pen(ink=NAVY, eye=NAVY, brow=HAIR, brow_w=7, mouth_fill=MOUTH, line_w=4.2)
    hair_back = ("M68 136 C62 64 104 34 150 34 C196 34 238 64 232 136 L236 214 "
                 "C237 232 222 240 208 232 L196 224 L104 224 L92 232 C78 240 63 232 64 214 Z")
    head = "M80 128 C80 76 108 60 150 60 C192 60 220 76 220 128 C220 178 194 206 150 206 C106 206 80 178 80 128 Z"
    fringe = FRINGE
    torso = ("M120 214 L180 214 C196 216 204 226 205 240 L210 330 C210 338 205 342 198 342 "
             "L102 342 C95 342 90 338 90 330 L95 240 C96 226 104 216 120 214 Z")
    return f"""<svg class="sam sam-a {classes}" viewBox="0 0 300 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sam">
<defs>{defs_A(uid)}</defs>
<style>{MOOD_CSS}{pose_css()}
.sam-a.on-dark .shadow-flood{{flood-color:{SKY};flood-opacity:.22}}
.sam-a .ground{{fill:{NAVY};opacity:.12}} .sam-a.on-dark .ground{{fill:#000;opacity:.25}}</style>
<ellipse class="ground" cx="150" cy="404" rx="78" ry="9"/>
<g class="body" filter="url(#{uid}-fx)">
  <g class="legs">
    <rect x="114" y="326" width="30" height="62" rx="8" fill="{NAVY}"/>
    <rect x="156" y="326" width="30" height="62" rx="8" fill="{NAVY}"/>
    <path d="M106 398 Q104 380 122 380 L140 380 Q148 380 148 390 L148 398 Z" fill="{LIME}"/>
    <path d="M152 398 L152 390 Q152 380 160 380 L178 380 Q196 380 194 398 Z" fill="{LIME}"/>
    <rect x="102" y="394" width="48" height="7" rx="3.5" fill="{WHITE}"/><rect x="150" y="394" width="48" height="7" rx="3.5" fill="{WHITE}"/>
  </g>
  <path class="hair-back" d="{hair_back}" fill="{HAIR}"/>
  <path d="M196 224 L208 232 C222 240 237 232 236 214 L232 136 C224 160 214 200 196 224 Z" fill="url(#{uid}-dots)"/>
  <rect x="136" y="190" width="28" height="34" rx="10" fill="{SKIN_SH}"/>
  <path class="torso" d="{torso}" fill="{BLUE}"/>
  <path d="M128 214 L150 262 L172 214 Z" fill="{WHITE}"/>
  <path d="M136 214 Q150 228 164 214" fill="{SKIN_SH}"/>
  <path d="M150 262 L150 342" stroke="#004A75" stroke-width="3"/>
  <circle cx="158" cy="282" r="3.2" fill="{SAND}"/><circle cx="158" cy="304" r="3.2" fill="{SAND}"/><circle cx="158" cy="326" r="3.2" fill="{SAND}"/>
  <path d="M178 216 C196 218 204 228 205 242 L210 330 C210 338 205 342 198 342 L176 342 C188 300 190 250 178 216 Z" fill="url(#{uid}-dots)"/>
  <g class="pin"><circle cx="126" cy="276" r="10" fill="{LIME}"/>
    <path d="M121 281 v-4 M126 281 v-9 M131 281 v-6" stroke="{NAVY}" stroke-width="2.4" stroke-linecap="round"/></g>
  <g class="head">
    <circle cx="80" cy="146" r="13" fill="{SKIN}"/><circle cx="220" cy="146" r="13" fill="{SKIN}"/>
    <path class="face" d="{head}" fill="{SKIN}"/>
    <path d="M98 94 C130 88 168 80 186 64 C204 82 216 104 222 130 L220 140 C212 116 200 94 186 78 C166 92 130 100 94 104 Z" fill="{SKIN_SH}" opacity=".55"/>
    {face_moods(p, uid, "A")}
    <g class="glasses" fill="none" stroke="{NAVY}" stroke-width="5.5">
      <circle cx="{EYE_L[0]}" cy="{EYE_L[1]}" r="21" fill="#fff" fill-opacity=".16"/>
      <circle cx="{EYE_R[0]}" cy="{EYE_R[1]}" r="21" fill="#fff" fill-opacity=".16"/>
      <path d="M147 140 Q150 136 153 140"/><path d="M105 138 L84 132"/><path d="M195 138 L216 132"/>
      <path d="M112 136 L120 128" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
      <path d="M160 136 L168 128" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
    </g>
    <path class="hair-front" d="{fringe}" fill="{HAIR}"/>
    <path d="M150 52 C172 52 194 62 206 80" stroke="{HAIR_HI}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="{FRINGE_SHADE}" fill="url(#{uid}-dots)"/>
    <g class="clip"><rect x="98" y="80" width="26" height="8" rx="4" fill="{LIME}" transform="rotate(-24 111 84)"/></g>
    {face_moods(p, uid, "A", "brows")}
    {face_fx(p, uid, "A")}
  </g>
  {arm_A("l", uid)}
  {arm_A("r", uid)}
  {laptop_A(uid, "#C8D0DA", LIME, SAND2, WGREY)}
</g>
</svg>"""


# ======================================================================
# Direction B: ink line + risograph
# ======================================================================
OFF = (5, 4)  # riso misregistration


def riso(d, fill, w=4.2, ink=NAVY, cl="", fill_only=False, op=1):
    f = f'<path d="{d}" fill="{fill}" transform="translate({OFF[0]} {OFF[1]})" opacity="{op}"/>'
    if fill_only:
        return f
    return f'<g class="{cl}">{f}<path d="{d}" fill="none" stroke="{ink}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/></g>'


def defs_B(uid):
    return f"""
<filter id="{uid}-fx" x="-15%" y="-15%" width="135%" height="135%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="4" result="wob"/>
  <feDisplacementMap in="SourceGraphic" in2="wob" scale="3.2" xChannelSelector="R" yChannelSelector="G" result="drawn"/>
  <feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="1" seed="11" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -2.8 1.35" result="speck"/>
  <feComposite in="speck" in2="drawn" operator="in" result="grain"/>
  <feComponentTransfer in="grain" result="grainSoft"><feFuncA type="linear" slope="0.14"/></feComponentTransfer>
  <feMorphology in="SourceAlpha" operator="dilate" radius="7" result="fat"/>
  <feDisplacementMap in="fat" in2="wob" scale="5" xChannelSelector="G" yChannelSelector="R" result="fatw"/>
  <feFlood class="sticker-flood" flood-color="#FFFDF6" result="cream"/>
  <feComposite in="cream" in2="fatw" operator="in" result="sticker"/>
  <feMerge><feMergeNode in="sticker"/><feMergeNode in="drawn"/><feMergeNode in="grainSoft"/></feMerge>
</filter>
<pattern id="{uid}-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
  <rect width="7" height="7" fill="none"/><path d="M0 0 V7" stroke="{SKY}" stroke-width="2"/></pattern>
"""


def arm_B(side, uid):
    sx, sy = SH_L if side == "l" else SH_R
    ex, ey = EL_L if side == "l" else EL_R
    hx, hy = HD_L if side == "l" else HD_R
    up = capsule(sx, sy, ey, 28)
    fore = capsule(ex, ey, hy - 10, 25)
    mug = coffee_B(uid) if side == "r" else ""
    return f"""<g class="arm arm-{side}">
  {riso(up, AZURE)}
  <g class="fore">{riso(fore, AZURE)}
    <path d="M{ex - 12} {hy - 16} L{ex + 12} {hy - 16}" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>
    {mug}
    <g class="hand-fist">{riso(f"M{hx - 12} {hy} a12 12 0 1 0 24 0 a12 12 0 1 0 -24 0 Z", "#FFB592", w=3.6)}</g>
    {hand_open(hx, hy, side, None, riso_fill="#FFB592")}
  </g></g>"""


def coffee_B(uid):
    hx, hy = HD_R
    x, y = hx - 40, hy - 26
    body = f"M{x} {y} L{x + 36} {y} L{x + 33} {y + 40} Q{x + 32} {y + 44} {x + 28} {y + 44} L{x + 8} {y + 44} Q{x + 4} {y + 44} {x + 3} {y + 40} Z"
    return f"""<g class="prop prop-coffee">
    <g fill="none" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"><path d="M{x + 10} {y - 8} q-6 -8 0 -16 t0 -16"/><path d="M{x + 24} {y - 6} q-6 -8 0 -16 t0 -14"/></g>
    <path d="M{x + 33} {y + 10} q15 0 15 12 t-16 12" fill="none" stroke="{NAVY}" stroke-width="4"/>
    {riso(body, "#FFFFFF")}
    {riso(f"M{x + 1} {y + 12} L{x + 35} {y + 12} L{x + 34} {y + 23} L{x + 2} {y + 23} Z", LIME, w=0, fill_only=True)}
    <path d="M{x + 1} {y + 12} L{x + 35} {y + 12} M{x + 2} {y + 23} L{x + 34} {y + 23}" stroke="{NAVY}" stroke-width="2.4"/>
  </g>"""


def laptop_B(uid):
    lid = "M62 262 Q62 254 70 254 L230 254 Q238 254 238 262 L242 352 L58 352 Z"
    return f"""<g class="prop prop-laptop">
  <path d="M0 356 L300 356 L300 420 L0 420 Z" fill="#FFFDF6"/>
  {riso("M-10 356 L310 356 L310 430 L-10 430 Z", SAND2)}
  <path d="M24 372 L120 372 M180 380 L272 380 M60 392 L150 392" stroke="{NAVY}" stroke-width="2" stroke-linecap="round" opacity=".35"/>
  {riso(lid, "#D7DDE4")}
  {riso("M128 302 a22 22 0 1 0 44 0 a22 22 0 1 0 -44 0 Z", LIME, w=3.2)}
  <path d="M141 312 v-8 M150 312 v-16 M159 312 v-11" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/>
  {riso("M46 350 Q46 346 52 346 L248 346 Q254 346 254 350 L254 356 L46 356 Z", "#AEB8C4", w=3.6)}
</g>"""


def sam_B(uid, classes="mood-neutral"):
    p = Pen(ink=NAVY, eye=NAVY, brow=NAVY, brow_w=5.2, mouth_fill=NAVY, line_w=3.8)
    hair_back = ("M70 138 C62 66 104 36 150 36 C196 36 238 66 230 138 L234 212 "
                 "C236 228 224 236 212 230 L198 222 L102 222 L88 230 C76 236 64 228 66 212 Z")
    head = "M82 130 C82 78 108 62 150 62 C192 62 218 78 218 130 C218 178 194 204 150 204 C106 204 82 178 82 130 Z"
    fringe = FRINGE
    torso = ("M120 214 L180 214 C196 216 204 226 205 240 L210 330 C210 338 205 342 198 342 "
             "L102 342 C95 342 90 338 90 330 L95 240 C96 226 104 216 120 214 Z")
    return f"""<svg class="sam sam-b {classes}" viewBox="0 0 300 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sam">
<defs>{defs_B(uid)}</defs>
<style>{MOOD_CSS}{pose_css()}
.sam-b .ground{{fill:{NAVY};opacity:.14}} .sam-b.on-dark .ground{{fill:#000;opacity:.3}}</style>
<path class="ground" d="M78 404 Q150 396 222 404 Q150 412 78 404 Z"/>
<g class="body" filter="url(#{uid}-fx)">
  <g class="legs">
    {riso("M116 330 L142 330 L142 386 L116 386 Z", WGREY)}
    {riso("M158 330 L184 330 L184 386 L158 386 Z", WGREY)}
    {riso("M106 398 Q104 380 122 380 L140 380 Q148 380 148 390 L148 398 Z", "#FFFFFF")}
    {riso("M152 398 L152 390 Q152 380 160 380 L178 380 Q196 380 194 398 Z", "#FFFFFF")}
    <path d="M110 392 L146 392 M154 392 L190 392" stroke="{LIME}" stroke-width="4"/>
  </g>
  {riso(hair_back, DEEP, w=4.6)}
  <path d="M206 120 C214 150 214 190 204 220 M92 120 C86 150 86 190 96 220" stroke="{SKY}" stroke-width="2.6" fill="none" stroke-linecap="round" opacity=".9"/>
  {riso("M136 188 L164 188 L164 222 L136 222 Z", "#F3A27F", w=3.4)}
  {riso(torso, AZURE, w=4.6)}
  {riso("M128 214 L150 262 L172 214 Z", LIME, w=3.6)}
  <path d="M150 262 L150 342" stroke="{NAVY}" stroke-width="3.2"/>
  <circle cx="158" cy="284" r="3.4" fill="{NAVY}"/><circle cx="158" cy="306" r="3.4" fill="{NAVY}"/>
  <path d="M104 330 L196 330" stroke="{NAVY}" stroke-width="2.4" stroke-dasharray="3 5" stroke-linecap="round"/>
  <path d="M112 300 C116 286 120 274 122 262 M190 300 C186 286 182 274 180 262" stroke="{NAVY}" stroke-width="2" fill="none" opacity=".5" stroke-linecap="round"/>
  <g class="head">
    {riso("M68 146 a13 13 0 1 0 26 0 a13 13 0 1 0 -26 0 Z", "#FFB592", w=3.6)}
    {riso("M206 146 a13 13 0 1 0 26 0 a13 13 0 1 0 -26 0 Z", "#FFB592", w=3.6)}
    {riso(head, "#FFB592", w=4.6)}
    {face_moods(p, uid, "B")}
    <g class="glasses" fill="none" stroke="{NAVY}" stroke-width="4.2">
      <path d="M{EYE_L[0] - 12} {EYE_L[1] - 6} L{EYE_L[0] - 4} {EYE_L[1] - 14} M{EYE_R[0] - 12} {EYE_R[1] - 6} L{EYE_R[0] - 4} {EYE_R[1] - 14}" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
      <circle cx="{EYE_L[0]}" cy="{EYE_L[1]}" r="20"/><circle cx="{EYE_R[0]}" cy="{EYE_R[1]}" r="20"/>
      <path d="M146 139 Q150 135 154 139"/><path d="M106 137 L86 132"/><path d="M194 137 L214 132"/>
    </g>
    {riso(fringe, DEEP, w=4.6)}
    <path d="M100 94 C126 86 156 76 178 60 M116 60 C134 52 154 50 172 52 M196 70 C206 82 214 98 218 116" stroke="{SKY}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
    {riso("M99 90 L122 79 L126 86 L103 97 Z", LIME, w=3)}
    {face_moods(p, uid, "B", "brows")}
    {face_fx(p, uid, "B")}
  </g>
  {arm_B("l", uid)}
  {arm_B("r", uid)}
  {laptop_B(uid)}
</g>
</svg>"""


# ======================================================================
# Direction C: soft 3D toy
# ======================================================================
def defs_C(uid):
    return f"""
<radialGradient id="{uid}-skin" cx="42%" cy="34%" r="70%"><stop offset="0" stop-color="#FAD3B6"/><stop offset=".6" stop-color="{SKIN}"/><stop offset="1" stop-color="#D88E68"/></radialGradient>
<radialGradient id="{uid}-skinS" cx="40%" cy="30%" r="75%"><stop offset="0" stop-color="#F8CBAA"/><stop offset="1" stop-color="#D99470"/></radialGradient>
<radialGradient id="{uid}-hair" cx="40%" cy="22%" r="85%"><stop offset="0" stop-color="#5B3B3C"/><stop offset=".55" stop-color="#33222A"/><stop offset="1" stop-color="#1C1218"/></radialGradient>
<linearGradient id="{uid}-cardi" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="#2E8BC4"/><stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="#03466F"/></linearGradient>
<linearGradient id="{uid}-sleeve" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2A86BE"/><stop offset=".6" stop-color="{BLUE}"/><stop offset="1" stop-color="#044A74"/></linearGradient>
<linearGradient id="{uid}-pants" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D3CFC4"/><stop offset="1" stop-color="#9E9A8F"/></linearGradient>
<clipPath id="{uid}-rimclip"><rect x="168" y="0" width="140" height="180"/></clipPath>
<clipPath id="{uid}-hairclip"><path d="M66 136 C60 60 104 30 150 30 C196 30 240 60 234 136 L238 206 C240 232 222 242 206 232 L194 224 L106 224 L94 232 C78 242 60 232 62 206 Z"/></clipPath>
<linearGradient id="{uid}-shoe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EAF79A"/><stop offset="1" stop-color="#B9D12E"/></linearGradient>
<radialGradient id="{uid}-eye" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#3A4E73"/><stop offset="1" stop-color="#0E1B33"/></radialGradient>
<radialGradient id="{uid}-star" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#F5FFB0"/><stop offset="1" stop-color="#C8E02E"/></radialGradient>
<radialGradient id="{uid}-nose" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#F7C6A4"/><stop offset="1" stop-color="#D98D68"/></radialGradient>
<radialGradient id="{uid}-drop" cx="40%" cy="40%" r="70%"><stop offset="0" stop-color="#D9F2FF"/><stop offset="1" stop-color="{SKY}"/></radialGradient>
<linearGradient id="{uid}-lid" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EEF2F6"/><stop offset=".5" stop-color="#CDD5DE"/><stop offset="1" stop-color="#A9B4C1"/></linearGradient>
<linearGradient id="{uid}-mug" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".7" stop-color="#F1EEE8"/><stop offset="1" stop-color="#D6D1C6"/></linearGradient>
<linearGradient id="{uid}-desk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F1EC"/><stop offset="1" stop-color="{SAND2}"/></linearGradient>
<filter id="{uid}-soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="{uid}-soft2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.5"/></filter>
<filter id="{uid}-fx" x="-15%" y="-15%" width="135%" height="135%" color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceAlpha" stdDeviation="5" result="b"/><feOffset in="b" dx="0" dy="6" result="ob"/>
  <feFlood class="shadow-flood" flood-color="{NAVY}" flood-opacity=".22" result="fc"/>
  <feComposite in="fc" in2="ob" operator="in" result="sh"/>
  <feMerge><feMergeNode in="sh"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<clipPath id="{uid}-headclip"><path d="M80 128 C80 74 110 58 150 58 C190 58 220 74 220 128 C220 180 194 206 150 206 C106 206 80 180 80 128 Z"/></clipPath>
"""


def arm_C(side, uid):
    sx, sy = SH_L if side == "l" else SH_R
    ex, ey = EL_L if side == "l" else EL_R
    hx, hy = HD_L if side == "l" else HD_R
    up = capsule(sx, sy, ey, 32)
    fore = capsule(ex, ey, hy - 10, 29)
    mug = coffee_C(uid) if side == "r" else ""
    return f"""<g class="arm arm-{side}">
  <path d="{up}" fill="url(#{uid}-sleeve)"/>
  <g class="fore"><path d="{fore}" fill="url(#{uid}-sleeve)"/>
    <rect x="{ex - 14.5}" y="{hy - 22}" width="29" height="11" rx="5.5" fill="#044A74"/>
    <path d="M{ex - 7} {ey - 8} L{ex - 7} {hy - 26}" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".18"/>
    {mug}
    <g class="hand-fist"><circle class="hand" cx="{hx}" cy="{hy}" r="13.5" fill="url(#{uid}-skinS)"/>
    <ellipse cx="{hx - 4}" cy="{hy - 5}" rx="4.5" ry="3" fill="#fff" opacity=".35"/></g>
    {hand_open(hx, hy, side, f"url(#{uid}-skinS)", line="#C98260")}
  </g></g>"""


def coffee_C(uid):
    hx, hy = HD_R
    x, y = hx - 42, hy - 28
    return f"""<g class="prop prop-coffee">
    <g fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".85" filter="url(#{uid}-soft2)">
      <path d="M{x + 12} {y - 8} q-6 -8 0 -16 t0 -16"/><path d="M{x + 26} {y - 6} q-6 -8 0 -16 t0 -14"/></g>
    <g fill="none" stroke="{WGREY}" stroke-width="3" stroke-linecap="round" opacity=".7">
      <path d="M{x + 12} {y - 8} q-6 -8 0 -16 t0 -16"/><path d="M{x + 26} {y - 6} q-6 -8 0 -16 t0 -14"/></g>
    <path d="M{x + 34} {y + 12} q17 0 17 13 t-17 13" fill="none" stroke="#E4E0D8" stroke-width="7"/>
    <rect x="{x}" y="{y}" width="38" height="46" rx="10" fill="url(#{uid}-mug)"/>
    <rect x="{x}" y="{y + 13}" width="38" height="12" fill="{LIME}"/>
    <ellipse cx="{x + 19}" cy="{y + 3}" rx="17" ry="4" fill="#6B4434"/>
    <rect x="{x + 6}" y="{y + 6}" width="5" height="34" rx="2.5" fill="#fff" opacity=".8"/>
  </g>"""


def laptop_C(uid):
    return f"""<g class="prop prop-laptop">
  <rect x="0" y="352" width="300" height="68" fill="url(#{uid}-desk)"/>
  <rect x="0" y="352" width="300" height="4" fill="#fff" opacity=".7"/>
  <path d="M62 264 Q62 254 72 254 L228 254 Q238 254 238 264 L242 352 L58 352 Z" fill="url(#{uid}-lid)"/>
  <path d="M72 260 L120 260" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/>
  <circle cx="150" cy="302" r="20" fill="{LIME}"/>
  <circle cx="150" cy="302" r="20" fill="url(#{uid}-star)" opacity=".6"/>
  <path d="M141 311 v-8 M150 311 v-16 M159 311 v-11" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/>
  <rect x="42" y="346" width="216" height="12" rx="6" fill="#9DA8B5"/>
  <rect x="50" y="347" width="200" height="3" rx="1.5" fill="#fff" opacity=".5"/>
  <ellipse cx="150" cy="364" rx="104" ry="6" fill="{NAVY}" opacity=".12" filter="url(#{uid}-soft2)"/>
</g>"""


def sam_C(uid, classes="mood-neutral"):
    p = Pen(ink=NAVY, eye=NAVY, brow=HAIR, brow_w=7.5, mouth_fill=MOUTH, line_w=4.4)
    hair_back = ("M66 136 C60 60 104 30 150 30 C196 30 240 60 234 136 L238 206 "
                 "C240 232 222 242 206 232 L194 224 L106 224 L94 232 C78 242 60 232 62 206 Z")
    head = "M80 128 C80 74 110 58 150 58 C190 58 220 74 220 128 C220 180 194 206 150 206 C106 206 80 180 80 128 Z"
    fringe = FRINGE
    torso = ("M118 212 L182 212 C200 214 208 226 209 242 L212 326 C212 338 206 344 196 344 "
             "L104 344 C94 344 88 338 88 326 L91 242 C92 226 100 214 118 212 Z")
    return f"""<svg class="sam sam-c {classes}" viewBox="0 0 300 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sam">
<defs>{defs_C(uid)}</defs>
<style>{MOOD_CSS}{pose_css()}
.sam-c .rim{{opacity:0}} .sam-c.on-dark .rim{{opacity:1}}
.sam-c.on-dark .shadow-flood{{flood-color:#000;flood-opacity:.35}}</style>
<ellipse cx="150" cy="404" rx="80" ry="10" fill="{NAVY}" opacity=".22" filter="url(#{uid}-soft)"/>
<g class="body" filter="url(#{uid}-fx)">
  <g class="legs">
    <rect x="113" y="326" width="32" height="62" rx="14" fill="url(#{uid}-pants)"/>
    <rect x="155" y="326" width="32" height="62" rx="14" fill="url(#{uid}-pants)"/>
    <path d="M104 396 Q102 378 122 378 L140 378 Q150 378 150 390 L150 398 Q150 402 145 402 L109 402 Q104 402 104 396 Z" fill="url(#{uid}-shoe)"/>
    <path d="M196 396 Q198 378 178 378 L160 378 Q150 378 150 390 L150 398 Q150 402 155 402 L191 402 Q196 402 196 396 Z" fill="url(#{uid}-shoe)"/>
    <rect x="104" y="396" width="46" height="6" rx="3" fill="#fff"/><rect x="150" y="396" width="46" height="6" rx="3" fill="#fff"/>
    <ellipse cx="118" cy="384" rx="7" ry="3" fill="#fff" opacity=".6"/><ellipse cx="182" cy="384" rx="7" ry="3" fill="#fff" opacity=".6"/>
  </g>
  <path class="hair-back" d="{hair_back}" fill="url(#{uid}-hair)"/>
  <rect x="134" y="186" width="32" height="36" rx="12" fill="#D38E6A"/>
  <path class="torso" d="{torso}" fill="url(#{uid}-cardi)"/>
  <path d="M126 212 L150 262 L174 212 Z" fill="#F6F4EF"/>
  <ellipse cx="150" cy="218" rx="22" ry="8" fill="#B87556" opacity=".55" filter="url(#{uid}-soft2)"/>
  <path d="M150 262 L150 344" stroke="#03466F" stroke-width="3"/>
  <circle cx="159" cy="282" r="4" fill="{SAND}"/><circle cx="159" cy="306" r="4" fill="{SAND}"/><circle cx="159" cy="330" r="4" fill="{SAND}"/>
  <path d="M104 236 C100 260 100 300 102 330" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".14"/>
  <g class="head">
    <circle cx="80" cy="146" r="14" fill="url(#{uid}-skinS)"/><circle cx="220" cy="146" r="14" fill="url(#{uid}-skinS)"/>
    <path class="face" d="{head}" fill="url(#{uid}-skin)"/>
    <g clip-path="url(#{uid}-headclip)"><path d="M96 100 C128 94 168 84 186 66 C206 86 218 108 226 136 L232 40 L70 40 Z" fill="#7A3E33" opacity=".35" filter="url(#{uid}-soft2)"/></g>
    <ellipse cx="116" cy="102" rx="16" ry="6" fill="#fff" opacity=".0"/>
    {face_moods(p, uid, "C")}
    <g class="glasses" fill="none">
      <rect x="{EYE_L[0] - 22}" y="{EYE_L[1] - 19}" width="44" height="38" rx="17" fill="#fff" fill-opacity=".14" stroke="{NAVY}" stroke-width="5.5"/>
      <rect x="{EYE_R[0] - 22}" y="{EYE_R[1] - 19}" width="44" height="38" rx="17" fill="#fff" fill-opacity=".14" stroke="{NAVY}" stroke-width="5.5"/>
      <path d="M147 139 Q150 135 153 139" stroke="{NAVY}" stroke-width="5"/>
      <path d="M104 136 L84 131 M196 136 L216 131" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/>
      <path d="M{EYE_L[0] - 14} {EYE_L[1] - 14} Q{EYE_L[0] - 4} {EYE_L[1] - 18} {EYE_L[0] + 8} {EYE_L[1] - 15}" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".8"/>
      <path d="M{EYE_R[0] - 14} {EYE_R[1] - 14} Q{EYE_R[0] - 4} {EYE_R[1] - 18} {EYE_R[0] + 8} {EYE_R[1] - 15}" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".8"/>
    </g>
    <path class="hair-front" d="{fringe}" fill="url(#{uid}-hair)"/>
    <path d="M150 50 C172 50 192 58 204 72" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".14"/>
    <path d="M160 52 C174 53 186 58 194 65" stroke="#fff" stroke-width="3.5" fill="none" stroke-linecap="round" opacity=".45"/>
    <g class="rim" clip-path="url(#{uid}-rimclip)"><path d="{hair_back}" clip-path="url(#{uid}-hairclip)" stroke="{SKY}" stroke-width="7" fill="none" opacity=".45"/></g>
    <g class="clip"><rect x="98" y="80" width="26" height="9" rx="4.5" fill="url(#{uid}-star)" transform="rotate(-24 111 84)"/><rect x="102" y="81" width="14" height="2.5" rx="1.2" fill="#fff" opacity=".7" transform="rotate(-24 111 84)"/></g>
    {face_moods(p, uid, "C", "brows")}
    {face_fx(p, uid, "C")}
  </g>
  {arm_C("l", uid)}
  {arm_C("r", uid)}
  {laptop_C(uid)}
</g>
</svg>"""


# ======================================================================
# Claude mascot
# ======================================================================
MASCOT_CSS = """
.spark .pz{display:none}
.spark.pose-stand .p-stand,.spark.pose-walk .p-walk,.spark.pose-read .p-read,
.spark.pose-thumbs .p-thumbs,.spark.pose-think .p-think{display:inline}
.spark .leg-l{transform-box:view-box;transform-origin:96px 168px}
.spark .leg-r{transform-box:view-box;transform-origin:124px 168px}
.spark.pose-walk .leg-l{transform:rotate(22deg)}
.spark.pose-walk .leg-r{transform:rotate(-18deg)}
.spark .bod{transform-box:view-box;transform-origin:110px 200px}
.spark.pose-walk .bod{transform:rotate(6deg)}
.spark.pose-think .bod{transform:rotate(4deg)}
"""


def pz(*poses):
    return "pz " + " ".join(f"p-{x}" for x in poses)


def rounded_star(cx, cy, n, r_out, r_in, rot=-90, r_alt=None):
    """smooth spark: quadratic curves through inner points, round tips.
    r_alt: every other tip uses this radius (long/short rays)."""
    pts = []
    for i in range(n * 2):
        r = (r_out if (i // 2) % 2 == 0 or r_alt is None else r_alt) if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # path through tips with control at inner points -> soft star
    d = ""
    tips = pts[0::2]
    inners = pts[1::2]
    d = f"M{tips[0][0]:.1f},{tips[0][1]:.1f} "
    for i in range(n):
        c = inners[i]
        t = tips[(i + 1) % n]
        d += f"Q{c[0]:.1f},{c[1]:.1f} {t[0]:.1f},{t[1]:.1f} "
    return d + "Z"


def mascot_face(uid, style):
    ink = "#3A1E14"
    cx, cy = 110, 104
    s = []
    # eyes
    def eye(x, y, r=5.2):
        if style == "flat":
            return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r + 1.6}" fill="{ink}"/><circle cx="{x + 1.8}" cy="{y - 2.4}" r="1.9" fill="#fff"/>'
        return (f'<ellipse cx="{x}" cy="{y}" rx="{r + .6}" ry="{r + 2.4}" fill="url(#{uid}-meye)"/>'
                f'<ellipse cx="{x + 2}" cy="{y - 2.8}" rx="2.2" ry="2.6" fill="#fff"/><circle cx="{x - 1.8}" cy="{y + 3.4}" r="1" fill="#fff" opacity=".8"/>')
    s.append(f'<g class="eyes {pz("stand", "walk")}">{eye(cx - 13, cy)}{eye(cx + 13, cy)}</g>')
    s.append(f'<g class="eyes {pz("read")}"><path d="M{cx - 19} {cy + 2} Q{cx - 13} {cy + 7} {cx - 7} {cy + 2}" stroke="{ink}" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
             f'<path d="M{cx + 7} {cy + 2} Q{cx + 13} {cy + 7} {cx + 19} {cy + 2}" stroke="{ink}" stroke-width="3.4" fill="none" stroke-linecap="round"/></g>')
    s.append(f'<g class="eyes {pz("thumbs")}">{eye(cx - 13, cy)}<path d="M{cx + 7} {cy + 1} Q{cx + 13} {cy - 6} {cx + 19} {cy + 1}" stroke="{ink}" stroke-width="3.4" fill="none" stroke-linecap="round"/></g>')
    s.append(f'<g class="eyes {pz("think")}">{eye(cx - 11, cy - 2, 4.6).replace(f"cx={chr(34)}{cx - 11}{chr(34)}", f"cx={chr(34)}{cx - 9}{chr(34)}", 1)}{eye(cx + 15, cy - 2, 4.6)}'
             f'<path d="M{cx + 8} {cy - 13} L{cx + 21} {cy - 15}" stroke="{ink}" stroke-width="3" stroke-linecap="round"/></g>')
    # cheeks
    s.append(f'<ellipse cx="{cx - 22}" cy="{cy + 11}" rx="6" ry="3.6" fill="#F08A7A" opacity=".55"/><ellipse cx="{cx + 22}" cy="{cy + 11}" rx="6" ry="3.6" fill="#F08A7A" opacity=".55"/>')
    # mouths
    s.append(f'<path class="{pz("stand", "walk")}" d="M{cx - 6} {cy + 12} Q{cx} {cy + 18} {cx + 6} {cy + 12}" stroke="{ink}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    s.append(f'<ellipse class="{pz("read")}" cx="{cx}" cy="{cy + 15}" rx="3.4" ry="4" fill="{ink}"/>')
    s.append(f'<g class="{pz("thumbs")}"><path d="M{cx - 8} {cy + 10} Q{cx} {cy + 11} {cx + 8} {cy + 10} Q{cx + 7} {cy + 21} {cx} {cy + 21} Q{cx - 7} {cy + 21} {cx - 8} {cy + 10} Z" fill="{ink}"/>'
             f'<path d="M{cx - 4} {cy + 18} Q{cx} {cy + 14} {cx + 4} {cy + 18} Q{cx} {cy + 21} {cx - 4} {cy + 18} Z" fill="#F0806C"/></g>')
    s.append(f'<path class="{pz("think")}" d="M{cx - 5} {cy + 15} Q{cx + 1} {cy + 12} {cx + 7} {cy + 14}" stroke="{ink}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return "".join(s)


def mascot_limbs(uid, col, col_dark, hand_col):
    """noodle arms per pose + legs. Shoulders at (66,120) and (154,120)."""
    a = []
    w = 7.5
    def arm(d, cl, hand=None, extra=""):
        h = f'<circle cx="{hand[0]}" cy="{hand[1]}" r="7.5" fill="{hand_col}"/>' if hand else ""
        return f'<g class="{cl}"><path d="{d}" stroke="{col_dark}" stroke-width="{w}" fill="none" stroke-linecap="round"/>{h}{extra}</g>'
    # stand
    a.append(arm("M64 124 Q50 136 48 150", pz("stand"), (48, 152)))
    a.append(arm("M156 124 Q170 136 172 150", pz("stand"), (172, 152)))
    # walk (swing)
    a.append(arm("M64 124 Q50 128 42 120", pz("walk"), (40, 118)))
    a.append(arm("M156 124 Q168 140 178 150", pz("walk"), (180, 152)))
    # thumbs: left relaxed, right up with thumb
    a.append(arm("M64 124 Q52 138 52 150", pz("thumbs"), (52, 152)))
    thumb = (f'<g transform="translate(184 98) scale(1.35) translate(-184 -98)">'
             f'<path d="M178 92 Q176 76 183 75 Q190 75 188 90 Z" fill="{hand_col}"/>'
             f'<rect x="172" y="89" width="22" height="19" rx="8" fill="{hand_col}"/>'
             f'<path d="M175 96 h11 M175 101 h11" stroke="{col_dark}" stroke-width="1.6" stroke-linecap="round" opacity=".45"/></g>')
    a.append(arm("M156 124 Q178 124 182 110", pz("thumbs"), None, thumb))
    # think: right hand on chin, left arm crossed under
    a.append(arm("M64 124 Q46 140 60 154", pz("think"), (62, 154)))
    a.append(arm("M156 124 Q164 152 136 146", pz("think"), (134, 144)))
    return "".join(a)


def book(uid, col_cover, title_col):
    # open book held in front, under the face; hands at the sides
    return f"""<g class="{pz('read')}">
  <path d="M64 124 Q60 146 74 156" stroke="BODYDARK" stroke-width="7.5" fill="none" stroke-linecap="round"/>
  <path d="M156 124 Q160 146 146 156" stroke="BODYDARK" stroke-width="7.5" fill="none" stroke-linecap="round"/>
  <path d="M70 128 L110 136 L150 128 L150 172 L110 180 L70 172 Z" fill="{col_cover}"/>
  <path d="M74 126 L110 133 L110 175 L74 168 Z" fill="#FFFDF6"/>
  <path d="M146 126 L110 133 L110 175 L146 168 Z" fill="#F4F1EA"/>
  <path d="M110 133 L110 175" stroke="{col_cover}" stroke-width="2"/>
  <path d="M80 140 L102 144 M80 148 L102 152 M80 156 L96 159" stroke="{WGREY}" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M120 160 v-8 M128 158 v-16 M136 156 v-11" stroke="{BLUE}" stroke-width="4" stroke-linecap="round"/>
  <rect x="118" y="138" width="22" height="5" rx="2.5" fill="{LIME}"/>
  <circle cx="74" cy="158" r="7.5" fill="HANDCOL"/><circle cx="146" cy="158" r="7.5" fill="HANDCOL"/>
</g>"""


def mascot_v1(uid, classes="pose-stand"):
    """Flat chunky spark: 8 soft rays, cream face plate."""
    ray = "M92 112 L98 50 A12 12 0 0 1 122 50 L128 112 Z"   # tapered ray, round tip, pointing up
    rays = "".join(f'<path d="{ray}" transform="rotate({22.5 + 45 * k} 110 112)"/>' for k in range(8))
    col, dark = CLAY, CLAY_SH
    bk = book(uid, BLUE, LIME).replace("BODYDARK", dark).replace("HANDCOL", CREAM)
    return f"""<svg class="spark spark-1 {classes}" viewBox="0 0 220 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Claude mascot">
<defs></defs>
<style>{MASCOT_CSS}
.spark-1 .gnd{{fill:{NAVY};opacity:.13}} .spark-1.on-dark .gnd{{fill:#000;opacity:.3}}
.spark-1.on-dark .edge{{stroke:{CREAM}}}</style>
<ellipse class="gnd" cx="110" cy="214" rx="46" ry="6"/>
<g class="pz p-walk" stroke="{WGREY}" stroke-width="3.4" stroke-linecap="round"><path d="M22 112 h18 M14 130 h22 M24 148 h14"/></g>
<g class="pz p-think"><circle cx="176" cy="54" r="5" fill="#fff" stroke="{NAVY}" stroke-width="2"/><circle cx="188" cy="36" r="8" fill="#fff" stroke="{NAVY}" stroke-width="2"/>
  <rect x="150" y="-2" width="62" height="34" rx="17" fill="#fff" stroke="{NAVY}" stroke-width="2.4"/>
  <path d="M168 22 v-6 M178 22 v-14 M188 22 v-9" stroke="{BLUE}" stroke-width="4" stroke-linecap="round"/><path d="M196 12 l3 -6 l3 6" stroke="{MINT}" stroke-width="3" fill="none" stroke-linecap="round"/></g>
<g class="bod">
  <g class="leg-l"><path d="M96 162 L92 196" stroke="{dark}" stroke-width="9" stroke-linecap="round"/><path d="M80 202 Q80 192 92 192 Q100 192 100 202 Z" fill="{NAVY}"/></g>
  <g class="leg-r"><path d="M124 162 L128 196" stroke="{dark}" stroke-width="9" stroke-linecap="round"/><path d="M120 202 Q120 192 128 192 Q140 192 140 202 Z" fill="{NAVY}"/></g>
  <g class="edge" fill="{col}">{rays}<circle cx="110" cy="112" r="40"/></g>
  <path d="M84 50 L89 62" stroke="{CLAY_HI}" stroke-width="6" stroke-linecap="round"/>
  <path d="M48 86 L58 91" stroke="{CLAY_HI}" stroke-width="6" stroke-linecap="round"/>
  <circle cx="110" cy="110" r="35" fill="{CREAM}"/>
  {mascot_face(uid, "flat")}
  {mascot_limbs(uid, col, "#9A4A31", CREAM)}
  {bk}
</g>
</svg>"""


def mascot_v2(uid, classes="pose-stand"):
    """Soft mochi bean with a spark tuft; gradient shading (pairs with C)."""
    col, dark = CLAY, CLAY_SH
    tuft = rounded_star(110, 40, 6, 20, 8, rot=-90)
    bk = book(uid, BLUE, LIME).replace("BODYDARK", dark).replace("HANDCOL", f"url(#{uid}-mhand)")
    body = "M110 52 C150 52 168 84 168 118 C168 156 144 176 110 176 C76 176 52 156 52 118 C52 84 70 52 110 52 Z"
    return f"""<svg class="spark spark-2 {classes}" viewBox="0 0 220 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Claude mascot">
<defs>
<radialGradient id="{uid}-mb" cx="38%" cy="30%" r="75%"><stop offset="0" stop-color="#F2A487"/><stop offset=".55" stop-color="{col}"/><stop offset="1" stop-color="#A9502F"/></radialGradient>
<radialGradient id="{uid}-mbelly" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#FFF9F1"/><stop offset="1" stop-color="#EBD9C4"/></radialGradient>
<radialGradient id="{uid}-meye" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#5A3426"/><stop offset="1" stop-color="#22110B"/></radialGradient>
<radialGradient id="{uid}-mhand" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#FFF6EA"/><stop offset="1" stop-color="#E4CDB4"/></radialGradient>
<radialGradient id="{uid}-tuft" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#FFE3A8"/><stop offset=".6" stop-color="#F4B183"/><stop offset="1" stop-color="{col}"/></radialGradient>
<filter id="{uid}-msoft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<style>{MASCOT_CSS}
.spark-2.on-dark .glow{{opacity:.55}} .spark-2 .glow{{opacity:0}}</style>
<ellipse cx="110" cy="214" rx="48" ry="7" fill="{NAVY}" opacity=".22" filter="url(#{uid}-msoft)"/>
<g class="pz p-walk" stroke="{WGREY}" stroke-width="3.4" stroke-linecap="round"><path d="M22 112 h18 M14 130 h22 M24 148 h14"/></g>
<g class="pz p-think"><circle cx="176" cy="54" r="5" fill="#fff"/><circle cx="188" cy="38" r="8" fill="#fff"/>
  <rect x="150" y="-2" width="62" height="34" rx="17" fill="#fff"/>
  <circle cx="168" cy="15" r="4" fill="{CLAY}"/><circle cx="181" cy="15" r="4" fill="{CLAY}"/><circle cx="194" cy="15" r="4" fill="{CLAY}"/></g>
<g class="bod">
  
  <g class="leg-l"><rect x="88" y="160" width="16" height="36" rx="8" fill="{dark}"/><ellipse cx="94" cy="198" rx="13" ry="7" fill="{NAVY}"/><ellipse cx="90" cy="195" rx="5" ry="2" fill="#fff" opacity=".35"/></g>
  <g class="leg-r"><rect x="116" y="160" width="16" height="36" rx="8" fill="{dark}"/><ellipse cx="126" cy="198" rx="13" ry="7" fill="{NAVY}"/><ellipse cx="122" cy="195" rx="5" ry="2" fill="#fff" opacity=".35"/></g>
  <path d="M110 58 C108 50 110 44 110 40" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>
  <path d="{tuft}" fill="url(#{uid}-tuft)" stroke="url(#{uid}-tuft)" stroke-width="6" stroke-linejoin="round"/>
  <path d="{body}" fill="url(#{uid}-mb)"/>
  <ellipse cx="110" cy="114" rx="38" ry="32" fill="url(#{uid}-mbelly)"/>
  <ellipse cx="84" cy="74" rx="14" ry="8" fill="#fff" opacity=".35" transform="rotate(-30 84 74)"/>
  {mascot_face(uid, "soft")}
  {mascot_limbs(uid, col, dark, f"url(#{uid}-mhand)")}
  {bk}
</g>
</svg>"""


# ======================================================================
# Write files
# ======================================================================
def write(name, s):
    with open(os.path.join(HERE, name), "w") as f:
        f.write(s)


DIRS = [
    ("a", "sam-a-editorial.svg", sam_A, "A. Bold editorial flat",
     "Chunky geometric shapes, chibi proportions, halftone shading and a hard offset shadow block. Confident, graphic, very legible at speed.",
     [BLUE, NAVY, LIME, SKY, HAIR, SKIN]),
    ("b", "sam-b-riso.svg", sam_B, "B. Ink line + riso",
     "Wobbly navy ink over spot-colour fills printed slightly off-register, paper grain and a cream sticker edge. Hand-made, witty, editorial.",
     [NAVY, AZURE, LIME, SKY, DEEP, "#FFB592"]),
    ("c", "sam-c-toy.svg", sam_C, "C. Soft 3D toy",
     "Rounded clay forms with gradient shading, glossy eyes and highlights, soft ambient shadows. Warm, polished, premium-app feel.",
     [BLUE, "#2E8BC4", LIME, NAVY, "#33222A", SKIN]),
]


def main():
    for key, fname, fn, *_ in DIRS:
        write(fname, fn(f"s{key}", "mood-neutral pose-rest"))
    write("claude-mascot-1-spark.svg", mascot_v1("m1", "pose-stand"))
    write("claude-mascot-2-bean.svg", mascot_v2("m2", "pose-stand"))
    import board
    board.build(globals())


if __name__ == "__main__":
    main()
