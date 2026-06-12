# History, Rank Tracking, And Dashboard Implementation Plan

> Implementation note: execute this plan task-by-task with tests before code changes.

**Goal:** Add saved run history, run-to-run comparisons, keyword rank tracking, and a lightweight static dashboard over saved audit runs.

**Architecture:** Keep this file-based and deterministic. Each audit run writes a normalized `run_summary.json` in its report directory; comparison and dashboard code read those summaries instead of re-parsing every raw output file each time. Keyword tracking is a snapshot layer derived from Google Search Console query positions when available, with DataForSEO opportunity data used only for opportunity context.

**Tech Stack:** Python standard library, existing JSON outputs, existing `reports/` directory convention, pytest.

---

### Task 1: Run Summary Builder

**Files:**
- Create: `utils/run_history.py`
- Test: `tests/test_run_history.py`
- Modify: `scripts/run_scheduled_analysis.py`

**Step 1: Write failing tests**

Add tests for:
- `build_run_summary(run_dir)` reads `analysis_data_*.json`, `dataforseo_final_*.json`, optional `google_data.json`, optional `performance_analysis.json`.
- Missing optional files produce zero/default metrics, not exceptions.
- `write_run_summary(run_dir)` writes `run_summary.json`.

Expected summary shape:

```json
{
  "run_id": "20260612_100000",
  "domain": "example.com",
  "created_at": "...",
  "metrics": {
    "total_urls": 10,
    "keyword_gaps": 2,
    "high_opportunity_keywords": 1,
    "quick_wins": 1,
    "gsc_clicks": 100,
    "gsc_impressions": 1000,
    "avg_position": 12.3,
    "performance_score_avg": 88
  },
  "top_keywords": [...]
}
```

**Step 2: Run tests to verify red**

Run: `python -m pytest -q tests/test_run_history.py`

Expected: fails because `utils.run_history` does not exist.

**Step 3: Implement minimal run summary code**

Implement:
- `find_latest_json(run_dir, pattern)`
- `load_json(path, default)`
- `build_run_summary(run_dir)`
- `write_run_summary(run_dir)`

Keep parsing conservative. Do not call external APIs.

**Step 4: Wire scheduled wrapper**

After successful scheduled runs, call `write_run_summary(run_dir)` after `write_summary(...)`.

**Step 5: Verify**

Run:
- `python -m pytest -q tests/test_run_history.py tests/test_scheduled_analysis.py`
- `python -m pytest -q`

**Step 6: Commit and PR**

Commit: `Add run history summaries`

---

### Task 2: Run Comparison

**Files:**
- Modify: `utils/run_history.py`
- Create: `compare_runs.py`
- Test: `tests/test_run_comparison.py`
- Modify: `README.md`

**Step 1: Write failing tests**

Add tests for:
- `compare_summaries(previous, current)` returns metric deltas.
- New/lost top keywords are detected by keyword text.
- CLI can compare two supplied `run_summary.json` files and write `run_comparison.json`.

Expected comparison shape:

```json
{
  "previous_run_id": "run-1",
  "current_run_id": "run-2",
  "metric_deltas": {
    "keyword_gaps": 5,
    "gsc_clicks": 20
  },
  "new_keywords": ["keyword c"],
  "lost_keywords": ["keyword a"]
}
```

**Step 2: Run tests to verify red**

Run: `python -m pytest -q tests/test_run_comparison.py`

Expected: fails because comparison functions/CLI do not exist.

**Step 3: Implement comparison utilities**

Add:
- `compare_summaries(previous, current)`
- `find_run_summaries(reports_root, domain=None)`
- `compare_latest_runs(reports_root, domain=None)`

Create `compare_runs.py` with:
- `--previous`
- `--current`
- `--reports-root`
- `--domain`
- `--output`

**Step 4: Verify**

Run:
- `python -m pytest -q tests/test_run_comparison.py`
- `python -m pytest -q`

**Step 5: Commit and PR**

