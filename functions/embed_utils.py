import json
import re
from datetime import datetime
from functions.utils import format_message_template
from functions.image_utils import extract_image_urls_from_embed, download_image, is_local_service_url

def create_discord_embed(embed_config, data=None, user_variables=None):
    """Create a Discord embed from configuration and data, with user variable support"""
    if not embed_config or not embed_config.get('enabled', False):
        return None
    user_variables = user_variables or {}
    embed = {}
    
    # Track which images need to be converted to attachment references
    attachment_mapping = {}
    
    # Title
    if embed_config.get('title'):
        embed['title'] = format_message_template(embed_config['title'], data or {}, user_variables)
    
    # Description
    if embed_config.get('description'):
        embed['description'] = format_message_template(embed_config['description'], data or {}, user_variables)
    
    # URL
    if embed_config.get('url'):
        embed['url'] = format_message_template(embed_config['url'], data or {}, user_variables)
    
    # Color (convert hex to integer)
    if embed_config.get('color'):
        color = embed_config['color'].lstrip('#')
        try:
            embed['color'] = int(color, 16)
        except ValueError:
            # Default to a nice blue if color is invalid
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
            footer_icon_url = format_message_template(embed_config['footer_icon'], data or {}, user_variables)
            if is_local_service_url(footer_icon_url):
                attachment_mapping['footer_icon'] = footer_icon_url
                footer['icon_url'] = 'attachment://footer_icon.png'
            else:
                footer['icon_url'] = footer_icon_url
        embed['footer'] = footer
    
    # Author
    if embed_config.get('author_name') or embed_config.get('author_icon') or embed_config.get('author_url'):
        author = {}
        if embed_config.get('author_name'):
            author['name'] = format_message_template(embed_config['author_name'], data or {}, user_variables)
        if embed_config.get('author_icon'):
            author_icon_url = format_message_template(embed_config['author_icon'], data or {}, user_variables)
            if is_local_service_url(author_icon_url):
                attachment_mapping['author_icon'] = author_icon_url
                author['icon_url'] = 'attachment://author_icon.png'
            else:
                author['icon_url'] = author_icon_url
        if embed_config.get('author_url'):
            author['url'] = format_message_template(embed_config['author_url'], data or {}, user_variables)
        embed['author'] = author
    
    # Thumbnail
    if embed_config.get('thumbnail_url'):
        thumbnail_url = format_message_template(embed_config['thumbnail_url'], data or {}, user_variables)
        if is_local_service_url(thumbnail_url):
            # Mark for attachment conversion
            attachment_mapping['thumbnail'] = thumbnail_url
            embed['thumbnail'] = {'url': 'attachment://embed_thumbnail.png'}
        else:
            embed['thumbnail'] = {'url': thumbnail_url}
    
    # Image
    if embed_config.get('image_url'):
        image_url = format_message_template(embed_config['image_url'], data or {}, user_variables)
        if is_local_service_url(image_url):
            # Mark for attachment conversion
            attachment_mapping['image'] = image_url
            embed['image'] = {'url': 'attachment://embed_image.png'}
        else:
            embed['image'] = {'url': image_url}
    
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
    
    # Add attachment mapping to embed for later processing
    if attachment_mapping:
        embed['_local_images'] = attachment_mapping
    
    return embed

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