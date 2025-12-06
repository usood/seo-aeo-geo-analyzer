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

load_dotenv()

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_KEY = os.getenv('PAGESPEED_API_KEY')  # Optional, but recommended

pages = [
    'https://unleashwellness.co/',
    'https://unleashwellness.co/products/jolly-gut',
    'https://unleashwellness.co/collections/all'
]

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
with open('performance_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analyzed {len(pages)} pages")
print(f"✓ Saved to performance_analysis.json")
