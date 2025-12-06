#!/usr/bin/env python3
"""
DataForSEO API Collection Script
Automates all 17 API calls for keyword gap analysis
Date: December 5, 2025
"""

import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os
from utils.path_manager import get_current_project_path, get_latest_file

# Load credentials
load_dotenv()
DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN')
DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD')

if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
    print("ERROR: DataForSEO credentials not found in .env file")
    exit(1)

# Load configuration from previous step
project_dir = get_current_project_path()
analysis_file = get_latest_file("analysis_data_*.json", project_dir)

if not analysis_file:
    print(f"ERROR: No analysis_data file found in {project_dir}. Run collect_data.py first.")
    exit(1)

with open(analysis_file, 'r') as f:
    analysis_data = json.load(f)
    metadata = analysis_data.get('metadata', {})
    TARGET_DOMAIN = metadata.get('target_domain')
    COMPETITORS = metadata.get('competitors', {})
    LOCATION = metadata.get('location', "India")
    LANGUAGE = metadata.get('language', "en")

print(f"Loaded config from {analysis_file}")
print(f"Target: {TARGET_DOMAIN}")

# API Configuration
API_BASE = "https://api.dataforseo.com/v3"
AUTH = (DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD)

# Results storage
results = {
    "metadata": {
        "target_domain": TARGET_DOMAIN,
        "competitors": COMPETITORS,
        "location": LOCATION,
        "language": LANGUAGE,
        "collection_date": datetime.now().isoformat(),
        "total_cost": 0.0
    },
    "domain_metrics": {},
    "ranked_keywords": {},
    "backlinks": {},
    "keyword_ideas": [],
    "gaps": {
        "all_gaps": [],
        "top_100": []
    },
    "keyword_enrichment": {},
    "search_intent": {},
    "serp_analysis": {}
}

def make_api_call(endpoint, payload):
    """Make DataForSEO API call with error handling"""
    url = f"{API_BASE}/{endpoint}"

    try:
        response = requests.post(url, json=payload, auth=AUTH, timeout=120)
        response.raise_for_status()

        data = response.json()

        # Check for API errors
        if data.get('status_code') == 20000:
            return data
        else:
            print(f"  API Error: {data.get('status_message', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  Request Error: {e}")
        return None


def get_domain_metrics(domain):
    """Get domain rank overview"""
    print(f"\n[Domain Metrics] Fetching for {domain}...")

    payload = [{
        "target": domain,
        "location_name": LOCATION,
        "language_code": LANGUAGE,
        "ignore_synonyms": True
    }]

    data = make_api_call("dataforseo_labs/google/domain_rank_overview/live", payload)

    if data and data['tasks'][0]['result']:
        result = data['tasks'][0]['result'][0]
        print(f"  ✓ Rank: {result.get('metrics', {}).get('organic', {}).get('etv', 0)}")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return result

    return None


