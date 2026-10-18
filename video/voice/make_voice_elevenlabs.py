"""Generate the narration with ElevenLabs, then bundle it.

Keep your API key out of chat and out of files. Set it in the terminal for this session only:
    export ELEVENLABS_API_KEY="..."            # from elevenlabs.io > Profile > API keys
    python video/voice/make_voice_elevenlabs.py video/<video> VOICE_ID  # the voice ID from the Voices page (Voice > ... > Copy voice ID)

Optional: --model eleven_multilingual_v2 (default) or another model your plan offers; --only s-why to redo one line.
Speaks every chunk of audio/lines.tsv on its own (with its neighbours as context, so the delivery stays continuous)
into audio/chunks/<scene>-<i>.mp3, then runs assemble_voice.py, which joins them with the scripted pauses and records
each chunk's start, so the visuals stay pinned to the words.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("video", help="the video folder, e.g. video/explainer-exec-ready-by-3")
ap.add_argument("voice_id")
ap.add_argument("--model", default="eleven_multilingual_v2")
ap.add_argument("--only", help="regenerate a single scene id, e.g. s-why")
args = ap.parse_args()

key = os.environ.get("ELEVENLABS_API_KEY")
if not key:
    sys.exit("Set ELEVENLABS_API_KEY first (see the top of this file).")

from make_scratch import VIDEO, parse

AUDIO = VIDEO / "audio"
rows = [r.split("\t", 1) for r in (AUDIO / "lines.tsv").read_text(encoding="utf-8").splitlines() if r.strip()]
lines = [(sid, [c for c, _ in parse(t)]) for sid, t in rows]
(AUDIO / "chunks").mkdir(exist_ok=True)

for li, (sid, chunks) in enumerate(lines):
    if args.only and sid != args.only:
        continue
    before_line = " ".join(lines[li - 1][1]) if li else ""
    after_line = " ".join(lines[li + 1][1]) if li + 1 < len(lines) else ""
    for i, text in enumerate(chunks):
        body = {
            "text": text,
            "model_id": args.model,
            # the surrounding words keep one continuous, natural delivery across chunks
            "previous_text": (before_line + " " + " ".join(chunks[:i])).strip() or None,
            "next_text": (" ".join(chunks[i + 1:]) + " " + after_line).strip() or None,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True},
        }
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{args.voice_id}?output_format=mp3_44100_128",
            data=json.dumps({k: v for k, v in body.items() if v is not None}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                (AUDIO / "chunks" / f"{sid}-{i}.mp3").write_bytes(resp.read())
        except urllib.error.HTTPError as e:
            sys.exit(f"{sid}-{i}: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
    print(f"{sid:12s} ok ({len(chunks)} chunks)")

subprocess.run([sys.executable, str(HERE / "assemble_voice.py"), str(VIDEO)], check=True)
