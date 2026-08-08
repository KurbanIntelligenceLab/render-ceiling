#!/usr/bin/env python
"""
CP19 — atom-centroid DETECTION from the frozen renders, with the mandatory quality gate.

This is the front end directive item 4 specified and CP17 did not build: pixels -> atom centroids.
CP0b's triangulator (cocr.reconstruct) already goes centroids -> 3D -> spglib, but it has only ever
been fed CIF-derived coordinates, so this closes the loop.

THE GATE RUNS FIRST AND IS NOT OPTIONAL. A low downstream symmetry score is uninterpretable unless
we know whether detection itself works. Ground-truth pixel positions come from ASE's own
PlottingVariables transform (see ledger/CP17_extractor/calibration.md — four naive projections gave
0-76% before this was right), so precision/recall are computed exactly and for free.

Detection: atoms are drawn as filled coloured discs with dark outlines on white. We segment on
saturation+darkness, label connected components, and split merged blobs by distance-transform peaks.
"""
import argparse, json, os, sys, collections
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import warnings; warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
from ase.io.utils import PlottingVariables
from pymatgen.core import Structure
from cocr.render import conventional_cell, VIEWS, VIEW_ORDER, _to_atoms


def ground_truth_pixels(structure, view, px=768, supercell=(2, 2, 2), radii=0.5):
    """Exact atom pixel centres + projected disc diameters + depth. See CP17/calibration.md.

    LETTERBOXING IS LOAD-BEARING: pv.w != pv.h in general, but the canvas is square and
    matplotlib uses equal aspect, so the LARGER span sets the pixel scale and the content is
    centred in the square box. Dividing x by pv.w and y by pv.h (the naive reading) puts
    centre-on-ink at 55.8% on a dense cell; the letterboxed form gives 100%.
    """
    at = _to_atoms(structure, supercell)
    n = len(at)
    pv = PlottingVariables(at, rotation=VIEWS[view], show_unit_cell=2, radii=radii, scale=1)
    P = pv.positions[:n]
    s = max(pv.w, pv.h)
    u = (P[:, 0] + (s - pv.w) / 2) / s * px
    v = px - (P[:, 1] + (s - pv.h) / 2) / s * px
    d_px = np.asarray(pv.d[:n]) / s * px
    return np.column_stack([u, v]), d_px, P[:, 2], at.get_chemical_symbols()


def detect(path, min_area=12):
    """Connected-component atom detection. Returns (centres Nx2, areas, mean_colours)."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    # atom discs: coloured OR mid-grey; exclude white background and the thin black wireframe
    mask = ((sat > 18) | ((lum < 245) & (lum > 60)))
    lab = _label(mask)
    out_c, out_a, out_col = [], [], []
    for lid in range(1, lab.max() + 1):
        ys, xs = np.nonzero(lab == lid)
        if len(xs) < min_area:
            continue
        for cy, cx, npx in _split_blob(ys, xs):
            out_c.append((cx, cy)); out_a.append(npx)
            out_col.append(a[int(cy), int(cx)].tolist())
    return np.array(out_c).reshape(-1, 2), np.array(out_a), out_col


def _label(mask):
    """4-connected labelling via iterative flood fill (no scipy dependency)."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    idx = np.argwhere(mask)
    seen = np.zeros((h, w), dtype=bool)
    for y0, x0 in idx:
        if seen[y0, x0]:
            continue
        cur += 1
        stack = [(y0, x0)]
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            lab[y, x] = cur
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
    return lab


