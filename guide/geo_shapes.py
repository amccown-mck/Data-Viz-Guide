"""Thin shim: the map code now lives in the mckviz package (python/mckviz/geo.py, data in python/mckviz/geodata/).

guide/ex_geo.py still does `import geo_shapes as gs`; this re-exports mckviz.geo and adds the guide's site list.
Not named ex_*.py, so exhibits.py does not import it as an exhibit module.
"""
from __future__ import annotations

from mckviz.geo import *  # noqa: F401,F403
from mckviz.geo import (_area, _clip_x, _conic, _conic_inv, _split_antimeridian)  # noqa: F401  (private helpers)

# Public city locations (lon, lat) for the guide's site markers. Reference geography, not data.
CITY = {"Memphis": (-90.05, 35.15), "Dallas": (-96.80, 32.78), "Columbus": (-82.99, 39.96),
        "Atlanta": (-84.39, 33.75), "Phoenix": (-112.07, 33.45), "Sacramento": (-121.49, 38.58),
        "Harrisburg": (-76.88, 40.27), "Chicago": (-87.63, 41.88), "Kansas City": (-94.58, 39.10),
        "Orlando": (-81.38, 28.54), "Denver": (-104.99, 39.74), "Seattle": (-122.33, 47.61),
        "Albany": (-73.76, 42.65), "Boise (satellite)": (-116.20, 43.62), "Irving": (-96.95, 32.81),
        "Fort Worth": (-97.33, 32.75)}
