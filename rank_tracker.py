#!/usr/bin/env python3
"""Create or compare keyword rank snapshots from saved run outputs."""

import argparse
import json
import sys
from pathlib import Path

from utils.rank_tracking import compare_rank_snapshots, write_rank_snapshot
from utils.run_history import load_json


def write_json(path: str | Path, payload: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Track keyword rankings from Google Search Console snapshots")
    parser.add_argument("--run-dir", help="Run directory containing google_data.json")
    parser.add_argument("--previous", help="Previous rank_snapshot.json")
    parser.add_argument("--current", help="Current rank_snapshot.json")
    parser.add_argument("--output", help="Output path")
    args = parser.parse_args(argv)

    try:
        if args.previous or args.current:
            if not args.previous or not args.current:
                raise ValueError("--previous and --current must be supplied together")
            output = args.output or "rank_comparison.json"
            comparison = compare_rank_snapshots(load_json(args.previous, {}), load_json(args.current, {}))
            path = write_json(output, comparison)
            print(f"Wrote rank comparison: {path}")
            return 0

        if not args.run_dir:
            raise ValueError("--run-dir is required when not comparing snapshots")

        path = write_rank_snapshot(args.run_dir, args.output)
        print(f"Wrote rank snapshot: {path}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
