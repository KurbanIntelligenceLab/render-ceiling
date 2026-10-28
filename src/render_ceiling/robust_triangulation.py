import numpy as np

from . import correspondence as OLD


def robust_triangulation(observations, cameras, lattice):
    rec = OLD.fit(observations, cameras)
    aligned, _ = OLD.assignments(rec["cart"], rec["species"], observations, cameras)
    y = np.stack(aligned, axis=1)
    a = np.concatenate([r[:, :2].T for r in cameras], axis=0)
    leverage = 1 - np.diag(a @ np.linalg.inv(a.T @ a) @ a.T)
    residual = y.reshape(len(y), -1) - rec["cart"] @ a.T
    normalized = residual / np.sqrt(np.maximum(leverage, 1e-8))
    sigma = max(float(np.median(np.abs(normalized)) / 0.6744897501960817), 0.001)
    x = rec["cart"].copy()
    for _ in range(80):
        norm = np.linalg.norm(y - np.stack([x @ r[:, :2] for r in cameras], axis=1), axis=2)
        weight = np.minimum(1.0, 4 * sigma / np.maximum(norm, 1e-30))
        h = np.stack(
            [sum(w * r[:, :2] @ r[:, :2].T for w, r in zip(weights, cameras)) for weights in weight]
        )
        rhs = np.stack(
            [
                sum(w * yy @ r[:, :2].T for w, yy, r in zip(weights, ys, cameras))
                for weights, ys in zip(weight, y)
            ]
        )
        new = np.linalg.solve(h, rhs[..., None])[..., 0]
        if np.max(np.abs(new - x)) < 1e-10:
            x = new
            break
        x = new
    uncertainty = np.sqrt(2 * sigma**2 * np.linalg.eigvalsh(np.linalg.inv(h)).max())
    predictions = {
        "huber_fixed_0.02": OLD.label(x, rec["species"], lattice, 0.02),
        "huber_adaptive_6": OLD.label(x, rec["species"], lattice, max(0.005, 6 * uncertainty)),
    }
    return {
        "cart": x,
        "species": rec["species"],
        "predictions": predictions,
        "estimated_sigma": sigma,
    }
