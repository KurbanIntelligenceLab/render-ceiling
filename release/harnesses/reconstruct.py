"""
CoCr E0.5 tool-oracle: reconstruct 3D structure from the multi-view projections
and measure how much crystallographic symmetry is recoverable from the finite view
set alone.

Identifiability question (per the plan): screw axes, glide planes, and translational
symmetry are exactly what static orthographic projections obscure. This oracle tests,
programmatically, whether space group (and the coarser levels) can be recovered from
the rendered view set.

FAITHFULNESS PRINCIPLE — the oracle must not be circular:
  * The renderer (render.py) projects Cartesian positions orthographically:
    screen = pos @ R, taking columns (0,1) as (x,y); column 2 (depth) is DROPPED.
    We replicate that projection exactly (analytic, from the same ASE rotation
    matrices) — this is the idealized "perfect extraction" of atom centroids +
    element colors from a render.
  * Crucially, the reconstructor is NOT given the atom<->atom correspondence across
    views. It must re-solve which projected point in view B is the same atom as a
    point in view A, using ONLY element identity (visible as color) and ray
    geometry. This is what a real observer must do, and it is exactly where
    projection overlap (the screw-axis / glide blind spot) causes failures.
  * The lattice is taken as known (the unit-cell edges are drawn in every render).

Given N view rotations, an atom at world point x observed at screen (u,v) constrains
x to a back-projection ray: x0 = u*R[:,0] + v*R[:,1], direction d = R[:,2]. Two rays
that meet (within tol) triangulate a candidate 3D atom; the candidate is accepted
only if it also projects onto an observed point of the same element in every other
view. Fewer views -> weaker verification -> more spurious/missing atoms -> lower
symmetry recovery, which is the view-count dependence the sweep measures.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
from ase.utils import rotate
from pymatgen.core import Structure, Lattice
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from .render import VIEWS, VIEW_ORDER, conventional_cell
from .labels import crystal_system_from_number


def projection_matrices(view_names: list[str]) -> list[np.ndarray]:
    """3x3 ASE rotation matrix per view (screen = pos @ R; cols 0,1 = x,y; col 2 = depth)."""
    return [rotate(VIEWS[v]) for v in view_names]


def project(cart: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Orthographic screen coords (n,2) exactly as render.py's plot_atoms projects."""
    return (cart @ R)[:, :2]