def get_ranked_keywords(domain, limit=100):
    """Get top ranked keywords for domain"""
    print(f"\n[Ranked Keywords] Fetching top {limit} for {domain}...")

    payload = [{
        "target": domain,
        "location_name": LOCATION,
        "language_code": LANGUAGE,
        "limit": limit,
        "filters": [["ranked_serp_element.serp_item.rank_group", "<=", 100]],
        "order_by": ["keyword_data.keyword_info.search_volume,desc"]
    }]

    data = make_api_call("dataforseo_labs/google/ranked_keywords/live", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Found {len(items)} keywords")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return items

    return []


def get_bulk_backlinks(domains):
    """Get referring domains for all domains"""
    print(f"\n[Backlinks] Fetching for {len(domains)} domains...")

    payload = [{
        "targets": domains
    }]

    data = make_api_call("backlinks/bulk_referring_domains/live", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Found data for {len(items)} domains")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return {item['target']: item for item in items}

    return {}


def get_keyword_ideas(seed_keywords):
    """Get related keyword ideas"""
    print(f"\n[Keyword Ideas] Fetching ideas for {len(seed_keywords)} seed keywords...")

    payload = [{
        "keywords": seed_keywords,
        "location_name": LOCATION,
        "language_code": LANGUAGE,
        "limit": 100
    }]

    data = make_api_call("dataforseo_labs/google/keyword_ideas/live", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Found {len(items)} keyword ideas")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return items

    return []


def get_keyword_overview(keywords):
    """Get keyword metrics for list of keywords"""
    print(f"\n[Keyword Overview] Enriching {len(keywords)} keywords...")

    # DataForSEO limits to 700 keywords per call
    keywords = keywords[:700]

    payload = [{
        "keywords": keywords,
        "location_name": LOCATION,
        "language_code": LANGUAGE,
        "include_clickstream_data": True
    }]

    data = make_api_call("dataforseo_labs/google/keyword_overview/live", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Enriched {len(items)} keywords")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return items

    return []


def get_search_intent(keywords):
    """Get search intent classification"""
    print(f"\n[Search Intent] Classifying {len(keywords)} keywords...")

    # Limit to 1000 keywords per call
    keywords = keywords[:1000]

    payload = [{
        "keywords": keywords,
        "language_code": LANGUAGE
    }]

    data = make_api_call("dataforseo_labs/google/search_intent/live", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Classified {len(items)} keywords")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return items

    return []


def get_serp_analysis(keyword):
    """Get SERP analysis for keyword"""
    print(f"\n[SERP Analysis] Analyzing '{keyword}'...")

    payload = [{
        "keyword": keyword,
        "location_name": LOCATION,
        "language_code": LANGUAGE,
        "device": "desktop",
        "depth": 20
    }]

    data = make_api_call("serp/google/organic/live/advanced", payload)

    if data and data['tasks'][0]['result']:
        items = data['tasks'][0]['result'][0].get('items', [])
        print(f"  ✓ Found {len(items)} SERP results")
        results['metadata']['total_cost'] += data['tasks'][0].get('cost', 0)
        return items

    return []


def process_keyword_gaps():
    """Identify keyword gaps and find top 100"""
    print("\n" + "="*60)
    print("PROCESSING KEYWORD GAPS")
    print("="*60)

    # Get target keywords
    target_keywords = set()
    for item in results['ranked_keywords'].get(TARGET_DOMAIN, []):
        keyword = item.get('keyword_data', {}).get('keyword')
        if keyword:
            target_keywords.add(keyword.lower())

    print(f"Target has {len(target_keywords)} keywords")

    # Find gaps
    all_gaps = []

    for comp_domain, comp_keywords in results['ranked_keywords'].items():
        if comp_domain == TARGET_DOMAIN:
            continue

        for item in comp_keywords:
            keyword_data = item.get('keyword_data', {})
            keyword = keyword_data.get('keyword')

            if keyword and keyword.lower() not in target_keywords:
                gap = {
                    'keyword': keyword,
                    'competitor': comp_domain,
                    'competitor_position': item.get('ranked_serp_element', {}).get('serp_item', {}).get('rank_absolute', 999),
                    'search_volume': keyword_data.get('keyword_info', {}).get('search_volume', 0),
                    'cpc': keyword_data.get('keyword_info', {}).get('cpc', 0),
                    'competition': keyword_data.get('keyword_info', {}).get('competition', 0)
                }
                all_gaps.append(gap)

    # Sort by search volume and get top 100 unique keywords
    all_gaps = sorted(all_gaps, key=lambda x: x['search_volume'], reverse=True)

    # Deduplicate keywords
    seen_keywords = set()
    unique_gaps = []
    for gap in all_gaps:
        if gap['keyword'].lower() not in seen_keywords:
            seen_keywords.add(gap['keyword'].lower())
            unique_gaps.append(gap)
            if len(unique_gaps) >= 100:
                break

    results['gaps']['all_gaps'] = all_gaps
    results['gaps']['top_100'] = unique_gaps

    print(f"\n✓ Found {len(all_gaps)} total gaps")
    print(f"✓ Selected top {len(unique_gaps)} unique keywords")

    return [gap['keyword'] for gap in unique_gaps]


def save_progress(filename_suffix="progress"):
    """Save current results"""
    filename = os.path.join(project_dir, f"dataforseo_{filename_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Saved to: {filename}")
    return filename


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("DATAFORSEO API COLLECTION")
    print(f"Target: {TARGET_DOMAIN}")
    print(f"Competitors: {len(COMPETITORS)}")
    print("="*60)

    all_domains = [TARGET_DOMAIN] + list(COMPETITORS.keys())

    # ========================================================================
    # PHASE 1: INDEPENDENT API CALLS (12 calls)
    # ========================================================================

    print("\n" + "="*60)
    print("PHASE 1: INDEPENDENT API CALLS")
    print("="*60)

    # Call Set 1: Domain Metrics (5 calls @ $0.05 = $0.25)
    print("\n--- Domain Metrics (5 calls) ---")
    for domain in all_domains:
        metrics = get_domain_metrics(domain)
        if metrics:
            results['domain_metrics'][domain] = metrics
        time.sleep(1)

    # Call Set 2: Ranked Keywords (5 calls @ $0.50 = $2.50)
    print("\n--- Ranked Keywords (5 calls) ---")
    for domain in all_domains:
        keywords = get_ranked_keywords(domain, limit=100)
        if keywords:
            results['ranked_keywords'][domain] = keywords
        time.sleep(1)

    # Call Set 6: Backlinks (1 call @ $0.50 = $0.50)
    print("\n--- Backlinks Bulk (1 call) ---")
    backlinks = get_bulk_backlinks(all_domains)
    results['backlinks'] = backlinks
    time.sleep(1)

    # Call Set 7: Keyword Ideas (1 call @ $0.50 = $0.50)
    print("\n--- Keyword Ideas (1 call) ---")
    seed_keywords = ["dog supplements", "pet wellness", "dog vitamins"]
    keyword_ideas = get_keyword_ideas(seed_keywords)
    results['keyword_ideas'] = keyword_ideas

    # Save Phase 1 results
    save_progress("phase1")

    # ========================================================================
    # PHASE 2: PROCESS GAPS
    # ========================================================================

    print("\n" + "="*60)
    print("PHASE 2: GAP PROCESSING")
    print("="*60)

    top_100_keywords = process_keyword_gaps()

    if not top_100_keywords:
        print("ERROR: No gaps found. Exiting.")
        save_progress("final")
        exit(1)

    # ========================================================================
    # PHASE 3: DEPENDENT API CALLS (5 calls)
    # ========================================================================

    print("\n" + "="*60)
    print("PHASE 3: DEPENDENT API CALLS")
    print("="*60)

    # Call Set 3: Keyword Enrichment (1 call @ $0.50 = $0.50)
    enrichment = get_keyword_overview(top_100_keywords)
    results['keyword_enrichment'] = enrichment
    time.sleep(1)

    # Call Set 4: Search Intent (1 call @ $0.20 = $0.20)
    intent = get_search_intent(top_100_keywords)
    results['search_intent'] = intent
    time.sleep(1)

    # Call Set 5: SERP Analysis for top 3 keywords (3 calls @ $0.50 = $1.50)
    print("\n--- SERP Analysis for Top 3 Keywords (3 calls) ---")
    top_3_keywords = [gap['keyword'] for gap in results['gaps']['top_100'][:3]]

    for keyword in top_3_keywords:
        serp = get_serp_analysis(keyword)
        results['serp_analysis'][keyword] = serp
        time.sleep(1)

    # ========================================================================
    # FINAL SAVE
    # ========================================================================

    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)
    print(f"\nTotal API Calls: 17")
    print(f"Total Cost: ${results['metadata']['total_cost']:.2f}")
    print(f"Target Keywords: {len(results['ranked_keywords'].get(TARGET_DOMAIN, []))}")
    print(f"Total Gaps Found: {len(results['gaps']['all_gaps'])}")
    print(f"Top Gaps Selected: {len(results['gaps']['top_100'])}")

    final_file = save_progress("final")

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Run geo_analyzer.py for JSON-LD analysis")
    print("2. Run performance_check.py for PageSpeed analysis")
    print("3. Generate HTML report")
    print(f"\nData saved to: {final_file}")