def _split_blob(ys, xs, min_sub=12):
    """Split a merged blob into disc-sized pieces by grid subdivision on its extent."""
    npx = len(xs)
    h = ys.max() - ys.min() + 1
    w = xs.max() - xs.min() + 1
    # a single disc has area ~ pi/4 * min(h,w)^2; if the blob is far larger, subdivide
    d = min(h, w)
    single = np.pi / 4 * d * d
    k = max(1, int(round(npx / max(single, 1))))
    if k <= 1 or npx < 2 * min_sub:
        return [(ys.mean(), xs.mean(), npx)]
    # k-means-lite: seed on a grid over the blob's bounding box, one Lloyd pass
    nx = int(np.ceil(np.sqrt(k * w / max(h, 1)))) or 1
    ny = int(np.ceil(k / nx)) or 1
    seeds = [(ys.min() + (i + .5) * h / ny, xs.min() + (j + .5) * w / nx)
             for i in range(ny) for j in range(nx)]
    pts = np.column_stack([ys, xs]).astype(float)
    S = np.array(seeds)
    for _ in range(3):
        dist = ((pts[:, None, :] - S[None, :, :]) ** 2).sum(-1)
        who = dist.argmin(1)
        for s in range(len(S)):
            m = who == s
            if m.sum():
                S[s] = pts[m].mean(0)
    res = []
    for s in range(len(S)):
        m = who == s
        if m.sum() >= min_sub:
            res.append((pts[m][:, 0].mean(), pts[m][:, 1].mean(), int(m.sum())))
    return res or [(ys.mean(), xs.mean(), npx)]


def match(det, gt, gt_d):
    """Greedy nearest matching within half a disc radius. Returns TP, FP, FN, errors."""
    if len(det) == 0:
        return 0, 0, len(gt), []
    used = set()
    tp, errs = 0, []
    for i, g in enumerate(gt):
        tol = max(3.0, gt_d[i] * 0.5)
        best, bd = None, 1e9
        for j, dpt in enumerate(det):
            if j in used:
                continue
            dd = float(np.hypot(dpt[0] - g[0], dpt[1] - g[1]))
            if dd < bd:
                best, bd = j, dd
        if best is not None and bd <= tol:
            used.add(best); tp += 1; errs.append(bd)
    return tp, len(det) - tp, len(gt) - tp, errs


def overlap_covariate(gt, gt_d, depth):
    """Fraction of atoms whose centre is covered by a NEARER atom's disc (difficulty covariate)."""
    n = len(gt)
    if n == 0:
        return 0.0
    hidden = 0
    for i in range(n):
        for j in range(n):
            if i == j or depth[j] <= depth[i]:
                continue
            if np.hypot(gt[j][0] - gt[i][0], gt[j][1] - gt[i][1]) < gt_d[j] * 0.5:
                hidden += 1
                break
    return hidden / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-jsonl", required=True)
    ap.add_argument("--structures", required=True)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--prefix", default="MP_")
    ap.add_argument("--views", default="axis_a,axis_b,axis_c")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.eval_jsonl)]
    if args.limit:
        rows = rows[: args.limit]
    store = json.load(open(args.structures))
    views = args.views.split(",")
    recs = []
    for i, r in enumerate(rows):
        mid = r["material_id"]
        try:
            conv = conventional_cell(Structure.from_str(store[mid]["cif"], fmt="cif"))
        except Exception:
            continue
        per_view = {}
        for v in views:
            vi = VIEW_ORDER.index(v)
            p = os.path.join(args.renders, f"{args.prefix}{mid}_view{vi}.png")
            if not os.path.exists(p):
                continue
            gt, gd, dep, _ = ground_truth_pixels(conv, v)
            det, areas, _ = detect(p)
            tp, fp, fn, errs = match(det, gt, gd)
            per_view[v] = {
                "n_gt": int(len(gt)), "n_det": int(len(det)),
                "tp": tp, "fp": fp, "fn": fn,
                "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1),
                "median_centroid_err_px": float(np.median(errs)) if errs else None,
                "overlap_covariate": overlap_covariate(gt, gd, dep),
            }
        if per_view:
            recs.append({"material_id": mid, "truth": r["crystal_system"], "views": per_view})
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(rows)}", flush=True)

    P = [w["precision"] for r in recs for w in r["views"].values()]
    R = [w["recall"] for r in recs for w in r["views"].values()]
    E = [w["median_centroid_err_px"] for r in recs for w in r["views"].values()
         if w["median_centroid_err_px"] is not None]
    summary = {
        "n_structures": len(recs), "n_view_measurements": len(P),
        "precision": {"median": float(np.median(P)), "mean": float(np.mean(P))},
        "recall": {"median": float(np.median(R)), "mean": float(np.mean(R))},
        "centroid_err_px": {"median": float(np.median(E)) if E else None},
        "overlap_covariate": {"median": float(np.median(
            [w["overlap_covariate"] for r in recs for w in r["views"].values()]))},
    }
    json.dump({"summary": summary, "records": recs}, open(args.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
