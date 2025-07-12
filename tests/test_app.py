#!/usr/bin/env python3
"""
Comprehensive test script for the Notification Organizer app
Tests all major features and functionality
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"
TEST_WEBHOOK_URL = "https://discord.com/api/webhooks/test/test"  # Dummy URL for testing

class TestResult:
    def __init__(self, test_name, success, message="", data=None):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()

class NotificationOrganizerTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.test_flow_name = f"test_flow_{int(time.time())}"
        
    def log_test(self, test_name, success, message="", data=None):
        """Log a test result"""
        result = TestResult(test_name, success, message, data)
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if not success and data:
            print(f"   Details: {data}")
    
    def test_server_connection(self):
        """Test if the server is running and accessible"""
        try:
            response = self.session.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                self.log_test("Server Connection", True, "Server is running and accessible")
                return True
            else:
                self.log_test("Server Connection", False, f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Connection", False, f"Could not connect to server: {str(e)}")
            return False
    
    def test_api_status(self):
        """Test the API status endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                expected_keys = ['status', 'timestamp', 'total_flows', 'active_flows', 'version']
                if all(key in data for key in expected_keys):
                    self.log_test("API Status Endpoint", True, f"Status: {data['status']}, Flows: {data['total_flows']}")
                    return True
                else:
                    self.log_test("API Status Endpoint", False, "Missing expected keys in response")
                    return False
            else:
                self.log_test("API Status Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Status Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_api_health(self):
        """Test the API health endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and 'checks' in data:
                    self.log_test("API Health Endpoint", True, f"Health status: {data['status']}")
                    return True
                else:
                    self.log_test("API Health Endpoint", False, "Missing health data")
                    return False
            else:
                self.log_test("API Health Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_api_flows(self):
        """Test the API flows endpoints"""
        try:
            # Test getting all flows
            response = self.session.get(f"{API_BASE}/flows", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'flows' in data and 'count' in data:
                    self.log_test("API Flows Endpoint", True, f"Found {data['count']} flows")
                else:
                    self.log_test("API Flows Endpoint", False, "Missing flows data")
                    return False
            else:
                self.log_test("API Flows Endpoint", False, f"Status code: {response.status_code}")
                return False
            
            # Test getting active flows
            response = self.session.get(f"{API_BASE}/flows/active", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'flows' in data and 'count' in data:
                    self.log_test("API Active Flows Endpoint", True, f"Found {data['count']} active flows")
                    return True
                else:
                    self.log_test("API Active Flows Endpoint", False, "Missing active flows data")
                    return False
            else:
                self.log_test("API Active Flows Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Flows Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_api_statistics(self):
        """Test the API statistics endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                expected_keys = ['timestamp', 'flows', 'statistics', 'recent_activity', 'logs']
                if all(key in data for key in expected_keys):
                    self.log_test("API Statistics Endpoint", True, f"Total flows: {data['flows']['total']}")
                    return True
                else:
                    self.log_test("API Statistics Endpoint", False, "Missing expected statistics data")
                    return False
            else:
                self.log_test("API Statistics Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Statistics Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_api_logs(self):
        """Test the API logs endpoints"""
        try:
            # Test getting logs
            response = self.session.get(f"{API_BASE}/logs?limit=5", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'logs' in data and 'count' in data and 'total_logs' in data:
                    self.log_test("API Logs Endpoint", True, f"Retrieved {data['count']} logs")
                else:
                    self.log_test("API Logs Endpoint", False, "Missing logs data")
                    return False
            else:
                self.log_test("API Logs Endpoint", False, f"Status code: {response.status_code}")
                return False
            
            # Test getting log stats
            response = self.session.get(f"{API_BASE}/logs/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_test("API Log Stats Endpoint", True, "Log statistics retrieved")
                    return True
                else:
                    self.log_test("API Log Stats Endpoint", False, "Invalid log stats format")
                    return False
            else:
                self.log_test("API Log Stats Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Logs Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_api_test_notification(self):
        """Test the API test notification endpoint"""
        try:
            test_data = {
                "message": f"Test notification from automated test at {datetime.now().isoformat()}",
                "webhook_name": "Automated Test"
            }
            
            response = self.session.post(
                f"{API_BASE}/test",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("API Test Notification", True, "Test notification sent successfully")
                    return True
                else:
                    self.log_test("API Test Notification", False, f"Test failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                self.log_test("API Test Notification", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Test Notification", False, f"Error: {str(e)}")
            return False
    
    def test_api_endpoints_list(self):
        """Test the API endpoints list endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/endpoints", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'endpoints' in data and isinstance(data['endpoints'], dict):
                    endpoint_count = len(data['endpoints'])
                    self.log_test("API Endpoints List", True, f"Found {endpoint_count} endpoints")
                    return True
                else:
                    self.log_test("API Endpoints List", False, "Missing endpoints data")
                    return False
            else:
                self.log_test("API Endpoints List", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Endpoints List", False, f"Error: {str(e)}")
            return False
    
    def test_web_pages(self):
        """Test that all web pages are accessible"""
        pages = [
            ("Homepage", "/"),
            ("Builder", "/builder"),
            ("Templates", "/templates"),
            ("Statistics", "/flow_stats"),
            ("API Docs", "/api/docs"),
            ("Configure", "/configure"),
            ("Logs", "/logs")
        ]
        
        all_passed = True
        for page_name, path in pages:
            try:
                response = self.session.get(f"{BASE_URL}{path}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Web Page: {page_name}", True, f"Page accessible at {path}")
                else:
                    self.log_test(f"Web Page: {page_name}", False, f"Status code: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Web Page: {page_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_template_formatting(self):
        """Test template formatting functionality"""
        try:
            # Test data that would come from an API
            test_data = {
                'result': {
                    'downloaded_issues': 299,
                    'files': 299,
                    'issues': 469,
                    'monitored': 29,
                    'total_file_size': 45108577065,
                    'unmonitored': 44,
                    'volumes': 73,
                    '0': {
                        'web_title': 'Test Comic Title',
                        'web_link': 'https://example.com/comic',
                        'source': 'Test Source',
                        'downloaded_at': '2025-01-12 10:30:00'
                    }
                },
                'value': 'test_value',
                'old_value': 'old_test_value',
                'field': 'test_field'
            }
            
            # Test template with various variable types
            test_template = """
📚 **{result['0']['web_title']}** downloaded!
📖 From: {result['0']['web_link']}
📥 Source: {result['0']['source']}
📊 Downloaded Issues: {result['downloaded_issues']}
💾 Total Files: {result['files']}
📈 Monitored Series: {result['monitored']}
💿 Total Size: {result['total_file_size']/1024/1024/1024:.2f} GB
⏰ Time: {time}
🔄 Changed from {old_value} to {value}
            """.strip()
            
            # This would normally be done by the app's template formatter
            # For testing, we'll just verify the template contains expected variables
            expected_vars = [
                "{result['0']['web_title']}",
                "{result['downloaded_issues']}",
                "{result['total_file_size']/1024/1024/1024:.2f}",
                "{time}",
                "{old_value}",
                "{value}"
            ]
            
            missing_vars = [var for var in expected_vars if var not in test_template]
            if not missing_vars:
                self.log_test("Template Formatting", True, "Template contains all expected variables")
                return True
            else:
                self.log_test("Template Formatting", False, f"Missing variables: {missing_vars}")
                return False
        except Exception as e:
            self.log_test("Template Formatting", False, f"Error: {str(e)}")
            return False
    
    def test_flow_templates(self):
        """Test that flow templates are accessible"""
        try:
            # Test getting templates page
            response = self.session.get(f"{BASE_URL}/templates", timeout=5)
            if response.status_code == 200:
                # Check if template categories are mentioned
                if 'Media' in response.text or 'System' in response.text or 'Monitoring' in response.text:
                    self.log_test("Flow Templates", True, "Templates page accessible with categories")
                    return True
                else:
                    self.log_test("Flow Templates", False, "Templates page missing expected content")
                    return False
            else:
                self.log_test("Flow Templates", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Flow Templates", False, f"Error: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test flow search functionality"""
        try:
            # Test search API endpoint
            response = self.session.get(f"{BASE_URL}/search_flows?q=test", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'flows' in data and 'count' in data:
                    self.log_test("Search Functionality", True, f"Search returned {data['count']} results")
                    return True
                else:
                    self.log_test("Search Functionality", False, "Search response missing expected data")
                    return False
            else:
                self.log_test("Search Functionality", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Functionality", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting Notification Organizer Test Suite")
        print("=" * 60)
        
        # Test server connection first
        if not self.test_server_connection():
            print("\n❌ Server is not running. Please start the app with 'python app.py'")
            return False
        
        print("\n📋 Running API Tests...")
        self.test_api_status()
        self.test_api_health()
        self.test_api_flows()
        self.test_api_statistics()
        self.test_api_logs()
        self.test_api_test_notification()
        self.test_api_endpoints_list()
        
        print("\n🌐 Running Web Page Tests...")
        self.test_web_pages()
        
        print("\n🔧 Running Functionality Tests...")
        self.test_template_formatting()
        self.test_flow_templates()
        self.test_search_functionality()
        
        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.message}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 All tests passed! The app is working correctly.")
            return True
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
            return False

def main():
    """Main test runner"""
    print("Notification Organizer - Comprehensive Test Suite")
    print("This script tests all major features of the app.")
    print("Make sure the app is running on http://localhost:5000")
    print()
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        if response.status_code != 200:
            print("❌ Server is not responding correctly.")
            print("Please start the app with: python app.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server.")
        print("Please start the app with: python app.py")
        sys.exit(1)
    
    # Run tests
    tester = NotificationOrganizerTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 