#!/usr/bin/env python
"""View-subset sweep of the ideal-extraction oracle (R1) over the frozen five-camera set.

Tests Corollary 3(a): R1 is non-decreasing in the view set at tau = 0. At tau > 0 the
corollary is approximate, so per-structure monotonicity violations are counted and
characterised rather than assumed absent.

Runs on the LOCAL evaluation CIFs (data/e3/structures.json + data/e3/eval.jsonl). It does
NOT call fetch_mp_stratified: oracle_view_curve records that the live database query returns a drifting
candidate pool (21 of 280 material_ids changed between runs at the same seed), so a live
fetch would not be comparable to the sample every other arm in the paper was scored on.

CPU only, zero API calls.
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from itertools import combinations
from multiprocessing import Pool

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import numpy as np
from pymatgen.core import Structure

from cocr.render import VIEW_ORDER, conventional_cell
from cocr.reconstruct import reconstruct_positions, recover_symmetry

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYMPREC, ANGLE_TOL, TOL = 0.01, 5.0, 0.15

SUBSETS = [list(c) for k in (2, 3, 4, 5) for c in combinations(VIEW_ORDER, k)]


def one(args):
    mid, cif, truth = args
    try:
        conv = conventional_cell(Structure.from_str(cif, fmt="cif"), symprec=SYMPREC)
    except Exception as e:
        return mid, {"error": f"{type(e).__name__}: {e}"}
    out = {}
    for sub in SUBSETS:
        key = "|".join(sub)
        try:
            rec = reconstruct_positions(conv, sub, tol=TOL)
            sym = recover_symmetry(rec, conv.lattice, symprec=SYMPREC, angle_tol=ANGLE_TOL)
            out[key] = {
                "correct": bool(sym["ok"] and sym["crystal_system"] == truth),
                "pred": sym["crystal_system"],
                "n_recovered": rec["n_recovered"],
                "n_true": rec["n_true"],
                "faithful_rmsd": rec["faithful_rmsd"],
            }
        except Exception as e:
            out[key] = {"correct": False, "pred": None, "error": f"{type(e).__name__}: {e}"}
    return mid, out


def main():
    S = json.load(open(f"{ROOT}/data/e3/structures.json"))
    rows = [json.loads(l) for l in open(f"{ROOT}/data/e3/eval.jsonl")]
    jobs = [(r["material_id"], S[r["material_id"]]["cif"], r["crystal_system"]) for r in rows]
    print(f"structures {len(jobs)} x subsets {len(SUBSETS)} = {len(jobs)*len(SUBSETS)} reconstructions",
          flush=True)

    per = {}
    with Pool(10) as p:
        for i, (mid, res) in enumerate(p.imap_unordered(one, jobs, chunksize=4), 1):
            per[mid] = res
            if i % 20 == 0:
                print(f"  {i}/{len(jobs)}", flush=True)

    json.dump({"subsets": ["|".join(s) for s in SUBSETS], "per_structure": per,
               "config": {"symprec": SYMPREC, "angle_tolerance": ANGLE_TOL, "ray_tol": TOL,
                          "view_order": VIEW_ORDER, "n": len(jobs),
                          "sample": "data/e3 eval (original 210-structure evaluation sample)"}},
              open(f"{ROOT}/results/view_subset_sweep/raw.json", "w"))
    print("wrote raw.json", flush=True)


if __name__ == "__main__":
    os.makedirs(f"{ROOT}/results/view_subset_sweep", exist_ok=True)
    main()
