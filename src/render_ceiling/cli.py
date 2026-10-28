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

    reconstruct_parser = subparsers.add_parser(
        "reconstruct", help="reconstruct coordinates from five calibrated views"
    )
    reconstruct_parser.add_argument("input", type=Path, help="JSON observations, cameras and lattice")
    reconstruct_parser.add_argument("--method", choices=("atomic", "collective", "huber"), default="atomic")
    reconstruct_parser.add_argument("--output", type=Path, help="write JSON to this file (default: stdout)")

    args = parser.parse_args(argv)

    if args.command == "reconstruct":
        from .workflow import ReconstructionInput, Reconstructor

        try:
            inputs = ReconstructionInput.from_json(args.input)
            result = Reconstructor(args.method).run(inputs).to_json()
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(result)
            else:
                print(result, end="")
        except (OSError, ValueError, TypeError) as exc:
            print(f"ERROR  {exc}", file=sys.stderr)
            return 1
        return 0

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
