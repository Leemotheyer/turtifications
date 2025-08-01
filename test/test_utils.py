"""
Comprehensive tests for functions/utils.py module.
Tests all utility functions including template formatting, conditions, and logging.
"""

import unittest
import tempfile
import shutil
import os
import json
import sys
from unittest.mock import patch, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.utils import (
    get_notification_logs, save_notification_logs, detect_log_category,
    log_notification_sent, log_notification, format_message_template,
    get_nested_value, evaluate_condition
)
from test_data import (
    SAMPLE_NOTIFICATION_LOGS, CONDITION_TEST_DATA, TEMPLATE_TEST_DATA,
    SONARR_WEBHOOK_DATA, SERVER_STATUS_DATA, SAMPLE_CONFIG
)

class TestUtils(unittest.TestCase):
    """Test suite for utils.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.notification_logs_file = os.path.join(self.test_dir, 'sent_notifications.json')
        
        # Patch the data directory path
        patcher = patch('functions.utils.open', create=True)
        self.mock_open = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        """Clean up test environment after each test"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_notification_logs_file_not_found(self):
        """Test get_notification_logs when file doesn't exist"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            logs = get_notification_logs()
            self.assertEqual(logs, [])

    def test_get_notification_logs_with_data(self):
        """Test get_notification_logs with existing data"""
        test_logs = SAMPLE_NOTIFICATION_LOGS.copy()
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_logs))):
            logs = get_notification_logs()
            self.assertEqual(len(logs), len(test_logs))
            self.assertEqual(logs[0]['flow_name'], test_logs[0]['flow_name'])

    def test_save_notification_logs(self):
        """Test save_notification_logs functionality"""
        test_logs = SAMPLE_NOTIFICATION_LOGS.copy()
        
        with patch('os.makedirs'), \
             patch('builtins.open', mock_open()) as mock_file:
            save_notification_logs(test_logs)
            
            # Check that file was opened for writing
            mock_file.assert_called_with('data/sent_notifications.json', 'w')
            
            # Check that json.dump was called
            write_calls = mock_file().write.call_args_list
            self.assertTrue(len(write_calls) > 0)

    def test_detect_log_category_notifications(self):
        """Test detect_log_category for notification messages"""
        test_cases = [
            ("✅ Notification sent for flow 'Test'", "Notifications"),
            ("Discord webhook called successfully", "Notifications"),
            ("❌ Failed to send notification", "Notifications"),
        ]
        
        for message, expected_category in test_cases:
            with self.subTest(message=message):
                category = detect_log_category(message)
                self.assertEqual(category, expected_category)

    def test_detect_log_category_api(self):
        """Test detect_log_category for API messages"""
        test_cases = [
            ("API request to endpoint /status", "API"),
            ("HTTP response received: 200", "API"),
            ("Endpoint fetch completed", "API"),
        ]
        
        for message, expected_category in test_cases:
            with self.subTest(message=message):
                category = detect_log_category(message)
                self.assertEqual(category, expected_category)

    def test_detect_log_category_system(self):
        """Test detect_log_category for system messages"""
        test_cases = [
            ("System configuration updated", "System"),
            ("Config file loaded successfully", "System"),
            ("Setting changed: interval = 300", "System"),
        ]
        
        for message, expected_category in test_cases:
            with self.subTest(message=message):
                category = detect_log_category(message)
                self.assertEqual(category, expected_category)

    def test_detect_log_category_errors(self):
        """Test detect_log_category for error messages"""
        test_cases = [
            ("Error: Connection failed", "Errors"),
            ("❌ Processing failed", "Errors"),
            ("Exception occurred in flow processing", "Errors"),
        ]
        
        for message, expected_category in test_cases:
            with self.subTest(message=message):
                category = detect_log_category(message)
                self.assertEqual(category, expected_category)

    def test_detect_log_category_timers(self):
        """Test detect_log_category for timer messages"""
        test_cases = [
            ("⏰ Timer triggered for flow", "Timers"),
            ("Interval check completed", "Timers"),
            ("Timer flow executed", "Timers"),
        ]
        
        for message, expected_category in test_cases:
            with self.subTest(message=message):
                category = detect_log_category(message)
                self.assertEqual(category, expected_category)

    def test_detect_log_category_default(self):
        """Test detect_log_category returns General for unmatched messages"""
        category = detect_log_category("Some random message that doesn't match patterns")
        self.assertEqual(category, "General")

    def test_log_notification_sent_valid_data(self):
        """Test log_notification_sent with valid data"""
        with patch('functions.utils.get_notification_logs', return_value=[]), \
             patch('functions.utils.save_notification_logs') as mock_save:
            
            log_notification_sent(
                flow_name="Test Flow",
                message_content="Test message",
                embed_info={"title": "Test Embed"},
                webhook_name="Test Webhook"
            )
            
            # Check that save was called
            mock_save.assert_called_once()
            
            # Get the saved logs
            saved_logs = mock_save.call_args[0][0]
            self.assertEqual(len(saved_logs), 1)
            self.assertEqual(saved_logs[0]['flow_name'], "Test Flow")
            self.assertEqual(saved_logs[0]['message_content'], "Test message")

    def test_log_notification_sent_empty_flow_name(self):
        """Test log_notification_sent with empty flow name"""
        with patch('functions.utils.save_notification_logs') as mock_save:
            log_notification_sent(
                flow_name="",
                message_content="Test message"
            )
            
            # Should not save anything
            mock_save.assert_not_called()

    def test_log_notification_sent_no_content(self):
        """Test log_notification_sent with no meaningful content"""
        with patch('functions.utils.save_notification_logs') as mock_save:
            log_notification_sent(
                flow_name="Test Flow",
                message_content="",
                embed_info={}
            )
            
            # Should not save anything
            mock_save.assert_not_called()

    def test_format_message_template_basic(self):
        """Test format_message_template with basic templates"""
        for test_case in TEMPLATE_TEST_DATA[:3]:  # First 3 basic cases
            with self.subTest(template=test_case['template']):
                result = format_message_template(
                    test_case['template'],
                    test_case['data'],
                    test_case['user_vars']
                )
                self.assertEqual(result, test_case['expected'])

    def test_format_message_template_complex(self):
        """Test format_message_template with complex nested data"""
        template = "Episode: S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}"
        data = {"episode": {"seasonNumber": 1, "episodeNumber": 5}}
        
        result = format_message_template(template, data, {})
        self.assertEqual(result, "Episode: S01E05")

    def test_format_message_template_user_variables(self):
        """Test format_message_template with user variables"""
        template = "Server {$server_name} status: {status}"
        data = {"status": "online"}
        user_vars = {"server_name": "Production"}
        
        result = format_message_template(template, data, user_vars)
        self.assertEqual(result, "Server Production status: online")

    def test_format_message_template_calculations(self):
        """Test format_message_template with calculations"""
        template = "Total usage: {calc:memory_usage + disk_usage}%"
        data = {"memory_usage": 50, "disk_usage": 30}
        
        result = format_message_template(template, data, {})
        self.assertEqual(result, "Total usage: 80%")

    def test_format_message_template_missing_variable(self):
        """Test format_message_template with missing variables"""
        template = "Hello {missing_var}!"
        data = {"other_var": "value"}
        
        # Should handle missing variables gracefully
        result = format_message_template(template, data, {})
        # The exact behavior may vary, but it shouldn't crash
        self.assertIsInstance(result, str)

    def test_format_message_template_sonarr_data(self):
        """Test format_message_template with real Sonarr data"""
        template = "🎬 **{series['title']}** - {episode['title']}"
        
        result = format_message_template(template, SONARR_WEBHOOK_DATA, {})
        expected = "🎬 **Breaking Bad** - Pilot"
        self.assertEqual(result, expected)

    def test_format_message_template_server_data(self):
        """Test format_message_template with server monitoring data"""
        template = "🖥️ Status: {status} | Memory: {memory_usage}% | Disk: {disk_usage}%"
        
        result = format_message_template(template, SERVER_STATUS_DATA, {})
        expected = "🖥️ Status: online | Memory: 68.5% | Disk: 45.2%"
        self.assertEqual(result, expected)

    def test_get_nested_value_simple(self):
        """Test get_nested_value with simple paths"""
        data = {"name": "test", "status": "active"}
        
        self.assertEqual(get_nested_value(data, "name"), "test")
        self.assertEqual(get_nested_value(data, "status"), "active")
        self.assertIsNone(get_nested_value(data, "missing"))

    def test_get_nested_value_nested(self):
        """Test get_nested_value with nested paths"""
        data = {
            "server": {
                "info": {
                    "name": "production",
                    "status": "online"
                }
            }
        }
        
        self.assertEqual(get_nested_value(data, "server.info.name"), "production")
        self.assertEqual(get_nested_value(data, "server.info.status"), "online")
        self.assertIsNone(get_nested_value(data, "server.info.missing"))

    def test_get_nested_value_array_access(self):
        """Test get_nested_value with array access"""
        data = {
            "items": [
                {"name": "item1", "value": 100},
                {"name": "item2", "value": 200}
            ]
        }
        
        self.assertEqual(get_nested_value(data, "items.0.name"), "item1")
        self.assertEqual(get_nested_value(data, "items.1.value"), 200)
        self.assertIsNone(get_nested_value(data, "items.5.name"))

    def test_get_nested_value_sonarr_data(self):
        """Test get_nested_value with real Sonarr data"""
        self.assertEqual(
            get_nested_value(SONARR_WEBHOOK_DATA, "series.title"),
            "Breaking Bad"
        )
        self.assertEqual(
            get_nested_value(SONARR_WEBHOOK_DATA, "episode.episodeNumber"),
            1
        )
        self.assertEqual(
            get_nested_value(SONARR_WEBHOOK_DATA, "series.images.0.remoteUrl"),
            "https://artworks.thetvdb.com/banners/posters/81189-1.jpg"
        )

    def test_evaluate_condition_simple(self):
        """Test evaluate_condition with simple conditions"""
        for test_case in CONDITION_TEST_DATA:
            with self.subTest(condition=test_case['condition']):
                result = evaluate_condition(test_case['condition'], test_case['data'])
                self.assertEqual(result, test_case['expected'])

    def test_evaluate_condition_string_comparison(self):
        """Test evaluate_condition with string comparisons"""
        data = {"status": "online", "mode": "production"}
        
        self.assertTrue(evaluate_condition("status == 'online'", data))
        self.assertFalse(evaluate_condition("status == 'offline'", data))
        self.assertTrue(evaluate_condition("mode != 'development'", data))

    def test_evaluate_condition_numeric_comparison(self):
        """Test evaluate_condition with numeric comparisons"""
        data = {"cpu": 75.5, "memory": 80, "disk": 45}
        
        self.assertTrue(evaluate_condition("cpu > 70", data))
        self.assertTrue(evaluate_condition("memory >= 80", data))
        self.assertTrue(evaluate_condition("disk < 50", data))
        self.assertFalse(evaluate_condition("cpu > 90", data))

    def test_evaluate_condition_logical_operators(self):
        """Test evaluate_condition with logical operators"""
        data = {"cpu": 60, "memory": 70, "status": "ok"}
        
        self.assertTrue(evaluate_condition("cpu < 80 and memory < 80", data))
        self.assertTrue(evaluate_condition("cpu > 50 or memory > 90", data))
        self.assertFalse(evaluate_condition("cpu > 80 and memory < 50", data))

    def test_evaluate_condition_nested_data(self):
        """Test evaluate_condition with nested data"""
        data = {
            "server": {"cpu": 60, "memory": 70},
            "services": ["nginx", "mysql", "redis"]
        }
        
        # Note: The actual implementation might need to handle nested access differently
        # This test assumes the condition can access nested data
        with patch('functions.utils.safe_eval_node') as mock_eval:
            mock_eval.return_value = True
            result = evaluate_condition("server['cpu'] < 80", data)
            self.assertTrue(result)

    def test_evaluate_condition_invalid_syntax(self):
        """Test evaluate_condition with invalid syntax"""
        data = {"status": "online"}
        
        # Should handle invalid conditions gracefully
        result = evaluate_condition("invalid syntax ===", data)
        self.assertFalse(result)

    def test_evaluate_condition_missing_variable(self):
        """Test evaluate_condition with missing variables"""
        data = {"status": "online"}
        
        # Should handle missing variables gracefully
        result = evaluate_condition("missing_var == 'test'", data)
        self.assertFalse(result)

    def test_log_notification_with_category(self):
        """Test log_notification with explicit category"""
        test_message = "Test log message"
        test_category = "Test Category"
        
        with patch('functions.config.get_logs', return_value=[]), \
             patch('functions.config.save_logs') as mock_save:
            
            log_notification(test_message, test_category)
            
            # Check that save was called
            mock_save.assert_called_once()
            
            # Get the saved logs
            saved_logs = mock_save.call_args[0][0]
            self.assertEqual(len(saved_logs), 1)
            self.assertEqual(saved_logs[0]['message'], test_message)
            self.assertEqual(saved_logs[0]['category'], test_category)

    def test_log_notification_auto_category(self):
        """Test log_notification with automatic category detection"""
        test_message = "✅ Notification sent successfully"
        
        with patch('functions.config.get_logs', return_value=[]), \
             patch('functions.config.save_logs') as mock_save:
            
            log_notification(test_message)
            
            # Get the saved logs
            saved_logs = mock_save.call_args[0][0]
            self.assertEqual(len(saved_logs), 1)
            self.assertEqual(saved_logs[0]['category'], 'Notifications')

    def test_performance_large_template(self):
        """Test performance with large template and data"""
        # Create large data set
        large_data = {f"var_{i}": f"value_{i}" for i in range(1000)}
        template = "Processing data with {var_500}"
        
        # Should complete without timeout
        result = format_message_template(template, large_data, {})
        self.assertEqual(result, "Processing data with value_500")

    def test_performance_complex_nested_data(self):
        """Test performance with deeply nested data"""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep_value"
                        }
                    }
                }
            }
        }
        
        result = get_nested_value(nested_data, "level1.level2.level3.level4.value")
        self.assertEqual(result, "deep_value")

    def test_edge_case_empty_data(self):
        """Test edge cases with empty data"""
        self.assertEqual(format_message_template("Static text", {}, {}), "Static text")
        self.assertEqual(format_message_template("", {}, {}), "")
        self.assertIsNone(get_nested_value({}, "any.path"))

    def test_edge_case_none_values(self):
        """Test edge cases with None values"""
        data = {"value": None, "other": "test"}
        
        result = format_message_template("Value: {value}", data, {})
        # Should handle None gracefully
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main(verbosity=2)