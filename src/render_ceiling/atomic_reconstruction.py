import numpy as np
from scipy.linalg import orth

from . import correspondence as OLD
from . import symmetry_spaces as G

label = OLD.label
CONFIGS = {
    f"{mode}_{k}": (float(k), mode == "split") for mode in ["physical", "split"] for k in [2, 3, 4]
}
CONFIGS["observation_only"] = (None, True)


def candidate_spaces(recon, lattice):
    x, species = recon["cart"], recon["species"]
    n = len(x)
    result = {"triclinic": {"reference": x.copy(), "basis": np.eye(3 * n), "operations": 1}}
    seen = set()
    for tau in OLD.PROPOSAL:
        ds = OLD.dataset(x, species, lattice, tau)
        if ds is None:
            continue
        name = OLD.crystal_system_from_number(ds.number)
        key = (int(ds.number), len(ds.rotations))
        if name == "triclinic" or key in seen:
            continue
        seen.add(key)
        ref = OLD.project_symmetry(x, species, lattice, ds)
        if label(ref, species, lattice, 1e-4) != name:
            continue
        z = G.invariant_basis(x, species, lattice, ds)
        ref, _, _ = G.weighted_projection(x, ref, z, recon["h"])
        if label(ref, species, lattice, 1e-4) != name:
            continue
        item = {"reference": ref, "basis": z, "operations": len(ds.rotations)}
        if name not in result or item["operations"] > result[name]["operations"]:
            result[name] = item
    return result


def group_shrink(x, threshold):
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x * np.maximum(0.0, 1 - threshold / np.maximum(norm, 1e-30))


def initial_sparse_fit(y, cameras, reference, basis, sigma, k, split_error, maxiter=400):





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
        if change < 1e-7 * max(sigma, 1e-3):
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


def fitted_family(observations, cameras, lattice):
    recon = OLD.fit(observations, cameras)
    aligned, _ = OLD.assignments(recon["cart"], recon["species"], observations, cameras)
    y = np.stack(aligned, axis=1)
    sigma = float(np.sqrt(max(recon["variance"], 1e-6)))
    spaces = candidate_spaces(recon, lattice)
    fits = {}
    for name, space in spaces.items():
        for config, (k, split_error) in CONFIGS.items():
            f = sparse_fit(y, cameras, space["reference"], space["basis"], sigma, k, split_error)
            f["operations"] = space["operations"]
            fits[name, config] = f
    return recon, sigma, fits


def predict(observations, cameras, lattice):
    cameras, lattice = np.asarray(cameras), np.asarray(lattice)
    folds = []
    convergence = []
    for held in range(len(cameras)):
        use = [i for i in range(len(cameras)) if i != held]
        recon, sigma, fits = fitted_family([observations[i] for i in use], cameras[use], lattice)
        fold = {}
        for (name, config), fitted in fits.items():
            target, _ = OLD.assignments(
                fitted["cart"], recon["species"], [observations[held]], [cameras[held]]
            )
            residual = fitted["cart"] @ cameras[held][:, :2] - target[0]
            norms = np.linalg.norm(residual, axis=1)
            split_error = CONFIGS[config][1]

            loss = (
                np.where(norms <= 4 * sigma, 0.5 * norms**2, 4 * sigma * (norms - 2 * sigma))
                if split_error
                else 0.5 * norms**2
            )
            fold[f"{name}:{config}"] = {
                "loss": float(np.mean(loss)),
                "operations": fitted["operations"],
                "support_n": len(fitted["support"]),
                "error_n": len(fitted["error_support"]),
                "kkt_residual": fitted["kkt_residual"],
                "converged": fitted["converged"],
            }
            convergence.append(fitted["kkt_residual"])
        folds.append(fold)
    recon, sigma, full = fitted_family(observations, cameras, lattice)
    available = set.intersection(*(set(f) for f in folds)) & {f"{n}:{c}" for n, c in full}
    scores = {key: sum(f[key]["loss"] for f in folds) for key in available}
    outputs = {}
    for config in CONFIGS:
        valid = [key for key in scores if key.endswith(":" + config)]
        chosen = min(
            valid,
            key=lambda key: (
                round(scores[key], 14),
                -full[tuple(key.split(":"))]["operations"],
                key,
            ),
        )
        name, _ = chosen.split(":")
        fitted = full[name, config]
        outputs[config] = {
            "label": label(fitted["cart"], recon["species"], lattice, 1e-4),
            "parent_hypothesis": name,
            "score": scores[chosen],
            **{k: v for k, v in fitted.items() if k != "operations"},
            "species": recon["species"],
        }

    for mode in ["physical", "split"]:
        chosen = min(
            [f"{mode}_{k}" for k in [2, 3, 4]],
            key=lambda key: (round(outputs[key]["score"], 14), -CONFIGS[key][0]),
        )
        outputs[mode + "_cv"] = dict(outputs[chosen], selected_config=chosen)
    for f in full.values():
        convergence.append(f["kkt_residual"])
    return {
        "predictions": {name: o["label"] for name, o in outputs.items()},
        "outputs": outputs,
        "folds": folds,
        "max_kkt_residual": float(max(convergence)),
        "estimated_sigma": sigma,
    }


def sparse_fit(*args, **kwargs):
    """Use the frozen residual check and accurate fallback solver."""

    result = initial_sparse_fit(*args, **kwargs)
    if result["kkt_residual"] > 1e-5:
        from .support_refit import sparse_fit as accurate_fit

        result = accurate_fit(*args, **kwargs)
    assert result["kkt_residual"] <= 1e-5, result["kkt_residual"]
    return result
