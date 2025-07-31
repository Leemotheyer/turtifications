# Message Template Calculations

This application now supports simple calculations within message templates using square brackets `[expression]`.

## Syntax

Use square brackets to wrap mathematical expressions that contain variable references:

```
[{variable1} operator {variable2}]
```

## Supported Operations

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Floor Division: `//`
- Modulo: `%`
- Exponentiation: `**`
- Unary operators: `+`, `-`

## Examples

### Basic Arithmetic
```
[{value} - {old_value}] total gain
[{price} * {quantity}] total cost
[{value} / {old_value}] ratio
```

### With User Variables
```
[{value} + {var:bonus}] with bonus
[{value} * {var:multiplier}] doubled
```

### Complex Expressions
```
[{value} - {old_value} + {var:bonus}] net gain
[{price} * {quantity} * {percentage}] discounted total
[{var:multiplier} ** 3] cubed
[{value} % 30] remainder
```

### Mixed with Regular Variables
```
Current value: {value}, Previous: {old_value}, Gain: [{value} - {old_value}]
```

## How It Works

1. Variables inside `{}` are replaced with their actual values
2. The resulting mathematical expression is safely evaluated using AST parsing
3. Results are formatted appropriately (integers for whole numbers, 2 decimal places for floats)
4. Price-related calculations (containing `*` and `price`) always show 2 decimal places

## Error Handling

- Unknown variables: `CALC_ERROR(UNKNOWN_VAR_variable + 5)`
- Division by zero: `CALC_ERROR(100 / 0)`
- Invalid syntax: `CALC_ERROR(100 +)`

## Security

The calculation engine uses Python's AST (Abstract Syntax Tree) parsing to safely evaluate mathematical expressions without the security risks of `eval()`. Only basic mathematical operations are supported - no function calls or other Python features are allowed.