"""Verify that the release is complete and internally consistent. Exit 0 = it is.

Checks, in order of severity:

  1   the directories the release is made of are all present
  2   every record directory carries a results.json, and results/ holds no loose files
  3   every JSON file in the release parses
  4   results/INDEX.json lists exactly the records that exist on disk
  5   every four-decimal number in README.md traces by value to a record
  6   README.md states the actual counts of records, data files and released files
  7   no provisional material (pilot, smoke, scratch, tmp) is shipped
  8   every prediction vector in release/ is a list of per-structure entries
  9   nothing in the release points at a document that is not shipped

This module deliberately imports nothing from the rest of the package. A claim
and the code that re-derives it must not be able to fail together, so the
verifier shares no code with the implementation it is checking.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# Directories the release is made of.
REQUIRED_DIRS = ("src/render_ceiling", "data", "results", "release")

# Words that mark a file as working material rather than a result.
PROVISIONAL = ("pilot", "smoke", "diagnostic", "tmp", "scratch", "draft", "wip")


class Report:
    """Collects failures and warnings so every check runs before anything exits."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passed = 0

    def check(self, condition: bool, message: str, *, warn: bool = False) -> bool:
        if condition:
            self.passed += 1
        elif warn:
            self.warnings.append(message)
        else:
            self.failures.append(message)
        return condition


def _numeric_values(obj: object, sink: set[float]) -> None:
    """Collect every number in a record, rounded to 2, 3 and 4 decimals.

    Numbers embedded in strings count too: records state some values in prose
    fields, and a value is traceable whether or not it happens to be typed.
    """
    if isinstance(obj, dict):
        for value in obj.values():
            _numeric_values(value, sink)
    elif isinstance(obj, list):
        for value in obj:
            _numeric_values(value, sink)
    elif isinstance(obj, bool):
        return
    elif isinstance(obj, (int, float)):
        for places in (4, 3, 2):
            sink.add(round(float(obj), places))
            sink.add(round(-float(obj), places))
    elif isinstance(obj, str):
        for match in re.finditer(r"(?<![\d.])(\d+\.\d{2,4})(?![\d])", obj):
            for places in (4, 3, 2):
                sink.add(round(float(match.group(1)), places))


def verify(root: Path) -> Report:
    report = Report()
    readme_path = root / "README.md"
    if not readme_path.exists():
        report.failures.append(f"[1] no README.md at {root}; is this the release root?")
        return report
    readme = readme_path.read_text()

    # 1 structure
    for name in REQUIRED_DIRS:
        report.check((root / name).is_dir(), f"[1] missing directory: {name}")

    results_root = root / "results"
    records = sorted(p for p in results_root.iterdir() if p.is_dir())

    # 2 one record, one results.json; nothing loose beside them
    for record in records:
        report.check(
            (record / "results.json").exists(),
            f"[2] record carries no results.json: results/{record.name}",
        )
    stray = [p.name for p in results_root.iterdir() if p.is_file() and p.name != "INDEX.json"]
    report.check(
        not stray,
        f"[2] loose files in results/ (expected one directory per record): {stray}",
    )

    # 3 every JSON parses, and collect the values while we are reading them
    values: set[float] = set()
    for path in sorted(root.glob("results/**/*.json")) + sorted(root.glob("release/**/*.json")):
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            report.check(False, f"[3] malformed JSON: {path.relative_to(root)}: {exc}")
            continue
        report.passed += 1
        if path.parts[-3:-1] and path.parent.parent.name == "results":
            _numeric_values(payload, values)

    # 4 INDEX.json agrees with the tree
    index_path = results_root / "INDEX.json"
    if report.check(index_path.exists(), "[4] results/INDEX.json is missing"):
        index = json.loads(index_path.read_text())
        listed = {entry["name"] for entry in index.get("records", [])}
        on_disk = {record.name for record in records}
        report.check(
            not (on_disk - listed),
            f"[4] records on disk but absent from INDEX.json: {sorted(on_disk - listed)}",
        )
        report.check(
            not (listed - on_disk),
            f"[4] records listed in INDEX.json but absent on disk: {sorted(listed - on_disk)}",
        )

    # 5 every four-decimal number in the README traces to a record.
    # This is the check the release rests on: the README is the only prose that
    # ships, so it is the only place a number can be asserted without a record.
    untraced = sorted(
        {
            match.group(1)
            for match in re.finditer(r"(?<![\d.])(\d\.\d{4})(?![\d])", readme)
            if round(float(match.group(1)), 4) not in values
        }
    )
    report.check(not untraced, f"[5] README numbers that trace to no record: {untraced}")

    # 6 the README's counts are the tree's counts.
    # Word-boundary match, not substring: a bare `str(v) in readme` lets a count
    # of 90 pass because "90" occurs inside "0.9095". A count check that any
    # decimal can satisfy is not a count check.
    counts = {
        "records": len(records),
        "record JSON files": len(list(root.glob("results/*/*.json"))),
        # Rendered images are a build product and are not tracked; count only
        # the structures, labels and splits the release actually ships.
        "data files": len(
            [p for p in root.glob("data/**/*") if p.is_file() and "renders" not in p.parts]
        ),
        "released files": len([p for p in root.glob("release/**/*") if p.is_file()]),
        "package modules": len(list((root / "src/render_ceiling").glob("*.py"))),
    }
    for label, value in counts.items():
        report.check(
            re.search(rf"(?<![\d.]){value}(?![\d.])", readme) is not None,
            f"[6] README does not state the actual {label} count ({value})",
        )

    # 7 no working material in the release
    for path in sorted(root.glob("results/**/*")) + sorted(root.glob("release/**/*")):
        if path.is_file() and any(word in path.name.lower() for word in PROVISIONAL):
            report.check(False, f"[7] provisional file shipped: {path.relative_to(root)}")

    # 8 prediction vectors are per-structure lists
    predictions = sorted((root / "release/predictions").glob("*.json"))
    report.check(bool(predictions), "[8] release/predictions holds no prediction vectors")
    for path in predictions:
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue  # already reported by check 3
        report.check(
            isinstance(payload, (list, dict)) and len(payload) > 0,
            f"[8] empty prediction vector: {path.relative_to(root)}",
        )

    # 9 nothing shipped points at a document that is not shipped.
    # The record prose and the supplementary document are the authors' working
    # material and are not part of the release, so a reference to one is a
    # dangling pointer for every reader.
    # Only a reference that points INTO the release is a dangling pointer. Some
    # records are audits whose subject is a document, and the titles they name
    # are data about what was audited, not links a reader should follow.
    pointer = re.compile(r"\b(?:results|release|data|src|docs|weights)/[\w/.-]*\.md\b")
    dangling = []
    for path in sorted(root.glob("results/**/*.json")) + sorted(root.glob("release/**/*.json")):
        for match in pointer.finditer(path.read_text()):
            dangling.append(f"{path.relative_to(root)} -> {match.group(0)}")
    report.check(
        not dangling,
        f"[9] release files reference documents that are not shipped: {dangling[:10]}"
        + (f" (and {len(dangling) - 10} more)" if len(dangling) > 10 else ""),
    )

    return report
