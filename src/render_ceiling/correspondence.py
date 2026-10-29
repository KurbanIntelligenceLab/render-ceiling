from itertools import combinations

import numpy as np
import spglib
from scipy.optimize import linear_sum_assignment

from render_ceiling.labels import crystal_system_from_number

FIXED = (0.005, 0.01, 0.02, 0.05, 0.10)
PROPOSAL = (*FIXED, 0.20)


def canonical_observations(observations):
    result = []
    for o in observations:
        xy = np.asarray(o["xy"], dtype=float)
        species = np.asarray(o["species"], dtype=int)
        order = np.lexsort((xy[:, 1], xy[:, 0], species))
        result.append({"xy": xy[order], "species": species[order]})
    return result


def assignments(cart, species, observations, cameras):
    aligned, indices = [], []
    for o, r in zip(observations, cameras):
        pred = cart @ r[:, :2]
        target = np.zeros_like(pred)
        ids = np.zeros(len(cart), dtype=int)
        for z in np.unique(species):
            a = np.flatnonzero(species == z)
            b = np.flatnonzero(o["species"] == z)
            assert len(a) == len(b)
            cost = np.sum((pred[a, None] - o["xy"][b][None]) ** 2, axis=2)
            ix, iy = linear_sum_assignment(cost)
            target[a[ix]] = o["xy"][b[iy]]
            ids[a[ix]] = b[iy]
        aligned.append(target)
        indices.append(ids)
    return aligned, np.asarray(indices)


def fit(observations, cameras, seed_pair=None):

    observations = canonical_observations(observations)
    cameras = np.asarray(cameras)
    if seed_pair is None:
        starts = []
        for i, j in combinations(range(len(cameras)), 2):
            if np.linalg.cond(np.column_stack([cameras[i][:, 2], cameras[j][:, 2]])) < 1e6:
                starts.append(fit(observations, cameras, (i, j)))
        best = min(starts, key=lambda r: r["sse"])
        best["starts"] = len(starts)
        return best
    v0, v1 = seed_pair
    a, b = observations[v0], observations[v1]
    species = a["species"].copy()
    cart = np.zeros((len(species), 3))
    r0, r1 = cameras[v0], cameras[v1]
    d0, d1 = r0[:, 2], r1[:, 2]
    normal = np.array([[d0 @ d0, -d0 @ d1], [d0 @ d1, -d1 @ d1]])
    for z in np.unique(species):
        ia, ib = np.flatnonzero(species == z), np.flatnonzero(b["species"] == z)
        xa = a["xy"][ia] @ r0[:, :2].T
        xb = b["xy"][ib] @ r1[:, :2].T
        delta = xb[None] - xa[:, None]
        rhs = np.stack((delta @ d0, delta @ d1), axis=-1)
        ts = rhs @ np.linalg.inv(normal).T
        pa = xa[:, None] + ts[..., 0, None] * d0
        pb = xb[None] + ts[..., 1, None] * d1
        candidates = 0.5 * (pa + pb)
        cost = np.sum((pa - pb) ** 2, axis=2)
        for o, r in zip(observations, cameras):
            target = o["xy"][o["species"] == z]
            pred = candidates @ r[:, :2]
            cost += np.min(np.sum((pred[:, :, None] - target[None, None]) ** 2, axis=-1), axis=-1)
        ix, iy = linear_sum_assignment(cost)
        cart[ia[ix]] = candidates[ix, iy]
    h = sum(r[:, :2] @ r[:, :2].T for r in cameras)
    h_inv = np.linalg.inv(h)
    previous = None
    for iteration in range(12):
        aligned, ids = assignments(cart, species, observations, cameras)
        updated = sum(y @ r[:, :2].T for y, r in zip(aligned, cameras)) @ h_inv
        converged = previous is not None and np.array_equal(ids, previous)
        cart = updated
        if converged:
            break
        previous = ids
    aligned, _ = assignments(cart, species, observations, cameras)
    sse = float(sum(np.sum((cart @ r[:, :2] - y) ** 2) for y, r in zip(aligned, cameras)))
    variance = sse / (len(cart) * (2 * len(cameras) - 3))
    return {
        "cart": cart,
        "species": species,
        "variance": variance,
        "h": h,
        "h_inv": h_inv,
        "sse": sse,
        "iterations": iteration + 1,
    }


def dataset(cart, species, lattice, tolerance):
    if not len(cart):
        return None
    frac = cart @ np.linalg.inv(lattice)
    return spglib.get_symmetry_dataset(
        (lattice, frac % 1, species), symprec=tolerance, angle_tolerance=5
    )


def label(cart, species, lattice, tolerance):
    ds = dataset(cart, species, lattice, tolerance)
    return crystal_system_from_number(ds.number) if ds is not None else None


def project_symmetry(cart, species, lattice, ds):

    frac = cart @ np.linalg.inv(lattice)
    for _ in range(3):
        correction = np.zeros_like(frac)
        for rot, trans in zip(ds.rotations, ds.translations):
            transformed = frac @ rot.T + trans
            difference = np.zeros_like(frac)
            for z in np.unique(species):
                ix = np.flatnonzero(species == z)
                delta = frac[ix][None] - transformed[ix, None]
                delta -= np.round(delta)
                cost = np.sum((delta @ lattice) ** 2, axis=-1)
                a, b = linear_sum_assignment(cost)
                difference[ix[a]] = delta[a, b]
            correction += difference @ np.linalg.inv(rot).T
        correction /= len(ds.rotations)
        frac += correction
        if np.max(np.abs(correction)) < 1e-12:
            break
    projected = frac @ lattice

    projected += np.mean(cart - projected, axis=0)
    return projected
