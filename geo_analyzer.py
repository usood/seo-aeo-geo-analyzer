#!/usr/bin/env python3
"""
GEO Analysis - Extract and audit JSON-LD schemas & AEO Signals
Focus: Product pages, Homepage, Blog posts
Date: December 5, 2025
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from utils.path_manager import get_current_project_path, get_latest_file

# Load project context
project_dir = get_current_project_path()
analysis_file = get_latest_file("analysis_data_*.json", project_dir)

test_urls = {}

if not analysis_file:
    print(f"ERROR: No analysis_data file found in {project_dir}. Run collect_data.py first.")
    exit(1)

with open(analysis_file) as f:
    data = json.load(f)
    target_domain = data.get('metadata', {}).get('target_domain')
    sitemap = data.get('sitemap_analysis', {}).get(target_domain, {})
    
    # Find one URL of each type
    sample_urls = sitemap.get('sample_urls', [])
    if sample_urls:
        test_urls['homepage'] = f"https://{target_domain}/"
        
        for url_data in sample_urls:
            u_type = url_data.get('type')
            if u_type == 'product' and 'product' not in test_urls:
                test_urls['product'] = url_data['url']
            elif u_type == 'content' and 'blog' not in test_urls:
                test_urls['blog'] = url_data['url']
            elif u_type == 'category' and 'collection' not in test_urls:
                test_urls['collection'] = url_data['url']

    # Fallback if no URLs found from sitemap (e.g. sitemap fetch failed)
    if not test_urls:
        print("⚠ Warning: No URLs found from sitemap. Using homepage fallback.")
        test_urls['homepage'] = f"https://{target_domain}/"

# Fail if no dynamic URLs
if not test_urls:
    print("ERROR: No dynamic URLs could be determined from analysis_data.json. Ensure sitemap analysis completed.")
    exit(1)

def extract_json_ld(soup, url):
    """Extract all JSON-LD from a page"""
    schemas = []
    scripts = soup.find_all('script', type='application/ld+json')
    
    for script in scripts:
        try:
            if script.string:
                data = json.loads(script.string)
                if isinstance(data, list):
                    schemas.extend(data)
                else:
                    schemas.append(data)
        except:
            pass
    return schemas

def analyze_aeo_signals(soup):
    """Analyze signals important for Answer Engine Optimization"""
    signals = {
        'has_h1': len(soup.find_all('h1')) > 0,
        'has_toc': False,
        'structure_depth': 0,
        'short_paragraphs': 0
    }
    
    # Check for Table of Contents (heuristic)
    if soup.find(class_=re.compile(r'toc|table-of-contents', re.I)) or soup.find(id=re.compile(r'toc|table-of-contents', re.I)):
        signals['has_toc'] = True
        
    # Check hierarchy depth
    if soup.find_all('h2'): signals['structure_depth'] = 2
    if soup.find_all('h3'): signals['structure_depth'] = 3
    
    # Check for short, answer-like paragraphs (good for featured snippets)
    paragraphs = soup.find_all('p')
    short_paras = [p for p in paragraphs if 40 < len(p.get_text().strip()) < 200]
    signals['short_paragraphs'] = len(short_paras)
    
    return signals

def validate_schema(schema, page_type):
    """Validate schema based on page type"""
    issues = []
    schema_type = schema.get('@type')
    
    if isinstance(schema_type, list):
        s_type = schema_type[0]
    else:
        s_type = schema_type

    if page_type == 'product' and s_type == 'Product':
        if 'offers' not in schema:
            issues.append("Missing 'offers' property")
        if 'aggregateRating' not in schema and 'review' not in schema:
            issues.append("Missing 'aggregateRating' or 'review'")
        if 'brand' not in schema:
            issues.append("Missing 'brand'")
            
    elif page_type == 'blog' and s_type in ['Article', 'BlogPosting', 'NewsArticle']:
        if 'headline' not in schema:
            issues.append("Missing 'headline'")
        if 'datePublished' not in schema:
            issues.append("Missing 'datePublished'")
        if 'author' not in schema:
            issues.append("Missing 'author'")
            
    elif s_type == 'Organization':
        if 'logo' not in schema:
            issues.append("Missing 'logo'")
        if 'contactPoint' not in schema:
            issues.append("Missing 'contactPoint'")
            
    return issues

def analyze_page(url, page_type):
    print(f"Analyzing {page_type}: {url}...")
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        
        if response.status_code != 200:
            return {"error": f"Status code {response.status_code}"}
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        schemas = extract_json_ld(soup, url)
        aeo_signals = analyze_aeo_signals(soup)
        
        schema_analysis = []
        for s in schemas:
            s_type = s.get('@type', 'Unknown')
            issues = validate_schema(s, page_type)
            schema_analysis.append({
                'type': s_type,
                'issues': issues,
                'valid': len(issues) == 0
            })
            
        return {
            'schemas': schema_analysis,
            'aeo_signals': aeo_signals,
            'url': url
        }
        
    except Exception as e:
        print(f"  Error: {e}")
        return {"error": str(e)}

results = {}
for page_type, url in test_urls.items():
    results[page_type] = analyze_page(url, page_type)

# Save
output_file = os.path.join(project_dir, 'geo_analysis.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analyzed {len(test_urls)} pages")
print(f"✓ Saved to {output_file}")