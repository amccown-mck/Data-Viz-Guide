/* GENERATED from tokens/tokens.json by tokens/build.py - do not edit by hand.
 * mck-viz.js: small helpers for McKesson charts in plain HTML pages. A plain script (no modules): it defines window.mck.
 *   <link rel="stylesheet" href="mck-viz.css"> <script src="mck-viz.js"></script> <script src="plotly.min.js"></script>
 * It also defines window.MCK_PLOTLY_TEMPLATE, so mck-plotly-template.js is optional when this file is loaded.
 *
 *   mck.tok("chart-focus")                -> "#005A8C"  CSS variable --mck-<name> (page overrides win), else the token
 *   mck.highlight(labels, {focus, accent, base})  -> colors: grey context, blue focus, navy accent (= mv.highlight)
 *   mck.fmtNum(v, {kind, decimals, sign, prefix, suffix}) -> "$4.3B", "12K", "19.9%", "+2.5%", "−7" (= mv.fmt_num)
 *   mck.suppressSmall(rows, nKey, {minN: 10, otherLabel: "Other", groupKeys, by, sumKeys, unit})
 *                                         -> [rows, footnote]  merges or drops groups under minN (= mv.suppress_small)
 *   mck.textOn(hex)                       -> "#FFFFFF" or headline navy, whichever reads better on hex (= mv.text_on)
 *   mck.status("at_risk")                 -> {color, symbol, word, ink}; never show the color without symbol + word
 *   mck.plotlyLayout(kind, extra)         -> Plotly layout for "bar" | "line" | "waterfall" | "stacked" | "heatmap" |
 *                                            "sankey" | "roadmap", on the McKesson template; extra is deep-merged in
 *   mck.alpha(hex, a), mck.zeroLine("x"|"y"), mck.srTable(id, caption, head, rows), mck.ready(fn), mck.plotConfig
 */
