#!/usr/bin/env python3

text = "{{value} - {old_value}}"

print(f"Text: {text}")
print(f"Length: {len(text)}")
print()

# Print each character with its position
for i, char in enumerate(text):
    print(f"Position {i:2d}: '{char}'")

print()

# Find {{ and }}
start_idx = text.find('{{')
print(f"{{ found at position: {start_idx}")

# Manual search for }}
for i in range(len(text) - 1):
    if text[i:i+2] == '}}':
        print(f"}} found at position: {i}")

# What should be extracted
print(f"\nWhat we want: '{{value}} - {{old_value}}'")
print("But the outer braces are {{ and }}, so content should be: '{value} - {old_value}'")

# Try different extractions
print(f"\nExtraction from 2 to 21: '{text[2:21]}'")
print(f"Extraction from 2 to 22: '{text[2:22]}'")  
print(f"Last 2 chars: '{text[-2:]}'")

# The correct approach should be to find the LAST }}
last_brace_pos = text.rfind('}}')
print(f"\nLast }} position: {last_brace_pos}")
print(f"Extraction from 2 to {last_brace_pos}: '{text[2:last_brace_pos]}'")