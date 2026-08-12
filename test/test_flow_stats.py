"""Tests for flow statistics helpers."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.flow_stats import (
    duplicate_flow,
    export_flow_config,
    extract_flow_name_from_message,
    get_flow_usage_from_logs,
    import_flow_config,
)


class TestFlowStats(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'config.json')
        self.log_file = os.path.join(self.test_dir, 'notification_logs.json')
        self.config_patcher = patch('functions.config.CONFIG_FILE', self.config_file)
        self.log_patcher = patch('functions.config.LOG_FILE', self.log_file)
        self.config_patcher.start()
        self.log_patcher.start()
        self.addCleanup(self._cleanup)

        config = {
            'discord_webhook': '',
            'notification_flows': [{
                'name': 'Monitor Flow',
                'active': True,
                'trigger_type': 'on_change',
                'message_template': 'Changed',
            }],
        }
        with open(self.config_file, 'w') as handle:
            json.dump(config, handle)
        with open(self.log_file, 'w') as handle:
            json.dump([], handle)

    def _cleanup(self):
        self.config_patcher.stop()
        self.log_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extract_flow_name_from_message(self):
        message = "🔄 Change detected: Field 'status' changed from 'a' to 'b' in flow 'Monitor Flow'"
        self.assertEqual(extract_flow_name_from_message(message), 'Monitor Flow')

    def test_get_flow_usage_from_logs_counts_change_detection(self):
        logs = [{
            'timestamp': '2026-08-12 12:00:00',
            'message': "🔄 Change detected: Field 'status' changed from 'a' to 'b' in flow 'Monitor Flow'",
            'category': 'Change Detection',
        }]
        stats = get_flow_usage_from_logs(logs)
        self.assertEqual(stats['Monitor Flow']['change_runs'], 1)

    def test_duplicate_flow_returns_new_name(self):
        new_name = duplicate_flow('Monitor Flow')
        self.assertIsNotNone(new_name)
        self.assertIn('Monitor Flow_copy_', new_name)

        with open(self.config_file, 'r') as handle:
            config = json.load(handle)
        names = [flow['name'] for flow in config['notification_flows']]
        self.assertIn(new_name, names)

    def test_export_and_import_single_flow(self):
        exported = export_flow_config('Monitor Flow')
        self.assertIsNotNone(exported)
        imported_name = import_flow_config(exported)
        self.assertIn('Monitor Flow_imported_', imported_name)


if __name__ == '__main__':
    unittest.main()
