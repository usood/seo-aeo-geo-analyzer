
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import datetime
import json

# Add parent directory to path to import google_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_integration import GoogleIntegration

class TestGoogleIntegrationOAuth(unittest.TestCase):
    def setUp(self):
        # We need to patch authenticate_user to prevent it from running during init
        with patch('google_integration.GoogleIntegration.authenticate_user'):
            self.gi = GoogleIntegration()
            
    @patch('google_integration.InstalledAppFlow')
    @patch('google_integration.Credentials')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_authenticate_user_flow(self, mock_open, mock_path_exists, mock_creds, mock_flow):
        """Test the OAuth authentication flow"""
        
        # Scenario 1: Token file exists and is valid
        mock_path_exists.side_effect = lambda x: x == 'token.json'
        mock_valid_creds = MagicMock()
        mock_valid_creds.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_valid_creds
        
        self.gi.authenticate_user()
        self.assertEqual(self.gi.creds, mock_valid_creds)
        
        # Scenario 2: No token, but client_secret exists (Login flow)
        mock_path_exists.side_effect = lambda x: x == 'client_secret.json'
        self.gi.creds = None # Reset
        
        mock_flow_instance = MagicMock()
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        mock_new_creds = MagicMock()
        mock_new_creds.to_json.return_value = '{"token": "abc"}'
        mock_flow_instance.run_local_server.return_value = mock_new_creds
        
        self.gi.authenticate_user()
        
        mock_flow.from_client_secrets_file.assert_called_with('client_secret.json', ['https://www.googleapis.com/auth/webmasters.readonly', 'https://www.googleapis.com/auth/analytics.readonly'])
        mock_flow_instance.run_local_server.assert_called_with(port=0)
        self.assertEqual(self.gi.creds, mock_new_creds)
        
        # Check if token was saved
        mock_open.assert_called_with('token.json', 'w')
        mock_open().write.assert_called_with('{"token": "abc"}')

    @patch('google_integration.build')
    def test_fetch_gsc_data_oauth(self, mock_build):
        """Test GSC data fetching with mocked OAuth creds"""
        self.gi.creds = MagicMock() # Simulate authenticated
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock responses for current and previous periods
        current_rows = [{'keys': ['kw1', 'page1'], 'clicks': 100, 'impressions': 1000, 'position': 1.0}]
        previous_rows = [{'keys': ['kw1', 'page1'], 'clicks': 80, 'impressions': 800, 'position': 2.0}]
        
        mock_query = mock_service.searchanalytics().query.return_value
        mock_query.execute.side_effect = [{'rows': current_rows}, {'rows': previous_rows}]
        
        self.gi.fetch_gsc_data("example.com", days=90)
        
        # Verify 90-day comparison logic works
        self.assertEqual(self.gi.data['gsc']['totals']['clicks'], 100)
        self.assertEqual(self.gi.data['gsc']['totals']['clicks_prev'], 80)
        self.assertEqual(self.gi.data['gsc']['totals']['clicks_growth'], 25.0)

if __name__ == '__main__':
    unittest.main()
