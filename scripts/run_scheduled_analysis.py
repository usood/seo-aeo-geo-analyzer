#!/usr/bin/env python3
"""Run configured analysis steps for cron or CI schedulers."""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from utils.rank_tracking import write_rank_snapshot
from utils.run_history import write_run_summary


REPO_ROOT = Path(__file__).resolve().parents[1]

STEP_SCRIPTS = {
    "collect_data": "collect_data.py",
    "dataforseo": "dataforseo_collection.py",
    "geo": "geo_analyzer.py",
    "google": "google_integration.py",
    "llm": "llm_runner.py",
    "performance": "performance_check.py",
    "site_llms": "generate_site_llms.py",
    "webmcp": "webmcp_analyzer.py",
    "agentic_browsing": "agentic_browsing_check.py",
    "report": "generate_report.py",
    "export": "export_data.py",
}

DEFAULT_STEPS = [
    "collect_data",
    "dataforseo",
    "geo",
    "google",
    "performance",
    "site_llms",
    "webmcp",
    "agentic_browsing",
    "report",
    "export",
]


class ScheduledAnalysisError(Exception):
    """Raised when scheduled analysis configuration or execution fails."""


def load_schedule_config(config_path: str | Path) -> dict:
    with Path(config_path).open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if not isinstance(config, dict):
        raise ScheduledAnalysisError("Configuration must be a YAML object")

    return config


def resolve_steps(config: dict, override_steps: list[str] | None = None) -> list[str]:
    steps = override_steps or config.get("schedule", {}).get("steps") or DEFAULT_STEPS
    steps = [str(step).strip() for step in steps if str(step).strip()]

    unknown = [step for step in steps if step not in STEP_SCRIPTS]
    if unknown:
        valid = ", ".join(sorted(STEP_SCRIPTS))
        raise ScheduledAnalysisError(f"Unknown scheduled step: {', '.join(unknown)}. Valid steps: {valid}")

    return steps


def _slugify_domain(domain: str) -> str:
    domain = re.sub(r"^https?://", "", str(domain or "site").strip().lower())
    domain = domain.removeprefix("www.").split("/", 1)[0]
    return re.sub(r"[^a-z0-9]+", "-", domain).strip("-") or "site"


def build_run_directory(
    config: dict,
    reports_root: str | Path = "reports",
    run_id: str | None = None,
) -> Path:
    domain = config.get("target", {}).get("domain", "site")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return Path(reports_root) / _slugify_domain(domain) / run_id


def run_steps(
    steps: list[str],
    run_dir: str | Path,
    config_path: str | Path = "config.yaml",
    runner=subprocess.run,
    repo_root: Path = REPO_ROOT,
) -> list[dict]:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["SEO_ANALYZER_OUTPUT_DIR"] = str(run_dir)
    env["SEO_ANALYZER_CONFIG"] = str(config_path)

    results = []
    for step in steps:
        script = STEP_SCRIPTS[step]
        command = [sys.executable, script]
        print(f"[scheduled] Running {step}: {script}")
        try:
            runner(command, cwd=repo_root, env=env, check=True)
        except subprocess.CalledProcessError as exc:
            results.append({"step": step, "script": script, "status": "failed", "returncode": exc.returncode})
            raise ScheduledAnalysisError(f"{step} failed with exit code {exc.returncode}") from exc

        results.append({"step": step, "script": script, "status": "success"})

    return results


def write_summary(run_dir: str | Path, steps: list[str], results: list[dict]) -> Path:
    summary_path = Path(run_dir) / "scheduled_run.json"
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "steps": steps,
        "results": results,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path


def write_analysis_artifacts(run_dir: str | Path, steps: list[str], results: list[dict]) -> dict[str, Path]:
    scheduled_run = write_summary(run_dir, steps, results)
    run_summary = write_run_summary(run_dir)
    rank_snapshot = write_rank_snapshot(run_dir)
    return {"scheduled_run": scheduled_run, "run_summary": run_summary, "rank_snapshot": rank_snapshot}


def parse_step_override(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a scheduled SEO/AEO/GEO analysis")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--steps", help="Comma-separated step override, e.g. collect_data,report,export")
    parser.add_argument("--reports-root", default="reports", help="Root directory for scheduled outputs")
    parser.add_argument("--run-id", help="Run id directory name. Defaults to current UTC timestamp")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved steps and output directory only")
    args = parser.parse_args(argv)

    try:
        config = load_schedule_config(args.config)
        steps = resolve_steps(config, parse_step_override(args.steps))
        run_dir = build_run_directory(config, args.reports_root, args.run_id)

        print(f"[scheduled] Output directory: {run_dir}")
        print(f"[scheduled] Steps: {', '.join(steps)}")

        if args.dry_run:
            return 0

        results = run_steps(steps, run_dir, config_path=args.config)
        artifacts = write_analysis_artifacts(run_dir, steps, results)
        print(f"[scheduled] Summary: {artifacts['scheduled_run']}")
        print(f"[scheduled] Run summary: {artifacts['run_summary']}")
        print(f"[scheduled] Rank snapshot: {artifacts['rank_snapshot']}")
        return 0
    except ScheduledAnalysisError as exc:
        print(f"[scheduled] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