Commit: `Add run comparison utility`

---

### Task 3: Keyword Rank Tracking

**Files:**
- Create: `rank_tracker.py`
- Create: `utils/rank_tracking.py`
- Test: `tests/test_rank_tracking.py`
- Modify: `config.example.yaml`
- Modify: `README.md`

**Step 1: Write failing tests**

Add tests for:
- `extract_rank_snapshot(run_dir)` reads GSC top queries and creates keyword position records.
- Missing `google_data.json` creates an empty snapshot with a clear `source_status`.
- `compare_rank_snapshots(previous, current)` reports improved, declined, new, and lost keywords.

Snapshot shape:

```json
{
  "run_id": "20260612_100000",
  "domain": "example.com",
  "source": "gsc",
  "keywords": [
    {"keyword": "example keyword", "position": 4.2, "clicks": 10, "impressions": 100}
  ]
}
```

**Step 2: Run tests to verify red**

Run: `python -m pytest -q tests/test_rank_tracking.py`

Expected: fails because rank tracking module does not exist.

**Step 3: Implement rank tracking**

Add:
- `extract_rank_snapshot(run_dir)`
- `write_rank_snapshot(run_dir)`
- `compare_rank_snapshots(previous, current)`

Add `rank_tracker.py` CLI:
- `--run-dir`
- `--previous`
- `--current`
- `--output`

**Step 4: Wire scheduled wrapper**

After `write_run_summary(run_dir)`, call `write_rank_snapshot(run_dir)` when possible.

**Step 5: Config docs**

Add optional config:

```yaml
tracking:
  keywords: []
```

Document that GSC rank data is used when `google_integration.py` has run.

**Step 6: Verify**

Run:
- `python -m pytest -q tests/test_rank_tracking.py tests/test_scheduled_analysis.py`
- `python -m pytest -q`

**Step 7: Commit and PR**

Commit: `Add keyword rank tracking snapshots`

---

### Task 4: Static Dashboard Mode

**Files:**
- Create: `generate_dashboard.py`
- Create: `utils/dashboard.py`
- Test: `tests/test_dashboard.py`
- Modify: `run_analysis.py`
- Modify: `README.md`

**Step 1: Write failing tests**

Add tests for:
- Dashboard builder reads multiple `run_summary.json` files.
- Generated HTML includes domain, run count, latest metrics, metric deltas, and latest report links.
- Empty history produces a useful empty-state HTML file.

**Step 2: Run tests to verify red**

Run: `python -m pytest -q tests/test_dashboard.py`

Expected: fails because dashboard module does not exist.

**Step 3: Implement dashboard utilities**

Add:
- `load_dashboard_runs(reports_root, domain=None)`
- `render_dashboard_html(runs, comparisons=None)`
- `write_dashboard(reports_root, output_path=None, domain=None)`

Keep this static HTML. No server, no database.

**Step 4: Add CLI**

`generate_dashboard.py` options:
- `--reports-root reports`
- `--domain`
- `--output reports/index.html`

**Step 5: Add menu option**

Add `run_analysis.py` option:
- `12. Generate History Dashboard`

**Step 6: Verify**

Run:
- `python -m pytest -q tests/test_dashboard.py tests/test_run_analysis.py`
- `python -m pytest -q`

**Step 7: Commit and PR**

Commit: `Add static history dashboard`

---

### Task 5: Final Documentation Pass

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

**Step 1: Update docs**

Document:
- Where run summaries live.
- How to compare latest runs.
- How to track keyword ranks.
- How to generate dashboard.
- Limitations: rank tracking requires GSC data; DataForSEO gap data is not a target-rank source.

**Step 2: Verify docs and tests**

Run:
- `python -m pytest -q`
- `python -m py_compile compare_runs.py rank_tracker.py generate_dashboard.py scripts/run_scheduled_analysis.py`

**Step 3: Commit and PR**

Commit: `Document history and tracking workflows`
