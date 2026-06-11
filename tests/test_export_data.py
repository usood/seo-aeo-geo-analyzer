#!/usr/bin/env python3
"""Tests for export_data.py."""

import py_compile


def test_export_data_compiles():
    """Export script should be importable by Python."""
    py_compile.compile("export_data.py", doraise=True)
