#!/usr/bin/env python3
"""
LLM Runner Script
Orchestrates LLM analysis on top of collected data
Date: December 6, 2025
"""

import json
import os
import glob
import requests
from llm_analyzer import LLMAnalyzer
from datetime import datetime
from utils.path_manager import get_current_project_path, get_latest_file

def fetch_page_content(url):
    """Fetch and clean text content from a URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
    except Exception as e:
        print(f"⚠ Failed to fetch {url}: {e}")
    return None

def main():
    print("="*60)
    print("LLM STRATEGIC ANALYSIS")
    print("="*60)
    
    import requests # Ensure requests is imported
    
    analyzer = LLMAnalyzer()
    if not analyzer.provider:
        print("❌ No API Key found. Please set GEMINI_API_KEY or OPENROUTER_API_KEY in .env")
        return

    print(f"✓ Using Provider: {analyzer.provider.title()}")
    
    # Load Data
    project_dir = get_current_project_path()
    gsc_file = os.path.join(project_dir, "google_data.json")
    dfs_file = get_latest_file("dataforseo_final_*.json", project_dir)
    
    insights = {}
    
    # 1. Aggregate Data for Holistic Analysis
    context = {
        'domain': '',
        'top_keywords': [],
        'declining_keywords': [],
        'technical_summary': 'No data',
        'content_summary': 'No data'
    }

    # Load DataForSEO (Keywords)
    if dfs_file:
        with open(dfs_file) as f:
            seo_data = json.load(f)
            top_gaps = seo_data.get('gaps', {}).get('top_100', [])
            context['top_keywords'] = [g['keyword'] for g in top_gaps[:5]]
            context['domain'] = seo_data.get('metadata', {}).get('target_domain') # Get domain from metadata

    # Load GSC (Trends)
    if os.path.exists(gsc_file):
        with open(gsc_file) as f:
            gsc_data = json.load(f)
            trending_down = gsc_data.get('gsc', {}).get('trending_down', [])
            context['declining_keywords'] = [t['keyword'] for t in trending_down[:5]]
            
            opt_targets = gsc_data.get('gsc', {}).get('optimization_needed', [])
            if opt_targets:
                context['content_summary'] = f"Top page needing optimization: {opt_targets[0]['url']} (Reason: {opt_targets[0]['reason']})"

    # Load Performance
    perf_file = os.path.join(project_dir, "performance_analysis.json")
    if os.path.exists(perf_file):
        with open(perf_file) as f:
            perf_data = json.load(f)
            avg_score = sum(p.get('performance_score', 0) for p in perf_data) / len(perf_data) if perf_data else 0
            context['technical_summary'] = f"Avg Mobile Performance Score: {avg_score:.1f}/100"

    print("\n🤖 Generating Holistic SEO Strategy...")
    strategy = analyzer.generate_holistic_strategy(context)
    insights['holistic_strategy'] = strategy
    print("✓ Strategy Generated")

    # Save Results
    if insights:
        output_file = os.path.join(project_dir, "llm_insights.json")
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)
        print(f"\n✓ Saved insights to {output_file}")
    else:
        print("\n⚠ No suitable data found to analyze.")

if __name__ == "__main__":
    main()
