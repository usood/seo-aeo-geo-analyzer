#!/usr/bin/env python3
"""
Google Integrations Module
Search Console (GSC) and Analytics (GA4) Data Fetcher
Date: December 6, 2025
"""

import os
import json
import datetime
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from utils.path_manager import get_current_project_path

# Load environment variables
load_dotenv()

# Configuration
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly', 'https://www.googleapis.com/auth/analytics.readonly']

class GoogleIntegration:
    def __init__(self):
        self.creds = None
        self.gsc_service = None
        self.ga4_client = None
        self.data = {
            'gsc': {
                'top_queries': [],
                'top_pages': [],
                'totals': {'clicks': 0, 'impressions': 0, 'ctr': 0, 'position': 0},
                'indexed_pages': 0 # Placeholder
            },
            'ga4': {
                'sessions': 0,
                'users': 0,
                'engagement_rate': 0,
                'traffic_trend': []
            },
            'status': 'not_run',
            'date': datetime.datetime.now().isoformat()
        }
        self.authenticate_user()

    def authenticate_user(self):
        """Authenticate user via OAuth 2.0"""
        if os.path.exists(TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except Exception:
                self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None

            if not self.creds:
                if os.path.exists(CLIENT_SECRET_FILE):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                        self.creds = flow.run_local_server(port=0)
                        # Save credentials
                        with open(TOKEN_FILE, 'w') as token:
                            token.write(self.creds.to_json())
                        print(f"✓ Authenticated and saved token to {TOKEN_FILE}")
                    except Exception as e:
                        print(f"⚠ Authentication failed: {e}")
                else:
                    print(f"⚠ {CLIENT_SECRET_FILE} not found. Please download OAuth 2.0 Client ID JSON from Google Cloud.")


    def init_gsc(self):
        """Initialize Search Console Service"""
        if self.creds and not self.gsc_service:
            try:
                self.gsc_service = build('searchconsole', 'v1', credentials=self.creds)
                return True
            except Exception as e:
                print(f"⚠ Failed to initialize GSC service: {e}")
        return False

    def init_ga4(self):
        """Initialize GA4 Client"""
        if self.creds and not self.ga4_client:
            try:
                self.ga4_client = BetaAnalyticsDataClient(credentials=self.creds)
                return True
            except Exception as e:
                print(f"⚠ Failed to initialize GA4 client: {e}")
        return False

    def fetch_gsc_data(self, site_url, days=90):
        """Fetch Search Console Data with comparison (Default 90 days)"""
        if not self.init_gsc():
            return

        # Format site URL
        if not site_url.startswith('http') and not site_url.startswith('sc-domain:'):
            site_url = f"sc-domain:{site_url}"

        print(f"  Fetching GSC data for {site_url} (Current: last {days} days vs Previous)...")
        
        end_date = datetime.date.today()
        start_date_current = end_date - datetime.timedelta(days=days)
        
        end_date_prev = start_date_current - datetime.timedelta(days=1)
        start_date_prev = end_date_prev - datetime.timedelta(days=days)

        def get_period_data(start, end, site_url_variant):
            try:
                request = {
                    'startDate': start.isoformat(),
                    'endDate': end.isoformat(),
                    'dimensions': ['query', 'page'],
                    'rowLimit': 1000
                }
                response = self.gsc_service.searchanalytics().query(
                    siteUrl=site_url_variant, body=request
                ).execute()
                return response.get('rows', [])
            except Exception as e:
                if '403' in str(e) or 'User does not have sufficient permission' in str(e):
                    raise PermissionError(f"Permission denied for {site_url_variant}")
                print(f"    ⚠ GSC Fetch Error ({start} to {end}): {e}")
                return []

        # Try Domain Property first, then fallback to URL Prefix
        site_variants = []
        clean_domain = site_url.replace('https://', '').replace('http://', '').replace('sc-domain:', '').strip('/')
        
        # Variant 1: Domain Property (sc-domain:example.com)
        site_variants.append(f"sc-domain:{clean_domain}")
        
        # Variant 2: URL Prefix (https://example.com/)
        site_variants.append(f"https://{clean_domain}/")
        
        # Variant 3: URL Prefix without trailing slash
        site_variants.append(f"https://{clean_domain}")
            
        rows_current = []
        rows_prev = []
        
        active_url = None
        
        for variant in site_variants:
            try:
                print(f"    Trying property: {variant}...")
                rows_current = get_period_data(start_date_current, end_date, variant)
                rows_prev = get_period_data(start_date_prev, end_date_prev, variant)
                active_url = variant
                print(f"    ✓ Successfully connected to {variant}")
                break
            except PermissionError:
                print(f"    ❌ Permission denied for {variant}. Trying next...")
                continue
        
        if not active_url:
            print("    ❌ Could not access any GSC property. Check your permissions in Search Console.")
            return

        # --- Helper to aggregate data ---
        def aggregate_data(rows):
            agg = {
                'clicks': 0, 'impressions': 0, 
                'queries': {}, 'pages': {}
            }
            for row in rows:
                agg['clicks'] += row['clicks']
                agg['impressions'] += row['impressions']
                
                q = row['keys'][0]
                p = row['keys'][1]
                
                # Query agg
                if q not in agg['queries']:
                    agg['queries'][q] = {'clicks': 0, 'impressions': 0, 'position': 0, 'count': 0}
                agg['queries'][q]['clicks'] += row['clicks']
                agg['queries'][q]['impressions'] += row['impressions']
                agg['queries'][q]['position'] += row['position']
                agg['queries'][q]['count'] += 1
                
                # Page agg
                if p not in agg['pages']:
                    agg['pages'][p] = {'clicks': 0, 'impressions': 0, 'position': 0, 'count': 0}
                agg['pages'][p]['clicks'] += row['clicks']
                agg['pages'][p]['impressions'] += row['impressions']
                agg['pages'][p]['position'] += row['position']
                agg['pages'][p]['count'] += 1
            return agg

        curr = aggregate_data(rows_current)
        prev = aggregate_data(rows_prev)

        # --- Totals & Growth ---
        self.data['gsc']['totals'] = {
            'clicks': curr['clicks'],
            'clicks_prev': prev['clicks'],
            'clicks_growth': round(((curr['clicks'] - prev['clicks']) / prev['clicks'] * 100), 1) if prev['clicks'] > 0 else 0,
            
            'impressions': curr['impressions'],
            'impressions_prev': prev['impressions'],
            'impressions_growth': round(((curr['impressions'] - prev['impressions']) / prev['impressions'] * 100), 1) if prev['impressions'] > 0 else 0,
        }

        # --- Analyze Trends (Winners/Losers) ---
        trending_up = []
        trending_down = []
        optimization_needed = []

        # Query Trends
        for q, data in curr['queries'].items():
            # Only consider significant queries (> 10 clicks or > 100 impressions in current period)
            if data['clicks'] < 5 and data['impressions'] < 100:
                continue
                
            prev_data = prev['queries'].get(q, {'clicks': 0, 'impressions': 0, 'position': 0, 'count': 1})
            prev_pos = prev_data['position'] / prev_data['count'] if prev_data['count'] else 0
            curr_pos = data['position'] / data['count']
            
            click_diff = data['clicks'] - prev_data['clicks']
            
            item = {
                'keyword': q,
                'clicks': data['clicks'],
                'click_change': click_diff,
                'position': round(curr_pos, 1),
                'position_change': round(prev_pos - curr_pos, 1) # Positive means rank improved (went down in number)
            }
            
            if click_diff > 5 or item['position_change'] > 3:
                trending_up.append(item)
            elif click_diff < -5 or item['position_change'] < -3:
                trending_down.append(item)

        # Page Optimization Candidates
        for p, data in curr['pages'].items():
            ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
            
            # High Impressions, Low CTR
            if data['impressions'] > 500 and ctr < 1.0:
                optimization_needed.append({
                    'url': p,
                    'reason': 'High Impressions, Low CTR',
                    'metric': f"{ctr:.1f}% CTR ({data['impressions']} impr)"
                })
            
            # Striking Distance (Avg Pos 11-20)
            avg_pos = data['position'] / data['count']
            if 10 < avg_pos <= 20 and data['impressions'] > 100:
                optimization_needed.append({
                    'url': p,
                    'reason': 'Striking Distance (Page 2)',
                    'metric': f"Pos {avg_pos:.1f}"
                })

        # Store Results
        self.data['gsc']['trending_up'] = sorted(trending_up, key=lambda x: x['click_change'], reverse=True)[:10]
        self.data['gsc']['trending_down'] = sorted(trending_down, key=lambda x: x['click_change'])[:10]
        self.data['gsc']['optimization_needed'] = sorted(optimization_needed, key=lambda x: x['url'])[:10]
        
        # Top Queries (Standard)
        sorted_queries = sorted(
            [{'keyword': k, 'clicks': v['clicks'], 'impressions': v['impressions'], 'position': v['position']/v['count']} 
                for k, v in curr['queries'].items()],
            key=lambda x: x['clicks'], reverse=True
        )[:10]
        self.data['gsc']['top_queries'] = sorted_queries

        # Top Pages (Standard)
        sorted_pages = sorted(
            [{'url': k, 'clicks': v['clicks'], 'impressions': v['impressions']} for k, v in curr['pages'].items()],
            key=lambda x: x['clicks'], reverse=True
        )[:10]
        self.data['gsc']['top_pages'] = sorted_pages
        
        print(f"    ✓ Fetched comparison data. Growth: Clicks {self.data['gsc']['totals']['clicks_growth']}%, Impr {self.data['gsc']['totals']['impressions_growth']}%")


    def fetch_ga4_data(self, property_id, days=30):
        """Fetch GA4 Data (Organic Search)"""
        if not self.init_ga4():
            return
            
        if not property_id:
            print("    ⚠ No GA4 Property ID provided.")
            return

        print(f"  Fetching GA4 data for property {property_id}...")
        
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="sessions"), 
                    Metric(name="totalUsers"),
                    Metric(name="engagementRate")
                ],
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                dimension_filter={
                    "filter": {
                        "field_name": "sessionDefaultChannelGroup",
                        "string_filter": {
                            "match_type": "EXACT",
                            "value": "Organic Search"
                        }
                    }
                }
            )
            
            response = self.ga4_client.run_report(request)
            
            total_sessions = 0
            total_users = 0
            weighted_engagement = 0
            
            trend = []
            
            for row in response.rows:
                date_str = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                users = int(row.metric_values[1].value)
                engagement = float(row.metric_values[2].value)
                
                total_sessions += sessions
                total_users += users
                weighted_engagement += (engagement * sessions)
                
                # Format date YYYYMMDD -> YYYY-MM-DD
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                trend.append({'date': formatted_date, 'sessions': sessions})
                
            avg_engagement = (weighted_engagement / total_sessions) if total_sessions > 0 else 0
            
            self.data['ga4'] = {
                'sessions': total_sessions,
                'users': total_users,
                'engagement_rate': round(avg_engagement * 100, 1),
                'traffic_trend': sorted(trend, key=lambda x: x['date'])
            }
            
            print(f"    ✓ Fetched GA4 data: {total_sessions} organic sessions")
            
        except Exception as e:
            print(f"    ⚠ GA4 Error: {e}")
            print(f"    (Make sure service account has access to property {property_id})")

    def save_data(self):
        """Save data to JSON"""
        self.data['status'] = 'success'
        
        project_dir = get_current_project_path()
        filename = os.path.join(project_dir, 'google_data.json')
        
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✓ Google data saved to {filename}")
        return filename

