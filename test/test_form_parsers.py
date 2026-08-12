"""Tests for shared form/API parsers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.form_parsers import build_flow_from_json


class TestFormParsers(unittest.TestCase):
    def test_build_flow_from_json_supports_partial_update(self):
        existing = {
            'name': 'Monitor Flow',
            'trigger_type': 'on_change',
            'endpoint': 'https://example.com/status',
            'field': 'status',
            'message_template': 'Status: {value}',
            'active': True,
            'poll_interval': 10,
        }

        updated = build_flow_from_json({'active': False, 'poll_interval': 25}, existing_flow=existing)

        self.assertEqual(updated['name'], 'Monitor Flow')
        self.assertFalse(updated['active'])
        self.assertEqual(updated['poll_interval'], 25)
        self.assertEqual(updated['endpoint'], 'https://example.com/status')


if __name__ == '__main__':
    unittest.main()
