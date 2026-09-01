"""Command-line entry point for the release."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .verify import verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="render-ceiling", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser(
        "verify", help="check that the release is complete and internally consistent"
    )
    verify_parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="release root (default: the working directory)",
    )
    verify_parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as failures",
    )

    args = parser.parse_args(argv)

    if args.command == "verify":
        report = verify(args.root.resolve())
        for message in report.warnings:
            print(f"WARN  {message}")
        for message in report.failures:
            print(f"FAIL  {message}")
        failed = len(report.failures) + (len(report.warnings) if args.strict else 0)
        print(f"\nPASSED {report.passed}  FAILED {failed}  WARNINGS {len(report.warnings)}")
        return 1 if failed else 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
