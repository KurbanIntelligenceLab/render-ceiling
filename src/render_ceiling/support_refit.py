import numpy as np
from scipy.linalg import orth

from .atomic_reconstruction import group_shrink


def sparse_fit(y, cameras, reference, basis, sigma, k, split_error, maxiter=12000):





    n, v, _ = y.shape
    a = np.concatenate([r[:, :2].T for r in cameras], axis=0)
    h = a.T @ a
    vals, vecs = np.linalg.eigh(h)
    h_inv_half = (vecs / np.sqrt(vals)) @ vecs.T
    b = np.kron(np.eye(n), a)
    physical = np.kron(np.eye(n), a @ h_inv_half)
    az = b @ basis
    u = orth(az, rcond=1e-9)
    target = y.ravel() - b @ reference.ravel()

    def project(t):
        return t - u @ (u.T @ t)

    qp = project(physical)
    qt = project(target)
    d = np.zeros((n, 3))
    e = np.zeros((n, v, 2))
    zd, ze = d.copy(), e.copy()
    momentum = 1.0
    step = 0.5 if split_error and k is not None else 1.0
    lam_d = None if k is None else k * sigma
    lam_e = 4 * sigma
    converged = False
    for iteration in range(maxiter):
        residual = qp @ zd.ravel() + project(ze.ravel()) - qt
        nd = (
            np.zeros_like(d)
            if k is None
            else group_shrink(zd - step * (qp.T @ residual).reshape(n, 3), step * lam_d)
        )
        ne = (
            group_shrink(ze - step * residual.reshape(n, v, 2), step * lam_e)
            if split_error
            else np.zeros_like(e)
        )
        change = max(np.max(np.abs(nd - d)), np.max(np.abs(ne - e)))
        oldd, olde = d, e
        d, e = nd, ne
        current_residual = qp @ d.ravel() + project(e.ravel()) - qt
        test_d = (
            np.zeros_like(d)
            if k is None
            else group_shrink(d - step * (qp.T @ current_residual).reshape(n, 3), step * lam_d)
        )
        test_e = (
            group_shrink(e - step * current_residual.reshape(n, v, 2), step * lam_e)
            if split_error
            else np.zeros_like(e)
        )
        certificate = max(np.max(np.abs(test_d - d)), np.max(np.abs(test_e - e))) / max(sigma, 1e-3)
        if certificate < 1e-7:
            converged = True
            break
        next_momentum = (1 + np.sqrt(1 + 4 * momentum**2)) / 2
        zd = d + (momentum - 1) / next_momentum * (d - oldd)
        ze = e + (momentum - 1) / next_momentum * (e - olde)
        momentum = next_momentum

    residual = qp @ d.ravel() + project(e.ravel()) - qt
    pd = (
        np.zeros_like(d)
        if k is None
        else group_shrink(d - step * (qp.T @ residual).reshape(n, 3), step * lam_d)
    )
    pe = (
        group_shrink(e - step * residual.reshape(n, v, 2), step * lam_e)
        if split_error
        else np.zeros_like(e)
    )
    kkt = max(np.max(np.abs(pd - d)), np.max(np.abs(pe - e))) / max(sigma, 1e-3)
    selected = np.flatnonzero(np.linalg.norm(d, axis=1) > 1e-5 * max(sigma, 1e-3))
    errors = np.argwhere(np.linalg.norm(e, axis=2) > 1e-5 * max(sigma, 1e-3))
    physical_cols = (
        np.concatenate([np.arange(3 * i, 3 * i + 3) for i in selected])
        if len(selected)
        else np.array([], int)
    )
    error_cols = (
        np.concatenate([np.arange(2 * (i * v + j), 2 * (i * v + j) + 2) for i, j in errors])
        if len(errors)
        else np.array([], int)
    )
    design = np.column_stack([az, physical[:, physical_cols], np.eye(2 * n * v)[:, error_cols]])
    coef, _, rank, _ = np.linalg.lstsq(design, target, rcond=1e-9)
    q = basis.shape[1]
    base = reference + (basis @ coef[:q]).reshape(n, 3)
    du = np.zeros(3 * n)
    du[physical_cols] = coef[q : q + len(physical_cols)]
    delta = du.reshape(n, 3) @ h_inv_half
    ev = np.zeros(2 * n * v)
    ev[error_cols] = coef[q + len(physical_cols) :]
    cart = base + delta
    return {
        "cart": cart,
        "base": base,
        "delta": delta,
        "observation_errors": ev.reshape(n, v, 2),
        "support": selected.tolist(),
        "error_support": errors.tolist(),
        "rank": int(rank),
        "iterations": iteration + 1,
        "kkt_residual": float(kkt),
        "converged": converged or kkt < 1e-5,
        "sse": float(np.sum((y.ravel() - b @ cart.ravel() - ev) ** 2)),
    }
