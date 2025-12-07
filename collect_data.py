#!/usr/bin/env python3
"""
Keyword Gap Analysis Data Collection Script
For: unleashwellness.co
Date: December 5, 2025
"""

import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
from datetime import datetime

# Configuration
try:
    import yaml
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            TARGET_DOMAIN = config.get('target', {}).get('domain')
            COMPETITORS = {c['domain']: c['name'] for c in config.get('competitors', [])}
            LOCATION = config.get('location', {}).get('country', 'India')
            LANGUAGE = config.get('location', {}).get('language_code', 'en')
    else:
        # Fallback to env or dummy for testing
        TARGET_DOMAIN = os.getenv('TARGET_DOMAIN', 'example.com')
        COMPETITORS = {}
        LOCATION = "India"
        LANGUAGE = "en"
except ImportError:
    print("⚠ PyYAML not installed. Using defaults.")
    TARGET_DOMAIN = os.getenv('TARGET_DOMAIN', 'example.com')
    COMPETITORS = {}
    LOCATION = "India"
    LANGUAGE = "en"

if not TARGET_DOMAIN or TARGET_DOMAIN == 'example.com':
    print("⚠ Warning: Using default/empty target domain. Configure config.yaml")

# Results storage
results = {
    "metadata": {
        "target_domain": TARGET_DOMAIN,
        "competitors": COMPETITORS,
        "location": LOCATION,
        "language": LANGUAGE,
        "analysis_date": datetime.now().isoformat()
    },
    "sitemap_analysis": {},
    "social_profiles": {},
    "local_international": {},
    "domain_metrics": {},
    "ranked_keywords": {},
    "keyword_gaps": {}
}


def fetch_sitemap(domain):
    """Fetch and parse sitemap.xml"""
    print(f"\n[Sitemap] Fetching sitemap for {domain}...")

    sitemap_urls = [
        f"https://{domain}/sitemap-index.xml",
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap-index.xml",
    ]

    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                print(f"✓ Found sitemap at: {sitemap_url}")

                # Parse XML
                root = ET.fromstring(response.content)

                # Check if it's a sitemap index
                namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                # Try to find sitemap elements (sitemap index)
                sitemaps = root.findall('.//sm:sitemap', namespaces)
                if sitemaps:
                    print(f"  Found sitemap index with {len(sitemaps)} sitemaps")
                    all_urls = []

                    # Fetch each sub-sitemap
                    for sitemap in sitemaps[:10]:  # Limit to first 10 sitemaps
                        loc = sitemap.find('sm:loc', namespaces)
                        if loc is not None:
                            sub_sitemap_url = loc.text
                            print(f"  Fetching sub-sitemap: {sub_sitemap_url}")
                            try:
                                sub_response = requests.get(sub_sitemap_url, timeout=15, headers={
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                                })
                                if sub_response.status_code == 200:
                                    sub_root = ET.fromstring(sub_response.content)
                                    sub_urls = parse_sitemap_urls(sub_root, namespaces)
                                    all_urls.extend(sub_urls)
                            except Exception as e:
                                print(f"    Error fetching sub-sitemap: {e}")

                    return analyze_sitemap_urls(all_urls, domain)

                # Otherwise, parse as regular sitemap
                urls = parse_sitemap_urls(root, namespaces)
                return analyze_sitemap_urls(urls, domain)

        except Exception as e:
            print(f"  Error with {sitemap_url}: {e}")
            continue

    return {"error": "No sitemap found", "total_urls": 0}


def parse_sitemap_urls(root, namespaces):
    """Parse URLs from sitemap XML"""
    urls = []

    for url_elem in root.findall('.//sm:url', namespaces):
        loc = url_elem.find('sm:loc', namespaces)
        lastmod = url_elem.find('sm:lastmod', namespaces)

        if loc is not None:
            url_data = {
                'url': loc.text,
                'lastmod': lastmod.text if lastmod is not None else None,
            }
            urls.append(url_data)

    return urls


