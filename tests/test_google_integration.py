
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import datetime

# Add parent directory to path to import google_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_integration import GoogleIntegration

class TestGoogleIntegration(unittest.TestCase):
    def setUp(self):
        self.gi = GoogleIntegration()
        # Mock credentials to bypass the file check
        self.gi.creds = MagicMock()

    @patch('google_integration.build')
    def test_fetch_gsc_data_logic(self, mock_build):
        """Test GSC data processing, growth calc, and trend detection"""
        
        # Setup Mock Service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        self.gi.init_gsc() # Initialize with the mock service
        
        # Define dates for context
        today = datetime.date.today()
        
        # --- Mock Data ---
        # We need to simulate two calls: Current Period and Previous Period
        
        # Current: 100 clicks, 1000 impressions
        # Keyword "trend_winner": 20 clicks, pos 5 (improved)
        # Page "opt_target": 0 clicks, 600 impressions (needs optimization)
        current_rows = [
            {'keys': ['trend_winner', 'page1'], 'clicks': 20, 'impressions': 200, 'position': 5.0},
            {'keys': ['stable_kw', 'page1'], 'clicks': 50, 'impressions': 200, 'position': 10.0},
            {'keys': ['opt_target_kw', 'page_needs_opt'], 'clicks': 0, 'impressions': 600, 'position': 15.0}, # High impr, low CTR
            {'keys': ['other', 'page2'], 'clicks': 30, 'impressions': 0, 'position': 0}, # remaining
        ]
        
        # Previous: 80 clicks, 800 impressions (So we expect +25% growth)
        # Keyword "trend_winner": 5 clicks, pos 10 (was worse)
        previous_rows = [
            {'keys': ['trend_winner', 'page1'], 'clicks': 5, 'impressions': 100, 'position': 10.0},
            {'keys': ['stable_kw', 'page1'], 'clicks': 50, 'impressions': 200, 'position': 10.0},
            {'keys': ['other', 'page2'], 'clicks': 25, 'impressions': 500, 'position': 0},
        ]

        # Configure mock to return current then previous rows
        mock_query = mock_service.searchanalytics().query.return_value
        mock_query.execute.side_effect = [
            {'rows': current_rows}, # Current period
            {'rows': previous_rows} # Previous period
        ]

        # Execution
        self.gi.fetch_gsc_data("example.com", days=90)
        
        # --- Assertions ---
        
        data = self.gi.data['gsc']
        
        # 1. Totals Calculation
        # Current Clicks: 20 + 50 + 0 + 30 = 100
        # Prev Clicks: 5 + 50 + 25 = 80
        # Growth: (100 - 80) / 80 = 0.25 = 25.0%
        self.assertEqual(data['totals']['clicks'], 100)
        self.assertEqual(data['totals']['clicks_prev'], 80)
        self.assertEqual(data['totals']['clicks_growth'], 25.0)
        
        # 2. Trend Detection (Trending Up)
        # "trend_winner": Clicks went 5 -> 20 (+15). Pos went 10 -> 5 (+5).
        # Should be in trending_up
        trending_keywords = [t['keyword'] for t in data['trending_up']]
        self.assertIn('trend_winner', trending_keywords)
        
        winner = next(item for item in data['trending_up'] if item['keyword'] == 'trend_winner')
        self.assertEqual(winner['click_change'], 15)
        self.assertEqual(winner['position_change'], 5.0)
        
        # 3. Optimization Needed
        # "page_needs_opt" has 600 impressions and 0 clicks (0% CTR)
        # Should be flagged
        opt_urls = [t['url'] for t in data['optimization_needed']]
        self.assertIn('page_needs_opt', opt_urls)
        
        target = next(item for item in data['optimization_needed'] if item['url'] == 'page_needs_opt')
        self.assertEqual(target['reason'], 'High Impressions, Low CTR')

    @patch('google_integration.BetaAnalyticsDataClient')
    def test_fetch_ga4_data_logic(self, mock_client_cls):
        """Test GA4 data parsing"""
        
        # Setup Mock
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        self.gi.init_ga4()
        
        # Mock Response Object structure
        # Row 1: 20230101, 100 sessions, 80 users, 0.5 engagement
        row1 = MagicMock()
        row1.dimension_values = [MagicMock(value="20230101")]
        row1.metric_values = [
            MagicMock(value="100"), # sessions
            MagicMock(value="80"),  # users
            MagicMock(value="0.5")  # engagement
        ]
        
        mock_response = MagicMock()
        mock_response.rows = [row1]
        mock_client.run_report.return_value = mock_response
        
        # Execution
        self.gi.fetch_ga4_data("123456")
        
        # --- Assertions ---
        data = self.gi.data['ga4']
        
        self.assertEqual(data['sessions'], 100)
        self.assertEqual(data['users'], 80)
        self.assertEqual(data['engagement_rate'], 50.0) # 0.5 * 100
        self.assertEqual(data['traffic_trend'][0]['date'], '2023-01-01')

if __name__ == '__main__':
    unittest.main()
