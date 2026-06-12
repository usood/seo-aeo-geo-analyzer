"""File-based run history summaries and comparisons."""

import json
from datetime import datetime, timezone
from pathlib import Path


SUMMARY_FILENAME = "run_summary.json"


def find_latest_json(run_dir: str | Path, pattern: str) -> Path | None:
    files = sorted(Path(run_dir).glob(pattern), key=lambda path: path.stat().st_mtime)
    return files[-1] if files else None


def load_json(path: str | Path | None, default):
    if not path:
        return default
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _average(values):
    values = [value for value in values if isinstance(value, (int, float))]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _keyword_categories(top_keywords):
    high_opportunity = 0
    quick_wins = 0

    for item in top_keywords:
        volume = item.get("search_volume") or 0
        position = item.get("competitor_position") or 999
        difficulty = item.get("difficulty")

        if volume >= 500 and position <= 10:
            high_opportunity += 1
        elif volume >= 100 and (difficulty is None or difficulty < 40):
            quick_wins += 1

    return high_opportunity, quick_wins


def _top_keywords(top_keywords, limit=25):
    normalized = []
    for item in top_keywords[:limit]:
        keyword = item.get("keyword")
        if not keyword:
            continue
        normalized.append(
            {
                "keyword": str(keyword),
                "search_volume": item.get("search_volume", 0) or 0,
                "competitor": item.get("competitor", ""),
                "competitor_position": item.get("competitor_position"),
            }
        )
    return normalized


def build_run_summary(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    analysis = load_json(find_latest_json(run_dir, "analysis_data_*.json"), {})
    dataforseo = load_json(find_latest_json(run_dir, "dataforseo_final_*.json"), {})
    google = load_json(run_dir / "google_data.json" if (run_dir / "google_data.json").exists() else None, {})
    performance = load_json(
        run_dir / "performance_analysis.json" if (run_dir / "performance_analysis.json").exists() else None,
        [],
    )

    metadata = analysis.get("metadata", {})
    domain = metadata.get("target_domain") or dataforseo.get("metadata", {}).get("target_domain") or "unknown"
    sitemap = analysis.get("sitemap_analysis", {}).get(domain, {})
    top_keywords = dataforseo.get("gaps", {}).get("top_100", []) or []
    high_opportunity, quick_wins = _keyword_categories(top_keywords)

    gsc = google.get("gsc", {})
    gsc_totals = gsc.get("totals", {})
    gsc_positions = [
        query.get("position")
        for query in gsc.get("top_queries", [])
        if isinstance(query.get("position"), (int, float))
    ]

    performance_scores = [
        item.get("performance_score")
        for item in performance
        if isinstance(item, dict) and isinstance(item.get("performance_score"), (int, float))
    ]

    return {
        "run_id": run_dir.name,
        "domain": domain,
        "company_name": metadata.get("company_name") or domain,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "metrics": {
            "total_urls": sitemap.get("total_urls", 0) or 0,
            "keyword_gaps": len(top_keywords),
            "high_opportunity_keywords": high_opportunity,
            "quick_wins": quick_wins,
            "gsc_clicks": gsc_totals.get("clicks", 0) or 0,
            "gsc_impressions": gsc_totals.get("impressions", 0) or 0,
            "avg_position": _average(gsc_positions),
            "performance_score_avg": _average(performance_scores),
        },
        "top_keywords": _top_keywords(top_keywords),
    }


def write_run_summary(run_dir: str | Path) -> Path:
    run_dir = Path(run_dir)
    summary = build_run_summary(run_dir)
    output = run_dir / SUMMARY_FILENAME
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return output


def compare_summaries(previous: dict, current: dict) -> dict:
    previous_metrics = previous.get("metrics", {})
    current_metrics = current.get("metrics", {})
    metric_names = sorted(set(previous_metrics) | set(current_metrics))
    metric_deltas = {}

    for name in metric_names:
        previous_value = previous_metrics.get(name)
        current_value = current_metrics.get(name)
        if isinstance(previous_value, (int, float)) and isinstance(current_value, (int, float)):
            metric_deltas[name] = round(current_value - previous_value, 2)

    previous_keywords = {item.get("keyword") for item in previous.get("top_keywords", []) if item.get("keyword")}
    current_keywords = {item.get("keyword") for item in current.get("top_keywords", []) if item.get("keyword")}

    return {
        "previous_run_id": previous.get("run_id"),
        "current_run_id": current.get("run_id"),
        "domain": current.get("domain") or previous.get("domain"),
        "metric_deltas": metric_deltas,
        "new_keywords": sorted(current_keywords - previous_keywords),
        "lost_keywords": sorted(previous_keywords - current_keywords),
    }


def find_run_summaries(reports_root: str | Path = "reports", domain: str | None = None) -> list[dict]:
    reports_root = Path(reports_root)
    summaries = []
    if not reports_root.exists():
        return summaries

    for path in sorted(reports_root.glob(f"**/{SUMMARY_FILENAME}")):
        summary = load_json(path, {})
        if domain and summary.get("domain") != domain:
            continue
        summaries.append(summary)

    return sorted(summaries, key=lambda item: item.get("run_id", ""))


def compare_latest_runs(reports_root: str | Path = "reports", domain: str | None = None) -> dict | None:
    summaries = find_run_summaries(reports_root, domain)
    if len(summaries) < 2:
        return None
    return compare_summaries(summaries[-2], summaries[-1])
