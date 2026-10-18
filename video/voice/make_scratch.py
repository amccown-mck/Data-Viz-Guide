"""Make the scratch narration (macOS `say`) chunk by chunk, so every chunk's start time is known.

<video>/audio/lines.tsv holds one line per scene: `scene-id <TAB> chunk | chunk [[slnc 800]] | chunk`.
A `|` starts a new chunk (a cue the visuals can lock to). `[[slnc N]]` at the end of a chunk is the
pause after it, in ms (default 250). Each chunk is spoken on its own, then the chunks and pauses
are joined, so the cue times are exact.

Writes audio/<id>.m4a and audio/timings-scratch.json, adds any new scene to <video>/ref_cues.json (the reference cue
times the scenes are authored against; --reref replaces existing ones too, after re-authoring a scene), then runs pack_audio.py.

Run (from the repo root):  python video/voice/make_scratch.py video/<video>            (all scenes)
                           python video/voice/make_scratch.py video/<video> s-hook     (one scene)
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import wave

HERE = pathlib.Path(__file__).resolve().parent


def video_dir(argv=sys.argv):
    """The video folder: the first positional argument (one with an audio/lines.tsv)."""
    for a in argv[1:]:
        if not a.startswith("-") and (pathlib.Path(a) / "audio" / "lines.tsv").exists():
            return pathlib.Path(a).resolve()
    sys.exit("usage: <script> video/<video> ...   (the video folder, with audio/lines.tsv)")


VIDEO = video_dir()
AUDIO = VIDEO / "audio"
VOICE, RATE, SR = "Samantha", "172", 22050
GAP = 250


def parse(text):
    """-> [(chunk text, pause ms after it)]"""
    out = []
    for raw in text.split("|"):
        pause = sum(int(n) for n in re.findall(r"\[\[slnc (\d+)\]\]", raw)) or GAP
        clean = re.sub(r"\s*\[\[[^\]]*\]\]\s*", " ", raw).strip()
        if clean:
            out.append((clean, pause))
    return out


def rates(text):
    """-> the speaking rate of each chunk (`[[rate 0.8]]` in a chunk slows that chunk; default 1)"""
    out = []
    for raw in text.split("|"):
        if re.sub(r"\s*\[\[[^\]]*\]\]\s*", " ", raw).strip():
            r = re.findall(r"\[\[rate ([\d.]+)\]\]", raw)
            out.append(float(r[0]) if r else 1.0)
    return out


def say(text, path):
    subprocess.run(["say", "-v", VOICE, "-r", RATE, "--data-format=LEI16@%d" % SR, "-o", str(path), text], check=True)
    with wave.open(str(path)) as w:
        return w.readframes(w.getnframes())


def main(only):
    rows = [r.split("\t", 1) for r in (AUDIO / "lines.tsv").read_text(encoding="utf-8").splitlines() if r.strip()]
    tfile = AUDIO / "timings-scratch.json"
    timings = json.loads(tfile.read_text()) if tfile.exists() else {}
    tmp = pathlib.Path(tempfile.mkdtemp())
    done = set()
    for sid, text in rows:
        if only and sid not in only:
            continue
        done.add(sid)
        pcm, cues, chunks = b"", [], parse(text)
        for i, (chunk, pause) in enumerate(chunks):
            cues.append(round(len(pcm) / 2 / SR, 3))
            pcm += say(chunk, tmp / f"{i}.wav")
            if i < len(chunks) - 1:
                pcm += b"\0\0" * int(SR * pause / 1000)
            else:
                pcm += b"\0\0" * int(SR * min(pause, 400) / 1000)   # the scene's own hold covers the rest
        wav = tmp / f"{sid}.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(wav), str(AUDIO / f"{sid}.m4a")], check=True)
        # the last chunk's long pause is a deliberate hold: keep it as the scene's minimum tail
        dur = round(len(pcm) / 2 / SR, 3)
        hold = round(max(0, chunks[-1][1] - 400) / 1000, 3)
        timings[sid] = {"cues": cues, "dur": dur, "hold": hold, "chunks": [c for c, _ in chunks]}
        print(f"{sid:11s} {dur:6.2f}s  cues " + " ".join(f"{c:.2f}" for c in cues))
    tfile.write_text(json.dumps(timings, indent=1))
    # the reference the scenes are authored against: only new scenes join it, unless --reref
    rfile = VIDEO / "ref_cues.json"
    ref = json.loads(rfile.read_text()) if rfile.exists() else {}
    for sid, tm in timings.items():
        if sid not in ref or (REREF and sid in done):
            ref[sid] = tm
    rfile.write_text(json.dumps(ref, indent=1))
    subprocess.run([sys.executable, str(HERE / "pack_audio.py"), str(VIDEO)], check=True)


REREF = "--reref" in sys.argv
if __name__ == "__main__":
    main(set(a for a in sys.argv[1:] if not a.startswith("--") and pathlib.Path(a).resolve() != VIDEO))
