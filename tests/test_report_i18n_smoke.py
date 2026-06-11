#!/usr/bin/env python3
"""Smoke tests for localized report rendering."""

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_generate_report_uses_spanish_ui_labels(tmp_path):
    (tmp_path / "config.yaml").write_text(
        """
target:
  domain: example.com
  name: Example
competitors:
  - domain: competitor.com
    name: Competitor
location:
  country: United States
  language_code: en
report:
  company_name: Example
  language: es
"""
    )
    (tmp_path / "analysis_data_fixture.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "target_domain": "example.com",
                    "competitors": {"competitor.com": "Competitor"},
                    "company_name": "Example",
                    "language": "en",
                    "branding": {},
                },
                "sitemap_analysis": {
                    "example.com": {
                        "total_urls": 1,
                        "categorization": {
                            "product": 0,
                            "content": 0,
                            "category": 0,
                            "static": 1,
                        },
                        "freshness": {"freshness_percentage": None},
                    }
                },
                "social_profiles": {"example.com": {}},
                "local_international": {},
            }
        )
    )
    (tmp_path / "dataforseo_final_fixture.json").write_text(
        json.dumps(
            {
                "gaps": {"top_100": []},
                "keyword_enrichment": [],
                "search_intent": [],
                "domain_metrics": {},
                "backlinks": {},
            }
        )
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "generate_report.py")],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    report_file = tmp_path / "example-com-seo-audit-2026-06-11.html"
    if not report_file.exists():
        generated = list(tmp_path.glob("example-com-seo-audit-*.html"))
        assert generated, result.stdout + result.stderr
        report_file = generated[0]

    html = report_file.read_text()
    assert '<html lang="es">' in html
    assert "Informe de analisis SEO" in html
    assert "Resumen ejecutivo" in html
    assert "Palabra clave" in html
