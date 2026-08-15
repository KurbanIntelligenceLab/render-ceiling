#!/usr/bin/env python
"""
extractor — DETERMINISTIC cell-geometry extractor from the frozen renders.

Not a learned model and NOT a proposed method: an instrument for localising the gap between the
identifiability oracle (0.9321 under ideal atom extraction) and the ~0.50 pixel models reach on the
box-ambiguous stratum (box_sufficiency).

The three axis views are ORTHOGRAPHIC projections down a, b, c (VIEWS in src/cocr/render.py),
drawn by ASE with show_unit_cell=2, so cell edges appear as straight dark segments whose 2D
lengths and mutual angles are affine images of the true cell metric.

Pipeline per structure:
  1. isolate the wireframe by darkness threshold (cell lines are drawn darker than atom spheres)
  2. Hough-transform line segments, cluster by orientation
  3. from each axis view recover the two in-plane edge lengths and their included angle
  4. assemble (a,b,c,alpha,beta,gamma) and classify with the SAME tolerance rule as box_sufficiency

Denominators are FIXED: a structure whose line detection fails is scored WRONG, never dropped.
"""
import argparse, json, os, collections
import numpy as np
from PIL import Image

# view index -> which cell axes lie in the image plane (VIEW_ORDER = a,b,c,body_diag,oblique2)
AXIS_VIEWS = {0: ("b", "c"), 1: ("a", "c"), 2: ("a", "b")}


def wireframe_mask(path, dark_thresh=110):
    """Cell lines are drawn darker than atom spheres and background. Returns a bool mask."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    # dark AND low-saturation => black wireframe, not a coloured sphere edge
    return (lum < dark_thresh) & (sat < 40)


def hough_segments(mask, n_theta=180, top_k=12, min_votes=40):
    """Minimal Hough line transform. Returns [(theta, rho, votes)] for the strongest lines."""
    ys, xs = np.nonzero(mask)
    if len(xs) < min_votes:
        return []
    h, w = mask.shape
    cx, cy = w / 2.0, h / 2.0
    x = xs - cx
    y = ys - cy
    thetas = np.linspace(-np.pi / 2, np.pi / 2, n_theta, endpoint=False)
    diag = int(np.hypot(h, w) / 2) + 1
    acc = np.zeros((n_theta, 2 * diag + 1), dtype=np.int32)
    for i, t in enumerate(thetas):
        r = np.round(x * np.cos(t) + y * np.sin(t)).astype(int) + diag
        np.add.at(acc[i], np.clip(r, 0, 2 * diag), 1)
    out = []
    flat = acc.ravel()
    for idx in np.argsort(flat)[::-1][: top_k * 6]:
        i, j = divmod(int(idx), acc.shape[1])
        v = int(flat[idx])
        if v < min_votes:
            break
        t, rho = float(thetas[i]), float(j - diag)
        # suppress near-duplicates
        if any(abs(t - t2) < 0.09 and abs(rho - r2) < 14 for t2, r2, _ in out):
            continue
        out.append((t, rho, v))
        if len(out) >= top_k:
            break
    return out


def two_directions(segs, min_sep=0.17):
    """Pick the two dominant, well-separated orientations (the projected cell edge directions)."""
    if len(segs) < 2:
        return None
    byw = sorted(segs, key=lambda s: -s[2])
    d1 = byw[0]
    for s in byw[1:]:
        d = abs(s[0] - d1[0])
        d = min(d, np.pi - d)
        if d > min_sep:
            return d1, s
    return None


def view_geometry(path):
    """Recover (len1, len2, included_angle_deg) for one axis view, or None on failure."""
    m = wireframe_mask(path)
    segs = hough_segments(m)
    dirs = two_directions(segs)
    if dirs is None:
        return None
    (t1, r1, _), (t2, r2, _) = dirs
    ang = abs(t1 - t2) * 180 / np.pi
    if ang > 90:
        ang = 180 - ang
    # projected edge extents: spread of wireframe pixels along each direction's normal
    ys, xs = np.nonzero(m)
    h, w = m.shape
    x = xs - w / 2.0
    y = ys - h / 2.0
    ext = []
    for t in (t1, t2):
        # extent ALONG the line direction (unit vector (-sin t, cos t) is along the line)
        proj = -x * np.sin(t) + y * np.cos(t)
        ext.append(float(np.percentile(proj, 97) - np.percentile(proj, 3)))
    return ext[0], ext[1], float(ang)


def classify(metric, tol_len=0.02, tol_ang=1.0):
    """Same rule as box_sufficiency, so the two checkpoints are commensurable."""
    a, b, c, al, be, ga = metric
    eq = lambda p, q: abs(p - q) / max(p, q) < tol_len
    n90 = lambda v: abs(v - 90) < tol_ang
    A = [al, be, ga]
    if eq(a, b) and eq(b, c) and all(n90(v) for v in A):
        return "cubic"
    if eq(a, b) and n90(al) and n90(be) and abs(ga - 120) < tol_ang:
        return "hexagonal_or_trigonal"
    if eq(a, b) and all(n90(v) for v in A):
        return "tetragonal"
    if all(n90(v) for v in A):
        return "orthorhombic"
    if sum(n90(v) for v in A) == 2:
        return "monoclinic"
    if eq(a, b) and eq(b, c) and eq(al, be) and eq(be, ga):
        return "trigonal_rhombohedral"
    return "triclinic"


def extract(mid, render_dir, prefix="MP_"):
    """Assemble a cell metric from the three axis views. Returns (metric, per_view) or (None, pv)."""
    per_view = {}
    for vi, (ax1, ax2) in AXIS_VIEWS.items():
        p = os.path.join(render_dir, f"{prefix}{mid}_view{vi}.png")
        if not os.path.exists(p):
            per_view[vi] = None
            continue
        per_view[vi] = view_geometry(p)
    if any(per_view.get(v) is None for v in AXIS_VIEWS):
        return None, per_view
    # view0 (down a) sees b,c ; view1 (down b) sees a,c ; view2 (down c) sees a,b
    b0, c0, alpha = per_view[0]
    a1, c1, beta = per_view[1]
    a2, b2, gamma = per_view[2]
    a = (a1 + a2) / 2
    b = (b0 + b2) / 2
    c = (c0 + c1) / 2
    return (a, b, c, alpha, beta, gamma), per_view


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-jsonl", required=True)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--structures", required=True, help="for the VALIDATION GATE (true cells)")
    ap.add_argument("--strata", default=None, help="box_sufficiency results.json, to report per-stratum")
    ap.add_argument("--prefix", default="MP_")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.eval_jsonl)]
    recs = []
    for i, r in enumerate(rows):
        mid = r["material_id"]
        metric, pv = extract(mid, args.renders, args.prefix)
        recs.append({"material_id": mid, "truth": r["crystal_system"],
                     "metric": metric, "detected": metric is not None,
                     "pred": classify(metric) if metric else None})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(rows)} detected={sum(x['detected'] for x in recs)}", flush=True)
    json.dump({"n": len(recs), "records": recs}, open(args.out, "w"), indent=1)
    det = sum(x["detected"] for x in recs)
    print(f"EXTRACTION: {det}/{len(recs)} = {det/len(recs):.4f} line-detection rate")


if __name__ == "__main__":
    main()
