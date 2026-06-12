#!/usr/bin/env python3
"""Tests for scheduled analysis wrapper."""

import subprocess

import pytest

from scripts.run_scheduled_analysis import (
    ScheduledAnalysisError,
    build_run_directory,
    load_schedule_config,
    resolve_steps,
    run_steps,
)


def test_load_schedule_config_reads_schedule_defaults(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
target:
  domain: example.com
schedule:
  enabled: true
  frequency: weekly
  timezone: UTC
  steps:
    - collect_data
    - report
"""
    )

    config = load_schedule_config(config_path)

    assert config["target"]["domain"] == "example.com"
    assert config["schedule"]["steps"] == ["collect_data", "report"]


def test_resolve_steps_uses_config_steps():
    config = {"schedule": {"steps": ["collect_data", "report"]}}

    assert resolve_steps(config) == ["collect_data", "report"]


def test_resolve_steps_rejects_unknown_step():
    config = {"schedule": {"steps": ["collect_data", "unknown"]}}

    with pytest.raises(ScheduledAnalysisError, match="Unknown scheduled step"):
        resolve_steps(config)


def test_build_run_directory_uses_domain_and_run_id(tmp_path):
    config = {"target": {"domain": "www.example.com"}}

    run_dir = build_run_directory(config, reports_root=tmp_path, run_id="20260611_120000")

    assert run_dir == tmp_path / "example-com" / "20260611_120000"


def test_run_steps_sets_output_dir_and_stops_on_failure(tmp_path):
    calls = []

    def fake_runner(command, **kwargs):
        calls.append((command, kwargs))
        if command[-1] == "dataforseo_collection.py":
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0)

    with pytest.raises(ScheduledAnalysisError, match="dataforseo failed"):
        run_steps(
            ["collect_data", "dataforseo", "report"],
            run_dir=tmp_path,
            config_path="examples/configs/d2c-ecommerce.yaml",
            runner=fake_runner,
        )

    assert [call[0][-1] for call in calls] == ["collect_data.py", "dataforseo_collection.py"]
    assert calls[0][1]["env"]["SEO_ANALYZER_OUTPUT_DIR"] == str(tmp_path)
    assert calls[0][1]["env"]["SEO_ANALYZER_CONFIG"] == "examples/configs/d2c-ecommerce.yaml"