def main():
    print("="*60)
    print("GOOGLE INTEGRATION (GSC & GA4)")
    print("="*60)
    
    gi = GoogleIntegration()
    
    if not gi.creds:
        print("\n❌ No valid credentials found.")
        print("1. Go to Google Cloud Console > APIs & Services > Credentials.")
        print("2. Create Credentials > OAuth 2.0 Client ID (Desktop App).")
        print("3. Download JSON and save as 'client_secret.json' in this folder.")
        print("4. Run this script again to login via browser.")
        return

    # Get config from env or use defaults
    # Ideally we load from config.yaml, but for standalone script we can use .env
    target_domain = os.getenv('TARGET_DOMAIN') 
    ga4_property_id = os.getenv('GA4_PROPERTY_ID') # e.g. '123456789'
    
    # Try loading from config.yaml if available
    try:
        import yaml
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                target_domain = config.get('target', {}).get('domain', target_domain)
                # Look for google config
                google_conf = config.get('google', {})
                ga4_property_id = google_conf.get('ga4_property_id', ga4_property_id)
    except ImportError:
        pass
        
    if not target_domain:
        print("❌ Target domain not configured. Set TARGET_DOMAIN in .env or config.yaml")
        return

    print(f"\nTarget: {target_domain}")
    print(f"GA4 Property: {ga4_property_id or 'Not set'}")
    
    gi.fetch_gsc_data(target_domain)
    if ga4_property_id:
        gi.fetch_ga4_data(ga4_property_id)
    
    gi.save_data()

if __name__ == "__main__":
    main()
