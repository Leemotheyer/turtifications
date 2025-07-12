# Testing Guide

This document explains how to run the comprehensive test suite for the Notification Organizer app.

## Quick Test

### Windows
```bash
run_tests.bat
```

### Unix/Linux/Mac
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Manual Run
```bash
python test_app.py
```

## What the Tests Cover

### 🔌 API Tests
- **Server Connection**: Verifies the app is running
- **API Status**: Tests `/api/status` endpoint
- **API Health**: Tests `/api/health` endpoint
- **API Flows**: Tests flow listing endpoints
- **API Statistics**: Tests statistics endpoint
- **API Logs**: Tests log retrieval endpoints
- **API Test Notification**: Tests sending test notifications
- **API Endpoints List**: Tests endpoint discovery

### 🌐 Web Page Tests
- **Homepage**: Tests main page accessibility
- **Builder**: Tests flow builder page
- **Templates**: Tests templates page
- **Statistics**: Tests statistics page
- **API Docs**: Tests API documentation page
- **Configure**: Tests configuration page
- **Logs**: Tests logs page

### 🔧 Functionality Tests
- **Template Formatting**: Tests template variable support
- **Flow Templates**: Tests template system
- **Search Functionality**: Tests flow search

## Test Results

The test script provides:
- ✅ **Pass/Fail status** for each test
- 📊 **Summary statistics** (total, passed, failed, success rate)
- ❌ **Detailed error messages** for failed tests
- 🎯 **Exit codes** (0 for success, 1 for failure)

## Example Output

```
🚀 Starting Notification Organizer Test Suite
============================================================
✅ PASS Server Connection: Server is running and accessible

📋 Running API Tests...
✅ PASS API Status Endpoint: Status: running, Flows: 3
✅ PASS API Health Endpoint: Health status: healthy
...

============================================================
📊 TEST SUMMARY
============================================================
Total Tests: 20
✅ Passed: 20
❌ Failed: 0
Success Rate: 100.0%

============================================================
🎉 All tests passed! The app is working correctly.
```

## When to Run Tests

Run the test suite after:
- ✅ Making major code changes
- ✅ Adding new features
- ✅ Updating dependencies
- ✅ Before deploying to production
- ✅ When troubleshooting issues

## Troubleshooting

### Server Not Running
```
❌ Cannot connect to server.
Please start the app with: python app.py
```

**Solution**: Start the app with `python app.py` before running tests.

### Failed Tests
If tests fail, check:
1. **Server is running** on `http://localhost:5000`
2. **Discord webhook** is configured (for notification tests)
3. **No firewall** blocking localhost connections
4. **Dependencies** are installed (`pip install -r requirements.txt`)

### Specific Test Failures
- **API Tests**: Check if API endpoints are working
- **Web Page Tests**: Check if pages are accessible
- **Functionality Tests**: Check if core features work

## Continuous Integration

The test script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    python app.py &
    sleep 5
    python test_app.py
```

## Adding New Tests

To add new tests:

1. **Add test method** to `NotificationOrganizerTester` class
2. **Call the test** in `run_all_tests()` method
3. **Update this documentation** with new test details

Example:
```python
def test_new_feature(self):
    """Test new feature functionality"""
    try:
        # Test implementation
        self.log_test("New Feature", True, "Feature working correctly")
        return True
    except Exception as e:
        self.log_test("New Feature", False, f"Error: {str(e)}")
        return False
``` 