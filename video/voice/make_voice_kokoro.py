"""Make the narration with Kokoro (open-source TTS, Apache 2.0; runs locally), chunk by chunk, then bundle it.

Setup (once, from video/voice):  uv venv .tts --python 3.12 && VIRTUAL_ENV=.tts uv pip install "kokoro>=0.9.4" "transformers>=4.44" torch soundfile en_core_web_sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
Run (from the repo root):
      video/voice/.tts/bin/python video/voice/make_voice_kokoro.py video/<video>                  (voice af_heart, every scene)
      video/voice/.tts/bin/python video/voice/make_voice_kokoro.py video/<video> --only s-why     (redo one scene)
      video/voice/.tts/bin/python video/voice/make_voice_kokoro.py video/<video> --voice af_heart,af_bella --speed 1.05   (blend two voices, a touch faster)
`[[rate 0.8]]` in a chunk of lines.tsv slows just that chunk (for emphasis).

Each chunk of audio/lines.tsv becomes audio/chunks/<scene>-<i>.wav; assemble_voice.py then joins them with the
scripted pauses and records each chunk's start, so the visuals stay pinned to the words.
"""
import argparse
import pathlib
import subprocess
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

from make_scratch import VIDEO, parse, rates

HERE = pathlib.Path(__file__).resolve().parent
AUDIO = VIDEO / "audio"
# spoken spellings, for words the voice would otherwise read oddly (on-screen text is unchanged)
SAY = {"CoverMyMeds": "Cover My Meds", "Power BI": "Power B.I."}

ap = argparse.ArgumentParser()
ap.add_argument("video", help="the video folder, e.g. video/explainer-exec-ready-by-3")
ap.add_argument("--voice", default="af_heart")
ap.add_argument("--speed", type=float, default=1.0)
ap.add_argument("--only")
args = ap.parse_args()

pipe = KPipeline(lang_code="a")
(AUDIO / "chunks").mkdir(exist_ok=True)
rows = [r.split("\t", 1) for r in (AUDIO / "lines.tsv").read_text(encoding="utf-8").splitlines() if r.strip()]
for sid, text in rows:
    if args.only and sid != args.only:
        continue
    for i, ((chunk, _), rate) in enumerate(zip(parse(text), rates(text))):
        for k, v in SAY.items():
            chunk = chunk.replace(k, v)
        audio = np.concatenate([np.asarray(a) for _, _, a in pipe(chunk, voice=args.voice, speed=args.speed * rate)])
        sf.write(AUDIO / "chunks" / f"{sid}-{i}.wav", audio, 24000)
    print(f"{sid:12s} ok")

subprocess.run([sys.executable, str(HERE / "assemble_voice.py"), str(VIDEO)], check=True)
