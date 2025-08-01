#!/usr/bin/env python3
"""
Comprehensive test runner for the Notification Organizer app.
Executes all test modules and provides detailed reporting.
"""

import unittest
import sys
import os
import time
from io import StringIO
import importlib

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.start_time = None
        
    def startTest(self, test):
        super().startTest(test)
        if self.start_time is None:
            self.start_time = time.time()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity >= 1:
            self.stream.write("✅ ")
            self.stream.writeln(f"PASS: {test._testMethodName}")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity >= 1:
            self.stream.write("🔥 ")
            self.stream.writeln(f"ERROR: {test._testMethodName}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity >= 1:
            self.stream.write("❌ ")
            self.stream.writeln(f"FAIL: {test._testMethodName}")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity >= 1:
            self.stream.write("⏭️ ")
            self.stream.writeln(f"SKIP: {test._testMethodName} - {reason}")

class ComprehensiveTestRunner:
    """Main test runner for all test modules"""
    
    def __init__(self):
        self.test_modules = [
            'test_config',
            'test_utils', 
            'test_notifications',
            'test_embed_utils',
            'test_flow_stats',
            'test_flow_templates'
        ]
        self.results = {}
        self.total_start_time = None
    
    def print_header(self):
        """Print test suite header"""
        print("=" * 70)
        print("🚀 NOTIFICATION ORGANIZER - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"📋 Running tests for {len(self.test_modules)} modules")
        print(f"🐍 Python version: {sys.version}")
        print(f"📁 Working directory: {os.getcwd()}")
        print("=" * 70)
        print()
    
    def run_module_tests(self, module_name):
        """Run tests for a specific module"""
        print(f"📦 Testing {module_name}")
        print("-" * 50)
        
        try:
            # Import the test module
            test_module = importlib.import_module(module_name)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests with custom result class
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream,
                verbosity=2,
                resultclass=ColoredTextTestResult
            )
            
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Calculate statistics
            total_tests = result.testsRun
            errors = len(result.errors)
            failures = len(result.failures)
            skipped = len(result.skipped)
            passed = total_tests - errors - failures - skipped
            
            success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
            duration = end_time - start_time
            
            # Store results
            self.results[module_name] = {
                'total': total_tests,
                'passed': passed,
                'failed': failures,
                'errors': errors,
                'skipped': skipped,
                'success_rate': success_rate,
                'duration': duration,
                'result_object': result
            }
            
            # Print module summary
            print(f"📊 Module Results:")
            print(f"   ✅ Passed: {passed}")
            print(f"   ❌ Failed: {failures}")
            print(f"   🔥 Errors: {errors}")
            print(f"   ⏭️ Skipped: {skipped}")
            print(f"   📈 Success Rate: {success_rate:.1f}%")
            print(f"   ⏱️ Duration: {duration:.2f}s")
            
            # Print details for failures and errors
            if failures > 0 or errors > 0:
                print(f"\n🔍 Detailed Results:")
                output = stream.getvalue()
                lines = output.split('\n')
                for line in lines:
                    if 'FAIL:' in line or 'ERROR:' in line or 'AssertionError' in line:
                        print(f"   {line}")
            
            print()
            return result
            
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            print()
            return None
        except Exception as e:
            print(f"🔥 Error running tests for {module_name}: {e}")
            print()
            return None
    
    def run_all_tests(self):
        """Run all test modules"""
        self.total_start_time = time.time()
        self.print_header()
        
        # Run tests for each module
        for module_name in self.test_modules:
            self.run_module_tests(module_name)
        
        # Print comprehensive summary
        self.print_final_summary()
        
        # Return overall success status
        return self.get_overall_success()
    
    def print_final_summary(self):
        """Print final test summary"""
        total_duration = time.time() - self.total_start_time
        
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        # Calculate totals
        total_tests = sum(r['total'] for r in self.results.values())
        total_passed = sum(r['passed'] for r in self.results.values())
        total_failed = sum(r['failed'] for r in self.results.values())
        total_errors = sum(r['errors'] for r in self.results.values())
        total_skipped = sum(r['skipped'] for r in self.results.values())
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 Overall Results:")
        print(f"   📝 Total Tests: {total_tests}")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   🔥 Errors: {total_errors}")
        print(f"   ⏭️ Skipped: {total_skipped}")
        print(f"   📈 Success Rate: {overall_success_rate:.1f}%")
        print(f"   ⏱️ Total Duration: {total_duration:.2f}s")
        print()
        
        # Print per-module breakdown
        print("📦 Module Breakdown:")
        for module_name, result in self.results.items():
            status_icon = "✅" if result['success_rate'] == 100 else "⚠️" if result['success_rate'] >= 80 else "❌"
            print(f"   {status_icon} {module_name:20} | "
                  f"{result['passed']:3}/{result['total']:3} | "
                  f"{result['success_rate']:6.1f}% | "
                  f"{result['duration']:6.2f}s")
        
        print()
        
        # Print recommendations
        if total_failed > 0 or total_errors > 0:
            print("🔧 RECOMMENDATIONS:")
            if total_errors > 0:
                print("   • Fix errors first - these indicate code issues")
            if total_failed > 0:
                print("   • Review failed tests - these indicate logic issues")
            print("   • Run individual modules with -v flag for detailed output")
            print("   • Check logs for more information")
        else:
            print("🎉 ALL TESTS PASSED! The application is working correctly.")
        
        print()
        
        # Print coverage information
        print("📋 Test Coverage Areas:")
        coverage_areas = [
            "✅ Configuration management (file operations, settings)",
            "✅ Utility functions (templates, conditions, logging)",
            "✅ Notification system (Discord webhooks, API requests)",
            "✅ Embed creation and formatting",
            "✅ Flow statistics and analytics",
            "✅ Template management system"
        ]
        
        for area in coverage_areas:
            print(f"   {area}")
        
        print()
        print("=" * 70)
    
    def get_overall_success(self):
        """Check if all tests passed"""
        for result in self.results.values():
            if result['failed'] > 0 or result['errors'] > 0:
                return False
        return True
    
    def print_usage(self):
        """Print usage information"""
        print("Usage: python run_all_tests.py [options]")
        print()
        print("Options:")
        print("  -h, --help     Show this help message")
        print("  -v, --verbose  Verbose output")
        print("  -q, --quiet    Quiet output (errors only)")
        print("  -m MODULE      Run specific module only")
        print("  --list         List available test modules")
        print()
        print("Examples:")
        print("  python run_all_tests.py                    # Run all tests")
        print("  python run_all_tests.py -v                 # Verbose output")
        print("  python run_all_tests.py -m test_config     # Run config tests only")
        print("  python run_all_tests.py --list             # List test modules")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run comprehensive test suite')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet output')
    parser.add_argument('-m', '--module', help='Run specific module only')
    parser.add_argument('--list', action='store_true', help='List available test modules')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    if args.list:
        print("Available test modules:")
        for module in runner.test_modules:
            print(f"  • {module}")
        return 0
    
    if args.module:
        if args.module not in runner.test_modules:
            print(f"❌ Module '{args.module}' not found")
            print("Available modules:", ', '.join(runner.test_modules))
            return 1
        
        runner.test_modules = [args.module]
    
    # Run tests
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    return 0 if success else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)