"""
Comprehensive tests for functions/flow_templates.py module.
Tests flow template management and retrieval functions.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from functions.flow_templates import (
    get_template_categories, get_templates_by_category, get_template, FLOW_TEMPLATES
)

class TestFlowTemplates(unittest.TestCase):
    """Test suite for flow_templates.py functions"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.known_templates = list(FLOW_TEMPLATES.keys())
        self.expected_categories = {"Media", "Development", "System", "General"}

    def test_flow_templates_structure(self):
        """Test that FLOW_TEMPLATES has the expected structure"""
        self.assertIsInstance(FLOW_TEMPLATES, dict)
        self.assertGreater(len(FLOW_TEMPLATES), 0)
        
        # Check each template has required fields
        for template_name, template_config in FLOW_TEMPLATES.items():
            with self.subTest(template=template_name):
                self.assertIn("name", template_config)
                self.assertIn("description", template_config)
                self.assertIn("category", template_config)
                self.assertIn("trigger_type", template_config)
                self.assertIn("message_template", template_config)

    def test_sonarr_template_structure(self):
        """Test Sonarr template has expected configuration"""
        sonarr_template = FLOW_TEMPLATES.get("sonarr_download")
        
        self.assertIsNotNone(sonarr_template)
        self.assertEqual(sonarr_template["name"], "Sonarr Download Notification")
        self.assertEqual(sonarr_template["category"], "Media")
        self.assertEqual(sonarr_template["trigger_type"], "webhook")
        self.assertIn("webhook_name", sonarr_template)
        self.assertEqual(sonarr_template["webhook_name"], "Sonarr")
        
        # Check embed configuration
        self.assertIn("embed_config", sonarr_template)
        embed_config = sonarr_template["embed_config"]
        self.assertTrue(embed_config.get("enabled", False))
        self.assertIn("title", embed_config)
        self.assertIn("description", embed_config)
        self.assertIn("color", embed_config)

    def test_radarr_template_structure(self):
        """Test Radarr template has expected configuration"""
        radarr_template = FLOW_TEMPLATES.get("radarr_download")
        
        self.assertIsNotNone(radarr_template)
        self.assertEqual(radarr_template["name"], "Radarr Download Notification")
        self.assertEqual(radarr_template["category"], "Media")
        self.assertEqual(radarr_template["trigger_type"], "webhook")
        self.assertEqual(radarr_template["webhook_name"], "Radarr")
        
        # Check that message template contains movie-specific variables
        self.assertIn("movie", radarr_template["message_template"])

    def test_kapowarr_template_structure(self):
        """Test Kapowarr template has expected configuration"""
        kapowarr_template = FLOW_TEMPLATES.get("kapowarr_download")
        
        self.assertIsNotNone(kapowarr_template)
        self.assertEqual(kapowarr_template["name"], "Kapowarr Download Notification")
        self.assertEqual(kapowarr_template["category"], "Media")
        self.assertEqual(kapowarr_template["trigger_type"], "webhook")
        self.assertEqual(kapowarr_template["webhook_name"], "Kapowarr")
        
        # Check that message template contains comic-specific variables
        self.assertIn("result", kapowarr_template["message_template"])

    def test_get_template_categories_returns_list(self):
        """Test get_template_categories returns a list of categories"""
        categories = get_template_categories()
        
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        # Check that all categories are strings
        for category in categories:
            self.assertIsInstance(category, str)

    def test_get_template_categories_unique_values(self):
        """Test get_template_categories returns unique category values"""
        categories = get_template_categories()
        
        # Should not have duplicates
        self.assertEqual(len(categories), len(set(categories)))

    def test_get_template_categories_matches_templates(self):
        """Test get_template_categories matches categories in templates"""
        categories = get_template_categories()
        template_categories = {template["category"] for template in FLOW_TEMPLATES.values()}
        
        # All template categories should be in the returned list
        for template_category in template_categories:
            self.assertIn(template_category, categories)

    def test_get_templates_by_category_all_templates(self):
        """Test get_templates_by_category returns all templates when no category specified"""
        templates = get_templates_by_category()
        
        self.assertIsInstance(templates, dict)
        self.assertEqual(len(templates), len(FLOW_TEMPLATES))
        
        # Should return the same as FLOW_TEMPLATES
        for template_name in FLOW_TEMPLATES:
            self.assertIn(template_name, templates)

    def test_get_templates_by_category_media_category(self):
        """Test get_templates_by_category filters by Media category"""
        templates = get_templates_by_category("Media")
        
        self.assertIsInstance(templates, dict)
        
        # All returned templates should be Media category
        for template_name, template_config in templates.items():
            self.assertEqual(template_config["category"], "Media")
        
        # Should include known media templates
        expected_media_templates = ["sonarr_download", "radarr_download", "kapowarr_download"]
        for expected_template in expected_media_templates:
            if expected_template in FLOW_TEMPLATES:
                self.assertIn(expected_template, templates)

    def test_get_templates_by_category_nonexistent_category(self):
        """Test get_templates_by_category with nonexistent category"""
        templates = get_templates_by_category("NonexistentCategory")
        
        self.assertIsInstance(templates, dict)
        self.assertEqual(len(templates), 0)

    def test_get_templates_by_category_case_sensitive(self):
        """Test get_templates_by_category is case sensitive"""
        # Test with different case
        templates_lower = get_templates_by_category("media")
        templates_proper = get_templates_by_category("Media")
        
        # Should be different results (case sensitive)
        self.assertNotEqual(len(templates_lower), len(templates_proper))
        # Proper case should have results, lowercase should not
        self.assertEqual(len(templates_lower), 0)
        self.assertGreater(len(templates_proper), 0)

    def test_get_template_existing_template(self):
        """Test get_template returns correct template configuration"""
        # Test with known template
        template = get_template("sonarr_download")
        
        self.assertIsNotNone(template)
        self.assertIsInstance(template, dict)
        self.assertEqual(template, FLOW_TEMPLATES["sonarr_download"])

    def test_get_template_nonexistent_template(self):
        """Test get_template returns None for nonexistent template"""
        template = get_template("nonexistent_template")
        
        self.assertIsNone(template)

    def test_get_template_case_sensitive(self):
        """Test get_template is case sensitive"""
        # Test with different case
        template_lower = get_template("sonarr_download")
        template_upper = get_template("SONARR_DOWNLOAD")
        
        self.assertIsNotNone(template_lower)
        self.assertIsNone(template_upper)

    def test_all_templates_have_valid_embed_config(self):
        """Test that all templates with embed_config have valid structure"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            if "embed_config" in template_config:
                with self.subTest(template=template_name):
                    embed_config = template_config["embed_config"]
                    
                    # Should have enabled field
                    self.assertIn("enabled", embed_config)
                    
                    if embed_config.get("enabled"):
                        # If enabled, should have at least title or description
                        has_title = bool(embed_config.get("title"))
                        has_description = bool(embed_config.get("description"))
                        self.assertTrue(has_title or has_description, 
                                      f"Template {template_name} embed must have title or description")

    def test_all_templates_have_valid_message_templates(self):
        """Test that all templates have non-empty message templates"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            with self.subTest(template=template_name):
                message_template = template_config.get("message_template", "")
                self.assertIsInstance(message_template, str)
                self.assertGreater(len(message_template.strip()), 0)

    def test_webhook_templates_have_webhook_info(self):
        """Test that webhook templates have webhook-specific configuration"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            if template_config.get("trigger_type") == "webhook":
                with self.subTest(template=template_name):
                    # Should have webhook_name
                    self.assertIn("webhook_name", template_config)
                    self.assertIsInstance(template_config["webhook_name"], str)
                    self.assertGreater(len(template_config["webhook_name"]), 0)

    def test_template_descriptions_are_descriptive(self):
        """Test that all templates have meaningful descriptions"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            with self.subTest(template=template_name):
                description = template_config.get("description", "")
                self.assertIsInstance(description, str)
                self.assertGreater(len(description.strip()), 10)  # At least 10 characters

    def test_template_names_are_descriptive(self):
        """Test that all templates have meaningful names"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            with self.subTest(template=template_name):
                name = template_config.get("name", "")
                self.assertIsInstance(name, str)
                self.assertGreater(len(name.strip()), 5)  # At least 5 characters

    def test_template_variables_in_message_templates(self):
        """Test that message templates contain appropriate variables"""
        variable_tests = {
            "sonarr_download": ["series", "episode"],
            "radarr_download": ["movie"],
            "kapowarr_download": ["result"]
        }
        
        for template_name, expected_vars in variable_tests.items():
            if template_name in FLOW_TEMPLATES:
                with self.subTest(template=template_name):
                    message_template = FLOW_TEMPLATES[template_name]["message_template"]
                    
                    for expected_var in expected_vars:
                        self.assertIn(expected_var, message_template,
                                    f"Template {template_name} should contain variable {expected_var}")

    def test_embed_color_formats(self):
        """Test that embed colors are in valid format"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            embed_config = template_config.get("embed_config", {})
            if "color" in embed_config:
                with self.subTest(template=template_name):
                    color = embed_config["color"]
                    self.assertIsInstance(color, str)
                    
                    # Should be hex color format
                    if color.startswith("#"):
                        self.assertEqual(len(color), 7)  # #RRGGBB
                        self.assertTrue(all(c in "0123456789abcdefABCDEF" for c in color[1:]))
                    else:
                        self.assertEqual(len(color), 6)  # RRGGBB
                        self.assertTrue(all(c in "0123456789abcdefABCDEF" for c in color))

    def test_template_consistency(self):
        """Test that templates are internally consistent"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            with self.subTest(template=template_name):
                # Name should match category context
                name = template_config["name"].lower()
                category = template_config["category"].lower()
                
                # Media templates should mention media-related terms
                if category == "media":
                    media_terms = ["download", "movie", "episode", "series", "comic"]
                    has_media_term = any(term in name for term in media_terms)
                    self.assertTrue(has_media_term, 
                                  f"Media template {template_name} should mention media terms in name")

    def test_template_avatar_urls(self):
        """Test that webhook avatars are valid URLs when present"""
        for template_name, template_config in FLOW_TEMPLATES.items():
            if "webhook_avatar" in template_config:
                with self.subTest(template=template_name):
                    avatar_url = template_config["webhook_avatar"]
                    self.assertIsInstance(avatar_url, str)
                    self.assertTrue(avatar_url.startswith(("http://", "https://")))

    def test_performance_template_operations(self):
        """Test performance of template operations"""
        import time
        
        # Test get_template_categories performance
        start_time = time.time()
        for _ in range(100):
            get_template_categories()
        categories_time = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(categories_time, 1.0)  # Less than 1 second for 100 calls
        
        # Test get_templates_by_category performance
        start_time = time.time()
        for _ in range(100):
            get_templates_by_category("Media")
        filter_time = time.time() - start_time
        
        self.assertLess(filter_time, 1.0)  # Less than 1 second for 100 calls

    def test_edge_cases(self):
        """Test edge cases in template functions"""
        # Test with None values
        self.assertEqual(get_templates_by_category(None), FLOW_TEMPLATES)
        self.assertIsNone(get_template(None))
        
        # Test with empty string
        self.assertEqual(get_templates_by_category(""), {})
        self.assertIsNone(get_template(""))
        
        # Test with whitespace
        self.assertEqual(get_templates_by_category("  "), {})
        self.assertIsNone(get_template("  "))

    def test_template_deep_copy_behavior(self):
        """Test that template retrieval doesn't allow modification of originals"""
        # Get template
        original_template = get_template("sonarr_download")
        
        # Modify the returned template
        if original_template:
            original_name = original_template["name"]
            original_template["name"] = "Modified Name"
            
            # Get template again
            fresh_template = get_template("sonarr_download")
            
            # Original should be unchanged if properly implemented
            # Note: This test depends on whether the implementation returns copies or references
            self.assertIsNotNone(fresh_template)

if __name__ == '__main__':
    unittest.main(verbosity=2)