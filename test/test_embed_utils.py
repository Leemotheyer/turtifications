"""
Comprehensive tests for functions/embed_utils.py module.
Tests Discord embed creation, validation, and field formatting.
"""

import unittest
import sys
import os
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.embed_utils import (
    create_discord_embed, parse_dynamic_fields, get_nested_value,
    format_field_value, format_file_size, validate_embed_config
)
from test_data import (
    SAMPLE_EMBED_CONFIGS, SONARR_WEBHOOK_DATA, SERVER_STATUS_DATA
)

class TestEmbedUtils(unittest.TestCase):
    """Test suite for embed_utils.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.sample_data = {
            "title": "Test Movie",
            "year": 2024,
            "status": "online",
            "memory_usage": 68.5,
            "disk_usage": 45.2
        }
        
        self.user_variables = {
            "server_name": "Production Server",
            "admin_email": "admin@example.com"
        }

    def test_create_discord_embed_disabled(self):
        """Test create_discord_embed when embed is disabled"""
        embed_config = {"enabled": False}
        
        result = create_discord_embed(embed_config)
        self.assertIsNone(result)

    def test_create_discord_embed_none_config(self):
        """Test create_discord_embed with None config"""
        result = create_discord_embed(None)
        self.assertIsNone(result)

    def test_create_discord_embed_basic(self):
        """Test create_discord_embed with basic configuration"""
        embed_config = SAMPLE_EMBED_CONFIGS["basic"]
        
        result = create_discord_embed(embed_config, self.sample_data, self.user_variables)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Basic Notification")
        self.assertEqual(result["description"], "This is a basic notification")
        self.assertEqual(result["color"], 0x3498db)  # Hex color converted to int
        self.assertIn("timestamp", result)

    def test_create_discord_embed_with_template_variables(self):
        """Test create_discord_embed with template variables"""
        embed_config = SAMPLE_EMBED_CONFIGS["advanced"]
        
        with patch('functions.embed_utils.format_message_template') as mock_format:
            mock_format.side_effect = lambda template, data, user_vars: template.replace(
                "{title}", "Test Title"
            ).replace("{status}", "online").replace("{server_name}", "Production Server")
            
            result = create_discord_embed(embed_config, self.sample_data, self.user_variables)
            
            self.assertIsNotNone(result)
            # Verify format_message_template was called for title and description
            self.assertTrue(mock_format.called)

    def test_create_discord_embed_color_conversion(self):
        """Test create_discord_embed color hex to int conversion"""
        test_cases = [
            ("#ff0000", 0xff0000),  # Red
            ("#00ff00", 0x00ff00),  # Green
            ("#0000ff", 0x0000ff),  # Blue
            ("ff0000", 0xff0000),   # Red without #
            ("invalid", 0x3498db)   # Invalid color defaults to blue
        ]
        
        for color_input, expected in test_cases:
            with self.subTest(color=color_input):
                embed_config = {
                    "enabled": True,
                    "title": "Test",
                    "color": color_input
                }
                
                result = create_discord_embed(embed_config)
                self.assertEqual(result["color"], expected)

    def test_create_discord_embed_timestamp(self):
        """Test create_discord_embed timestamp handling"""
        # Test with timestamp enabled
        embed_config = {
            "enabled": True,
            "title": "Test",
            "timestamp": True
        }
        
        result = create_discord_embed(embed_config)
        self.assertIn("timestamp", result)
        
        # Test with timestamp disabled
        embed_config["timestamp"] = False
        result = create_discord_embed(embed_config)
        self.assertNotIn("timestamp", result)

    def test_create_discord_embed_footer(self):
        """Test create_discord_embed footer creation"""
        embed_config = {
            "enabled": True,
            "title": "Test",
            "footer_text": "Footer text",
            "footer_icon": "https://example.com/icon.png"
        }
        
        with patch('functions.embed_utils.format_message_template', side_effect=lambda x, y, z: x):
            result = create_discord_embed(embed_config)
            
            self.assertIn("footer", result)
            self.assertEqual(result["footer"]["text"], "Footer text")
            self.assertEqual(result["footer"]["icon_url"], "https://example.com/icon.png")

    def test_create_discord_embed_author(self):
        """Test create_discord_embed author creation"""
        embed_config = {
            "enabled": True,
            "title": "Test",
            "author_name": "Author Name",
            "author_icon": "https://example.com/author.png",
            "author_url": "https://example.com/author"
        }
        
        with patch('functions.embed_utils.format_message_template', side_effect=lambda x, y, z: x):
            result = create_discord_embed(embed_config)
            
            self.assertIn("author", result)
            self.assertEqual(result["author"]["name"], "Author Name")
            self.assertEqual(result["author"]["icon_url"], "https://example.com/author.png")
            self.assertEqual(result["author"]["url"], "https://example.com/author")

    def test_create_discord_embed_thumbnail_and_image(self):
        """Test create_discord_embed thumbnail and image URLs"""
        embed_config = {
            "enabled": True,
            "title": "Test",
            "thumbnail_url": "https://example.com/thumb.png",
            "image_url": "https://example.com/image.png"
        }
        
        with patch('functions.embed_utils.format_message_template', side_effect=lambda x, y, z: x):
            result = create_discord_embed(embed_config)
            
            self.assertIn("thumbnail", result)
            self.assertEqual(result["thumbnail"]["url"], "https://example.com/thumb.png")
            self.assertIn("image", result)
            self.assertEqual(result["image"]["url"], "https://example.com/image.png")

    def test_create_discord_embed_with_fields(self):
        """Test create_discord_embed with dynamic fields"""
        embed_config = {
            "enabled": True,
            "title": "Test",
            "fields": [
                {"name": "Field 1", "value": "Value 1", "inline": True},
                {"name": "Field 2", "value": "Value 2", "inline": False}
            ]
        }
        
        with patch('functions.embed_utils.parse_dynamic_fields') as mock_parse:
            mock_parse.return_value = [
                {"name": "Field 1", "value": "Value 1", "inline": True},
                {"name": "Field 2", "value": "Value 2", "inline": False}
            ]
            
            result = create_discord_embed(embed_config, self.sample_data, self.user_variables)
            
            self.assertIn("fields", result)
            self.assertEqual(len(result["fields"]), 2)
            mock_parse.assert_called_once()

    def test_parse_dynamic_fields_basic(self):
        """Test parse_dynamic_fields with basic field configuration"""
        fields_config = [
            {"name": "Memory", "value": "{memory_usage}%", "inline": True},
            {"name": "Disk", "value": "{disk_usage}%", "inline": True}
        ]
        
        with patch('functions.embed_utils.format_message_template') as mock_format:
            mock_format.side_effect = lambda template, data, user_vars: template.replace(
                "{memory_usage}", "68.5"
            ).replace("{disk_usage}", "45.2")
            
            result = parse_dynamic_fields(fields_config, self.sample_data, self.user_variables)
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["name"], "Memory")
            self.assertTrue(result[0]["inline"])

    def test_parse_dynamic_fields_with_format_type(self):
        """Test parse_dynamic_fields with format type"""
        fields_config = [
            {
                "name": "File Size",
                "value": "{file_size}",
                "format_type": "file_size",
                "inline": False
            }
        ]
        
        data = {"file_size": 1024000}
        
        with patch('functions.embed_utils.format_field_value') as mock_format:
            mock_format.return_value = "1.02 MB"
            
            result = parse_dynamic_fields(fields_config, data, {})
            
            self.assertEqual(len(result), 1)
            mock_format.assert_called_once_with(1024000, "file_size")

    def test_parse_dynamic_fields_empty_value(self):
        """Test parse_dynamic_fields with empty values"""
        fields_config = [
            {"name": "Test Field", "value": "", "inline": True}
        ]
        
        result = parse_dynamic_fields(fields_config, {}, {})
        
        # Should not include fields with empty values
        self.assertEqual(len(result), 0)

    def test_get_nested_value_simple(self):
        """Test get_nested_value with simple paths"""
        data = {"name": "test", "value": 123}
        
        self.assertEqual(get_nested_value(data, "name"), "test")
        self.assertEqual(get_nested_value(data, "value"), 123)
        self.assertIsNone(get_nested_value(data, "missing"))

    def test_get_nested_value_nested_dict(self):
        """Test get_nested_value with nested dictionary paths"""
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
                {"name": "item1"},
                {"name": "item2"}
            ]
        }
        
        self.assertEqual(get_nested_value(data, "items.0.name"), "item1")
        self.assertEqual(get_nested_value(data, "items.1.name"), "item2")
        self.assertIsNone(get_nested_value(data, "items.5.name"))

    def test_get_nested_value_with_real_data(self):
        """Test get_nested_value with real Sonarr webhook data"""
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

    def test_format_field_value_file_size(self):
        """Test format_field_value with file size formatting"""
        test_cases = [
            (1024, "1.00 KB"),
            (1024000, "1000.00 KB"),
            (1048576, "1.00 MB"),
            (1073741824, "1.00 GB"),
            (512, "512 B")
        ]
        
        for size_bytes, expected in test_cases:
            with self.subTest(size=size_bytes):
                result = format_field_value(size_bytes, "file_size")
                self.assertTrue(result.endswith(expected.split()[-1]))  # Check unit

    def test_format_field_value_percentage(self):
        """Test format_field_value with percentage formatting"""
        test_cases = [
            (0.75, "75.0%"),
            (0.5, "50.0%"),
            (1.0, "100.0%"),
            (75.5, "75.5%")  # Already a percentage
        ]
        
        for value, expected in test_cases:
            with self.subTest(value=value):
                result = format_field_value(value, "percentage")
                # Check that it contains a percentage
                self.assertIn("%", result)

    def test_format_field_value_default(self):
        """Test format_field_value with default formatting (no format type)"""
        test_cases = [
            ("string", "string"),
            (123, "123"),
            (45.67, "45.67"),
            (None, "N/A")
        ]
        
        for value, expected in test_cases:
            with self.subTest(value=value):
                result = format_field_value(value, None)
                self.assertEqual(result, expected)

    def test_format_file_size_various_sizes(self):
        """Test format_file_size with various file sizes"""
        test_cases = [
            (0, "0 B"),
            (512, "512 B"),
            (1024, "1.00 KB"),
            (1536, "1.50 KB"),
            (1048576, "1.00 MB"),
            (1073741824, "1.00 GB"),
            (1099511627776, "1.00 TB")
        ]
        
        for size_bytes, expected in test_cases:
            with self.subTest(size=size_bytes):
                result = format_file_size(size_bytes)
                self.assertEqual(result, expected)

    def test_format_file_size_edge_cases(self):
        """Test format_file_size with edge cases"""
        # Negative size
        self.assertEqual(format_file_size(-100), "0 B")
        
        # Very large size
        very_large = 1024 ** 5  # Petabyte
        result = format_file_size(very_large)
        self.assertIn("TB", result)  # Should still use TB as max unit

    def test_validate_embed_config_valid(self):
        """Test validate_embed_config with valid configuration"""
        valid_config = {
            "enabled": True,
            "title": "Valid Title",
            "description": "Valid description",
            "color": "#ff0000",
            "fields": [
                {"name": "Field", "value": "Value", "inline": True}
            ]
        }
        
        result = validate_embed_config(valid_config)
        self.assertTrue(result)

    def test_validate_embed_config_disabled(self):
        """Test validate_embed_config with disabled embed"""
        config = {"enabled": False}
        
        result = validate_embed_config(config)
        self.assertTrue(result)  # Disabled embeds are valid

    def test_validate_embed_config_missing_content(self):
        """Test validate_embed_config with missing title and description"""
        config = {
            "enabled": True,
            "color": "#ff0000"
        }
        
        result = validate_embed_config(config)
        self.assertFalse(result)  # Should have at least title or description

    def test_validate_embed_config_invalid_color(self):
        """Test validate_embed_config with invalid color format"""
        config = {
            "enabled": True,
            "title": "Test",
            "color": "not-a-color"
        }
        
        # Should still be valid, invalid colors are handled in creation
        result = validate_embed_config(config)
        self.assertTrue(result)

    def test_validate_embed_config_invalid_fields(self):
        """Test validate_embed_config with invalid field configuration"""
        config = {
            "enabled": True,
            "title": "Test",
            "fields": [
                {"name": "Field 1"},  # Missing value
                {"value": "Value 2"}  # Missing name
            ]
        }
        
        result = validate_embed_config(config)
        self.assertFalse(result)

    def test_embed_with_sonarr_data(self):
        """Test full embed creation with real Sonarr data"""
        embed_config = {
            "enabled": True,
            "title": "New Episode Downloaded",
            "description": "**{series['title']}** - {episode['title']}",
            "color": "#00ff00",
            "thumbnail_url": "{series['images']['0']['remoteUrl']}",
            "fields": [
                {
                    "name": "Episode",
                    "value": "S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}",
                    "inline": True
                },
                {
                    "name": "Quality",
                    "value": "{episode['quality']}",
                    "inline": True
                }
            ]
        }
        
        with patch('functions.embed_utils.format_message_template') as mock_format:
            # Mock template formatting to return expected values
            def format_side_effect(template, data, user_vars):
                if "series['title']" in template and "episode['title']" in template:
                    return "**Breaking Bad** - Pilot"
                elif "series['images']" in template:
                    return "https://artworks.thetvdb.com/banners/posters/81189-1.jpg"
                return template
            
            mock_format.side_effect = format_side_effect
            
            with patch('functions.embed_utils.parse_dynamic_fields') as mock_parse:
                mock_parse.return_value = [
                    {"name": "Episode", "value": "S01E01", "inline": True},
                    {"name": "Quality", "value": "HDTV-720p", "inline": True}
                ]
                
                result = create_discord_embed(embed_config, SONARR_WEBHOOK_DATA, {})
                
                self.assertIsNotNone(result)
                self.assertEqual(result["title"], "New Episode Downloaded")
                self.assertEqual(result["color"], 0x00ff00)
                self.assertIn("fields", result)
                self.assertEqual(len(result["fields"]), 2)

    def test_embed_with_server_monitoring_data(self):
        """Test embed creation with server monitoring data"""
        embed_config = {
            "enabled": True,
            "title": "Server Status Update",
            "description": "Server monitoring report",
            "color": "#3498db",
            "fields": [
                {
                    "name": "Memory Usage",
                    "value": "{memory_usage}%",
                    "inline": True
                },
                {
                    "name": "Disk Usage", 
                    "value": "{disk_usage}%",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "{status}",
                    "inline": True
                }
            ]
        }
        
        with patch('functions.embed_utils.format_message_template', side_effect=lambda x, y, z: x), \
             patch('functions.embed_utils.parse_dynamic_fields') as mock_parse:
            
            mock_parse.return_value = [
                {"name": "Memory Usage", "value": "68.5%", "inline": True},
                {"name": "Disk Usage", "value": "45.2%", "inline": True},
                {"name": "Status", "value": "online", "inline": True}
            ]
            
            result = create_discord_embed(embed_config, SERVER_STATUS_DATA, {})
            
            self.assertIsNotNone(result)
            self.assertIn("fields", result)
            self.assertEqual(len(result["fields"]), 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)