#!/usr/bin/env python3
"""Tests for report label localization."""

from pathlib import Path

from utils.config_loader import Config
from utils.i18n import (
    LocaleCatalog,
    find_unknown_locale_keys,
    load_locale,
    resolve_report_language,
)


def test_load_locale_translates_known_key_and_falls_back_to_english():
    catalog = load_locale("es")

    assert catalog.t("report.nav.executive_summary") == "Resumen ejecutivo"
    assert catalog.t("report.empty.no_urgent_fixes") == "No urgent fixes detected via GSC."


def test_unknown_language_falls_back_to_english():
    catalog = load_locale("zz")

    assert catalog.language == "en"
    assert catalog.t("report.nav.executive_summary") == "Executive Summary"


def test_unknown_key_returns_key_for_visibility():
    catalog = LocaleCatalog(language="en", labels={"known": "Known"}, fallback={})

    assert catalog.t("missing.key") == "missing.key"


def test_find_unknown_locale_keys_flags_keys_not_in_english(tmp_path):
    locale_dir = tmp_path / "locales"
    locale_dir.mkdir()
    (locale_dir / "en.json").write_text('{"known": "Known"}')
    (locale_dir / "es.json").write_text('{"known": "Conocido", "extra": "Extra"}')

    assert find_unknown_locale_keys(locale_dir) == {"es.json": ["extra"]}


def test_project_locale_files_do_not_define_unknown_keys():
    assert find_unknown_locale_keys() == {}


def test_resolve_report_language_prefers_report_language(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
target:
  domain: example.com
  name: Example
competitors:
  - domain: competitor.com
    name: Competitor
location:
  country: United States
  language_code: fr
report:
  language: es
"""
    )

    assert resolve_report_language(Config(str(config_path))) == "es"


def test_resolve_report_language_falls_back_to_location_language(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
target:
  domain: example.com
  name: Example
competitors:
  - domain: competitor.com
    name: Competitor
location:
  country: United States
  language_code: fr
"""
    )

    assert resolve_report_language(Config(str(config_path))) == "fr"
