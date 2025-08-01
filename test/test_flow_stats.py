"""
Comprehensive tests for functions/flow_stats.py module.
Tests flow statistics, analytics, and management functions.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.flow_stats import (
    get_flow_statistics, get_flow_usage_from_logs, extract_flow_name_from_message,
    update_flow_stats, get_flow_success_rate, get_recent_flow_activity,
    export_flow_config, import_flow_config, duplicate_flow
)
from test_data import SAMPLE_CONFIG, SAMPLE_LOGS

class TestFlowStats(unittest.TestCase):
    """Test suite for flow_stats.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.sample_flows = SAMPLE_CONFIG["notification_flows"]
        self.sample_logs = SAMPLE_LOGS.copy()

    @patch('functions.config.get_config')
    @patch('functions.flow_stats.get_logs')
    def test_get_flow_statistics_with_existing_flows(self, mock_get_logs, mock_get_config):
        """Test get_flow_statistics with existing flows and logs"""
        mock_get_config.return_value = SAMPLE_CONFIG
        mock_get_logs.return_value = self.sample_logs
        
        stats = get_flow_statistics()
        
        self.assertIsInstance(stats, dict)
        # Should have stats for all flows in config
        for flow in self.sample_flows:
            self.assertIn(flow["name"], stats)
        
        # Check that flow info is included
        sonarr_stats = stats.get("Sonarr Downloads", {})
        self.assertEqual(sonarr_stats.get("active"), True)
        self.assertEqual(sonarr_stats.get("trigger_type"), "webhook")
        self.assertEqual(sonarr_stats.get("category"), "Media")

    @patch('functions.config.get_config')
    @patch('functions.flow_stats.get_logs')
    def test_get_flow_statistics_no_logs(self, mock_get_logs, mock_get_config):
        """Test get_flow_statistics with no logs (new flows)"""
        mock_get_config.return_value = SAMPLE_CONFIG
        mock_get_logs.return_value = []
        
        stats = get_flow_statistics()
        
        # Should still have entries for all flows with zero stats
        for flow in self.sample_flows:
            flow_stats = stats[flow["name"]]
            self.assertEqual(flow_stats["total_runs"], 0)
            self.assertEqual(flow_stats["successful_runs"], 0)
            self.assertEqual(flow_stats["failed_runs"], 0)
            self.assertIsNone(flow_stats["first_run"])
            self.assertIsNone(flow_stats["last_run"])

    def test_get_flow_usage_from_logs_various_messages(self):
        """Test get_flow_usage_from_logs with various log messages"""
        test_logs = [
            {
                "timestamp": "2024-01-15 14:30:00",
                "message": "✅ Notification sent for flow 'Sonarr Downloads'",
                "category": "Notifications"
            },
            {
                "timestamp": "2024-01-15 14:25:00", 
                "message": "⏰ Timer triggered for flow 'Server Monitoring'",
                "category": "Timers"
            },
            {
                "timestamp": "2024-01-15 14:20:00",
                "message": "🔄 Change detected for 'Server Monitoring': status changed",
                "category": "Change Detection"
            },
            {
                "timestamp": "2024-01-15 14:15:00",
                "message": "🌐 Incoming webhook for flow 'Sonarr Downloads'",
                "category": "Webhooks"
            },
            {
                "timestamp": "2024-01-15 14:10:00",
                "message": "❌ Failed to send notification for flow 'GitHub Releases'",
                "category": "Errors"
            },
            {
                "timestamp": "2024-01-15 14:05:00",
                "message": "🧪 Test notification sent for flow 'GitHub Releases'",
                "category": "Testing"
            }
        ]
        
        stats = get_flow_usage_from_logs(test_logs)
        
        # Check Sonarr Downloads stats
        sonarr_stats = stats.get("Sonarr Downloads", {})
        self.assertEqual(sonarr_stats["total_runs"], 2)  # 1 notification + 1 webhook
        self.assertEqual(sonarr_stats["webhook_runs"], 1)
        self.assertEqual(sonarr_stats["successful_runs"], 1)
        
        # Check Server Monitoring stats
        server_stats = stats.get("Server Monitoring", {})
        self.assertEqual(server_stats["total_runs"], 2)  # 1 timer + 1 change
        self.assertEqual(server_stats["timer_runs"], 1)
        self.assertEqual(server_stats["change_runs"], 1)
        
        # Check GitHub Releases stats
        github_stats = stats.get("GitHub Releases", {})
        self.assertEqual(github_stats["total_runs"], 2)  # 1 failed + 1 test
        self.assertEqual(github_stats["failed_runs"], 1)
        self.assertEqual(github_stats["test_runs"], 1)

    def test_extract_flow_name_from_message_various_patterns(self):
        """Test extract_flow_name_from_message with various message patterns"""
        test_cases = [
            ("✅ Notification sent for flow 'Test Flow'", "Test Flow"),
            ("⏰ Timer triggered for flow 'Server Monitoring'", "Server Monitoring"),
            ("🔄 Change detected for 'API Monitor': value changed", "API Monitor"),
            ("🌐 Incoming webhook for flow 'Sonarr Downloads'", "Sonarr Downloads"),
            ("❌ Failed to send notification for flow 'GitHub'", "GitHub"),
            ("🧪 Test notification sent for flow 'Test'", "Test"),
            ("Random message without flow name", None),
            ("Flow mentioned but no quotes", None)
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = extract_flow_name_from_message(message)
                self.assertEqual(result, expected)

    def test_update_flow_stats_new_flow(self):
        """Test update_flow_stats with new flow (no existing stats)"""
        flow_stats = {}
        flow_name = "New Flow"
        trigger_type = "timer"
        timestamp = "2024-01-15 14:30:00"
        
        update_flow_stats(flow_stats, flow_name, trigger_type, timestamp)
        
        self.assertIn(flow_name, flow_stats)
        stats = flow_stats[flow_name]
        self.assertEqual(stats["total_runs"], 1)
        self.assertEqual(stats["timer_runs"], 1)
        self.assertEqual(stats["first_run"], timestamp)
        self.assertEqual(stats["last_run"], timestamp)

    def test_update_flow_stats_existing_flow(self):
        """Test update_flow_stats with existing flow stats"""
        flow_stats = {
            "Existing Flow": {
                "total_runs": 5,
                "timer_runs": 3,
                "webhook_runs": 2,
                "first_run": "2024-01-14 10:00:00",
                "last_run": "2024-01-15 12:00:00"
            }
        }
        
        flow_name = "Existing Flow"
        trigger_type = "webhook"
        timestamp = "2024-01-15 14:30:00"
        
        update_flow_stats(flow_stats, flow_name, trigger_type, timestamp)
        
        stats = flow_stats[flow_name]
        self.assertEqual(stats["total_runs"], 6)
        self.assertEqual(stats["timer_runs"], 3)
        self.assertEqual(stats["webhook_runs"], 3)
        self.assertEqual(stats["first_run"], "2024-01-14 10:00:00")  # Unchanged
        self.assertEqual(stats["last_run"], timestamp)  # Updated

    def test_update_flow_stats_various_trigger_types(self):
        """Test update_flow_stats with various trigger types"""
        flow_stats = {}
        flow_name = "Test Flow"
        
        trigger_types = ["timer", "webhook", "change", "test", "unknown"]
        
        for trigger_type in trigger_types:
            update_flow_stats(flow_stats, flow_name, trigger_type, "2024-01-15 14:30:00")
        
        stats = flow_stats[flow_name]
        self.assertEqual(stats["total_runs"], 5)
        self.assertEqual(stats["timer_runs"], 1)
        self.assertEqual(stats["webhook_runs"], 1)
        self.assertEqual(stats["change_runs"], 1)
        self.assertEqual(stats["test_runs"], 1)

    @patch('functions.flow_stats.get_logs')
    def test_get_flow_success_rate_with_logs(self, mock_get_logs):
        """Test get_flow_success_rate with success and failure logs"""
        test_logs = [
            {
                "message": "✅ Notification sent for flow 'Test Flow'",
                "category": "Notifications"
            },
            {
                "message": "✅ Notification sent for flow 'Test Flow'",
                "category": "Notifications"
            },
            {
                "message": "❌ Failed to send notification for flow 'Test Flow'",
                "category": "Errors"
            },
            {
                "message": "✅ Notification sent for flow 'Other Flow'",
                "category": "Notifications"
            }
        ]
        mock_get_logs.return_value = test_logs
        
        success_rate = get_flow_success_rate("Test Flow")
        
        # 2 successes out of 3 total = 66.67%
        self.assertAlmostEqual(success_rate, 66.67, places=1)

    @patch('functions.flow_stats.get_logs')
    def test_get_flow_success_rate_no_runs(self, mock_get_logs):
        """Test get_flow_success_rate for flow with no runs"""
        mock_get_logs.return_value = []
        
        success_rate = get_flow_success_rate("Nonexistent Flow")
        
        self.assertEqual(success_rate, 0.0)

    @patch('functions.flow_stats.get_logs')
    def test_get_flow_success_rate_all_success(self, mock_get_logs):
        """Test get_flow_success_rate for flow with 100% success"""
        test_logs = [
            {
                "message": "✅ Notification sent for flow 'Perfect Flow'",
                "category": "Notifications"
            },
            {
                "message": "✅ Notification sent for flow 'Perfect Flow'",
                "category": "Notifications"
            }
        ]
        mock_get_logs.return_value = test_logs
        
        success_rate = get_flow_success_rate("Perfect Flow")
        
        self.assertEqual(success_rate, 100.0)

    @patch('functions.flow_stats.get_logs')
    def test_get_recent_flow_activity_default_hours(self, mock_get_logs):
        """Test get_recent_flow_activity with default 24 hours"""
        now = datetime.now()
        recent_time = now - timedelta(hours=12)
        old_time = now - timedelta(hours=30)
        
        test_logs = [
            {
                "timestamp": recent_time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "✅ Notification sent for flow 'Recent Flow'",
                "category": "Notifications"
            },
            {
                "timestamp": old_time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "✅ Notification sent for flow 'Old Flow'",
                "category": "Notifications"
            }
        ]
        mock_get_logs.return_value = test_logs
        
        recent_activity = get_recent_flow_activity()
        
        # Should only include recent activity
        self.assertIn("Recent Flow", [item["flow_name"] for item in recent_activity])
        self.assertNotIn("Old Flow", [item["flow_name"] for item in recent_activity])

    @patch('functions.flow_stats.get_logs')
    def test_get_recent_flow_activity_custom_hours(self, mock_get_logs):
        """Test get_recent_flow_activity with custom time range"""
        now = datetime.now()
        within_range = now - timedelta(hours=6)
        outside_range = now - timedelta(hours=15)
        
        test_logs = [
            {
                "timestamp": within_range.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "✅ Notification sent for flow 'Within Range'",
                "category": "Notifications"
            },
            {
                "timestamp": outside_range.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "✅ Notification sent for flow 'Outside Range'",
                "category": "Notifications"
            }
        ]
        mock_get_logs.return_value = test_logs
        
        recent_activity = get_recent_flow_activity(hours=12)
        
        # Should only include activity within 12 hours
        flow_names = [item["flow_name"] for item in recent_activity]
        self.assertIn("Within Range", flow_names)
        self.assertNotIn("Outside Range", flow_names)

    @patch('functions.config.get_config')
    def test_export_flow_config_single_flow(self, mock_get_config):
        """Test export_flow_config for single flow"""
        mock_get_config.return_value = SAMPLE_CONFIG
        
        result = export_flow_config("Sonarr Downloads")
        
        self.assertIsInstance(result, dict)
        self.assertIn("flows", result)
        self.assertEqual(len(result["flows"]), 1)
        self.assertEqual(result["flows"][0]["name"], "Sonarr Downloads")
        self.assertIn("export_timestamp", result)
        self.assertIn("exported_by", result)

    @patch('functions.config.get_config')
    def test_export_flow_config_all_flows(self, mock_get_config):
        """Test export_flow_config for all flows"""
        mock_get_config.return_value = SAMPLE_CONFIG
        
        result = export_flow_config()
        
        self.assertIsInstance(result, dict)
        self.assertIn("flows", result)
        self.assertEqual(len(result["flows"]), len(SAMPLE_CONFIG["notification_flows"]))
        self.assertIn("export_timestamp", result)

    @patch('functions.config.get_config')
    def test_export_flow_config_nonexistent_flow(self, mock_get_config):
        """Test export_flow_config for nonexistent flow"""
        mock_get_config.return_value = SAMPLE_CONFIG
        
        result = export_flow_config("Nonexistent Flow")
        
        self.assertIsNone(result)

    @patch('functions.config.get_config')
    @patch('functions.config.save_config')
    def test_import_flow_config_new_flows(self, mock_save_config, mock_get_config):
        """Test import_flow_config with new flows"""
        mock_get_config.return_value = {
            "notification_flows": [],
            "user_variables": {}
        }
        
        import_data = {
            "flows": [
                {
                    "name": "Imported Flow",
                    "active": True,
                    "trigger_type": "webhook",
                    "message_template": "Test message"
                }
            ]
        }
        
        result = import_flow_config(import_data)
        
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["skipped"], 0)
        mock_save_config.assert_called_once()

    @patch('functions.config.get_config')
    @patch('functions.config.save_config')
    def test_import_flow_config_existing_flows(self, mock_save_config, mock_get_config):
        """Test import_flow_config with existing flows (updates)"""
        existing_config = SAMPLE_CONFIG.copy()
        mock_get_config.return_value = existing_config
        
        import_data = {
            "flows": [
                {
                    "name": "Sonarr Downloads",  # Existing flow
                    "active": False,  # Different value
                    "trigger_type": "webhook",
                    "message_template": "Updated message"
                }
            ]
        }
        
        result = import_flow_config(import_data)
        
        self.assertEqual(result["imported"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 0)
        mock_save_config.assert_called_once()

    @patch('functions.config.get_config')
    @patch('functions.config.save_config')
    def test_import_flow_config_invalid_data(self, mock_save_config, mock_get_config):
        """Test import_flow_config with invalid data"""
        mock_get_config.return_value = {"notification_flows": []}
        
        # Missing required fields
        import_data = {
            "flows": [
                {
                    "active": True,
                    # Missing name
                }
            ]
        }
        
        result = import_flow_config(import_data)
        
        self.assertEqual(result["imported"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertIn("error", result)

    @patch('functions.config.get_config')
    @patch('functions.config.save_config')
    def test_duplicate_flow_success(self, mock_save_config, mock_get_config):
        """Test duplicate_flow with existing flow"""
        mock_get_config.return_value = SAMPLE_CONFIG
        
        result = duplicate_flow("Sonarr Downloads")
        
        self.assertTrue(result["success"])
        self.assertIn("new_name", result)
        self.assertTrue(result["new_name"].startswith("Sonarr Downloads (Copy"))
        mock_save_config.assert_called_once()

    @patch('functions.config.get_config')
    def test_duplicate_flow_nonexistent(self, mock_get_config):
        """Test duplicate_flow with nonexistent flow"""
        mock_get_config.return_value = SAMPLE_CONFIG
        
        result = duplicate_flow("Nonexistent Flow")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch('functions.config.get_config')
    @patch('functions.config.save_config')
    def test_duplicate_flow_with_existing_copy(self, mock_save_config, mock_get_config):
        """Test duplicate_flow when copy already exists"""
        config_with_copy = SAMPLE_CONFIG.copy()
        config_with_copy["notification_flows"].append({
            "name": "Sonarr Downloads (Copy)",
            "active": False,
            "trigger_type": "webhook"
        })
        mock_get_config.return_value = config_with_copy
        
        result = duplicate_flow("Sonarr Downloads")
        
        self.assertTrue(result["success"])
        # Should create "Sonarr Downloads (Copy 2)"
        self.assertIn("(Copy 2)", result["new_name"])

    def test_flow_stats_edge_cases(self):
        """Test edge cases in flow statistics"""
        # Empty logs
        stats = get_flow_usage_from_logs([])
        self.assertEqual(stats, {})
        
        # Logs with no flow names
        logs_no_flows = [
            {"message": "General system message", "timestamp": "2024-01-15 14:30:00"}
        ]
        stats = get_flow_usage_from_logs(logs_no_flows)
        self.assertEqual(stats, {})
        
        # Malformed timestamp handling
        logs_bad_timestamp = [
            {
                "message": "✅ Notification sent for flow 'Test'",
                "timestamp": "invalid-timestamp"
            }
        ]
        # Should not crash
        stats = get_flow_usage_from_logs(logs_bad_timestamp)
        self.assertIsInstance(stats, dict)

    def test_performance_large_dataset(self):
        """Test performance with large number of logs"""
        # Create large log dataset
        large_logs = []
        for i in range(1000):
            large_logs.append({
                "timestamp": f"2024-01-15 {i//60:02d}:{i%60:02d}:00",
                "message": f"✅ Notification sent for flow 'Flow {i % 10}'",
                "category": "Notifications"
            })
        
        # Should complete without timeout
        stats = get_flow_usage_from_logs(large_logs)
        
        # Should have stats for 10 different flows
        self.assertEqual(len(stats), 10)
        # Each flow should have 100 runs
        for flow_name, flow_stats in stats.items():
            self.assertEqual(flow_stats["total_runs"], 100)

if __name__ == '__main__':
    unittest.main(verbosity=2)