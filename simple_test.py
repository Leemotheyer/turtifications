#!/usr/bin/env python3
"""Simple test for get_nested_value function"""

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

print("Test data:", test_data)
print("Direct access:", test_data["series"]["images"][0]["remoteUrl"])

# Import and test the function
try:
    from functions.utils import get_nested_value
    result = get_nested_value(test_data, "series.images.0.remoteUrl")
    print("Function result:", result)
    print("Success:", result == "https://artworks.thetvdb.com/banners/posters/81189-1.jpg")
except Exception as e:
    print("Error:", e) 