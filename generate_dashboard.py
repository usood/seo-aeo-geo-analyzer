#!/usr/bin/env python3
"""Generate a static dashboard from saved run summaries."""

import argparse
import sys

from utils.dashboard import write_dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a static history dashboard")
    parser.add_argument("--reports-root", default="reports", help="Root containing saved scheduled runs")
    parser.add_argument("--domain", help="Limit dashboard to one domain")
    parser.add_argument("--output", help="Output HTML path. Defaults to <reports-root>/index.html")
    args = parser.parse_args(argv)

    try:
        output = write_dashboard(args.reports_root, output_path=args.output, domain=args.domain)
        print(f"Wrote dashboard: {output}")
        return 0
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
