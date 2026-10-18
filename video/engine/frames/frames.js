// Shared helpers for the style frames.
//   ?s=N        show only section N (for 1920x1080 screenshots)
//   ?guides=0   hide layout guides (mascot slot)
// <img data-src="..."> falls back to a labelled grey placeholder if the file is missing.
// <span class="av claude"></span> gets the placeholder spark glyph.
(function () {
  const q = new URLSearchParams(location.search);
  const s = q.get("s");
  const frames = [...document.querySelectorAll(".frame")];
  if (s || frames.length === 1) {
    document.documentElement.classList.add("one");
    frames.forEach((f, i) => { if (s && i + 1 !== +s) f.style.display = "none"; });
  }
  if (q.get("guides") === "0") document.documentElement.classList.add("noguides");

  window.mckImages = function (root) {
    (root || document).querySelectorAll("img[data-src]").forEach((img) => {
      const src = img.dataset.src;
      img.removeAttribute("data-src");
      img.onerror = () => {
        const d = document.createElement("div");
        d.className = "ph";
        d.innerHTML = "<span>" + src.split("/").pop() + "</span>";
        img.replaceWith(d);
      };
      img.src = src;
    });
  };

  const SPARK = '<svg viewBox="0 0 24 24"><path d="M12 1.5c.9 6.4 3.9 9.6 10.5 10.5-6.6.9-9.6 4.1-10.5 10.5C11.1 16.1 8.1 12.9 1.5 12 8.1 11.1 11.1 7.9 12 1.5z"/></svg>';
  document.querySelectorAll(".av.claude").forEach((e) => (e.innerHTML = SPARK));

  // JSON from ../assets (needs --allow-file-access-from-files when opened from disk)
  window.loadJSON = async function (p) {
    try { const r = await fetch(p); if (!r.ok) throw 0; return await r.json(); } catch (e) { return null; }
  };
  const esc = window.esc = (t) => String(t).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));


  // Tiny Python highlighter for notebook cells (comments, strings, keywords, numbers, calls).
  window.pyHL = function (code) {
    const re = /(#.*$)|(f?"(?:[^"\\]|\\.)*")|\b(import|as|for|in|if|from|def|return|None|True|False)\b|\b(\d+(?:\.\d+)?)\b|([A-Za-z_]\w*)(?=\()/g;
    return code.split("\n").map((line) => {
      line = line.replace(/\s{3,}#/, "   #");
      let out = "", last = 0, m;
      re.lastIndex = 0;
      while ((m = re.exec(line))) {
        out += esc(line.slice(last, m.index));
        const t = esc(m[0]);
        const c = m[1] ? "tk-c" : m[2] ? "tk-s" : m[3] ? "tk-k" : m[4] ? "tk-n" : "tk-f";
        out += `<span class="${c}">${t}</span>`;
        last = re.lastIndex;
      }
      return out + esc(line.slice(last));
    }).join("\n");
  };

  document.addEventListener("DOMContentLoaded", () => mckImages());
  if (document.readyState !== "loading") mckImages();
})();
