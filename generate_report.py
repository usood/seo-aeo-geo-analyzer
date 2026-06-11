#!/usr/bin/env python3
"""
Generate comprehensive SEO Analysis HTML report
Generates an HTML SEO/AEO/GEO report for the configured target domain.
Includes: Keyword Gaps, GEO, Performance, Content Optimization
Date: December 5, 2025
"""

import json
import glob
import os
from datetime import datetime
from utils.path_manager import get_current_project_path, get_latest_file
from utils.config_loader import load_config # Assuming config_loader is moved to utils
from utils.html_safety import escape_html, safe_css_class, safe_http_url

# ============================================================================
# LOAD DATA FILES
# ============================================================================

print("Loading data files...")

project_dir = get_current_project_path()
print(f"Loading data from project directory: {project_dir}")

# Load sitemap data
sitemap_file = get_latest_file("analysis_data_*.json", project_dir)
if not sitemap_file:
    print("ERROR: Sitemap data not found. Run collect_data.py first.")
    exit(1)

with open(sitemap_file, 'r') as f:
    sitemap_data = json.load(f)
print(f"✓ Loaded: {sitemap_file}")

# Load DataForSEO data
dataforseo_file = get_latest_file("dataforseo_final_*.json", project_dir)
if not dataforseo_file:
    print("ERROR: DataForSEO data not found. Run dataforseo_collection.py first.")
    exit(1)

with open(dataforseo_file, 'r') as f:
    dataforseo_data = json.load(f)
print(f"✓ Loaded: {dataforseo_file}")

# Load GEO analysis
geo_file = os.path.join(project_dir, "geo_analysis.json")
if os.path.exists(geo_file):
    with open(geo_file, 'r') as f:
        geo_data = json.load(f)
    print(f"✓ Loaded: {geo_file}")
else:
    geo_data = None
    print("⚠ GEO analysis not found. Run geo_analyzer.py first.")

# Load Google Integration data
google_file = os.path.join(project_dir, "google_data.json")
if os.path.exists(google_file):
    with open(google_file, 'r') as f:
        google_data = json.load(f)
    print(f"✓ Loaded: {google_file}")
else:
    google_data = None
    print("⚠ Google data not found. Run google_integration.py first.")

# Load LLM Insights
llm_file = os.path.join(project_dir, "llm_insights.json")
if os.path.exists(llm_file):
    with open(llm_file, 'r') as f:
        llm_data = json.load(f)
    print(f"✓ Loaded: {llm_file}")
else:
    llm_data = None
    print("⚠ LLM insights not found. Run llm_runner.py first.")

# Load performance data
perf_file = os.path.join(project_dir, "performance_analysis.json")
if os.path.exists(perf_file):
    with open(perf_file, 'r') as f:
        performance_data = json.load(f)
    print(f"✓ Loaded: {perf_file}")
else:
    performance_data = None
    print("⚠ Performance data not found. Run performance_check.py first.")

# ============================================================================
# PROCESS DATA
# ============================================================================

TARGET_DOMAIN = sitemap_data['metadata']['target_domain']
COMPETITORS = sitemap_data['metadata']['competitors']
COMPANY_NAME = sitemap_data['metadata'].get('company_name', TARGET_DOMAIN.split('.')[0].title())
COMPANY_NAME_HTML = escape_html(COMPANY_NAME)

# Extract gap data from DataForSEO results
gaps = dataforseo_data.get('gaps', {})
top_100_gaps = gaps.get('top_100', [])

# Categorize the top 100 gaps
categorized_gaps = {
    'high_opportunity': [],
    'quick_wins': [],
    'content_gaps': [],
    'product_gaps': []
}

# Load keyword enrichment and intent data for categorization
keyword_enrichment = {item['keyword']: item for item in dataforseo_data.get('keyword_enrichment', [])}
keyword_intent = {item['keyword']: item for item in dataforseo_data.get('search_intent', [])}

for gap in top_100_gaps:
    keyword = gap['keyword']
    search_volume = gap.get('search_volume', 0)
    position = gap.get('competitor_position', 999)

    # Get enrichment data
    enrichment = keyword_enrichment.get(keyword, {})
    intent_data = keyword_intent.get(keyword, {})

    # Add enrichment to gap
    competition = enrichment.get('keyword_info', {}).get('competition') if enrichment else None
    gap['difficulty'] = competition * 100 if competition is not None else 0
    gap['cpc'] = enrichment.get('keyword_info', {}).get('cpc') or 0
    gap['intent'] = intent_data.get('primary_intent', {}).get('intent', 'unknown') if intent_data else 'unknown'

    # Categorize
    # High opportunity: high volume + good competitor position
    if search_volume >= 500 and position <= 10:
        categorized_gaps['high_opportunity'].append(gap)

    # Quick wins: lower difficulty, decent volume
    elif gap.get('difficulty') and gap['difficulty'] < 40 and search_volume >= 100:
        categorized_gaps['quick_wins'].append(gap)

    # Content gaps: informational intent or content keywords
    elif gap['intent'] == 'informational' or any(word in keyword.lower() for word in ['how', 'what', 'best', 'guide', 'tips', 'care']):
        categorized_gaps['content_gaps'].append(gap)

    # Product gaps: transactional or product keywords
    elif gap['intent'] == 'transactional' or any(word in keyword.lower() for word in [
        'buy', 'supplement', 'vitamin', 'product', 'price', 'cost', 'shop', 'store', 
        'online', 'order', 'sale', 'offer', 'deal', 'discount', 'cheap', 'best', 
        'review', 'dog food', 'cat food', 'pet food', 'treats', 'chews', 'shampoo', 
        'oil', 'spray', 'powder', 'tablet', 'medicine'
    ]):
        categorized_gaps['product_gaps'].append(gap)

    # Default to content gaps
    else:
        categorized_gaps['content_gaps'].append(gap)

# Sort each category by search volume
for category in categorized_gaps:
    categorized_gaps[category] = sorted(categorized_gaps[category], key=lambda x: x.get('search_volume', 0), reverse=True)

# ============================================================================
# GENERATE HTML REPORT
# ============================================================================

