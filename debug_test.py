#!/usr/bin/env python3
"""Debug script to test get_nested_value function"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from functions.utils import get_nested_value
from test.test_data import SONARR_WEBHOOK_DATA

print("Testing get_nested_value function...")
print()

# Test the specific case that's failing
print("SONARR_WEBHOOK_DATA structure:")
print(f"series.images: {SONARR_WEBHOOK_DATA['series']['images']}")
print(f"series.images[0]: {SONARR_WEBHOOK_DATA['series']['images'][0]}")
print(f"series.images[0]['remoteUrl']: {SONARR_WEBHOOK_DATA['series']['images'][0]['remoteUrl']}")
print()

# Test the function
result = get_nested_value(SONARR_WEBHOOK_DATA, "series.images.0.remoteUrl")
print(f"get_nested_value result: {result}")
print()

# Test other cases
print("Other test cases:")
print(f"series.title: {get_nested_value(SONARR_WEBHOOK_DATA, 'series.title')}")
print(f"episode.episodeNumber: {get_nested_value(SONARR_WEBHOOK_DATA, 'episode.episodeNumber')}")
print(f"missing.path: {get_nested_value(SONARR_WEBHOOK_DATA, 'missing.path')}") 