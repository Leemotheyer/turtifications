"""
Comprehensive tests for functions/notifications.py module.
Tests notification sending, API requests, and endpoint monitoring.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, Mock, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.notifications import (
    extract_field_value, send_discord_notification, 
    make_api_request, check_endpoints
)
from test_data import (
    SONARR_WEBHOOK_DATA, RADARR_WEBHOOK_DATA, SERVER_STATUS_DATA,
    SAMPLE_CONFIG, SAMPLE_EMBED_CONFIGS
)

class TestNotifications(unittest.TestCase):
    """Test suite for notifications.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.sample_flow = {
            "name": "Test Flow",
            "webhook_url": "https://discord.com/api/webhooks/123/test",
            "message_template": "Test message: {status}",
            "embed_config": SAMPLE_EMBED_CONFIGS["basic"],
            "condition_enabled": False
        }

    def test_extract_field_value_simple_path(self):
        """Test extract_field_value with simple field paths"""
        data = {"status": "online", "uptime": 3600}
        
        self.assertEqual(extract_field_value(data, "status"), "online")
        self.assertEqual(extract_field_value(data, "uptime"), "3600")
        self.assertIsNone(extract_field_value(data, "missing"))

    def test_extract_field_value_nested_bracket_notation(self):
        """Test extract_field_value with bracket notation"""
        data = SONARR_WEBHOOK_DATA
        
        # Test series title
        result = extract_field_value(data, "series['title']")
        self.assertEqual(result, "Breaking Bad")
        
        # Test episode number
        result = extract_field_value(data, "episode['episodeNumber']")
        self.assertEqual(result, "1")
        
        # Test nested image URL
        result = extract_field_value(data, "series['images']['0']['remoteUrl']")
        self.assertEqual(result, "https://artworks.thetvdb.com/banners/posters/81189-1.jpg")

    def test_extract_field_value_array_access(self):
        """Test extract_field_value with array access"""
        data = {
            "items": [
                {"name": "item1", "value": 100},
                {"name": "item2", "value": 200}
            ]
        }
        
        result = extract_field_value(data, "items['0']['name']")
        self.assertEqual(result, "item1")
        
        result = extract_field_value(data, "items['1']['value']")
        self.assertEqual(result, "200")

    def test_extract_field_value_invalid_path(self):
        """Test extract_field_value with invalid paths"""
        data = {"test": "value"}
        
        # Non-existent key
        self.assertIsNone(extract_field_value(data, "missing['key']"))
        
        # Invalid array index
        self.assertIsNone(extract_field_value(data, "test['999']"))
        
        # Invalid syntax
        self.assertIsNone(extract_field_value(data, "invalid..syntax"))

    def test_extract_field_value_edge_cases(self):
        """Test extract_field_value with edge cases"""
        data = {"null_value": None, "empty_string": "", "zero": 0}
        
        # None should return None
        self.assertIsNone(extract_field_value(data, "null_value"))
        
        # Empty string should return empty string
        self.assertEqual(extract_field_value(data, "empty_string"), "")
        
        # Zero should return "0"
        self.assertEqual(extract_field_value(data, "zero"), "0")

    @patch('functions.notifications.requests.post')
    @patch('functions.config.get_config')
    def test_send_discord_notification_success(self, mock_get_config, mock_post):
        """Test successful Discord notification sending"""
        # Setup mocks
        mock_get_config.return_value = {"user_variables": {}}
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        flow = self.sample_flow.copy()
        
        with patch('functions.notifications.format_message_template', return_value="Formatted message"):
            result = send_discord_notification("Test message", flow)
            
            self.assertTrue(result)
            mock_post.assert_called_once()

    @patch('functions.config.get_config')
    def test_send_discord_notification_no_webhook(self, mock_get_config):
        """Test Discord notification with no webhook URL"""
        mock_get_config.return_value = {"discord_webhook": "", "user_variables": {}}
        
        flow = {"name": "Test Flow"}
        
        result = send_discord_notification("Test message", flow)
        self.assertFalse(result)

    @patch('functions.notifications.requests.post')
    @patch('functions.config.get_config')
    def test_send_discord_notification_with_embed(self, mock_get_config, mock_post):
        """Test Discord notification with embed"""
        mock_get_config.return_value = {"user_variables": {}}
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        flow = self.sample_flow.copy()
        flow["embed_config"]["enabled"] = True
        
        with patch('functions.notifications.format_message_template', return_value="Formatted message"), \
             patch('functions.notifications.create_discord_embed', return_value={"title": "Test Embed"}):
            
            result = send_discord_notification("Test message", flow)
            
            self.assertTrue(result)
            # Check that embed was included in the request
            call_args = mock_post.call_args
            self.assertIn('json', call_args.kwargs)
            self.assertIn('embeds', call_args.kwargs['json'])

    @patch('functions.notifications.evaluate_condition')
    @patch('functions.config.get_config')
    def test_send_discord_notification_condition_not_met(self, mock_get_config, mock_evaluate):
        """Test Discord notification when condition is not met"""
        mock_get_config.return_value = {"user_variables": {}}
        mock_evaluate.return_value = False
        
        flow = self.sample_flow.copy()
        flow["condition_enabled"] = True
        flow["condition"] = "status == 'online'"
        flow["last_data"] = '{"status": "offline"}'
        
        result = send_discord_notification("Test message", flow)
        
        # Should return True (handled) but not actually send
        self.assertTrue(result)
        mock_evaluate.assert_called_once()

    @patch('functions.notifications.evaluate_condition')
    @patch('functions.notifications.requests.post')
    @patch('functions.config.get_config')
    def test_send_discord_notification_condition_met(self, mock_get_config, mock_post, mock_evaluate):
        """Test Discord notification when condition is met"""
        mock_get_config.return_value = {"user_variables": {}}
        mock_evaluate.return_value = True
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        flow = self.sample_flow.copy()
        flow["condition_enabled"] = True
        flow["condition"] = "status == 'online'"
        flow["last_data"] = '{"status": "online"}'
        
        with patch('functions.notifications.format_message_template', return_value="Formatted message"):
            result = send_discord_notification("Test message", flow)
            
            self.assertTrue(result)
            mock_evaluate.assert_called_once()
            mock_post.assert_called_once()

    @patch('functions.notifications.requests.post')
    @patch('functions.config.get_config')
    def test_send_discord_notification_request_error(self, mock_get_config, mock_post):
        """Test Discord notification with request error"""
        mock_get_config.return_value = {"user_variables": {}}
        mock_post.side_effect = Exception("Connection error")
        
        flow = self.sample_flow.copy()
        
        with patch('functions.notifications.format_message_template', return_value="Formatted message"), \
             patch('functions.notifications.log_notification'):
            
            result = send_discord_notification("Test message", flow)
            self.assertFalse(result)

    @patch('functions.notifications.requests.get')
    def test_make_api_request_get_success(self, mock_get):
        """Test successful GET API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        
        result = make_api_request("https://api.example.com/status")
        
        self.assertEqual(result, {"status": "ok"})
        mock_get.assert_called_once_with(
            "https://api.example.com/status",
            headers=None,
            timeout=30
        )

    @patch('functions.notifications.requests.post')
    def test_make_api_request_post_with_body(self, mock_post):
        """Test POST API request with request body"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": True}
        mock_post.return_value = mock_response
        
        headers = {"Content-Type": "application/json"}
        body = {"name": "test", "value": 123}
        
        result = make_api_request(
            "https://api.example.com/create",
            headers=headers,
            request_body=body
        )
        
        self.assertEqual(result, {"created": True})
        mock_post.assert_called_once_with(
            "https://api.example.com/create",
            headers=headers,
            json=body,
            timeout=30
        )

    @patch('functions.notifications.requests.get')
    def test_make_api_request_404_error(self, mock_get):
        """Test API request with 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        result = make_api_request("https://api.example.com/missing")
        
        self.assertIsNone(result)

    @patch('functions.notifications.requests.get')
    def test_make_api_request_connection_error(self, mock_get):
        """Test API request with connection error"""
        mock_get.side_effect = Exception("Connection failed")
        
        with patch('functions.notifications.log_notification'):
            result = make_api_request("https://api.example.com/status")
            
            self.assertIsNone(result)

    @patch('functions.notifications.requests.get')
    def test_make_api_request_json_decode_error(self, mock_get):
        """Test API request with JSON decode error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"
        mock_get.return_value = mock_response
        
        with patch('functions.notifications.log_notification'):
            result = make_api_request("https://api.example.com/status")
            
            self.assertIsNone(result)

    @patch('functions.notifications.requests.get')
    def test_make_api_request_with_custom_headers(self, mock_get):
        """Test API request with custom headers"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"authenticated": True}
        mock_get.return_value = mock_response
        
        headers = {
            "Authorization": "Bearer token123",
            "User-Agent": "Test Agent"
        }
        
        result = make_api_request("https://api.example.com/secure", headers=headers)
        
        self.assertEqual(result, {"authenticated": True})
        mock_get.assert_called_once_with(
            "https://api.example.com/secure",
            headers=headers,
            timeout=30
        )

    @patch('time.sleep')
    @patch('functions.config.get_config')
    @patch('functions.notifications.make_api_request')
    @patch('functions.notifications.send_discord_notification')
    def test_check_endpoints_timer_flow(self, mock_send, mock_api, mock_get_config, mock_sleep):
        """Test check_endpoints with timer-based flow"""
        # Mock configuration with timer flow
        mock_config = {
            "notification_flows": [
                {
                    "name": "Timer Flow",
                    "active": True,
                    "trigger_type": "timer",
                    "url": "https://api.example.com/status",
                    "interval": 60,
                    "message_template": "Status: {status}",
                    "change_detection": False,
                    "last_run": None
                }
            ]
        }
        mock_get_config.return_value = mock_config
        
        # Mock API response
        mock_api.return_value = {"status": "online"}
        mock_send.return_value = True
        
        # Mock to exit after one iteration
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        with patch('functions.config.save_config'), \
             patch('functions.notifications.log_notification'):
            
            try:
                check_endpoints()
            except KeyboardInterrupt:
                pass
            
            # Verify API was called
            mock_api.assert_called()
            # Verify notification was sent
            mock_send.assert_called()

    @patch('time.sleep')
    @patch('functions.config.get_config')
    @patch('functions.notifications.make_api_request')
    @patch('functions.notifications.send_discord_notification')
    def test_check_endpoints_change_detection(self, mock_send, mock_api, mock_get_config, mock_sleep):
        """Test check_endpoints with change detection"""
        mock_config = {
            "notification_flows": [
                {
                    "name": "Change Detection Flow",
                    "active": True,
                    "trigger_type": "timer",
                    "url": "https://api.example.com/status",
                    "interval": 60,
                    "message_template": "Status changed to: {status}",
                    "change_detection": True,
                    "last_value": "offline",
                    "last_run": None
                }
            ]
        }
        mock_get_config.return_value = mock_config
        
        # Mock API response showing change
        mock_api.return_value = {"status": "online"}
        mock_send.return_value = True
        
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        with patch('functions.config.save_config'), \
             patch('functions.notifications.log_notification'):
            
            try:
                check_endpoints()
            except KeyboardInterrupt:
                pass
            
            # Should send notification due to change detection
            mock_send.assert_called()

    @patch('time.sleep')
    @patch('functions.config.get_config')
    @patch('functions.notifications.make_api_request')
    def test_check_endpoints_api_failure(self, mock_api, mock_get_config, mock_sleep):
        """Test check_endpoints with API failure"""
        mock_config = {
            "notification_flows": [
                {
                    "name": "API Flow",
                    "active": True,
                    "trigger_type": "timer",
                    "url": "https://api.example.com/status",
                    "interval": 60,
                    "message_template": "Status: {status}",
                    "last_run": None
                }
            ]
        }
        mock_get_config.return_value = mock_config
        
        # Mock API failure
        mock_api.return_value = None
        
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        with patch('functions.config.save_config'), \
             patch('functions.notifications.log_notification'):
            
            try:
                check_endpoints()
            except KeyboardInterrupt:
                pass
            
            # API should have been called despite failure
            mock_api.assert_called()

    @patch('time.sleep')
    @patch('functions.config.get_config')
    def test_check_endpoints_inactive_flow(self, mock_get_config, mock_sleep):
        """Test check_endpoints skips inactive flows"""
        mock_config = {
            "notification_flows": [
                {
                    "name": "Inactive Flow",
                    "active": False,
                    "trigger_type": "timer",
                    "url": "https://api.example.com/status",
                    "interval": 60,
                    "message_template": "Status: {status}",
                    "last_run": None
                }
            ]
        }
        mock_get_config.return_value = mock_config
        
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        with patch('functions.notifications.make_api_request') as mock_api:
            try:
                check_endpoints()
            except KeyboardInterrupt:
                pass
            
            # Should not call API for inactive flow
            mock_api.assert_not_called()

    def test_field_extraction_with_real_data(self):
        """Test field extraction with real webhook data"""
        # Test Sonarr data
        sonarr_tests = [
            ("series['title']", "Breaking Bad"),
            ("episode['title']", "Pilot"),
            ("episode['episodeNumber']", "1"),
            ("episode['seasonNumber']", "1"),
            ("series['tvdbId']", "81189")
        ]
        
        for field_path, expected in sonarr_tests:
            with self.subTest(field_path=field_path):
                result = extract_field_value(SONARR_WEBHOOK_DATA, field_path)
                self.assertEqual(result, str(expected))
        
        # Test Radarr data
        radarr_tests = [
            ("movie['title']", "The Matrix"),
            ("movie['year']", "1999"),
            ("movie['quality']", "Bluray-1080p"),
            ("movie['size']", "8192")
        ]
        
        for field_path, expected in radarr_tests:
            with self.subTest(field_path=field_path):
                result = extract_field_value(RADARR_WEBHOOK_DATA, field_path)
                self.assertEqual(result, str(expected))

    @patch('functions.notifications.requests.post')
    @patch('functions.config.get_config')
    def test_notification_with_real_webhook_data(self, mock_get_config, mock_post):
        """Test full notification flow with real webhook data"""
        mock_get_config.return_value = {"user_variables": {}}
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        # Test with Sonarr data
        flow = {
            "name": "Sonarr Downloads",
            "webhook_url": "https://discord.com/api/webhooks/123/test",
            "message_template": "🎬 **{series['title']}** - {episode['title']}",
            "last_data": json.dumps(SONARR_WEBHOOK_DATA)
        }
        
        with patch('functions.notifications.format_message_template') as mock_format:
            mock_format.return_value = "🎬 **Breaking Bad** - Pilot"
            
            result = send_discord_notification("", flow, SONARR_WEBHOOK_DATA)
            
            self.assertTrue(result)
            mock_post.assert_called_once()
            
            # Verify the template was called with the webhook data
            mock_format.assert_called_with("", SONARR_WEBHOOK_DATA, {})

if __name__ == '__main__':
    unittest.main(verbosity=2)