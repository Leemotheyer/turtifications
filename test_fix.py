#!/usr/bin/env python3

text = "{{value} - {old_value}}"
print(f"String: {text}")

# Find {{ position 
start = text.find('{{')
print(f"{{ at: {start}")

# Find }} position
end = text.find('}}')
print(f"}} at: {end}")

# Extract content - this should be the calculation expression
calc_expr = text[start + 2:end]
print(f"Extracted: '{calc_expr}'")

# This should be: {value} - {old_value}
expected = "{value} - {old_value}"
print(f"Expected:  '{expected}'")
print(f"Match: {calc_expr == expected}")

# Let's check with actual positions
print(f"\nPositions 2 to 21 (exclusive): '{text[2:21]}'")
print(f"Positions 2 to 22 (exclusive): '{text[2:22]}'")  

# Ah! Position 22 is the second }, so I need [2:22] to include everything up to the first }
print(f"\nThe issue is: text.find('}}') gives {text.find('}}')} (start of '}}')")
print(f"But I need to include everything before the '}}', which ends at position {text.find('}}')}")
end_pos = text.find('}}')
print(f"So extraction should be [2:{end_pos}]: '{text[2:end_pos]}'")
print(f"Which equals: '{text[2:21]}'")

# I think the issue is actually in understanding what the expression should be
# {{value} - {old_value}} means:
# - Take the value of the 'value' variable
# - Subtract the value of the 'old_value' variable  
# So the expression I need to evaluate is: value - old_value (without braces)
# And {value} and {old_value} should be substituted with actual values first

print(f"\nI think the approach should be:")
print(f"1. Extract: '{text[2:text.find('}}')]}'")
print(f"2. Replace {{variable}} with actual values")
print(f"3. Evaluate the resulting mathematical expression")