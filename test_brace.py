#!/usr/bin/env python3

def find_matching_braces(text):
    """Debug version of brace finding"""
    start_idx = text.find('{{')
    if start_idx == -1:
        return None, None
    
    print(f"Found {{ at position {start_idx}")
    print(f"Text: {text}")
    print(f"      {' ' * start_idx}^^")
    
    # Find matching }} by counting braces
    brace_count = 0
    end_idx = -1
    i = start_idx + 2
    
    while i < len(text) - 1:
        if text[i:i+2] == '{{':
            brace_count += 1
            print(f"Found {{ at {i}, count now {brace_count}")
            i += 2
        elif text[i:i+2] == '}}':
            if brace_count == 0:
                end_idx = i
                print(f"Found matching }} at {i}")
                break
            else:
                brace_count -= 1
                print(f"Found }} at {i}, count now {brace_count}")
                i += 2
        else:
            i += 1
    
    if end_idx != -1:
        calc_expr = text[start_idx + 2:end_idx]
        print(f"Extracted: '{calc_expr}'")
        print(f"From position {start_idx + 2} to {end_idx}")
        return start_idx, end_idx
    else:
        print("No matching }} found")
        return None, None

# Test cases
test_cases = [
    "{{value} - {old_value}}",
    "{{a + b}}",
    "{{{{nested}}}}",
    "prefix {{calc}} suffix"
]

for test in test_cases:
    print(f"\nTesting: {test}")
    find_matching_braces(test)
    print("-" * 40)