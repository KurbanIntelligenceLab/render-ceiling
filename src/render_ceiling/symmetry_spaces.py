import numpy as np
from scipy.linalg import null_space, orth
from scipy.optimize import linear_sum_assignment


def invariant_basis(cart, species, lattice, ds):

    n = len(cart)
    frac = cart @ np.linalg.inv(lattice)
    reynolds = np.zeros((3 * n, 3 * n))
    actions = []
    for rot, trans in zip(ds.rotations, ds.translations):
        transformed = frac @ rot.T + trans
        ids = np.zeros(n, dtype=int)
        for z in np.unique(species):
            ix = np.flatnonzero(species == z)
            delta = frac[ix][None] - transformed[ix, None]
            delta -= np.round(delta)
            a, b = linear_sum_assignment(np.sum((delta @ lattice) ** 2, axis=-1))
            ids[ix[a]] = ix[b]
        inverse_action = lattice.T @ np.linalg.inv(rot) @ np.linalg.inv(lattice.T)
        action = np.zeros_like(reynolds)
        for i, j in enumerate(ids):
            action[3 * i : 3 * i + 3, 3 * j : 3 * j + 3] = inverse_action
        reynolds += action / len(ds.rotations)
        actions.append(action)
    fixed = null_space(np.eye(3 * n) - reynolds, rcond=1e-8)
    if fixed.shape[1]:
        assert max(np.max(np.abs(a @ fixed - fixed)) for a in actions) < 1e-6
    translations = np.tile(np.eye(3), (n, 1)) / np.sqrt(n)
    return orth(np.column_stack([fixed, translations]), rcond=1e-8)


def weighted_projection(cart, reference, basis, h):

    n = len(cart)
    w = np.kron(np.eye(n), h)
    c = np.kron(np.eye(n), np.linalg.inv(h))
    p = basis @ np.linalg.solve(basis.T @ w @ basis, basis.T @ w)
    residual = (np.eye(3 * n) - p) @ (cart - reference).ravel()
    covariance = (np.eye(3 * n) - p) @ c @ (np.eye(3 * n) - p).T
    projected = cart - residual.reshape(n, 3)
    return projected, (covariance + covariance.T) / 2, p
