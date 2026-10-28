"""Local collective-displacement alternative; no truth enters inference."""

import numpy as np
from scipy.linalg import null_space, orth
from scipy.optimize import linear_sum_assignment

from . import atomic_reconstruction as M


class InvalidModeGeometry(ValueError):
    pass


def representation(cart, species, lattice, ds):
    """Forward action on Cartesian displacements, including cell translations."""
    n = len(cart)
    frac = cart @ np.linalg.inv(lattice)
    perms, actions = [], []
    for rot, trans in zip(ds.rotations, ds.translations):
        transformed = frac @ rot.T + trans
        ids = np.zeros(n, int)
        for z in np.unique(species):
            ix = np.flatnonzero(species == z)
            delta = frac[ix][None] - transformed[ix, None]
            delta -= np.round(delta)
            ii, jj = linear_sum_assignment(np.sum((delta @ lattice) ** 2, axis=-1))
            ids[ix[ii]] = ix[jj]
        r = lattice.T @ rot @ np.linalg.inv(lattice.T)
        action = np.zeros((3 * n, 3 * n))
        for i, j in enumerate(ids):
            action[3 * j : 3 * j + 3, 3 * i : 3 * i + 3] = r
        perms.append(ids)
        actions.append(action)
    return np.asarray(perms), np.asarray(actions)


def mode_groups(cart, species, lattice):
    """Real isotypic subspaces from simultaneous symmetric class sums.

    Whole equivalent-irrep copies are grouped together. No arbitrary individual
    basis vector is penalized. Complex conjugate components stay together.
    """
    ds = M.OLD.dataset(cart, species, lattice, 1e-4)
    assert ds is not None
    perms, acts = representation(cart, species, lattice, ds)
    n = len(cart)
    order = len(acts)
    eye = np.eye(3 * n)
    metric_error = float(np.max(np.abs(acts @ np.swapaxes(acts, 1, 2) - eye)))
    if metric_error >= 1e-6:
        raise InvalidModeGeometry(f"Non-isometric fixed-lattice action: {metric_error}")
    keys = {(tuple(r.ravel()), tuple(p)): i for i, (r, p) in enumerate(zip(ds.rotations, perms))}
    assert len(keys) == order
    mul = np.empty((order, order), int)
    for i in range(order):
        for j in range(order):
            mul[i, j] = keys[
                (tuple((ds.rotations[i] @ ds.rotations[j]).ravel()), tuple(perms[i][perms[j]]))
            ]
    identity = next(i for i, a in enumerate(acts) if np.max(np.abs(a - eye)) < 1e-6)
    inv = [int(np.flatnonzero(mul[i] == identity)[0]) for i in range(order)]
    classes = []
    seen = set()
    for h in range(order):
        if h in seen:
            continue
        group = sorted({int(mul[mul[g, h], inv[g]]) for g in range(order)})
        classes.append(group)
        seen.update(group)
    fixed = null_space(eye - acts.mean(axis=0), rcond=1e-8)
    translations = np.tile(np.eye(3), (n, 1)) / np.sqrt(n)
    nuisance = orth(np.column_stack([fixed, translations]), rcond=1e-8)
    complement = null_space(nuisance.T, rcond=1e-8)
    blocks = [complement] if complement.shape[1] else []
    for cls in classes:
        center = acts[cls].mean(axis=0)
        center = (center + center.T) / 2
        new = []
        for u in blocks:
            vals, vecs = np.linalg.eigh(u.T @ center @ u)
            breaks = [0, *list(np.flatnonzero(np.diff(vals) > 1e-6) + 1), len(vals)]
            new += [u @ vecs[:, a:b] for a, b in zip(breaks[:-1], breaks[1:])]
        blocks = new
    total = nuisance @ nuisance.T
    invariance = 0.0
    for u in blocks:
        total += u @ u.T
        invariance = max(
            invariance, max(float(np.max(np.abs(a @ u - u @ (u.T @ a @ u)))) for a in acts)
        )
    assert invariance < 1e-6
    assert np.max(np.abs(total - eye)) < 1e-6
    return blocks, {
        "order": order,
        "class_sizes": list(map(len, classes)),
        "ranks": [u.shape[1] for u in blocks],
        "nuisance_rank": nuisance.shape[1],
        "invariance_residual": invariance,
    }


def huber_refit(design, target, n, v, sigma):
    coef = np.linalg.lstsq(design, target, rcond=1e-9)[0]
    for it in range(2000):
        residual = (design @ coef - target).reshape(n, v, 2)
        weight = np.minimum(1.0, 4 * sigma / np.maximum(np.linalg.norm(residual, axis=2), 1e-30))
        w = np.repeat(np.sqrt(weight.ravel()), 2)
        new = np.linalg.lstsq(design * w[:, None], target * w, rcond=1e-9)[0]
        if np.max(np.abs(design @ (new - coef))) < 1e-10:
            coef = new
            break
        coef = new
    grad = design.T @ ((design @ coef - target) * np.repeat(weight.ravel(), 2))
    return coef, float(np.max(np.abs(grad)) / max(sigma, 0.001))