def categorize_url(url):
    """Categorize URL by type (Expanded heuristics)"""
    url_lower = url.lower()

    # Product/Service related
    if any(x in url_lower for x in ['/products/', '/pricing', '/features', '/solution', '/service', '/tool']):
        return 'product'
    
    # Categories/Tags
    elif any(x in url_lower for x in ['/collections/', '/category/', '/tag/', '/topics/', '/sections/']):
        return 'category'
        
    # Content/Blog
    elif any(x in url_lower for x in ['/blogs/', '/articles/', '/news/', '/post/', '/guide/', '/tutorial/', '/blog']):
        return 'content'
    elif any(x in url_lower for x in ['/2023/', '/2024/', '/2025/']): # Date based URLs
        return 'content'
        
    # Static Pages
    elif any(x in url_lower for x in ['/pages/', '/about', '/contact', '/terms', '/privacy', '/legal']):
        return 'static'
        
    else:
        # Heuristic: if URL path is deep (>3 segments) and no extension, likely content
        path = urlparse(url).path
        if path.count('/') > 2 and '.' not in path.split('/')[-1]:
            return 'content'
            
        return 'other'


def analyze_sitemap_urls(urls, domain):
    """Analyze sitemap URLs and categorize"""
    print(f"  Analyzing {len(urls)} URLs...")

    categorization = {
        'product': 0,
        'content': 0,
        'category': 0,
        'static': 0,
        'other': 0
    }

    for url_data in urls:
        url_type = categorize_url(url_data['url'])
        categorization[url_type] += 1
        url_data['type'] = url_type

    # Calculate freshness (URLs modified in last 90 days)
    fresh_count = 0
    urls_with_date = 0
    
    if urls:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=90)

        for url_data in urls:
            if url_data.get('lastmod'):
                urls_with_date += 1
                try:
                    mod_date = datetime.fromisoformat(url_data['lastmod'].replace('Z', '+00:00'))
                    if mod_date > cutoff_date:
                        fresh_count += 1
                except:
                    pass

    if urls_with_date > 0:
        freshness_pct = (fresh_count / len(urls) * 100)
    else:
        freshness_pct = None

    return {
        'total_urls': len(urls),
        'categorization': categorization,
        'freshness': {
            'fresh_count': fresh_count,
            'freshness_percentage': round(freshness_pct, 1) if freshness_pct is not None else None,
            'has_dates': urls_with_date > 0
        },
        'sample_urls': urls[:20]  # First 20 for reference
    }


