#!/usr/bin/env python3
"""Detailed test for get_nested_value function"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test data
test_data = {
    "series": {
        "images": [
            {
                "remoteUrl": "https://artworks.thetvdb.com/banners/posters/81189-1.jpg"
            }
        ]
    }
}

print("=== Testing get_nested_value function ===")
print("Test data:", test_data)
print("Direct access:", test_data["series"]["images"][0]["remoteUrl"])

# Import the function
try:
    from functions.utils import get_nested_value
    
    # Test step by step
    print("\n=== Step by step testing ===")
    
    # Test 1: Simple access
    result1 = get_nested_value(test_data, "series")
    print("1. series:", result1)
    
    # Test 2: Nested access
    result2 = get_nested_value(test_data, "series.images")
    print("2. series.images:", result2)
    
    # Test 3: Array access
    result3 = get_nested_value(test_data, "series.images.0")
    print("3. series.images.0:", result3)
    
    # Test 4: Final access
    result4 = get_nested_value(test_data, "series.images.0.remoteUrl")
    print("4. series.images.0.remoteUrl:", result4)
    
    # Test 5: Expected result
    expected = "https://artworks.thetvdb.com/banners/posters/81189-1.jpg"
    print("5. Expected:", expected)
    print("6. Success:", result4 == expected)
    
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc() 