"""Turn tokenwall/tokenwall.html into the s-wall scene (scenes/70-wall.html) of this video.

The tokenwall timeline is authored in scene time (u, narration from narrAt = .5; see the SWAPS comment in
tokenwall.html), so frame(u) seeks it 1:1. This script fixes font paths for <video>/explainer.html,
scopes the CSS under #s-wall and hands the clock to the video engine.
Cues (CUES.md, s-wall): 0 brand in one file, 1 change one line (3.32), 2 CoverMyMeds (8.42),
3 Sarah Cannon (10.16), 4 The US Oncology Network (11.84), 5 Even dark mode (14.34); u = .5 + cue.
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
    """Prefix every top-level selector with #s-wall so the wall's .tw classes can't touch other scenes."""
    out, i = [], 0
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if sel.startswith("@") or not sel:
            out.append(f"{sel}{{{body}}}")
        else:
            out.append(",".join("#s-wall " + x.strip() for x in sel.split(",")) + "{" + body + "}")
    return "\n".join(out)


style = scope(style)
script = script.replace('document.querySelector(".tw")', 'document.getElementById("tokenwall")')

# the video engine drives time: no autoplay, no URL handling
script = re.sub(r"var q = new URLSearchParams\(location.search\);.*?\n\}\)\(\);\s*$",
                "seek(0);\n})();\n", script, flags=re.S)

scene = f"""<section class="scene" id="s-wall" data-min="18">
  <div class="tw" id="tokenwall" data-nofit></div>
</section>
<style>
{style}
#s-wall .tw{{left:0;top:0}}
</style>
<script>
{script}
SCENES["s-wall"] = {{
  narrAt: .5,
  frame(u) {{ window.tokenwall?.seek(Math.min(u, window.tokenwall.duration)); }},
  sfx: [[3.95, "type", {{dur: .85}}], [6.25, "blip"], [6.95, "blip"], [7.6, "blip"],
        [8.3, "snap"], [10.58, "snap"], [12.26, "snap"], [14.76, "snap"], [16.35, "snap"], [16.9, "sparkle"]],
}};
</script>
"""
(VIDEO / "scenes" / "70-wall.html").write_text(scene, encoding="utf-8")
print("70-wall.html written", len(scene) // 1000, "KB")
