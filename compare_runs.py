#!/usr/bin/env python3
"""Compare saved SEO/AEO/GEO analyzer run summaries."""

import argparse
import json
import sys
from pathlib import Path

from utils.run_history import compare_latest_runs, compare_summaries, load_json


def write_comparison(comparison: dict, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    return output_path


def build_comparison(args: argparse.Namespace) -> dict | None:
    if args.previous or args.current:
        if not args.previous or not args.current:
            raise ValueError("--previous and --current must be supplied together")
        previous = load_json(args.previous, {})
        current = load_json(args.current, {})
        return compare_summaries(previous, current)

    return compare_latest_runs(args.reports_root, domain=args.domain)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare saved run_summary.json files")
    parser.add_argument("--previous", help="Path to the previous run_summary.json")
    parser.add_argument("--current", help="Path to the current run_summary.json")
    parser.add_argument("--reports-root", default="reports", help="Root containing saved reports")
    parser.add_argument("--domain", help="Limit latest-run comparison to one domain")
    parser.add_argument("--output", default="run_comparison.json", help="Output JSON path")
    args = parser.parse_args(argv)

    try:
        comparison = build_comparison(args)
        if comparison is None:
            print("Need at least two run_summary.json files to compare", file=sys.stderr)
            return 1
        output_path = write_comparison(comparison, args.output)
        print(f"Wrote comparison: {output_path}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
