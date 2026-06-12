#!/usr/bin/env python3
"""Tests for keyword rank tracking snapshots."""

import json
import subprocess
import sys
from pathlib import Path

from utils.rank_tracking import (
    compare_rank_snapshots,
    extract_rank_snapshot,
    write_rank_snapshot,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_extract_rank_snapshot_reads_gsc_top_queries(tmp_path):
    write_json(
        tmp_path / "analysis_data_20260612.json",
        {
            "metadata": {"target_domain": "example.com"},
            "sitemap_analysis": {"example.com": {"total_urls": 1}},
        },
    )
    write_json(
        tmp_path / "google_data.json",
        {
            "status": "success",
            "gsc": {
                "top_queries": [
                    {"keyword": "alpha", "position": 4.2, "clicks": 20, "impressions": 300},
                    {"keyword": "beta", "position": 12.0, "clicks": 3, "impressions": 120},
                ]
            },
        },
    )

    snapshot = extract_rank_snapshot(tmp_path)

    assert snapshot["run_id"] == tmp_path.name
    assert snapshot["domain"] == "example.com"
    assert snapshot["source"] == "gsc"
    assert snapshot["source_status"] == "available"
    assert snapshot["keywords"] == [
        {"keyword": "alpha", "position": 4.2, "clicks": 20, "impressions": 300},
        {"keyword": "beta", "position": 12.0, "clicks": 3, "impressions": 120},
    ]


def test_extract_rank_snapshot_handles_missing_google_data(tmp_path):
    snapshot = extract_rank_snapshot(tmp_path)

    assert snapshot["source"] == "gsc"
    assert snapshot["source_status"] == "missing"
    assert snapshot["keywords"] == []


def test_write_rank_snapshot_persists_json(tmp_path):
    write_json(
        tmp_path / "google_data.json",
        {"status": "success", "gsc": {"top_queries": [{"keyword": "alpha", "position": 4.2}]}},
    )

    output = write_rank_snapshot(tmp_path)

    assert output == tmp_path / "rank_snapshot.json"
    assert json.loads(output.read_text())["keywords"][0]["keyword"] == "alpha"


def test_compare_rank_snapshots_reports_directional_changes():
    previous = {
        "run_id": "run-1",
        "keywords": [
            {"keyword": "alpha", "position": 8.0},
            {"keyword": "beta", "position": 2.0},
            {"keyword": "lost", "position": 10.0},
        ],
    }
    current = {
        "run_id": "run-2",
        "keywords": [
            {"keyword": "alpha", "position": 4.0},
            {"keyword": "beta", "position": 5.0},
            {"keyword": "new", "position": 3.0},
        ],
    }

    comparison = compare_rank_snapshots(previous, current)

    assert comparison["previous_run_id"] == "run-1"
    assert comparison["current_run_id"] == "run-2"
    assert comparison["improved"] == [{"keyword": "alpha", "previous_position": 8.0, "current_position": 4.0, "position_delta": 4.0}]
    assert comparison["declined"] == [{"keyword": "beta", "previous_position": 2.0, "current_position": 5.0, "position_delta": -3.0}]
    assert comparison["new"] == [{"keyword": "new", "current_position": 3.0}]
    assert comparison["lost"] == [{"keyword": "lost", "previous_position": 10.0}]


def test_rank_tracker_cli_writes_snapshot(tmp_path):
    write_json(
        tmp_path / "google_data.json",
        {"status": "success", "gsc": {"top_queries": [{"keyword": "alpha", "position": 4.2}]}},
    )
    output = tmp_path / "custom_rank_snapshot.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "rank_tracker.py"),
            "--run-dir",
            str(tmp_path),
            "--output",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert json.loads(output.read_text())["keywords"][0]["keyword"] == "alpha"
