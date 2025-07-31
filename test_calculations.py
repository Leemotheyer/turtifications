#!/usr/bin/env python3
"""
Test script for message template calculations
"""

import sys
import os
sys.path.append('.')

from functions.utils import format_message_template

def test_calculations():
    """Test various calculation scenarios"""
    
    print("Testing Message Template Calculations")
    print("=" * 50)
    
    # Test data
    test_data = {
        'value': 100,
        'old_value': 80,
        'price': 25.50,
        'quantity': 4,
        'score': '95',  # String number
        'percentage': 0.85
    }
    
    user_vars = {
        'bonus': 10,
        'multiplier': 2
    }
    
    # Test cases
    test_cases = [
        # Basic arithmetic
        ("{{value} - {old_value}} total gain", "20 total gain"),
        ("{{value} + {old_value}} total sum", "180 total sum"),
        ("{{price} * {quantity}} total cost", "102.00 total cost"),
        ("{{value} / {old_value}} ratio", "1.25 ratio"),
        
        # With user variables
        ("{{value} + {var:bonus}} with bonus", "110 with bonus"),
        ("{{value} * {var:multiplier}} doubled", "200 doubled"),
        
        # More complex expressions
        ("{{value} - {old_value} + {var:bonus}} net gain", "30 net gain"),
        ("{{price} * {quantity} * {percentage}} discounted total", "86.70 discounted total"),
        
        # String numbers
        ("{{score} + {var:bonus}} final score", "105 final score"),
        
        # Power and modulo
        ("{{var:multiplier} ** 3}} cubed", "8 cubed"),
        ("{{value} % 30}} remainder", "10 remainder"),
        
        # Mixed with regular variables
        ("Current value: {value}, Previous: {old_value}, Gain: {{value} - {old_value}}", 
         "Current value: 100, Previous: 80, Gain: 20"),
    ]
    
    print(f"Test data: {test_data}")
    print(f"User variables: {user_vars}")
    print()
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (template, expected) in enumerate(test_cases, 1):
        try:
            result = format_message_template(template, test_data, user_vars)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            if result != expected:
                print(f"Test {i}: {status}")
                print(f"  Template: {template}")
                print(f"  Expected: {expected}")
                print(f"  Got:      {result}")
            else:
                print(f"Test {i}: {status} - {template}")
                success_count += 1
        except Exception as e:
            print(f"Test {i}: ❌ ERROR - {template}")
            print(f"  Error: {str(e)}")
        print()
    
    print(f"Results: {success_count}/{total_count} tests passed")
    
    # Test error cases
    print("\nTesting Error Cases:")
    error_cases = [
        "{{invalid_var + 5}} should error",
        "{{value / 0}} division by zero",
        "{{value +}} incomplete expression",
    ]
    
    for case in error_cases:
        try:
            result = format_message_template(case, test_data, user_vars)
            print(f"Error case: {case} -> {result}")
        except Exception as e:
            print(f"Error case: {case} -> Exception: {str(e)}")

if __name__ == "__main__":
    test_calculations()