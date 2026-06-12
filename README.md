# SEO/AEO/GEO Analyzer

> Comprehensive SEO, AEO (Answer Engine Optimization), and GEO (Generative Engine Optimization) competitive analysis tool for D2C, B2B, and B2C brands. Identifies keyword opportunities, optimizes for AI search engines, and provides actionable recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Project Status

This project is actively maintained as an open-source SEO and AI-search analysis toolkit.

- **Current maintenance focus:** reliability, security hardening, example anonymization, and AI/agentic search readiness.
- **Supported runtime:** Python 3.8+.
- **Verification command:** `python -m pytest -q`.
- **Contribution model:** pull requests with tests for behavior changes.
- **Recent maintenance evidence:** CI/security hygiene, issue and PR templates, scheduled analysis workflow, localization, AI-readiness checks, and run-history dashboard support are all documented in [CHANGELOG.md](CHANGELOG.md).
- **Security reporting:** see [SECURITY.md](SECURITY.md).
- **Release notes:** see [CHANGELOG.md](CHANGELOG.md).

## Features

Each capability maps to an SEO/AEO/GEO aspect, with _why it matters_ called out so results are easy to prioritize:

- **🎯 Keyword Gap Analysis** - Find 100+ high-value keywords your competitors rank for. _Why it matters: surfaces proven demand you're currently invisible for — usually the fastest path to incremental organic traffic._
- **🗺️ Sitemap & Content Structure** - Crawl the sitemap and categorize/measure freshness of pages. _Why it matters: crawlability, a clean structure, and fresh content are the foundation Google and AI engines rely on to index you at all._
- **🤖 GEO (Generative Engine Optimization)** - Optimize for AI search experiences, including ChatGPT, Perplexity, Google AI Overviews, and Google AI Mode. _Why it matters: AI answers increasingly resolve queries before the click, so structured, citable content is how you stay visible._
- **⚡ Performance Audit** - Core Web Vitals analysis with PageSpeed Insights. _Why it matters: speed and visual stability are confirmed Google ranking signals and directly affect conversion._
- **📊 Competitive Intelligence** - Domain metrics, backlinks, and SERP analysis. _Why it matters: benchmarks the gap to competitors so effort targets winnable terms instead of lost causes._
- **📝 Content Opportunities** - Categorized by intent (informational, transactional, commercial). _Why it matters: matching content to search intent is what converts rankings into revenue._
- **🧭 Site `llms.txt` Generator** - Emit a curated `llms.txt` of the analyzed site's key entry points. _Why it matters: helps AI agents and LLM tools discover your most important pages (optional; not a Google Search requirement)._
- **🧩 WebMCP Opportunity Analysis** - Flag action-oriented pages/flows (checkout, signup, booking, forms) and score WebMCP readiness. _Why it matters: as AI agents start completing tasks in the browser, exposing structured tools for these flows is how you stay actionable to them (experimental signal)._
- **🧭 Agentic Browsing Audit** - Run Lighthouse's experimental agentic-browsing category (with graceful fallback when unavailable). _Why it matters: a forward-looking readiness signal for how well AI agents can perceive and act on your pages._
- **📈 Actionable Roadmap** - 30/60/90-day implementation plan. _Why it matters: turns findings into sequenced, shippable work._
- **🎨 Beautiful HTML Reports** - Interactive, sortable data tables
- **📤 Data Export** - Export analysis data to CSV, Excel, and PDF formats

## Who This Is For

This tool is useful when you need a repeatable SEO/AEO/GEO audit without building a custom data pipeline from scratch.

- **SEO agencies and consultants** can use it to produce client-ready audits, benchmark competitors, and turn discovery work into prioritized implementation plans.
- **Content and growth teams** can use it to find keyword gaps, content gaps, product-page opportunities, and AI-search visibility issues.
- **DTC and ecommerce brands** can use it to identify product, collection, comparison, and buying-guide opportunities competitors already rank for.
- **B2B SaaS companies** can use it to discover bottom-of-funnel topics, category-page gaps, competitor positioning, and technical SEO issues.
- **Consumer apps and marketplaces** can use it to map high-intent acquisition queries, landing-page gaps, and performance issues across key flows.
- **Developers and technical marketers** can use it as an extensible base for scheduled audits, custom report sections, WebMCP checks, `llms.txt`, and agentic-browser readiness.

## Done-For-You Implementation

