#!/usr/bin/env python3

text = "{{value} - {old_value}}"
print(f"String: {text}")
print("Positions:")

for i, char in enumerate(text):
    print(f"{i:2d}: {char}")

# What I want to extract: {value} - {old_value}
target = "{value} - {old_value}"
print(f"\nTarget extraction: '{target}'")

# The content between {{ and }} should be: {value} - {old_value}
# {{ starts at 0
# }} should end at the last two positions
print(f"\nLast two characters: '{text[-2:]}'")
print(f"Positions of last two: {len(text)-2}, {len(text)-1}")

# So }} is at positions 21, 22  
# Content should be from position 2 to position 21 (exclusive)
print(f"\nExtraction [2:21]: '{text[2:21]}'")
print(f"This should be: '{target}'")
print(f"But I get: '{text[2:21]}'")

print(f"\nActual positions where }} starts: {text.find('}}')}")
print(f"So I should extract from 2 to {text.find('}}')}: '{text[2:text.find('}}')]}'")

# But wait, let me see what the target should actually be:
# If the template is {{value} - {old_value}}
# The CALCULATION EXPRESSION should be: {value} - {old_value}
# But that doesn't make sense as a mathematical expression
# 
# I think the user actually wants: value - old_value (without the braces)
# And the {value} and {old_value} are references to variables that should be substituted

print(f"\nMaybe the expression should be without the inner braces:")
print(f"Like: 'value - old_value'")
print(f"And then {value} and {old_value} get replaced with actual values before calculation")

# Let's try extracting inner content differently
# Find everything between {{ and }} and then remove variable braces?
content = text[2:text.find('}}')]
print(f"\nRaw content: '{content}'")

# Now I should process this to replace {variable} with values and then evaluate