#!/usr/bin/env python3
"""Tests for run comparison CLI."""

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_compare_runs_cli_compares_supplied_summaries(tmp_path):
    previous = tmp_path / "previous.json"
    current = tmp_path / "current.json"
    output = tmp_path / "run_comparison.json"
    write_json(
        previous,
        {
            "run_id": "run-1",
            "domain": "example.com",
            "metrics": {"keyword_gaps": 3, "gsc_clicks": 100},
            "top_keywords": [{"keyword": "alpha"}, {"keyword": "beta"}],
        },
    )
    write_json(
        current,
        {
            "run_id": "run-2",
            "domain": "example.com",
            "metrics": {"keyword_gaps": 5, "gsc_clicks": 120},
            "top_keywords": [{"keyword": "beta"}, {"keyword": "gamma"}],
        },
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "compare_runs.py"),
            "--previous",
            str(previous),
            "--current",
            str(current),
            "--output",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    comparison = json.loads(output.read_text())
    assert comparison["metric_deltas"]["keyword_gaps"] == 2
    assert comparison["metric_deltas"]["gsc_clicks"] == 20
    assert comparison["new_keywords"] == ["gamma"]
    assert comparison["lost_keywords"] == ["alpha"]


def test_compare_runs_cli_compares_latest_reports_root(tmp_path):
    first = tmp_path / "example-com" / "20260601"
    second = tmp_path / "example-com" / "20260602"
    output = tmp_path / "latest_comparison.json"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    write_json(
        first / "run_summary.json",
        {
            "run_id": "20260601",
            "domain": "example.com",
            "metrics": {"gsc_clicks": 10},
            "top_keywords": [{"keyword": "alpha"}],
        },
    )
    write_json(
        second / "run_summary.json",
        {
            "run_id": "20260602",
            "domain": "example.com",
            "metrics": {"gsc_clicks": 18},
            "top_keywords": [{"keyword": "alpha"}, {"keyword": "beta"}],
        },
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "compare_runs.py"),
            "--reports-root",
            str(tmp_path),
            "--domain",
            "example.com",
            "--output",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    comparison = json.loads(output.read_text())
    assert comparison["previous_run_id"] == "20260601"
    assert comparison["current_run_id"] == "20260602"
    assert comparison["metric_deltas"]["gsc_clicks"] == 8
