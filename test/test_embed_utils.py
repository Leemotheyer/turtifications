"""Tests for embed utilities."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.embed_utils import create_discord_embed, validate_embed_config


class TestEmbedUtils(unittest.TestCase):
    def test_validate_embed_config_accepts_minimal_embed(self):
        errors = validate_embed_config({
            'enabled': True,
            'title': 'Hello',
            'description': 'World',
            'color': '#3498db',
        })
        self.assertEqual(errors, [])

    def test_validate_embed_config_rejects_invalid_color(self):
        errors = validate_embed_config({'color': 'not-a-color'})
        self.assertTrue(any('color' in error.lower() for error in errors))

    def test_create_discord_embed_basic(self):
        embed = create_discord_embed({
            'enabled': True,
            'title': 'Status',
            'description': 'All good',
            'color': '#00ff00',
            'timestamp': False,
        }, {'status': 'ok'}, {})

        self.assertEqual(embed['title'], 'Status')
        self.assertEqual(embed['description'], 'All good')
        self.assertEqual(embed['color'], 0x00FF00)

    def test_create_discord_embed_disabled_returns_none(self):
        self.assertIsNone(create_discord_embed({'enabled': False}, {}, {}))


if __name__ == '__main__':
    unittest.main()
