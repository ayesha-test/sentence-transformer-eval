#!/usr/bin/env python3
"""Evaluate sample (or custom) LLM outputs and write report.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evalkit.evaluator import evaluate_all

ROOT = Path(__file__).parent
DEFAULT_DATA = ROOT / "data" / "samples.json"


def print_report(report: dict) -> None:
    summary = report["summary"]
    print("\n=== LLM output evaluation ===")
    print(
        f"Total: {summary['total']}  "
        f"Passed: {summary['passed']}  "
        f"Failed: {summary['failed']}"
    )
    print(f"Pass rate: {summary['pass_rate']:.0%}\n")

    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        label = f"  {result['label']}" if result.get("label") else ""
        print(f"[{status}] {result['id']}  score={result['overall_score']:.3f}{label}")
        print(
            f"  structure={result['structure_score']:.2f}  "
            f"coverage={result['coverage_score']:.2f}  "
            f"similarity={result['similarity_score']:.2f}"
        )
        for reason in result["reasons"]:
            print(f"  - {reason}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="JSON array of {id, source_text, generated_output} objects",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "report.json",
        help="Where to write the JSON report",
    )
    args = parser.parse_args()

    try:
        items = json.loads(args.data.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading {args.data}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(items, list):
        print("Expected a JSON array of evaluation items", file=sys.stderr)
        return 1

    report = evaluate_all(items)
    print_report(report)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Report written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