def fit_modes(y, cameras, reference, basis, groups, sigma, k):
    n, v, _ = y.shape
    a = np.concatenate([r[:, :2].T for r in cameras])
    b = np.kron(np.eye(n), a)
    az = b @ basis
    u = orth(az, rcond=1e-9)

    def project(t):
        return t - u @ (u.T @ t)

    target = y.ravel() - b @ reference.ravel()
    qt = project(target)
    gs = []
    slices = []
    weights = []
    end = 0
    for g in groups:
        qg = project(b @ g)
        vals, vecs = np.linalg.eigh(qg.T @ qg)
        assert vals.min() > 1e-9
        normalized = g @ (vecs / np.sqrt(vals)) @ vecs.T
        gs.append(normalized)
        slices.append(slice(end, end + g.shape[1]))
        end += g.shape[1]
        weights.append(np.sqrt(g.shape[1] / 3.0))
    physical = np.column_stack(gs) if gs else np.empty((3 * n, 0))
    qp = project(b @ physical)
    lip = max(1.0, float(np.linalg.norm(qp, 2) ** 2) + 1.0) if end else 1.0
    step = 1 / lip

    def shrink(d):
        z = d.copy()
        for sl, w in zip(slices, weights):
            z[sl] *= max(0.0, 1 - step * k * sigma * w / max(np.linalg.norm(d[sl]), 1e-30))
        return z

    d = np.zeros(end)
    e = np.zeros((n, v, 2))
    zd = d.copy()
    ze = e.copy()
    momentum = 1.0

    def prox(d, e):
        res = qp @ d + project(e.ravel()) - qt
        return shrink(d - step * qp.T @ res), M.group_shrink(
            e - step * res.reshape(n, v, 2), step * 4 * sigma
        )

    for it in range(12000):
        nd, ne = prox(zd, ze)
        od, oe = d, e
        d, e = nd, ne
        td, te = prox(d, e)
        cert = max(np.max(np.abs(td - d), initial=0), np.max(np.abs(te - e))) / max(sigma, 0.001)
        if cert < 1e-7:
            break
        nm = (1 + np.sqrt(1 + 4 * momentum**2)) / 2
        zd = d + (momentum - 1) / nm * (d - od)
        ze = e + (momentum - 1) / nm * (e - oe)
        momentum = nm
    assert cert <= 1e-5, cert
    active = [i for i, sl in enumerate(slices) if np.linalg.norm(d[sl]) > 1e-5 * max(sigma, 0.001)]
    errors = np.argwhere(np.linalg.norm(e, axis=2) > 1e-5 * max(sigma, 0.001))
    columns = (
        np.concatenate([np.arange(slices[i].start, slices[i].stop) for i in active]).astype(int)
        if active
        else np.array([], int)
    )
    ecol = (
        np.concatenate([np.arange(2 * (i * v + j), 2 * (i * v + j) + 2) for i, j in errors]).astype(
            int
        )
        if len(errors)
        else np.array([], int)
    )
    dphys = physical[:, columns]
    design = np.column_stack([az, b @ dphys])
    full = np.column_stack([design, np.eye(2 * n * v)[:, ecol]])
    coef = np.linalg.lstsq(full, target, rcond=1e-9)[0]
    hc, hgrad = huber_refit(design, target, n, v, sigma)
    assert hgrad < 1e-5, hgrad
    q = basis.shape[1]

    def output(c):
        base = reference + (basis @ c[:q]).reshape(n, 3)
        delta = (dphys @ c[q : q + len(columns)]).reshape(n, 3)
        return {
            "cart": base + delta,
            "base": base,
            "delta": delta,
            "support": active,
            "error_support": errors.tolist(),
            "kkt_residual": float(cert),
            "converged": True,
            "iterations": it + 1,
            "group_ranks": [g.shape[1] for g in groups],
            "selected_rank": len(columns),
            "huber_gradient": hgrad,
            "penalized_delta": (physical @ d).reshape(n, 3),
            "penalized_errors": e,
            "penalized_objective": float(
                0.5 * np.sum((qp @ d + project(e.ravel()) - qt) ** 2)
                + k * sigma * sum(w * np.linalg.norm(d[sl]) for sl, w in zip(slices, weights))
                + 4 * sigma * np.linalg.norm(e, axis=2).sum()
            ),
        }

    return output(coef), output(hc)