This repository is the open-source analyzer. If you want the audit findings implemented for you, [Snezzi](https://snezzi.com) can help with the done-for-you layer: technical SEO fixes, content plans, programmatic SEO workflows, AI-search readiness, `llms.txt`, WebMCP planning, and recurring reporting.

The open-source project remains useful on its own; Snezzi is the service option for teams that want execution and ongoing maintenance handled end to end.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/usood/seo-aeo-geo-analyzer.git
cd seo-aeo-geo-analyzer

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example config
cp config.example.yaml config.yaml

# Add your DataForSEO credentials
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Run Analysis

```bash
# Interactive mode
python run_analysis.py

# Or run complete analysis automatically
python run_analysis.py --auto
```

### 4. Scheduled Runs

Scheduling is handled by a thin wrapper around the same CLI scripts:

```bash
python scripts/run_scheduled_analysis.py
```

By default it reads `schedule.steps` from `config.yaml`, writes outputs under `reports/<domain>/<run_id>/`, and exits non-zero if any step fails. You can run a smaller no-cost subset with:

```bash
python scripts/run_scheduled_analysis.py --steps collect_data,site_llms,webmcp,report
```

The GitHub Actions workflow at [.github/workflows/scheduled-analysis.yml](.github/workflows/scheduled-analysis.yml) is manual by default because the DataForSEO step can incur cost. Its default workflow inputs run a no-cost subset against a public example config:

- `config_path`: `examples/configs/d2c-ecommerce.yaml`
- `steps`: `collect_data,site_llms,webmcp`

To run a full paid workflow, choose a real config and include `dataforseo` in the step list. Enable the commented cron block only after adding the required repository secrets:

- `DATAFORSEO_LOGIN`
- `DATAFORSEO_PASSWORD`
- `PAGESPEED_API_KEY`
- optional `GEMINI_API_KEY` or `OPENROUTER_API_KEY`

Each scheduled run writes:

- `scheduled_run.json` - step execution status
- `run_summary.json` - normalized metrics for history and comparison
- `rank_snapshot.json` - GSC keyword positions when Google Search Console data is available

Scheduled reports are uploaded as workflow artifacts and should not be committed back to the repository.

Generated run artifacts:

| File | Created by | Purpose |
| ---- | ---------- | ------- |
| `scheduled_run.json` | `scripts/run_scheduled_analysis.py` | Records which scheduled steps ran and whether they succeeded |
| `run_summary.json` | `utils/run_history.py` | Normalized metrics used by comparisons and dashboards |
| `rank_snapshot.json` | `utils/rank_tracking.py` | Google Search Console keyword position snapshot |
| `run_comparison.json` | `compare_runs.py` | Metric deltas plus new/lost opportunity keywords |
| `rank_comparison.json` | `rank_tracker.py --previous ... --current ...` | Improved, declined, new, and lost keyword rankings |
| `reports/index.html` | `generate_dashboard.py` | Static history dashboard over saved runs |

### 5. Compare Runs And Generate Dashboard

```bash
# Compare the latest two saved runs
python compare_runs.py --reports-root reports --domain example.com --output reports/example-com/latest-comparison.json

# Track keyword rank movement from saved GSC data
python rank_tracker.py --run-dir reports/example-com/20260612_100000

# Generate a static dashboard at reports/index.html
python generate_dashboard.py --reports-root reports
```

The dashboard is static HTML and reads saved `run_summary.json` files. It does not require a database or web server.

## Configuration

Edit `config.yaml` to customize for your brand:

```yaml
target:
  domain: "yourbrand.com"
  name: "Your Brand Name"
  industry: "E-commerce"

competitors:
  - domain: "competitor1.com"
    name: "Competitor One"

location:
  country: "United States"
  language_code: "en"

branding:
  primary_color: "#3b82f6"
  logo_emoji: "🚀"

report:
  language: "en" # UI labels only; keywords, URLs, metrics, and AI text stay unchanged.

tracking:
  keywords: [] # Optional future allowlist; GSC top queries are tracked by default when available.
```

### Report Languages

Report UI labels are deterministic and free to render. Set `report.language` in `config.yaml`; if it is omitted, the report falls back to `location.language_code`, then English.

Supported starter locales:

- `en` - English
- `es` - Spanish

To add a language, copy [locales/en.json](locales/en.json), translate the values, save it as `locales/<language>.json`, and open a PR. Locale files can be partial; missing labels fall back to English.

### Example Configurations

Pre-configured examples for different business types:

- **DTC E-commerce**: [examples/configs/d2c-ecommerce.yaml](examples/configs/d2c-ecommerce.yaml) using Allbirds
- **B2B SaaS**: [examples/configs/saas-b2b.yaml](examples/configs/saas-b2b.yaml) using Asana
- **Consumer App**: [examples/configs/consumer-app.yaml](examples/configs/consumer-app.yaml) using Duolingo

## Components

### Data Collection Scripts

| Script                      | Purpose                                                      | Output                      | Time    |
| --------------------------- | ------------------------------------------------------------ | --------------------------- | ------- |
| `collect_data.py`           | Sitemap & social analysis                                    | `analysis_data_*.json`      | ~30s    |
| `dataforseo_collection.py`  | Keyword & SERP data                                          | `dataforseo_final_*.json`   | ~25min  |
| `geo_analyzer.py`           | JSON-LD schema extraction                                    | `geo_analysis.json`         | ~30s    |
| `performance_check.py`      | Core Web Vitals                                              | `performance_analysis.json` | ~3min   |
| `export_data.py`            | Data export (CSV/XLSX/PDF)                                   | `exports/`                  | ~10s    |
| `generate_site_llms.py`     | Recommended `llms.txt` for the analyzed site (offline, free) | `<domain>-llms.txt`         | ~5s     |
| `webmcp_analyzer.py`        | WebMCP opportunity scoring for action flows (offline, free)  | `webmcp_analysis.json`      | ~5s     |
| `agentic_browsing_check.py` | Local Lighthouse agentic-browsing audit (graceful fallback)  | `agentic_browsing.json`     | ~1-3min |
| `scripts/run_scheduled_analysis.py` | Scheduled wrapper for cron/CI runs                  | `reports/<domain>/<run_id>/` | varies  |
| `compare_runs.py`          | Compare saved run summaries                                  | `run_comparison.json`       | ~5s     |
| `rank_tracker.py`          | Create or compare GSC keyword rank snapshots                 | `rank_snapshot.json`        | ~5s     |
| `generate_dashboard.py`    | Generate static history dashboard                            | `reports/index.html`        | ~5s     |

### Report Generation

| Script               | Purpose     | Output                      |
| -------------------- | ----------- | --------------------------- |
| `generate_report.py` | HTML report | `seo-audit-YYYY-MM-DD.html` |

### Orchestrator

| Script            | Purpose                      |
| ----------------- | ---------------------------- |
| `run_analysis.py` | Interactive workflow manager |

## API Costs

Uses [DataForSEO](https://dataforseo.com/) API (affordable SEO data):

| Call Type          | Quantity | Estimated Cost | Actual Cost\* |
| ------------------ | -------- | -------------- | ------------- |
| Domain Metrics     | 5        | $0.25          | ~$0.05        |
| Ranked Keywords    | 5        | $2.50          | ~$0.10        |
| Keyword Enrichment | 1        | $0.50          | ~$0.03        |
| Search Intent      | 1        | $0.20          | ~$0.02        |
| SERP Analysis      | 3        | $1.50          | ~$0.02        |
| Backlinks          | 1        | $0.50          | ~$0.01        |
| Keyword Ideas      | 1        | $0.50          | ~$0.01        |
| **TOTAL**          | **17**   | **$6.45**      | **~$0.24**    |

\* _Actual costs are significantly lower than list prices due to DataForSEO's on-demand pricing model. Your actual cost may vary based on data volume returned._

**PageSpeed Insights API** is free from Google (requires API key: set `PAGESPEED_API_KEY` in `.env`).

**Cost of a full run:** DataForSEO (step 2) is the only paid component — roughly **$6.45 list / ~$0.24 actual** per complete analysis. Every other step runs offline or against free APIs: sitemap & social collection, GEO/JSON-LD analysis, performance (free PSI), data export, the site `llms.txt` generator (step 9), WebMCP opportunity analysis (step 10), and the Lighthouse agentic-browsing audit (step 11, runs the local Lighthouse CLI) add **no API cost**. LLM insights (step 5) cost only if you configure a paid `GEMINI_API_KEY`/`OPENROUTER_API_KEY`.

## Report Sections

The generated HTML report includes:

1. **Executive Summary** - Key metrics and opportunities
2. **Sitemap Analysis** - Content structure and freshness
3. **Social Presence** - Platform coverage
4. **High-Opportunity Keywords** - High volume, validated demand
5. **Quick Wins** - Low difficulty opportunities
6. **Content Gaps** - Missing informational content
7. **Product Gaps** - Transactional keyword opportunities
8. **GEO Optimization** - JSON-LD schema recommendations with code
9. **Performance Audit** - Core Web Vitals analysis
10. **Action Items** - 30/60/90-day roadmap

## AI And Agentic Search Readiness

The project tracks current AI search guidance without overclaiming unsupported tactics:

- Google Search's official guidance says core SEO fundamentals remain the foundation for Google generative AI features, including crawlability, indexability, helpful content, and clear technical structure.
- `llms.txt` is included as an optional machine-readable project summary and because Lighthouse's experimental agentic browsing category checks for it. Google Search currently says `llms.txt` and other special AI text files are not required for appearance in generative AI search.
- WebMCP is tracked as an experimental, proposed Chrome capability for exposing structured browser tools to agents. It is most relevant for sites with forms, checkout, booking, dashboards, support flows, or other action-oriented workflows.
- Lighthouse agentic browsing audits are experimental. Treat their output as readiness signals, not a ranking score.

See [docs/AI_READINESS.md](docs/AI_READINESS.md) for implementation guidance and source links.

## Use Cases

### D2C E-commerce

- Identify product keywords competitors rank for
- Find content opportunities (buying guides, comparisons)
- Optimize product pages for transactional keywords
- Improve Core Web Vitals for better mobile shopping experience

### B2B SaaS

- Discover bottom-of-funnel keywords
- Find educational content gaps
- Optimize for commercial intent searches
- GEO optimization for AI-powered search

### B2C Services

- Local SEO opportunities
- Service-specific keyword gaps
- Content marketing ideas
- Technical SEO improvements

## Project Structure

```
seo-aeo-geo-analyzer/
├── config.yaml              # Your configuration
├── .env                     # API credentials
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── run_analysis.py         # Main orchestrator
├── compare_runs.py         # Compare saved run summaries
├── rank_tracker.py         # Create/compare keyword rank snapshots
├── generate_dashboard.py   # Static history dashboard generator
├── collect_data.py         # Sitemap & social scraper
├── dataforseo_collection.py # API automation
├── geo_analyzer.py         # JSON-LD extractor
├── performance_check.py    # PageSpeed analysis
├── generate_report.py      # HTML report generator
└── examples/
    └── configs/            # Example configurations
        ├── d2c-ecommerce.yaml
        ├── saas-b2b.yaml
        └── consumer-app.yaml
```

## Advanced Usage

### Run Individual Components

```bash
# Just sitemap analysis
python collect_data.py

# Just DataForSEO API calls
python dataforseo_collection.py

# Just performance check
python performance_check.py

# Export data to CSV/Excel/PDF
python export_data.py

# Generate report from existing data
python generate_report.py

# Compare latest saved runs
python compare_runs.py --reports-root reports --domain example.com

# Generate keyword rank snapshot for a saved run
python rank_tracker.py --run-dir reports/example-com/20260612_100000

# Generate static dashboard
python generate_dashboard.py --reports-root reports
```

### History And Rank Tracking

Run history is file-based. `scripts/run_scheduled_analysis.py` creates one directory per run under `reports/<domain>/<run_id>/` and writes normalized summary files that can be checked into an artifact store, copied to object storage, or used locally.

Keyword rank tracking uses Google Search Console `top_queries` from `google_data.json`. If Google data is missing, the snapshot is still written with `source_status: "missing"` so dashboards and automation can handle the run safely. DataForSEO gap data is used for opportunity discovery, not as a live rank-tracking source.

### Custom Configuration

```python
# Load custom config file
python run_analysis.py --config my-custom-config.yaml
```

## Maintainer Workflow

Before merging changes:

```bash
python -m pytest -q
```

Security-sensitive changes should include regression tests where possible and should avoid committing generated reports, local `.env` files, API keys, or customer data.

Documentation-sensitive changes should update the relevant user-facing docs in the same PR:

- [CHANGELOG.md](CHANGELOG.md) for notable changes.
- [README.md](README.md) for commands, config, roadmap, and workflow changes.
- [docs/AI_READINESS.md](docs/AI_READINESS.md) for AI search, `llms.txt`, WebMCP, or agentic-browsing behavior.
- [llms.txt](llms.txt) when entry points, test commands, or maintenance policies change.

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with:

- [DataForSEO](https://dataforseo.com/) - SEO data API
- [Google PageSpeed Insights](https://developers.google.com/speed/docs/insights/v5/get-started) - Performance metrics
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [PyYAML](https://pyyaml.org/) - Configuration management

## Support

- **Issues and questions**: [GitHub Issues](https://github.com/usood/seo-aeo-geo-analyzer/issues)
- **Security reports**: see [SECURITY.md](SECURITY.md)

## Roadmap

- [x] Multi-language support for report UI labels
- [x] Export to CSV/Excel/PDF
- [x] Integration with Google Search Console
- [x] Agentic browsing readiness checks
- [x] WebMCP opportunity detection for actionable site flows
- [x] `llms.txt` generator for analyzed websites
- [x] Automated scheduling wrapper and manual GitHub Actions workflow
- [x] Run history summaries and run-to-run comparisons
- [x] Keyword rank tracking snapshots from Google Search Console data
- [x] Static dashboard view for tracking over time
- [ ] Slack/Email notifications
- [ ] Backlink monitoring

---

**Made with ❤️ for SEO professionals and digital marketers**
