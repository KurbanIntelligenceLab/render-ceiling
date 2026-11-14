from __future__ import annotations

from typing import Any

import numpy as np
from ase.utils import rotate
from pymatgen.core import Lattice, Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from .labels import crystal_system_from_number
from .render import VIEWS


def projection_matrices(
    view_names: list[str], view_map: dict[str, str] | None = None
) -> list[np.ndarray]:






    vm = VIEWS if view_map is None else view_map
    return [rotate(vm[v]) for v in view_names]


def project(cart: np.ndarray, R: np.ndarray) -> np.ndarray:

    return (cart @ R)[:, :2]


def _ray(u: float, v: float, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:

    x0 = u * R[:, 0] + v * R[:, 1]
    d = R[:, 2] / np.linalg.norm(R[:, 2])
    return x0, d


def _ray_intersection(x0a, da, x0b, db) -> tuple[np.ndarray | None, float]:


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
    view_map: dict[str, str] | None = None,
) -> dict[str, Any]:





    cart_true = conv.cart_coords
    species = np.array([s.symbol for s in conv.species])
    Rs = projection_matrices(view_names, view_map)
    proj = [
        project(cart_true, R) for R in Rs
    ]


    if centroid_noise and centroid_noise > 0:
        rng = rng or np.random.default_rng(0)
        proj = [p + rng.normal(0.0, centroid_noise, size=p.shape) for p in proj]

    n = len(conv)

    v0, v1 = 0, 1
    R0, R1 = Rs[v0], Rs[v1]
    cand_pts = []
    cand_species = []
    for i in range(n):
        u0, w0 = proj[v0][i]
        s0 = species[i]
        x0a, da = _ray(u0, w0, R0)
        for j in range(n):
            if species[j] != s0:
                continue
            u1, w1 = proj[v1][j]
            x0b, db = _ray(u1, w1, R1)
            X, dist = _ray_intersection(x0a, da, x0b, db)
            if X is None or dist > tol:
                continue

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

    if recon["n_recovered"] == 0:
        return {
            "space_group_number": None,
            "point_group": None,
            "crystal_system": None,
            "ok": False,
            "reason": "no atoms recovered",
        }
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
        return {
            "space_group_number": None,
            "point_group": None,
            "crystal_system": None,
            "ok": False,
            "reason": f"{type(e).__name__}: {e}",
        }
