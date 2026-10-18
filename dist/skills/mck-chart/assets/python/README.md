# mckviz wheel

`mckviz-1.1.0-py3-none-any.whl`: the kit's Python package with the Libre Franklin fonts and the map data inside, built from `python/` in the repo. Install it with no access to GitHub:

    pip install assets/python/mckviz-1.1.0-py3-none-any.whl

(add `--no-deps` when PyPI is unreachable and matplotlib and numpy are already installed). `python scripts/check_env.py` does this for you and says which path worked.

The wheel is built into this folder by `python tools/build_skill.py --zip` and `tools/make_bundle.py` (with uv), so it is in the skill zip and the release bundle but not in git. If it is missing here, use one of those, or install from GitHub.
