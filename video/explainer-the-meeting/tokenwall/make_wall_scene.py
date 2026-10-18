"""Turn tokenwall/tokenwall.html into the s-brand scene (scenes/70-brand.html) of this video.

The tokenwall timeline is authored in scene time (u, narration from narrAt = .5; see the SWAPS comment in
tokenwall.html), so frame(u) seeks it 1:1. This script fixes font paths for <video>/explainer.html,
scopes the CSS under #s-brand and hands the clock to the video engine.
Cues (CUES.md, s-brand, u = .5 + cue): c0 .5 house style in one file; c1 3.23 "so CoverMyMeds, Sarah Cannon and
The US Oncology Network each get their own edition" (waves at 4.63 / 6.23 / 7.83, pinned to the music cue sheet);
c2 9.26 "One standard, every McKesson business" (swap back to McKesson + the band caption, held to the end).
Scene length: .5 + 13.22 + 1 ≈ 15 (data-min).
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent     # <video>/tokenwall
VIDEO = HERE.parent
src = (HERE / "tokenwall.html").read_text(encoding="utf-8")
style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
script = re.search(r"<script>(.*?)</script>", src, re.S).group(1)

style = style.replace("../../../dist/", "../../dist/")
style = re.sub(r"html,body\{[^}]*\}", "", style)
style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)  # comments (with commas) would break the selector scoping


def scope(css):
    """Prefix every top-level selector with #s-brand so the wall's .tw classes can't touch other scenes."""
    out, i = [], 0
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if sel.startswith("@") or not sel:
            out.append(f"{sel}{{{body}}}")
        else:
            out.append(",".join("#s-brand " + x.strip() for x in sel.split(",")) + "{" + body + "}")
    return "\n".join(out)


style = scope(style)
script = script.replace('document.querySelector(".tw")', 'document.getElementById("tokenwall")')

# the video engine drives time: no autoplay, no URL handling
script = re.sub(r"var q = new URLSearchParams\(location.search\);.*?\n\}\)\(\);\s*$",
                "seek(0);\n})();\n", script, flags=re.S)

scene = f"""<section class="scene" id="s-brand" data-min="15">
  <div class="tw" id="tokenwall" data-nofit></div>
</section>
<style>
{style}
#s-brand .tw{{left:0;top:0}}
</style>
<script>
{script}
SCENES["s-brand"] = {{
  narrAt: .5,
  clock: () => null,
  frame(u) {{ window.tokenwall?.seek(Math.min(u, window.tokenwall.duration)); }},
  sfx: [[3.23, "type", {{dur: .6}}], [3.95, "blip"], [4.15, "blip"], [4.35, "blip"],
        [4.63, "snap"], [6.23, "snap"], [7.83, "snap"], [9.26, "snap"]],
}};
</script>
"""
(VIDEO / "scenes" / "70-brand.html").write_text(scene, encoding="utf-8")
stale = VIDEO / "scenes" / "70-wall.html"
if stale.exists():
    stale.unlink()
    print("removed stale 70-wall.html")
print("70-brand.html written", len(scene) // 1000, "KB")
