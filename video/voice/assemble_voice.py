"""Join per-chunk voice clips into one clip per scene, keeping every chunk's start time.

Expects audio/chunks/<scene-id>-<i>.mp3 (or .wav/.m4a), one per chunk of audio/lines.tsv
(chunks are separated by `|`; `[[slnc N]]` is the pause after a chunk, as in make_scratch.py).
Writes audio/<scene-id>.voice.m4a and audio/timings-voice.json, then runs pack_audio.py,
which prefers these files over the scratch voice. Delete the .voice.m4a files to go back to the scratch.

Run (from the repo root):  python video/voice/assemble_voice.py video/<video>   (every scene whose chunks are all present)
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import wave

from make_scratch import VIDEO, parse

HERE = pathlib.Path(__file__).resolve().parent
AUDIO, CHUNKS = VIDEO / "audio", VIDEO / "audio" / "chunks"
SR = 44100


def pcm_of(src, tmp):
    """Decode any clip to 16-bit mono PCM at SR; trim leading/trailing near-silence."""
    out = tmp / (src.stem + ".wav")
    subprocess.run(["afconvert", "-f", "WAVE", "-d", f"LEI16@{SR}", "-c", "1", str(src), str(out)], check=True)
    with wave.open(str(out)) as w:
        raw = w.readframes(w.getnframes())
    import array
    a = array.array("h", raw)
    thr, lo, hi = 300, 0, len(a)
    while lo < hi and abs(a[lo]) < thr:
        lo += 1
    while hi > lo and abs(a[hi - 1]) < thr:
        hi -= 1
    lo, hi = max(0, lo - int(SR * .02)), min(len(a), hi + int(SR * .06))
    return a[lo:hi].tobytes()


def main():
    rows = [r.split("\t", 1) for r in (AUDIO / "lines.tsv").read_text(encoding="utf-8").splitlines() if r.strip()]
    tfile = AUDIO / "timings-voice.json"
    timings = json.loads(tfile.read_text()) if tfile.exists() else {}
    tmp = pathlib.Path(tempfile.mkdtemp())
    for sid, text in rows:
        chunks = parse(text)
        files = []
        for i in range(len(chunks)):
            f = next((CHUNKS / f"{sid}-{i}{e}" for e in (".mp3", ".wav", ".m4a") if (CHUNKS / f"{sid}-{i}{e}").exists()), None)
            files.append(f)
        if not all(files):
            print(f"{sid:11s} skipped ({sum(1 for f in files if f)}/{len(chunks)} chunks present)")
            continue
        pcm, cues = b"", []
        for i, ((_, pause), f) in enumerate(zip(chunks, files)):
            cues.append(round(len(pcm) / 2 / SR, 3))
            pcm += pcm_of(f, tmp)
            pcm += b"\0\0" * int(SR * (pause if i < len(chunks) - 1 else min(pause, 400)) / 1000)
        wav = tmp / f"{sid}.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "128000", str(wav), str(AUDIO / f"{sid}.voice.m4a")], check=True)
        dur = round(len(pcm) / 2 / SR, 3)
        timings[sid] = {"cues": cues, "dur": dur, "hold": round(max(0, chunks[-1][1] - 400) / 1000, 3), "chunks": [c for c, _ in chunks]}
        print(f"{sid:11s} {dur:6.2f}s  cues " + " ".join(f"{c:.2f}" for c in cues))
    tfile.write_text(json.dumps(timings, indent=1))
    subprocess.run([sys.executable, str(HERE / "pack_audio.py"), str(VIDEO)], check=True)


if __name__ == "__main__":
    main()
