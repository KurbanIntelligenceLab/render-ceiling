"""
CoCr multi-view rendering pipeline.

Standardized ball-and-stick renders of a crystal structure for VLM input.
Per the experiment plan's "Rendering" section:
  - three principal-axis views (a, b, c) + one body-diagonal view
  - unit-cell edges drawn
  - consistent style, fixed pixel size (default 768)
  - NO label leakage: filenames, view ordering, camera parameters, and style
    carry no symmetry information beyond what the pixels show.

Implementation uses ASE's matplotlib-backed plot_atoms so rendering has no
non-Python dependency (POV-Ray/GLES-free). A supercell replication makes the
periodic packing legible; camera rotations are FIXED strings independent of the
structure's symmetry, so no label leaks through view choice.
"""
from __future__ import annotations

import os
from typing import Any

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ase import Atoms
from ase.visualize.plot import plot_atoms
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def conventional_cell(structure: Structure, symprec: float = 0.01) -> Structure:
    """Return the conventional standard cell so cell shape reflects crystal system
    (cubic renders as cubic, not the skewed primitive setting)."""
    return SpacegroupAnalyzer(structure, symprec=symprec).get_conventional_standard_structure()

# Fixed camera orientations, identical for every structure (no symmetry leak).
# ASE rotation strings: sequence of axis rotations in degrees.
VIEWS = {
    "axis_a": "0x,-90y,0z",   # looking down a
    "axis_b": "-90x,0y,0z",   # looking down b
    "axis_c": "0x,0y,0z",     # looking down c (default)
    "body_diagonal": "-60x,-30y,-15z",  # generic oblique / body-diagonal-ish
    "oblique2": "-30x,-60y,-45z",  # 2nd generic oblique (for the 5-view condition)
}
VIEW_ORDER = ["axis_a", "axis_b", "axis_c", "body_diagonal", "oblique2"]

# View subsets used by the E1 view-count sweep {1,3,5}. Ordered so 1 view = the
# c-axis (most information-dense single projection), 3 = the principal axes, 5 = all.
VIEW_SWEEP = {
    1: ["axis_c"],
    3: ["axis_a", "axis_b", "axis_c"],
    5: ["axis_a", "axis_b", "axis_c", "body_diagonal", "oblique2"],
}

# Contamination-control perturbation: camera rotations offset from the canonical set
# and a restyled palette/radii, applied to the SAME structures. If a model's accuracy
# drops sharply on these re-renders vs the canonical ones, that gap estimates
# memorization of web/pretraining images rather than genuine perception.
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
    atoms = atoms.repeat(supercell)
    return atoms


def _axis_colored_cell(ax, atoms, rot_string, lw=2.5):
    """Draw the unit-cell edges colored by crystallographic axis (a=red, b=green,
    c=blue), projected through the SAME ASE rotation as the atoms. Lets the viewer
    read edge lengths/parallelism directly instead of inferring from the silhouette.
    Adds short a/b/c axis labels at the far end of each origin edge.
    """
    import numpy as np
    from ase.utils import rotate
    R = rotate(rot_string)  # 3x3; screen = pos @ R, take [:, :2]
    cell = atoms.get_cell()[:]  # 3x3 rows = a,b,c
    corners = {(i, j, k): (i*cell[0] + j*cell[1] + k*cell[2])
               for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    colors = ["#d62728", "#2ca02c", "#1f77b4"]  # a, b, c
    # 12 edges, each labeled by the axis it runs along (0=a,1=b,2=c)
    edges = []
    for base in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]:
        for axis in range(3):
            nxt = list(base); nxt[axis] += 1
            if nxt[axis] <= 1:
                edges.append((base, tuple(nxt), axis))
    for a_corner, b_corner, axis in edges:
        p0 = corners[a_corner] @ R
        p1 = corners[b_corner] @ R
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=colors[axis], lw=lw,
                solid_capstyle="round", zorder=5)
    # axis labels at the end of the three origin edges
    for axis, name in enumerate("abc"):
        end = corners[tuple(1 if i == axis else 0 for i in range(3))] @ R
        ax.annotate(name, (end[0], end[1]), color=colors[axis], fontsize=13,
                    fontweight="bold", zorder=6, ha="center", va="center")


def render_legible(
    structure: Structure,
    out_dir: str,
    stem: str,
    px: int = 1024,
    radii: float = 0.4,
    view_names: list[str] | None = None,
    view_map: dict[str, str] | None = None,
) -> dict[str, str]:
    """Perceptually-legible render for symmetry reading (E1 render redesign).

    Single conventional cell (no supercell), small atoms, and cell edges colored by
    crystallographic axis with a/b/c labels — so crystal system is readable from the
    cell geometry directly, robust to camera orientation, rather than from a memorized
    axis-aligned silhouette. Filenames index-only (leakage guard).
    """
    os.makedirs(out_dir, exist_ok=True)
    views = view_names if view_names is not None else VIEW_ORDER
    vmap = view_map if view_map is not None else VIEWS
    atoms = _to_atoms(structure, (1, 1, 1))
    figsize = px / DPI
    paths: dict[str, str] = {}
    import numpy as np
    from ase.utils import rotate
    for idx, view in enumerate(views):
        rot = vmap[view]
        fig, ax = plt.subplots(figsize=(figsize, figsize), dpi=DPI)
        plot_atoms(atoms, ax, rotation=rot, radii=radii, show_unit_cell=0)
        _axis_colored_cell(ax, atoms, rot)
        ax.set_axis_off(); ax.set_xticks([]); ax.set_yticks([])
        ax.set_aspect("equal")
        # Frame to include BOTH atoms and the full cell box (plot_atoms limits to
        # atoms only, which clips the projected cell edges). Add a margin.
        R = rotate(rot)
        cell = atoms.get_cell()[:]
        corners = np.array([(i*cell[0] + j*cell[1] + k*cell[2]) @ R
                            for i in (0, 1) for j in (0, 1) for k in (0, 1)])
        pos = atoms.get_positions() @ R
        allpts = np.vstack([corners[:, :2], pos[:, :2]])
        lo = allpts.min(0); hi = allpts.max(0)
        span = (hi - lo).max(); cx, cy = (lo + hi) / 2
        half = span / 2 * 1.15  # 15% margin
        ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
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
    """Render a view set for one structure. Returns {view_name: filepath}.

    view_names: which views (default VIEW_ORDER). view_map: camera-string source
    (default VIEWS; pass VIEWS_PERTURBED for the contamination-control re-render).
    File naming: <stem>_view0.png .. — indices only, NO view name or symmetry hint in
    the filename (leakage guard). The index->view map is returned, not in the filename.
    """
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
