"""Assemble a video's explainer.html from the engine (shell.html) and the video's scenes/*.html (in filename order).

Also inlines the characters (video/characters/final/{sam,spark}.svg, falling back to the exploration files),
the UI components from engine/frames/frames.css (scoped under .scene), and the video's chart metadata
(assets/options.json, assets/nb_lint.json, assets/fc_lint.json) plus ref_cues.json as window.KIT / window.REFCUES,
since pages opened from disk can't fetch JSON. Paths to the repo's dist/ (fonts, mck-viz.css) are rewritten for
wherever the output lands. If the video has no narration.js yet, voice/pack_audio.py builds it first.

Run (from the repo root):
    python video/engine/build_video.py video/<video>                      -> video/<video>/explainer.html
    python video/engine/build_video.py video/<video> --out preview-me.html  (a private copy, when several people preview at once)
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

ENGINE = pathlib.Path(__file__).resolve().parent
KIT = ENGINE.parent                     # video/
REPO = KIT.parent
CHAR = KIT / "characters"


def first(*paths):
    for p in paths:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def components():
    """frames.css UI components, every selector prefixed with .scene so nothing leaks into the actors."""
    src = (ENGINE / "frames" / "frames.css").read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    out = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", src):
        sel = sel.strip()
        if not sel or sel.startswith("@") or sel in (":root", "*") or re.match(r"^(html|body)\b", sel):
            continue
        if re.search(r"(^|[\s,])(\.frame(?![\w-])|\.cap(?![\w-])|\.m(?![\w-])|\.kick(?![\w-])|\.sticker(?![\w-])|\.spark(?![\w-])|\.bg-|html)", sel):
            continue                    # the shell defines these (or they would clash with the actors)
        scoped = ",".join(".scene " + s.strip() for s in sel.split(","))
        out.append(f"{scoped}{{{body.strip()}}}")
    return "\n".join(out)


def kit_assets(video):
    data = {}
    for key, name in (("options", "options.json"), ("nb", "nb_lint.json"), ("fc", "fc_lint.json")):
        p = video / "assets" / name
        data[key] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    cues = video / "ref_cues.json"
    ref = json.loads(cues.read_text(encoding="utf-8")) if cues.exists() else {}
    return "window.KIT = " + json.dumps(data) + ";\nwindow.REFCUES = " + json.dumps(ref) + ";"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("video", help="the video folder, e.g. video/explainer-exec-ready-by-3")
    ap.add_argument("--out", default="explainer.html", help="output file name inside the video folder (use your own when previewing in parallel)")
    args = ap.parse_args()
    video = pathlib.Path(args.video).resolve()
    if not (video / "scenes").is_dir():
        sys.exit(f"{video} has no scenes/ folder")
    out = video / args.out
    if not (video / "narration.js").exists() and (video / "audio" / "lines.tsv").exists():
        print("narration.js missing: packing the narration first")
        subprocess.run([sys.executable, str(KIT / "voice" / "pack_audio.py"), str(video)], check=True)
    shell = (ENGINE / "shell.html").read_text(encoding="utf-8")
    scenes = sorted((video / "scenes").glob("*.html"))
    body = "\n".join(f"<!-- ===== {p.name} ===== -->\n" + p.read_text(encoding="utf-8") for p in scenes)
    sam = first(CHAR / "final" / "sam.svg", CHAR / "sam-a-editorial.svg")
    spark = first(CHAR / "final" / "spark.svg", CHAR / "claude-mascot-1-spark.svg")
    html = (shell.replace("/*COMPONENTS*/", components())
                 .replace("/*ASSETS*/", kit_assets(video))
                 .replace("<!--SCENES-->", body)
                 .replace("<!--SAM_SVG-->", re.sub(r"<\?xml[^>]*>", "", sam))
                 .replace("<!--SPARK_SVG-->", re.sub(r"<\?xml[^>]*>", "", spark)))
    # the shell and the scenes refer to the repo's dist/ as ../../dist/ (a video folder directly under video/);
    # rewrite that for wherever the output actually lands
    rel = pathlib.Path(os.path.relpath(REPO, out.parent)).as_posix()
    html = html.replace("../../dist/", f"{rel}/dist/")
    out.write_text(html, encoding="utf-8")
    print(f"{out.relative_to(REPO) if out.is_relative_to(REPO) else out}: {len(scenes)} scenes ({', '.join(p.stem for p in scenes)}), {len(html) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
