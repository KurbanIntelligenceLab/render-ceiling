import numpy as np
from scipy.linalg import null_space, orth
from scipy.optimize import minimize

from render_ceiling.collective_reconstruction import fit_modes
from render_ceiling.reconstruct import projection_matrices
from render_ceiling.render import VIEW_ORDER, VIEWS_PERTURBED


def test_collective_objective_and_basis_invariance():
    rng = np.random.default_rng(387)
    n = 4
    cameras = projection_matrices(VIEW_ORDER, VIEWS_PERTURBED)
    v = len(cameras)
    z = np.tile(np.eye(3), (n, 1)) / np.sqrt(n)
    groups = [null_space(z.T)[:, :3]]
    ref = rng.normal(size=(n, 3))
    sigma = 0.01
    y = np.stack(
        [
            (ref + (groups[0] @ np.array([0.12, -0.08, 0.06])).reshape(n, 3)) @ r[:, :2]
            for r in cameras
        ],
        axis=1,
    )
    y += rng.normal(0, sigma, y.shape)
    y[1, 2] += [0.11, -0.03]
    split, huber = fit_modes(y, cameras, ref, z, groups, sigma, 3)
    a = np.concatenate([r[:, :2].T for r in cameras])
    b = np.kron(np.eye(n), a)
    az = b @ z
    u = orth(az)
    qg = b @ groups[0]
    qg -= u @ (u.T @ qg)
    vals, vecs = np.linalg.eigh(qg.T @ qg)
    g = groups[0] @ (vecs / np.sqrt(vals)) @ vecs.T
    design = np.column_stack([az, b @ g])
    target = y.ravel() - b @ ref.ravel()

    def objective(c):
        norm = np.linalg.norm((design @ c - target).reshape(n, v, 2), axis=2)
        return np.where(
            norm <= 4 * sigma, 0.5 * norm**2, 4 * sigma * (norm - 2 * sigma)
        ).sum() + 3 * sigma * np.linalg.norm(c[3:])

    opt = minimize(
        objective, np.ones(6) * 0.01, method="BFGS", options={"gtol": 1e-10, "maxiter": 2000}
    )
    np.testing.assert_allclose(opt.fun, split["penalized_objective"], atol=1e-9)
    rot = np.linalg.qr(rng.normal(size=(3, 3)))[0]
    again, h2 = fit_modes(y, cameras, ref, z, [groups[0] @ rot], sigma, 3)
    np.testing.assert_allclose(again["cart"], split["cart"], atol=1e-8)
    np.testing.assert_allclose(h2["cart"], huber["cart"], atol=1e-8)


def test_complete_pipeline_accepts_camera_matrix_list():
    from pymatgen.core import Lattice, Structure

    from render_ceiling.collective_reconstruction import predict

    structure = Structure(
        Lattice.cubic(5),
        ["Si"] * 4,
        [[0, 0, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
    )
    cameras = projection_matrices(VIEW_ORDER, VIEWS_PERTURBED)
    observations = [
        {
            "xy": structure.cart_coords @ camera[:, :2],
            "species": np.asarray(structure.atomic_numbers),
        }
        for camera in cameras
    ]
    result = predict(observations, cameras, structure.lattice.matrix)
    assert set(result["outputs"]) == {
        "atomic",
        "mode_split",
        "mode_huber",
        "atom_or_mode_split",
        "atom_or_mode_huber",
    }
    for output in result["outputs"].values():
        assert output["label"] == "cubic"
        assert np.isfinite(output["cart"]).all()
    assert result["max_kkt"] <= 1e-5
