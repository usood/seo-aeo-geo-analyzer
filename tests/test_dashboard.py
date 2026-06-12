#!/usr/bin/env python3
"""Tests for static history dashboard generation."""

import json
import subprocess
import sys
from pathlib import Path

from utils.dashboard import load_dashboard_runs, render_dashboard_html, write_dashboard


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def make_run(reports_root, run_id, metrics, keywords=None, domain="example.com"):
    run_dir = reports_root / "example-com" / run_id
    run_dir.mkdir(parents=True)
    report = run_dir / f"{run_id}-seo-audit.html"
    report.write_text("<html>report</html>", encoding="utf-8")
    write_json(
        run_dir / "run_summary.json",
        {
            "run_id": run_id,
            "domain": domain,
            "run_dir": str(run_dir),
            "metrics": metrics,
            "top_keywords": [{"keyword": keyword} for keyword in (keywords or [])],
        },
    )
    return run_dir


def test_load_dashboard_runs_reads_sorted_summaries_and_report_links(tmp_path):
    make_run(tmp_path, "20260602", {"keyword_gaps": 8}, ["beta"])
    make_run(tmp_path, "20260601", {"keyword_gaps": 5}, ["alpha"])

    runs = load_dashboard_runs(tmp_path, domain="example.com")

    assert [run["run_id"] for run in runs] == ["20260601", "20260602"]
    assert runs[-1]["report_path"] == "example-com/20260602/20260602-seo-audit.html"


def test_render_dashboard_html_includes_latest_metrics_deltas_and_escapes_content(tmp_path):
    make_run(tmp_path, "20260601", {"keyword_gaps": 5, "gsc_clicks": 10}, ["alpha"], domain="<script>")
    make_run(tmp_path, "20260602", {"keyword_gaps": 8, "gsc_clicks": 18}, ["alpha", "beta"], domain="<script>")
    runs = load_dashboard_runs(tmp_path)

    html = render_dashboard_html(runs)

    assert "2 runs" in html
    assert "Keyword Gaps" in html
    assert "8" in html
    assert "+3" in html
    assert "+8" in html
    assert "20260602-seo-audit.html" in html
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_write_dashboard_handles_empty_history(tmp_path):
    output = write_dashboard(tmp_path)

    html = output.read_text(encoding="utf-8")
    assert output == tmp_path / "index.html"
    assert "No saved runs yet" in html


def test_generate_dashboard_cli_writes_output(tmp_path):
    make_run(tmp_path, "20260601", {"keyword_gaps": 5}, ["alpha"])
    output = tmp_path / "dashboard.html"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "generate_dashboard.py"),
            "--reports-root",
            str(tmp_path),
            "--output",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "SEO/AEO/GEO History Dashboard" in output.read_text(encoding="utf-8")
