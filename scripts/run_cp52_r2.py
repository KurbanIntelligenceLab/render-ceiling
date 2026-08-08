"""CP52 rung R2 — the oracle run on DETECTOR output instead of ground-truth projections.

The detector gives pixel centres per view with no species and no correspondence. The oracle's
reconstruct_positions needs species-labelled projections, so R2 must supply species from the detected
disc colour, matched against the render's own CPK palette. Everything downstream (ray intersection,
cross-view verification, dedup, spglib) is the R1 path unchanged.
"""
import os as _o, sys as _s
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), ''))
from _paths import SCRIPTS, SRC
import json, sys, os, time, warnings, importlib.util
import numpy as np
warnings.filterwarnings("ignore"); sys.path.insert(0, f"{SRC}")
from pymatgen.core import Structure
from cocr.render import conventional_cell, VIEW_ORDER
from cocr import reconstruct as RC
from cocr.reconstruct import projection_matrices, _ray, _ray_intersection

_s = importlib.util.spec_from_file_location("da", f"{SCRIPTS}/detect_atoms.py")
da = importlib.util.module_from_spec(_s); _s.loader.exec_module(da)

PX = 768

def palette(conv, view):
    """Map each species to its rendered disc colour, read from the renderer itself."""
    from ase.data.colors import jmol_colors
    from ase.data import atomic_numbers
    out = {}
    for s in {sp.symbol for sp in conv.species}:
        z = atomic_numbers[s]
        out[s] = tuple((np.array(jmol_colors[z]) * 255).astype(int))
    return out

def species_of(colour, pal):
    c = np.array(colour, dtype=float)
    best, bd = None, 1e18
    for s, rgb in pal.items():
        d = float(((c - np.array(rgb, dtype=float)) ** 2).sum())
        if d < bd: bd, best = d, s
    return best

def pixels_to_world_units(conv, view, xy):
    """Invert the letterboxed pixel mapping ground_truth_pixels applies, so detected centres land in
    the same 2D units the oracle's projections use. Calibrated against the ground-truth mapping."""
    from cocr.render import _to_atoms
    from ase.visualize.plot import Plot as _P  # noqa
    return xy  # placeholder, replaced by the calibrated affine below

def calibrate(conv, view):
    """Least-squares affine from ground-truth PIXELS to oracle PROJECTION units, per view."""
    XY, d, z, _ = da.ground_truth_pixels(conv, view, px=PX)
    R = projection_matrices([view])[0]
    P = (conv.cart_coords @ R)[:, :2]
    n = min(len(XY), len(P))
    # ground_truth_pixels covers the 2x2x2 supercell in _to_atoms order (tiled k % n_cell);
    # the first n_cell entries correspond to the conventional-cell atoms in order.
    A = np.c_[XY[:n], np.ones(n)]
    sol, *_ = np.linalg.lstsq(A, P[:n], rcond=None)
    resid = float(np.abs(A @ sol - P[:n]).max())
    return sol, resid

def r2_one(conv, render_dir, img_paths, tol=0.15):
    pal = palette(conv, VIEW_ORDER[0])
    proj, species_per_view, calres = [], [], []
    for vi, v in enumerate(VIEW_ORDER):
        # render filenames are <SOURCE>_<material_id>_view<N>.png, N indexing VIEW_ORDER
        p = os.path.join(render_dir, os.path.basename(img_paths[vi]))
        if not os.path.exists(p): return {"error": f"missing render {v}"}
        centres, areas, cols = da.detect(p)
        if len(centres) == 0: return {"error": f"no detections in {v}"}
        sol, resid = calibrate(conv, v); calres.append(resid)
        A = np.c_[centres, np.ones(len(centres))]
        proj.append(A @ sol)
        species_per_view.append([species_of(c, pal) for c in cols])
    Rs = projection_matrices(VIEW_ORDER)
    cand = []
    for i, s0 in enumerate(species_per_view[0]):
        x0a, dA = _ray(*proj[0][i], Rs[0])
        for j, s1 in enumerate(species_per_view[1]):
            if s1 != s0: continue
            x0b, dB = _ray(*proj[1][j], Rs[1])
            X, dist = _ray_intersection(x0a, dA, x0b, dB)
            if X is None or dist > tol: continue
            ok = True
            for k in range(2, len(Rs)):
                scr = (X @ Rs[k])[:2]
                same = [t for t, sp in enumerate(species_per_view[k]) if sp == s0]
                if not same or np.linalg.norm(proj[k][same] - scr, axis=1).min() > tol:
                    ok = False; break
            if ok: cand.append((X, s0))
    kept = []
    for X, s in cand:
        if not any(sy == s and np.linalg.norm(X - Y) < tol for Y, sy in kept): kept.append((X, s))
    pts = np.array([k[0] for k in kept]) if kept else np.zeros((0, 3))
    rec = {"species": [k[1] for k in kept], "cart": pts, "n_recovered": len(kept),
           "n_true": len(conv), "count_match": len(kept) == len(conv)}
    sym = RC.recover_symmetry(rec, conv.lattice)
    return {"cs": sym["crystal_system"], "n_recovered": len(kept), "n_true": len(conv),
            "count_match": rec["count_match"], "over": len(kept) > len(conv),
            "calib_resid_max": round(max(calres), 4)}

def run(evjs, stjs, render_dir, tag):
    S = json.load(open(stjs)); rows = [json.loads(l) for l in open(evjs)]
    out = []; t0 = time.time()
    for idx, r in enumerate(rows):
        mid = r["material_id"]
        try:
            conv = conventional_cell(Structure.from_str(S[mid]["cif"], fmt="cif"))
            res = r2_one(conv, render_dir, r["images"])
            res.update({"material_id": mid, "truth": r["crystal_system"]})
            res["cs_ok"] = (res.get("cs") == r["crystal_system"])
            out.append(res)
        except Exception as e:
            out.append({"material_id": mid, "truth": r["crystal_system"],
                        "error": f"{type(e).__name__}: {str(e)[:90]}", "cs_ok": False})
        if idx % 40 == 39: print(f"  {tag}: {idx+1}/{len(rows)} {time.time()-t0:.0f}s", flush=True)
    return out

if __name__ == "__main__":
    RES = {}
    for tag, ev, stj, rd in (("original", "data/e3/eval.jsonl", "data/e3/structures.json", "data/e3/renders/eval"),
                             ("expansion", "data/e3x/eval.jsonl", "data/e3x/structures.json", "data/e3x/renders/eval")):
        print(f"=== {tag}", flush=True)
        RES[tag] = run(ev, stj, rd, tag)
        json.dump(RES, open("ledger/CP52_rung_R2_detector_oracle/r2_raw.json", "w"))
        k = sum(1 for x in RES[tag] if x.get("cs_ok")); e = sum(1 for x in RES[tag] if "error" in x)
        print(f"  {tag}: {k}/{len(RES[tag])} = {k/len(RES[tag]):.4f} | errors {e}", flush=True)
    print("R2 COMPLETE", flush=True)
