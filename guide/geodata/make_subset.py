"""Cut the North Texas county subset from the full us-atlas counties file (run once; output is committed).

    python guide/geodata/make_subset.py path/to/counties-albers-10m.json

Keeps every county whose bounding box meets the frame below (Albers USA px, the us-atlas frame), with only the arcs
they use, re-indexed. Quantization and transform are unchanged, so the result reads like the original.
"""
import json
import sys
from pathlib import Path

FRAME = (428, 404, 520, 478)        # x0, y0, x1, y1 around Dallas-Fort Worth (y down)


def main(src: str) -> None:
    t = json.loads(Path(src).read_text(encoding="utf-8"))
    (sx, sy), (tx, ty) = t["transform"]["scale"], t["transform"]["translate"]
    absolute = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x, y = x + dx, y + dy
            pts.append((x * sx + tx, y * sy + ty))
        absolute.append(pts)

    def refs(g):
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        return [r if r >= 0 else ~r for poly in polys for ring in poly for r in ring]

    keep = []
    for g in t["objects"]["counties"]["geometries"]:
        pts = [p for i in refs(g) for p in absolute[i]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if max(xs) >= FRAME[0] and min(xs) <= FRAME[2] and max(ys) >= FRAME[1] and min(ys) <= FRAME[3]:
            keep.append(g)
    used = sorted({i for g in keep for i in refs(g)})
    new = {old: k for k, old in enumerate(used)}

    def remap(arcs):
        return [remap(a) for a in arcs] if isinstance(arcs[0], list) else \
            [new[r] if r >= 0 else ~new[~r] for r in arcs]

    geoms = [{"type": g["type"], "id": g["id"], "properties": g["properties"], "arcs": remap(g["arcs"])} for g in keep]
    out = {"type": "Topology", "bbox": t["bbox"], "transform": t["transform"],
           "objects": {"counties": {"type": "GeometryCollection", "geometries": geoms}},
           "arcs": [t["arcs"][i] for i in used]}
    dst = Path(__file__).with_name("counties-north-texas.json")
    dst.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"{len(geoms)} counties, {len(used)} arcs -> {dst.name} ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main(sys.argv[1])
