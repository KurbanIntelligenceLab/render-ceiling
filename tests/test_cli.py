import hashlib
import json
import subprocess
import sys

import pytest


def invoke(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "render_ceiling.cli", *args],
        cwd=cwd, text=True, capture_output=True, check=False,
    )


@pytest.mark.parametrize("args", [("--help",), ("verify", "--help"), ("reconstruct", "--help")])
def test_help(args):
    result = invoke(*args)
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert not result.stderr


@pytest.mark.parametrize("args", [(), ("unknown-command",)])
def test_invalid_command(args):
    result = invoke(*args)
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_missing_root_reports_failure(tmp_path):
    result = invoke("verify", "--root", str(tmp_path / "missing"))
    assert result.returncode == 1
    assert "Missing directory" in result.stdout
    assert "Traceback" not in result.stderr


def test_verification_from_another_directory(tmp_path):
    root = tmp_path / "checkout"
    for name in ("src/render_ceiling", "data", "results", "release"):
        (root / name).mkdir(parents=True)
    for name in ("README.md", "REPRODUCIBILITY.md", "results/README.md", "release/README.md"):
        (root / name).write_text("# Research records\n")
    record = root / "results/README.md"
    (root / "results/INDEX.json").write_text(json.dumps({
        "files": {"results/README.md": hashlib.sha256(record.read_bytes()).hexdigest()},
        "paper_scope": {"results/README.md": "Paper result map"},
    }))
    result = invoke("verify", "--root", str(root), cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FAILED 0" in result.stdout
    assert not result.stderr
