"""Plot the dumped score (<video>/stills/score-<mix>.wav): spectrogram + loudness, with scenes and sections marked.
Run:  python video/engine/tools/score_plot.py video/<video> [music|all]   (after dump_audio.py)"""
import sys, wave, pathlib, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
mix = sys.argv[2] if len(sys.argv) > 2 else "music"; d = pathlib.Path(sys.argv[1]).resolve() / "stills"
with wave.open(str(d / f"score-{mix}.wav")) as w: sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
meta = (d / f"score-{mix}.txt").read_text(); scenes, secs = meta.split(" SECS ")
hop = int(sr * .1); rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)]); db = 20 * np.log10(rms + 1e-6)
print(f"peak {np.abs(x).max():.2f}  clipped samples {(np.abs(x) > .99).sum()}  quietest 1s windows:")
t = np.arange(len(db)) * .1
fig, ax = plt.subplots(2, 1, figsize=(26, 9), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
ax[0].specgram(x, NFFT=1024, Fs=sr, noverlap=512, cmap="magma", vmin=-120); ax[0].set_ylim(0, 6000)
ax[1].plot(t, db, lw=.8); ax[1].set_ylim(-60, 0); ax[1].set_ylabel("dBFS (100 ms RMS)")
for s in scenes.split(","):
    n, at = s.split("@"); at = float(at)
    for a in ax: a.axvline(at, color="w" if a is ax[0] else "k", lw=1.2)
    ax[1].text(at + .3, -5, n.replace("s-", ""), fontsize=9, rotation=90, va="top")
for s in secs.split(","):
    n, at = s.split("@"); at = float(at); ax[1].axvline(at, color="r", lw=.5, ls=":"); ax[1].text(at + .2, -58, n, fontsize=7, rotation=90, color="r", va="bottom")
plt.tight_layout(); plt.savefig(d / f"score-{mix}.png", dpi=70)
# per-section mean loudness
pts = [(float(s.split("@")[1]), s.split("@")[0]) for s in secs.split(",")] + [(len(x) / sr, "end")]
for (a, n), (b, _) in zip(pts, pts[1:]):
    if b - a > .3: seg = db[int(a * 10):int(b * 10)]; print(f"{n:10s} {a:6.1f}-{b:6.1f}s  mean {seg.mean():6.1f} dB  min {seg.min():6.1f}")
