"""Keyword rank tracking snapshots derived from saved Google Search Console data."""

import json
from pathlib import Path

from utils.run_history import find_latest_json, load_json


SNAPSHOT_FILENAME = "rank_snapshot.json"


def _domain_from_run_dir(run_dir: Path) -> str:
    analysis = load_json(find_latest_json(run_dir, "analysis_data_*.json"), {})
    return analysis.get("metadata", {}).get("target_domain") or "unknown"


def _keyword_record(query: dict) -> dict | None:
    keyword = query.get("keyword") or query.get("query")
    position = query.get("position")
    if not keyword or not isinstance(position, (int, float)):
        return None
    return {
        "keyword": str(keyword),
        "position": round(float(position), 2),
        "clicks": query.get("clicks", 0) or 0,
        "impressions": query.get("impressions", 0) or 0,
    }


def extract_rank_snapshot(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    google_path = run_dir / "google_data.json"
    google = load_json(google_path if google_path.exists() else None, {})
    top_queries = google.get("gsc", {}).get("top_queries", []) if google.get("status") == "success" else []

    keywords = []
    for query in top_queries:
        if not isinstance(query, dict):
            continue
        record = _keyword_record(query)
        if record:
            keywords.append(record)

    return {
        "run_id": run_dir.name,
        "domain": _domain_from_run_dir(run_dir),
        "source": "gsc",
        "source_status": "available" if google_path.exists() and google.get("status") == "success" else "missing",
        "keywords": keywords,
    }


def write_rank_snapshot(run_dir: str | Path, output_path: str | Path | None = None) -> Path:
    run_dir = Path(run_dir)
    output_path = Path(output_path) if output_path else run_dir / SNAPSHOT_FILENAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(extract_rank_snapshot(run_dir), indent=2), encoding="utf-8")
    return output_path


def compare_rank_snapshots(previous: dict, current: dict) -> dict:
    previous_by_keyword = {
        item["keyword"]: item
        for item in previous.get("keywords", [])
        if item.get("keyword") and isinstance(item.get("position"), (int, float))
    }
    current_by_keyword = {
        item["keyword"]: item
        for item in current.get("keywords", [])
        if item.get("keyword") and isinstance(item.get("position"), (int, float))
    }

    improved = []
    declined = []
    for keyword in sorted(previous_by_keyword.keys() & current_by_keyword.keys()):
        previous_position = previous_by_keyword[keyword]["position"]
        current_position = current_by_keyword[keyword]["position"]
        delta = round(previous_position - current_position, 2)
        record = {
            "keyword": keyword,
            "previous_position": previous_position,
            "current_position": current_position,
            "position_delta": delta,
        }
        if delta > 0:
            improved.append(record)
        elif delta < 0:
            declined.append(record)

    new = [
        {"keyword": keyword, "current_position": current_by_keyword[keyword]["position"]}
        for keyword in sorted(current_by_keyword.keys() - previous_by_keyword.keys())
    ]
    lost = [
        {"keyword": keyword, "previous_position": previous_by_keyword[keyword]["position"]}
        for keyword in sorted(previous_by_keyword.keys() - current_by_keyword.keys())
    ]

    return {
        "previous_run_id": previous.get("run_id"),
        "current_run_id": current.get("run_id"),
        "domain": current.get("domain") or previous.get("domain"),
        "improved": improved,
        "declined": declined,
        "new": new,
        "lost": lost,
    }
