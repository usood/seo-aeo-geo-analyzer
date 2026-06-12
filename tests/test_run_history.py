#!/usr/bin/env python3
"""Tests for run history summaries and comparisons."""

import json

from utils.run_history import (
    build_run_summary,
    compare_summaries,
    find_run_summaries,
    write_run_summary,
)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_run_summary_collects_metrics_from_run_outputs(tmp_path):
    write_json(
        tmp_path / "analysis_data_20260612.json",
        {
            "metadata": {"target_domain": "example.com", "company_name": "Example"},
            "sitemap_analysis": {
                "example.com": {
                    "total_urls": 12,
                    "categorization": {"product": 3, "content": 4, "category": 2, "static": 3},
                    "freshness": {"freshness_percentage": 25},
                }
            },
        },
    )
    write_json(
        tmp_path / "dataforseo_final_20260612.json",
        {
            "gaps": {
                "top_100": [
                    {"keyword": "alpha", "search_volume": 1000, "competitor_position": 3},
                    {"keyword": "beta", "search_volume": 200, "competitor_position": 12},
                ]
            }
        },
    )
    write_json(
        tmp_path / "google_data.json",
        {
            "status": "success",
            "gsc": {
                "totals": {"clicks": 120, "impressions": 2400},
                "top_queries": [
                    {"keyword": "alpha", "position": 4.2, "clicks": 20, "impressions": 300}
                ],
            },
        },
    )
    write_json(
        tmp_path / "performance_analysis.json",
        [
            {"url": "https://example.com/", "performance_score": 90},
            {"url": "https://example.com/blog", "performance_score": 70},
        ],
    )

    summary = build_run_summary(tmp_path)

    assert summary["domain"] == "example.com"
    assert summary["company_name"] == "Example"
    assert summary["run_id"] == tmp_path.name
    assert summary["metrics"]["total_urls"] == 12
    assert summary["metrics"]["keyword_gaps"] == 2
    assert summary["metrics"]["high_opportunity_keywords"] == 1
    assert summary["metrics"]["quick_wins"] == 1
    assert summary["metrics"]["gsc_clicks"] == 120
    assert summary["metrics"]["gsc_impressions"] == 2400
    assert summary["metrics"]["avg_position"] == 4.2
    assert summary["metrics"]["performance_score_avg"] == 80
    assert [item["keyword"] for item in summary["top_keywords"]] == ["alpha", "beta"]


def test_build_run_summary_handles_optional_outputs(tmp_path):
    write_json(
        tmp_path / "analysis_data_20260612.json",
        {
            "metadata": {"target_domain": "example.com"},
            "sitemap_analysis": {"example.com": {"total_urls": 1}},
        },
    )
    write_json(tmp_path / "dataforseo_final_20260612.json", {"gaps": {"top_100": []}})

    summary = build_run_summary(tmp_path)

    assert summary["metrics"]["gsc_clicks"] == 0
    assert summary["metrics"]["avg_position"] is None
    assert summary["metrics"]["performance_score_avg"] is None


def test_write_run_summary_persists_json(tmp_path):
    write_json(
        tmp_path / "analysis_data_20260612.json",
        {
            "metadata": {"target_domain": "example.com"},
            "sitemap_analysis": {"example.com": {"total_urls": 1}},
        },
    )
    write_json(tmp_path / "dataforseo_final_20260612.json", {"gaps": {"top_100": []}})

    output = write_run_summary(tmp_path)

    assert output == tmp_path / "run_summary.json"
    assert json.loads(output.read_text())["domain"] == "example.com"


def test_compare_summaries_reports_metric_deltas_and_keyword_changes():
    previous = {
        "run_id": "run-1",
        "metrics": {"keyword_gaps": 3, "gsc_clicks": 100},
        "top_keywords": [{"keyword": "alpha"}, {"keyword": "beta"}],
    }
    current = {
        "run_id": "run-2",
        "metrics": {"keyword_gaps": 5, "gsc_clicks": 90},
        "top_keywords": [{"keyword": "beta"}, {"keyword": "gamma"}],
    }

    comparison = compare_summaries(previous, current)

    assert comparison["previous_run_id"] == "run-1"
    assert comparison["current_run_id"] == "run-2"
    assert comparison["metric_deltas"]["keyword_gaps"] == 2
    assert comparison["metric_deltas"]["gsc_clicks"] == -10
    assert comparison["new_keywords"] == ["gamma"]
    assert comparison["lost_keywords"] == ["alpha"]


def test_find_run_summaries_returns_sorted_summaries(tmp_path):
    first = tmp_path / "example-com" / "20260601"
    second = tmp_path / "example-com" / "20260602"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    write_json(first / "run_summary.json", {"run_id": "20260601", "domain": "example.com"})
    write_json(second / "run_summary.json", {"run_id": "20260602", "domain": "example.com"})

    summaries = find_run_summaries(tmp_path, domain="example.com")

    assert [summary["run_id"] for summary in summaries] == ["20260601", "20260602"]
