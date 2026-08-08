"""Repo-relative paths. Every script imports these instead of hardcoding a location.

Override the repo root with the RENDER_CEILING_ROOT environment variable.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
REPO = _os.environ.get("RENDER_CEILING_ROOT", _os.path.dirname(_HERE))
ROOT = REPO
RESULTS = _os.path.join(REPO, "results")
DATA = _os.path.join(REPO, "data")
SRC = _os.path.join(REPO, "scripts", "src")
SCRIPTS = _os.path.join(REPO, "scripts")
