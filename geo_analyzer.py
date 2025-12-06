#!/usr/bin/env python3
"""
GEO Analysis - Extract and audit JSON-LD schemas
Focus: Product pages, Homepage, Blog posts
Date: December 5, 2025
"""

import requests
from bs4 import BeautifulSoup
import json

def extract_json_ld(url):
    """Extract all JSON-LD from a page"""
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')

        schemas = []
        for script in scripts:
            try:
                schemas.append(json.loads(script.string))
            except:
                pass

        return schemas
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return []

# Test URLs
test_urls = {
    'homepage': 'https://unleashwellness.co/',
    'product': 'https://unleashwellness.co/products/jolly-gut',
    'collection': 'https://unleashwellness.co/collections/all',
    'blog': 'https://unleashwellness.co/blogs/pet-wellness'
}

results = {}
for page_type, url in test_urls.items():
    print(f"Analyzing {page_type}...")
    results[page_type] = extract_json_ld(url)

# Save
with open('geo_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analyzed {len(test_urls)} pages")
print(f"✓ Saved to geo_analysis.json")
