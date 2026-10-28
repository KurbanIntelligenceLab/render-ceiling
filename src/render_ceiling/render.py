from __future__ import annotations

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ase import Atoms
from ase.visualize.plot import plot_atoms
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def conventional_cell(structure: Structure, symprec: float = 0.01) -> Structure:


    return SpacegroupAnalyzer(structure, symprec=symprec).get_conventional_standard_structure()




VIEWS = {
    "axis_a": "0x,-90y,0z",
    "axis_b": "-90x,0y,0z",
    "axis_c": "0x,0y,0z",
    "body_diagonal": "-60x,-30y,-15z",
    "oblique2": "-30x,-60y,-45z",
}
VIEW_ORDER = ["axis_a", "axis_b", "axis_c", "body_diagonal", "oblique2"]



VIEW_SWEEP = {
    1: ["axis_c"],
    3: ["axis_a", "axis_b", "axis_c"],
    5: ["axis_a", "axis_b", "axis_c", "body_diagonal", "oblique2"],
}





VIEWS_PERTURBED = {
    "axis_a": "12x,-78y,7z",
    "axis_b": "-78x,10y,-8z",
    "axis_c": "15x,12y,20z",
    "body_diagonal": "-48x,-42y,-3z",
    "oblique2": "-18x,-72y,-30z",
}

DEFAULT_PX = 768
DPI = 100


def _to_atoms(structure: Structure, supercell: tuple[int, int, int]) -> Atoms:
    atoms = AseAtomsAdaptor.get_atoms(structure)
    return atoms.repeat(supercell)


def _axis_colored_cell(ax, atoms, rot_string, lw=2.5):





    from ase.utils import rotate

    R = rotate(rot_string)
    cell = atoms.get_cell()[:]
    corners = {
        (i, j, k): (i * cell[0] + j * cell[1] + k * cell[2])
        for i in (0, 1)
        for j in (0, 1)
        for k in (0, 1)
    }
    colors = ["#d62728", "#2ca02c", "#1f77b4"]

    edges = []
    for base in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]:
        for axis in range(3):
            nxt = list(base)
            nxt[axis] += 1
            if nxt[axis] <= 1:
                edges.append((base, tuple(nxt), axis))
    for a_corner, b_corner, axis in edges:
        p0 = corners[a_corner] @ R
        p1 = corners[b_corner] @ R
        ax.plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            color=colors[axis],
            lw=lw,
            solid_capstyle="round",
            zorder=5,
        )

    for axis, name in enumerate("abc"):
        end = corners[tuple(1 if i == axis else 0 for i in range(3))] @ R
        ax.annotate(
            name,
            (end[0], end[1]),
            color=colors[axis],
            fontsize=13,
            fontweight="bold",
            zorder=6,
            ha="center",
            va="center",
        )


def render_legible(
    structure: Structure,
    out_dir: str,
    stem: str,
    px: int = 1024,
    radii: float = 0.4,
    view_names: list[str] | None = None,
    view_map: dict[str, str] | None = None,
) -> dict[str, str]:







    os.makedirs(out_dir, exist_ok=True)
    views = view_names if view_names is not None else VIEW_ORDER
    vmap = view_map if view_map is not None else VIEWS
    atoms = _to_atoms(structure, (1, 1, 1))
    figsize = px / DPI
    paths: dict[str, str] = {}
    from ase.utils import rotate

    for idx, view in enumerate(views):
        rot = vmap[view]
        fig, ax = plt.subplots(figsize=(figsize, figsize), dpi=DPI)
        plot_atoms(atoms, ax, rotation=rot, radii=radii, show_unit_cell=0)
        _axis_colored_cell(ax, atoms, rot)
        ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")


        R = rotate(rot)
        cell = atoms.get_cell()[:]
        corners = np.array(
            [
                (i * cell[0] + j * cell[1] + k * cell[2]) @ R
                for i in (0, 1)
                for j in (0, 1)
                for k in (0, 1)
            ]
        )
        pos = atoms.get_positions() @ R
        allpts = np.vstack([corners[:, :2], pos[:, :2]])
        lo = allpts.min(0)
        hi = allpts.max(0)
        span = (hi - lo).max()
        cx, cy = (lo + hi) / 2
        half = span / 2 * 1.15
        ax.set_xlim(cx - half, cx + half)
        ax.set_ylim(cy - half, cy + half)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        path = os.path.join(out_dir, f"{stem}_view{idx}.png")
        fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(fig)
        paths[view] = path
    return paths


def render_views(
    structure: Structure,
    out_dir: str,
    stem: str,
    px: int = DEFAULT_PX,
    supercell: tuple[int, int, int] = (1, 1, 1),
    radii: float = 0.5,
    view_names: list[str] | None = None,
    view_map: dict[str, str] | None = None,
) -> dict[str, str]:







    os.makedirs(out_dir, exist_ok=True)
    views = view_names if view_names is not None else VIEW_ORDER
    vmap = view_map if view_map is not None else VIEWS
    atoms = _to_atoms(structure, supercell)
    figsize = px / DPI
    paths: dict[str, str] = {}
    for idx, view in enumerate(views):
        rot = vmap[view]
        fig, ax = plt.subplots(figsize=(figsize, figsize), dpi=DPI)
        plot_atoms(atoms, ax, rotation=rot, radii=radii, show_unit_cell=2)
        ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        path = os.path.join(out_dir, f"{stem}_view{idx}.png")
        fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(fig)
        paths[view] = path
    return paths