def find_social_profiles(domain):
    """Find social media profiles for domain"""
    print(f"\n[Social] Finding social profiles for {domain}...")

    profiles = {}

    # Try homepage
    try:
        response = requests.get(f"https://{domain}", timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Social platform patterns
            social_patterns = {
                'facebook': ['facebook.com/', 'fb.com/'],
                'instagram': ['instagram.com/'],
                'twitter': ['twitter.com/', 'x.com/'],
                'tiktok': ['tiktok.com/@'],
                'youtube': ['youtube.com/', 'youtu.be/'],
                'linkedin': ['linkedin.com/'],
                'pinterest': ['pinterest.com/'],
                'reddit': ['reddit.com/user/', 'reddit.com/r/'],
            }

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']

                for platform, patterns in social_patterns.items():
                    if platform not in profiles:  # Only take first match
                        if any(pattern in href for pattern in patterns):
                            # Clean up URL
                            if not href.startswith('http'):
                                href = urljoin(f"https://{domain}", href)
                            profiles[platform] = {
                                'url': href,
                                'found': True
                            }

            print(f"  Found {len(profiles)} social profiles")
            for platform, data in profiles.items():
                print(f"    ✓ {platform.title()}: {data['url']}")

    except Exception as e:
        print(f"  Error scraping {domain}: {e}")

    # Mark missing platforms
    all_platforms = ['facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'linkedin', 'pinterest', 'reddit']
    for platform in all_platforms:
        if platform not in profiles:
            profiles[platform] = {'found': False, 'url': None}

    return profiles


def analyze_local_international_seo(domain):
    """Analyze Local and International SEO signals"""
    print(f"\n[Local/Intl] Analyzing Local & International SEO for {domain}...")
    
    data = {
        'international': {
            'hreflang_tags': [],
            'content_language': None,
            'has_intl_signals': False
        },
        'local': {
            'phone_found': False,
            'address_found': False,
            'map_embed': False,
            'has_local_signals': False
        }
    }
    
    try:
        response = requests.get(f"https://{domain}", timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- International SEO ---
            # Check hreflang
            hreflangs = soup.find_all('link', rel='alternate', hreflang=True)
            for tag in hreflangs:
                data['international']['hreflang_tags'].append({
                    'lang': tag.get('hreflang'),
                    'url': tag.get('href')
                })
            
            # Check content-language
            meta_lang = soup.find('meta', attrs={'http-equiv': 'Content-Language'})
            if meta_lang:
                data['international']['content_language'] = meta_lang.get('content')
                
            if data['international']['hreflang_tags'] or data['international']['content_language']:
                data['international']['has_intl_signals'] = True
                
            # --- Local SEO ---
            text_content = soup.get_text().lower()
            
            # Simple phone check (heuristic)
            import re
            # Matches +91-..., +1-..., or standard 10-digit sequences with separators
            phone_pattern = re.compile(r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}')
            if phone_pattern.search(text_content):
                data['local']['phone_found'] = True
                
            # Simple address keywords check
            address_keywords = ['street', 'road', 'avenue', 'lane', 'floor', 'building', 'pincode', 'zip code', 'suite']
            if any(keyword in text_content for keyword in address_keywords):
                data['local']['address_found'] = True
                
            # Check for map embed
            if soup.find('iframe', src=re.compile(r'google\.com/maps')):
                data['local']['map_embed'] = True
                
            if data['local']['phone_found'] or data['local']['address_found'] or data['local']['map_embed']:
                data['local']['has_local_signals'] = True
                
            print(f"  International: Found {len(data['international']['hreflang_tags'])} hreflang tags")
            print(f"  Local: Phone={'Yes' if data['local']['phone_found'] else 'No'}, Address={'Yes' if data['local']['address_found'] else 'No'}")
            
    except Exception as e:
        print(f"  Error analyzing SEO signals: {e}")
        
    return data


def get_project_folder():
    """Determine project folder based on domain"""
    # Dynamic naming: example.com -> Example Com
    project_name = TARGET_DOMAIN.replace('.', ' ').title()
        
    path = os.path.join("reports", project_name)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def save_results():
    """Save results to JSON file"""
    output_dir = get_project_folder()
    output_file = os.path.join(output_dir, f"analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to: {output_file}")
    
    # Save a 'latest' pointer for other scripts to find
    with open('.latest_project', 'w') as f:
        f.write(output_dir)
        
    return output_file



# Main execution
if __name__ == "__main__":
    print("="*60)
    print("KEYWORD GAP ANALYSIS - DATA COLLECTION")
    print(f"Target: {TARGET_DOMAIN}")
    print(f"Competitors: {len(COMPETITORS)}")
    print("="*60)

    # 1. Analyze target sitemap
    print("\n" + "="*60)
    print("STEP 1: SITEMAP ANALYSIS")
    print("="*60)
    results['sitemap_analysis'][TARGET_DOMAIN] = fetch_sitemap(TARGET_DOMAIN)

    # 2. Find social profiles
    print("\n" + "="*60)
    print("STEP 2: SOCIAL PROFILE DISCOVERY")
    print("="*60)
    results['social_profiles'][TARGET_DOMAIN] = find_social_profiles(TARGET_DOMAIN)

    # 3. Local & International Analysis
    print("\n" + "="*60)
    print("STEP 3: LOCAL & INTERNATIONAL SEO")
    print("="*60)
    results['local_international'][TARGET_DOMAIN] = analyze_local_international_seo(TARGET_DOMAIN)

    # Save intermediate results
    print("\n" + "="*60)
    print("SAVING INITIAL RESULTS")
    print("="*60)
    output_file = save_results()

    print("\n" + "="*60)
    print("INITIAL DATA COLLECTION COMPLETE")
    print("="*60)
    print(f"\nNext steps:")
    print("1. Use DataForSEO API to collect domain metrics")
    print("2. Use DataForSEO API to collect ranked keywords")
    print("3. Perform keyword gap analysis")
    print("4. Generate HTML report")
    print(f"\nData saved to: {output_file}")
