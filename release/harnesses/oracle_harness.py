#!/usr/bin/env python
"""
E0.5 tool-oracle identifiability sweep -> ledger/identifiability/

For a stratified sample across all 7 crystal systems (MP + JARVIS), reconstruct 3D
structure from the multi-view projections and run spglib, as a function of:
  view count : {2, 3, 4} principal views
  style      : centroid-extraction noise {ideal 0.0, realistic 0.03A, pessimistic 0.10A}
Recovery is scored at THREE hierarchy levels — crystal system, point group, space
group — reported as micro accuracy, macro-F1, and per-crystal-system breakdown, so
the Gate 0 retargeting evidence is explicit about which levels are view-identifiable.
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import warnings; warnings.filterwarnings("ignore")
import numpy as np

from cocr.data import fetch_mp_stratified, fetch_jarvis_stratified
from cocr.render import conventional_cell, VIEW_ORDER
from cocr.labels import make_labels
from cocr.reconstruct import reconstruct_positions, recover_symmetry

LEDGER = os.path.join(os.path.dirname(__file__), "..", "ledger", "identifiability")

VIEW_COUNTS = [2, 3, 4, 5]   # extended for oracle_view_curve: 5 added. 1 view is GEOMETRICALLY
                             # IMPOSSIBLE (triangulation needs >=2 rays); 8 does not
                             # exist (only 5 cameras in the frozen protocol).
# The oracle upper-bounds identifiability under PERFECT centroid extraction (noise=0):
# this is the decision-relevant quantity for Gate 0 (can the flagship label be
# recovered from the view set at all, in the best case?). A single small-noise arm is
# retained ONLY as a reconstruction-stability caveat (reported separately, NOT as an
# identifiability measure): under independent per-view centroid jitter this specific
# triangulator loses cross-view correspondence and spglib needs symprec ~6*sigma to
# see symmetry. Observed failure mode at this noise level is wrong/lower or None SG
# assignments (e.g. mp-1229124 R3c over-triangulates 60 vs 48 atoms; mp-861724
# 225->221), NOT inflation to higher symmetry — the adaptive symprec is capped at
# 0.25 A precisely to keep it from merging distinct atoms into a spuriously higher
# setting. That fragility is an artifact of THIS reconstruction algorithm, not of the
# renders — the flagship VLM does not triangulate — so it must not enter the Gate 0
# decision.
STYLES = {"ideal": 0.0}
STABILITY_NOISE = 0.03  # separate stability caveat only


def score(recovered, truth):
    return recovered is not None and recovered == truth


def _metric_system(lat, tol=1e-2):
    """box_sufficiency's conventional-cell metric rule, verbatim, so strata are comparable across checkpoints."""
    a, b, c = lat.abc
    al, be, ga = lat.angles
    eq = lambda x, y: abs(x - y) < tol * max(abs(x), abs(y), 1e-9)
    ang = lambda x, y: abs(x - y) < 0.5
    if eq(a, b) and eq(b, c) and ang(al, 90) and ang(be, 90) and ang(ga, 90): return "cubic"
    if eq(a, b) and ang(al, 90) and ang(be, 90) and ang(ga, 120): return "hexagonal_or_trigonal"
    if eq(a, b) and eq(b, c) and ang(al, be) and ang(be, ga) and not ang(al, 90): return "trigonal_rhombohedral"
    if eq(a, b) and ang(al, 90) and ang(be, 90) and ang(ga, 90): return "tetragonal"
    if ang(al, 90) and ang(be, 90) and ang(ga, 90): return "orthorhombic"
    if ang(al, 90) and ang(ga, 90): return "monoclinic"
    return "triclinic"


