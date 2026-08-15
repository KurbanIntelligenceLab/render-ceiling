#!/usr/bin/env python
"""Regenerate the benchmark's rendered images from the CIFs in this repository.

The renders are the model inputs: five orthographic views of each evaluation structure.
They are not committed — 2,100 PNGs that are a pure function of inputs already here — so
this script rebuilds them byte-for-byte from `data/<sample>/structures.json`, which
carries the CIF text for every structure in the split.

    python scripts/render_from_cifs.py --sample e3   --split eval
    python scripts/render_from_cifs.py --sample e3x  --split eval

Output goes to `data/<sample>/renders/<split>/`, matching the paths the `images` field of
`<sample>/<split>.jsonl` already names, so the harnesses resolve without further work.

This differs from `render_e3.py`, which fetches structures from the Materials Project and
therefore needs an API key. Everything this script reads is in the repository, so a reader
can reproduce the inputs offline. The render itself is deterministic: the camera set and
pixel size are frozen constants and no stage draws a random number, so re-rendering the
same CIF gives the same image.
"""
import argparse
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from pymatgen.core import Structure  # noqa: E402

from cocr.render import VIEW_ORDER, conventional_cell, render_views  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", required=True, choices=["e3", "e3x"],
                    help="e3 is the original split, e3x the expansion replication")
    ap.add_argument("--split", default="eval", choices=["train", "eval"])
    ap.add_argument("--root", default=".", help="repository root")
    args = ap.parse_args()

    base = os.path.join(args.root, "data", args.sample)
    rows = [json.loads(line) for line in open(f"{base}/{args.split}.jsonl")]
    cifs = json.load(open(f"{base}/structures.json"))

    missing = [r["material_id"] for r in rows if r["material_id"] not in cifs]
    if missing:
        sys.exit(f"{len(missing)} structures in {args.split}.jsonl are absent from "
                 f"structures.json, e.g. {missing[:3]}")

    out_dir = os.path.join(base, "renders", args.split)
    os.makedirs(out_dir, exist_ok=True)
    for i, row in enumerate(rows, 1):
        mid = row["material_id"]
        # the committed image paths are <source>_<material_id>_view<k>.png; the stem is
        # taken from the row itself rather than rebuilt, so a naming change in the data
        # cannot silently desynchronise the renders from the paths that reference them
        stem = os.path.basename(row["images"][0]).rsplit("_view", 1)[0]
        structure = Structure.from_str(cifs[mid]["cif"], fmt="cif")
        render_views(conventional_cell(structure), out_dir, stem,
                     supercell=(2, 2, 2), view_names=VIEW_ORDER)
        if i % 25 == 0 or i == len(rows):
            print(f"  {i}/{len(rows)}", flush=True)

    expected = {os.path.join(args.root, p) for r in rows for p in r["images"]}
    absent = sorted(p for p in expected if not os.path.exists(p))
    if absent:
        sys.exit(f"{len(absent)} expected image paths were not produced, "
                 f"e.g. {absent[:2]}")
    print(f"{out_dir}: {len(rows)} structures, {len(expected)} images, "
          f"every path referenced by {args.split}.jsonl resolves")


if __name__ == "__main__":
    main()
