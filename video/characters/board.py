"""Design board: board-characters.html (stacked 1920x1080 pages) + PNG per page."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
_n = [0]


def uid(p="u"):
    _n[0] += 1
    return f"{p}{_n[0]}"


CSS = """
@font-face{font-family:LF;src:url(FONTS/LibreFranklin-Regular.ttf);font-weight:400}
@font-face{font-family:LF;src:url(FONTS/LibreFranklin-Medium.ttf);font-weight:500}
@font-face{font-family:LF;src:url(FONTS/LibreFranklin-SemiBold.ttf);font-weight:600}
@font-face{font-family:LF;src:url(FONTS/LibreFranklin-Bold.ttf);font-weight:700}
:root{--blue:#005A8C;--navy:#143359;--deep:#0B3266;--sky:#66C4FF;--azure:#009EFF;--lime:#D9F14E;--sand:#EFEDE7;--sand2:#DEDBD1;--grey:#B4B0A5;--text:#505050}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#d9d6cc;font-family:LF,sans-serif;color:var(--navy)}
.page{width:1920px;height:1080px;position:relative;overflow:hidden;background:#FBFAF7;margin:0 auto 24px;padding:64px 80px}
body.solo .page{display:none;margin:0} body.solo .page.on{display:block}
.eyebrow{font-size:20px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--blue)}
h1{font-size:60px;font-weight:700;line-height:1.05;margin-top:10px;letter-spacing:-.01em}
h2{font-size:44px;font-weight:700;line-height:1.1;margin-top:8px}
.lede{font-size:24px;line-height:1.4;color:var(--text);max-width:900px;margin-top:14px}
.chips{display:flex;gap:10px;margin-top:18px}
.chip{width:40px;height:40px;border-radius:50%;box-shadow:inset 0 0 0 2px rgba(0,0,0,.06)}
.card{border-radius:28px;background:var(--sand);position:relative;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;overflow:hidden}
.card.dark{background:var(--deep)}
.card .lbl{position:absolute;left:24px;top:20px;font-size:20px;font-weight:700;color:var(--navy)}
.card .sub{position:absolute;left:24px;top:48px;font-size:16px;color:var(--text)}
.card.dark .lbl{color:#fff}.card.dark .sub{color:#B6E2FA}
.card svg{display:block}
.row{display:flex;gap:24px}
.tag{display:inline-block;font-size:15px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:6px 12px;border-radius:999px;background:var(--lime);color:var(--navy)}
.note{font-size:18px;color:var(--text);line-height:1.4}
.small{display:flex;gap:18px;align-items:flex-end;justify-content:center}
.small svg{height:150px;width:auto}
.small.mini svg{height:116px}
.cap{font-size:15px;font-weight:600;color:var(--text);text-align:center;margin-top:6px}
.dark .cap{color:#B6E2FA}
"""


def page(pid, inner, bg=None):
    style = f' style="background:{bg}"' if bg else ""
    return f'<section class="page" id="{pid}"{style}>{inner}</section>'


def sam(g, key, classes, h=None):
    fn = {"a": g["sam_A"], "b": g["sam_B"], "c": g["sam_C"]}[key]
    s = fn(uid("s" + key), classes)
    if h:
        s = s.replace('viewBox="0 0 300 420"', f'viewBox="0 0 300 420" height="{h}" width="{round(h * 300 / 420)}"', 1)
    return s


def mascot(g, v, classes, h=None):
    fn = g["mascot_v1"] if v == 1 else g["mascot_v2"]
    s = fn(uid(f"m{v}"), classes)
    if h:
        s = s.replace('viewBox="0 0 220 240"', f'viewBox="0 0 220 240" height="{h}" width="{round(h * 220 / 240)}"', 1)
    return s


MOODS = [("Stressed", "mood-stressed pose-type with-laptop", "at the laptop, deadline"),
         ("Ooh", "mood-ooh pose-cheeks", "starry-eyed discovery"),
         ("Proud", "mood-proud pose-coffee with-coffee", "chart shipped, coffee earned")]
EXTRA = [("Wave", "mood-happy pose-wave"), ("Shrug", "mood-shrug pose-shrug"),
         ("Typing", "mood-focus pose-type with-laptop"), ("Neutral", "mood-neutral pose-rest")]


def direction_page(g, i, d):
    key, fname, fn, title, desc, chips = d
    cards = "".join(
        f'<div class="card" style="width:400px;height:640px;padding-bottom:18px"><div class="lbl">{n}</div><div class="sub">{s}</div>{sam(g, key, c, 520)}</div>'
        for n, c, s in MOODS)
    small_dark = "".join(f'<div>{sam(g, key, c + " on-dark", 150)}<div class="cap">{n}</div></div>' for n, c, _ in MOODS)
    small_light = "".join(f'<div>{sam(g, key, c, 150)}<div class="cap">{n}</div></div>' for n, c in EXTRA)
    chips_html = "".join(f'<span class="chip" style="background:{c}"></span>' for c in chips)
    inner = f"""
<div style="display:flex;justify-content:space-between;align-items:flex-start">
  <div><div class="eyebrow">Sam · direction {i} of 3 · {fname}</div><h1>{title}</h1><p class="lede">{desc}</p></div>
  <div class="chips" style="margin-top:40px">{chips_html}</div>
</div>
<div class="row" style="margin-top:34px">
  <div class="row">{cards}</div>
  <div style="display:flex;flex-direction:column;gap:24px;width:536px">
    <div class="card dark" style="height:352px;justify-content:center;padding-top:40px"><div class="lbl">On deep navy at 150 px</div>
      <div class="small dark">{small_dark}</div></div>
    <div class="card" style="height:264px;justify-content:center;padding-top:36px"><div class="lbl">More poses at 150 px</div>
      <div class="small" style="gap:6px">{small_light}</div></div>
  </div>
</div>"""
    return page(f"p{i + 1}", inner)


def cover(g, dirs):
    cols = ""
    for (key, fname, fn, title, desc, chips) in dirs:
        rec = '<span class="tag" style="margin-left:12px">recommended</span>' if key == "a" else ""
        cols += f"""<div style="width:560px">
  <div class="row" style="gap:16px">
    <div class="card" style="width:272px;height:470px;padding-bottom:12px">{sam(g, key, "mood-happy pose-wave", 400)}</div>
    <div class="card dark" style="width:272px;height:470px;padding-bottom:12px">{sam(g, key, "mood-proud pose-coffee with-coffee on-dark", 400)}</div>
  </div>
  <h2 style="font-size:32px;margin-top:22px">{title}{rec}</h2>
  <p class="note" style="margin-top:8px">{desc}</p></div>"""
    inner = f"""
<div class="eyebrow">Explainer video · character exploration</div>
<h1>Meet Sam, three ways (and a Claude sidekick)</h1>
<p class="lede">Sam makes exec charts under deadline. Each direction uses the same rig: swappable moods, arms that rotate at shoulder and elbow, and props, so any of them can carry the story.</p>
<div class="row" style="margin-top:40px;gap:40px">{cols}</div>"""
    return page("p1", inner)


POSES_M = [("Walk", "pose-walk", "heading to the toolkit"), ("Read", "pose-read", "studying the manual"),
           ("Thumbs-up", "pose-thumbs", "chart passes QA"), ("Thoughtful", "pose-think", "picking a chart type")]


def mascot_page(g, pid):
    rows = ""
    meta = [(1, "Variant 1 · Spark", "A chunky eight-ray spark with a cream face plate. Flat, bold, instantly readable; pairs with directions A and B.", "claude-mascot-1-spark.svg"),
            (2, "Variant 2 · Ember", "A soft mochi bean wearing a little spark tuft, gradient-shaded with glossy eyes; pairs with direction C.", "claude-mascot-2-bean.svg")]
    for v, name, desc, fname in meta:
        cards = "".join(f'<div class="card" style="width:244px;height:330px;padding-bottom:8px"><div class="lbl">{n}</div><div class="sub">{s}</div>{mascot(g, v, c, 240)}</div>' for n, c, s in POSES_M)
        small = "".join(f'<div>{mascot(g, v, c + " on-dark", 120)}</div>' for _, c, _ in POSES_M)
        rows += f"""<div class="row" style="margin-top:28px;align-items:stretch">
  <div style="width:250px;padding-top:10px"><h2 style="font-size:34px">{name}</h2><p class="note" style="margin-top:10px">{desc}</p><p class="note" style="margin-top:10px;font-size:15px;opacity:.8">{fname}</p></div>
  <div class="row" style="gap:18px">{cards}</div>
  <div class="card dark" style="width:470px;height:330px;justify-content:center;padding-top:40px"><div class="lbl">On navy at 120 px</div><div class="small mini dark" style="gap:0">{small}</div></div>
</div>"""
    inner = f"""
<div class="eyebrow">Claude mascot · 2 variants · 4 poses</div>
<h1>A little spark who goes to the toolkit</h1>
<p class="lede" style="max-width:1400px">Warm terracotta with a cream accent, an original character built on the spark motif (not the logo). Tiny noodle arms and legs; legs pivot at the hip for a walk cycle.</p>
{rows}"""
    return page(pid, inner)


def duo_page(g, pid):
    inner = f"""
<div class="eyebrow">Together in a scene · recommended pairing</div>
<h1>Sam and the spark, at video speed</h1>
<p class="lede">Direction A with Spark (left) and direction C with Ember (right), sized as they would sit in a 1920 × 1080 frame.</p>
<div class="row" style="margin-top:40px;gap:40px">
  <div class="card" style="width:860px;height:700px;flex-direction:row;align-items:flex-end;justify-content:center;gap:10px;padding-bottom:30px">
    {sam(g, "a", "mood-proud pose-coffee with-coffee", 560)}{mascot(g, 1, "pose-thumbs", 300)}</div>
  <div class="card dark" style="width:860px;height:700px;flex-direction:row;align-items:flex-end;justify-content:center;gap:10px;padding-bottom:30px">
    {sam(g, "c", "mood-ooh pose-cheeks on-dark", 560)}{mascot(g, 2, "pose-read on-dark", 300)}</div>
</div>"""
    return page(pid, inner)


def build(g):
    dirs = g["DIRS"]
    pages = [cover(g, dirs)]
    for i, d in enumerate(dirs, start=1):
        pages.append(direction_page(g, i, d))
    pages.append(mascot_page(g, "p5"))
    pages.append(duo_page(g, "p6"))
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1920"><title>Character board</title>
<style>{CSS.replace("FONTS/", g["FONTS"])}</style></head>
<body>
{"".join(pages)}
<script>
const m = location.hash.match(/^#(p\\d+)$/);
if (m) {{ document.body.classList.add('solo'); document.getElementById(m[1]).classList.add('on'); }}
</script>
</body></html>"""
    path = os.path.join(HERE, "board-characters.html")
    with open(path, "w") as f:
        f.write(html)
    import sys
    only = sys.argv[1:] or [str(i) for i in range(1, len(pages) + 1)]
    for n in only:
        out = os.path.join(HERE, f"board-p{n}.png")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1920,1080", "--virtual-time-budget=3000",
                        f"--screenshot={out}", f"file://{path}#p{n}"],
                       check=True, capture_output=True)
        print("wrote", out)
