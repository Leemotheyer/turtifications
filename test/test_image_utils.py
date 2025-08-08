#!/usr/bin/env python3
"""
Test file for image utilities and image template functionality.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open, MagicMock
import sys
import shutil

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.image_utils import (
    download_image_to_temp, 
    cleanup_temp_file, 
    cleanup_temp_files, 
    get_image_filename_from_url
)
from functions.utils import format_message_template

class TestImageUtils(unittest.TestCase):
    
    def setUp(self):
        """Setup test environment"""
        self.test_temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_temp_dir):
            shutil.rmtree(self.test_temp_dir)
    
    def test_get_image_filename_from_url(self):
        """Test extracting filename from image URLs"""
        # Test with normal image URL
        url1 = "http://example.com/images/test.png"
        filename1 = get_image_filename_from_url(url1)
        self.assertEqual(filename1, "test.png")
        
        # Test with complex URL with parameters
        url2 = "http://example.com/api/image.jpg?size=100&format=jpg"
        filename2 = get_image_filename_from_url(url2)
        self.assertEqual(filename2, "image.jpg")
        
        # Test with URL without extension - should generate random name
        url3 = "http://example.com/api/getimage"
        filename3 = get_image_filename_from_url(url3)
        self.assertTrue(filename3.startswith("image_"))
        self.assertTrue(filename3.endswith(".png"))
    
    def test_cleanup_temp_file(self):
        """Test cleanup of temporary files"""
        # Create a temporary file
        temp_file = os.path.join(self.test_temp_dir, "test_image.png")
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        # Verify file exists
        self.assertTrue(os.path.exists(temp_file))
        
        # Cleanup file
        with patch('functions.image_utils.log_notification') as mock_log:
            cleanup_temp_file(temp_file)
        
        # Verify file is removed
        self.assertFalse(os.path.exists(temp_file))
        mock_log.assert_called()
    
    def test_cleanup_temp_files(self):
        """Test cleanup of multiple temporary files"""
        # Create multiple temporary files
        temp_files = []
        for i in range(3):
            temp_file = os.path.join(self.test_temp_dir, f"test_image_{i}.png")
            with open(temp_file, 'w') as f:
                f.write(f"test content {i}")
            temp_files.append(temp_file)
        
        # Verify all files exist
        for temp_file in temp_files:
            self.assertTrue(os.path.exists(temp_file))
        
        # Cleanup files
        with patch('functions.image_utils.log_notification') as mock_log:
            cleanup_temp_files(temp_files)
        
        # Verify all files are removed
        for temp_file in temp_files:
            self.assertFalse(os.path.exists(temp_file))
        
        # Should have logged cleanup for each file
        self.assertEqual(mock_log.call_count, 3)
    
    @patch('requests.get')
    @patch('tempfile.mkstemp')
    def test_download_image_to_temp_success(self, mock_mkstemp, mock_get):
        """Test successful image download"""
        # Setup mocks
        temp_file_path = os.path.join(self.test_temp_dir, "temp_image.png")
        mock_mkstemp.return_value = (1, temp_file_path)  # fd, path
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/png'}
        mock_response.iter_content.return_value = [b'fake image data']
        mock_get.return_value = mock_response
        
        # Mock os.fdopen for writing
        with patch('os.fdopen', mock_open()) as mock_fdopen:
            with patch('functions.image_utils.log_notification') as mock_log:
                result = download_image_to_temp("http://example.com/image.png")
        
        # Verify result
        self.assertEqual(result, temp_file_path)
        mock_get.assert_called_once()
        mock_log.assert_called()
    
    @patch('requests.get')
    def test_download_image_to_temp_failure(self, mock_get):
        """Test failed image download"""
        # Setup mock to raise exception
        mock_get.side_effect = Exception("Network error")
        
        with patch('functions.image_utils.log_notification') as mock_log:
            result = download_image_to_temp("http://example.com/image.png")
        
        # Verify result is None on failure
        self.assertIsNone(result)
        mock_log.assert_called()
    
    @patch('tempfile.mkstemp')
    @patch('requests.get')
    def test_download_image_to_temp_fd_leak_prevention(self, mock_get, mock_mkstemp):
        """Test that file descriptors are properly closed on failure"""
        # Setup mocks
        mock_fd = 123  # Mock file descriptor
        temp_file_path = "/tmp/test_image.png"
        mock_mkstemp.return_value = (mock_fd, temp_file_path)
        
        # Mock requests.get to raise an exception after mkstemp but before fdopen
        mock_get.side_effect = Exception("Network error")
        
        with patch('os.close') as mock_close, \
             patch('os.path.exists', return_value=True) as mock_exists, \
             patch('os.unlink') as mock_unlink, \
             patch('functions.image_utils.log_notification') as mock_log:
            
            result = download_image_to_temp("http://example.com/image.png")
        
        # Verify that the file descriptor was closed
        mock_close.assert_called_once_with(mock_fd)
        # Verify that os.path.exists was called to check if file exists
        mock_exists.assert_called_with(temp_file_path)
        # Verify that the temp file was removed
        mock_unlink.assert_called_once_with(temp_file_path)
        # Verify result is None on failure
        self.assertIsNone(result)
        mock_log.assert_called()


class TestImageTemplateProcessing(unittest.TestCase):
    
    def test_format_message_template_with_images(self):
        """Test message template processing with image patterns"""
        # Test template with simple image URLs
        template = "Hello {name}! Check out this image: {img:http://example.com/test.png} and another: {img:http://example.com/test2.jpg}"
        data = {"name": "John"}
        
        message, image_urls = format_message_template(template, data, extract_images=True)
        
        # Should extract images and remove from message
        expected_message = "Hello John! Check out this image:  and another: "
        self.assertEqual(message, expected_message)
        self.assertEqual(len(image_urls), 2)
        self.assertIn("http://example.com/test.png", image_urls)
        self.assertIn("http://example.com/test2.jpg", image_urls)
    
    def test_format_message_template_with_simple_variable_in_image(self):
        """Test image URLs that contain simple variables"""
        template = "Image: {img:http://example.com/image.png}"
        data = {"image_name": "testimage"}
        
        message, image_urls = format_message_template(template, data, extract_images=True)
        
        # Should process the image URL correctly
        self.assertEqual(message, "Image: ")
        self.assertEqual(len(image_urls), 1)
        self.assertEqual(image_urls[0], "http://example.com/image.png")
    
    def test_format_message_template_without_extract_images(self):
        """Test that normal template processing still works"""
        template = "Hello {name}! {img:http://example.com/test.png}"
        data = {"name": "John"}
        
        # When extract_images=False, should return just the message
        result = format_message_template(template, data, extract_images=False)
        
        # Should not extract images, just return processed template
        expected = "Hello John! {img:http://example.com/test.png}"
        self.assertEqual(result, expected)
    
    def test_format_message_template_no_images(self):
        """Test template processing when no images are present"""
        template = "Hello {name}! No images here."
        data = {"name": "John"}
        
        message, image_urls = format_message_template(template, data, extract_images=True)
        
        # Should process normally with empty image list
        self.assertEqual(message, "Hello John! No images here.")
        self.assertEqual(len(image_urls), 0)
    
    def test_format_message_template_malformed_image_pattern(self):
        """Test handling of malformed image patterns"""
        # Test with malformed pattern that won't be detected
        template = "Image: {img:no_closing_brace"
        data = {"name": "John"}
        
        message, image_urls = format_message_template(template, data, extract_images=True)
        
        # Should not detect malformed pattern as image - leaves pattern unchanged
        self.assertEqual(message, "Image: {img:no_closing_brace")
        self.assertEqual(len(image_urls), 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)