"""Public workflow validation and end-to-end CLI/API agreement."""

import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from render_ceiling import ReconstructionInput, Reconstructor

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/silicon_projections.json"


@pytest.mark.parametrize("method", ["atomic", "collective", "huber"])
def test_reconstruction_cli_matches_api(method, tmp_path):
    inputs = ReconstructionInput.from_json(EXAMPLE)
    expected = Reconstructor(method).run(inputs)
    destination = tmp_path / "nested" / "prediction.json"
    process = subprocess.run(
        [sys.executable, "-m", "render_ceiling.cli", "reconstruct", str(EXAMPLE),
         "--method", method, "--output", str(destination)],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert process.returncode == 0, process.stderr
    actual = json.loads(destination.read_text())
    assert actual == expected.to_dict()
    assert actual["prediction"]["label"] == "cubic"
    cart = np.asarray(actual["prediction"]["cart"])
    for view, camera in zip(inputs.observations, inputs.cameras):
        projected = cart @ camera[:, :2]
        distances = np.linalg.norm(projected[:, None] - view["xy"][None, :], axis=2)
        assert distances.min(axis=1).max() < 1e-6


@pytest.mark.parametrize("problem", ["missing", "invalid_json", "wrong_shape", "species", "singular", "nan"])
def test_bad_inputs_report_actionable_error(problem, tmp_path):
    path = tmp_path / "input.json"
    payload = json.loads(EXAMPLE.read_text())
    if problem == "invalid_json":
        path.write_text("{")
    elif problem != "missing":
        if problem == "wrong_shape":
            payload["cameras"] = []
        elif problem == "species":
            payload["observations"][0]["species"][0] = 8
        elif problem == "singular":
            payload["lattice"] = [[0] * 3] * 3
        elif problem == "nan":
            payload["observations"][0]["xy"][0][0] = float("nan")
        path.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "-m", "render_ceiling.cli", "reconstruct", str(path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "ERROR" in result.stderr and "Traceback" not in result.stderr
    assert not result.stdout


def test_stdout_is_json():
    result = subprocess.run(
        [sys.executable, "-m", "render_ceiling.cli", "reconstruct", str(EXAMPLE), "--method", "huber"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["method"] == "huber"
