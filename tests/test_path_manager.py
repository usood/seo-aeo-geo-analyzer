#!/usr/bin/env python3
"""Tests for report path discovery safety."""

from pathlib import Path

from utils.path_manager import get_current_project_path


def test_latest_project_accepts_reports_subdirectory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    project_dir = tmp_path / "reports" / "client"
    project_dir.mkdir(parents=True)
    Path(".latest_project").write_text("reports/client")

    assert get_current_project_path() == str(project_dir.resolve())


def test_latest_project_rejects_paths_outside_reports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    external_dir = tmp_path.parent
    Path(".latest_project").write_text(str(external_dir))

    assert get_current_project_path() == "."


def test_latest_project_rejects_parent_traversal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path(".latest_project").write_text("../")

    assert get_current_project_path() == "."
