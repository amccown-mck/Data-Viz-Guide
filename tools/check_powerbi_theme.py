"""Validate dist/powerbi/mckesson-dataviz-theme.json against Microsoft's report-theme JSON schema.

    python tools/check_powerbi_theme.py                    # downloads the newest schema from GitHub
    python tools/check_powerbi_theme.py --schema FILE      # validate against a local copy (offline / CI)

Schemas: https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema
Also checks the house rules the schema can't: unique data colors, the categorical order, and the font stack.
Needs: pip install jsonschema
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "dist" / "powerbi" / "mckesson-dataviz-theme.json"
TOKENS = ROOT / "tokens" / "tokens.json"
LISTING = "https://api.github.com/repos/microsoft/powerbi-desktop-samples/contents/Report%20Theme%20JSON%20Schema"


def latest_schema() -> tuple[str, dict]:
    with urllib.request.urlopen(LISTING, timeout=30) as r:
        files = [f for f in json.load(r) if f["name"].startswith("reportThemeSchema-")]
    newest = max(files, key=lambda f: tuple(int(p) for p in f["name"][18:-5].split(".")))
    with urllib.request.urlopen(newest["download_url"], timeout=60) as r:
        return newest["name"], json.load(r)


def main() -> int:
    import jsonschema

    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", type=Path, help="local schema file instead of downloading the newest")
    args = ap.parse_args()
    name, schema = (args.schema.name, json.loads(args.schema.read_text(encoding="utf-8"))) if args.schema else latest_schema()
    theme = json.loads(THEME.read_text(encoding="utf-8"))
    validator = jsonschema.validators.validator_for(schema)(schema)
    problems = [f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in validator.iter_errors(theme)]

    colors = theme.get("dataColors", [])
    if len(set(c.upper() for c in colors)) != len(colors):
        problems.append("dataColors repeat a color, so two series would look the same")
    cat = json.loads(TOKENS.read_text(encoding="utf-8"))["color"]["categorical"]["values"]
    if [c.upper() for c in colors[:6]] != [c.upper() for c in cat[:6]]:
        problems.append("the first 6 dataColors must be the categorical palette in its fixed order")
    if not theme["textClasses"]["label"]["fontFace"].startswith("Libre Franklin, Segoe UI"):
        problems.append("font stack should be 'Libre Franklin, Segoe UI, ...' so viewers without the font fall back to Segoe UI")

    print(f"{THEME.relative_to(ROOT)} vs {name}: {'OK' if not problems else f'{len(problems)} problem(s)'}")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
