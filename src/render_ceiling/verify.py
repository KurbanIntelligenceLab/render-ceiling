from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


class Report:


    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passed = 0

    def check(self, condition: bool, message: str) -> None:
        if condition:
            self.passed += 1
        else:
            self.failures.append(message)


def verify(root: Path) -> Report:
    report = Report()
    for name in ("src/render_ceiling", "data", "results", "release"):
        report.check((root / name).is_dir(), f"Missing directory: {name}")
    index = root / "results/INDEX.json"
    if not index.exists():
        report.check(False, "Missing results/INDEX.json")
        return report
    try:
        manifest = json.loads(index.read_text())
        inventory = manifest["files"]
        if not isinstance(inventory, dict):
            raise ValueError("files must be a mapping")
    except (ValueError, KeyError, TypeError) as exc:
        report.check(False, f"Invalid result inventory: {exc}")
        return report
    actual = {
        str(p.relative_to(root)): p
        for p in (root / "results").rglob("*")
        if p.is_file() and p != index and p.name != ".DS_Store"
    }
    report.check(set(actual) == set(inventory), "Result inventory differs from files on disk")
    paper_scope = manifest.get("paper_scope", {})
    report.check(
        isinstance(paper_scope, dict)
        and set(paper_scope) == set(actual)
        and all(isinstance(value, str) and value.strip() for value in paper_scope.values()),
        "Every result file must have an explicit paper/SI scope entry",
    )
    for name, path in actual.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        report.check(digest == inventory.get(name), f"Result checksum mismatch: {name}")
        if path.suffix == ".json":
            try:
                json.loads(path.read_text())
                report.check(True, name)
            except (ValueError, UnicodeError) as exc:
                report.check(False, f"Invalid JSON: {name}: {exc}")
        elif path.suffix == ".jsonl":
            try:
                for line in path.read_text().splitlines():
                    if line.strip():
                        json.loads(line)
                report.check(True, name)
            except (ValueError, UnicodeError) as exc:
                report.check(False, f"Invalid JSONL: {name}: {exc}")

    for directory in ("data", "release"):
        for path in (root / directory).rglob("*"):
            if path.suffix not in {".json", ".jsonl"}:
                continue
            try:
                if path.suffix == ".json":
                    json.loads(path.read_text())
                else:
                    for line in path.read_text().splitlines():
                        if line.strip():
                            json.loads(line)
                report.check(True, str(path))
            except (ValueError, UnicodeError) as exc:
                report.check(False, f"Invalid data record: {path.relative_to(root)}: {exc}")
    documents = [root / "README.md", root / "results/README.md", root / "release/README.md"]
    documents.append(root / "REPRODUCIBILITY.md")
    documents += list((root / "protocols").glob("*.md"))
    for path in documents:
        report.check(path.is_file(), f"Missing document: {path.relative_to(root)}")
        if not path.is_file():
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if "://" not in target and not target.startswith("#"):
                destination = (path.parent / target.split("#")[0]).resolve()
                report.check(
                    not destination.is_relative_to((root / "development").resolve()),
                    f"Public documentation links to development: {path.relative_to(root)}",
                )
                report.check(
                    destination.exists(),
                    f"Broken link in {path.relative_to(root)}: {target}",
                )
    for path in (root / "results").rglob("*"):
        report.check(
            path.suffix not in {".py", ".js", ".mjs", ".ipynb"}, f"Code in results: {path}"
        )
    return report
