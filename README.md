# SEO/AEO/GEO Analyzer 🔍

> Comprehensive SEO, AEO (Answer Engine Optimization), and GEO (Generative Engine Optimization) competitive analysis tool for D2C, B2B, and B2C brands. Identifies keyword opportunities, optimizes for AI search engines, and provides actionable recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- **🎯 Keyword Gap Analysis** - Find 100+ high-value keywords your competitors rank for
- **🤖 GEO (Generative Engine Optimization)** - Optimize for AI search (ChatGPT, Perplexity, Google SGE)
- **⚡ Performance Audit** - Core Web Vitals analysis with PageSpeed Insights
- **📊 Competitive Intelligence** - Domain metrics, backlinks, and SERP analysis
- **📝 Content Opportunities** - Categorized by intent (informational, transactional, commercial)
- **📈 Actionable Roadmap** - 30/60/90-day implementation plan
- **🎨 Beautiful HTML Reports** - Interactive, sortable data tables

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/seo-gap-analyzer.git
cd seo-gap-analyzer

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

## 📋 Configuration

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
```

### Example Configurations

Pre-configured examples for different business types:

- **D2C E-commerce**: `examples/configs/d2c-ecommerce.yaml`
- **B2B SaaS**: `examples/configs/saas-b2b.yaml`
- **Pet Wellness**: `examples/configs/unleash-wellness.yaml`

## 🛠️ Components

### Data Collection Scripts

| Script | Purpose | Output | Time |
|--------|---------|--------|------|
| `collect_data.py` | Sitemap & social analysis | `analysis_data_*.json` | ~30s |
| `dataforseo_collection.py` | Keyword & SERP data | `dataforseo_final_*.json` | ~25min |
| `geo_analyzer.py` | JSON-LD schema extraction | `geo_analysis.json` | ~30s |
| `performance_check.py` | Core Web Vitals | `performance_analysis.json` | ~3min |

### Report Generation

| Script | Purpose | Output |
|--------|---------|--------|
| `generate_report.py` | HTML report | `seo-audit-YYYY-MM-DD.html` |

### Orchestrator

| Script | Purpose |
|--------|---------|
| `run_analysis.py` | Interactive workflow manager |

## 💰 API Costs

Uses [DataForSEO](https://dataforseo.com/) API (affordable SEO data):

| Call Type | Quantity | Estimated Cost | Actual Cost* |
|-----------|----------|----------------|--------------|
| Domain Metrics | 5 | $0.25 | ~$0.05 |
| Ranked Keywords | 5 | $2.50 | ~$0.10 |
| Keyword Enrichment | 1 | $0.50 | ~$0.03 |
| Search Intent | 1 | $0.20 | ~$0.02 |
| SERP Analysis | 3 | $1.50 | ~$0.02 |
| Backlinks | 1 | $0.50 | ~$0.01 |
| Keyword Ideas | 1 | $0.50 | ~$0.01 |
| **TOTAL** | **17** | **$6.45** | **~$0.24** |

\* *Actual costs are significantly lower than list prices due to DataForSEO's on-demand pricing model. Your actual cost may vary based on data volume returned.*

**PageSpeed Insights API** is free from Google (requires API key: set `PAGESPEED_API_KEY` in `.env`).

## 📊 Report Sections

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

## 🎯 Use Cases

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

## 📁 Project Structure

```
seo-gap-analyzer/
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
        └── unleash-wellness.yaml
```

## 🔧 Advanced Usage

### Run Individual Components

```bash
# Just sitemap analysis
python collect_data.py

# Just DataForSEO API calls
python dataforseo_collection.py

# Just performance check
python performance_check.py

# Generate report from existing data
python generate_report.py
```

### Custom Configuration

```python
# Load custom config file
python run_analysis.py --config my-custom-config.yaml
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

Built with:
- [DataForSEO](https://dataforseo.com/) - SEO data API
- [Google PageSpeed Insights](https://developers.google.com/speed/docs/insights/v5/get-started) - Performance metrics
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [PyYAML](https://pyyaml.org/) - Configuration management

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/seo-gap-analyzer/issues)
- **Questions**: [Discussions](https://github.com/yourusername/seo-gap-analyzer/discussions)

## 🗺️ Roadmap

- [ ] Multi-language support for reports
- [ ] Export to CSV/Excel
- [ ] Integration with Google Search Console
- [ ] Automated scheduling (weekly/monthly reports)
- [ ] Slack/Email notifications
- [ ] Dashboard view for tracking over time
- [ ] Keyword rank tracking
- [ ] Backlink monitoring

---

**Made with ❤️ for SEO professionals and digital marketers**