def _box_sufficient(conv, true_cs):
    ms = _metric_system(conv.lattice)
    if ms == "hexagonal_or_trigonal": return False, ms
    if ms == "trigonal_rhombohedral": return (true_cs == "trigonal"), ms
    return (ms == true_cs), ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-system", type=int, default=10)
    ap.add_argument("--min-sites", type=int, default=2)
    ap.add_argument("--max-sites", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(args.seed)

    print(f"[E0.5] fetching stratified sample ({args.per_system}/system/source)...")
    mp = fetch_mp_stratified(args.per_system, num_elements=(2, 4),
                             num_sites=(args.min_sites, args.max_sites))
    jv = fetch_jarvis_stratified(args.per_system, min_sites=args.min_sites,
                                 max_sites=args.max_sites)
    records = mp + jv
    print(f"[E0.5] {len(records)} structures ({len(mp)} MP + {len(jv)} JARVIS)")

    rows = []
    for k, rc in enumerate(records):
        try:
            conv = conventional_cell(rc["structure"])
            lab = make_labels(rc["structure"], rc["material_id"], rc["source"])
        except Exception as e:
            rows.append({"material_id": rc["material_id"], "error": str(e)})
            continue
        truth = {"crystal_system": lab["crystal_system"],
                 "point_group": lab["point_group"],
                 "space_group": lab["space_group"]["number"]}
        base = {"material_id": rc["material_id"], "source": rc["source"],
                "crystal_system": lab["crystal_system"], "n_sites": len(conv),
                "true_sg": truth["space_group"], "true_pg": truth["point_group"],
                "box_sufficient": _box_sufficient(conv, lab["crystal_system"])[0],
                "metric_class": _box_sufficient(conv, lab["crystal_system"])[1],
                "results": {}}
        for nv in VIEW_COUNTS:
            views = VIEW_ORDER[:nv]
            # --- identifiability arm: perfect extraction (Gate 0 evidence) ---
            rec = reconstruct_positions(conv, views, tol=0.15, centroid_noise=0.0)
            sym = recover_symmetry(rec, conv.lattice, symprec=0.01)
            base["results"][f"{nv}v_ideal"] = {
                "n_recovered": rec["n_recovered"], "n_true": rec["n_true"],
                "count_match": rec["count_match"],
                "rec_sg": sym["space_group_number"], "rec_pg": sym["point_group"],
                "rec_cs": sym["crystal_system"],
                "cs_ok": score(sym["crystal_system"], truth["crystal_system"]),
                "pg_ok": score(sym["point_group"], truth["point_group"]),
                "sg_ok": score(sym["space_group_number"], truth["space_group"]),
            }
        # --- stability caveat (4 views only, reported separately, NOT Gate 0) ---
        rec_n = reconstruct_positions(conv, VIEW_ORDER, tol=max(0.15, 4.0 * STABILITY_NOISE),
                                      centroid_noise=STABILITY_NOISE, rng=rng)
        # adaptive symprec matched to the MEASURED reconstruction RMSD (principled
        # tolerance-matching); capped so it cannot over-merge into higher symmetry.
        adasp = min(0.25, max(0.01, 6.0 * (rec_n["faithful_rmsd"] or 0.0)))
        sym_n = recover_symmetry(rec_n, conv.lattice, symprec=adasp)
        base["stability_4v"] = {
            "noise": STABILITY_NOISE, "adaptive_symprec": round(adasp, 4),
            "faithful_rmsd": rec_n["faithful_rmsd"], "count_match": rec_n["count_match"],
            "rec_sg": sym_n["space_group_number"],
            "sg_ok": score(sym_n["space_group_number"], truth["space_group"]),
            "cs_ok": score(sym_n["crystal_system"], truth["crystal_system"]),
        }
        rows.append(base)
        if (k + 1) % 20 == 0:
            print(f"  ...{k+1}/{len(records)}")

    os.makedirs(LEDGER, exist_ok=True)
    out = {"rows": rows, "view_counts": VIEW_COUNTS, "styles": STYLES,
           "meta": {"per_system": args.per_system, "n_mp": len(mp), "n_jarvis": len(jv),
                    "seed": args.seed, "elapsed_sec": round(time.time() - t0, 1)}}
    with open(os.path.join(LEDGER, "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"[E0.5] wrote results.json ({len(rows)} rows, {out['meta']['elapsed_sec']}s)")


if __name__ == "__main__":
    main()
