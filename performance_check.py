#!/usr/bin/env python3
"""
Performance Check - PageSpeed Insights for key pages
Date: December 5, 2025
"""

import requests
import json
import time

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

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
            response = requests.get(API_URL, params={
                'url': url,
                'strategy': strategy,
                'category': 'performance'
            }, timeout=60)

            data = response.json()
            lighthouse = data.get('lighthouseResult', {})
            audits = lighthouse.get('audits', {})

            results.append({
                'url': url,
                'device': strategy,
                'performance_score': lighthouse.get('categories', {}).get('performance', {}).get('score', 0) * 100,
                'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000,
                'fid': audits.get('max-potential-fid', {}).get('numericValue', 0),
                'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
            })

            print(f"  {strategy}: {results[-1]['performance_score']:.0f}/100")
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(3)  # Rate limiting

# Save
with open('performance_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analyzed {len(pages)} pages")
print(f"✓ Saved to performance_analysis.json")
