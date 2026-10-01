# Map geometry for the guide

Read by `guide/geo_shapes.py` (a small TopoJSON reader; no geopandas needed) for the Geo-spatial exhibits.

| File | What | Source |
|---|---|---|
| `states-albers-10m.json` | 50 states and DC, projected to Albers USA (975 × 610 px, Alaska and Hawaii inset), ids = state FIPS | [us-atlas](https://github.com/topojson/us-atlas) 3.x, `states-albers-10m.json`, unchanged |
| `countries-110m.json` | World countries in longitude/latitude, ids = ISO 3166 numeric | [world-atlas](https://github.com/topojson/world-atlas) 2.x, `countries-110m.json`, unchanged |
| `counties-north-texas.json` | The 94 counties around Dallas-Fort Worth, same Albers USA frame as the states file | Cut from us-atlas 3.x `counties-albers-10m.json` by `make_subset.py` |

Downloaded from `https://cdn.jsdelivr.net/npm/us-atlas@3/` and `https://cdn.jsdelivr.net/npm/world-atlas@2/`.

**Licenses.** us-atlas and world-atlas are ISC-licensed (Copyright 2013-2019 Michael Bostock). The underlying boundaries
are the U.S. Census Bureau's cartographic boundary files and Natural Earth, both in the public domain.

To cut a different county subset, download the full counties file, change `FRAME` in `make_subset.py`, and run
`python guide/geodata/make_subset.py path/to/counties-albers-10m.json`.