(function () {
  "use strict";
  var TOKENS = {"blue":"#005A8C","navy":"#143359","orange":"#EF8200","sand":"#DEDBD1","deep-navy":"#0B3266","sand-light":"#EFEDE7","text":"#505050","lime-light":"#F7FCDC","lime-mid":"#E8F795","lime-base":"#D9F14E","green-light":"#B3E7D2","green-mid":"#66CFA4","green-base":"#00AF68","green-dark":"#00622C","mint-light":"#B4F0DE","mint-mid":"#69E2BC","mint-base":"#05CE90","mint-dark":"#008264","teal-light":"#B3E7E2","teal-mid":"#66CFC4","teal-base":"#00AF9D","teal-dark":"#00737A","sky-light":"#B3ECFF","sky-mid":"#66D8FF","sky-base":"#00BEFF","sky-dark":"#0074D0","azure-light":"#B6E2FA","azure-mid":"#66C4FF","azure-base":"#009EFF","azure-dark":"#0A5FBC","text-title":"#005A8C","text-headline":"#143359","text-primary":"#505050","text-muted":"#737373","text-inverse":"#FFFFFF","surface-default":"#FFFFFF","surface-subtle":"#EFEDE7","surface-dark":"#0B3266","chart-axis":"#8C8C8C","chart-grid":"#E6E4DE","chart-context":"#B4B0A5","chart-context-light":"#DEDBD1","chart-focus":"#005A8C","chart-focus-light":"#66C4FF","chart-accent":"#143359","chart-total":"#143359","chart-annotation":"#143359","chart-focus-on-dark":"#66C4FF","chart-context-on-dark":"#5A7194","semantic-positive":"#00AF68","semantic-positive-text":"#007A48","semantic-negative":"#EF8200","semantic-negative-text":"#A75B00","semantic-neutral":"#B4B0A5","cat-1":"#005A8C","cat-2":"#143359","cat-3":"#009EFF","cat-4":"#00AF9D","cat-5":"#05CE90","cat-6":"#EF8200","cat-tint-1":"#B3ECFF","cat-tint-2":"#B3E7E2","step-1":"#005A8C","step-2":"#009EFF","step-3":"#00BEFF","step-4":"#00AF9D","step-5":"#05CE90","step-6":"#00AF68","status-on-track":"#00AF68","status-at-risk":"#FFB500","status-off-track":"#DA2103","status-not-started":"#BFBFBF","status-done":"#005A8C","seq-blue-1":"#E6F3FB","seq-blue-2":"#B6E2FA","seq-blue-3":"#66C4FF","seq-blue-4":"#009EFF","seq-blue-5":"#0A5FBC","seq-blue-6":"#143359","seq-teal-1":"#E6F7F5","seq-teal-2":"#B3E7E2","seq-teal-3":"#66CFC4","seq-teal-4":"#00AF9D","seq-teal-5":"#00737A","seq-teal-6":"#004B4F","seq-orange-1":"#FFF3E0","seq-orange-2":"#FFD9A8","seq-orange-3":"#F7B25C","seq-orange-4":"#EF8200","seq-orange-5":"#A75B00","seq-orange-6":"#6B3A00","div-1":"#A75B00","div-2":"#EF8200","div-3":"#F7C180","div-4":"#EFEDE7","div-5":"#99BDD1","div-6":"#005A8C","div-7":"#143359","slide-title-color":"#005A8C","headline-color":"#143359","subtitle-color":"#505050","label-color":"#505050","tick-color":"#737373","annotation-color":"#143359","footnote-color":"#737373","kpi-color":"#143359"};
  var STATUS = {"on_track":{"css":"status-on-track","symbol":"✓","word":"On track","ink":"#143359"},"at_risk":{"css":"status-at-risk","symbol":"!","word":"At risk","ink":"#143359"},"off_track":{"css":"status-off-track","symbol":"✕","word":"Off track","ink":"#FFFFFF"},"not_started":{"css":"status-not-started","symbol":"–","word":"Not started","ink":"#143359"},"done":{"css":"status-done","symbol":"✓","word":"Complete","ink":"#FFFFFF"}};
  window.MCK_PLOTLY_TEMPLATE = window.MCK_PLOTLY_TEMPLATE || {"layout":{"font":{"family":"Libre Franklin, Franklin Gothic Book, Arial, Helvetica, sans-serif","size":13,"color":"#505050"},"title":{"font":{"size":20,"color":"#143359","weight":600},"x":0,"xanchor":"left","xref":"container","pad":{"l":24},"subtitle":{"font":{"size":15,"color":"#505050"}}},"colorway":["#005A8C","#143359","#009EFF","#00AF9D","#05CE90","#EF8200"],"separators":".,","paper_bgcolor":"#FFFFFF","plot_bgcolor":"#FFFFFF","margin":{"l":64,"r":32,"t":96,"b":72},"bargap":0.33,"bargroupgap":0.08,"xaxis":{"showgrid":false,"zeroline":true,"zerolinecolor":"#8C8C8C","zerolinewidth":1.0,"showline":true,"linecolor":"#8C8C8C","linewidth":1.0,"ticks":"","tickfont":{"size":12,"color":"#737373"},"title":{"font":{"size":12,"color":"#737373"},"standoff":8},"automargin":true},"yaxis":{"showgrid":true,"zeroline":true,"zerolinecolor":"#8C8C8C","zerolinewidth":1.0,"showline":false,"linecolor":"#8C8C8C","linewidth":1.0,"ticks":"","tickfont":{"size":12,"color":"#737373"},"title":{"font":{"size":12,"color":"#737373"},"standoff":8},"automargin":true,"gridcolor":"#E6E4DE","gridwidth":0.75},"legend":{"orientation":"h","x":0,"xanchor":"left","y":1.02,"yanchor":"bottom","font":{"size":13,"color":"#505050"},"title":{"text":""}},"hoverlabel":{"bgcolor":"#143359","bordercolor":"#143359","font":{"family":"Libre Franklin, Franklin Gothic Book, Arial, Helvetica, sans-serif","color":"#FFFFFF","size":13}},"colorscale":{"sequential":[[0.0,"#E6F3FB"],[0.2,"#B6E2FA"],[0.4,"#66C4FF"],[0.6,"#009EFF"],[0.8,"#0A5FBC"],[1.0,"#143359"]],"diverging":[[0.0,"#A75B00"],[0.16666666666666666,"#EF8200"],[0.3333333333333333,"#F7C180"],[0.5,"#EFEDE7"],[0.6666666666666666,"#99BDD1"],[0.8333333333333334,"#005A8C"],[1.0,"#143359"]]},"annotationdefaults":{"font":{"size":13,"color":"#143359"},"showarrow":false,"align":"left"},"shapedefaults":{"line":{"color":"#8C8C8C","width":1}}},"data":{"scatter":[{"line":{"width":2.0},"marker":{"size":6}}],"bar":[{"marker":{"line":{"width":0}},"textfont":{"size":13},"cliponaxis":false}],"pie":[{"hole":0.62,"sort":true,"direction":"clockwise","marker":{"line":{"color":"#FFFFFF","width":2}}}],"waterfall":[{"increasing":{"marker":{"color":"#B4B0A5"}},"decreasing":{"marker":{"color":"#EF8200"}},"totals":{"marker":{"color":"#143359"}},"connector":{"line":{"color":"#8C8C8C","width":1.0}},"textfont":{"size":13},"cliponaxis":false}],"heatmap":[{"colorscale":[[0.0,"#E6F3FB"],[0.2,"#B6E2FA"],[0.4,"#66C4FF"],[0.6,"#009EFF"],[0.8,"#0A5FBC"],[1.0,"#143359"]],"colorbar":{"outlinewidth":0,"ticks":"","tickfont":{"size":12,"color":"#737373"}}}],"sankey":[{"node":{"color":"#143359","line":{"width":0},"thickness":14},"link":{"color":"rgba(0, 90, 140, 0.4)"}}]}};
  var MINUS = "−", SCALES = { K: 1e3, M: 1e6, B: 1e9 };
  var css = null;

  function tok(name) {
    name = String(name).replace(/^--mck-/, "").replace(/_/g, "-");
    try {
      css = css || getComputedStyle(document.documentElement);
      var val = css.getPropertyValue("--mck-" + name).trim();
      if (val) return val;
    } catch (e) { /* no DOM: fall back to the tokens */ }
    if (!(name in TOKENS)) throw new Error("mck.tok: no token --mck-" + name);
    return TOKENS[name];
  }

  function asSet(x) { return x == null ? [] : Array.isArray(x) ? x : [x]; }
  function highlight(labels, o) {
    o = o || {};
    var f = asSet(o.focus), a = asSet(o.accent), base = o.base || tok("chart-context");
    return labels.map(function (l) {
      return a.indexOf(l) >= 0 ? tok("chart-accent") : f.indexOf(l) >= 0 ? tok("chart-focus") : base;
    });
  }

  function round(x, d) { return Number(Math.abs(x).toFixed(d)); }
  function fmtNum(value, o) {
    o = o || {};
    var kind = o.kind || "auto", dec = o.decimals == null ? null : o.decimals;
    var sign = !!o.sign, prefix = o.prefix || "", suffix = o.suffix || "";
    if (value == null || Number.isNaN(Number(value))) return "–";
    var v = Number(value), unit = "", d;
    kind = ["auto", "plain", "pct"].indexOf(kind) >= 0 ? kind : String(kind).toUpperCase();
    if (["auto", "plain", "pct", "K", "M", "B"].indexOf(kind) < 0)
      throw new Error("mck.fmtNum: kind must be 'auto', 'plain', 'pct', 'K', 'M' or 'B', not " + kind);
    if (kind === "pct") { d = dec == null ? 1 : dec; unit = "%"; }
    else if (kind === "plain" || (kind === "auto" && Math.abs(v) < 1e4)) { d = dec == null ? 0 : dec; }
    else {
      var order = ["K", "M", "B"], abs = Math.abs(v), scaled;
      var k = kind !== "auto" ? order.indexOf(kind) : abs >= 1e9 ? 2 : abs >= 1e6 ? 1 : 0;
      for (;;) {
        scaled = v / SCALES[order[k]];
        d = dec == null ? (Math.abs(scaled) < 9.95 ? 1 : 0) : dec;
        if (kind === "auto" && k < 2 && round(scaled, d) >= 1000) { k += 1; continue; }   // 999,960 -> "1.0M"
        break;
      }
      v = scaled; unit = order[k];
    }
    var body = Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    if (parseFloat(body.replace(/,/g, "")) === 0) return prefix + body + unit + suffix;
    return (v > 0 && sign ? "+" : v < 0 ? MINUS : "") + prefix + body + unit + suffix;
  }

  function suppressSmall(rows, nKey, o) {
    o = o || {};
    var minN = o.minN == null ? 10 : o.minN, other = o.otherLabel === undefined ? "Other" : o.otherLabel;
    var unit = o.unit || "people", by = asSet(o.by), sums = [nKey].concat(asSet(o.sumKeys));
    if (!rows.length) return [[], ""];
    if (!(nKey in rows[0])) throw new Error("mck.suppressSmall: no key " + nKey);
    var keys = Object.keys(rows[0]);
    var numeric = keys.filter(function (c) {
      return by.indexOf(c) < 0 && rows.every(function (r) { return typeof r[c] === "number"; });
    });
    var groups = o.groupKeys ? asSet(o.groupKeys) : keys.filter(function (c) { return numeric.indexOf(c) < 0 && by.indexOf(c) < 0; });
    var small = function (r) { return r[nKey] < minN; };
    var isOther = function (r) { return groups.length > 0 && other != null && r[groups[0]] === other; };
    if (!rows.some(small)) return [rows.slice(), ""];
    var keep = rows.filter(function (r) { return !small(r) && !isOther(r); });
    var dropped = 0, merged = 0, out = [];
    if (other != null) {
      var parts = new Map();
      rows.filter(function (r) { return small(r) || isOther(r); }).forEach(function (r) {
        var key = JSON.stringify(by.map(function (b) { return r[b]; }));
        if (!parts.has(key)) parts.set(key, []);
        parts.get(key).push(r);
      });
      parts.forEach(function (part) {
        var n = part.reduce(function (s, r) { return s + r[nKey]; }, 0);
        var k = part.filter(function (r) { return small(r) && !isOther(r); }).length;
        if (n < minN) { dropped += k; return; }
        merged += k;
        var row = Object.assign({}, part[0]);
        groups.forEach(function (g) { row[g] = other; });
        numeric.forEach(function (c) {
          row[c] = sums.indexOf(c) >= 0 ? part.reduce(function (s, r) { return s + r[c]; }, 0)
            : part.reduce(function (s, r) { return s + r[c] * r[nKey]; }, 0) / n;           // n-weighted mean
        });
        out.push(row);
      });
    } else {
      dropped = rows.filter(function (r) { return small(r) && !isOther(r); }).length;
    }
    var g = function (k) { return k + " group" + (k !== 1 ? "s" : ""); }, notes = [];
    if (merged) notes.push(g(merged) + " with fewer than " + minN + " " + unit + " merged into \"" + other + "\"");
    if (dropped) notes.push(g(dropped) + " with fewer than " + minN + " " + unit + " not shown");
    var note = notes.join("; ");
    return [keep.concat(out), note.charAt(0).toUpperCase() + note.slice(1) + "."];
  }

  function lum(hex) {
    var n = parseInt(String(hex).replace("#", ""), 16);
    return [n >> 16, (n >> 8) & 255, n & 255].reduce(function (s, c, i) {
      c /= 255;
      return s + [0.2126, 0.7152, 0.0722][i] * (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
    }, 0);
  }
  function textOn(hex) {
    var f = lum(hex), navy = tok("text-headline");
    return 1.05 / (f + 0.05) >= (f + 0.05) / (lum(navy) + 0.05) ? "#FFFFFF" : navy;
  }
  function alpha(hex, a) {
    var n = parseInt(String(hex).replace("#", ""), 16);
    return "rgba(" + (n >> 16) + ", " + ((n >> 8) & 255) + ", " + (n & 255) + ", " + a + ")";
  }

  function status(key) {
    var s = STATUS[String(key).replace(/-/g, "_")];
    if (!s) throw new Error("mck.status: unknown status " + key + " (use " + Object.keys(STATUS).join(", ") + ")");
    return { color: tok(s.css), symbol: s.symbol, word: s.word, ink: s.ink };
  }

  function isObj(x) { return x && typeof x === "object" && !Array.isArray(x); }
  function merge(a, b) {
    var out = Object.assign({}, a);
    Object.keys(b || {}).forEach(function (k) { out[k] = isObj(out[k]) && isObj(b[k]) ? merge(out[k], b[k]) : b[k]; });
    return out;
  }
  function zeroLine(axis) {                                    // a thin baseline at 0, for charts with a hidden value axis
    var line = { color: tok("chart-axis"), width: window.MCK_PLOTLY_TEMPLATE.layout.xaxis.linewidth };
    return axis === "y"
      ? { type: "line", y0: 0, y1: 0, x0: 0, x1: 1, xref: "paper", layer: "above", line: line }
      : { type: "line", x0: 0, x1: 0, y0: 0, y1: 1, yref: "paper", layer: "above", line: line };
  }
  var BAR_GAP = window.MCK_PLOTLY_TEMPLATE.layout.bargap;      // bar : gap = 2 : 1
  var LAYOUTS = {
    bar: function () {                                         // horizontal, labelled bars; rows top to bottom in data order
      return { bargap: BAR_GAP, xaxis: { visible: false, rangemode: "tozero" },
               yaxis: { showgrid: false, autorange: "reversed", ticklabelstandoff: 8, automargin: true }, shapes: [zeroLine("x")] };
    },
    line: function () {
      return { hovermode: "x unified", margin: { r: 150 }, xaxis: { showgrid: false, tickangle: 0 },   // never rotate
               yaxis: { gridcolor: tok("chart-grid"), tickformat: "," } };
    },
    waterfall: function () {                                   // labelled bars: no value axis, baseline at 0
      return { bargap: BAR_GAP, xaxis: { showgrid: false, showline: false, zeroline: false, automargin: true },
               yaxis: { visible: false, rangemode: "tozero" }, shapes: [zeroLine("y")] };
    },
    stacked: function () {                                     // horizontal 100% stacked bars
      return { barmode: "stack", bargap: BAR_GAP, xaxis: { visible: false, range: [0, 100] },
               yaxis: { showgrid: false, autorange: "reversed", ticklabelstandoff: 8, automargin: true }, shapes: [zeroLine("x")] };
    },
    heatmap: function () {
      var off = { showgrid: false, showline: false, zeroline: false, ticks: "", tickangle: 0 };
      return { plot_bgcolor: tok("surface-default"), xaxis: merge(off, { side: "top" }),
               yaxis: merge(off, { autorange: "reversed", ticklabelstandoff: 8 }) };
    },
    sankey: function () { return { margin: { t: 8, r: 8, b: 8, l: 8 } }; },
    roadmap: function () {                                     // Gantt as horizontal stacked bars (offset + segments)
      return { barmode: "stack", bargap: 0.45, xaxis: { showgrid: false, zeroline: false, side: "top" },
               yaxis: { showgrid: false, zeroline: false, autorange: "reversed", ticklabelstandoff: 8 } };
    }
  };
  function plotlyLayout(kind, extra) {
    if (!LAYOUTS[kind]) throw new Error("mck.plotlyLayout: kind must be one of " + Object.keys(LAYOUTS).join(", "));
    var base = { template: window.MCK_PLOTLY_TEMPLATE, autosize: true, showlegend: false,
                 margin: { t: 24, r: 16, b: 32, l: 8 } };      // the HTML carries the titles, so a small margin
    return merge(merge(base, LAYOUTS[kind]()), extra);
  }

  function srTable(id, caption, head, rows) {                  // visually hidden data table (class sr-only)
    var esc = function (s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); };
    document.getElementById(id).innerHTML = "<caption>" + esc(caption) + "</caption><thead><tr>"
      + head.map(function (h) { return '<th scope="col">' + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>"
      + rows.map(function (r) {
        return '<tr><th scope="row">' + esc(r[0]) + "</th>"
          + r.slice(1).map(function (x) { return "<td>" + esc(x) + "</td>"; }).join("") + "</tr>";
      }).join("") + "</tbody>";
  }
  function ready(fn) {                                         // draw after Libre Franklin loads (Plotly measures text once)
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fn); else window.addEventListener("load", fn);
  }

  window.mck = { tok: tok, highlight: highlight, fmtNum: fmtNum, suppressSmall: suppressSmall, textOn: textOn,
                 status: status, plotlyLayout: plotlyLayout, alpha: alpha, zeroLine: zeroLine, srTable: srTable,
                 ready: ready, MINUS: MINUS, plotConfig: { displayModeBar: false, responsive: true } };
})();