total_gaps = len(top_100_gaps)
report_date = datetime.now().strftime('%B %d, %Y')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>SEO Analysis Report | {COMPANY_NAME_HTML} | {report_date}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700;800&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        /* ... existing styles ... */
        :root {{
            --primary: #f59e0b;
            --primary-dark: #d97706;
            --dark: #78350f;
            --dark-light: #92400e;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --glass-bg: rgba(255, 255, 255, 0.65);
            --glass-border: rgba(255, 255, 255, 0.4);
            --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            --sidebar-bg: rgba(120, 53, 15, 0.9);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: var(--text-main);
            background: linear-gradient(135deg, #fdfbf7 0%, #fff7ed 50%, #fff1f2 100%);
            background-attachment: fixed;
            min-height: 100vh;
        }}

        /* Glass Components */
        .glass-panel {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            box-shadow: var(--glass-shadow);
            border-radius: 16px;
        }}

        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: var(--sidebar-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.1);
            color: white;
            padding: 30px 0;
            overflow-y: auto;
            z-index: 100;
        }}

        .sidebar-header {{
            padding: 0 25px 30px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }}

        .sidebar-logo {{
            font-size: 1.5em;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .sidebar-subtitle {{
            font-size: 0.85em;
            opacity: 0.7;
            margin-top: 5px;
        }}
        
        /* ... rest of styles ... */
        .nav-section {{
            padding: 0 15px;
            margin-bottom: 25px;
        }}

        .nav-section-title {{
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: rgba(255,255,255,0.4);
            padding: 0 10px;
            margin-bottom: 10px;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            color: rgba(255,255,255,0.8);
            font-size: 0.95em;
            margin-bottom: 4px;
        }}

        .nav-item:hover {{
            background: rgba(255,255,255,0.1);
            color: white;
            transform: translateX(4px);
        }}

        .nav-item.active {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(4px);
        }}

        .nav-icon {{
            font-size: 1.2em;
            width: 24px;
            text-align: center;
        }}

        .nav-badge {{
            margin-left: auto;
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
        }}

        .nav-badge.critical {{
            background: rgba(239, 68, 68, 0.8);
            color: white;
        }}

        .main-content {{
            margin-left: 280px;
            min-height: 100vh;
            padding-bottom: 60px;
        }}

        .header {{
            background: transparent;
            padding: 50px 60px;
        }}

        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .header h1 {{
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 3em;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--dark);
            text-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}

        .header .date {{
            color: var(--text-muted);
            font-weight: 400;
            font-size: 1.1em;
        }}

        .score-card {{
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 24px;
            padding: 25px 35px;
            text-align: center;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1);
            min-width: 200px;
        }}

        .score-label {{
            font-size: 0.8em;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}

        .score-value {{
            font-size: 3.5em;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary) 0%, #ea580c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
            filter: drop-shadow(0 2px 4px rgba(245, 158, 11, 0.2));
        }}

        .score-status {{
            margin-top: 10px;
            font-size: 0.85em;
            color: var(--primary);
            font-weight: 600;
        }}

        .content {{
            padding: 0 60px;
        }}

        .section {{
            display: none;
            animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .section.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .section-title {{
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 2.2em;
            font-weight: 500;
            color: var(--dark);
            margin: 40px 0 30px;
            display: flex;
            align-items: center;
            gap: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            padding: 30px 25px;
            border-radius: 20px;
            box-shadow: var(--glass-shadow);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
            text-shadow: 0 2px 10px rgba(245, 158, 11, 0.1);
        }}

        .stat-label {{
            color: var(--text-muted);
            font-size: 0.95em;
            font-weight: 500;
        }}

        .data-table {{
            width: 100%;
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
            margin-bottom: 30px;
            border-collapse: separate;
            border-spacing: 0;
        }}

        .data-table th {{
            background: rgba(120, 53, 15, 0.9);
            color: white;
            padding: 20px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            cursor: pointer;
            user-select: none;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .data-table th:first-child {{
            padding-left: 30px;
        }}
        
        .data-table th:last-child {{
            padding-right: 30px;
        }}

        .data-table td {{
            padding: 18px 20px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            vertical-align: middle;
            color: var(--text-main);
        }}
        
        .data-table td:first-child {{
            padding-left: 30px;
        }}
        
        .data-table td:last-child {{
            padding-right: 30px;
        }}

        .data-table tr:last-child td {{
            border-bottom: none;
        }}

        .data-table tr:hover td {{
            background: rgba(255,255,255,0.4);
        }}

        .status-pill {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .status-pill.informational {{ background: #dbeafe; color: #1e40af; }}
        .status-pill.transactional {{ background: #d1fae5; color: #065f46; }}
        .status-pill.commercial {{ background: #fef3c7; color: #92400e; }}
        .status-pill.navigational {{ background: #f3f4f6; color: #4b5563; }}
        .status-pill.unknown {{ background: #f3f4f6; color: #6b7280; }}

        .priority-badge {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .priority-badge.critical {{
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}

        .priority-badge.high {{
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            color: #b45309;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}

        .competitor-list {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}

        .competitor-tag {{
            font-size: 0.75em;
            padding: 4px 10px;
            background: rgba(255,255,255,0.5);
            border: 1px solid rgba(0,0,0,0.1);
            border-radius: 8px;
            color: var(--text-muted);
        }}

        .insight-box {{
            background: rgba(255, 251, 235, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-left: 5px solid var(--primary);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.05);
        }}

        .insight-box h3 {{
            color: var(--primary-dark);
            margin-bottom: 10px;
            font-size: 1.1em;
        }}

        .code-block {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 25px;
            border-radius: 12px;
            overflow-x: auto;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.6;
            margin: 20px 0;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .performance-score {{
            display: inline-flex;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2em;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .performance-score.good {{ background: #d1fae5; color: #065f46; }}
        .performance-score.needs-improvement {{ background: #fef3c7; color: #92400e; }}
        .performance-score.poor {{ background: #fee2e2; color: #991b1b; }}

        .social-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .social-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            padding: 25px;
            border-radius: 16px;
            box-shadow: var(--glass-shadow);
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .social-card:hover {{
            transform: translateY(-5px);
            background: rgba(255,255,255,0.8);
        }}

        .social-card.inactive {{
            opacity: 0.6;
            filter: grayscale(0.8);
        }}

        .social-icon {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-logo">🐾 {COMPANY_NAME_HTML}</div>
            <div class="sidebar-subtitle">SEO Analysis Report</div>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Overview</div>
            <a href="#executive-summary" class="nav-item active" data-section="executive-summary">
                <span class="nav-icon">📊</span>
                <span>Executive Summary</span>
            </a>
            <a href="#sitemap" class="nav-item" data-section="sitemap">
                <span class="nav-icon">🗺️</span>
                <span>Sitemap Analysis</span>
            </a>
            <a href="#social" class="nav-item" data-section="social">
                <span class="nav-icon">📱</span>
                <span>Social Presence</span>
            </a>
            <a href="#local-intl" class="nav-item" data-section="local-intl">
                <span class="nav-icon">🌍</span>
                <span>Local & Intl SEO</span>
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Keyword Gaps</div>
            <a href="#high-opportunity" class="nav-item" data-section="high-opportunity">
                <span class="nav-icon">🎯</span>
                <span>High-Opportunity</span>
                <span class="nav-badge critical">{len(categorized_gaps['high_opportunity'])}</span>
            </a>
            <a href="#quick-wins" class="nav-item" data-section="quick-wins">
                <span class="nav-icon">⚡</span>
                <span>Quick Wins</span>
                <span class="nav-badge">{len(categorized_gaps['quick_wins'])}</span>
            </a>
            <a href="#content-gaps" class="nav-item" data-section="content-gaps">
                <span class="nav-icon">📝</span>
                <span>Content Gaps</span>
                <span class="nav-badge">{len(categorized_gaps['content_gaps'])}</span>
            </a>
            <a href="#product-gaps" class="nav-item" data-section="product-gaps">
                <span class="nav-icon">🛒</span>
                <span>Product Gaps</span>
                <span class="nav-badge">{len(categorized_gaps['product_gaps'])}</span>
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Technical SEO</div>
            <a href="#geo" class="nav-item" data-section="geo">
                <span class="nav-icon">🤖</span>
                <span>GEO (AI Visibility)</span>
            </a>
            <a href="#google-data" class="nav-item" data-section="google-data">
                <span class="nav-icon">📈</span>
                <span>Google Search & GA4</span>
            </a>
            <a href="#performance" class="nav-item" data-section="performance">
                <span class="nav-icon">⚡</span>
                <span>Performance</span>
            </a>
        </div>
    </nav>

    <main class="main-content">
        <header class="header">
            <div class="header-top">
                <div>
                    <h1>SEO Analysis Report</h1>
                    <p class="date">{COMPANY_NAME_HTML} • {report_date} • India Market</p>
                </div>
                <div class="score-card">
                    <div class="score-label">Total Opportunities</div>
                    <div class="score-value">{total_gaps}</div>
                    <div class="score-status">Keyword Gaps Found</div>
                </div>
            </div>
        </header>

        <div class="content">
            <!-- Executive Summary -->
            <section id="executive-summary" class="section active">
                <h2 class="section-title"><span class="icon">📊</span> Executive Summary</h2>

                <div class="insight-box">
                    <h3>🎯 Key Finding</h3>
                    <p>{COMPANY_NAME_HTML} has <strong>significant growth opportunities</strong> in organic search. Competitors are ranking for {total_gaps} high-value keywords where you currently have limited or no presence.</p>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{sitemap_data['sitemap_analysis'][TARGET_DOMAIN]['total_urls']}</div>
                        <div class="stat-label">Indexed Pages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_gaps}</div>
                        <div class="stat-label">Keyword Opportunities</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(categorized_gaps['high_opportunity'])}</div>
                        <div class="stat-label">High-Priority Gaps</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(COMPETITORS)}</div>
                        <div class="stat-label">Competitors Analyzed</div>
                    </div>
                </div>

"""
# LLM Strategic Analysis Integration (Moved to bottom of Exec Summary)
html += f"""
                <h3 style="margin-bottom: 20px; color: var(--dark);">Gap Distribution</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" style="color: var(--danger);">{len(categorized_gaps['high_opportunity'])}</div>
                        <div class="stat-label">High-Opportunity Keywords</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: var(--warning);">{len(categorized_gaps['quick_wins'])}</div>
                        <div class="stat-label">Quick Win Opportunities</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: var(--primary);">{len(categorized_gaps['content_gaps'])}</div>
                        <div class="stat-label">Content Gaps</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #3b82f6;">{len(categorized_gaps['product_gaps'])}</div>
                        <div class="stat-label">Product/Transactional Gaps</div>
                    </div>
                </div>

                <!-- Focused Action Plan -->
                <div style="background: white; border-radius: 16px; padding: 30px; margin-top: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                    <h3 style="display: flex; align-items: center; gap: 10px; margin-bottom: 25px; font-size: 1.4em;">
                        <span style="font-size: 1.2em;">🚀</span> Focused Action Plan
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                        <!-- Top 5 Keywords -->
                        <div>
                            <h4 style="margin-bottom: 15px; color: var(--primary); text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;">Top 5 Keywords to Target</h4>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
"""
for kw in categorized_gaps['high_opportunity'][:5]:
    keyword_html = escape_html(kw.get('keyword', ''))
    intent = kw.get('intent', 'unknown')
    intent_class = safe_css_class(intent)
    intent_html = escape_html(str(intent).title())
    search_volume = kw.get('search_volume', 0)
    try:
        search_volume_html = escape_html(f"{int(search_volume):,}")
    except (TypeError, ValueError):
        search_volume_html = escape_html(search_volume)
    try:
        difficulty_html = escape_html(int(kw.get('difficulty', 0)))
    except (TypeError, ValueError):
        difficulty_html = escape_html(kw.get('difficulty', 0))
    html += f"""                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: var(--gray-50); border-radius: 8px; border-left: 4px solid var(--primary);">
                                    <div style="min-width: 0;">
                                        <div style="font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{keyword_html}</div>
                                        <div style="font-size: 0.8em; color: var(--gray-600);">{search_volume_html}/mo • Diff: {difficulty_html}</div>
                                    </div>
                                    <span class="status-pill {intent_class}" style="margin-left: 10px;">{intent_html}</span>
                                </div>"""
html += """                            </div>
                        </div>

                        <!-- Top 5 Page Fixes -->
                        <div>
                            <h4 style="margin-bottom: 15px; color: var(--danger); text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;">Top 5 Pages to Fix</h4>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
"""
if google_data and google_data.get('gsc', {}).get('optimization_needed'):
    for p in google_data['gsc']['optimization_needed'][:5]:
        url = p.get('url', '')
        url_path = url.replace('https://', '').replace('http://', '').split('/', 1)[-1]
        
        # Determine advice
        reason = p.get('reason', '')
        if 'CTR' in reason:
            advice = "✍️ Rewrite Title/Meta & Add Schema"
        elif 'Striking' in reason:
            advice = "🔗 Add Internal Links & Expand Content"
        else:
            advice = "🔍 Review User Intent"
            
        url_html = escape_html(url)
        url_path_html = escape_html(url_path)
        reason_html = escape_html(reason)
        metric_html = escape_html(p.get('metric', ''))
        advice_html = escape_html(advice)
        html += f"""                                <div style="display: flex; justify-content: space-between; align-items: flex-start; padding: 12px; background: #fef2f2; border-radius: 8px; border-left: 4px solid var(--danger);">
                                    <div style="flex: 1; min-width: 0; margin-right: 15px;">
                                        <div style="font-weight: 600; word-break: break-all; line-height: 1.3; margin-bottom: 4px; color: var(--dark);" title="{url_html}">/{url_path_html}</div>
                                        <div style="font-size: 0.8em; color: var(--gray-600); margin-bottom: 2px;">{reason_html}</div>
                                        <div style="font-size: 0.75em; color: var(--dark); font-weight: 600;">{advice_html}</div>
                                    </div>
                                    <span style="font-size: 0.8em; font-weight: 600; color: var(--danger); white-space: nowrap; margin-top: 2px;">{metric_html}</span>
                                </div>"""
else:
    html += """<div style="padding: 20px; text-align: center; color: var(--gray-600); background: var(--gray-50); border-radius: 8px;">No urgent fixes detected via GSC.</div>"""

html += """                            </div>
                        </div>
                    </div>
                </div>

"""
# AI Strategic Analysis (New Location & Format)
if llm_data and 'holistic_strategy' in llm_data:
    strategy = llm_data['holistic_strategy']
    
    # Handle errors or text-only response
    if 'error' in strategy:
        strategy_content = f"<p style='color: var(--danger);'>{escape_html(strategy['error'])}</p>"
    elif 'text_response' in strategy:
        strategy_content = f"<div style='white-space: pre-wrap;'>{escape_html(strategy['text_response'][:1000])}...</div>"
    else:
        # Pillars
        pillars = strategy.get('pillars', {})
        content_pillar = "".join([f"<li style='margin-bottom: 5px;'>{escape_html(item)}</li>" for item in pillars.get('content', [])])
        tech_pillar = "".join([f"<li style='margin-bottom: 5px;'>{escape_html(item)}</li>" for item in pillars.get('technical', [])])
        auth_pillar = "".join([f"<li style='margin-bottom: 5px;'>{escape_html(item)}</li>" for item in pillars.get('authority', [])])
        
        # Quick Wins
        quick_wins = "".join([f"<span style='background: rgba(255,255,255,0.5); padding: 4px 8px; border-radius: 4px; font-size: 0.85em;'>⚡ {escape_html(item)}</span>" for item in strategy.get('quick_wins', [])])

        strategy_content = f"""
            <div style="margin-bottom: 25px;">
                <h4 style="color: var(--primary-dark); margin-bottom: 10px; font-size: 1.1em;">Strategic Executive Summary</h4>
                <p style="font-size: 1em; line-height: 1.6; color: var(--gray-800); background: rgba(255,255,255,0.5); padding: 15px; border-radius: 8px; border-left: 4px solid var(--primary);">
                    {escape_html(strategy.get('executive_summary', 'No summary available.'))}
                </p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <!-- Content Pillar -->
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h5 style="color: var(--dark); margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2em;">📝</span> Content
                    </h5>
                    <ul style="padding-left: 20px; font-size: 0.9em; color: var(--gray-700);">
                        {content_pillar}
                    </ul>
                </div>

                <!-- Technical Pillar -->
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h5 style="color: var(--dark); margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2em;">⚙️</span> Technical
                    </h5>
                    <ul style="padding-left: 20px; font-size: 0.9em; color: var(--gray-700);">
                        {tech_pillar}
                    </ul>
                </div>

                <!-- Authority Pillar -->
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h5 style="color: var(--dark); margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2em;">🔗</span> Authority
                    </h5>
                    <ul style="padding-left: 20px; font-size: 0.9em; color: var(--gray-700);">
                        {auth_pillar}
                    </ul>
                </div>
            </div>
            
            <div>
                <h4 style="font-size: 0.9em; color: var(--gray-600); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">Quick Wins</h4>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    {quick_wins}
                </div>
            </div>
        """

    html += f"""
                <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-radius: 16px; padding: 30px; margin-top: 40px; border: 1px solid rgba(245, 158, 11, 0.3);">
                    <h3 style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; color: var(--dark);">
                        <span style="font-size: 1.4em;">🧠</span> AI Strategic Roadmap
                    </h3>
                    {strategy_content}
                </div>
"""

# Append Roadmap to Executive Summary (Merged Recommendations)
html += f"""
                <div style="margin-top: 50px; border-top: 1px solid var(--neutral-200); padding-top: 40px;">
                    <h2 style="color: var(--dark); margin-bottom: 30px; font-size: 1.8em;">📋 Implementation Roadmap</h2>

                    <h3 style="margin-bottom: 20px; font-size: 1.2em; color: var(--primary-dark);">30-Day Quick Wins</h3>
                    <div class="stats-grid" style="grid-template-columns: 1fr; margin-bottom: 30px;">
                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Week 1-2: Technical SEO Foundation</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>✅ Add Product schema to all product pages</li>
                                <li>✅ Implement Organization schema on homepage</li>
                                <li>✅ Optimize top 5 product images (WebP, lazy loading)</li>
                                <li>✅ Fix Core Web Vitals issues (target LCP < 2.5s)</li>
                            </ul>
                        </div>

                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Week 3-4: Content Creation</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>📝 Create blog posts for top 5 Quick Win keywords</li>
                                <li>📝 Optimize existing product descriptions with target keywords</li>
                                <li>📝 Add FAQ schema to product pages</li>
                                <li>📝 Create collection pages for high-volume categories</li>
                            </ul>
                        </div>
                    </div>

                    <h3 style="margin: 40px 0 20px; font-size: 1.2em; color: var(--primary-dark);">60-Day Growth Strategy</h3>
                    <div class="stats-grid" style="grid-template-columns: 1fr; margin-bottom: 30px;">
                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Content Expansion</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>📖 Create {min(10, len(categorized_gaps['content_gaps']))} educational blog posts from Content Gaps</li>
                                <li>📖 Develop comprehensive guides for top-performing keywords</li>
                                <li>📖 Add Article schema to all blog posts</li>
                                <li>📖 Internal linking strategy between blog posts and products</li>
                            </ul>
                        </div>

                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Product Optimization</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>🛒 Optimize {min(15, len(categorized_gaps['product_gaps']))} product pages for Product Gap keywords</li>
                                <li>🛒 Add customer reviews with Review schema</li>
                                <li>🛒 Create product comparison pages</li>
                                <li>🛒 Implement breadcrumb navigation with schema</li>
                            </ul>
                        </div>
                    </div>

                    <h3 style="margin: 40px 0 20px; font-size: 1.2em; color: var(--primary-dark);">90-Day Advanced Tactics</h3>
                    <div class="stats-grid" style="grid-template-columns: 1fr; margin-bottom: 30px;">
                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Link Building & Authority</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>🔗 Guest post on pet wellness blogs (target: 5 quality backlinks)</li>
                                <li>🔗 Partner with pet influencers for product reviews</li>
                                <li>🔗 Submit to pet industry directories</li>
                                <li>🔗 Create linkable assets (infographics, research data)</li>
                            </ul>
                        </div>

                        <div class="stat-card" style="text-align: left;">
                            <h4 style="color: var(--primary); margin-bottom: 15px;">Advanced GEO & AI Optimization</h4>
                            <ul style="line-height: 2; color: var(--gray-700);">
                                <li>🤖 Implement HowTo schema for care guides</li>
                                <li>🤖 Add VideoObject schema for product videos</li>
                                <li>🤖 Create comprehensive FAQ pages with FAQPage schema</li>
                                <li>🤖 Monitor AI tool citations (ChatGPT, Perplexity)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>
"""

# Sitemap section
site_data = sitemap_data['sitemap_analysis'].get(TARGET_DOMAIN, {})
cat_data = site_data.get('categorization', {'product': 0, 'content': 0, 'category': 0, 'static': 0})
fresh_data = site_data.get('freshness', {'freshness_percentage': 0})
total_urls = site_data.get('total_urls', 0)

html += f"""
            <!-- Sitemap Analysis -->
            <section id="sitemap" class="section">
                <h2 class="section-title"><span class="icon">🗺️</span> Sitemap Analysis</h2>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total_urls}</div>
                        <div class="stat-label">Total URLs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{cat_data['product']}</div>
                        <div class="stat-label">Product Pages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{cat_data['content']}</div>
                        <div class="stat-label">Blog/Content Pages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{f"{fresh_data['freshness_percentage']}%" if fresh_data.get('freshness_percentage') is not None else '<span style="font-size:0.6em">N/A</span>'}</div>
                        <div class="stat-label">Content Freshness (90d)</div>
                    </div>
                </div>

                <h3 style="margin: 30px 0 20px;">Page Type Distribution</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Page Type</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Product Pages</strong></td>
                            <td>{cat_data['product']}</td>
                            <td>{round(cat_data['product'] / total_urls * 100, 1) if total_urls > 0 else 0}%</td>
                        </tr>
                        <tr>
                            <td><strong>Collections/Categories</strong></td>
                            <td>{cat_data['category']}</td>
                            <td>{round(cat_data['category'] / total_urls * 100, 1) if total_urls > 0 else 0}%</td>
                        </tr>
                        <tr>
                            <td><strong>Blog/Content</strong></td>
                            <td>{cat_data['content']}</td>
                            <td>{round(cat_data['content'] / total_urls * 100, 1) if total_urls > 0 else 0}%</td>
                        </tr>
                        <tr>
                            <td><strong>Static Pages</strong></td>
                            <td>{cat_data['static']}</td>
                            <td>{round(cat_data['static'] / total_urls * 100, 1) if total_urls > 0 else 0}%</td>
                        </tr>
                    </tbody>
                </table>

                <div class="insight-box" style="margin-top: 20px;">
                    <h3>💡 Insight</h3>
                    <p>
                        {f"Content freshness is at <strong>{fresh_data['freshness_percentage']}%</strong> for the past 90 days." if fresh_data.get('freshness_percentage') is not None else "<strong>Content freshness could not be calculated</strong> because your sitemap does not provide 'lastmod' dates."} 
                        Regular content updates signal to search engines that your site is active and relevant. 
                        {"" if fresh_data.get('freshness_percentage') is not None else "Consider enabling 'lastmod' in your sitemap generator."}
                    </p>
                </div>
            </section>
"""

# Social presence section
social_profiles = sitemap_data['social_profiles'][TARGET_DOMAIN]
social_platforms = {
    'facebook': {'name': 'Facebook', 'icon': '📘'},
    'instagram': {'name': 'Instagram', 'icon': '📷'},
    'twitter': {'name': 'Twitter/X', 'icon': '🐦'},
    'youtube': {'name': 'YouTube', 'icon': '📹'},
    'linkedin': {'name': 'LinkedIn', 'icon': '💼'},
    'pinterest': {'name': 'Pinterest', 'icon': '📌'},
    'reddit': {'name': 'Reddit', 'icon': '🤖'},
}

html += """
            <!-- Social Presence -->
            <section id="social" class="section">
                <h2 class="section-title"><span class="icon">📱</span> Social Media Presence</h2>

                <div class="social-grid">
"""

for platform, info in social_platforms.items():
    is_active = social_profiles.get(platform, {}).get('found', False)
    profile_url = social_profiles.get(platform, {}).get('url', '')

    status_class = '' if is_active else 'inactive'
    status_text = '✅ Active' if is_active else '❌ Not Found'

    html += f"""                    <div class="social-card {status_class}">
                        <div class="social-icon">{info['icon']}</div>
                        <div style="font-weight: 600; margin-bottom: 5px;">{info['name']}</div>
                        <div style="font-size: 0.85em; color: var(--gray-600);">{status_text}</div>
"""
    if is_active and profile_url:
        profile_url_html = safe_http_url(profile_url)
        if profile_url_html:
            html += f"""                        <a href="{profile_url_html}" target="_blank" rel="noopener noreferrer" style="font-size: 0.75em; color: var(--primary); margin-top: 5px; display: inline-block;">View Profile</a>
"""
    html += """                    </div>
"""

active_count = sum(1 for p in social_profiles.values() if p.get('found', False))

html += f"""                </div>

                <div class="insight-box">
                    <h3>📊 Social Media Recommendation</h3>
                    <p><strong>Active Platforms:</strong> {active_count} of {len(social_platforms)}</p>
                    <p style="margin-top: 10px;">Social signals can indirectly impact SEO through brand awareness and traffic. Consider expanding presence on platforms where pet owners are active, especially Instagram and YouTube for visual content showcasing pet wellness products.</p>
                </div>
            </section>
"""

# Local & International SEO Section
local_intl = sitemap_data.get('local_international', {}).get(TARGET_DOMAIN, {})
intl_data = local_intl.get('international', {'hreflang_tags': [], 'has_intl_signals': False})
local_data = local_intl.get('local', {'phone_found': False, 'address_found': False, 'has_local_signals': False})

html += f"""
            <!-- Local & International SEO -->
            <section id="local-intl" class="section">
                <h2 class="section-title"><span class="icon">🌍</span> Local & International SEO</h2>

                <div class="stats-grid" style="grid-template-columns: 1fr 1fr;">
                    <!-- International SEO -->
                    <div class="stat-card" style="text-align: left;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="font-size: 1.2em; margin: 0;">🌐 International SEO</h3>
                            <span class="status-pill {'transactional' if intl_data['has_intl_signals'] else 'unknown'}">
                                {'✅ Active' if intl_data['has_intl_signals'] else '⚪ Not Detected'}
                            </span>
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>Hreflang Tags:</strong>
                            <span style="color: var(--gray-600);">{len(intl_data['hreflang_tags'])} found</span>
                        </div>
"""
if intl_data['hreflang_tags']:
    html += """                        <div style="background: var(--gray-100); padding: 10px; border-radius: 8px; font-size: 0.85em; margin-bottom: 15px;">"""
    for tag in intl_data['hreflang_tags'][:3]:
        lang_html = escape_html(tag.get('lang', ''))
        url_html = escape_html(tag.get('url', ''))
        html += f"""<div>{lang_html}: {url_html}</div>"""
    if len(intl_data['hreflang_tags']) > 3:
        html += f"""<div>...and {len(intl_data['hreflang_tags']) - 3} more</div>"""
    html += """</div>"""
else:
    html += """                        <p style="font-size: 0.9em; color: var(--gray-600); margin-bottom: 15px;">
                            No hreflang tags found. If you target multiple countries or languages, use hreflang to tell Google which version to show.
                        </p>
"""
html += f"""
                        <div class="insight-box" style="margin-top: auto; margin-bottom: 0; padding: 15px;">
                            <h4 style="font-size: 0.9em; margin-bottom: 5px;">Recommendation</h4>
                            <p style="font-size: 0.85em;">{'Monitor hreflang for errors in Search Console.' if intl_data['has_intl_signals'] else 'If expanding globally, implement hreflang tags for each region/language variant.'}</p>
                        </div>
                    </div>

                    <!-- Local SEO -->
                    <div class="stat-card" style="text-align: left;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="font-size: 1.2em; margin: 0;">📍 Local SEO</h3>
                            <span class="status-pill {'transactional' if local_data['has_local_signals'] else 'unknown'}">
                                {'✅ Active' if local_data['has_local_signals'] else '⚪ Basic'}
                            </span>
                        </div>

                        <ul style="list-style: none; margin-bottom: 20px;">
                            <li style="margin-bottom: 10px;">
                                {'✅' if local_data['phone_found'] else '❌'} <strong>Phone Number</strong> 
                                <span style="font-size: 0.85em; color: var(--gray-600);">(homepage)</span>
                            </li>
                            <li style="margin-bottom: 10px;">
                                {'✅' if local_data['address_found'] else '❌'} <strong>Address/Location</strong> 
                                <span style="font-size: 0.85em; color: var(--gray-600);">(homepage text)</span>
                            </li>
                            <li style="margin-bottom: 10px;">
                                {'✅' if local_data.get('map_embed') else '❌'} <strong>Google Map Embed</strong>
                            </li>
                        </ul>

                        <div class="insight-box" style="margin-top: auto; margin-bottom: 0; padding: 15px;">
                            <h4 style="font-size: 0.9em; margin-bottom: 5px;">Recommendation</h4>
                            <p style="font-size: 0.85em;">{'Ensure NAP (Name, Address, Phone) is consistent across all directories.' if local_data['has_local_signals'] else 'Add your physical address and phone number to the footer for better local ranking signals.'}</p>
                        </div>
                    </div>
                </div>
            </section>
"""

# High-opportunity keywords section
html += f"""
            <!-- High-Opportunity Keywords -->
            <section id="high-opportunity" class="section">
                <h2 class="section-title"><span class="icon">🎯</span> High-Opportunity Keywords</h2>

                <div class="insight-box">
                    <h3>What are High-Opportunity Keywords?</h3>
                    <p>Keywords with <strong>high search volume (500+/month)</strong> where competitors are ranking well (top 10). These represent validated demand and clear opportunities for traffic growth.</p>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(this, 0)">Keyword</th>
                            <th onclick="sortTable(this, 1)">Search Volume</th>
                            <th onclick="sortTable(this, 2)">Difficulty</th>
                            <th onclick="sortTable(this, 3)">Intent</th>
                            <th>Competitor</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for kw in categorized_gaps['high_opportunity'][:25]:
    difficulty = kw.get('difficulty', 'N/A')
    difficulty_display = f"{int(difficulty)}" if isinstance(difficulty, (int, float)) else 'N/A'
    difficulty_value_html = escape_html(difficulty if isinstance(difficulty, (int, float)) else 0)
    search_volume = kw.get('search_volume', 0)
    search_volume_value = search_volume if isinstance(search_volume, (int, float)) else 0
    search_volume_html = escape_html(search_volume)

    keyword_html = escape_html(kw.get('keyword', ''))
    intent = kw.get('intent', 'unknown')
    intent_class = safe_css_class(intent)
    intent_html = escape_html(str(intent).title())
    comp_name = escape_html(kw.get('competitor', '').split('.')[0].title())
    comp_pos = escape_html(kw.get('competitor_position', '?'))

    priority = 'critical' if search_volume_value >= 1000 else 'high'
    priority_text = 'CRITICAL' if priority == 'critical' else 'HIGH'

    html += f"""                        <tr>
                            <td><strong>{keyword_html}</strong></td>
                            <td data-value="{search_volume_value}">{search_volume_html}/mo</td>
                            <td data-value="{difficulty_value_html}">{difficulty_display}</td>
                            <td><span class="status-pill {intent_class}">{intent_html}</span></td>
                            <td><span class="competitor-tag">#{comp_pos} {comp_name}</span></td>
                            <td><span class="priority-badge {priority}">{priority_text}</span></td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </section>
"""

# Quick Wins section
html += f"""
            <!-- Quick Wins -->
            <section id="quick-wins" class="section">
                <h2 class="section-title"><span class="icon">⚡</span> Quick Win Opportunities</h2>

                <div class="insight-box">
                    <h3>What are Quick Wins?</h3>
                    <p>Keywords with <strong>lower difficulty (< 40)</strong> and decent search volume (100+). These represent opportunities where you could rank faster with targeted content.</p>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(this, 0)">Keyword</th>
                            <th onclick="sortTable(this, 1)">Search Volume</th>
                            <th onclick="sortTable(this, 2)">Difficulty</th>
                            <th onclick="sortTable(this, 3)">Intent</th>
                            <th>Suggested Action</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for kw in categorized_gaps['quick_wins'][:25]:
    difficulty = kw.get('difficulty', 'N/A')
    difficulty_display = f"{int(difficulty)}" if isinstance(difficulty, (int, float)) else 'N/A'
    difficulty_value_html = escape_html(difficulty if isinstance(difficulty, (int, float)) else 0)
    search_volume = kw.get('search_volume', 0)
    search_volume_value = search_volume if isinstance(search_volume, (int, float)) else 0
    search_volume_html = escape_html(search_volume)
    keyword_html = escape_html(kw.get('keyword', ''))
    intent = kw.get('intent', 'unknown')
    intent_class = safe_css_class(intent)
    intent_html = escape_html(str(intent).title())

    # Suggest action based on intent
    if intent == 'informational':
        action = 'Create blog post'
    elif intent == 'transactional':
        action = 'Optimize product page'
    elif intent == 'commercial':
        action = 'Create comparison page'
    else:
        action = 'Create targeted content'

    html += f"""                        <tr>
                            <td><strong>{keyword_html}</strong></td>
                            <td data-value="{search_volume_value}">{search_volume_html}/mo</td>
                            <td data-value="{difficulty_value_html}"><span class="status-pill" style="background: #d1fae5; color: #065f46;">{difficulty_display}</span></td>
                            <td><span class="status-pill {intent_class}">{intent_html}</span></td>
                            <td>{action}</td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </section>
"""

# Content Gaps section
html += f"""
            <!-- Content Gaps -->
            <section id="content-gaps" class="section">
                <h2 class="section-title"><span class="icon">📝</span> Content Gap Opportunities</h2>

                <div class="insight-box">
                    <h3>What are Content Gaps?</h3>
                    <p>Keywords indicating <strong>informational content needs</strong> - guides, tips, care instructions, etc. These suggest blog posts or educational pages that competitors have but you're missing.</p>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(this, 0)">Keyword</th>
                            <th onclick="sortTable(this, 1)">Search Volume</th>
                            <th>Content Type Suggested</th>
                            <th>Intent</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for kw in categorized_gaps['content_gaps'][:30]:
    keyword = kw.get('keyword', '')
    keyword_html = escape_html(keyword)
    search_volume = kw.get('search_volume', 0)
    search_volume_value = search_volume if isinstance(search_volume, (int, float)) else 0
    search_volume_html = escape_html(search_volume)
    keyword_lower = keyword.lower()
    intent = kw.get('intent', 'unknown')
    intent_class = safe_css_class(intent)
    intent_html = escape_html(str(intent).title())

    # Suggest content type
    if 'how' in keyword_lower or 'tips' in keyword_lower:
        content_type = '📖 How-To Guide'
    elif 'best' in keyword_lower or 'top' in keyword_lower:
        content_type = '🏆 Listicle/Roundup'
    elif 'care' in keyword_lower or 'health' in keyword_lower:
        content_type = '🏥 Care Guide'
    elif 'guide' in keyword_lower:
        content_type = '📚 Comprehensive Guide'
    else:
        content_type = '✍️ Blog Post'

    html += f"""                        <tr>
                            <td><strong>{keyword_html}</strong></td>
                            <td data-value="{search_volume_value}">{search_volume_html}/mo</td>
                            <td>{content_type}</td>
                            <td><span class="status-pill {intent_class}">{intent_html}</span></td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </section>
"""

# Product Gaps section
html += f"""
            <!-- Product Gaps -->
            <section id="product-gaps" class="section">
                <h2 class="section-title"><span class="icon">🛒</span> Product/Transactional Keywords</h2>

                <div class="insight-box">
                    <h3>What are Product Gaps?</h3>
                    <p>Keywords with <strong>transactional intent</strong> or product-related terms. These suggest product pages or categories that need optimization or creation.</p>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(this, 0)">Keyword</th>
                            <th onclick="sortTable(this, 1)">Search Volume</th>
                            <th onclick="sortTable(this, 2)">CPC</th>
                            <th>Commercial Value</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for kw in categorized_gaps['product_gaps'][:20]:
    cpc = kw.get('cpc', 0)
    commercial_value = 'High' if cpc > 20 else ('Medium' if cpc > 10 else 'Low')
    keyword = kw.get('keyword', '')
    keyword_html = escape_html(keyword)
    search_volume = kw.get('search_volume', 0)
    search_volume_value = search_volume if isinstance(search_volume, (int, float)) else 0
    search_volume_html = escape_html(search_volume)

    # Suggest action
    if 'buy' in keyword.lower():
        action = 'Optimize product page'
    elif 'supplement' in keyword.lower() or 'vitamin' in keyword.lower():
        action = 'Create/optimize product'
    else:
        action = 'Review product category'

    html += f"""                        <tr>
                            <td><strong>{keyword_html}</strong></td>
                            <td data-value="{search_volume_value}">{search_volume_html}/mo</td>
                            <td data-value="{cpc}">₹{cpc:.2f}</td>
                            <td><span class="status-pill" style="background: {'#d1fae5' if commercial_value == 'High' else '#fef3c7'}; color: {'#065f46' if commercial_value == 'High' else '#92400e'};">{commercial_value}</span></td>
                            <td>{action}</td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </section>
"""

# GEO Section
if geo_data:
    html += """
            <!-- GEO (Generative Engine Optimization) -->
            <section id="geo" class="section">
                <h2 class="section-title"><span class="icon">🤖</span> GEO - AI Visibility Optimization</h2>

                <div class="insight-box">
                    <h3>What is GEO?</h3>
                    <p><strong>Generative Engine Optimization</strong> helps your content work well in AI search experiences such as ChatGPT, Perplexity, Google AI Overviews, and Google AI Mode. This involves clear content structure, valid structured data where useful, and AEO signals that help systems understand and cite your content.</p>
                </div>

                <h3 style="margin: 30px 0 20px;">Current JSON-LD Schema Status</h3>
"""

    # Analyze GEO data
    page_types = ['homepage', 'product', 'collection', 'blog']
    for page_type in page_types:
        if page_type in geo_data:
            data = geo_data[page_type]
            if 'error' in data:
                continue
                
            schemas = data.get('schemas', [])
            aeo = data.get('aeo_signals', {})
            
            page_name = escape_html(page_type.title())
            
            # Format schema list
            schema_types = [s.get('type', '') for s in schemas]
            schema_list = escape_html(', '.join(set(schema_types)) if schema_types else 'None found')
            
            # Determine status
            issues_count = sum(len(s.get('issues', [])) for s in schemas)
            if not schemas:
                status = '❌ Missing'
            elif issues_count > 0:
                status = '⚠️ Issues'
            else:
                status = '✅ Good'

            html += f"""
                <div class="stat-card" style="text-align: left; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; font-size: 1.1em; margin-bottom: 5px;">{page_name}</div>
                            <div style="font-size: 0.9em; color: var(--gray-600);">Schemas: {schema_list}</div>
"""
            # Show specific issues
            for s in schemas:
                issues = s.get('issues', [])
                if issues:
                    schema_type_html = escape_html(s.get('type', ''))
                    issues_html = escape_html(', '.join(str(issue) for issue in issues))
                    html += f"""                            <div style="font-size: 0.85em; color: var(--danger); margin-top: 2px;">⚠️ {schema_type_html}: {issues_html}</div>"""
            
            # Show AEO signals
            if aeo:
                aeo_text = []
                if aeo.get('has_toc'): aeo_text.append("✅ TOC Found")
                if aeo.get('short_paragraphs', 0) > 2: aeo_text.append("✅ Concise Answers")
                if aeo.get('structure_depth', 0) >= 2: aeo_text.append("✅ Good Structure")
                
                if aeo_text:
                    html += f"""                            <div style="font-size: 0.85em; color: var(--primary); margin-top: 5px;">🤖 AEO Signals: {', '.join(aeo_text)}</div>"""

            html += f"""                        </div>
                        <div style="font-size: 1.5em;">{status}</div>
                    </div>
                </div>
"""

    html += """
                <h3 style="margin: 40px 0 20px;">Recommended Schema Enhancements</h3>

                <div class="insight-box">
                    <h3>📋 Product Pages</h3>
                    <p><strong>Add:</strong> Product, Offers, Review, AggregateRating schemas</p>
                    <p><strong>Why:</strong> AI tools can extract pricing, availability, and review data to answer user queries like "best dog supplements in India"</p>
                </div>

                <div class="code-block">
&lt;script type="application/ld+json"&gt;
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "brand": {
    "@type": "Brand",
    "name": "{COMPANY_NAME_HTML}"
  },
  "offers": {
    "@type": "Offer",
    "price": "999",
    "priceCurrency": "INR",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "24"
  }
}
&lt;/script&gt;
                </div>

                <div class="insight-box">
                    <h3>📝 Blog Posts</h3>
                    <p><strong>Add:</strong> Article, HowTo, FAQPage schemas</p>
                    <p><strong>Why:</strong> Structured content helps AI extract step-by-step instructions and frequently asked questions</p>
                </div>

                <div class="code-block">
&lt;script type="application/ld+json"&gt;
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Care for Your Dog's Joint Health",
  "author": {
    "@type": "Organization",
    "name": "{COMPANY_NAME_HTML}"
  },
  "datePublished": "2025-12-05",
  "articleBody": "Full article text..."
}
&lt;/script&gt;
                </div>

                <div class="insight-box">
                    <h3>🏢 Organization Schema</h3>
                    <p><strong>Add:</strong> Organization, LocalBusiness schemas on homepage</p>
                    <p><strong>Why:</strong> Establishes brand identity and contact information for AI assistants</p>
                </div>
            </section>
"""

# Google Data Section
if google_data and google_data.get('status') == 'success':
    gsc = google_data.get('gsc', {})
    ga4 = google_data.get('ga4', {})
    
    # Safely get totals
    totals = gsc.get('totals', {})
    total_clicks = totals.get('clicks', 0)
    clicks_growth = totals.get('clicks_growth', 0)
    total_impressions = totals.get('impressions', 0)
    impressions_growth = totals.get('impressions_growth', 0)
    
    html += f"""
            <!-- Google Data -->
            <section id="google-data" class="section">
                <h2 class="section-title"><span class="icon">📈</span> Google Search & Analytics</h2>
                
                <!-- Growth Summary -->
                <div class="insight-box">
                    <h3>📊 90-Day Growth Summary</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                        <div>
                            <div style="font-size: 0.9em; color: var(--gray-600);">Total Clicks</div>
                            <div style="font-size: 1.8em; font-weight: 700; color: var(--dark);">{total_clicks:,}</div>
                            <div style="font-size: 0.9em; color: {'var(--success)' if clicks_growth >= 0 else 'var(--danger)'}; font-weight: 600;">
                                {'+' if clicks_growth >= 0 else ''}{clicks_growth}% vs prev 90d
                            </div>
                        </div>
                        <div>
                            <div style="font-size: 0.9em; color: var(--gray-600);">Total Impressions</div>
                            <div style="font-size: 1.8em; font-weight: 700; color: var(--dark);">{total_impressions:,}</div>
                            <div style="font-size: 0.9em; color: {'var(--success)' if impressions_growth >= 0 else 'var(--danger)'}; font-weight: 600;">
                                {'+' if impressions_growth >= 0 else ''}{impressions_growth}% vs prev 90d
                            </div>
                        </div>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{ga4.get('sessions', 0):,}</div>
                        <div class="stat-label">Organic Sessions (30d)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{ga4.get('engagement_rate', 0)}%</div>
                        <div class="stat-label">Engagement Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(gsc.get('trending_up', []))}</div>
                        <div class="stat-label">Keywords Trending Up</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(gsc.get('optimization_needed', []))}</div>
                        <div class="stat-label">Optimization Targets</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px;">
                    <!-- Trending Up -->
                    <div>
                        <h3 style="margin-bottom: 15px; color: var(--success);">🚀 Trending Up (Last 90d)</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Keyword</th>
                                    <th>Click Growth</th>
                                    <th>Pos Change</th>
                                </tr>
                            </thead>
                            <tbody>
"""
    if gsc.get('trending_up'):
        for q in gsc.get('trending_up', []):
            keyword_html = escape_html(q.get('keyword', ''))
            click_change_html = escape_html(q.get('click_change', ''))
            position_change_html = escape_html(q.get('position_change', ''))
            html += f"""                                <tr>
                                    <td><strong>{keyword_html}</strong></td>
                                    <td style="color: var(--success);">+{click_change_html}</td>
                                    <td style="color: var(--success);">+{position_change_html}</td>
                                </tr>"""
    else:
        html += """<tr><td colspan="3" style="text-align:center; color: var(--gray-600);">No significant uptrends detected</td></tr>"""

    html += """                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Optimization Needed -->
                    <div>
                        <h3 style="margin-bottom: 15px; color: var(--warning);">🛠️ Optimization Opportunities</h3>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Page</th>
                                    <th>Issue</th>
                                    <th>Metric</th>
                                </tr>
                            </thead>
                            <tbody>
"""
    if gsc.get('optimization_needed'):
        for p in gsc.get('optimization_needed', []):
            url = p.get('url', '')
            url_path = url.replace('https://', '').replace('http://', '').split('/', 1)[-1]
            if not url_path: url_path = '/'
            url_html = escape_html(url)
            url_path_html = escape_html(url_path[:30])
            reason_html = escape_html(p.get('reason', ''))
            metric_html = escape_html(p.get('metric', ''))
            html += f"""                                <tr>
                                    <td title="{url_html}">/{url_path_html}...</td>
                                    <td>{reason_html}</td>
                                    <td>{metric_html}</td>
                                </tr>"""
    else:
        html += """<tr><td colspan="3" style="text-align:center; color: var(--gray-600);">No urgent optimization targets found</td></tr>"""

    html += """                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="margin-bottom: 15px;">🏆 Top Ranking Queries</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Query</th>
                                <th>Clicks</th>
                                <th>Impressions</th>
                                <th>Pos</th>
                            </tr>
                        </thead>
                        <tbody>
"""
    for q in gsc.get('top_queries', []):
        keyword_html = escape_html(q.get('keyword', ''))
        clicks_html = escape_html(q.get('clicks', ''))
        impressions_html = escape_html(q.get('impressions', ''))
        position = q.get('position', 0)
        try:
            position_html = escape_html(f"{float(position):.1f}")
        except (TypeError, ValueError):
            position_html = escape_html(position)
        html += f"""                            <tr>
                                <td><strong>{keyword_html}</strong></td>
                                <td>{clicks_html}</td>
                                <td>{impressions_html}</td>
                                <td>{position_html}</td>
                            </tr>"""
    html += """                        </tbody>
                    </table>
                </div>
            </section>
"""
else:
    html += """
            <section id="google-data" class="section">
                <h2 class="section-title"><span class="icon">📈</span> Google Search & Analytics</h2>
                <div class="insight-box">
                    <h3>⚠️ Data Not Available</h3>
                    <p>Run <strong>google_integration.py</strong> with a valid account to see real search performance data.</p>
                </div>
            </section>
"""

# Performance Section
if performance_data and len(performance_data) > 0:
    html += """
            <!-- Performance Analysis -->
            <section id="performance" class="section">
                <h2 class="section-title"><span class="icon">⚡</span> Performance & Core Web Vitals</h2>

                <div class="insight-box">
                    <h3>Why Performance Matters for SEO</h3>
                    <p>Google uses <strong>Core Web Vitals</strong> as ranking factors. Faster sites provide better user experience and typically rank higher in search results.</p>
                </div>

                <h3 style="margin: 30px 0 20px;">PageSpeed Scores</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Page</th>
                            <th>Device</th>
                            <th>Performance Score</th>
                            <th>LCP</th>
                            <th>FID</th>
                            <th>CLS</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    for result in performance_data:
        score = result.get('performance_score', 0)
        lcp = result.get('lcp', 0)
        fid = result.get('fid', 0)
        cls = result.get('cls', 0)

        # Determine score status
        score_class = 'good' if score >= 90 else ('needs-improvement' if score >= 50 else 'poor')
        lcp_status = '✅' if lcp < 2.5 else ('⚠️' if lcp < 4 else '❌')
        fid_status = '✅' if fid < 100 else ('⚠️' if fid < 300 else '❌')
        cls_status = '✅' if cls < 0.1 else ('⚠️' if cls < 0.25 else '❌')

        page_name = escape_html(result.get('url', '').split('/')[-1] or 'Homepage')
        device_html = escape_html(str(result.get('device', '')).title())

        html += f"""                        <tr>
                            <td><strong>{page_name}</strong></td>
                            <td>{device_html}</td>
                            <td>
                                <div class="performance-score {score_class}" style="display: inline-flex; width: 50px; height: 50px;">
                                    {int(score)}
                                </div>
                            </td>
                            <td>{lcp_status} {lcp:.2f}s</td>
                            <td>{fid_status} {fid:.0f}ms</td>
                            <td>{cls_status} {cls:.3f}</td>
                        </tr>
"""

    html += """                    </tbody>
                </table>

                <h3 style="margin: 40px 0 20px;">Performance Optimization Recommendations</h3>

                <div class="stats-grid" style="grid-template-columns: 1fr;">
                    <div class="insight-box">
                        <h3>🎯 Largest Contentful Paint (LCP)</h3>
                        <p><strong>Target:</strong> < 2.5 seconds</p>
                        <p><strong>Fixes:</strong> Optimize images (use WebP), implement lazy loading, use CDN, minimize server response time</p>
                    </div>

                    <div class="insight-box">
                        <h3>⚡ First Input Delay (FID)</h3>
                        <p><strong>Target:</strong> < 100 milliseconds</p>
                        <p><strong>Fixes:</strong> Minimize JavaScript execution, break up long tasks, use web workers, defer non-critical JavaScript</p>
                    </div>

                    <div class="insight-box">
                        <h3>📐 Cumulative Layout Shift (CLS)</h3>
                        <p><strong>Target:</strong> < 0.1</p>
                        <p><strong>Fixes:</strong> Set size attributes on images/videos, avoid inserting content above existing content, use transform animations</p>
                    </div>
                </div>
            </section>
"""
else:
    html += """
            <section id="performance" class="section">
                <h2 class="section-title"><span class="icon">⚡</span> Performance & Core Web Vitals</h2>
                <div class="insight-box">
                    <h3>⚠️ Performance Data Not Available</h3>
                    <p>Run performance_check.py to analyze Core Web Vitals.</p>
                </div>
            </section>
"""

# Recommendations section (Merged into Executive Summary)
if False:
    html += f"""
            <!-- Recommendations & Action Items -->
            <section id="recommendations" class="section">
                <h2 class="section-title"><span class="icon">📋</span> Action Items & Roadmap</h2>

                <h3 style="margin-bottom: 20px;">30-Day Quick Wins</h3>
                <div class="stats-grid" style="grid-template-columns: 1fr;">
                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Week 1-2: Technical SEO Foundation</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>✅ Add Product schema to all product pages</li>
                            <li>✅ Implement Organization schema on homepage</li>
                            <li>✅ Optimize top 5 product images (WebP, lazy loading)</li>
                            <li>✅ Fix Core Web Vitals issues (target LCP < 2.5s)</li>
                        </ul>
                    </div>

                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Week 3-4: Content Creation</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>📝 Create blog posts for top 5 Quick Win keywords</li>
                            <li>📝 Optimize existing product descriptions with target keywords</li>
                            <li>📝 Add FAQ schema to product pages</li>
                            <li>📝 Create collection pages for high-volume categories</li>
                        </ul>
                    </div>
                </div>

                <h3 style="margin: 40px 0 20px;">60-Day Growth Strategy</h3>
                <div class="stats-grid" style="grid-template-columns: 1fr;">
                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Content Expansion</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>📖 Create {min(10, len(categorized_gaps['content_gaps']))} educational blog posts from Content Gaps</li>
                            <li>📖 Develop comprehensive guides for top-performing keywords</li>
                            <li>📖 Add Article schema to all blog posts</li>
                            <li>📖 Internal linking strategy between blog posts and products</li>
                        </ul>
                    </div>

                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Product Optimization</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>🛒 Optimize {min(15, len(categorized_gaps['product_gaps']))} product pages for Product Gap keywords</li>
                            <li>🛒 Add customer reviews with Review schema</li>
                            <li>🛒 Create product comparison pages</li>
                            <li>🛒 Implement breadcrumb navigation with schema</li>
                        </ul>
                    </div>
                </div>

                <h3 style="margin: 40px 0 20px;">90-Day Advanced Tactics</h3>
                <div class="stats-grid" style="grid-template-columns: 1fr;">
                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Link Building & Authority</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>🔗 Guest post on pet wellness blogs (target: 5 quality backlinks)</li>
                            <li>🔗 Partner with pet influencers for product reviews</li>
                            <li>🔗 Submit to pet industry directories</li>
                            <li>🔗 Create linkable assets (infographics, research data)</li>
                        </ul>
                    </div>

                    <div class="stat-card" style="text-align: left;">
                        <h4 style="color: var(--primary); margin-bottom: 15px;">Advanced GEO & AI Optimization</h4>
                        <ul style="line-height: 2; color: var(--gray-700);">
                            <li>🤖 Implement HowTo schema for care guides</li>
                            <li>🤖 Add VideoObject schema for product videos</li>
                            <li>🤖 Create comprehensive FAQ pages with FAQPage schema</li>
                            <li>🤖 Monitor AI tool citations (ChatGPT, Perplexity)</li>
                        </ul>
                    </div>
                </div>

                <h3 style="margin: 40px 0 20px;">Priority Matrix</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Action Item</th>
                            <th>Impact</th>
                            <th>Effort</th>
                            <th>Timeline</th>
                            <th>Category</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Add Product schema to all products</strong></td>
                            <td><span class="priority-badge critical">HIGH</span></td>
                            <td><span class="priority-badge medium">MEDIUM</span></td>
                            <td>1 week</td>
                            <td>Technical SEO</td>
                        </tr>
                        <tr>
                            <td><strong>Create blog posts for Quick Win keywords</strong></td>
                            <td><span class="priority-badge critical">HIGH</span></td>
                            <td><span class="priority-badge high">HIGH</span></td>
                            <td>2-3 weeks</td>
                            <td>Content</td>
                        </tr>
                        <tr>
                            <td><strong>Optimize Core Web Vitals (LCP, CLS)</strong></td>
                            <td><span class="priority-badge critical">HIGH</span></td>
                            <td><span class="priority-badge medium">MEDIUM</span></td>
                            <td>1-2 weeks</td>
                            <td>Performance</td>
                        </tr>
                        <tr>
                            <td><strong>Optimize top {min(10, len(categorized_gaps['high_opportunity']))} High-Opportunity keywords</strong></td>
                            <td><span class="priority-badge critical">HIGH</span></td>
                            <td><span class="priority-badge high">HIGH</span></td>
                            <td>4 weeks</td>
                            <td>Content + On-Page</td>
                        </tr>
                        <tr>
                            <td><strong>Build backlinks from pet industry sites</strong></td>
                            <td><span class="priority-badge high">MEDIUM</span></td>
                            <td><span class="priority-badge high">HIGH</span></td>
                            <td>Ongoing</td>
                            <td>Off-Page SEO</td>
                        </tr>
                    </tbody>
                </table>

                <div class="insight-box" style="margin-top: 30px;">
                    <h3>📈 Expected Results</h3>
                    <p><strong>30 days:</strong> 10-15% improvement in Core Web Vitals, initial rankings for Quick Win keywords</p>
                    <p><strong>60 days:</strong> 20-30 new blog posts indexed, traffic increase of 25-40% from content gaps</p>
                    <p><strong>90 days:</strong> Ranking for 30-50% of target keywords, 2-3x organic traffic growth</p>
                </div>
            </section>
"""

# Close the HTML document (MUST be outside the if False block!)
html += """        </div>
    </main>

    <script>
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                // Hide all sections
                document.querySelectorAll('.section').forEach(s => {
                    s.classList.remove('active');
                });

                // Show clicked section
                const sectionId = item.dataset.section;
                const targetSection = document.getElementById(sectionId);
                if (targetSection) {
                    targetSection.classList.add('active');
                }

                // Update nav active state
                document.querySelectorAll('.nav-item').forEach(i => {
                    i.classList.remove('active');
                });
                item.classList.add('active');
            });
        });

        // Table sorting
        function sortTable(header, columnIndex) {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            // Determine sort direction
            const currentOrder = header.dataset.order || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

            // Sort rows
            rows.sort((a, b) => {
                const aCell = a.cells[columnIndex];
                const bCell = b.cells[columnIndex];

                // Try to get data-value attribute, otherwise use text content
                let aValue = aCell.dataset.value || aCell.textContent.trim();
                let bValue = bCell.dataset.value || bCell.textContent.trim();

                // Convert to numbers if possible
                const aNum = parseFloat(aValue.replace(/[^0-9.-]/g, ''));
                const bNum = parseFloat(bValue.replace(/[^0-9.-]/g, ''));

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return newOrder === 'asc' ? aNum - bNum : bNum - aNum;
                }

                // String comparison
                return newOrder === 'asc'
                    ? aValue.localeCompare(bValue)
                    : bValue.localeCompare(aValue);
            });

            // Update table
            rows.forEach(row => tbody.appendChild(row));

            // Update header sort indicator
            header.dataset.order = newOrder;
        }
    </script>
</body>
</html>
"""

# ============================================================================
# SAVE REPORT
# ============================================================================

safe_domain_name = TARGET_DOMAIN.replace('.', '-').replace('http://', '').replace('https://', '').strip('-')
report_filename = os.path.join(project_dir, f"{safe_domain_name}-seo-audit-{datetime.now().strftime('%Y-%m-%d')}.html")
with open(report_filename, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n{'='*60}")
print(f"✅ REPORT GENERATED SUCCESSFULLY")
print(f"{'='*60}")
print(f"\nFilename: {report_filename}")
print(f"\nSummary:")
print(f"  High-Opportunity Keywords: {len(categorized_gaps['high_opportunity'])}")
print(f"  Quick Wins: {len(categorized_gaps['quick_wins'])}")
print(f"  Content Gaps: {len(categorized_gaps['content_gaps'])}")
print(f"  Product Gaps: {len(categorized_gaps['product_gaps'])}")
print(f"  Total Opportunities: {total_gaps}")
print(f"\nOpen with: open {report_filename}")
print(f"{'='*60}\n")
