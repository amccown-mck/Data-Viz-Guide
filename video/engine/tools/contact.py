"""Contact sheet: python3 v3/contact.py DIR OUT.png [cols]  -> a grid of every PNG in DIR (sorted), labelled."""
import pathlib, subprocess, sys
d, out = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
ims = sorted(d.glob("*.png"), key=lambda p: (p.stem.rsplit("-", 1)[0], float(p.stem.rsplit("-", 1)[1]) if p.stem.rsplit("-", 1)[1].replace(".", "").isdigit() else 0))
w = 640
cells = "".join(f'<figure><img src="{p.as_uri()}"><figcaption>{p.stem}</figcaption></figure>' for p in ims)
html = d / "_sheet.html"
html.write_text(f'<style>body{{margin:0;background:#222;display:grid;grid-template-columns:repeat({cols},{w}px);gap:6px;padding:6px;width:max-content}}'
                f'figure{{margin:0}}img{{width:{w}px;display:block}}figcaption{{color:#fff;font:14px sans-serif;padding:2px 4px}}</style>{cells}')
rows = -(-len(ims) // cols)
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                f"--window-size={cols * (w + 6) + 6},{rows * (w * 9 // 16 + 28) + 12}", f"--screenshot={out}", html.as_uri()],
               stderr=subprocess.DEVNULL, check=True)
print(out)
