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
```

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
- [ ] Automated scheduling (weekly/monthly reports)
- [ ] Slack/Email notifications
- [ ] Dashboard view for tracking over time
- [ ] Keyword rank tracking
- [ ] Backlink monitoring

---

**Made with ❤️ for SEO professionals and digital marketers**