def _ray(u: float, v: float, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Back-projection ray for a screen point (u,v) under rotation R: (origin, unit dir)."""
    x0 = u * R[:, 0] + v * R[:, 1]
    d = R[:, 2] / np.linalg.norm(R[:, 2])
    return x0, d


def _ray_intersection(x0a, da, x0b, db) -> tuple[np.ndarray, float]:
    """Closest-approach midpoint of two rays and their minimum distance."""
    # Solve for parameters minimizing |(x0a+ta*da) - (x0b+tb*db)|.
    A = np.array([[da @ da, -da @ db], [da @ db, -db @ db]])
    rhs = np.array([(x0b - x0a) @ da, (x0b - x0a) @ db])
    try:
        ta, tb = np.linalg.solve(A, rhs)
    except np.linalg.LinAlgError:
        return None, np.inf
    pa = x0a + ta * da
    pb = x0b + tb * db
    return 0.5 * (pa + pb), float(np.linalg.norm(pa - pb))


def reconstruct_positions(
    conv: Structure,
    view_names: list[str],
    tol: float = 0.15,
    centroid_noise: float = 0.0,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Reconstruct 3D atom positions from the view set WITHOUT known correspondence.

    Returns {species, cart, n_recovered, n_true, faithful_rmsd, ...}. tol is the
    world-space (Angstrom) tolerance for ray intersection and cross-view verification.
    """
    cart_true = conv.cart_coords
    species = np.array([s.symbol for s in conv.species])
    Rs = projection_matrices(view_names)
    proj = [project(cart_true, R) for R in Rs]  # per-view (n,2), same index order (we forget it below)
    # centroid_noise: Gaussian jitter (Angstrom) on projected points, a proxy for
    # finite render resolution / centroid-localization error at 768px.
    if centroid_noise and centroid_noise > 0:
        rng = rng or np.random.default_rng(0)
        proj = [p + rng.normal(0.0, centroid_noise, size=p.shape) for p in proj]

    n = len(conv)
    # Anchor on the first two views; generate candidates by species-matched ray intersection.
    v0, v1 = 0, 1
    R0, R1 = Rs[v0], Rs[v1]
    cand_pts = []
    cand_species = []
    for i in range(n):  # points in view 0 (index forgotten as identity; only (species,uv) used)
        u0, w0 = proj[v0][i]
        s0 = species[i]
        x0a, da = _ray(u0, w0, R0)
        for j in range(n):  # points in view 1
            if species[j] != s0:
                continue
            u1, w1 = proj[v1][j]
            x0b, db = _ray(u1, w1, R1)
            X, dist = _ray_intersection(x0a, da, x0b, db)
            if X is None or dist > tol:
                continue
            # verify against remaining views: must hit an observed same-species point
            ok = True
            for vk in range(len(Rs)):
                if vk in (v0, v1):
                    continue
                scr = (X @ Rs[vk])[:2]
                same = np.where(species == s0)[0]
                d2 = np.linalg.norm(proj[vk][same] - scr, axis=1)
                if len(d2) == 0 or d2.min() > tol:
                    ok = False
                    break
            if ok:
                cand_pts.append(X)
                cand_species.append(s0)
    cand_pts = np.array(cand_pts) if cand_pts else np.zeros((0, 3))

    # dedup candidates within tol (overlapping rays produce duplicates)
    kept_pts = []
    kept_species = []
    for X, s in zip(cand_pts, cand_species):
        dup = False
        for Y, sy in zip(kept_pts, kept_species):
            if sy == s and np.linalg.norm(X - Y) < tol:
                dup = True
                break
        if not dup:
            kept_pts.append(X)
            kept_species.append(s)
    kept_pts = np.array(kept_pts) if kept_pts else np.zeros((0, 3))

    # faithfulness: match each recovered point to nearest true point of same species
    rmsds = []
    for X, s in zip(kept_pts, kept_species):
        mask = species == s
        if mask.any():
            d = np.linalg.norm(cart_true[mask] - X, axis=1)
            rmsds.append(d.min())
    faithful_rmsd = float(np.sqrt(np.mean(np.square(rmsds)))) if rmsds else None

    return {
        "species": kept_species,
        "cart": kept_pts,
        "n_recovered": len(kept_pts),
        "n_true": n,
        "faithful_rmsd": faithful_rmsd,
        "count_match": len(kept_pts) == n,
    }


def recover_symmetry(
    recon: dict[str, Any],
    lattice: Lattice,
    symprec: float = 0.01,
    angle_tol: float = 5.0,
) -> dict[str, Any]:
    """Run spglib on the reconstructed atoms (lattice known from drawn cell edges)."""
    if recon["n_recovered"] == 0:
        return {"space_group_number": None, "point_group": None, "crystal_system": None,
                "ok": False, "reason": "no atoms recovered"}
    frac = lattice.get_fractional_coords(recon["cart"]) % 1.0
    try:
        st = Structure(lattice, recon["species"], frac, coords_are_cartesian=False)
        sga = SpacegroupAnalyzer(st, symprec=symprec, angle_tolerance=angle_tol)
        sgn = sga.get_space_group_number()
        return {
            "space_group_number": sgn,
            "point_group": sga.get_point_group_symbol(),
            "crystal_system": crystal_system_from_number(sgn),
            "ok": True,
        }
    except Exception as e:
        return {"space_group_number": None, "point_group": None, "crystal_system": None,
                "ok": False, "reason": f"{type(e).__name__}: {e}"}
