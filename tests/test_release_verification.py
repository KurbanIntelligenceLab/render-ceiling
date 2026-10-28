import json
from pathlib import Path

from render_ceiling.verify import verify


def release_root(tmp_path: Path) -> Path:
    for directory in ("src/render_ceiling", "data", "results", "release"):
        (tmp_path / directory).mkdir(parents=True)
    for document in ("README.md", "REPRODUCIBILITY.md", "results/README.md", "release/README.md"):
        (tmp_path / document).write_text("# Release\n")
    (tmp_path / "results/INDEX.json").write_text(
        json.dumps({"files": {"results/README.md": "bad"}})
    )
    return tmp_path


def test_corrupt_inventory_is_reported(tmp_path):
    root = release_root(tmp_path)
    (root / "results/INDEX.json").write_text("{")
    assert any("Invalid result inventory" in failure for failure in verify(root).failures)


def test_changed_result_and_invalid_prediction_are_reported(tmp_path):
    root = release_root(tmp_path)
    (root / "release/prediction.json").write_text("{")
    failures = verify(root).failures
    assert any("checksum mismatch" in failure for failure in failures)
    assert any("Invalid data record" in failure for failure in failures)


def test_missing_document_is_reported(tmp_path):
    root = release_root(tmp_path)
    (root / "README.md").unlink()
    assert any("Missing document: README.md" in failure for failure in verify(root).failures)


def test_result_without_paper_scope_is_rejected(tmp_path):
    root = release_root(tmp_path)
    assert any("paper/SI scope" in failure for failure in verify(root).failures)


def test_public_document_cannot_depend_on_private_archive(tmp_path):
    root = release_root(tmp_path)
    (root / "development").mkdir()
    (root / "development/private.md").write_text("Private notes")
    (root / "README.md").write_text("[Notes](development/private.md)")
    assert any("links to development" in failure for failure in verify(root).failures)
