"""Static dashboard generation for saved analyzer run history."""

from html import escape
from pathlib import Path

from utils.run_history import compare_summaries, find_run_summaries


METRIC_LABELS = {
    "total_urls": "Total URLs",
    "keyword_gaps": "Keyword Gaps",
    "high_opportunity_keywords": "High Opportunity Keywords",
    "quick_wins": "Quick Wins",
    "gsc_clicks": "GSC Clicks",
    "gsc_impressions": "GSC Impressions",
    "avg_position": "Average Position",
    "performance_score_avg": "Average Performance Score",
}


def _latest_report_path(run: dict, reports_root: Path) -> str:
    run_dir = run.get("run_dir")
    if not run_dir:
        return ""
    path = Path(run_dir)
    if not path.exists():
        return ""
    matches = sorted(path.glob("*seo-audit*.html"))
    if not matches:
        matches = sorted(path.glob("*.html"))
    if not matches:
        return ""
    report_path = matches[-1]
    try:
        return str(report_path.relative_to(reports_root))
    except ValueError:
        return str(report_path)


def load_dashboard_runs(reports_root: str | Path = "reports", domain: str | None = None) -> list[dict]:
    reports_root = Path(reports_root)
    runs = find_run_summaries(reports_root, domain=domain)
    for run in runs:
        run["report_path"] = _latest_report_path(run, reports_root)
    return runs


def _format_delta(value) -> str:
    if not isinstance(value, (int, float)):
        return ""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:g}"


def _metric_tiles(latest: dict, comparison: dict | None) -> str:
    metrics = latest.get("metrics", {})
    deltas = comparison.get("metric_deltas", {}) if comparison else {}
    tiles = []
    for key, label in METRIC_LABELS.items():
        if key not in metrics:
            continue
        value = metrics.get(key)
        delta = _format_delta(deltas.get(key))
        delta_html = f'<span class="delta">{escape(delta)}</span>' if delta else ""
        tiles.append(
            f"""
            <section class="tile">
              <div class="label">{escape(label)}</div>
              <div class="value">{escape(str(value))}</div>
              {delta_html}
            </section>
            """
        )
    return "\n".join(tiles)


def _run_rows(runs: list[dict]) -> str:
    rows = []
    for run in reversed(runs):
        report_path = run.get("report_path") or ""
        report_link = (
            f'<a href="{escape(report_path)}">Open report</a>'
            if report_path
            else '<span class="muted">No report link</span>'
        )
        rows.append(
            f"""
            <tr>
              <td>{escape(str(run.get("run_id", "")))}</td>
              <td>{escape(str(run.get("domain", "")))}</td>
              <td>{escape(str(run.get("metrics", {}).get("keyword_gaps", "")))}</td>
              <td>{escape(str(run.get("metrics", {}).get("gsc_clicks", "")))}</td>
              <td>{report_link}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def render_dashboard_html(runs: list[dict], comparisons: dict | None = None) -> str:
    if not runs:
        body = """
        <main>
          <h1>SEO/AEO/GEO History Dashboard</h1>
          <p class="empty">No saved runs yet. Run <code>python scripts/run_scheduled_analysis.py</code> to create history.</p>
        </main>
        """
    else:
        latest = runs[-1]
        comparison = comparisons or (compare_summaries(runs[-2], latest) if len(runs) >= 2 else None)
        domain = latest.get("domain", "unknown")
        body = f"""
        <main>
          <header>
            <p class="eyebrow">{escape(str(len(runs)))} runs</p>
            <h1>SEO/AEO/GEO History Dashboard</h1>
            <p class="domain">{escape(str(domain))}</p>
          </header>
          <section class="tiles">
            {_metric_tiles(latest, comparison)}
          </section>
          <section>
            <h2>Saved Runs</h2>
            <table>
              <thead>
                <tr><th>Run</th><th>Domain</th><th>Keyword Gaps</th><th>GSC Clicks</th><th>Report</th></tr>
              </thead>
              <tbody>{_run_rows(runs)}</tbody>
            </table>
          </section>
        </main>
        """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SEO/AEO/GEO History Dashboard</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172033; background: #f6f8fb; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 48px 24px; }}
    h1 {{ margin: 0; font-size: 40px; line-height: 1.1; letter-spacing: 0; }}
    h2 {{ margin-top: 40px; font-size: 22px; }}
    .eyebrow {{ margin: 0 0 8px; color: #047857; font-weight: 700; text-transform: uppercase; font-size: 13px; }}
    .domain {{ color: #516071; font-size: 18px; }}
    .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 32px; }}
    .tile {{ background: #ffffff; border: 1px solid #d9e0ea; border-radius: 8px; padding: 18px; }}
    .label {{ color: #5b6878; font-size: 13px; }}
    .value {{ margin-top: 8px; font-size: 28px; font-weight: 700; }}
    .delta {{ display: inline-block; margin-top: 8px; color: #047857; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #d9e0ea; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #e7ecf2; text-align: left; }}
    th {{ color: #5b6878; font-size: 13px; background: #f0f4f8; }}
    a {{ color: #1d4ed8; }}
    code {{ background: #e7ecf2; padding: 2px 5px; border-radius: 4px; }}
    .empty, .muted {{ color: #5b6878; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def write_dashboard(
    reports_root: str | Path = "reports",
    output_path: str | Path | None = None,
    domain: str | None = None,
) -> Path:
    reports_root = Path(reports_root)
    output_path = Path(output_path) if output_path else reports_root / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_dashboard_html(load_dashboard_runs(reports_root, domain=domain))
    output_path.write_text(html, encoding="utf-8")
    return output_path
