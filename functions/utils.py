import json
import re
import ast
import operator
from datetime import datetime
from functions.config import get_logs, save_logs, get_config, save_config

def get_nested_value(data_dict, path):
    """Get a nested value from a dictionary using dot notation"""
    if not data_dict or not path:
        return None
    
    try:
        keys = path.split('.')
        current = data_dict
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
    except Exception:
        return None

def get_notification_logs():
    """Get notification-specific logs"""
    try:
        with open('data/sent_notifications.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_notification_logs(logs):
    """Save notification-specific logs"""
    import os
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    with open('data/sent_notifications.json', 'w') as f:
        json.dump(logs, f, indent=2)

def detect_log_category(message):
    """Auto-detect log category based on message content"""
    message_lower = message.lower()
    
    # Error-related
    if any(keyword in message_lower for keyword in ['error', 'failed', 'exception', 'processing failed']):
        return 'Errors'
    
    # Notification-related
    if any(keyword in message_lower for keyword in ['notification sent', 'discord webhook', '✅', '❌']):
        return 'Notifications'
    
    # API-related
    if any(keyword in message_lower for keyword in ['api', 'endpoint', 'http', 'request', 'response', 'fetch']):
        return 'API'
    
    # System-related
    if any(keyword in message_lower for keyword in ['system', 'config', 'configuration', 'setting']):
        return 'System'
    
    # Test-related
    if any(keyword in message_lower for keyword in ['test', '🧪', 'preview']):
        return 'Testing'
    
    # Timer-related
    if any(keyword in message_lower for keyword in ['timer', '⏰', 'interval']):
        return 'Timers'
    
    # Change detection
    if any(keyword in message_lower for keyword in ['change detected', '🔄', 'changed from']):
        return 'Change Detection'
    
    # Webhook-related
    if any(keyword in message_lower for keyword in ['webhook', '🌐', 'incoming']):
        return 'Webhooks'
    
    # Condition-related
    if any(keyword in message_lower for keyword in ['condition', '⏭️', 'evaluate']):
        return 'Conditions'
    
    # Debug-related
    if any(keyword in message_lower for keyword in ['debug', '🔍', '🔄']):
        return 'Debug'
    
    # Default category
    return 'General'

def log_notification_sent(flow_name, message_content, embed_info=None, webhook_name=None):
    """Log a successfully sent notification with details"""
    # Only log if we have meaningful content
    if not flow_name:
        return
        
    # Check if we have actual content to log
    has_message = message_content and str(message_content).strip()
    has_embed = embed_info and (embed_info.get('title') or embed_info.get('description'))
    
    if not has_message and not has_embed:
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notification_entry = {
        'timestamp': timestamp,
        'flow_name': flow_name,
        'message_content': str(message_content).strip() if has_message else '',
        'embed_info': embed_info if has_embed else None,
        'webhook_name': webhook_name or '',
        'type': 'sent',
        'category': 'Notifications'
    }
    
    # Get existing notification logs
    logs = get_notification_logs()
    
    # Add new notification entry
    logs.append(notification_entry)
    
    # Get configurable log retention limit
    config = get_config()
    notification_log_retention = config.get('notification_log_retention', 500)  # Default to 500
    
    # Keep only the last N notification logs
    if len(logs) > notification_log_retention:
        logs = logs[-notification_log_retention:]
    
    # Save notification logs
    save_notification_logs(logs)
    
    # Increment total notifications counter
    config = get_config()
    total_sent = config.get('total_notifications_sent', 0)
    config['total_notifications_sent'] = total_sent + 1
    save_config(config)

def log_notification(message, category=None):
    """Log a notification message with timestamp and category"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Auto-detect category based on message content if not provided
    if category is None:
        category = detect_log_category(message)
    
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'category': category
    }
    
    # Get existing logs
    logs = get_logs()
    
    # Add new log entry
    logs.append(log_entry)
    
    # Get configurable log retention limit
    config = get_config()
    log_retention = config.get('log_retention', 1000)  # Default to 1000
    
    # Keep only the last N logs to prevent file from growing too large
    if len(logs) > log_retention:
        logs = logs[-log_retention:]
    
    # Save logs
    save_logs(logs)

def format_message_template(template, data, user_variables=None, extract_images=False):
    """Simple and reliable message template formatter with user variable support and calculations
    
    Args:
        template: The template string to process
        data: Data dictionary for variable substitution
        user_variables: User-defined variables
        extract_images: If True, returns (formatted_text, image_urls) tuple instead of just text
    
    Returns:
        If extract_images=False: formatted text string
        If extract_images=True: (formatted_text, list_of_image_urls) tuple
    """
    user_variables = user_variables or {}
    
    # Extract and collect image URLs from {img:url} patterns
    image_urls = []
    if extract_images:
        # More sophisticated pattern to handle nested braces
        img_pattern = r'\{img:([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        img_matches = re.findall(img_pattern, template)
        
        for img_url in img_matches:
            # Process the URL through the same variable substitution system
            processed_url = format_message_template(img_url, data, user_variables, extract_images=False)
            if processed_url and processed_url != "N/A" and processed_url != "ERROR":
                image_urls.append(processed_url)
        
        # Remove image patterns from template for text processing
        template = re.sub(img_pattern, '', template)
    
    def replace_template_var(match):
        """Replace template variables with actual values"""
        try:
            var_expr = match.group(1)  # Get the content inside {}
            
            # Handle {img:url} patterns - leave them unchanged when not extracting images
            if var_expr.startswith('img:') and not extract_images:
                return match.group(0)  # Return the whole match unchanged
            
            # Handle {time} variable
            if var_expr == 'time':
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Handle {data} variable (full data object)
            if var_expr == 'data':
                return json.dumps(data, indent=2)
            
            # Handle {data['key']['subkey']} pattern
            if var_expr.startswith("data['") and var_expr.endswith("']"):
                # Extract the path: data['result']['downloaded_issues'] -> result.downloaded_issues
                path = var_expr[6:-3]  # Remove data[' and ']
                path = path.replace("']['", ".")  # Convert to dot notation
                
                value = get_nested_value(data, path)
                if value is not None:
                    return str(value)
                else:
                    return "N/A"
            
            # Handle {key['subkey']} or {key['0']} pattern (for direct access to nested data or arrays)
            if var_expr.endswith("']") and "['" in var_expr:
                # Convert e.g. result['0'] or result['downloaded_issues'] to result.0 or result.downloaded_issues
                path = var_expr.replace("['", ".").replace("']", "")
                value = get_nested_value(data, path)
                if value is not None:
                    return str(value)
                else:
                    return "N/A"
            
            # Handle {data['key']['subkey']/1024/1024/1024:.2f} pattern (for file sizes)
            if var_expr.startswith("data['") and "/1024/1024/1024" in var_expr:
                # Extract the path and formatting
                parts = var_expr.split("/1024/1024/1024")
                if len(parts) == 2:
                    path_part = parts[0]
                    format_part = parts[1]
                    
                    # Extract path
                    path = path_part[6:-3]  # Remove data[' and ']
                    path = path.replace("']['", ".")
                    
                    value = get_nested_value(data, path)
                    if value is not None and isinstance(value, (int, float)):
                        # Apply the division and formatting
                        result = value / 1024 / 1024 / 1024
                        if ":.2f" in format_part:
                            return f"{result:.2f}"
                        return str(result)
                    else:
                        return "N/A"
            
            # Handle simple {variable} patterns
            if var_expr in data:
                # If it's a dictionary, convert to JSON string for display
                if isinstance(data[var_expr], dict):
                    return json.dumps(data[var_expr], indent=2)
                return str(data[var_expr])
            
            # Handle user variables: {$variable} format
            if var_expr.startswith('$'):
                var_name = var_expr[1:]
                if var_name in user_variables:
                    return str(user_variables[var_name])
                return 'N/A'
            
            # Handle calculations: {calc:expression} format
            if var_expr.startswith('calc:'):
                calc_expr = var_expr[5:]
                # Use the existing calculation logic
                return replace_calculation(re.match(r'\[([^\]]+)\]', f"[{calc_expr}]"))
            
            # Handle bracket notation: {key['subkey']} format
            if var_expr.endswith("']") and "['" in var_expr:
                # Convert bracket notation to dot notation
                path = var_expr.replace("['", ".").replace("']", "")
                value = get_nested_value(data, path)
                if value is not None:
                    return str(value)
                return "N/A"
            
            # Try to get nested value using dot notation
            value = get_nested_value(data, var_expr)
            if value is not None:
                return str(value)
            
            # Try direct access in data
            if var_expr in data:
                return str(data[var_expr])
            
            return "N/A"
            
        except Exception as e:
            log_notification(f"Template formatting error: {str(e)}")
            return "ERROR"
    
    def replace_calculation(match):
        """Replace calculation expressions with computed values"""
        try:
            calc_expr = match.group(1)  # Get the content inside {{}}
            
            # Build variables dictionary for calculation
            calc_variables = {}
            
            # Add simple data variables
            for key, value in data.items():
                if isinstance(value, (int, float, str)):
                    # Try to convert strings to numbers if possible
                    if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        try:
                            calc_variables[key] = float(value) if '.' in value else int(value)
                        except ValueError:
                            calc_variables[key] = value
                    else:
                        calc_variables[key] = value
            
            # Add user variables
            for key, value in user_variables.items():
                if isinstance(value, (int, float, str)):
                    if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        try:
                            calc_variables[key] = float(value) if '.' in value else int(value)
                        except ValueError:
                            calc_variables[key] = value
                    else:
                        calc_variables[key] = value
            
            # Handle nested data access in calculations by replacing {var} patterns
            # Replace {variable} references with actual values before calculation
            def replace_var_in_calc(var_match):
                var_name = var_match.group(1)
                
                # Handle time variable
                if var_name == 'time':
                    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Handle data['key']['subkey'] pattern
                if var_name.startswith("data['") and var_name.endswith("']"):
                    path = var_name[6:-3]  # Remove data[' and ']
                    path = path.replace("']['", ".")  # Convert to dot notation
                    value = get_nested_value(data, path)
                    if value is not None and isinstance(value, (int, float)):
                        return str(value)
                    return "0"  # Default for calculations
                
                # Handle simple variables
                if var_name in data and isinstance(data[var_name], (int, float)):
                    return str(data[var_name])
                
                # Handle user variables
                if var_name.startswith('var:'):
                    user_var = var_name[4:]
                    if user_var in user_variables and isinstance(user_variables[user_var], (int, float)):
                        return str(user_variables[user_var])
                
                # Try direct lookup in calc_variables
                if var_name in calc_variables:
                    return str(calc_variables[var_name])
                
                # Return a placeholder that will cause an error in AST evaluation
                return f"UNKNOWN_VAR_{var_name}"
            
            # Replace {variable} patterns in the calculation expression
            calc_expr_processed = re.sub(r'\{([^}]+)\}', replace_var_in_calc, calc_expr)
            
            # Evaluate the processed expression
            result = safe_eval_calculation(calc_expr_processed, calc_variables)
            
            # Format the result nicely
            if isinstance(result, float):
                # Always show 2 decimal places for multiplication results involving prices
                if calc_expr_processed.count('*') > 0 and any(var in calc_expr for var in ['price', 'cost']):
                    return f"{result:.2f}"
                # Round to 2 decimal places if it's a float
                elif result == int(result):
                    return str(int(result))
                else:
                    return f"{result:.2f}"
            else:
                return str(result)
                
        except Exception as e:
            log_notification(f"Calculation replacement error: {str(e)}")
            return f"CALC_ERROR"
    
    # First replace all {variable} patterns
    pattern = r'\{([^}]+)\}'
    result = re.sub(pattern, replace_template_var, template)
    
    # Then replace all standalone [calculation] patterns (not inside variables)
    calc_pattern = r'\[([^\]]+)\]'
    result = re.sub(calc_pattern, replace_calculation, result)
    
    # Return appropriate format based on extract_images flag
    if extract_images:
        return result, image_urls
    else:
        return result

def safe_eval_calculation(expression, variables):
    """Safely evaluate mathematical expressions using AST"""
    try:
        # Supported operations
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        def eval_node(node):
            if isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # For older Python versions
                return node.n
            elif isinstance(node, ast.Str):  # For older Python versions
                return node.s
            elif isinstance(node, ast.Name):
                # Variable lookup
                var_name = node.id
                if var_name in variables:
                    return variables[var_name]
                else:
                    raise ValueError(f"Unknown variable: {var_name}")
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                op = ops.get(type(node.op))
                if op:
                    return op(left, right)
                else:
                    raise ValueError(f"Unsupported operation: {type(node.op)}")
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                op = ops.get(type(node.op))
                if op:
                    return op(operand)
                else:
                    raise ValueError(f"Unsupported unary operation: {type(node.op)}")
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")
        
        # Parse the expression
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return result
        
    except Exception as e:
        log_notification(f"Calculation error in '{expression}': {str(e)}")
        return f"CALC_ERROR({expression})"

def evaluate_condition(condition, data):
    """Safely evaluate a condition expression using AST instead of eval()"""
    if not condition or not condition.strip():
        return True
    
    try:
        # Define safe operators
        safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
            ast.BitOr: operator.or_,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
            ast.FloorDiv: operator.floordiv,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Is: operator.is_,
            ast.IsNot: operator.is_not,
            ast.In: lambda x, y: x in y,
            ast.NotIn: lambda x, y: x not in y,
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
            ast.Not: operator.not_,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }
        
        # Use the top-level get_nested_value function
        
        # Create safe variables context
        # Start with user variables and data fields
        safe_vars = {}
        
        # Add user variables first
        for var_name, var_value in user_variables.items():
            safe_vars[var_name] = var_value
        
        # Add all data fields to the safe variables
        if isinstance(data, dict):
            safe_vars.update(data)
        
        # Define built-in variables that cannot be overwritten
        builtin_vars = {
            'value': data.get('value'),
            'old_value': data.get('old_value'),
            'data': data,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'True': True,
            'False': False,
            'None': None,
            'len': len,  # Add built-in len function
        }
        
        # Add all data fields to the safe variables
        if isinstance(data, dict):
            safe_vars.update(data)
        
        def safe_eval_node(node):
            """Safely evaluate an AST node"""
            if isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Python < 3.8
                return node.n
            elif isinstance(node, ast.Str):  # Python < 3.8
                return node.s
            elif isinstance(node, ast.NameConstant):  # Python < 3.8
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in safe_vars:
                    return safe_vars[node.id]
                else:
                    raise ValueError(f"Variable '{node.id}' not allowed")
            elif isinstance(node, ast.Call):
                # Handle function calls like len()
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in safe_vars and callable(safe_vars[func_name]):
                        # Evaluate arguments
                        args = [safe_eval_node(arg) for arg in node.args]
                        return safe_vars[func_name](*args)
                    else:
                        raise ValueError(f"Function '{func_name}' not allowed")
                else:
                    raise ValueError("Only simple function calls are allowed")
            elif isinstance(node, ast.BinOp):
                left = safe_eval_node(node.left)
                right = safe_eval_node(node.right)
                if type(node.op) in safe_operators:
                    return safe_operators[type(node.op)](left, right)
                else:
                    raise ValueError(f"Operator {type(node.op).__name__} not allowed")
            elif isinstance(node, ast.UnaryOp):
                operand = safe_eval_node(node.operand)
                if type(node.op) in safe_operators:
                    return safe_operators[type(node.op)](operand)
                else:
                    raise ValueError(f"Unary operator {type(node.op).__name__} not allowed")
            elif isinstance(node, ast.Compare):
                left = safe_eval_node(node.left)
                result = left
                for op, comparator in zip(node.ops, node.comparators):
                    right = safe_eval_node(comparator)
                    if type(op) in safe_operators:
                        result = safe_operators[type(op)](result, right)
                        if not result:
                            break
                    else:
                        raise ValueError(f"Comparison operator {type(op).__name__} not allowed")
                return result
            elif isinstance(node, ast.BoolOp):
                values = [safe_eval_node(value) for value in node.values]
                if isinstance(node.op, ast.And):
                    return all(values)
                elif isinstance(node.op, ast.Or):
                    return any(values)
                else:
                    raise ValueError(f"Boolean operator {type(node.op).__name__} not allowed")
            elif isinstance(node, ast.Subscript):
                # Handle dictionary/list access like data['key'] or data[0]
                obj = safe_eval_node(node.value)
                if isinstance(node.slice, ast.Index):  # Python < 3.9
                    key = safe_eval_node(node.slice.value)
                else:  # Python 3.9+
                    key = safe_eval_node(node.slice)
                
                if isinstance(obj, (dict, list)):
                    try:
                        return obj[key]
                    except (KeyError, IndexError, TypeError):
                        return None
                else:
                    raise ValueError(f"Subscript access not allowed on {type(obj).__name__}")
            else:
                raise ValueError(f"AST node type {type(node).__name__} not allowed")
        
        # Pre-process the condition to handle bracket notation
        condition_processed = condition
        
        # Handle bracket notation: result['downloaded_issues'] -> result['downloaded_issues']
        # AST can handle bracket notation directly, no transformation needed
        bracket_pattern = r'(\w+)\[\'([^\']+)\'\]'
        
        # Parse and evaluate the condition safely
        try:
            parsed = ast.parse(condition_processed, mode='eval')
            result = safe_eval_node(parsed.body)
            
            # Log the evaluation result
            log_notification(f"Condition evaluation: '{condition}' -> {result}")
            
            return bool(result)
        except SyntaxError as e:
            log_notification(f"Condition syntax error: '{condition}' - {str(e)}")
            return False
        
    except Exception as e:
        log_notification(f"Condition evaluation error: '{condition}' - {str(e)}")
        return False  # Default to False on error to prevent unwanted notifications 