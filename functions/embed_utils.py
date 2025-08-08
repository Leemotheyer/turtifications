import json
import re
import ast
import operator
from datetime import datetime
from functions.utils import format_message_template

def create_discord_embed(embed_config, data=None, user_variables=None):
    """Create a Discord embed from configuration and data, with user variable support"""
    if not embed_config or not embed_config.get('enabled', False):
        return None
    user_variables = user_variables or {}
    embed = {}
    
    # Title
    if embed_config.get('title'):
        embed['title'] = format_message_template(embed_config['title'], data or {}, user_variables)
    
    # Description
    if embed_config.get('description'):
        embed['description'] = format_message_template(embed_config['description'], data or {}, user_variables)
    
    # URL
    if embed_config.get('url'):
        embed['url'] = format_message_template(embed_config['url'], data or {}, user_variables)
    
    # Color handling (static / if / gradient)
    computed_color_hex = compute_embed_color(embed_config, data or {}, user_variables)
    if computed_color_hex:
        color = computed_color_hex.lstrip('#')
        try:
            embed['color'] = int(color, 16)
        except ValueError:
            embed['color'] = 0x3498db
    
    # Timestamp
    if embed_config.get('timestamp', True):
        embed['timestamp'] = datetime.now().isoformat()
    
    # Footer
    if embed_config.get('footer_text') or embed_config.get('footer_icon'):
        footer = {}
        if embed_config.get('footer_text'):
            footer['text'] = format_message_template(embed_config['footer_text'], data or {}, user_variables)
        if embed_config.get('footer_icon'):
            footer['icon_url'] = format_message_template(embed_config['footer_icon'], data or {}, user_variables)
        embed['footer'] = footer
    
    # Author
    if embed_config.get('author_name') or embed_config.get('author_icon') or embed_config.get('author_url'):
        author = {}
        if embed_config.get('author_name'):
            author['name'] = format_message_template(embed_config['author_name'], data or {}, user_variables)
        if embed_config.get('author_icon'):
            author['icon_url'] = format_message_template(embed_config['author_icon'], data or {}, user_variables)
        if embed_config.get('author_url'):
            author['url'] = format_message_template(embed_config['author_url'], data or {}, user_variables)
        embed['author'] = author
    
    # Thumbnail
    if embed_config.get('thumbnail_url'):
        # Support {img:...} extraction in embed thumbnail URL
        thumb_template = embed_config['thumbnail_url']
        formatted_thumb, thumb_images = format_message_template(thumb_template, data or {}, user_variables, extract_images=True)
        thumb_url = None
        if thumb_images and len(thumb_images) > 0:
            thumb_url = thumb_images[0]
        else:
            thumb_url = format_message_template(thumb_template, data or {}, user_variables)
        embed['thumbnail'] = {
            'url': thumb_url
        }
    
    # Image
    if embed_config.get('image_url'):
        # Support {img:...} extraction in embed image URL
        image_template = embed_config['image_url']
        formatted_image, image_urls = format_message_template(image_template, data or {}, user_variables, extract_images=True)
        image_url = None
        if image_urls and len(image_urls) > 0:
            image_url = image_urls[0]
        else:
            image_url = format_message_template(image_template, data or {}, user_variables)
        embed['image'] = {
            'url': image_url
        }
    
    # Fields
    fields = []
    if embed_config.get('fields'):
        for field_config in embed_config['fields']:
            if field_config.get('name') and field_config.get('value'):
                field = {
                    'name': format_message_template(field_config['name'], data or {}, user_variables),
                    'value': format_message_template(field_config['value'], data or {}, user_variables),
                    'inline': field_config.get('inline', False)
                }
                fields.append(field)
    
    # Add dynamic fields based on data if configured
    if embed_config.get('dynamic_fields') and data:
        dynamic_fields = parse_dynamic_fields(embed_config['dynamic_fields'], data, user_variables)
        fields.extend(dynamic_fields)
    
    if fields:
        embed['fields'] = fields
    
    return embed

