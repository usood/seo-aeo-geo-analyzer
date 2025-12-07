#!/usr/bin/env python3
"""
Performance Check - PageSpeed Insights for key pages
Date: December 5, 2025

NOTE: This script uses Google PageSpeed Insights API which requires an API key
for production use. Without an API key, you're limited to very few requests.

To add an API key, set PAGESPEED_API_KEY in your .env file.
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from utils.path_manager import get_current_project_path, get_latest_file

load_dotenv()

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_KEY = os.getenv('PAGESPEED_API_KEY')

# Load project context
project_dir = get_current_project_path()
analysis_file = get_latest_file("analysis_data_*.json", project_dir)

pages = []

# Try loading from config.yaml first
try:
    import yaml
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            raw_pages = config.get('analysis', {}).get('performance_urls', [])
            # Filter out empty strings
            pages = [p for p in raw_pages if p and p.strip()]
            if pages:
                print(f"✓ Loaded {len(pages)} performance URLs from config.yaml")
            elif raw_pages:
                 print(f"ℹ Config has {len(raw_pages)} empty performance URL slots. Will use auto-detection.")
except ImportError:
    pass

# Fallback to dynamic analysis if config is empty
if not pages and analysis_file:
    print("⚠ Config URLs not found. Falling back to dynamic analysis data.")
    with open(analysis_file) as f:
        data = json.load(f)
        target_domain = data.get('metadata', {}).get('target_domain')
        sitemap = data.get('sitemap_analysis', {}).get(target_domain, {})
        
        sample_urls = sitemap.get('sample_urls', [])
        seen_types = set()
        
        # Add homepage
        pages.append(f"https://{target_domain}/")
        
        for url_data in sample_urls:
            u_type = url_data.get('type')
            if u_type in ['product', 'category', 'content'] and u_type not in seen_types:
                pages.append(url_data['url'])
                seen_types.add(u_type)

# Fail if no dynamic URLs
if not pages:
    print("ERROR: No dynamic URLs could be determined. Ensure sitemap analysis completed or config.yaml is set.")
    exit(1)

results = []

for url in pages:
    print(f"Analyzing: {url}")

    for strategy in ['mobile', 'desktop']:
        try:
            params = {
                'url': url,
                'strategy': strategy,
                'category': 'performance'
            }
            if API_KEY:
                params['key'] = API_KEY

            response = requests.get(API_URL, params=params, timeout=60)
            data = response.json()

            # Check for API errors
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                print(f"  {strategy}: API Error - {error_msg}")
                results.append({
                    'url': url,
                    'device': strategy,
                    'performance_score': 0,
                    'lcp': 0,
                    'fid': 0,
                    'cls': 0,
                    'error': error_msg
                })
                continue

            lighthouse = data.get('lighthouseResult', {})
            audits = lighthouse.get('audits', {})
            score = lighthouse.get('categories', {}).get('performance', {}).get('score')

            results.append({
                'url': url,
                'device': strategy,
                'performance_score': (score * 100) if score is not None else 0,
                'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000,
                'fid': audits.get('max-potential-fid', {}).get('numericValue', 0),
                'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
            })

            print(f"  {strategy}: {results[-1]['performance_score']:.0f}/100")
        except Exception as e:
            print(f"  {strategy}: Error - {e}")
            results.append({
                'url': url,
                'device': strategy,
                'performance_score': 0,
                'lcp': 0,
                'fid': 0,
                'cls': 0,
                'error': str(e)
            })

        time.sleep(3)  # Rate limiting

# Save
output_file = os.path.join(project_dir, 'performance_analysis.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analyzed {len(pages)} pages")
print(f"✓ Saved to {output_file}")
