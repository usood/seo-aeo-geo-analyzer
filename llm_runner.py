#!/usr/bin/env python3
"""
LLM Runner Script
Orchestrates LLM analysis on top of collected data
Date: December 6, 2025
"""

import json
import os
import glob
from llm_analyzer import LLMAnalyzer
from datetime import datetime

def find_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    return max(files, key=os.path.getctime)

def main():
    print("="*60)
    print("LLM STRATEGIC ANALYSIS")
    print("="*60)
    
    analyzer = LLMAnalyzer()
    if not analyzer.provider:
        print("❌ No API Key found. Please set GEMINI_API_KEY or OPENROUTER_API_KEY in .env")
        return

    print(f"✓ Using Provider: {analyzer.provider.title()}")
    
    # Load Data
    gsc_file = "google_data.json"
    dfs_file = find_latest_file("dataforseo_final_*.json")
    
    insights = {}
    
    # 1. Analyze Top Keyword Opportunity (DataForSEO)
    if dfs_file:
        with open(dfs_file) as f:
            seo_data = json.load(f)
            top_gaps = seo_data.get('gaps', {}).get('top_100', [])
            
            # Find highest volume opportunity
            high_value = next((g for g in top_gaps if g.get('search_volume', 0) > 1000), None)
            
            if high_value:
                kw = high_value['keyword']
                competitors = [high_value.get('competitor', 'competitors')]
                print(f"\n🤖 Generating Content Brief for: '{kw}'...")
                
                brief = analyzer.generate_content_brief(kw, competitors)
                insights['content_brief'] = {
                    'keyword': kw,
                    'brief': brief
                }
                print("✓ Brief Generated")

    # 2. Analyze Page Optimization (GSC)
    if os.path.exists(gsc_file):
        with open(gsc_file) as f:
            gsc_data = json.load(f)
            opt_targets = gsc_data.get('gsc', {}).get('optimization_needed', [])
            
            if opt_targets:
                target = opt_targets[0] # Analyze top target
                url = target['url']
                print(f"\n🤖 Analyzing Page for Optimization: {url}...")
                
                # Note: We aren't scraping the page content here to keep it simple, 
                # but we could add a fetch_page_content() helper. 
                # For now, we ask LLM to infer or browse if it has capability (Gemini often can)
                rec = analyzer.analyze_page_content(url, "target keyword inferred")
                insights['page_audit'] = {
                    'url': url,
                    'analysis': rec
                }
                print("✓ Audit Complete")

    # Save Results
    if insights:
        output_file = "llm_insights.json"
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)
        print(f"\n✓ Saved insights to {output_file}")
    else:
        print("\n⚠ No suitable data found to analyze.")

if __name__ == "__main__":
    main()