def fitted(obs, cameras, lattice):
    recon, sigma, fits = M.fitted_family(obs, cameras, lattice)
    recon["mode_exclusions"] = {}
    aligned, _ = M.OLD.assignments(recon["cart"], recon["species"], obs, cameras)
    y = np.stack(aligned, axis=1)
    spaces = M.candidate_spaces(recon, lattice)
    for parent, space in spaces.items():
        if space["basis"].shape[1] == 3 * len(y):
            groups, audit = (
                [],
                {"order": 1, "ranks": [], "nuisance_rank": 3 * len(y), "invariance_residual": 0.0},
            )
        else:
            try:
                groups, audit = mode_groups(space["reference"], recon["species"], lattice)
            except InvalidModeGeometry as exc:
                # A pseudo-symmetry accepted by the legacy atom method need not
                # define an orthogonal displacement representation of this lattice.
                recon["mode_exclusions"][parent] = str(exc)
                continue
        for k in [2, 3, 4]:
            f, h = fit_modes(y, cameras, space["reference"], space["basis"], groups, sigma, k)
            for kind, val in [("mode_split", f), ("mode_huber", h)]:
                fits[parent, f"{kind}_{k}"] = {
                    **val,
                    "operations": space["operations"],
                    "mode_audit": audit,
                }
    return recon, sigma, fits


def choose_family(outputs, folds, prefix):
    keys = [f"{prefix}_{k}" for k in [2, 3, 4]]
    losses = {k: np.array([f[outputs[k]["key"]]["loss"] for f in folds]) for k in keys}
    best = min(keys, key=lambda k: (round(float(losses[k].sum()), 14), -int(k[-1])))
    good = [
        k
        for k in keys
        if (losses[k] - losses[best]).mean()
        <= (losses[k] - losses[best]).std(ddof=1) / np.sqrt(len(folds)) + 1e-14
    ]
    return max(good, key=lambda k: int(k[-1]))


def predict(obs, cameras, lattice):
    cameras = np.asarray(cameras)
    folds = []
    maximum = 0.0
    exclusions = []
    for held in range(len(cameras)):
        use = [i for i in range(len(cameras)) if i != held]
        recon, sigma, fits = fitted([obs[i] for i in use], cameras[use], lattice)
        exclusions.append(recon["mode_exclusions"])
        fold = {}
        for (parent, config), f in fits.items():
            target, _ = M.OLD.assignments(f["cart"], recon["species"], [obs[held]], [cameras[held]])
            norms = np.linalg.norm(f["cart"] @ cameras[held][:, :2] - target[0], axis=1)
            loss = (
                0.5 * norms**2
                if config.startswith("physical_")
                else np.where(norms <= 4 * sigma, 0.5 * norms**2, 4 * sigma * (norms - 2 * sigma))
            )
            fold[parent + ":" + config] = {"loss": float(loss.mean())}
            maximum = max(maximum, f["kkt_residual"])
        folds.append(fold)
    recon, sigma, full = fitted(obs, cameras, lattice)
    exclusions.append(recon["mode_exclusions"])
    common = set.intersection(*(set(f) for f in folds)) & {":".join(k) for k in full}
    scores = {key: sum(f[key]["loss"] for f in folds) for key in common}
    outputs = {}
    for prefix in ["split", "mode_split", "mode_huber"]:
        for k in [2, 3, 4]:
            config = f"{prefix}_{k}"
            key = min(
                [t for t in common if t.endswith(":" + config)],
                key=lambda t: (round(scores[t], 14), -full[tuple(t.split(":"))]["operations"], t),
            )
            val = full[tuple(key.split(":"))]
            outputs[config] = {
                k: val[k] for k in ["cart", "support", "error_support", "kkt_residual"]
            }
            outputs[config].update(
                species=recon["species"],
                key=key,
                label=M.label(val["cart"], recon["species"], lattice, 1e-4),
            )
            if "mode_audit" in val:
                outputs[config].update(
                    mode_audit=val["mode_audit"], selected_rank=val["selected_rank"]
                )
    selected = {p: choose_family(outputs, folds, p) for p in ["split", "mode_split", "mode_huber"]}
    methods = {
        "atomic": outputs[selected["split"]],
        "mode_split": outputs[selected["mode_split"]],
        "mode_huber": outputs[selected["mode_huber"]],
    }
    for mode in ["split", "huber"]:
        atom = methods["atomic"]
        other = methods["mode_" + mode]
        delta = np.array([f[atom["key"]]["loss"] - f[other["key"]]["loss"] for f in folds])
        methods["atom_or_mode_" + mode] = (
            other if delta.mean() > delta.std(ddof=1) / np.sqrt(len(folds)) + 1e-14 else atom
        )
    maximum = max(maximum, max(f["kkt_residual"] for f in full.values()))
    return {
        "outputs": methods,
        "candidates": outputs,
        "folds": folds,
        "sigma": sigma,
        "max_kkt": maximum,
        "mode_exclusions": exclusions,
    }