def compute_embed_color(embed_config, data, user_variables):
    """Compute embed color based on color_mode.
    Returns a hex string like '#RRGGBB' or None.
    Modes:
    - static: use embed_config.color
    - if: evaluate rules on monitored value (variable 'x' in conditions), else white
    - gradient: interpolate between two colors based on monitored numeric value
    """
    try:
        mode = embed_config.get('color_mode', 'static')
        if mode == 'static':
            return embed_config.get('color')
        # Resolve monitored value (supports template variables and calculations)
        monitor_expr = embed_config.get('color_monitor', '')
        monitored_value = None
        if monitor_expr:
            # First expand variables and calculations
            expanded = format_message_template(str(monitor_expr), data, user_variables)
            # Try to parse numeric if possible
            try:
                monitored_value = float(expanded)
            except Exception:
                monitored_value = expanded
        if mode == 'if':
            rules = embed_config.get('color_rules', []) or []
            # Provide 'x' as the monitored value in condition context
            condition_ctx = dict(data or {})
            condition_ctx['x'] = monitored_value
            for rule in rules:
                test = (rule.get('test') or '').strip()
                color = rule.get('color') or '#ffffff'
                if not test:
                    continue
                try:
                    if safe_eval_condition_local(test, condition_ctx):
                        return color
                except Exception:
                    continue
            return '#ffffff'
        if mode == 'gradient':
            gradient = embed_config.get('gradient') or {}
            start_val_expr = gradient.get('start_value', '')
            end_val_expr = gradient.get('end_value', '')
            start_color = gradient.get('start_color', '#00ff00')
            end_color = gradient.get('end_color', '#ff0000')
            # Resolve values
            start_val = format_message_template(str(start_val_expr), data, user_variables)
            end_val = format_message_template(str(end_val_expr), data, user_variables)
            try:
                start_num = float(start_val)
                end_num = float(end_val)
            except Exception:
                return start_color  # fallback
            # Resolve monitored numeric value
            try:
                x = float(monitored_value)
            except Exception:
                return start_color
            # Clamp outside range to nearest end color
            if end_num == start_num:
                return start_color
            if x <= start_num:
                return start_color
            if x >= end_num:
                return end_color
            # Interpolate
            t = (x - start_num) / (end_num - start_num)
            return interpolate_hex_color(start_color, end_color, t)
        return embed_config.get('color')
    except Exception:
        return embed_config.get('color') or '#3498db'

