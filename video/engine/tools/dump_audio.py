"""Render the soundtrack headless and save it as a WAV (+ a spectrogram/level PNG) for checking the score.
Run:  python video/engine/tools/dump_audio.py video/<video> [music|all] [sample_rate]   -> <video>/stills/score-<mix>.wav (+ score_plot.py for the .png)
"""
import base64, pathlib, re, subprocess, sys, wave
root = pathlib.Path(sys.argv[1]).resolve()        # the video folder (holds explainer.html)
mix = sys.argv[2] if len(sys.argv) > 2 else "music"; sr = int(sys.argv[3]) if len(sys.argv) > 3 else 16000
url = f"file://{root}/explainer.html?dumpaudio={sr}" + ("&mix=music" if mix == "music" else "")
log = subprocess.run(["perl", "-e", "alarm 900; exec @ARGV", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu",
                      "--enable-logging=stderr", "--v=1", f"--user-data-dir=/tmp/claude-501/chr-dump-{mix}", url], capture_output=True, text=True, errors="replace").stderr
parts = {int(m.group(1)): m.group(3) for m in re.finditer(r'"AUDIO (\d+)/(\d+) \d+ ([A-Za-z0-9+/=]+)"', log)}
end = re.search(r'"AUDIO END ([^"]*)"', log)
if not parts or not end: sys.exit("no audio found in the log")
pcm = b"".join(base64.b64decode(parts[i]) for i in sorted(parts))
out = root / "stills"; out.mkdir(parents=True, exist_ok=True)
wav = out / f"score-{mix}.wav"
with wave.open(str(wav), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
(out / f"score-{mix}.txt").write_text(end.group(1))
print(wav, f"{len(pcm) / 2 / sr:.1f}s")
