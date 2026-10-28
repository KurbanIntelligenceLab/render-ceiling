import numpy as np
from pymatgen.core import Lattice, Structure
from scipy.linalg import orth

from render_ceiling.atomic_reconstruction import predict, sparse_fit
from render_ceiling.reconstruct import projection_matrices
from render_ceiling.render import VIEW_ORDER, VIEWS_PERTURBED


def problem():
    s = Structure(
        Lattice.cubic(5), ["Si"] * 4, [[0, 0, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]]
    )
    c = projection_matrices(VIEW_ORDER, VIEWS_PERTURBED)
    z = orth(np.tile(np.eye(3), (4, 1)))
    return s, c, z


def test_physical_and_observation_errors_have_different_support():
    s, c, z = problem()
    rng = np.random.default_rng(419)
    noise = rng.normal(0, 0.001, (4, 5, 2))
    base = np.stack([s.cart_coords @ r[:, :2] for r in c], axis=1)
    delta = np.array([0.08, 0.04, 0.02])
    physical = base + noise
    physical[0] += np.stack([delta @ r[:, :2] for r in c])
    a = sparse_fit(physical, c, s.cart_coords, z, 0.001, 3, True)
    observed = base + noise
    observed[0, 2] += [0.10, 0.06]
    b = sparse_fit(observed, c, s.cart_coords, z, 0.001, 3, True)
    assert a["support"] == [0] and a["error_support"] == []
    assert b["support"] == [] and b["error_support"] == [[0, 2]]
    assert np.linalg.norm(a["delta"][0] - delta) < 0.004
    assert np.max(np.abs(b["cart"] - s.cart_coords)) < 0.004
    assert max(a["kkt_residual"], b["kkt_residual"]) < 1e-5


def test_free_origin_does_not_create_a_defect():
    s, c, z = problem()
    x = s.cart_coords + [0.17, 0.29, 0.31]
    y = np.stack([x @ r[:, :2] for r in c], axis=1)
    a = sparse_fit(y, c, s.cart_coords, z, 0.001, 3, True)
    assert a["support"] == a["error_support"] == []
    assert np.allclose(a["cart"], x, atol=1e-10)


def test_zero_noise_symmetry_and_permutation_independence():
    s, c, z = problem()
    obs = [{"xy": s.cart_coords @ r[:, :2], "species": np.asarray(s.atomic_numbers)} for r in c]
    a = predict(obs, c, s.lattice.matrix)
    assert all(v == "cubic" for v in a["predictions"].values())
    rng = np.random.default_rng(4)
    shuffled = []
    for o in obs:
        ix = rng.permutation(len(s))
        shuffled.append({k: v[ix] for k, v in o.items()})
    b = predict(shuffled, c, s.lattice.matrix)
    assert a["predictions"] == b["predictions"]
    for name in a["outputs"]:
        assert np.allclose(a["outputs"][name]["cart"], b["outputs"][name]["cart"])


def test_unconstrained_fit_agrees_with_ordinary_least_squares():
    s, c, z = problem()
    rng = np.random.default_rng(71)
    y = np.stack([s.cart_coords @ r[:, :2] for r in c], axis=1) + rng.normal(0, 0.003, (4, 5, 2))
    a = sparse_fit(y, c, s.cart_coords, np.eye(12), 0.003, 3, False)
    h = sum(r[:, :2] @ r[:, :2].T for r in c)
    expected = sum(y[:, i] @ r[:, :2].T for i, r in enumerate(c)) @ np.linalg.inv(h)
    assert a["support"] == []
    assert np.allclose(a["cart"], expected, atol=1e-10)
