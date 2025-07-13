import json
import re
from datetime import datetime
from functions.config import get_logs, save_logs, get_config

def get_notification_logs():
    """Get notification-specific logs"""
    try:
        with open('data/sent_notifications.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_notification_logs(logs):
    """Save notification-specific logs"""
    with open('data/sent_notifications.json', 'w') as f:
        json.dump(logs, f, indent=2)

def detect_log_category(message):
    """Auto-detect log category based on message content"""
    message_lower = message.lower()
    
    # Notification-related
    if any(keyword in message_lower for keyword in ['notification sent', 'discord webhook', '✅', '❌']):
        return 'Notifications'
    
    # API-related
    if any(keyword in message_lower for keyword in ['api', 'endpoint', 'http', 'request', 'response', 'fetch']):
        return 'API'
    
    # System-related
    if any(keyword in message_lower for keyword in ['system', 'config', 'configuration', 'setting']):
        return 'System'
    
    # Error-related
    if any(keyword in message_lower for keyword in ['error', 'failed', '❌', 'exception']):
        return 'Errors'
    
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
    notification_log_retention = config.get('notification_log_retention', 100)  # Default to 100
    
    # Keep only the last N notification logs
    if len(logs) > notification_log_retention:
        logs = logs[-notification_log_retention:]
    
    # Save notification logs
    save_notification_logs(logs)

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

def format_message_template(template, data):
    """Simple and reliable message template formatter"""
    
    def get_nested_value(data_dict, path):
        """Safely get nested dictionary value using dot notation"""
        try:
            # Convert path like "result.downloaded_issues" to nested access
            keys = path.split('.')
            current = data_dict
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                elif isinstance(current, list) and key.isdigit():
                    # Handle array access
                    index = int(key)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            return current
        except:
            return None
    
    def replace_template_var(match):
        """Replace template variables with actual values"""
        try:
            var_expr = match.group(1)  # Get the content inside {}
            
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
            
            return "N/A"
            
        except Exception as e:
            log_notification(f"Template formatting error: {str(e)}")
            return "ERROR"
    
    # Replace all {variable} patterns
    pattern = r'\{([^}]+)\}'
    result = re.sub(pattern, replace_template_var, template)
    
    return result

def evaluate_condition(condition, data):
    """
    Evaluate a condition expression against data
    Supports: ==, !=, >, <, >=, <=, and, or, not, in, not in
    Variables: value, old_value, data, time, and any API data fields
    Uses bracket notation like message templates: result['downloaded_issues'] > 1
    """
    if not condition or not condition.strip():
        return True  # No condition means always true
    
    try:
        # Create a safe evaluation environment with the same logic as message templates
        safe_dict = {
            'value': data.get('value'),
            'old_value': data.get('old_value'),
            'data': data,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'True': True,
            'False': False,
            'None': None,
            # Add basic operators and functions
            'int': int,
            'float': float,
            'str': str,
            'len': len
        }
        
        # Add all data fields to the safe environment
        if isinstance(data, dict):
            safe_dict.update(data)
        
        # Pre-process the condition to handle bracket notation like message templates
        condition_processed = condition
        
        # Handle bracket notation: result['downloaded_issues'] -> safe_get_nested(data, 'result.downloaded_issues')
        def get_nested_value(data_dict, path):
            """Safely get nested dictionary value using dot notation (same as message templates)"""
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
            except Exception as e:
                log_notification(f"Field extraction error for '{path}': {str(e)}")
                return None
        
        # Create a closure to capture the data variable
        def make_get_nested(data_dict):
            def get_nested(path):
                return get_nested_value(data_dict, path)
            return get_nested
        
        # Add the helper function to the evaluation environment
        safe_dict['get_nested_value'] = make_get_nested(data)
        
        # Only process bracket notation if it exists in the condition
        import re
        bracket_pattern = r'(\w+)\[\'([^\']+)\'\]'
        if re.search(bracket_pattern, condition_processed):
            def replace_brackets(match):
                var_name = match.group(1)
                key = match.group(2)
                # Use dictionary access since the data is already in safe_dict
                replacement = f"{var_name}['{key}']"
                return replacement
            
            condition_processed = re.sub(bracket_pattern, replace_brackets, condition_processed)
        
        # Evaluate the condition
        result = eval(condition_processed, {"__builtins__": {}}, safe_dict)
        
        # Log the evaluation result
        log_notification(f"Condition evaluation: '{condition}' -> {result}")
        
        return bool(result)
        
    except Exception as e:
        log_notification(f"Condition evaluation error: '{condition}' - {str(e)}")
        return False  # Default to False on error to prevent unwanted notifications 