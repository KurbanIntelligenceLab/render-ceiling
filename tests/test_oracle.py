"""The oracle must recover the symmetry it was given, from the frozen cameras alone.

These are the invariants the render ceiling rests on. If any of them breaks, the
ceiling is no longer a property of the images.
"""

from __future__ import annotations

import numpy as np
import pytest
from pymatgen.core import Lattice, Structure

from render_ceiling.reconstruct import (
    project,
    projection_matrices,
    reconstruct_positions,
    recover_symmetry,
)
from render_ceiling.render import VIEW_ORDER, VIEWS, conventional_cell


@pytest.fixture
def cubic() -> Structure:
    """Rock-salt NaCl: cubic, Fm-3m (225), unambiguous under any tolerance."""
    return Structure.from_spacegroup(
        "Fm-3m",
        Lattice.cubic(5.64),
        ["Na", "Cl"],
        [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]],
    )


@pytest.fixture
def tetragonal() -> Structure:
    """Rutile TiO2: tetragonal, P4_2/mnm (136). Distinguishes c from a and b."""
    return Structure.from_spacegroup(
        "P4_2/mnm",
        Lattice.tetragonal(4.594, 2.959),
        ["Ti", "O"],
        [[0.0, 0.0, 0.0], [0.305, 0.305, 0.0]],
    )


def test_view_set_is_frozen():
    """The camera set is a frozen constant of the protocol, not a parameter."""
    assert VIEW_ORDER == ["axis_a", "axis_b", "axis_c", "body_diagonal", "oblique2"]
    assert set(VIEWS) == set(VIEW_ORDER)


def test_projection_matrices_are_rotations():
    """Each camera is a rotation: orthonormal, determinant +1, so it loses no scale."""
    for matrix in projection_matrices(VIEW_ORDER):
        assert matrix.shape == (3, 3)
        np.testing.assert_allclose(matrix @ matrix.T, np.eye(3), atol=1e-10)
        assert np.isclose(np.linalg.det(matrix), 1.0, atol=1e-10)


def test_projection_discards_only_depth():
    """Projection keeps the two screen axes; the third column is depth."""
    matrix = projection_matrices(["axis_a"])[0]
    cart = np.array([[1.0, 2.0, 3.0], [-4.0, 0.5, 0.0]])
    screen = project(cart, matrix)
    assert screen.shape == (2, 2)
    np.testing.assert_allclose(screen, (cart @ matrix)[:, :2], atol=1e-12)


@pytest.mark.parametrize("structure_name", ["cubic", "tetragonal"])
def test_oracle_round_trips_under_perfect_extraction(structure_name, request):
    """With exact centroids and all five views, the oracle returns the true system.

    This is the render ceiling itself: invert the frozen cameras, re-solve
    cross-view correspondence, and the answer the images support comes back.
    """
    structure = request.getfixturevalue(structure_name)
    conv = conventional_cell(structure)
    expected = conv.get_space_group_info()[1]

    recon = reconstruct_positions(conv, VIEW_ORDER, centroid_noise=0.0)
    recovered = recover_symmetry(recon, conv.lattice)

    assert recovered["space_group_number"] == expected


def test_two_views_is_the_minimum(cubic):
    """Triangulation needs at least two rays; one view cannot place an atom."""
    conv = conventional_cell(cubic)
    recon = reconstruct_positions(conv, VIEW_ORDER[:2], centroid_noise=0.0)
    assert recon["n_recovered"] > 0


def test_reconstruction_is_deterministic(cubic):
    """No stage draws a random number at zero noise, so two runs agree exactly."""
    conv = conventional_cell(cubic)
    first = reconstruct_positions(conv, VIEW_ORDER, centroid_noise=0.0)
    second = reconstruct_positions(conv, VIEW_ORDER, centroid_noise=0.0)
    np.testing.assert_array_equal(first["cart"], second["cart"])
    assert first["species"] == second["species"]
    assert first["n_recovered"] == second["n_recovered"]


def test_view_map_actually_changes_the_cameras(cubic):
    """A perturbed camera set must measure its own ceiling, not the frozen one.

    Guards the defect this parameter was introduced to fix: view_map was once
    hardcoded, so a perturbed-camera condition silently reproduced the frozen
    result instead of measuring itself.
    """
    perturbed = dict(VIEWS)
    perturbed["axis_a"] = "10x,5y,0z"
    frozen_matrix = projection_matrices(["axis_a"])[0]
    perturbed_matrix = projection_matrices(["axis_a"], view_map=perturbed)[0]
    assert not np.allclose(frozen_matrix, perturbed_matrix)
