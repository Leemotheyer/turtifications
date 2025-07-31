#!/usr/bin/env python3
import sys
sys.path.append('.')

from functions.utils import format_message_template

# Simple test
template = "{{value} - {old_value}}"
data = {'value': 100, 'old_value': 80}

print(f"Template: {template}")
print(f"Data: {data}")

# Manually extract what should be captured
start_idx = template.find('{{')
end_idx = template.find('}}', start_idx + 2)
calc_expr = template[start_idx + 2:end_idx]

print(f"Extracted expression: '{calc_expr}'")
print(f"Start: {start_idx}, End: {end_idx}")

# Test the format function
result = format_message_template(template, data)
print(f"Result: {result}")