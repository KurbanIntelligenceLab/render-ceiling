#!/usr/bin/env python
"""G1 — full detector characterisation against Proposition 2's soundness/completeness target.

The audit's protocol asks for, per view: (a) the centroid-error distribution, (b) precision
(no spurious detections), and (c) the fraction of structures whose compared distances avoid the
band [tau - 2*kappa*eps, tau + 2*kappa*eps]. (a) and (b) existed only for 28 structures on 3 views;
(c) had never been computed at all, because it needs per-atom centroid errors in Angstrom and the
stored records keep per-view pixel aggregates.

Renders are regenerated from the local CIFs under the frozen protocol (conventional cell, 2x2x2
supercell, px=768, radii=0.5). This reproduces atom_detection's 84 recorded view measurements exactly,
including the pixel-dependent detection counts, so the regenerated images are the frozen ones.

CPU only, zero API calls.
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from multiprocessing import Pool

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, HERE)

import numpy as np
from pymatgen.core import Structure

from ase.io.utils import PlottingVariables

from cocr.render import conventional_cell, render_views, VIEW_ORDER, VIEWS, _to_atoms
from detect_atoms import ground_truth_pixels, detect, match, overlap_covariate


def px_per_angstrom(structure, view, px=768, supercell=(2, 2, 2), radii=0.5):
    """Pixels per Angstrom for this view, from the same letterboxed transform the GT uses.

    ground_truth_pixels maps world units to pixels by dividing by s = max(pv.w, pv.h) and
    multiplying by px, so the scale is exactly px / s. Recovering it lets a centroid error
    measured in pixels be converted to Angstrom, which is what Proposition 2's band needs.
    """
    at = _to_atoms(structure, supercell)
    pv = PlottingVariables(at, rotation=VIEWS[view], show_unit_cell=2, radii=radii, scale=1)
    return px / max(pv.w, pv.h)

ROOT = os.path.dirname(HERE)
OUT = f"{ROOT}/results/detector_characterisation"
RENDERS = "/tmp/rc_g1_renders"

# Frozen label tolerance and the measured conditioning constant from the theory audit.
TAU = 0.01
KAPPA = 1.7689


def one(args):
    mid, cif, truth = args
    try:
        conv = conventional_cell(Structure.from_str(cif, fmt="cif"))
    except Exception as e:
        return mid, {"error": f"{type(e).__name__}: {e}"}
    d = os.path.join(RENDERS, mid)
    os.makedirs(d, exist_ok=True)
    try:
        render_views(conv, d, f"MP_{mid}", supercell=(2, 2, 2))
    except Exception as e:
        return mid, {"error": f"render: {type(e).__name__}: {e}"}

    per_view = {}
    for v in VIEW_ORDER:
        p = os.path.join(d, f"MP_{mid}_view{VIEW_ORDER.index(v)}.png")
        if not os.path.exists(p):
            continue
        gt, gd, dep, _species = ground_truth_pixels(conv, v)
        scale = px_per_angstrom(conv, v)
        det, areas, _ = detect(p)
        tp, fp, fn, errs = match(det, gt, gd)
        per_view[v] = {
            "n_gt": int(len(gt)), "n_det": int(len(det)),
            "tp": int(tp), "fp": int(fp), "fn": int(fn),
            "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1),
            "median_centroid_err_px": float(np.median(errs)) if errs else None,
            "centroid_errs_px": [float(x) for x in errs],
            "px_per_angstrom": float(scale) if scale else None,
            "overlap_covariate": overlap_covariate(gt, gd, dep),
        }
    # clean up renders for this structure; they are regenerable and 210x5 PNGs is bulk
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    os.rmdir(d)
    return mid, {"truth": truth, "views": per_view}


def main():
    S = json.load(open(f"{ROOT}/data/e3/structures.json"))
    rows = [json.loads(l) for l in open(f"{ROOT}/data/e3/eval.jsonl")]
    jobs = [(r["material_id"], S[r["material_id"]]["cif"], r["crystal_system"]) for r in rows]
    print(f"{len(jobs)} structures x {len(VIEW_ORDER)} views", flush=True)

    per = {}
    with Pool(10) as pool:
        for i, (mid, res) in enumerate(pool.imap_unordered(one, jobs, chunksize=2), 1):
            per[mid] = res
            if i % 25 == 0:
                print(f"  {i}/{len(jobs)}", flush=True)

    os.makedirs(OUT, exist_ok=True)
    json.dump({"per_structure": per,
               "config": {"tau": TAU, "kappa": KAPPA, "views": VIEW_ORDER,
                          "render": "conventional cell, 2x2x2 supercell, px=768, radii=0.5",
                          "n": len(jobs),
                          "sample": "data/e3 eval (original 210-structure evaluation sample)"}},
              open(f"{OUT}/detection_full.json", "w"))
    print("wrote detection_full.json", flush=True)


if __name__ == "__main__":
    os.makedirs(RENDERS, exist_ok=True)
    main()