def interpolate_hex_color(start_hex, end_hex, t):
    """Linear interpolate between two hex colors, t in [0,1]"""
    s = start_hex.lstrip('#')
    e = end_hex.lstrip('#')
    try:
        sr, sg, sb = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        er, eg, eb = int(e[0:2], 16), int(e[2:4], 16), int(e[4:6], 16)
    except Exception:
        return start_hex
    r = round(sr + (er - sr) * t)
    g = round(sg + (eg - sg) * t)
    b = round(sb + (eb - sb) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def safe_eval_condition_local(condition, context):
    """Safely evaluate a boolean condition with access to variables in context.
    Supports numbers, strings, dict/list subscripts, comparisons, and/or/not.
    """
    if not condition or not str(condition).strip():
        return True
    # Build safe variables
    safe_vars = {}
    if isinstance(context, dict):
        safe_vars.update(context)
    # Builtins
    safe_vars.update({
        'True': True,
        'False': False,
        'None': None,
        'len': len,
    })
    # Allowed operators
    safe_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.FloorDiv: operator.floordiv,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.In: lambda x, y: x in y,
        ast.NotIn: lambda x, y: x not in y,
        ast.And: lambda x, y: x and y,
        ast.Or: lambda x, y: x or y,
        ast.Not: operator.not_,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }
    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.NameConstant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in safe_vars:
                return safe_vars[node.id]
            raise ValueError(f"Variable '{node.id}' not allowed")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                func = safe_vars.get(func_name)
                if callable(func):
                    args = [eval_node(arg) for arg in node.args]
                    return func(*args)
            raise ValueError("Function call not allowed")
        if isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            op = safe_ops.get(type(node.op))
            if not op:
                raise ValueError("Operator not allowed")
            return op(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            op = safe_ops.get(type(node.op))
            if not op:
                raise ValueError("Unary operator not allowed")
            return op(operand)
        if isinstance(node, ast.Compare):
            left = eval_node(node.left)
            result = True
            for op, comparator in zip(node.ops, node.comparators):
                right = eval_node(comparator)
                op_fn = safe_ops.get(type(op))
                if not op_fn:
                    raise ValueError("Comparison operator not allowed")
                if not op_fn(left, right):
                    return False
                left = right
            return result
        if isinstance(node, ast.BoolOp):
            values = [eval_node(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            raise ValueError("Boolean operator not allowed")
        if isinstance(node, ast.Subscript):
            obj = eval_node(node.value)
            # slice handling for different Python versions
            if isinstance(node.slice, ast.Index):
                key = eval_node(node.slice.value)
            else:
                key = eval_node(node.slice)
            if isinstance(obj, (dict, list)):
                try:
                    return obj[key]
                except Exception:
                    return None
            raise ValueError("Subscript access not allowed")
        raise ValueError(f"Unsupported expression: {type(node).__name__}")
    tree = ast.parse(condition, mode='eval')
    return bool(eval_node(tree.body))

def parse_dynamic_fields(fields_config, data, user_variables):
    """Parse dynamic field configurations and create embed fields"""
    fields = []
    
    for field_config in fields_config:
        if not field_config.get('enabled', False):
            continue
            
        field_name = field_config.get('name', '')
        field_path = field_config.get('path', '')
        field_format = field_config.get('format', 'text')
        field_inline = field_config.get('inline', False)
        
        if not field_name or not field_path:
            continue
        
        # Get the value from the data using the path
        value = get_nested_value(data, field_path)
        
        if value is not None:
            # Format the value based on the format type
            formatted_value = format_field_value(value, field_format)
            
            field = {
                'name': format_message_template(field_name, data, user_variables),
                'value': formatted_value,
                'inline': field_inline
            }
            fields.append(field)
    
    return fields

def get_nested_value(data, path):
    """Safely get nested dictionary value using dot notation"""
    try:
        keys = path.split('.')
        current = data
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
    except:
        return None

def format_field_value(value, format_type):
    """Format a field value based on the specified format type"""
    if value is None:
        return "N/A"
    
    try:
        if format_type == 'number':
            return str(value)
        elif format_type == 'percentage':
            if isinstance(value, (int, float)):
                return f"{value:.1f}%"
            return str(value)
        elif format_type == 'file_size':
            if isinstance(value, (int, float)):
                return format_file_size(value)
            return str(value)
        elif format_type == 'currency':
            if isinstance(value, (int, float)):
                return f"${value:,.2f}"
            return str(value)
        elif format_type == 'date':
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
            return str(value)
        elif format_type == 'boolean':
            if isinstance(value, bool):
                return "✅ Yes" if value else "❌ No"
            elif isinstance(value, (int, float)):
                return "✅ Yes" if value else "❌ No"
            return str(value)
        elif format_type == 'status':
            if isinstance(value, str):
                value_lower = value.lower()
                if value_lower in ['active', 'online', 'running', 'success']:
                    return "🟢 " + str(value)
                elif value_lower in ['inactive', 'offline', 'stopped', 'error']:
                    return "🔴 " + str(value)
                elif value_lower in ['warning', 'pending', 'processing']:
                    return "🟡 " + str(value)
            return str(value)
        else:  # text (default)
            return str(value)
    except:
        return str(value)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 0:
        return "0 B"
    elif size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes < 1024 * 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024 * 1024):.2f} TB"

def validate_embed_config(embed_config):
    """Validate embed configuration and return any errors"""
    errors = []
    
    if not embed_config:
        return errors
    
    # Validate color format
    if embed_config.get('color'):
        color = embed_config['color'].lstrip('#')
        try:
            int(color, 16)
        except ValueError:
            errors.append("Color must be a valid hex color (e.g., #3498db)")
    
    # Validate URLs
    url_fields = ['url', 'footer_icon', 'author_icon', 'author_url', 'thumbnail_url', 'image_url']
    for field in url_fields:
        if embed_config.get(field):
            url = embed_config[field]
            if not url.startswith(('http://', 'https://')):
                errors.append(f"{field.replace('_', ' ').title()} must be a valid URL")
    
    # Validate fields
    if embed_config.get('fields'):
        for i, field in enumerate(embed_config['fields']):
            if not field.get('name'):
                errors.append(f"Field {i+1} must have a name")
            if not field.get('value'):
                errors.append(f"Field {i+1} must have a value")
    
    # Validate dynamic fields
    if embed_config.get('dynamic_fields'):
        for i, field in enumerate(embed_config['dynamic_fields']):
            if not field.get('name'):
                errors.append(f"Dynamic field {i+1} must have a name")
            if not field.get('path'):
                errors.append(f"Dynamic field {i+1} must have a path")
    
    return errors 