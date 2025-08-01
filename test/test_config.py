"""
Comprehensive tests for functions/config.py module.
Tests all configuration-related functions with realistic data.
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

from functions.config import (
    initialize_files, get_config, save_config, get_logs, 
    save_logs, clear_logs, get_log_stats, CONFIG_FILE, LOG_FILE
)
from test_data import SAMPLE_CONFIG, SAMPLE_LOGS

class TestConfig(unittest.TestCase):
    """Test suite for config.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_dir = tempfile.mkdtemp()
        self.original_config_file = CONFIG_FILE
        self.original_log_file = LOG_FILE
        
        # Patch the file paths to use test directory
        config_patcher = patch('functions.config.CONFIG_FILE', 
                              os.path.join(self.test_dir, 'config.json'))
        log_patcher = patch('functions.config.LOG_FILE', 
                           os.path.join(self.test_dir, 'notification_logs.json'))
        
        self.addCleanup(config_patcher.stop)
        self.addCleanup(log_patcher.stop)
        config_patcher.start()
        log_patcher.start()

    def tearDown(self):
        """Clean up test environment after each test"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialize_files_creates_directory(self):
        """Test that initialize_files creates the data directory"""
        # Remove test directory to simulate fresh start
        shutil.rmtree(self.test_dir)
        
        initialize_files()
        
        # Check that directory was created
        self.assertTrue(os.path.exists(self.test_dir))

    def test_initialize_files_creates_default_config(self):
        """Test that initialize_files creates default config file"""
        config_file = os.path.join(self.test_dir, 'config.json')
        
        initialize_files()
        
        # Check that config file exists
        self.assertTrue(os.path.exists(config_file))
        
        # Check default config content
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        expected_keys = [
            "discord_webhook", "check_interval", "log_retention",
            "notification_log_retention", "user_variables", 
            "total_notifications_sent"
        ]
        
        for key in expected_keys:
            self.assertIn(key, config)
        
        self.assertEqual(config["check_interval"], 5)
        self.assertEqual(config["log_retention"], 1000)
        self.assertEqual(config["user_variables"], {})

    def test_initialize_files_creates_empty_log_file(self):
        """Test that initialize_files creates empty log file"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        
        initialize_files()
        
        # Check that log file exists
        self.assertTrue(os.path.exists(log_file))
        
        # Check that it contains empty array
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(logs, [])

    def test_initialize_files_preserves_existing_files(self):
        """Test that initialize_files doesn't overwrite existing files"""
        config_file = os.path.join(self.test_dir, 'config.json')
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        
        # Create files with test content
        test_config = {"custom": "value"}
        test_logs = [{"test": "log"}]
        
        os.makedirs(self.test_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        with open(log_file, 'w') as f:
            json.dump(test_logs, f)
        
        initialize_files()
        
        # Check that files weren't overwritten
        with open(config_file, 'r') as f:
            config = json.load(f)
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(config, test_config)
        self.assertEqual(logs, test_logs)

    def test_get_config_returns_valid_config(self):
        """Test that get_config returns valid configuration"""
        # Initialize files first
        initialize_files()
        
        config = get_config()
        
        # Check that config is a dictionary
        self.assertIsInstance(config, dict)
        
        # Check required keys exist
        self.assertIn('user_variables', config)
        self.assertIn('discord_webhook', config)
        self.assertIn('check_interval', config)

    def test_get_config_adds_missing_user_variables(self):
        """Test that get_config adds user_variables if missing"""
        config_file = os.path.join(self.test_dir, 'config.json')
        
        # Create config without user_variables
        test_config = {
            "discord_webhook": "test",
            "check_interval": 5
        }
        
        os.makedirs(self.test_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        config = get_config()
        
        # Check that user_variables was added
        self.assertIn('user_variables', config)
        self.assertEqual(config['user_variables'], {})

    def test_save_config_writes_file(self):
        """Test that save_config writes configuration to file"""
        config_file = os.path.join(self.test_dir, 'config.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        test_config = SAMPLE_CONFIG.copy()
        
        save_config(test_config)
        
        # Check that file was written
        self.assertTrue(os.path.exists(config_file))
        
        # Check content
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config['discord_webhook'], test_config['discord_webhook'])
        self.assertEqual(saved_config['check_interval'], test_config['check_interval'])

    def test_save_config_handles_complex_last_data(self):
        """Test that save_config properly serializes complex last_data"""
        config_file = os.path.join(self.test_dir, 'config.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        test_config = {
            "notification_flows": [
                {
                    "name": "test_flow",
                    "last_data": {"complex": {"nested": "data"}}
                }
            ]
        }
        
        save_config(test_config)
        
        # Check that complex data was serialized
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        
        flow = saved_config['notification_flows'][0]
        self.assertIsInstance(flow['last_data'], str)
        
        # Check that it can be deserialized
        deserialized = json.loads(flow['last_data'])
        self.assertEqual(deserialized, {"complex": {"nested": "data"}})

    def test_get_logs_returns_list(self):
        """Test that get_logs returns a list"""
        initialize_files()
        
        logs = get_logs()
        
        self.assertIsInstance(logs, list)

    def test_get_logs_with_existing_data(self):
        """Test that get_logs returns existing log data"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        test_logs = SAMPLE_LOGS.copy()
        
        with open(log_file, 'w') as f:
            json.dump(test_logs, f)
        
        logs = get_logs()
        
        self.assertEqual(len(logs), len(test_logs))
        self.assertEqual(logs[0]['message'], test_logs[0]['message'])

    def test_save_logs_writes_file(self):
        """Test that save_logs writes logs to file"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        test_logs = SAMPLE_LOGS.copy()
        
        save_logs(test_logs)
        
        # Check that file was written
        self.assertTrue(os.path.exists(log_file))
        
        # Check content
        with open(log_file, 'r') as f:
            saved_logs = json.load(f)
        
        self.assertEqual(len(saved_logs), len(test_logs))
        self.assertEqual(saved_logs[0]['message'], test_logs[0]['message'])

    def test_clear_logs_empties_file(self):
        """Test that clear_logs empties the log file"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create file with test logs
        test_logs = SAMPLE_LOGS.copy()
        with open(log_file, 'w') as f:
            json.dump(test_logs, f)
        
        clear_logs()
        
        # Check that file is empty
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(logs, [])

    def test_get_log_stats_all_categories(self):
        """Test that get_log_stats returns stats for all categories"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create logs with different categories
        test_logs = SAMPLE_LOGS.copy()
        with open(log_file, 'w') as f:
            json.dump(test_logs, f)
        
        stats = get_log_stats()
        
        # Check that stats is a dictionary
        self.assertIsInstance(stats, dict)
        
        # Check that it contains expected categories
        expected_categories = {'Notifications', 'Change Detection', 'Timers', 'Webhooks', 'Errors', 'Testing'}
        found_categories = set(stats.keys())
        
        self.assertTrue(expected_categories.issubset(found_categories))

    def test_get_log_stats_specific_category(self):
        """Test that get_log_stats returns stats for specific category"""
        log_file = os.path.join(self.test_dir, 'notification_logs.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        test_logs = SAMPLE_LOGS.copy()
        with open(log_file, 'w') as f:
            json.dump(test_logs, f)
        
        stats = get_log_stats(category='Notifications')
        
        # Should only contain Notifications category
        self.assertIn('Notifications', stats)
        # Count should match number of notification logs
        notification_count = sum(1 for log in test_logs if log['category'] == 'Notifications')
        self.assertEqual(stats['Notifications'], notification_count)

    def test_get_log_stats_empty_logs(self):
        """Test that get_log_stats handles empty logs"""
        initialize_files()  # Creates empty log file
        
        stats = get_log_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats, {})

    def test_file_permissions_error_handling(self):
        """Test handling of file permission errors"""
        # Create a directory where config file should be, causing permission error
        config_dir = os.path.join(self.test_dir, 'config.json')
        os.makedirs(config_dir, exist_ok=True)
        
        with self.assertRaises(Exception):
            initialize_files()

    def test_json_decode_error_handling(self):
        """Test handling of malformed JSON files"""
        config_file = os.path.join(self.test_dir, 'config.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Write malformed JSON
        with open(config_file, 'w') as f:
            f.write('{"invalid": json}')
        
        with self.assertRaises(Exception):
            get_config()

    def test_large_config_handling(self):
        """Test handling of large configuration files"""
        config_file = os.path.join(self.test_dir, 'config.json')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create large config with many flows
        large_config = {
            "discord_webhook": "test",
            "notification_flows": []
        }
        
        # Add 100 test flows
        for i in range(100):
            large_config["notification_flows"].append({
                "name": f"flow_{i}",
                "active": True,
                "message_template": f"Test message {i}",
                "last_data": {"test": f"data_{i}"}
            })
        
        save_config(large_config)
        loaded_config = get_config()
        
        self.assertEqual(len(loaded_config["notification_flows"]), 100)
        self.assertEqual(loaded_config["notification_flows"][50]["name"], "flow_50")

if __name__ == '__main__':
    unittest.main(verbosity=2)