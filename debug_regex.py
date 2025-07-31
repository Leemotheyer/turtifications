import re

test_string = "{{value} - {old_value}} total gain"
print(f"Test string: {test_string}")
print()

# Let's try a different approach - find patterns like {{...}}
patterns = [
    r'\{\{(.*?)\}\}',  # Original - doesn't work  
    r'\{\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}\}',  # Complex - doesn't work
    r'\{\{((?:[^{}]|\{[^}]*\})*)\}\}',  # Another complex one
    r'\{\{(.*?(?:\}[^}].*?)?)\}\}',  # Try to handle the end better
    r'\{\{([^}]*\}[^}]*[^}])\}\}',  # Match until last }}
]

for i, pattern in enumerate(patterns, 1):
    print(f"Pattern {i}: {pattern}")
    matches = re.findall(pattern, test_string)
    print(f"Matches: {matches}")
    
    # Also try substitution to see what would be replaced
    def replacer(match):
        return f"REPLACED({match.group(1)})"
    
    result = re.sub(pattern, replacer, test_string)
    print(f"After substitution: {result}")
    print()

# Let's also test what the current pattern captures
print("Manual parsing approach:")
# Find all {{ positions
start_positions = []
for i, char in enumerate(test_string):
    if i < len(test_string) - 1 and test_string[i:i+2] == '{{':
        start_positions.append(i)

print(f"{{ positions: {start_positions}")

# Find all }} positions  
end_positions = []
for i, char in enumerate(test_string):
    if i < len(test_string) - 1 and test_string[i:i+2] == '}}':
        end_positions.append(i)

print(f"}} positions: {end_positions}")

if start_positions and end_positions:
    start = start_positions[0] + 2
    end = end_positions[0]
    captured = test_string[start:end]
    print(f"Manual capture: '{captured}'")