"""Validated inputs and a common interface to the paper's reconstruction methods."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np


def _plain(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return value


@dataclass
class ReconstructionInput:
    """Five calibrated views of the same atoms, with coordinates in angstroms."""

    observations: list[dict]
    cameras: np.ndarray
    lattice: np.ndarray

    def __post_init__(self):
        self.cameras = np.asarray(self.cameras, dtype=float)
        self.lattice = np.asarray(self.lattice, dtype=float)
        if self.cameras.shape != (5, 3, 3) or not np.isfinite(self.cameras).all():
            raise ValueError("cameras must be a finite 5 by 3 by 3 array")
        if self.lattice.shape != (3, 3) or not np.isfinite(self.lattice).all():
            raise ValueError("lattice must be a finite 3 by 3 array")
        if np.linalg.matrix_rank(self.lattice) != 3:
            raise ValueError("lattice must be nonsingular")
        if not np.allclose(self.cameras.transpose(0, 2, 1) @ self.cameras, np.eye(3), atol=1e-6):
            raise ValueError("camera columns must be orthonormal")
        for held_out in range(5):
            remaining = np.delete(self.cameras, held_out, axis=0)
            if np.linalg.matrix_rank(np.concatenate([c[:, :2].T for c in remaining])) != 3:
                raise ValueError("each four-view training subset must span three dimensions")
        if not isinstance(self.observations, list) or len(self.observations) != 5:
            raise ValueError("observations must contain exactly five views")
        normalized = []
        expected = None
        for view in self.observations:
            if not isinstance(view, dict) or not {"xy", "species"} <= view.keys():
                raise ValueError("each observation requires xy and species")
            xy = np.asarray(view["xy"], dtype=float)
            species = np.asarray(view["species"], dtype=float)
            if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) == 0 or not np.isfinite(xy).all():
                raise ValueError("xy must be a nonempty finite N by 2 array")
            if species.shape != (len(xy),) or not np.isfinite(species).all():
                raise ValueError("species must contain one atomic number per centroid")
            if not np.all((species == np.floor(species)) & (species >= 1) & (species <= 118)):
                raise ValueError("species must be integer atomic numbers from 1 to 118")
            counts = sorted(species.tolist())
            if expected is not None and counts != expected:
                raise ValueError("every view must contain the same species counts")
            expected = counts
            normalized.append({"xy": xy.copy(), "species": species.astype(int)})
        self.observations = normalized

    @classmethod
    def from_json(cls, path: str | Path) -> "ReconstructionInput":
        payload = json.loads(Path(path).read_text())
        if not isinstance(payload, dict) or set(payload) != {"observations", "cameras", "lattice"}:
            raise ValueError("input requires exactly observations, cameras and lattice")
        return cls(**payload)


@dataclass
class ReconstructionResult:
    """Selected prediction plus the full candidate and selection records."""

    method: str
    selected_configuration: str
    prediction: dict
    diagnostics: dict

    def to_dict(self) -> dict:
        return _plain(vars(self))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, allow_nan=False) + "\n"


@dataclass
class Reconstructor:
    """Run a frozen paper method without changing its numerical settings."""

    method: str = "atomic"

    def __post_init__(self):
        if self.method not in ("atomic", "collective", "huber"):
            raise ValueError("method must be atomic, collective or huber")

    def run(self, inputs: ReconstructionInput) -> ReconstructionResult:
        args = inputs.observations, inputs.cameras, inputs.lattice
        if self.method == "atomic":
            from .atomic_reconstruction import predict
            from .penalty_selection import choose

            raw = predict(*args)
            selection = choose(raw)
            name = selection["selected"]["paired_1se"]
            prediction = raw["outputs"][name]
            diagnostics = {"reconstruction": raw, "selection": selection}
        elif self.method == "collective":
            from .collective_reconstruction import predict

            raw = predict(*args)
            name = "atom_or_mode_split"
            prediction = raw["outputs"][name]
            diagnostics = {"reconstruction": raw}
        else:
            from .robust_triangulation import robust_triangulation

            raw = robust_triangulation(*args)
            name = "huber_adaptive_6"
            prediction = {"cart": raw["cart"], "species": raw["species"], "label": raw["predictions"][name]}
            diagnostics = {"reconstruction": raw}
        return ReconstructionResult(self.method, name, prediction, diagnostics)
