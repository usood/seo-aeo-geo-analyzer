#!/usr/bin/env python3
"""Tests for run_analysis.py menu dispatch."""

from unittest.mock import patch

import run_analysis


def test_choice_8_runs_export_step():
    calls = []

    with patch.object(run_analysis, "run_script", side_effect=lambda *args: calls.append(args)):
        run_analysis.handle_choice("8")

    assert calls == [("export_data.py", "Export Data to CSV/Excel/PDF")]


def test_choice_7_checks_report_prerequisites():
    with patch.object(run_analysis, "check_prerequisites", return_value=False) as prereq:
        run_analysis.handle_choice("7")

    prereq.assert_called_once_with("7")
